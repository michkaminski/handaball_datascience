from dataclasses import dataclass


@dataclass(frozen=True)
class PozycjaListyZawodnikowViewModel:
    id_zawodnik: int
    imie: str
    nazwisko: str
    rocznik: str
    pozycje: str
    druzyny: str
    wzrost: str
    waga: str


@dataclass(frozen=True)
class StronaZawodnikowViewModel:
    pozycje: list[PozycjaListyZawodnikowViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int
