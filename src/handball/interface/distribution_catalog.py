from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PozycjaRozkladu:
    klucz: str
    tytul: str
    opis: str
    kategoria: str
    punkt_koncowy: str


KATALOG_ROZKLADOW: tuple[PozycjaRozkladu, ...] = (
    PozycjaRozkladu(
        "rozklad_bramek",
        "Rozkład bramek na mecz",
        "Jak często pada dana liczba bramek w meczu oraz jak często gospodarze i goście "
        "zdobywają kolejne liczby bramek.",
        "Wyniki",
        "administracja.rozklad_bramek",
    ),
)
