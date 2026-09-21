from dataclasses import dataclass


@dataclass(frozen=True)
class SzczegolyHaliViewModel:
    id_hala: int
    nazwa: str
    miasto: str
    adres: str
    pojemnosc: str
    pierwszy_mecz: str
    ostatni_mecz: str
    liczba_meczow: int
    liczba_rozegranych: int
    liczba_rozgrywek: int
    liczba_sezonow: int
    liczba_druzyn: int
    liczba_zawodnikow: int


@dataclass(frozen=True)
class ZawodnikHaliViewModel:
    id_zawodnik: int
    zawodnik: str
    pierwszy_wystep: str
    ostatni_wystep: str
    wystepy: int
    bramki: str
    srednia_bramek: str
    druzyny: str


@dataclass(frozen=True)
class StronaZawodnikowHaliViewModel:
    pozycje: list[ZawodnikHaliViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class RankingDruzynyHaliViewModel:
    druzyna: str
    mecze: int
    zwyciestwa: int
    remisy: int
    porazki: int
    bramki_zdobyte: int
    bramki_stracone: int
    bilans: str


@dataclass(frozen=True)
class RankingRozgrywekHaliViewModel:
    rozgrywki: str
    mecze: int
    sezony: int
    pierwszy_sezon: str
    ostatni_sezon: str


@dataclass(frozen=True)
class RankingZawodnikaHaliViewModel:
    id_zawodnik: int
    zawodnik: str
    wystepy: int
    bramki: int
    srednia_bramek: str
    druzyny: str


@dataclass(frozen=True)
class PasekHaliViewModel:
    etykieta: str
    wartosc: str
    liczba: int
    szerokosc: int
    opis: str = ""


@dataclass(frozen=True)
class KomorkaKalendarzaHaliViewModel:
    sezon: str
    miesiac: int
    mecze: int
    intensywnosc: int


@dataclass(frozen=True)
class ProfilWynikowHaliViewModel:
    srednia_bramek: str
    mediana_bramek: str
    odchylenie_bramek: str
    zakres_bramek: str
    kwartyle: str
    srednia_roznica: str
    mecze_jedna_bramka: str
    mecze_trzy_bramki: str
    mecze_piec_bramek: str


@dataclass(frozen=True)
class FrekwencjaHaliViewModel:
    kompletne: bool
    kompletnosc: str
    srednia: str
    mediana: str
    maksimum: str
    wypelnienie: str


@dataclass(frozen=True)
class PorownanieHaliViewModel:
    metryka: str
    hala: str
    wszystkie_hale: str


@dataclass(frozen=True)
class RekordMeczuHaliViewModel:
    rodzaj: str
    id_mecz: int
    data: str
    mecz: str
    wynik: str
    wartosc: str


@dataclass(frozen=True)
class StatystykiHaliViewModel:
    druzyny: list[RankingDruzynyHaliViewModel]
    rozgrywki: list[RankingRozgrywekHaliViewModel]
    zawodnicy: list[RankingZawodnikaHaliViewModel]
    skuteczni_zawodnicy: list[RankingZawodnikaHaliViewModel]
    liczba_druzyn: int
    liczba_rozgrywek: int
    liczba_zawodnikow: int
    trendy_mecze: list[PasekHaliViewModel]
    trendy_bramki: list[PasekHaliViewModel]
    dni_tygodnia: list[PasekHaliViewModel]
    histogram_bramek: list[PasekHaliViewModel]
    sezony_kalendarza: list[str]
    kalendarz: list[KomorkaKalendarzaHaliViewModel]
    profil_wynikow: ProfilWynikowHaliViewModel
    frekwencja: FrekwencjaHaliViewModel
    porownanie: list[PorownanieHaliViewModel]
    rekordy: list[RekordMeczuHaliViewModel]
