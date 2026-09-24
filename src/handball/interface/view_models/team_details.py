from dataclasses import dataclass

from handball.interface.view_models.matches import PozycjaListyMeczowViewModel


@dataclass(frozen=True)
class NazwaHistorycznaDruzynyViewModel:
    nazwa: str
    sezony: str
    liczba_sezonow: int


@dataclass(frozen=True)
class SezonDruzynyViewModel:
    id_zespol_sezon: int
    sezon: str
    nazwa: str
    miasto: str
    kategoria: str
    status: str
    wycofana: bool


@dataclass(frozen=True)
class HalaDruzynyViewModel:
    id_hala: int
    nazwa: str
    miasto: str
    liczba_meczow: int
    srednia_widzow: str


@dataclass(frozen=True)
class SzczegolyDruzynyViewModel:
    id_zespol: int
    nazwa: str
    nr_klubu: str
    plec: str
    kategoria: str
    miasto: str
    status: str
    wycofana: bool
    liczba_sezonow: int
    zakres_sezonow: str
    liczba_meczow: int
    nazwy: list[NazwaHistorycznaDruzynyViewModel]
    sezony: list[SezonDruzynyViewModel]
    hale: list[HalaDruzynyViewModel]


@dataclass(frozen=True)
class BilansViewModel:
    rozegrane: int
    wygrane: int
    remisy: int
    porazki: int
    rozstrzygniecia: str
    bramki: str
    roznica: str
    srednia_zdobytych: str
    srednia_straconych: str
    procent_zwyciestw: str
    inne: str
    widzowie_dom: str
    widzowie_wyjazd: str
    widzowie_dom_suma: str
    pokrycie_widzow: str


@dataclass(frozen=True)
class FrekwencjaMiejscaViewModel:
    srednia: str
    mediana: str
    suma: str
    pokrycie: str
    rekord: str
    rekord_mecz: int | None
    rekord_opis: str


@dataclass(frozen=True)
class FrekwencjaDruzynyViewModel:
    dom: FrekwencjaMiejscaViewModel
    wyjazd: FrekwencjaMiejscaViewModel
    ma_dane: bool


@dataclass(frozen=True)
class WierszSezonuDruzynyViewModel:
    sezon: str
    rozgrywki: str
    nazwa_druzyny: str
    bilans: BilansViewModel
    podsumowanie_sezonu: bool


@dataclass(frozen=True)
class MeczDruzynyViewModel:
    mecz: PozycjaListyMeczowViewModel
    termin: str
    miejsce: str
    przeciwnik: str
    wynik_druzyny: str
    rezultat: str
    rezultat_klasa: str
    rozstrzygniecie: str
    widzowie: str


@dataclass(frozen=True)
class StronaMeczowDruzynyViewModel:
    pozycje: list[MeczDruzynyViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class ZawodnikDruzynyViewModel:
    id_zawodnik: int
    nazwa: str
    mecze: int
    bramki: str
    srednia: str
    karne: str
    kary: str
    sezony: str
    ostatni_mecz: str


@dataclass(frozen=True)
class StronaZawodnikowDruzynyViewModel:
    pozycje: list[ZawodnikDruzynyViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class RekordMeczuDruzynyViewModel:
    id_mecz: int
    opis: str
    szczegoly: str


@dataclass(frozen=True)
class PodsumowanieDruzynyViewModel:
    bilans: BilansViewModel
    seria_zwyciestw: str
    seria_bez_porazki: str
    rekordy: list[tuple[str, RekordMeczuDruzynyViewModel | None]]
    bilanse_sezonow: list[dict[str, int | float | str]]


@dataclass(frozen=True)
class MiaraBramekDruzynyViewModel:
    etykieta: str
    zdobyte: str
    stracone: str
    roznica: str


@dataclass(frozen=True)
class GrupaMiarBramekDruzynyViewModel:
    nazwa: str
    miary: list[MiaraBramekDruzynyViewModel]


@dataclass(frozen=True)
class AnalizaBramekDruzynyViewModel:
    liczba_meczow: str
    liczba_znanych: str
    miary: list[MiaraBramekDruzynyViewModel]
    grupy: list[GrupaMiarBramekDruzynyViewModel]
    sezony: list[dict[str, object]]
    rozklad: list[dict[str, object]]
    mecze: dict[str, dict[str, object]]
    rozstepy: list[dict[str, object]]


@dataclass(frozen=True)
class KomorkaZestawieniaViewModel:
    bramki: str
    kary: str
    karne: str
    opis: str


@dataclass(frozen=True)
class KolumnaMeczuZestawieniaViewModel:
    id_mecz: int
    data: str
    przeciwnik: str
    miejsce: str
    wynik: str
    rezultat: str
    rezultat_klasa: str


@dataclass(frozen=True)
class WierszZestawieniaViewModel:
    id_zawodnik: int
    nazwa: str
    numery: str
    pozycje: str
    komorki: list[KomorkaZestawieniaViewModel | None]
    suma: KomorkaZestawieniaViewModel
    mecze: int


@dataclass(frozen=True)
class ZestawienieSezonuDruzynyViewModel:
    sezon: str
    mecze: list[KolumnaMeczuZestawieniaViewModel]
    wiersze: list[WierszZestawieniaViewModel]
    sumy_meczow: list[KomorkaZestawieniaViewModel]
    suma: KomorkaZestawieniaViewModel
