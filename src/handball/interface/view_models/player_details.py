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


@dataclass(frozen=True)
class FormaWedlugMiejscaZawodnikaViewModel:
    liczba_znanych: str
    wystarczajaco_na_trend_5: bool
    wystarczajaco_na_trend_10: bool
    punkty: list[dict[str, int | str | float | None]]


@dataclass(frozen=True)
class FormaIRegularnoscZawodnikaViewModel:
    liczba_meczow: str
    liczba_znanych: str
    srednia: str
    mediana: str
    dominanta: str
    minimum: str
    maksimum: str
    kwartyle: str
    iqr: str
    odchylenie_standardowe: str
    mad: str
    wspolczynnik_zmiennosci: str
    percentyl_10: str
    percentyl_90: str
    srednia_ucieta: str
    udzial_0_bramek: str
    udzial_1_2_bramki: str
    udzial_3_5_bramek: str
    udzial_6_plus_bramek: str
    wszystkie: FormaWedlugMiejscaZawodnikaViewModel
    dom: FormaWedlugMiejscaZawodnikaViewModel
    wyjazd: FormaWedlugMiejscaZawodnikaViewModel
    sezony: list[dict[str, int | str | float | bool | list[int]]]


@dataclass(frozen=True)
class PodsumowanieAnalityczneZawodnikaViewModel:
    liczba_meczow: str
    bramki: str
    srednia: str
    mediana: str
    dominanta: str
    kwartyle: str
    mecze_z_bramka: str
    karne: str
    skutecznosc_karnych: str
    dwie_minuty: str
    upomnienia: str
    dyskwalifikacje: str
    pokrycie_bramek: str
    punkty: list[dict[str, int | str | None]]
    rozklad: list[dict[str, int]]
    sezony_rozgrywki: list[dict[str, int | str | float | list[int] | None]]
    mediana_wartosc: float | None
    mediana_dom_wartosc: float | None
    mediana_wyjazd_wartosc: float | None
    rekord_bramek: str
    rekordowe_mecze: list[dict[str, int | str | None]]
    najdluzsza_seria: str
    jakosc: list[dict[str, int | str | float]]
