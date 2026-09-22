from dataclasses import dataclass
from datetime import date, datetime
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
class PunktFormyZawodnika:
    id_mecz: int
    termin: datetime | None
    sezon: str
    bramki: int | None
    mediana_kroczaca_5: float | None
    srednia_kroczaca_5: float | None
    mediana_kroczaca_10: float | None


@dataclass(frozen=True)
class RozstepSezonuZawodnika:
    sezon: str
    liczba_znanych: int
    mala_proba: bool
    mediana: float
    kwartyl_pierwszy: float
    kwartyl_trzeci: float
    minimum: int
    maksimum: int
    wartosci_odstajace: tuple[int, ...]


@dataclass(frozen=True)
class FormaWedlugMiejscaZawodnika:
    liczba_znanych: int
    wystarczajaco_na_trend_5: bool
    wystarczajaco_na_trend_10: bool
    punkty: tuple[PunktFormyZawodnika, ...]


@dataclass(frozen=True)
class FormaIRegularnoscZawodnika:
    liczba_meczow: int
    liczba_znanych: int
    sezony: tuple[RozstepSezonuZawodnika, ...]
    dom: FormaWedlugMiejscaZawodnika
    wyjazd: FormaWedlugMiejscaZawodnika
    srednia: float | None
    mediana: float | None
    dominanty: tuple[int, ...]
    minimum: int | None
    maksimum: int | None
    kwartyl_pierwszy: float | None
    kwartyl_trzeci: float | None
    rozstep_miedzykwartylowy: float | None
    odchylenie_standardowe: float | None
    mad: float | None
    wspolczynnik_zmiennosci: float | None
    percentyl_10: float | None
    percentyl_90: float | None
    srednia_ucieta: float | None
    udzial_0_bramek: float | None
    udzial_1_2_bramki: float | None
    udzial_3_5_bramek: float | None
    udzial_6_plus_bramek: float | None


@dataclass(frozen=True)
class PodsumowanieAnalityczneZawodnika:
    mecze: tuple[AnalitykaMeczuZawodnika, ...]
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
