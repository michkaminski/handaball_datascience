from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class FiltryMeczowHali:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    druzyna: str | None = None
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
class FiltryZawodnikowHali:
    szukaj: str | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "-wystepy"

    def __post_init__(self) -> None:
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Niepoprawny numer lub rozmiar strony.")
        if self.sortowanie.removeprefix("-") not in {
            "nazwisko",
            "pierwszy_wystep",
            "ostatni_wystep",
            "wystepy",
            "bramki",
            "srednia_bramek",
        }:
            raise ValueError("Niepoprawne sortowanie.")


@dataclass(frozen=True)
class SzczegolyHali:
    id_hala: int
    nazwa: str | None
    miasto: str | None
    ulica: str | None
    numer: str | None
    pojemnosc: int | None
    pierwszy_mecz: datetime | None
    ostatni_mecz: datetime | None
    liczba_meczow: int
    liczba_rozegranych: int
    liczba_rozgrywek: int
    liczba_sezonow: int
    liczba_druzyn: int
    liczba_zawodnikow: int


@dataclass(frozen=True)
class ZawodnikHali:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    pierwszy_wystep: datetime | None
    ostatni_wystep: datetime | None
    wystepy: int
    bramki: int | None
    srednia_bramek: Decimal | None
    druzyny: tuple[str, ...]


@dataclass(frozen=True)
class StronaZawodnikowHali:
    pozycje: list[ZawodnikHali]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class RankingDruzynyHali:
    id_zespol: int
    druzyna: str | None
    mecze: int
    zwyciestwa: int
    remisy: int
    porazki: int
    bramki_zdobyte: int
    bramki_stracone: int


@dataclass(frozen=True)
class RankingRozgrywekHali:
    rozgrywki: str
    mecze: int
    sezony: int
    pierwszy_sezon: str | None
    ostatni_sezon: str | None


@dataclass(frozen=True)
class RankingZawodnikaHali:
    id_zawodnik: int
    zawodnik: str
    wystepy: int
    bramki: int
    srednia_bramek: Decimal
    druzyny: tuple[str, ...]


@dataclass(frozen=True)
class TrendSezonuHali:
    sezon: str
    mecze: int
    srednia_bramek: Decimal
    srednia_widzow: Decimal | None
    mecze_z_frekwencja: int


@dataclass(frozen=True)
class RozkladKalendarzaHali:
    etykieta: str
    mecze: int


@dataclass(frozen=True)
class KomorkaKalendarzaHali:
    sezon: str
    miesiac: int
    mecze: int


@dataclass(frozen=True)
class PrzedzialHali:
    etykieta: str
    mecze: int


@dataclass(frozen=True)
class ProfilWynikowHali:
    srednia_bramek: Decimal | None
    mediana_bramek: Decimal | None
    odchylenie_bramek: Decimal | None
    minimum_bramek: int | None
    maksimum_bramek: int | None
    kwartyl_pierwszy: Decimal | None
    kwartyl_trzeci: Decimal | None
    srednia_roznica: Decimal | None
    mecze_jedna_bramka: int
    mecze_trzy_bramki: int
    mecze_piec_bramek: int


@dataclass(frozen=True)
class FrekwencjaHali:
    mecze_z_danymi: int
    wszystkie_mecze: int
    srednia: Decimal | None
    mediana: Decimal | None
    maksimum: int | None
    wypelnienie: Decimal | None


@dataclass(frozen=True)
class PorownanieHali:
    metryka: str
    hala: Decimal | None
    wszystkie_hale: Decimal | None


@dataclass(frozen=True)
class RekordMeczuHali:
    rodzaj: str
    id_mecz: int
    data: datetime | None
    gospodarz: str | None
    gosc: str | None
    wynik_gosp: int
    wynik_gosc: int
    wartosc: int


@dataclass(frozen=True)
class StatystykiHali:
    druzyny: list[RankingDruzynyHali]
    rozgrywki: list[RankingRozgrywekHali]
    zawodnicy: list[RankingZawodnikaHali]
    skuteczni_zawodnicy: list[RankingZawodnikaHali]
    liczba_druzyn: int
    liczba_rozgrywek: int
    liczba_zawodnikow: int
    trendy: list[TrendSezonuHali]
    dni_tygodnia: list[RozkladKalendarzaHali]
    kalendarz: list[KomorkaKalendarzaHali]
    histogram_bramek: list[PrzedzialHali]
    profil_wynikow: ProfilWynikowHali
    frekwencja: FrekwencjaHali
    porownanie: list[PorownanieHali]
    rekordy: list[RekordMeczuHali]


@dataclass(frozen=True)
class LimityStatystykHali:
    druzyny: int | None = 10
    rozgrywki: int | None = 10
    zawodnicy: int | None = 10
    skuteczni_zawodnicy: int | None = 10
