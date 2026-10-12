from dataclasses import dataclass

from handball.interface.match_report_charts import (
    HistogramReszt,
    WykresRatingu,
    WykresSezonu,
)
from handball.interface.view_models.match_statistics import FormaDruzynyViewModel


@dataclass(frozen=True)
class KafelekRaportu:
    etykieta: str
    wartosc: str
    opis: str
    klasa: str = ""


@dataclass(frozen=True)
class WierszPorownaniaRaportu:
    etykieta: str
    gospodarz: str
    gosc: str
    pasek_gospodarza: int
    pasek_goscia: int
    lepszy: str | None


@dataclass(frozen=True)
class ModelRaportuViewModel:
    nazwa: str
    szansa_gospodarza: int
    szansa_remisu: int
    szansa_goscia: int
    oczekiwany_wynik: str
    wynik: str
    reszta: str
    ocena: str
    rating_gospodarza: str
    rating_goscia: str
    zmiana_gospodarza: str
    zmiana_goscia: str
    ranking_gospodarza: str
    ranking_goscia: str
    histogram: HistogramReszt | None
    opis_histogramu: str


@dataclass(frozen=True)
class StrzelecRaportuViewModel:
    nr: str
    zawodnik: str
    pozycja: str
    bramki: int
    pasek: int
    karne: str
    kary: str
    srednia: str
    roznica: str
    klasa_roznicy: str
    wyjatkowy: bool


@dataclass(frozen=True)
class AtakRaportuViewModel:
    strzelcy: list[StrzelecRaportuViewModel]
    pozostali: str
    efektywna_liczba: str
    udzial_trzech: str
    zawodnicy_bez_bramki: str


@dataclass(frozen=True)
class TloRaportuViewModel:
    wykres: WykresSezonu | None
    zdobyte: str
    stracone: str
    opis_aria: str


@dataclass(frozen=True)
class SegmentAtakuViewModel:
    etykieta: str
    bramki: int
    szerokosc: float
    klasa: str


@dataclass(frozen=True)
class StrukturaAtakuViewModel:
    nazwa: str
    strona: str
    segmenty: list[SegmentAtakuViewModel]
    opis: str


@dataclass(frozen=True)
class MeczBezposredniViewModel:
    data: str
    miejsce: str
    wynik: str
    rezultat: str
    klasa: str
    rozgrywki: str


@dataclass(frozen=True)
class HistoriaSpotkanViewModel:
    mecze: list[MeczBezposredniViewModel]
    bilans: str
    bramki: str
    liczba: int


@dataclass(frozen=True)
class DruzynaRaportuViewModel:
    nazwa: str
    strona: str
    atak: AtakRaportuViewModel | None
    tlo: TloRaportuViewModel | None
    forma: FormaDruzynyViewModel | None


@dataclass(frozen=True)
class RaportMeczuViewModel:
    id_mecz: int
    tytul_dokumentu: str
    kontekst: str
    termin: str
    hala: str
    widzowie: str
    gospodarz: str
    gosc: str
    wynik: str
    przebieg: str
    dopisek: str
    naglowek: str
    wnioski: list[str]
    kafelki: list[KafelekRaportu]
    porownanie: list[WierszPorownaniaRaportu]
    model: ModelRaportuViewModel | None
    wykres_ratingu: WykresRatingu | None
    opis_ratingu: str
    druzyny: list[DruzynaRaportuViewModel]
    przypisy: list[str]
    struktura: list[StrukturaAtakuViewModel]
    historia: HistoriaSpotkanViewModel | None
    dlugie_nazwy: bool
