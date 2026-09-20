from dataclasses import dataclass

from handball.interface.view_models.matches import PozycjaListyMeczowViewModel


@dataclass(frozen=True)
class DaneSezonoweZawodnikaViewModel:
    sezon: str
    druzyna: str
    nr_koszulki: str
    pozycja: str
    rozgrywki: str
    bramki: str
    karne: str
    kary: str


@dataclass(frozen=True)
class SzczegolyZawodnikaViewModel:
    id_zawodnik: int
    nazwa: str
    data_urodzenia: str
    foto_url: str | None
    wzrost: str
    waga: str
    sezony: list[DaneSezonoweZawodnikaViewModel]


@dataclass(frozen=True)
class WpisMeczowyZawodnikaViewModel:
    strona: str
    druzyna: str
    przeciwnik: str
    nr_koszulki: str
    pozycja: str
    bramki: str
    karne: str
    karne_seria: str
    dwie_minuty: str
    upomnienie: str
    dyskwalifikacja: str


@dataclass(frozen=True)
class MeczZawodnikaViewModel:
    mecz: PozycjaListyMeczowViewModel
    termin: str
    wpisy: list[WpisMeczowyZawodnikaViewModel]
    wiele_stron: bool


@dataclass(frozen=True)
class StronaMeczowZawodnikaViewModel:
    pozycje: list[MeczZawodnikaViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int
