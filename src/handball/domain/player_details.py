from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from handball.domain.goal_statistics import StatystykiSezonu
from handball.domain.matches import PozycjaListyMeczow, ZawodnikMeczu


@dataclass(frozen=True)
class FiltryMeczowZawodnika:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    przeciwnik: str | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "-data"

    def __post_init__(self) -> None:
        if self.id_sezon is not None and self.id_sezon < 1:
            raise ValueError("Niepoprawny sezon.")
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Niepoprawny numer lub rozmiar strony.")
        if self.sortowanie not in {"data", "-data"}:
            raise ValueError("Niepoprawne sortowanie.")


@dataclass(frozen=True)
class DaneSezonoweZawodnika:
    id_zespol_sezon: int
    sezon: str
    druzyna: str | None
    nr_koszulki: int | None
    pozycja: str | None
    wzrost: Decimal | None
    waga: Decimal | None
    rozgrywki: str | None = None
    bramki: int | None = None
    karne_bramki: int | None = None
    karne_liczba: int | None = None
    dwie_minuty: int | None = None
    upomnienia: int | None = None
    dyskwalifikacje: int | None = None


@dataclass(frozen=True)
class SzczegolyZawodnika:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    data_urodzenia: date | None
    foto_url: str | None
    sezony: tuple[DaneSezonoweZawodnika, ...]


@dataclass(frozen=True)
class WpisMeczowyZawodnika:
    strona: str
    statystyki: ZawodnikMeczu


@dataclass(frozen=True)
class MeczZawodnika:
    mecz: PozycjaListyMeczow
    wpisy: tuple[WpisMeczowyZawodnika, ...]


@dataclass(frozen=True)
class StronaMeczowZawodnika:
    pozycje: list[MeczZawodnika]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class AnalitykaMeczuZawodnika:
    id_mecz: int
    termin: datetime | None
    sezon: str
    rozgrywki: str
    bramki: int | None
    karne_bramki: int | None
    karne_liczba: int | None
    dwie_minuty: int | None
    upomnienia: int | None
    dyskwalifikacje: int | None
    miejsce: str | None


@dataclass(frozen=True)
class PodsumowanieAnalityczneZawodnika:
    mecze: tuple[AnalitykaMeczuZawodnika, ...]
    statystyki_sezonow: tuple[StatystykiSezonu, ...]
    liczba_meczow: int
    liczba_znanych_bramek: int
    suma_bramek: int | None
    srednia_bramek: float | None
    mediana_bramek: float | None
    mediana_bramek_dom: float | None
    mediana_bramek_wyjazd: float | None
    dominanty_bramek: tuple[int, ...]
    kwartyl_pierwszy: float | None
    kwartyl_trzeci: float | None
    mecze_z_bramka: int
    karne_bramki: int | None
    karne_liczba: int | None
    dwie_minuty: int | None
    upomnienia: int | None
    dyskwalifikacje: int | None
    rekord_bramek: int | None
    rekordowe_mecze: tuple[int, ...]
    najdluzsza_seria_z_bramka: int
    znane_karne_bramki: int
    znane_karne_liczba: int
    znane_dwie_minuty: int
    znane_upomnienia: int
    znane_dyskwalifikacje: int
