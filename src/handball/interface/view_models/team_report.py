from __future__ import annotations

from dataclasses import dataclass

from handball.interface.view_models.team_details import WierszSezonuDruzynyViewModel


@dataclass(frozen=True)
class UkladRaportuViewModel:
    wysokosc_wiersza_mm: float
    czcionka_pt: float


@dataclass(frozen=True)
class LiczbaRaportuViewModel:
    etykieta: str
    wartosc: str
    dopisek: str = ""


@dataclass(frozen=True)
class PoprzedniSezonViewModel:
    zagral: bool
    mecze: str
    bramki: str
    srednia: str
    klub: str
    inny_klub: bool
    wyroznij_bramki: bool = False


@dataclass(frozen=True)
class ZawodnikRaportuViewModel:
    numer: str
    nazwa: str
    rocznik: str
    pozycja: str
    grupa: str
    nowa_grupa: bool
    mecze: str
    bramki: str
    srednia: str
    karne: str
    karne_procent: str
    dwie_minuty: str
    upomnienia: str
    dyskwalifikacje: str
    poprzedni: PoprzedniSezonViewModel
    wyroznij_bramki: bool = False
    wyroznij_karne: bool = False


@dataclass(frozen=True)
class MeczRaportuViewModel:
    data: str
    rozgrywki: str
    miejsce: str
    przeciwnik: str
    wynik: str
    rezultat: str
    rezultat_klasa: str
    rozstrzygniecie: str
    karne: str
    dwie_minuty: str
    widzowie: str
    strzelcy: str
    nowy_sezon: bool


@dataclass(frozen=True)
class RaportDruzynyViewModel:
    druzyna: str
    opis: str
    sezon: str
    poprzedni_sezon: str
    rozgrywki: str
    stan_na: str
    liczby: tuple[LiczbaRaportuViewModel, ...]
    sezony: tuple[WierszSezonuDruzynyViewModel, ...]
    zawodnicy: tuple[ZawodnikRaportuViewModel, ...]
    ze_skladu: bool
    mecze: tuple[MeczRaportuViewModel, ...]
    uklad: UkladRaportuViewModel


@dataclass(frozen=True)
class UkladZestawieniaViewModel:
    wysokosc_wiersza_mm: float
    czcionka_pt: float
    szerokosc_meczu_mm: float


@dataclass(frozen=True)
class KomorkaZestawieniaRaportuViewModel:
    bramki: str
    kary: str
    karne: str
    opis: str
    najlepszy: bool = False


@dataclass(frozen=True)
class KolumnaZestawieniaRaportuViewModel:
    data: str
    przeciwnik: str
    miejsce: str
    wynik: str
    zdobyte: str
    stracone: str
    wygrana: bool


@dataclass(frozen=True)
class SumaZestawieniaRaportuViewModel:
    mecze: str
    bramki: str
    karne: str
    kary: str
    wyroznij_bramki: bool = False
    wyroznij_karne: bool = False


@dataclass(frozen=True)
class WierszZestawieniaRaportuViewModel:
    nazwa: str
    numery: str
    rocznik: str
    pozycja: str
    nowa_grupa: bool
    komorki: tuple[KomorkaZestawieniaRaportuViewModel | None, ...]
    suma: SumaZestawieniaRaportuViewModel


@dataclass(frozen=True)
class StronaZestawienViewModel:
    sezon: str
    opis: str
    brak: str
    mecze: tuple[KolumnaZestawieniaRaportuViewModel, ...]
    wiersze: tuple[WierszZestawieniaRaportuViewModel, ...]
    sumy_meczow: tuple[KomorkaZestawieniaRaportuViewModel, ...]
    suma: SumaZestawieniaRaportuViewModel | None
    uklad: UkladZestawieniaViewModel


@dataclass(frozen=True)
class ZestawieniaDruzynyViewModel:
    druzyna: str
    stan_na: str
    strony: tuple[StronaZestawienViewModel, ...]
