from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar


@dataclass(frozen=True)
class FiltryKatalogu:
    szukaj: str | None = None
    id_sezon: int | None = None
    plec: str | None = None
    stan: str | None = None
    miasto: str | None = None
    wycofany: bool | None = None
    pojemnosc_min: int | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "id"

    def __post_init__(self) -> None:
        if self.id_sezon is not None and self.id_sezon < 1:
            raise ValueError("Niepoprawny sezon.")
        if self.plec not in {None, "K", "M"}:
            raise ValueError("Niepoprawna płeć.")
        if self.pojemnosc_min is not None and self.pojemnosc_min < 0:
            raise ValueError("Pojemność nie może być ujemna.")
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Niepoprawny numer lub rozmiar strony.")
        if self.sortowanie.startswith("--"):
            raise ValueError("Niepoprawne sortowanie.")


@dataclass(frozen=True)
class PozycjaSezonu:
    id: int
    nazwa: str
    rok_rozpoczecia: int | None
    liczba_rozgrywek: int
    stan: str | None


@dataclass(frozen=True)
class PozycjaRozgrywek:
    id: int
    sezon: str
    nazwa: str
    plec: str | None
    liczba_zespolow: int | None


@dataclass(frozen=True)
class PozycjaDruzyny:
    id: int
    id_zespol: int
    sezon: str
    nazwa: str | None
    plec: str | None
    miasto: str | None
    wycofany: bool | None


@dataclass(frozen=True)
class PozycjaSedziego:
    id: int
    nazwisko: str | None
    miasto: str | None
    liczba_meczow: int


@dataclass(frozen=True)
class PozycjaHali:
    id: int
    nazwa: str | None
    miasto: str | None
    adres: str | None
    pojemnosc: int | None
    liczba_meczow: int


T = TypeVar("T")


@dataclass(frozen=True)
class StronaKatalogu[T]:
    pozycje: list[T]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int
