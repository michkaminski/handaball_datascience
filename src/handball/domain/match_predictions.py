from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Plec(StrEnum):
    MEZCZYZN = "M"
    KOBIET = "K"


class PoziomRozgrywek(StrEnum):
    SUPERLIGA = "superliga"
    LIGA_CENTRALNA = "liga_centralna"
    I_LIGA = "i_liga"


@dataclass(frozen=True)
class Liga:
    poziom: PoziomRozgrywek
    plec: Plec


class Typ1X2(StrEnum):
    GOSPODARZ = "H"
    REMIS = "X"
    GOSC = "A"


class KlasaTrafnosci(StrEnum):
    BARDZO_TRAFNA = "bardzo_trafna"
    TRAFNA = "trafna"
    PRZECIETNA = "przecietna"
    SLABA = "slaba"
    BARDZO_SLABA = "bardzo_slaba"


class KlasaWyniku(StrEnum):
    DOKLADNY_WYNIK = "dokladny_wynik"
    DOKLADNA_ROZNICA = "dokladna_roznica"
    ROZNICA_1 = "roznica_1"
    ROZNICA_2_3 = "roznica_2_3"
    ROZNICA_4_PLUS = "roznica_4_plus"


class PowodWykluczenia(StrEnum):
    NIEZNANA_LIGA = "nieznana_liga"
    BRAK_DATY = "brak_daty"
    NIEPRAWIDLOWA_DATA = "nieprawidlowa_data"
    WYCOFANY = "wycofany"
    WALKOWER = "walkower"
    BRAK_GOSPODARZA = "brak_gospodarza"
    BRAK_GOSCIA = "brak_goscia"
    BRAK_WYNIKU = "brak_wyniku"


@dataclass(frozen=True)
class WzorzecPoziomu:
    poziom: PoziomRozgrywek
    wyrazenie: str


@dataclass(frozen=True)
class WzorceNazwLig:
    wzorce: tuple[WzorzecPoziomu, ...] = (
        WzorzecPoziomu(PoziomRozgrywek.SUPERLIGA, "superliga|superligę|ekstraklasa"),
        WzorzecPoziomu(PoziomRozgrywek.LIGA_CENTRALNA, r"liga\s+centralna"),
        WzorzecPoziomu(PoziomRozgrywek.I_LIGA, r"(^|[^a-ząćęłńóśźż])i\s+liga"),
    )

    def poziom(self, nazwa: str | None) -> PoziomRozgrywek | None:
        if not nazwa:
            return None
        for wzorzec in self.wzorce:
            if re.search(wzorzec.wyrazenie, nazwa, re.IGNORECASE):
                return wzorzec.poziom
        return None


@dataclass(frozen=True)
class KonfiguracjaSilyDruzyn:
    wersja_modelu: str = "team_strength_v1"
    rating_poczatkowy: float = 1500.0
    przewaga_wlasnego_parkietu: float = 50.0
    wyraz_wolny_roznicy: float = 0.0
    nachylenie_roznicy: float = 0.025
    poczatkowa_suma_bramek: float = 58.0
    alfa_ewma: float = 0.08
    wspolczynnik_k: float = 25.0
    skala_roznicy: float = 6.0
    zachowanie_miedzy_sezonami: float = 0.70
    prog_remisu: float = 0.75

    def jako_slownik(self) -> dict[str, float]:
        return {
            "initial_rating": self.rating_poczatkowy,
            "home_advantage": self.przewaga_wlasnego_parkietu,
            "margin_intercept": self.wyraz_wolny_roznicy,
            "margin_slope": self.nachylenie_roznicy,
            "initial_expected_total": self.poczatkowa_suma_bramek,
            "ewma_alpha": self.alfa_ewma,
            "k_factor": self.wspolczynnik_k,
            "margin_scale": self.skala_roznicy,
            "season_retention": self.zachowanie_miedzy_sezonami,
            "draw_margin_threshold": self.prog_remisu,
        }


@dataclass(frozen=True)
class ProgiTrafnosci:
    bardzo_trafna: float = 2.0
    trafna: float = 4.0
    przecietna: float = 7.0
    slaba: float = 10.0
    progi_podsumowania: tuple[float, ...] = (2.0, 4.0, 6.0)

    def klasyfikuj(self, blad_wyniku: float) -> KlasaTrafnosci:
        if blad_wyniku <= self.bardzo_trafna:
            return KlasaTrafnosci.BARDZO_TRAFNA
        if blad_wyniku <= self.trafna:
            return KlasaTrafnosci.TRAFNA
        if blad_wyniku <= self.przecietna:
            return KlasaTrafnosci.PRZECIETNA
        if blad_wyniku <= self.slaba:
            return KlasaTrafnosci.SLABA
        return KlasaTrafnosci.BARDZO_SLABA


@dataclass(frozen=True)
class ProgiWyniku:
    bliska_roznica: int = 1
    umiarkowana_roznica: int = 3

    def klasyfikuj(self, dokladny_wynik: bool, blad_roznicy: int) -> KlasaWyniku:
        if dokladny_wynik:
            return KlasaWyniku.DOKLADNY_WYNIK
        if blad_roznicy == 0:
            return KlasaWyniku.DOKLADNA_ROZNICA
        if blad_roznicy <= self.bliska_roznica:
            return KlasaWyniku.ROZNICA_1
        if blad_roznicy <= self.umiarkowana_roznica:
            return KlasaWyniku.ROZNICA_2_3
        return KlasaWyniku.ROZNICA_4_PLUS


@dataclass(frozen=True)
class ZakresBacktestu:
    docelowa_liczba_sezonow_raportu: int | None = 10
    uwzglednij_sezon_w_toku: bool = True


@dataclass(frozen=True)
class MeczLigowy:
    id_mecz: int
    plec: str | None
    nazwa_rozgrywek: str | None
    id_sezon: int
    sezon: str
    rok_sezonu: int | None
    kolejka: int | None
    data: datetime | None
    id_zespol_gosp: int | None
    id_zespol_gosc: int | None
    nazwa_gosp: str | None
    nazwa_gosc: str | None
    wynik_gosp: int | None
    wynik_gosc: int | None
    zamiana: bool | None
    wycofany: bool | None
    walkower: bool


@dataclass(frozen=True)
class UczestnikPrognozy:
    id_zespol: int
    nazwa: str


@dataclass(frozen=True)
class SezonPrognoz:
    id_sezon: int
    nazwa: str
    rok: int | None

    @property
    def klucz(self) -> tuple[int, int]:
        return (self.rok if self.rok is not None else 0, self.id_sezon)


@dataclass(frozen=True)
class MeczDoPrognozy:
    id_mecz: int
    liga: Liga
    sezon: SezonPrognoz
    kolejka: int | None
    data: datetime
    gospodarz: UczestnikPrognozy
    gosc: UczestnikPrognozy
    bramki_gospodarza: int
    bramki_goscia: int
    zamiana: bool

    @property
    def klucz_chronologii(self) -> tuple[datetime, int]:
        return (self.data, self.id_mecz)


@dataclass(frozen=True)
class MeczPrzyszly:
    id_mecz: int
    liga: Liga
    sezon: SezonPrognoz
    kolejka: int | None
    data: datetime | None
    gospodarz: UczestnikPrognozy
    gosc: UczestnikPrognozy
    zamiana: bool


class KwalifikacjaMeczuPolicy:
    def __init__(self, wzorce: WzorceNazwLig) -> None:
        self._wzorce = wzorce

    def liga(self, mecz: MeczLigowy) -> Liga | None:
        poziom = self._wzorce.poziom(mecz.nazwa_rozgrywek)
        if poziom is None or mecz.plec not in {plec.value for plec in Plec}:
            return None
        return Liga(poziom, Plec(mecz.plec))

    def powod_wykluczenia(self, mecz: MeczLigowy) -> PowodWykluczenia | None:
        if self.liga(mecz) is None:
            return PowodWykluczenia.NIEZNANA_LIGA
        if mecz.wycofany:
            return PowodWykluczenia.WYCOFANY
        if mecz.walkower:
            return PowodWykluczenia.WALKOWER
        if mecz.id_zespol_gosp is None:
            return PowodWykluczenia.BRAK_GOSPODARZA
        if mecz.id_zespol_gosc is None:
            return PowodWykluczenia.BRAK_GOSCIA
        if mecz.wynik_gosp is None or mecz.wynik_gosc is None:
            return PowodWykluczenia.BRAK_WYNIKU
        if mecz.data is None:
            return PowodWykluczenia.BRAK_DATY
        if mecz.rok_sezonu is not None and mecz.data.year not in {
            mecz.rok_sezonu,
            mecz.rok_sezonu + 1,
        }:
            return PowodWykluczenia.NIEPRAWIDLOWA_DATA
        return None

    def powod_braku_zapowiedzi(self, mecz: MeczLigowy) -> PowodWykluczenia | None:
        if self.liga(mecz) is None:
            return PowodWykluczenia.NIEZNANA_LIGA
        if mecz.wycofany:
            return PowodWykluczenia.WYCOFANY
        if mecz.walkower:
            return PowodWykluczenia.WALKOWER
        if mecz.id_zespol_gosp is None:
            return PowodWykluczenia.BRAK_GOSPODARZA
        if mecz.id_zespol_gosc is None:
            return PowodWykluczenia.BRAK_GOSCIA
        return None

    def do_zapowiedzi(self, mecz: MeczLigowy) -> MeczPrzyszly:
        liga = self.liga(mecz)
        if (
            self.powod_braku_zapowiedzi(mecz) is not None
            or liga is None
            or mecz.id_zespol_gosp is None
            or mecz.id_zespol_gosc is None
        ):
            raise ValueError(f"Mecz {mecz.id_mecz} nie kwalifikuje się do zapowiedzi.")
        kolumna_gosp, kolumna_gosc = self._uczestnicy(
            mecz, mecz.id_zespol_gosp, mecz.id_zespol_gosc
        )
        zamiana = bool(mecz.zamiana)
        return MeczPrzyszly(
            id_mecz=mecz.id_mecz,
            liga=liga,
            sezon=SezonPrognoz(mecz.id_sezon, mecz.sezon, mecz.rok_sezonu),
            kolejka=mecz.kolejka,
            data=mecz.data,
            gospodarz=kolumna_gosc if zamiana else kolumna_gosp,
            gosc=kolumna_gosp if zamiana else kolumna_gosc,
            zamiana=zamiana,
        )

    def _uczestnicy(
        self, mecz: MeczLigowy, id_gosp: int, id_gosc: int
    ) -> tuple[UczestnikPrognozy, UczestnikPrognozy]:
        return (
            UczestnikPrognozy(id_gosp, (mecz.nazwa_gosp or "").strip() or f"Drużyna #{id_gosp}"),
            UczestnikPrognozy(id_gosc, (mecz.nazwa_gosc or "").strip() or f"Drużyna #{id_gosc}"),
        )

    def do_prognozy(self, mecz: MeczLigowy) -> MeczDoPrognozy:
        liga = self.liga(mecz)
        if (
            self.powod_wykluczenia(mecz) is not None
            or liga is None
            or mecz.id_zespol_gosp is None
            or mecz.id_zespol_gosc is None
            or mecz.wynik_gosp is None
            or mecz.wynik_gosc is None
            or mecz.data is None
        ):
            raise ValueError(f"Mecz {mecz.id_mecz} nie kwalifikuje się do prognozy.")
        kolumna_gosp, kolumna_gosc = self._uczestnicy(
            mecz, mecz.id_zespol_gosp, mecz.id_zespol_gosc
        )
        zamiana = bool(mecz.zamiana)
        return MeczDoPrognozy(
            id_mecz=mecz.id_mecz,
            liga=liga,
            sezon=SezonPrognoz(mecz.id_sezon, mecz.sezon, mecz.rok_sezonu),
            kolejka=mecz.kolejka,
            data=mecz.data,
            gospodarz=kolumna_gosc if zamiana else kolumna_gosp,
            gosc=kolumna_gosp if zamiana else kolumna_gosc,
            bramki_gospodarza=mecz.wynik_gosc if zamiana else mecz.wynik_gosp,
            bramki_goscia=mecz.wynik_gosp if zamiana else mecz.wynik_gosc,
            zamiana=zamiana,
        )


@dataclass(frozen=True)
class RegresjaSezonowa:
    rating_konca_sezonu: float
    rating_po_regresji: float
    sezon_poprzedni: str
    liczba_regresji: int = 1


@dataclass(frozen=True)
class RatingPrzedMeczem:
    rating: float
    nowa_druzyna: bool
    regresja: RegresjaSezonowa | None


@dataclass(frozen=True)
class AktualizacjaEwma:
    id_mecz: int
    stan_przed: float
    suma_bramek: int
    alfa: float
    stan_po: float


@dataclass(frozen=True)
class StanPrzedMeczem:
    gospodarz: RatingPrzedMeczem
    gosc: RatingPrzedMeczem
    oczekiwana_suma_ligi: float
    ostatnie_aktualizacje_ewma: tuple[AktualizacjaEwma, ...]


@dataclass(frozen=True)
class PrognozaPunktowa:
    roznica_ratingow: float
    przewidywana_roznica: float
    przewidywana_suma: float
    bramki_gospodarza: float
    bramki_goscia: float
    typ: Typ1X2

    @property
    def bramki_gospodarza_prezentowane(self) -> int:
        return math.floor(self.bramki_gospodarza + 0.5)

    @property
    def bramki_goscia_prezentowane(self) -> int:
        return math.floor(self.bramki_goscia + 0.5)

    @property
    def roznica_prezentowana(self) -> int:
        return self.bramki_gospodarza_prezentowane - self.bramki_goscia_prezentowane

    @property
    def typ_prezentowany(self) -> Typ1X2:
        if self.roznica_prezentowana > 0:
            return Typ1X2.GOSPODARZ
        if self.roznica_prezentowana < 0:
            return Typ1X2.GOSC
        return Typ1X2.REMIS


@dataclass(frozen=True)
class OcenaPrognozy:
    roznica: int
    suma: int
    typ: Typ1X2
    trafiony: bool
    blad_gospodarza: float
    blad_goscia: float
    blad_roznicy: float
    blad_sumy: float
    blad_wyniku: float
    klasa: KlasaTrafnosci
    blad_roznicy_prezentowanej: int
    dokladny_wynik: bool
    klasa_wyniku: KlasaWyniku
    typ_prezentowany: Typ1X2

    @property
    def poprawny_typ_prognozy(self) -> bool:
        return self.typ_prezentowany == self.typ

    @property
    def poprawna_roznica(self) -> bool:
        return self.blad_roznicy_prezentowanej == 0


@dataclass(frozen=True)
class AktualizacjaRatingu:
    reszta_roznicy: float
    poprawka: float
    rating_gospodarza_po: float
    rating_goscia_po: float
    oczekiwana_suma_po: float


@dataclass(frozen=True)
class PrognozaMeczu:
    mecz: MeczDoPrognozy
    stan: StanPrzedMeczem
    prognoza: PrognozaPunktowa
    ocena: OcenaPrognozy
    aktualizacja: AktualizacjaRatingu
    parametry: KonfiguracjaSilyDruzyn
    w_raporcie: bool

    @property
    def wersja_modelu(self) -> str:
        return self.parametry.wersja_modelu

    def dotyczy_druzyny(self, id_zespol: int) -> bool:
        return id_zespol in {self.mecz.gospodarz.id_zespol, self.mecz.gosc.id_zespol}


class OcenaPrognozyPolicy:
    def __init__(self, progi: ProgiTrafnosci, progi_wyniku: ProgiWyniku | None = None) -> None:
        self._progi = progi
        self._progi_wyniku = progi_wyniku or ProgiWyniku()

    def ocen(self, prognoza: PrognozaPunktowa, mecz: MeczDoPrognozy) -> OcenaPrognozy:
        roznica = mecz.bramki_gospodarza - mecz.bramki_goscia
        blad_gospodarza = abs(prognoza.bramki_gospodarza - mecz.bramki_gospodarza)
        blad_goscia = abs(prognoza.bramki_goscia - mecz.bramki_goscia)
        blad_wyniku = blad_gospodarza + blad_goscia
        typ = self.typ_wyniku(roznica)
        dokladny_wynik = (
            prognoza.bramki_gospodarza_prezentowane == mecz.bramki_gospodarza
            and prognoza.bramki_goscia_prezentowane == mecz.bramki_goscia
        )
        blad_roznicy_prezentowanej = abs(prognoza.roznica_prezentowana - roznica)
        return OcenaPrognozy(
            roznica=roznica,
            suma=mecz.bramki_gospodarza + mecz.bramki_goscia,
            typ=typ,
            trafiony=typ == prognoza.typ,
            blad_gospodarza=blad_gospodarza,
            blad_goscia=blad_goscia,
            blad_roznicy=abs(prognoza.przewidywana_roznica - roznica),
            blad_sumy=abs(
                prognoza.przewidywana_suma - (mecz.bramki_gospodarza + mecz.bramki_goscia)
            ),
            blad_wyniku=blad_wyniku,
            klasa=self._progi.klasyfikuj(blad_wyniku),
            blad_roznicy_prezentowanej=blad_roznicy_prezentowanej,
            dokladny_wynik=dokladny_wynik,
            klasa_wyniku=self._progi_wyniku.klasyfikuj(dokladny_wynik, blad_roznicy_prezentowanej),
            typ_prezentowany=self.typ_wyniku(prognoza.roznica_prezentowana),
        )

    def typ_wyniku(self, roznica: int) -> Typ1X2:
        if roznica > 0:
            return Typ1X2.GOSPODARZ
        if roznica < 0:
            return Typ1X2.GOSC
        return Typ1X2.REMIS


@dataclass(frozen=True)
class WynikBacktestu:
    prognozy: tuple[PrognozaMeczu, ...]
    sezony_raportu: tuple[SezonPrognoz, ...]
    sezony_rozgrzewki: tuple[SezonPrognoz, ...]
    sezon_w_toku: SezonPrognoz | None
    wykluczenia: dict[PowodWykluczenia, int]
    parametry: KonfiguracjaSilyDruzyn

    @property
    def prognozy_raportu(self) -> tuple[PrognozaMeczu, ...]:
        return tuple(p for p in self.prognozy if p.w_raporcie)


@dataclass(frozen=True)
class FiltryPrognoz:
    wersja_modelu: str = "team_strength_v1"
    poziom: PoziomRozgrywek | None = None
    plec: Plec | None = None
    id_sezon: int | None = None
    druzyna: str | None = None
    trafiony: bool | None = None
    klasy: frozenset[KlasaTrafnosci] = frozenset()
    klasy_wyniku: frozenset[KlasaWyniku] = frozenset()
    tylko_dokladny_wynik: bool = False
    tylko_poprawna_roznica: bool = False
    poprawny_typ_prognozy: bool | None = None
    typy_wyniku: frozenset[Typ1X2] = frozenset()
    strona: int = 1
    rozmiar_strony: int = 100
    zakres: ZakresBacktestu = ZakresBacktestu()


@dataclass(frozen=True)
class LicznikProgu:
    prog: float
    liczba: int
    procent: float | None


@dataclass(frozen=True)
class PodsumowaniePrognoz:
    liczba: int
    trafione: int
    trafnosc: float | None
    mae_gospodarza: float | None
    mae_goscia: float | None
    mae_roznicy: float | None
    mae_sumy: float | None
    sredni_blad_wyniku: float | None
    mediana_bledu_wyniku: float | None
    progi: tuple[LicznikProgu, ...]
    dokladne_wyniki: int = 0
    poprawne_roznice: int = 0
    roznice_do_1: int = 0
    poprawne_typy_prognozy: int = 0


@dataclass(frozen=True)
class StronaPrognoz:
    pozycje: tuple[PrognozaMeczu, ...]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class OpisModeluPrognoz:
    wersja: str
    nazwa: str


@dataclass(frozen=True)
class RaportPrognoz:
    model: OpisModeluPrognoz
    modele: tuple[OpisModeluPrognoz, ...]
    strona: StronaPrognoz
    podsumowanie: PodsumowaniePrognoz
    sezony: tuple[SezonPrognoz, ...]
    sezony_rozgrzewki: tuple[SezonPrognoz, ...]
    sezon_w_toku: SezonPrognoz | None
    wykluczenia: dict[PowodWykluczenia, int]
    parametry: KonfiguracjaSilyDruzyn


@dataclass(frozen=True)
class SzczegolyPrognozy:
    model: OpisModeluPrognoz
    prognoza: PrognozaMeczu
    historia_gospodarza: tuple[PrognozaMeczu, ...]
    historia_goscia: tuple[PrognozaMeczu, ...]


@dataclass(frozen=True)
class PrognozaBiezaca:
    mecz: MeczPrzyszly
    stan: StanPrzedMeczem
    prognoza: PrognozaPunktowa
    parametry: KonfiguracjaSilyDruzyn
    liczba_meczow_ligi: int
    ostatni_mecz_ligi: datetime | None


@dataclass(frozen=True)
class PrognozaZapowiedzi:
    model: OpisModeluPrognoz
    po_meczu: PrognozaMeczu | None = None
    biezaca: PrognozaBiezaca | None = None
    powod_braku: PowodWykluczenia | None = None
