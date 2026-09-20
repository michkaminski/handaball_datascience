from dataclasses import dataclass
from datetime import date
from decimal import Decimal

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
