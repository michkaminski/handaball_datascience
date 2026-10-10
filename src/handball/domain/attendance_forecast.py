from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby

from handball.domain.attendance_formatting import formatuj_dziesietna, formatuj_zaokraglona
from handball.domain.attendance_sample import MeczProbki

MIN_MECZOW_PROGNOZY = 40
UDZIAL_TESTOWY = 0.2
OKNO_SREDNIEJ_GOSPODARZA = 5
REGULARYZACJA = 1e-6
PROG_OSOBLIWOSCI = 1e-12
NAZWY_CECH = (
    f"Średnia ostatnich {OKNO_SREDNIEJ_GOSPODARZA} meczów gospodarza u siebie (widzowie)",
    "Weekend (sobota lub niedziela)",
    "Godzina rozpoczęcia (godziny)",
    "Miesiąc, składnik sin",
    "Miesiąc, składnik cos",
)


@dataclass(frozen=True)
class WspolczynnikModelu:
    nazwa: str
    wartosc: float

    @property
    def wartosc_etykieta(self) -> str:
        return formatuj_dziesietna(self.wartosc, 2)


@dataclass(frozen=True)
class PrognozaFrekwencji:
    n_uczace: int
    n_testowe: int
    mae: float
    rmse: float
    mae_sredniej_uczacej: float
    mae_sredniej_kroczacej: float
    wspolczynniki: tuple[WspolczynnikModelu, ...]

    @property
    def mae_etykieta(self) -> str:
        return formatuj_zaokraglona(self.mae)

    @property
    def rmse_etykieta(self) -> str:
        return formatuj_zaokraglona(self.rmse)

    @property
    def mae_sredniej_uczacej_etykieta(self) -> str:
        return formatuj_zaokraglona(self.mae_sredniej_uczacej)

    @property
    def mae_sredniej_kroczacej_etykieta(self) -> str:
        return formatuj_zaokraglona(self.mae_sredniej_kroczacej)

    @property
    def lepsza_od_sredniej(self) -> bool:
        return self.mae < self.mae_sredniej_uczacej


@dataclass(frozen=True)
class WynikPrognozy:
    prognoza: PrognozaFrekwencji | None
    powod_pominiecia: str | None = None


@dataclass(frozen=True)
class _WierszModelu:
    mecz: MeczProbki
    srednia_kroczaca: float
    weekend: float
    godzina: float | None
    sinus_miesiaca: float
    cosinus_miesiaca: float


class RegresjaOLS:
    def dopasuj(
        self, cechy: Sequence[Sequence[float]], cele: Sequence[float]
    ) -> tuple[float, ...] | None:
        if not cechy or len(cechy) != len(cele):
            return None
        wiersze = [(1.0, *wiersz) for wiersz in cechy]
        liczba = len(wiersze[0])
        macierz = [
            [sum(wiersz[i] * wiersz[j] for wiersz in wiersze) for j in range(liczba)]
            for i in range(liczba)
        ]
        for indeks in range(1, liczba):
            macierz[indeks][indeks] += REGULARYZACJA
        prawa = [
            sum(wiersz[i] * cel for wiersz, cel in zip(wiersze, cele, strict=True))
            for i in range(liczba)
        ]
        return self._rozwiaz(macierz, prawa)

    @staticmethod
    def _rozwiaz(macierz: list[list[float]], prawa: list[float]) -> tuple[float, ...] | None:
        liczba = len(prawa)
        uklad = [wiersz[:] + [wartosc] for wiersz, wartosc in zip(macierz, prawa, strict=True)]
        for kolumna in range(liczba):
            glowny = max(range(kolumna, liczba), key=lambda i: abs(uklad[i][kolumna]))
            if abs(uklad[glowny][kolumna]) < PROG_OSOBLIWOSCI:
                return None
            uklad[kolumna], uklad[glowny] = uklad[glowny], uklad[kolumna]
            for wiersz in range(liczba):
                if wiersz == kolumna:
                    continue
                mnoznik = uklad[wiersz][kolumna] / uklad[kolumna][kolumna]
                for indeks in range(kolumna, liczba + 1):
                    uklad[wiersz][indeks] -= mnoznik * uklad[kolumna][indeks]
        return tuple(uklad[i][liczba] / uklad[i][i] for i in range(liczba))


class PrognozaFrekwencjiCalculator:
    def __init__(self, regresja: RegresjaOLS) -> None:
        self._regresja = regresja

    def prognozuj(self, probka: Sequence[MeczProbki]) -> WynikPrognozy:
        wiersze = self._wiersze(probka)
        if len(wiersze) < MIN_MECZOW_PROGNOZY:
            return WynikPrognozy(
                None,
                f"Prognoza pominięta: za mało meczów z terminem i historią "
                f"(n={len(wiersze)}, wymagane co najmniej {MIN_MECZOW_PROGNOZY}).",
            )
        liczba_testowych = max(1, int(len(wiersze) * UDZIAL_TESTOWY))
        uczace, testowe = wiersze[:-liczba_testowych], wiersze[-liczba_testowych:]
        godziny = [wiersz.godzina for wiersz in uczace if wiersz.godzina is not None]
        srednia_godziny = sum(godziny) / len(godziny) if godziny else 0.0
        cechy_uczace = [self._cechy(wiersz, srednia_godziny) for wiersz in uczace]
        srednie, odchylenia = self._standaryzacja(cechy_uczace)
        cele_uczace = [float(wiersz.mecz.widzowie) for wiersz in uczace]
        wspolczynniki = self._regresja.dopasuj(
            [self._skaluj(cechy, srednie, odchylenia) for cechy in cechy_uczace], cele_uczace
        )
        if wspolczynniki is None:
            return WynikPrognozy(None, "Prognoza pominięta: nie udało się dopasować modelu.")
        return WynikPrognozy(
            self._ocen(
                testowe, uczace, wspolczynniki, srednie, odchylenia, srednia_godziny, cele_uczace
            )
        )

    def _ocen(
        self,
        testowe: Sequence[_WierszModelu],
        uczace: Sequence[_WierszModelu],
        wspolczynniki: tuple[float, ...],
        srednie: Sequence[float],
        odchylenia: Sequence[float],
        srednia_godziny: float,
        cele_uczace: Sequence[float],
    ) -> PrognozaFrekwencji:
        rzeczywiste = [float(wiersz.mecz.widzowie) for wiersz in testowe]
        przewidziane = [
            max(
                0.0,
                wspolczynniki[0]
                + sum(
                    waga * wartosc
                    for waga, wartosc in zip(
                        wspolczynniki[1:],
                        self._skaluj(self._cechy(wiersz, srednia_godziny), srednie, odchylenia),
                        strict=True,
                    )
                ),
            )
            for wiersz in testowe
        ]
        srednia_uczaca = sum(cele_uczace) / len(cele_uczace)
        kroczace = [wiersz.srednia_kroczaca for wiersz in testowe]
        return PrognozaFrekwencji(
            n_uczace=len(uczace),
            n_testowe=len(testowe),
            mae=self._mae(rzeczywiste, przewidziane),
            rmse=math.sqrt(
                sum((r - p) ** 2 for r, p in zip(rzeczywiste, przewidziane, strict=True))
                / len(rzeczywiste)
            ),
            mae_sredniej_uczacej=self._mae(rzeczywiste, [srednia_uczaca] * len(rzeczywiste)),
            mae_sredniej_kroczacej=self._mae(rzeczywiste, kroczace),
            wspolczynniki=tuple(
                WspolczynnikModelu(nazwa=nazwa, wartosc=waga / odchylenie)
                for nazwa, waga, odchylenie in zip(
                    NAZWY_CECH, wspolczynniki[1:], odchylenia, strict=True
                )
                if odchylenie > 0
            ),
        )

    @staticmethod
    def _mae(rzeczywiste: Sequence[float], przewidziane: Sequence[float]) -> float:
        return sum(abs(r - p) for r, p in zip(rzeczywiste, przewidziane, strict=True)) / len(
            rzeczywiste
        )

    def _wiersze(self, probka: Sequence[MeczProbki]) -> list[_WierszModelu]:
        mecze = sorted(
            (mecz for mecz in probka if mecz.termin is not None),
            key=lambda mecz: (mecz.termin or datetime.min, mecz.id_mecz),
        )
        historia: dict[int, list[int]] = {}
        suma, liczba = 0, 0
        wiersze: list[_WierszModelu] = []
        for _termin, grupa in groupby(mecze, key=lambda mecz: mecz.termin):
            rownoczesne = list(grupa)
            for mecz in rownoczesne:
                wiersz = self._wiersz(mecz, historia, suma, liczba)
                if wiersz is not None:
                    wiersze.append(wiersz)
            for mecz in rownoczesne:
                suma += mecz.widzowie
                liczba += 1
                if mecz.id_gospodarza is not None:
                    historia.setdefault(mecz.id_gospodarza, []).append(mecz.widzowie)
        return wiersze

    def _wiersz(
        self, mecz: MeczProbki, historia: dict[int, list[int]], suma: int, liczba: int
    ) -> _WierszModelu | None:
        dzien, miesiac = mecz.dzien, mecz.numer_miesiaca
        if dzien is None or miesiac is None:
            return None
        poprzednie = historia.get(mecz.id_gospodarza, []) if mecz.id_gospodarza is not None else []
        if poprzednie:
            ostatnie = poprzednie[-OKNO_SREDNIEJ_GOSPODARZA:]
            srednia = sum(ostatnie) / len(ostatnie)
        elif liczba:
            srednia = suma / liczba
        else:
            return None
        kat = 2 * math.pi * (miesiac - 1) / 12
        return _WierszModelu(
            mecz=mecz,
            srednia_kroczaca=srednia,
            weekend=1.0 if mecz.weekend else 0.0,
            godzina=float(mecz.godzina) if mecz.godzina is not None else None,
            sinus_miesiaca=math.sin(kat),
            cosinus_miesiaca=math.cos(kat),
        )

    @staticmethod
    def _cechy(wiersz: _WierszModelu, srednia_godziny: float) -> list[float]:
        godzina = wiersz.godzina if wiersz.godzina is not None else srednia_godziny
        return [
            wiersz.srednia_kroczaca,
            wiersz.weekend,
            godzina,
            wiersz.sinus_miesiaca,
            wiersz.cosinus_miesiaca,
        ]

    @staticmethod
    def _standaryzacja(cechy: Sequence[Sequence[float]]) -> tuple[list[float], list[float]]:
        liczba = len(cechy)
        srednie = [sum(wiersz[i] for wiersz in cechy) / liczba for i in range(len(cechy[0]))]
        odchylenia = [
            math.sqrt(sum((wiersz[i] - srednie[i]) ** 2 for wiersz in cechy) / liczba)
            for i in range(len(srednie))
        ]
        return srednie, odchylenia

    @staticmethod
    def _skaluj(
        cechy: Sequence[float], srednie: Sequence[float], odchylenia: Sequence[float]
    ) -> list[float]:
        return [
            (wartosc - srednia) / odchylenie if odchylenie > 0 else 0.0
            for wartosc, srednia, odchylenie in zip(cechy, srednie, odchylenia, strict=True)
        ]
