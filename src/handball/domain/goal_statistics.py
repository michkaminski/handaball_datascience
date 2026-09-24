from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class MeczZBramkami(Protocol):
    @property
    def id_mecz(self) -> int: ...

    @property
    def termin(self) -> datetime | None: ...

    @property
    def sezon(self) -> str: ...

    @property
    def rozgrywki(self) -> str: ...

    @property
    def bramki(self) -> int | None: ...

    @property
    def miejsce(self) -> str | None: ...


@dataclass(frozen=True)
class PunktFormy:
    id_mecz: int
    termin: datetime | None
    sezon: str
    bramki: int | None
    mediana_kroczaca_5: float | None
    srednia_kroczaca_5: float | None
    mediana_kroczaca_10: float | None


@dataclass(frozen=True)
class StatystykiBramekGrupy:
    liczba_meczow: int
    liczba_znanych: int
    suma: int | None
    srednia: float | None
    mediana: float | None
    dominanty: tuple[int, ...]
    kwartyl_pierwszy: float | None
    kwartyl_trzeci: float | None
    minimum: int | None
    maksimum: int | None


@dataclass(frozen=True)
class StatystykiRozgrywekSezonu:
    rozgrywki: str
    statystyki: StatystykiBramekGrupy


@dataclass(frozen=True)
class StatystykiSezonu:
    sezon: str
    statystyki: StatystykiBramekGrupy
    rozgrywki: tuple[StatystykiRozgrywekSezonu, ...]


@dataclass(frozen=True)
class RozstepSezonu:
    sezon: str
    liczba_znanych: int
    mala_proba: bool
    mediana: float
    kwartyl_pierwszy: float
    kwartyl_trzeci: float
    minimum: int
    maksimum: int
    wartosci_odstajace: tuple[int, ...]


@dataclass(frozen=True)
class FormaWedlugMiejsca:
    liczba_znanych: int
    wystarczajaco_na_trend_5: bool
    wystarczajaco_na_trend_10: bool
    punkty: tuple[PunktFormy, ...]


@dataclass(frozen=True)
class FormaIRegularnosc:
    liczba_meczow: int
    liczba_znanych: int
    sezony: tuple[RozstepSezonu, ...]
    wszystkie: FormaWedlugMiejsca
    dom: FormaWedlugMiejsca
    wyjazd: FormaWedlugMiejsca
    srednia: float | None
    mediana: float | None
    dominanty: tuple[int, ...]
    minimum: int | None
    maksimum: int | None
    kwartyl_pierwszy: float | None
    kwartyl_trzeci: float | None
    rozstep_miedzykwartylowy: float | None
    odchylenie_standardowe: float | None
    mad: float | None
    wspolczynnik_zmiennosci: float | None
    percentyl_10: float | None
    percentyl_90: float | None
    srednia_ucieta: float | None
    udzial_0_bramek: float | None
    udzial_1_2_bramki: float | None
    udzial_3_5_bramek: float | None
    udzial_6_plus_bramek: float | None
