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
        "rozkłady",
        "Rozkłady",
        "Rozkłady częstości wyników: ile razy pada dana liczba bramek w meczu, "
        "u gospodarzy i u gości.",
        "Statystyka",
        "administracja.lista_rozkladow",
    ),
    PozycjaRaportu(
        "frekwencja",
        "Frekwencja",
        "Widzowie na meczach: kluczowe miary, trendy sezonowe, ranking klubów jako gospodarzy "
        "i TOP 50 rekordów. Brak danych o widzach nie jest traktowany jako zero.",
        "Statystyka",
        "administracja.raport_frekwencji",
    ),
    PozycjaRaportu(
        "raporty_druzyn",
        "Raporty drużyn — wydruki PDF",
        "Raport drużyny na jednej kartce A4 (sezony, kadra z poprzednim sezonem, ostatnie mecze) "
        "oraz zestawienia sezonu i poprzedniego sezonu na kartkach poziomych.",
        "Wydruki",
        "administracja.raporty_druzyn",
    ),
    PozycjaRaportu(
        "prognozy_meczow",
        "Prognozy meczów — siła drużyn",
        "Historyczny backtest prognoz Superligi, Ligi Centralnej i I Ligi mężczyzn i kobiet "
        "na podstawie dynamicznej "
        "siły drużyn: prognoza przed meczem, wynik, błąd i aktualizacja ratingu.",
        "Model predykcyjny",
        "administracja.raport_prognoz_meczow",
    ),
    PozycjaRaportu(
        "typowania_meczow",
        "Typowania meczów",
        "Prognozy meczów z wybranego okresu, także przyszłych. Mecz rozegrany ma prognozę "
        "i ocenę jak w historii prognoz, nierozegrany prognozę ze stanu modelu na teraz.",
        "Model predykcyjny",
        "administracja.raport_typowan_meczow",
    ),
)
