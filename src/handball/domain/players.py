from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FiltryZawodnikow:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    druzyna: str | None = None
    pozycja: str | None = None
    rocznik: int | None = None
    szukaj: str | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "nazwisko"

    def __post_init__(self) -> None:
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Strona musi być dodatnia, a rozmiar strony wynosić od 1 do 100.")
        if self.id_sezon is not None and self.id_sezon < 1:
            raise ValueError("Identyfikator sezonu musi być dodatni.")
        if self.rocznik is not None and not 1 <= self.rocznik <= 9999:
            raise ValueError("Rocznik musi wynosić od 1 do 9999.")
        if self.sortowanie.lstrip("-") not in {
            "id",
            "imie",
            "nazwisko",
            "rocznik",
            "wzrost",
            "waga",
        } or self.sortowanie.startswith("--"):
            raise ValueError("Niepoprawne sortowanie.")


@dataclass(frozen=True)
class PozycjaListyZawodnikow:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    rocznik: int | None
    pozycje: tuple[str, ...]
    druzyny: tuple[str, ...]
    wzrost: Decimal | None
    waga: Decimal | None


@dataclass(frozen=True)
class StronaZawodnikow:
    pozycje: list[PozycjaListyZawodnikow]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int
