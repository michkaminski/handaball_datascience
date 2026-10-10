from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from handball.domain.attendance_calendar import nazwa_dnia
from handball.domain.attendance_forecast import PrognozaFrekwencjiCalculator, WynikPrognozy
from handball.domain.attendance_formatting import (
    PROG_MALEJ_PROBY,
    formatuj_calkowita,
    formatuj_roznice,
    formatuj_udzial,
    formatuj_wspolczynnik,
    formatuj_zaokraglona,
    percentyl,
)
from handball.domain.attendance_sample import LIMIT_PROBKI, MeczProbki

PERCENTYLE = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
MIN_PRZEDZIALOW = 5
MAX_PRZEDZIALOW = 20
MNOZNIK_IQR = 1.5
LIMIT_ANOMALII = 15
LIMIT_EFEKTU_PRZECIWNIKA = 30
MIN_PARY_KORELACJI = 3
UWAGA_O_KORELACJI = (
    "Korelacja opisuje współwystępowanie, a nie przyczynę. Wynik meczu jest znany dopiero po "
    "meczu, więc nie może tłumaczyć frekwencji, która jest znana przed gwizdkiem."
)
UWAGA_O_PROGNOZIE = (
    "Prognoza używa wyłącznie cech znanych przed meczem (dzień tygodnia, miesiąc, godzina, "
    "średnia wcześniejszych meczów gospodarza). Zbiór uczący to wcześniejsze 80% meczów w "
    "kolejności czasu, testowy to ostatnie 20%."
)
UWAGA_O_BRAKU_KLUBU = (
    "Efekt przeciwnika jest liczony tylko po wybraniu klubu w filtrze „Gospodarz”."
)


@dataclass(frozen=True)
class PrzedzialHistogramu:
    od: float
    do: float
    liczba: int

    @property
    def etykieta(self) -> str:
        return f"{formatuj_zaokraglona(self.od)}–{formatuj_zaokraglona(self.do)}"


@dataclass(frozen=True)
class PercentylFrekwencji:
    procent: int
    wartosc: float

    @property
    def wartosc_etykieta(self) -> str:
        return formatuj_zaokraglona(self.wartosc)


@dataclass(frozen=True)
class HistogramFrekwencji:
    przedzialy: tuple[PrzedzialHistogramu, ...]
    percentyle: tuple[PercentylFrekwencji, ...]


@dataclass(frozen=True)
class RozrzutFrekwencji:
    n: int
    srednia: float | None
    odchylenie: float | None
    wspolczynnik_zmiennosci: float | None

    @property
    def mala_proba(self) -> bool:
        return self.n < PROG_MALEJ_PROBY

    @property
    def srednia_etykieta(self) -> str:
        return formatuj_zaokraglona(self.srednia)

    @property
    def odchylenie_etykieta(self) -> str:
        return formatuj_zaokraglona(self.odchylenie)

    @property
    def wspolczynnik_etykieta(self) -> str:
        return formatuj_udzial(self.wspolczynnik_zmiennosci)

    @property
    def ostrzezenie(self) -> str | None:
        if not self.mala_proba:
            return None
        return (
            f"Mała próba (n={self.n} < {PROG_MALEJ_PROBY}): odchylenie standardowe "
            "i współczynnik zmienności są mało wiarygodne."
        )


@dataclass(frozen=True)
class AnomaliaFrekwencji:
    mecz: MeczProbki
    kierunek: str
    odchylenie: float

    @property
    def odchylenie_etykieta(self) -> str:
        return formatuj_roznice(self.odchylenie)


@dataclass(frozen=True)
class AnomalieFrekwencji:
    q1: float | None
    q3: float | None
    dolna_granica: float | None
    gorna_granica: float | None
    wysokie: tuple[AnomaliaFrekwencji, ...]
    niskie: tuple[AnomaliaFrekwencji, ...]
    liczba_wysokich: int
    liczba_niskich: int

    @property
    def ma_dane(self) -> bool:
        return self.gorna_granica is not None

    @property
    def dolna_etykieta(self) -> str:
        return formatuj_zaokraglona(self.dolna_granica)

    @property
    def gorna_etykieta(self) -> str:
        return formatuj_zaokraglona(self.gorna_granica)


@dataclass(frozen=True)
class GrupaEfektu:
    klucz: int
    etykieta: str
    n: int
    srednia: float
    mediana: float
    roznica: float

    @property
    def mala_proba(self) -> bool:
        return self.n < PROG_MALEJ_PROBY

    @property
    def n_etykieta(self) -> str:
        return formatuj_calkowita(self.n)

    @property
    def srednia_etykieta(self) -> str:
        return formatuj_zaokraglona(self.srednia)

    @property
    def mediana_etykieta(self) -> str:
        return formatuj_zaokraglona(self.mediana)

    @property
    def roznica_etykieta(self) -> str:
        return formatuj_roznice(self.roznica)


@dataclass(frozen=True)
class KorelacjaFrekwencji:
    nazwa: str
    n: int
    wspolczynnik: float | None

    @property
    def wspolczynnik_etykieta(self) -> str:
        return formatuj_wspolczynnik(self.wspolczynnik)

    @property
    def mala_proba(self) -> bool:
        return self.n < PROG_MALEJ_PROBY

    @property
    def sila(self) -> str:
        if self.wspolczynnik is None:
            return "brak danych"
        modul = abs(self.wspolczynnik)
        if modul < 0.1:
            return "pomijalna"
        if modul < 0.3:
            return "słaba"
        if modul < 0.5:
            return "umiarkowana"
        return "silna"

    @property
    def kierunek(self) -> str:
        if self.wspolczynnik is None or self.sila == "pomijalna":
            return "—"
        return "dodatnia" if self.wspolczynnik > 0 else "ujemna"


@dataclass(frozen=True)
class AnalizaDataScience:
    n: int
    ucieta: bool
    histogram: HistogramFrekwencji | None
    rozrzut: RozrzutFrekwencji
    anomalie: AnomalieFrekwencji
    dni_tygodnia: tuple[GrupaEfektu, ...]
    przeciwnicy: tuple[GrupaEfektu, ...] | None
    korelacje: tuple[KorelacjaFrekwencji, ...]
    prognoza: WynikPrognozy

    @property
    def ma_dane(self) -> bool:
        return self.n > 0

    @property
    def uwaga_o_probce(self) -> str | None:
        if not self.ucieta:
            return None
        return (
            f"Analiza obejmuje {formatuj_calkowita(self.n)} najnowszych meczów "
            f"(limit próbki {formatuj_calkowita(LIMIT_PROBKI)})."
        )

    @property
    def uwaga_o_korelacji(self) -> str:
        return UWAGA_O_KORELACJI

    @property
    def uwaga_o_prognozie(self) -> str:
        return UWAGA_O_PROGNOZIE

    @property
    def uwaga_o_braku_klubu(self) -> str:
        return UWAGA_O_BRAKU_KLUBU


def pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    if len(x) != len(y) or len(x) < MIN_PARY_KORELACJI:
        return None
    srednia_x, srednia_y = sum(x) / len(x), sum(y) / len(y)
    suma_xy = sum((a - srednia_x) * (b - srednia_y) for a, b in zip(x, y, strict=True))
    suma_xx = sum((a - srednia_x) ** 2 for a in x)
    suma_yy = sum((b - srednia_y) ** 2 for b in y)
    if suma_xx == 0 or suma_yy == 0:
        return None
    return suma_xy / math.sqrt(suma_xx * suma_yy)


class FrekwencjaDataScienceCalculator:
    def __init__(self, prognoza: PrognozaFrekwencjiCalculator) -> None:
        self._prognoza = prognoza

    def analizuj(
        self,
        probka: Sequence[MeczProbki],
        znane_w_filtrze: int,
        id_zespol: int | None,
    ) -> AnalizaDataScience:
        wartosci = [float(mecz.widzowie) for mecz in probka]
        return AnalizaDataScience(
            n=len(probka),
            ucieta=znane_w_filtrze > len(probka),
            histogram=self.histogram(wartosci),
            rozrzut=self.rozrzut(wartosci),
            anomalie=self.anomalie(probka),
            dni_tygodnia=self.efekt_dnia_tygodnia(probka),
            przeciwnicy=self.efekt_przeciwnika(probka) if id_zespol is not None else None,
            korelacje=self.korelacje(probka),
            prognoza=self._prognoza.prognozuj(probka),
        )

    def histogram(self, wartosci: Sequence[float]) -> HistogramFrekwencji | None:
        if not wartosci:
            return None
        percentyle = tuple(
            PercentylFrekwencji(round(ulamek * 100), wynik)
            for ulamek in PERCENTYLE
            if (wynik := percentyl(wartosci, ulamek)) is not None
        )
        return HistogramFrekwencji(przedzialy=self._przedzialy(wartosci), percentyle=percentyle)

    @staticmethod
    def _przedzialy(wartosci: Sequence[float]) -> tuple[PrzedzialHistogramu, ...]:
        minimum, maksimum = min(wartosci), max(wartosci)
        if minimum == maksimum:
            return (PrzedzialHistogramu(minimum, maksimum, len(wartosci)),)
        liczba = min(MAX_PRZEDZIALOW, max(MIN_PRZEDZIALOW, round(math.sqrt(len(wartosci)))))
        szerokosc = (maksimum - minimum) / liczba
        zliczenia = [0] * liczba
        for wartosc in wartosci:
            zliczenia[min(int((wartosc - minimum) / szerokosc), liczba - 1)] += 1
        return tuple(
            PrzedzialHistogramu(
                minimum + indeks * szerokosc, minimum + (indeks + 1) * szerokosc, zliczenie
            )
            for indeks, zliczenie in enumerate(zliczenia)
        )

    def rozrzut(self, wartosci: Sequence[float]) -> RozrzutFrekwencji:
        n = len(wartosci)
        if n == 0:
            return RozrzutFrekwencji(0, None, None, None)
        srednia = sum(wartosci) / n
        if n < 2:
            return RozrzutFrekwencji(n, srednia, None, None)
        odchylenie = math.sqrt(sum((w - srednia) ** 2 for w in wartosci) / (n - 1))
        wspolczynnik = odchylenie / srednia if srednia > 0 else None
        return RozrzutFrekwencji(n, srednia, odchylenie, wspolczynnik)

    def anomalie(self, probka: Sequence[MeczProbki]) -> AnomalieFrekwencji:
        wartosci = [float(mecz.widzowie) for mecz in probka]
        q1, q3 = percentyl(wartosci, 0.25), percentyl(wartosci, 0.75)
        if q1 is None or q3 is None or len(wartosci) < 4:
            return AnomalieFrekwencji(q1, q3, None, None, (), (), 0, 0)
        iqr = q3 - q1
        dolna, gorna = q1 - MNOZNIK_IQR * iqr, q3 + MNOZNIK_IQR * iqr
        wysokie = sorted(
            (
                AnomaliaFrekwencji(mecz, "wysoka", mecz.widzowie - gorna)
                for mecz in probka
                if mecz.widzowie > gorna
            ),
            key=lambda anomalia: (-anomalia.odchylenie, anomalia.mecz.id_mecz),
        )
        niskie = sorted(
            (
                AnomaliaFrekwencji(mecz, "niska", mecz.widzowie - dolna)
                for mecz in probka
                if mecz.widzowie < dolna
            ),
            key=lambda anomalia: (anomalia.odchylenie, anomalia.mecz.id_mecz),
        )
        return AnomalieFrekwencji(
            q1=q1,
            q3=q3,
            dolna_granica=dolna,
            gorna_granica=gorna,
            wysokie=tuple(wysokie[:LIMIT_ANOMALII]),
            niskie=tuple(niskie[:LIMIT_ANOMALII]),
            liczba_wysokich=len(wysokie),
            liczba_niskich=len(niskie),
        )

    def efekt_dnia_tygodnia(self, probka: Sequence[MeczProbki]) -> tuple[GrupaEfektu, ...]:
        return self._grupy(
            probka,
            klucz=lambda mecz: mecz.dzien,
            etykieta=lambda klucz, _mecz: nazwa_dnia(klucz),
            sortowanie=lambda grupa: grupa.klucz,
        )

    def efekt_przeciwnika(self, probka: Sequence[MeczProbki]) -> tuple[GrupaEfektu, ...]:
        grupy = self._grupy(
            probka,
            klucz=lambda mecz: mecz.id_goscia,
            etykieta=lambda _klucz, mecz: mecz.gosc,
            sortowanie=lambda grupa: -grupa.srednia,
        )
        return grupy[:LIMIT_EFEKTU_PRZECIWNIKA]

    def korelacje(self, probka: Sequence[MeczProbki]) -> tuple[KorelacjaFrekwencji, ...]:
        wskazniki: tuple[tuple[str, Callable[[MeczProbki], int | None]], ...] = (
            ("Różnica bramek (gospodarz − gość)", lambda mecz: mecz.roznica_bramek),
            ("Suma bramek w meczu", lambda mecz: mecz.suma_bramek),
        )
        return tuple(self._korelacja(nazwa, probka, wskaznik) for nazwa, wskaznik in wskazniki)

    @staticmethod
    def _korelacja(
        nazwa: str, probka: Sequence[MeczProbki], wskaznik: Callable[[MeczProbki], int | None]
    ) -> KorelacjaFrekwencji:
        pary = [
            (float(mecz.widzowie), float(wartosc))
            for mecz in probka
            if (wartosc := wskaznik(mecz)) is not None
        ]
        return KorelacjaFrekwencji(
            nazwa=nazwa,
            n=len(pary),
            wspolczynnik=pearson([widzowie for widzowie, _ in pary], [w for _, w in pary]),
        )

    @staticmethod
    def _grupy(
        probka: Sequence[MeczProbki],
        klucz: Callable[[MeczProbki], int | None],
        etykieta: Callable[[int, MeczProbki], str],
        sortowanie: Callable[[GrupaEfektu], float],
    ) -> tuple[GrupaEfektu, ...]:
        if not probka:
            return ()
        ogolna = sum(mecz.widzowie for mecz in probka) / len(probka)
        mecze_grup: dict[int, list[MeczProbki]] = defaultdict(list)
        for mecz in probka:
            wartosc = klucz(mecz)
            if wartosc is not None:
                mecze_grup[wartosc].append(mecz)
        grupy = (
            GrupaEfektu(
                klucz=wartosc,
                etykieta=etykieta(wartosc, mecze[0]),
                n=len(mecze),
                srednia=sum(mecz.widzowie for mecz in mecze) / len(mecze),
                mediana=percentyl([mecz.widzowie for mecz in mecze], 0.5) or 0.0,
                roznica=sum(mecz.widzowie for mecz in mecze) / len(mecze) - ogolna,
            )
            for wartosc, mecze in mecze_grup.items()
        )
        return tuple(sorted(grupy, key=lambda grupa: (sortowanie(grupa), grupa.klucz)))
