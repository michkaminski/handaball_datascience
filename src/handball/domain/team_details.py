from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from handball.domain.goal_statistics import (
    FormaIRegularnosc,
    StatystykiBramekGrupy,
    StatystykiSezonu,
)
from handball.domain.match_rules import MeczPolicy, StatusMeczu
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow
from handball.domain.options import OpcjaWyboru

SORTOWANIA_ZAWODNIKOW_DRUZYNY = frozenset(
    kierunek + pole
    for pole in ("bramki", "mecze", "srednia", "nazwisko", "ostatni_mecz")
    for kierunek in ("", "-")
)


class RezultatMeczu(StrEnum):
    WYGRANA = "wygrana"
    REMIS = "remis"
    PORAZKA = "porazka"


class RodzajBramek(StrEnum):
    ZDOBYTE = "zdobyte"
    STRACONE = "stracone"
    ROZNICA = "roznica"


class RozstrzygniecieRemisu(StrEnum):
    WYGRANA_PO_DOGRYWCE = "wygrana_po_dogrywce"
    PORAZKA_PO_DOGRYWCE = "porazka_po_dogrywce"
    WYGRANA_PO_KARNYCH = "wygrana_po_karnych"
    PORAZKA_PO_KARNYCH = "porazka_po_karnych"


@dataclass(frozen=True)
class FiltryDruzyny:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    przeciwnik: str | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "-data"
    tylko_zakonczone: bool = False

    def __post_init__(self) -> None:
        if self.id_sezon is not None and self.id_sezon < 1:
            raise ValueError("Niepoprawny sezon.")
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Niepoprawny numer lub rozmiar strony.")
        if self.sortowanie not in {"data", "-data"}:
            raise ValueError("Niepoprawne sortowanie.")


@dataclass(frozen=True)
class FiltryZawodnikowDruzyny:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    zawodnik: str | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "-bramki"

    def __post_init__(self) -> None:
        if self.id_sezon is not None and self.id_sezon < 1:
            raise ValueError("Niepoprawny sezon.")
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Niepoprawny numer lub rozmiar strony zawodników.")
        if self.sortowanie not in SORTOWANIA_ZAWODNIKOW_DRUZYNY:
            raise ValueError("Niepoprawne sortowanie zawodników.")


@dataclass(frozen=True)
class FiltryZestawieniaDruzyny:
    id_sezon: int
    rozgrywki: str | None = None
    przeciwnik: str | None = None

    def __post_init__(self) -> None:
        if self.id_sezon < 1:
            raise ValueError("Niepoprawny sezon zestawienia.")


@dataclass(frozen=True)
class WpisZestawienia:
    id_mecz: int
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    nr_koszulki: int | None
    pozycja: str | None
    bramki: int | None
    dwie_minuty: int | None
    upomnienie: bool | None
    dyskwalifikacja: bool | None
    karne_bramki: int | None
    karne_liczba: int | None


@dataclass(frozen=True)
class DaneZestawieniaDruzyny:
    mecze: tuple["MeczDruzyny", ...]
    wpisy: tuple[WpisZestawienia, ...]


@dataclass(frozen=True)
class StatystykiZestawienia:
    mecze: int
    bramki: int | None
    dwie_minuty: int | None
    upomnienia: int
    dyskwalifikacje: int
    karne_trafione: int | None
    karne_wszystkie: int | None


@dataclass(frozen=True)
class WierszZestawienia:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    numery: tuple[int, ...]
    pozycje: tuple[str, ...]
    komorki: tuple[StatystykiZestawienia | None, ...]
    suma: StatystykiZestawienia


@dataclass(frozen=True)
class ZestawienieSezonuDruzyny:
    mecze: tuple["WystepDruzyny", ...]
    wiersze: tuple[WierszZestawienia, ...]
    sumy_meczow: tuple[StatystykiZestawienia, ...]
    suma: StatystykiZestawienia


@dataclass(frozen=True)
class SezonDruzyny:
    id_zespol_sezon: int
    id_sezon: int
    sezon: str
    nazwa: str | None
    plec: str | None
    kategoria: str | None
    miasto: str | None
    wycofany: bool | None


@dataclass(frozen=True)
class HalaDruzyny:
    id_hala: int
    nazwa: str | None
    miasto: str | None
    liczba_meczow: int
    mecze_z_widzami: int
    srednia_widzow: float | None


@dataclass(frozen=True)
class SzczegolyDruzyny:
    id_zespol: int
    nr_klubu: int | None
    nazwa: str | None
    plec: str | None
    kategoria: str | None
    wycofany: bool | None
    liczba_meczow: int
    sezony: tuple[SezonDruzyny, ...]
    hale: tuple[HalaDruzyny, ...]


@dataclass(frozen=True)
class OpcjeFiltrowDruzyny:
    sezony: tuple[OpcjaWyboru, ...]
    rozgrywki: tuple[str, ...]


@dataclass(frozen=True)
class MeczDruzyny:
    mecz: PozycjaListyMeczow
    kolumna: str


@dataclass(frozen=True)
class StronaMeczowDruzyny:
    pozycje: list[MeczDruzyny]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class WystepDruzyny:
    id_mecz: int
    termin: datetime | None
    sezon: str
    rozgrywki: str
    miejsce: str | None
    przeciwnik: str | None
    status: StatusMeczu
    bramki: int | None
    stracone: int | None
    rezultat: RezultatMeczu | None
    rozstrzygniecie: RozstrzygniecieRemisu | None
    widzowie: int | None


@dataclass(frozen=True)
class ZawodnikDruzyny:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    mecze: int
    mecze_ze_znanymi_bramkami: int
    bramki: int | None
    karne_bramki: int | None
    karne_liczba: int | None
    dwie_minuty: int | None
    upomnienia: int | None
    dyskwalifikacje: int | None
    sezony: tuple[str, ...]
    ostatni_mecz: datetime | None


@dataclass(frozen=True)
class StronaZawodnikowDruzyny:
    pozycje: list[ZawodnikDruzyny]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class FrekwencjaMiejsca:
    mecze: int
    znane: int
    suma: int | None
    srednia: float | None
    mediana: float | None
    rekord: WystepDruzyny | None


@dataclass(frozen=True)
class FrekwencjaDruzyny:
    dom: FrekwencjaMiejsca
    wyjazd: FrekwencjaMiejsca


@dataclass(frozen=True)
class BilansDruzyny:
    mecze: int
    rozegrane: int
    wygrane: int
    remisy: int
    porazki: int
    remisy_wygrane_po_dogrywce: int
    remisy_przegrane_po_dogrywce: int
    remisy_wygrane_po_karnych: int
    remisy_przegrane_po_karnych: int
    bramki_zdobyte: int
    bramki_stracone: int
    walkowery: int
    wycofane: int
    bez_wyniku: int
    frekwencja: FrekwencjaDruzyny


@dataclass(frozen=True)
class BilansRozgrywekSezonu:
    rozgrywki: str
    bilans: BilansDruzyny


@dataclass(frozen=True)
class BilansSezonuDruzyny:
    sezon: str
    nazwa_druzyny: str | None
    bilans: BilansDruzyny
    rozgrywki: tuple[BilansRozgrywekSezonu, ...]


@dataclass(frozen=True)
class PodsumowanieDruzyny:
    rozegrane: tuple[WystepDruzyny, ...]
    bilans: BilansDruzyny
    bilanse_sezonow: tuple[BilansSezonuDruzyny, ...]
    najwyzsze_zwyciestwo: WystepDruzyny | None
    najwyzsza_porazka: WystepDruzyny | None
    najwiecej_zdobytych: WystepDruzyny | None
    najwiecej_straconych: WystepDruzyny | None
    najdluzsza_seria_zwyciestw: int
    najdluzsza_seria_bez_porazki: int


@dataclass(frozen=True)
class BramkiMeczuDruzyny:
    wystep: WystepDruzyny
    bramki: int | None

    @property
    def id_mecz(self) -> int:
        return self.wystep.id_mecz

    @property
    def termin(self) -> datetime | None:
        return self.wystep.termin

    @property
    def sezon(self) -> str:
        return self.wystep.sezon

    @property
    def rozgrywki(self) -> str:
        return self.wystep.rozgrywki

    @property
    def miejsce(self) -> str | None:
        return self.wystep.miejsce


@dataclass(frozen=True)
class SeriaBramekDruzyny:
    rodzaj: RodzajBramek
    mecze: tuple[BramkiMeczuDruzyny, ...]
    statystyki: StatystykiBramekGrupy
    statystyki_sezonow: tuple[StatystykiSezonu, ...]
    mediana_dom: float | None
    mediana_wyjazd: float | None
    forma: FormaIRegularnosc


class KolejnoscPozycjiPolicy:
    KOLEJNOSC = ("bramkarz", "rozgrywający", "skrzydłowy", "obrotowy")

    def pozycja(self, pozycje: tuple[str, ...]) -> int:
        if not pozycje:
            return len(self.KOLEJNOSC) + 1
        nazwa = pozycje[0].casefold()
        return next(
            (indeks for indeks, prefiks in enumerate(self.KOLEJNOSC) if nazwa.startswith(prefiks)),
            len(self.KOLEJNOSC),
        )


class WystepDruzynyPolicy:
    def __init__(self, reguly: MeczPolicy) -> None:
        self._reguly = reguly

    def wystep(self, dane: MeczDruzyny) -> WystepDruzyny:
        mecz = dane.mecz.mecz
        wlasna = dane.kolumna == "gosp"
        status = self._reguly.status(mecz)
        bramki, stracone = self._wlasne(mecz.wynik_gosp_full, mecz.wynik_gosc_full, wlasna)
        rozegrany = status == StatusMeczu.ROZEGRANY
        rezultat = None
        if rozegrany and bramki is not None and stracone is not None:
            rezultat = (
                RezultatMeczu.WYGRANA
                if bramki > stracone
                else RezultatMeczu.PORAZKA
                if bramki < stracone
                else RezultatMeczu.REMIS
            )
        return WystepDruzyny(
            id_mecz=dane.mecz.id_mecz,
            termin=dane.mecz.termin,
            sezon=dane.mecz.sezon or "—",
            rozgrywki=dane.mecz.rozgrywki or "—",
            miejsce=self._miejsce(mecz, wlasna),
            przeciwnik=dane.mecz.gosc if wlasna else dane.mecz.gospodarz,
            status=status,
            bramki=bramki if rozegrany else None,
            stracone=stracone if rozegrany else None,
            rezultat=rezultat,
            rozstrzygniecie=(
                self._rozstrzygniecie(mecz, wlasna) if rezultat == RezultatMeczu.REMIS else None
            ),
            widzowie=mecz.widzowie if rozegrany else None,
        )

    @staticmethod
    def _miejsce(mecz: DaneMeczu, wlasna: bool) -> str:
        return "dom" if wlasna != bool(mecz.zamiana) else "wyjazd"

    @staticmethod
    def _wlasne(gosp: int | None, gosc: int | None, wlasna: bool) -> tuple[int | None, int | None]:
        return (gosp, gosc) if wlasna else (gosc, gosp)

    def _rozstrzygniecie(self, mecz: DaneMeczu, wlasna: bool) -> RozstrzygniecieRemisu | None:
        dogrywka = self._wlasne(mecz.dogrywka_2_full_gosp, mecz.dogrywka_2_full_gosc, wlasna)
        if None in dogrywka:
            dogrywka = self._wlasne(mecz.dogrywka_1_full_gosp, mecz.dogrywka_1_full_gosc, wlasna)
        if dogrywka[0] is not None and dogrywka[1] is not None and dogrywka[0] != dogrywka[1]:
            return (
                RozstrzygniecieRemisu.WYGRANA_PO_DOGRYWCE
                if dogrywka[0] > dogrywka[1]
                else RozstrzygniecieRemisu.PORAZKA_PO_DOGRYWCE
            )
        karne = self._wlasne(mecz.dogrywka_karne_gosp, mecz.dogrywka_karne_gosc, wlasna)
        if karne[0] is not None and karne[1] is not None and karne[0] != karne[1]:
            return (
                RozstrzygniecieRemisu.WYGRANA_PO_KARNYCH
                if karne[0] > karne[1]
                else RozstrzygniecieRemisu.PORAZKA_PO_KARNYCH
            )
        return None
