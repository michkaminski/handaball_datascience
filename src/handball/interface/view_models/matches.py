from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PozycjaListyMeczowViewModel:
    id_mecz: int
    termin: datetime | None
    sezon: str | None
    rozgrywki: str | None
    gospodarz: str | None
    gosc: str | None
    wynik: str
    hala: str | None
    runda: str | None = None
    kolejka: str | None = None
    dopisek_wyniku: str | None = None


@dataclass(frozen=True)
class StronaMeczowViewModel:
    pozycje: list[PozycjaListyMeczowViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class ZawodnikMeczuViewModel:
    nr_koszulki: str
    zawodnik: str
    pozycja: str
    bramki: str
    dwie_minuty: str
    upomnienie: str
    dyskwalifikacja: str
    kd: str
    wyjscie: str
    karne: str
    karne_seria: str
    kolor_pozycji: int | None = None
    najlepszy_strzelec: bool = False


@dataclass(frozen=True)
class SzczegolyMeczuViewModel:
    id_mecz: int
    gospodarz: str
    gosc: str
    wynik_naglowek: str
    wynik_do_przerwy: str
    dopisek_wyniku: str
    rozgrywki: str
    kolejka: str
    termin: str
    hala: str
    status: str
    dane_podstawowe: list[tuple[str, str]]
    statystyki: list[tuple[str, str, str]]
    sklad_gospodarz: list[ZawodnikMeczuViewModel]
    sklad_gosc: list[ZawodnikMeczuViewModel]
    sklad_inne: list[ZawodnikMeczuViewModel]
