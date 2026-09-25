from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PozycjaRaportu:
    klucz: str
    tytul: str
    opis: str
    kategoria: str
    punkt_koncowy: str


KATALOG_RAPORTOW: tuple[PozycjaRaportu, ...] = (
    PozycjaRaportu(
        "prognozy_meczow",
        "Prognozy meczów — siła drużyn",
        "Historyczny backtest prognoz Superligi, Ligi Centralnej i I Ligi mężczyzn i kobiet "
        "na podstawie dynamicznej "
        "siły drużyn: prognoza przed meczem, wynik, błąd i aktualizacja ratingu.",
        "Model predykcyjny",
        "administracja.raport_prognoz_meczow",
    ),
)
