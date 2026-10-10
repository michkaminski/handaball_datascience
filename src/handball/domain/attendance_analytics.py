from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from handball.domain.attendance_calendar import KalendarzFrekwencji
from handball.domain.attendance_cities import RaportMiast
from handball.domain.attendance_data_science import AnalizaDataScience
from handball.domain.attendance_formatting import (
    PROG_MALEJ_PROBY,
    formatuj_calkowita,
    formatuj_opcjonalna_calkowita,
    formatuj_procent,
    formatuj_roznice,
    formatuj_udzial,
    formatuj_zaokraglona,
    formatuj_zmiane,
    wypelnienie_procent,
)
from handball.domain.attendance_formatting import percentyl as percentyl
from handball.domain.attendance_formatting import zmiana_wzgledna as zmiana_wzgledna
from handball.domain.attendance_opponents import RankingPrzeciwnikow
from handball.domain.attendance_records import RekordFrekwencji as RekordFrekwencji
from handball.domain.attendance_records import RekordyRozszerzoneFrekwencji
from handball.domain.goal_distribution import DOZWOLONE_PLCI, OpcjaFiltrow

LIMIT_REKORDOW = 50
LIMIT_RANKINGU = 100
OKNO_SREDNIEJ_KROCZACEJ = 3
UWAGA_O_BRAKACH = "Mecze bez znanej frekwencji nie wchodzą do średniej, mediany ani sumy."
UWAGA_O_POJEMNOSCI = (
    "Pojemność hal nie jest znana dla wybranych meczów, więc wypełnienie nie jest pokazywane."
)


@dataclass(frozen=True)
class FiltryFrekwencji:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    plec: str | None = None
    id_zespol: int | None = None
    id_hala: int | None = None
    bez_zer: bool = False

    def __post_init__(self) -> None:
        if self.plec is not None and self.plec not in DOZWOLONE_PLCI:
            raise ValueError("nieobsługiwana płeć")

    def bez_sezonu(self) -> FiltryFrekwencji:
        return replace(self, id_sezon=None)


@dataclass(frozen=True)
class OpcjeFiltrowFrekwencji:
    sezony: tuple[OpcjaFiltrow, ...]
    rozgrywki: tuple[OpcjaFiltrow, ...]
    kluby: tuple[OpcjaFiltrow, ...]
    hale: tuple[OpcjaFiltrow, ...]


@dataclass(frozen=True)
class PodsumowanieFrekwencji:
    rozegrane: int
    znane: int
    suma: int
    srednia: float | None
    mediana: float | None
    q1: float | None
    q3: float | None
    minimum: int | None
    maksimum: int | None
    mecze_zero: int = 0
    widzowie_z_pojemnoscia: int = 0
    pojemnosc_laczna: int = 0

    def __post_init__(self) -> None:
        if self.rozegrane < 0 or self.znane < 0 or self.mecze_zero < 0:
            raise ValueError("liczba meczów nie może być ujemna")
        if self.znane > self.rozegrane:
            raise ValueError("mecze ze znaną frekwencją nie mogą przekraczać rozegranych")

    @property
    def pominiete(self) -> int:
        return self.rozegrane - self.znane

    @property
    def pokrycie(self) -> float | None:
        if self.rozegrane == 0:
            return None
        return self.znane / self.rozegrane

    @property
    def wypelnienie(self) -> float | None:
        return wypelnienie_procent(self.widzowie_z_pojemnoscia, self.pojemnosc_laczna)

    @property
    def mala_proba(self) -> bool:
        return 0 < self.znane < PROG_MALEJ_PROBY

    @property
    def rozegrane_etykieta(self) -> str:
        return formatuj_calkowita(self.rozegrane)

    @property
    def znane_etykieta(self) -> str:
        return formatuj_calkowita(self.znane)

    @property
    def suma_etykieta(self) -> str:
        return formatuj_calkowita(self.suma)

    @property
    def pokrycie_etykieta(self) -> str:
        return formatuj_udzial(self.pokrycie)

    @property
    def srednia_etykieta(self) -> str:
        return formatuj_zaokraglona(self.srednia)

    @property
    def mediana_etykieta(self) -> str:
        return formatuj_zaokraglona(self.mediana)

    @property
    def q1_etykieta(self) -> str:
        return formatuj_zaokraglona(self.q1)

    @property
    def q3_etykieta(self) -> str:
        return formatuj_zaokraglona(self.q3)

    @property
    def minimum_etykieta(self) -> str:
        return formatuj_opcjonalna_calkowita(self.minimum)

    @property
    def maksimum_etykieta(self) -> str:
        return formatuj_opcjonalna_calkowita(self.maksimum)

    @property
    def wypelnienie_etykieta(self) -> str:
        return formatuj_procent(self.wypelnienie)


@dataclass(frozen=True)
class SezonFrekwencji:
    id_sezon: int
    nazwa: str
    rok_poczatku: int | None
    podsumowanie: PodsumowanieFrekwencji


@dataclass(frozen=True)
class PunktTrendu:
    sezon: SezonFrekwencji
    zmiana: float | None
    srednia_kroczaca: float | None

    @property
    def zmiana_etykieta(self) -> str:
        return formatuj_zmiane(self.zmiana)

    @property
    def srednia_kroczaca_etykieta(self) -> str:
        return formatuj_zaokraglona(self.srednia_kroczaca)


@dataclass(frozen=True)
class TrendFrekwencji:
    punkty: tuple[PunktTrendu, ...]
    nachylenie: float | None

    @property
    def nachylenie_etykieta(self) -> str:
        if self.nachylenie is None:
            return "—"
        return f"{formatuj_roznice(self.nachylenie)} widzów na sezon"


@dataclass(frozen=True)
class ParaSezonow:
    cel: PunktTrendu
    poprzedni: PunktTrendu

    @property
    def zmiana(self) -> float | None:
        return zmiana_wzgledna(
            self.cel.sezon.podsumowanie.srednia, self.poprzedni.sezon.podsumowanie.srednia
        )

    @property
    def zmiana_etykieta(self) -> str:
        return formatuj_zmiane(self.zmiana)

    @property
    def opis(self) -> str:
        return f"{self.cel.sezon.nazwa} vs {self.poprzedni.sezon.nazwa}"


@dataclass(frozen=True)
class KlubFrekwencji:
    id_zespol: int
    nazwa: str
    podsumowanie: PodsumowanieFrekwencji


@dataclass(frozen=True)
class SredniaKlubuSezonu:
    id_zespol: int
    id_sezon: int
    srednia: float


@dataclass(frozen=True)
class WierszRankingu:
    pozycja: int
    klub: KlubFrekwencji
    zmiana: float | None

    @property
    def zmiana_etykieta(self) -> str:
        return formatuj_zmiane(self.zmiana)


@dataclass(frozen=True)
class RaportFrekwencji:
    filtry: FiltryFrekwencji
    podsumowanie: PodsumowanieFrekwencji
    trend: TrendFrekwencji
    para_sezonow: ParaSezonow | None
    ranking: tuple[WierszRankingu, ...]
    rekordy: tuple[RekordFrekwencji, ...]
    rekordy_rozszerzone: RekordyRozszerzoneFrekwencji
    przeciwnicy: RankingPrzeciwnikow
    kalendarz: KalendarzFrekwencji
    data_science: AnalizaDataScience
    miasta: RaportMiast

    @property
    def rekord(self) -> RekordFrekwencji | None:
        return self.rekordy[0] if self.rekordy else None

    @property
    def zmiana_etykieta(self) -> str:
        if self.para_sezonow is None:
            return "—"
        return self.para_sezonow.zmiana_etykieta

    @property
    def zmiana_opis(self) -> str:
        if self.para_sezonow is None:
            return "Brak porównywalnego poprzedniego sezonu"
        return f"Średnia, {self.para_sezonow.opis}"

    @property
    def ma_wypelnienie(self) -> bool:
        return self.podsumowanie.wypelnienie is not None

    @property
    def uwagi(self) -> tuple[str, ...]:
        podsumowanie = self.podsumowanie
        uwagi = [
            UWAGA_O_BRAKACH,
            f"Znana frekwencja: {podsumowanie.znane_etykieta} z "
            f"{podsumowanie.rozegrane_etykieta} rozegranych meczów "
            f"({podsumowanie.pokrycie_etykieta}).",
        ]
        if podsumowanie.mecze_zero:
            liczba = formatuj_calkowita(podsumowanie.mecze_zero)
            if self.filtry.bez_zer:
                uwagi.append(f"{liczba} meczów bez publiczności (0 widzów) pominięto filtrem.")
            else:
                uwagi.append(
                    f"{liczba} meczów bez publiczności (0 widzów) liczy się jako znana frekwencja."
                )
        if not self.ma_wypelnienie:
            uwagi.append(UWAGA_O_POJEMNOSCI)
        return tuple(uwagi)


class FrekwencjaCalculator:
    def znane_wartosci(
        self, wartosci: Sequence[int | None], bez_zer: bool = False
    ) -> tuple[int, ...]:
        return tuple(
            wartosc
            for wartosc in wartosci
            if wartosc is not None and wartosc >= 0 and not (bez_zer and wartosc == 0)
        )

    def podsumuj(
        self, wartosci: Sequence[int | None], bez_zer: bool = False
    ) -> PodsumowanieFrekwencji:
        znane = self.znane_wartosci(wartosci, bez_zer)
        suma = sum(znane)
        return PodsumowanieFrekwencji(
            rozegrane=len(wartosci),
            znane=len(znane),
            suma=suma,
            srednia=suma / len(znane) if znane else None,
            mediana=percentyl(znane, 0.5),
            q1=percentyl(znane, 0.25),
            q3=percentyl(znane, 0.75),
            minimum=min(znane) if znane else None,
            maksimum=max(znane) if znane else None,
            mecze_zero=sum(1 for wartosc in wartosci if wartosc == 0),
        )

    def srednia_kroczaca(
        self, wartosci: Sequence[float | None], okno: int = OKNO_SREDNIEJ_KROCZACEJ
    ) -> tuple[float | None, ...]:
        if okno < 1:
            raise ValueError("okno musi być dodatnie")
        wynik: list[float | None] = []
        for indeks, wartosc in enumerate(wartosci):
            if wartosc is None:
                wynik.append(None)
                continue
            poczatek = max(0, indeks - okno + 1)
            ostatnie = [
                pozycja for pozycja in wartosci[poczatek : indeks + 1] if pozycja is not None
            ]
            wynik.append(sum(ostatnie) / len(ostatnie))
        return tuple(wynik)

    def nachylenie(self, punkty: Sequence[tuple[float, float | None]]) -> float | None:
        znane = [(x, y) for x, y in punkty if y is not None]
        if len(znane) < 2:
            return None
        srednia_x = sum(x for x, _ in znane) / len(znane)
        srednia_y = sum(y for _, y in znane) / len(znane)
        wariancja = sum((x - srednia_x) ** 2 for x, _ in znane)
        if wariancja == 0:
            return None
        return sum((x - srednia_x) * (y - srednia_y) for x, y in znane) / wariancja

    def zbuduj_trend(self, sezony: Sequence[SezonFrekwencji]) -> TrendFrekwencji:
        uporzadkowane = sorted(
            sezony,
            key=lambda sezon: (
                sezon.rok_poczatku is not None,
                sezon.rok_poczatku or 0,
                sezon.id_sezon,
            ),
        )
        srednie = [sezon.podsumowanie.srednia for sezon in uporzadkowane]
        kroczace = self.srednia_kroczaca(srednie)
        punkty = tuple(
            PunktTrendu(
                sezon=sezon,
                zmiana=zmiana_wzgledna(srednie[indeks], srednie[indeks - 1] if indeks else None),
                srednia_kroczaca=kroczace[indeks],
            )
            for indeks, sezon in enumerate(uporzadkowane)
        )
        nachylenie = self.nachylenie(
            [
                (float(sezon.rok_poczatku), srednia)
                for sezon, srednia in zip(uporzadkowane, srednie, strict=True)
                if sezon.rok_poczatku is not None
            ]
        )
        return TrendFrekwencji(punkty=punkty, nachylenie=nachylenie)

    def para_sezonow(self, trend: TrendFrekwencji, wybrany_sezon: int | None) -> ParaSezonow | None:
        indeks = self._indeks_celu(trend.punkty, wybrany_sezon)
        if indeks is None or indeks == 0:
            return None
        cel, poprzedni = trend.punkty[indeks], trend.punkty[indeks - 1]
        if cel.sezon.podsumowanie.srednia is None or poprzedni.sezon.podsumowanie.srednia is None:
            return None
        return ParaSezonow(cel=cel, poprzedni=poprzedni)

    def uloz_ranking(
        self,
        kluby: Sequence[KlubFrekwencji],
        srednie_sezonow: Sequence[SredniaKlubuSezonu],
        para: ParaSezonow | None,
        limit: int = LIMIT_RANKINGU,
    ) -> tuple[WierszRankingu, ...]:
        srednie: Mapping[tuple[int, int], float] = {
            (pozycja.id_zespol, pozycja.id_sezon): pozycja.srednia for pozycja in srednie_sezonow
        }
        kwalifikujace = sorted(
            (klub for klub in kluby if klub.podsumowanie.srednia is not None),
            key=lambda klub: (
                -(klub.podsumowanie.srednia or 0.0),
                -klub.podsumowanie.znane,
                klub.nazwa.casefold(),
                klub.id_zespol,
            ),
        )
        return tuple(
            WierszRankingu(
                pozycja=pozycja,
                klub=klub,
                zmiana=self._zmiana_klubu(klub.id_zespol, srednie, para),
            )
            for pozycja, klub in enumerate(kwalifikujace[:limit], start=1)
        )

    def _indeks_celu(self, punkty: Sequence[PunktTrendu], wybrany_sezon: int | None) -> int | None:
        if wybrany_sezon is not None:
            for indeks, punkt in enumerate(punkty):
                if punkt.sezon.id_sezon == wybrany_sezon:
                    return indeks
            return None
        for indeks in range(len(punkty) - 1, -1, -1):
            if punkty[indeks].sezon.podsumowanie.srednia is not None:
                return indeks
        return None

    def _zmiana_klubu(
        self, id_zespol: int, srednie: Mapping[tuple[int, int], float], para: ParaSezonow | None
    ) -> float | None:
        if para is None:
            return None
        return zmiana_wzgledna(
            srednie.get((id_zespol, para.cel.sezon.id_sezon)),
            srednie.get((id_zespol, para.poprzedni.sezon.id_sezon)),
        )
