from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from handball.domain.match_report import PunktRatingu, SciezkaRatingu


def liczba(wartosc: float, miejsca: int = 1) -> str:
    tekst = f"{wartosc:.{miejsca}f}".replace(".", ",")
    return tekst.replace("-", "−")


def ze_znakiem(wartosc: float, miejsca: int = 1) -> str:
    if round(wartosc, miejsca) == 0:
        return liczba(0, miejsca)
    return ("+" if wartosc > 0 else "") + liczba(wartosc, miejsca)


@dataclass(frozen=True)
class Slupek:
    x: float
    y: float
    szerokosc: float
    wysokosc: float
    ogon: bool


@dataclass(frozen=True)
class Podzialka:
    pozycja: float
    etykieta: str


@dataclass(frozen=True)
class HistogramReszt:
    szerokosc: int
    wysokosc: int
    slupki: tuple[Slupek, ...]
    krzywa: str
    znacznik_x: float
    znacznik_etykieta: str
    etykieta_x: float
    etykieta_szerokosc: float
    os_x: tuple[Podzialka, ...]
    zero_x: float
    os_y: float


class HistogramResztBuilder:
    SZEROKOSC = 300
    WYSOKOSC = 74
    DOL = 62
    ZAKRES = 20
    KROK = 2

    def zbuduj(self, reszty: Sequence[float], reszta: float, sigma: float) -> HistogramReszt:
        kosze = Counter(
            min(self.ZAKRES - self.KROK, max(-self.ZAKRES, math.floor(r / self.KROK) * self.KROK))
            for r in reszty
        )
        najwiecej = max(kosze.values()) if kosze else 1
        skala_y = (self.DOL - 16) / najwiecej
        prog = abs(reszta)
        slupki = tuple(
            Slupek(
                x=self._x(poczatek) + 0.6,
                y=self.DOL - kosze[poczatek] * skala_y,
                szerokosc=self._x(poczatek + self.KROK) - self._x(poczatek) - 1.2,
                wysokosc=kosze[poczatek] * skala_y,
                ogon=poczatek >= prog or poczatek + self.KROK <= -prog,
            )
            for poczatek in range(-self.ZAKRES, self.ZAKRES, self.KROK)
        )
        n = len(reszty)
        punkty = []
        for krok in range(0, 161):
            r = -self.ZAKRES + krok * self.ZAKRES * 2 / 160
            gestosc = math.exp(-0.5 * (r / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
            punkty.append(f"{self._x(r):.1f},{self.DOL - gestosc * n * self.KROK * skala_y:.1f}")
        znacznik = self._x(max(-self.ZAKRES + 0.3, min(self.ZAKRES - 0.3, reszta)))
        etykieta = f"ten mecz {ze_znakiem(reszta)}"
        szerokosc_etykiety = len(etykieta) * 4.6 + 4
        etykieta_x = (
            znacznik - 3 - szerokosc_etykiety if znacznik > self.SZEROKOSC * 0.7 else znacznik + 3
        )
        return HistogramReszt(
            szerokosc=self.SZEROKOSC,
            wysokosc=self.WYSOKOSC,
            slupki=slupki,
            krzywa=" ".join(punkty),
            znacznik_x=znacznik,
            znacznik_etykieta=etykieta,
            etykieta_x=etykieta_x,
            etykieta_szerokosc=szerokosc_etykiety,
            os_x=tuple(Podzialka(self._x(w), ze_znakiem(w, 0)) for w in range(-15, 16, 5)),
            zero_x=self._x(0),
            os_y=self.DOL,
        )

    def _x(self, wartosc: float) -> float:
        return 4 + (wartosc + self.ZAKRES) / (2 * self.ZAKRES) * (self.SZEROKOSC - 8)


@dataclass(frozen=True)
class LiniaRatingu:
    klasa: str
    odcinki: tuple[str, ...]
    kropki: tuple[tuple[float, float], ...]
    koniec_x: float
    koniec_y: float
    etykieta: str
    etykieta_y: float


@dataclass(frozen=True)
class WykresRatingu:
    szerokosc: int
    wysokosc: int
    linie: tuple[LiniaRatingu, ...]
    os_y: tuple[Podzialka, ...]
    os_x: tuple[Podzialka, ...]
    separatory: tuple[float, ...]
    srednia_y: float | None
    analizowany_x: float
    os_dol: float
    prawa_krawedz: float


class WykresRatinguBuilder:
    SZEROKOSC = 600
    WYSOKOSC = 86
    LEWO = 34
    PRAWO = 122
    GORA = 8
    DOL = 72

    def zbuduj(self, sciezki: Sequence[tuple[str, SciezkaRatingu, str]]) -> WykresRatingu | None:
        wybrane = [
            (klasa, s.punkty[1:] if len(s.punkty) > 2 else s.punkty, nazwa)
            for klasa, s, nazwa in sciezki
            if s.punkty
        ]
        punkty = [p for _, lista, _ in wybrane for p in lista]
        if len(punkty) < 3:
            return None
        daty = sorted({p.data for p in punkty})
        indeks = {data: numer for numer, data in enumerate(daty)}
        sezony = {p.data: p.sezon for p in punkty}
        ratingi = [p.rating for p in punkty]
        dol = math.floor((min(ratingi) - 10) / 50) * 50
        gora = math.ceil((max(ratingi) + 10) / 50) * 50
        szerokosc_osi = self.SZEROKOSC - self.LEWO - self.PRAWO

        def x(data: datetime) -> float:
            if len(daty) == 1:
                return self.SZEROKOSC - self.PRAWO
            return self.LEWO + 6 + indeks[data] / (len(daty) - 1) * (szerokosc_osi - 12)

        def y(rating: float) -> float:
            return self.DOL - (rating - dol) / (gora - dol) * (self.DOL - self.GORA)

        linie = []
        for klasa, lista, nazwa in wybrane:
            ostatni = lista[-1]
            wspolrzedne = [(x(p.data), y(p.rating)) for p in lista]
            linie.append(
                LiniaRatingu(
                    klasa=klasa,
                    odcinki=self._odcinki(lista, wspolrzedne),
                    kropki=tuple(wspolrzedne),
                    koniec_x=wspolrzedne[-1][0],
                    koniec_y=wspolrzedne[-1][1],
                    etykieta=f"{nazwa} {ostatni.rating:.0f}",
                    etykieta_y=wspolrzedne[-1][1],
                )
            )
        if len(linie) == 2 and abs(linie[0].etykieta_y - linie[1].etykieta_y) < 11:
            gorna, dolna = sorted(linie, key=lambda linia: linia.etykieta_y)
            srodek = (gorna.etykieta_y + dolna.etykieta_y) / 2
            linie = [_przesun(gorna, srodek - 5.5), _przesun(dolna, srodek + 5.5)]
        separatory = []
        etykiety = []
        poczatek = 0
        for numer in range(1, len(daty) + 1):
            if numer == len(daty) or sezony[daty[numer]] != sezony[daty[poczatek]]:
                srodek = (x(daty[poczatek]) + x(daty[numer - 1])) / 2
                etykiety.append(Podzialka(srodek, f"sezon {sezony[daty[poczatek]]}"))
                if numer < len(daty):
                    separatory.append((x(daty[numer - 1]) + x(daty[numer])) / 2)
                poczatek = numer
        krok = 50 if gora - dol <= 300 else 100
        return WykresRatingu(
            szerokosc=self.SZEROKOSC,
            wysokosc=self.WYSOKOSC,
            linie=tuple(linie),
            os_y=tuple(Podzialka(y(r), f"{r}") for r in range(dol, gora + 1, krok)),
            os_x=tuple(etykiety),
            separatory=tuple(separatory),
            srednia_y=y(1500) if dol <= 1500 <= gora else None,
            analizowany_x=x(daty[-1]),
            os_dol=self.DOL,
            prawa_krawedz=self.SZEROKOSC - self.PRAWO,
        )

    def _odcinki(
        self, punkty: Sequence[PunktRatingu], wspolrzedne: Sequence[tuple[float, float]]
    ) -> tuple[str, ...]:
        odcinki: list[list[tuple[float, float]]] = []
        poprzedni: str | None = None
        for punkt, xy in zip(punkty, wspolrzedne, strict=True):
            if punkt.sezon != poprzedni:
                odcinki.append([])
                poprzedni = punkt.sezon
            odcinki[-1].append(xy)
        return tuple(" ".join(f"{a:.1f},{b:.1f}" for a, b in o) for o in odcinki)


def _przesun(linia: LiniaRatingu, etykieta_y: float) -> LiniaRatingu:
    return LiniaRatingu(
        linia.klasa,
        linia.odcinki,
        linia.kropki,
        linia.koniec_x,
        linia.koniec_y,
        linia.etykieta,
        etykieta_y,
    )


@dataclass(frozen=True)
class Kropka:
    x: float
    y: float
    biezaca: bool


@dataclass(frozen=True)
class RzadPunktow:
    etykieta: str
    y: float
    kropki: tuple[Kropka, ...]
    srednia_x: float | None


@dataclass(frozen=True)
class WykresSezonu:
    szerokosc: int
    wysokosc: int
    rzedy: tuple[RzadPunktow, ...]
    os_x: tuple[Podzialka, ...]


class WykresSezonuBuilder:
    SZEROKOSC = 260
    WYSOKOSC = 42
    LEWO = 44
    PRAWO = 8

    def zbuduj(self, rzedy: Sequence[tuple[str, Sequence[int], int | None]]) -> WykresSezonu | None:
        wartosci = [v for _, proba, _ in rzedy for v in proba] + [
            b for _, _, b in rzedy if b is not None
        ]
        if not wartosci:
            return None
        dol = min(wartosci) - 1
        gora = max(wartosci) + 1

        def x(v: float) -> float:
            return self.LEWO + (v - dol) / (gora - dol) * (self.SZEROKOSC - self.LEWO - self.PRAWO)

        wynik = []
        for numer, (etykieta, proba, biezaca) in enumerate(rzedy):
            srodek = 8 + numer * 14
            licznik: Counter[int] = Counter()
            kropki = []
            for v in sorted(proba):
                poziom = licznik[v]
                licznik[v] += 1
                przesuniecie = ((poziom + 1) // 2) * 2.6 * (1 if poziom % 2 else -1)
                kropki.append(Kropka(x(v), srodek + przesuniecie, False))
            if biezaca is not None:
                kropki.append(Kropka(x(biezaca), srodek, True))
            srednia = sum(proba) / len(proba) if proba else None
            wynik.append(
                RzadPunktow(
                    etykieta, srodek, tuple(kropki), x(srednia) if srednia is not None else None
                )
            )
        krok = 5 if gora - dol <= 30 else 10
        start = math.ceil(dol / krok) * krok
        return WykresSezonu(
            szerokosc=self.SZEROKOSC,
            wysokosc=self.WYSOKOSC,
            rzedy=tuple(wynik),
            os_x=tuple(Podzialka(x(v), str(v)) for v in range(start, gora + 1, krok)),
        )
