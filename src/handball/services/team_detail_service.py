from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from statistics import mean, median

from handball.contracts.team_detail_repository import SzczegolyDruzynyReadRepository
from handball.domain.match_rules import StatusMeczu
from handball.domain.team_details import (
    BilansDruzyny,
    BilansRozgrywekSezonu,
    BilansSezonuDruzyny,
    BramkiMeczuDruzyny,
    FiltryDruzyny,
    FiltryZawodnikowDruzyny,
    FiltryZestawieniaDruzyny,
    FrekwencjaDruzyny,
    FrekwencjaMiejsca,
    KolejnoscPozycjiPolicy,
    OpcjeFiltrowDruzyny,
    PodsumowanieDruzyny,
    RezultatMeczu,
    RodzajBramek,
    RozstrzygniecieRemisu,
    SeriaBramekDruzyny,
    SezonDruzyny,
    StatystykiZestawienia,
    StronaMeczowDruzyny,
    StronaZawodnikowDruzyny,
    SzczegolyDruzyny,
    WierszZestawienia,
    WpisZestawienia,
    WystepDruzyny,
    WystepDruzynyPolicy,
    ZestawienieSezonuDruzyny,
)
from handball.services.goal_statistics import StatystykiBramekCalculator


@dataclass(frozen=True)
class AnalitykaDruzyny:
    podsumowanie: PodsumowanieDruzyny
    zdobyte: SeriaBramekDruzyny
    stracone: SeriaBramekDruzyny
    roznica: SeriaBramekDruzyny


@dataclass(frozen=True)
class HistoriaDruzyny:
    bilans: BilansDruzyny
    sezony: tuple[BilansSezonuDruzyny, ...]


class FrekwencjaDruzynyCalculator:
    def frekwencja(self, wystepy: Sequence[WystepDruzyny]) -> FrekwencjaDruzyny:
        rozegrane = [w for w in wystepy if w.status == StatusMeczu.ROZEGRANY]
        return FrekwencjaDruzyny(
            dom=self._miejsce([w for w in rozegrane if w.miejsce == "dom"]),
            wyjazd=self._miejsce([w for w in rozegrane if w.miejsce == "wyjazd"]),
        )

    @staticmethod
    def _miejsce(wystepy: Sequence[WystepDruzyny]) -> FrekwencjaMiejsca:
        znane = [w for w in wystepy if w.widzowie is not None]
        wartosci = [w.widzowie for w in znane if w.widzowie is not None]
        return FrekwencjaMiejsca(
            mecze=len(wystepy),
            znane=len(znane),
            suma=sum(wartosci) if wartosci else None,
            srednia=float(mean(wartosci)) if wartosci else None,
            mediana=float(median(wartosci)) if wartosci else None,
            rekord=max(znane, key=lambda w: w.widzowie or 0, default=None),
        )


class SzczegolyDruzynyService:
    def __init__(self, repozytorium: SzczegolyDruzynyReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_szczegoly(self, id_zespol: int) -> SzczegolyDruzyny:
        return self._repozytorium.pobierz_szczegoly(id_zespol)

    def pobierz_opcje_filtrow(self, id_zespol: int) -> OpcjeFiltrowDruzyny:
        return self._repozytorium.pobierz_opcje_filtrow(id_zespol)

    def pobierz_mecze(self, id_zespol: int, filtry: FiltryDruzyny) -> StronaMeczowDruzyny:
        return self._repozytorium.pobierz_mecze(id_zespol, filtry)

    def pobierz_zawodnikow(
        self, id_zespol: int, filtry: FiltryZawodnikowDruzyny
    ) -> StronaZawodnikowDruzyny:
        return self._repozytorium.pobierz_zawodnikow(id_zespol, filtry)


class ZestawienieDruzynyService:
    def __init__(
        self,
        repozytorium: SzczegolyDruzynyReadRepository,
        reguly: WystepDruzynyPolicy,
        pozycje: KolejnoscPozycjiPolicy,
    ) -> None:
        self._repozytorium = repozytorium
        self._reguly = reguly
        self._pozycje = pozycje

    def pobierz_zestawienie(
        self, id_zespol: int, filtry: FiltryZestawieniaDruzyny
    ) -> ZestawienieSezonuDruzyny:
        dane = self._repozytorium.pobierz_zestawienie(id_zespol, filtry)
        identyfikatory = [mecz.mecz.id_mecz for mecz in dane.mecze]
        zawodnicy: dict[int, list[WpisZestawienia]] = {}
        mecze: dict[int, list[WpisZestawienia]] = {}
        for wpis in dane.wpisy:
            zawodnicy.setdefault(wpis.id_zawodnik, []).append(wpis)
            mecze.setdefault(wpis.id_mecz, []).append(wpis)
        wiersze = []
        for id_zawodnik, wpisy in zawodnicy.items():
            wedlug_meczu = {wpis.id_mecz: wpis for wpis in wpisy}
            ostatni = wpisy[-1]
            wiersze.append(
                WierszZestawienia(
                    id_zawodnik=id_zawodnik,
                    imie=ostatni.imie,
                    nazwisko=ostatni.nazwisko,
                    numery=tuple(
                        sorted({w.nr_koszulki for w in wpisy if w.nr_koszulki is not None})
                    ),
                    pozycje=self._pozycje_wpisow(wpisy),
                    komorki=tuple(
                        self._statystyki([wedlug_meczu[id_mecz]])
                        if id_mecz in wedlug_meczu
                        else None
                        for id_mecz in identyfikatory
                    ),
                    suma=self._statystyki(wpisy),
                )
            )
        wiersze.sort(
            key=lambda w: (
                self._pozycje.pozycja(w.pozycje),
                w.suma.bramki is None,
                -(w.suma.bramki or 0),
                (w.nazwisko or "").casefold(),
                (w.imie or "").casefold(),
            )
        )
        return ZestawienieSezonuDruzyny(
            mecze=tuple(self._reguly.wystep(mecz) for mecz in dane.mecze),
            wiersze=tuple(wiersze),
            sumy_meczow=tuple(
                self._statystyki(mecze.get(id_mecz, [])) for id_mecz in identyfikatory
            ),
            suma=self._statystyki(dane.wpisy),
        )

    @staticmethod
    def _pozycje_wpisow(wpisy: Sequence[WpisZestawienia]) -> tuple[str, ...]:
        czestosci = Counter(
            pozycja for w in wpisy if (pozycja := (w.pozycja or "").strip()) not in {"", "—", "-"}
        )
        return tuple(sorted(czestosci, key=lambda pozycja: (-czestosci[pozycja], pozycja)))

    @staticmethod
    def _statystyki(wpisy: Sequence[WpisZestawienia]) -> StatystykiZestawienia:
        def suma(wartosci: list[int | None]) -> int | None:
            znane = [w for w in wartosci if w is not None]
            return sum(znane) if znane else None

        return StatystykiZestawienia(
            mecze=len({w.id_mecz for w in wpisy}),
            bramki=suma([w.bramki for w in wpisy]),
            dwie_minuty=suma([w.dwie_minuty for w in wpisy]),
            upomnienia=sum(w.upomnienie is True for w in wpisy),
            dyskwalifikacje=sum(w.dyskwalifikacja is True for w in wpisy),
            karne_trafione=suma([w.karne_bramki for w in wpisy]),
            karne_wszystkie=suma([w.karne_liczba for w in wpisy]),
        )


class BilansDruzynyCalculator:
    def __init__(self, frekwencja: FrekwencjaDruzynyCalculator) -> None:
        self._frekwencja = frekwencja

    def bilans(self, wystepy: Sequence[WystepDruzyny]) -> BilansDruzyny:
        rozegrane = [w for w in wystepy if w.status == StatusMeczu.ROZEGRANY]
        rozstrzygniecia = [w.rozstrzygniecie for w in rozegrane]
        return BilansDruzyny(
            mecze=len(wystepy),
            rozegrane=len(rozegrane),
            wygrane=sum(w.rezultat == RezultatMeczu.WYGRANA for w in rozegrane),
            remisy=sum(w.rezultat == RezultatMeczu.REMIS for w in rozegrane),
            porazki=sum(w.rezultat == RezultatMeczu.PORAZKA for w in rozegrane),
            remisy_wygrane_po_dogrywce=rozstrzygniecia.count(
                RozstrzygniecieRemisu.WYGRANA_PO_DOGRYWCE
            ),
            remisy_przegrane_po_dogrywce=rozstrzygniecia.count(
                RozstrzygniecieRemisu.PORAZKA_PO_DOGRYWCE
            ),
            remisy_wygrane_po_karnych=rozstrzygniecia.count(
                RozstrzygniecieRemisu.WYGRANA_PO_KARNYCH
            ),
            remisy_przegrane_po_karnych=rozstrzygniecia.count(
                RozstrzygniecieRemisu.PORAZKA_PO_KARNYCH
            ),
            bramki_zdobyte=sum(w.bramki or 0 for w in rozegrane),
            bramki_stracone=sum(w.stracone or 0 for w in rozegrane),
            walkowery=sum(w.status == StatusMeczu.WALKOWER for w in wystepy),
            wycofane=sum(w.status == StatusMeczu.WYCOFANY for w in wystepy),
            bez_wyniku=sum(w.status == StatusMeczu.ZAPLANOWANY for w in wystepy),
            frekwencja=self._frekwencja.frekwencja(wystepy),
        )

    def bilanse_sezonow(
        self,
        wystepy: Sequence[WystepDruzyny],
        nazwy: dict[str, str | None],
    ) -> tuple[BilansSezonuDruzyny, ...]:
        sezony: dict[str, list[WystepDruzyny]] = {}
        for wystep in wystepy:
            sezony.setdefault(wystep.sezon, []).append(wystep)
        wynik = []
        for sezon, wystepy_sezonu in sezony.items():
            rozgrywki: dict[str, list[WystepDruzyny]] = {}
            for wystep in wystepy_sezonu:
                rozgrywki.setdefault(wystep.rozgrywki, []).append(wystep)
            wynik.append(
                BilansSezonuDruzyny(
                    sezon=sezon,
                    nazwa_druzyny=nazwy.get(sezon),
                    bilans=self.bilans(wystepy_sezonu),
                    rozgrywki=tuple(
                        BilansRozgrywekSezonu(nazwa, self.bilans(grupa))
                        for nazwa, grupa in rozgrywki.items()
                    ),
                )
            )
        return tuple(wynik)


class AnalitykaDruzynyService:
    def __init__(
        self,
        repozytorium: SzczegolyDruzynyReadRepository,
        reguly: WystepDruzynyPolicy,
        bilanse: BilansDruzynyCalculator,
        kalkulator: StatystykiBramekCalculator,
    ) -> None:
        self._repozytorium = repozytorium
        self._reguly = reguly
        self._bilanse = bilanse
        self._kalkulator = kalkulator

    def pobierz_historie(
        self, id_zespol: int, sezony_druzyny: Sequence[SezonDruzyny]
    ) -> HistoriaDruzyny:
        kolejnosc = {sezon.sezon: indeks for indeks, sezon in enumerate(sezony_druzyny)}
        wystepy = self._wystepy(id_zespol, FiltryDruzyny())
        bilanse = self._bilanse.bilanse_sezonow(wystepy, self._nazwy(sezony_druzyny))
        return HistoriaDruzyny(
            bilans=self._bilanse.bilans(wystepy),
            sezony=tuple(
                sorted(bilanse, key=lambda bilans: kolejnosc.get(bilans.sezon, len(kolejnosc)))
            ),
        )

    def pobierz_analityke(
        self,
        id_zespol: int,
        filtry: FiltryDruzyny,
        sezony_druzyny: Sequence[SezonDruzyny],
    ) -> AnalitykaDruzyny:
        wystepy = self._wystepy(id_zespol, filtry)
        rozegrane = tuple(w for w in wystepy if w.status == StatusMeczu.ROZEGRANY)
        return AnalitykaDruzyny(
            podsumowanie=self._podsumowanie(wystepy, rozegrane, self._nazwy(sezony_druzyny)),
            zdobyte=self._seria(RodzajBramek.ZDOBYTE, rozegrane),
            stracone=self._seria(RodzajBramek.STRACONE, rozegrane),
            roznica=self._seria(RodzajBramek.ROZNICA, rozegrane),
        )

    def _wystepy(self, id_zespol: int, filtry: FiltryDruzyny) -> tuple[WystepDruzyny, ...]:
        return tuple(
            self._reguly.wystep(mecz)
            for mecz in self._repozytorium.pobierz_wszystkie_mecze(id_zespol, filtry)
        )

    @staticmethod
    def _nazwy(sezony_druzyny: Sequence[SezonDruzyny]) -> dict[str, str | None]:
        return {sezon.sezon: sezon.nazwa for sezon in sezony_druzyny}

    def _seria(
        self, rodzaj: RodzajBramek, rozegrane: Sequence[WystepDruzyny]
    ) -> SeriaBramekDruzyny:
        mecze = tuple(BramkiMeczuDruzyny(w, self._wartosc(rodzaj, w)) for w in rozegrane)
        kalkulator = self._kalkulator
        return SeriaBramekDruzyny(
            rodzaj=rodzaj,
            mecze=mecze,
            statystyki=kalkulator.statystyki_grupy(mecze),
            statystyki_sezonow=kalkulator.statystyki_sezonow(mecze),
            mediana_dom=kalkulator.mediana_wedlug_miejsca(mecze, "dom"),
            mediana_wyjazd=kalkulator.mediana_wedlug_miejsca(mecze, "wyjazd"),
            forma=kalkulator.forma(mecze),
        )

    @staticmethod
    def _wartosc(rodzaj: RodzajBramek, wystep: WystepDruzyny) -> int | None:
        if rodzaj == RodzajBramek.ZDOBYTE:
            return wystep.bramki
        if rodzaj == RodzajBramek.STRACONE:
            return wystep.stracone
        if wystep.bramki is None or wystep.stracone is None:
            return None
        return wystep.bramki - wystep.stracone

    def _podsumowanie(
        self,
        wystepy: Sequence[WystepDruzyny],
        rozegrane: Sequence[WystepDruzyny],
        nazwy: dict[str, str | None],
    ) -> PodsumowanieDruzyny:
        kalkulator = self._kalkulator
        wygrane = [w for w in rozegrane if w.rezultat == RezultatMeczu.WYGRANA]
        porazki = [w for w in rozegrane if w.rezultat == RezultatMeczu.PORAZKA]
        return PodsumowanieDruzyny(
            rozegrane=tuple(rozegrane),
            bilans=self._bilanse.bilans(wystepy),
            bilanse_sezonow=self._bilanse.bilanse_sezonow(wystepy, nazwy),
            najwyzsze_zwyciestwo=self._skrajny(wygrane, lambda w: self._roznica(w)),
            najwyzsza_porazka=self._skrajny(porazki, lambda w: -self._roznica(w)),
            najwiecej_zdobytych=self._skrajny(rozegrane, lambda w: w.bramki or 0),
            najwiecej_straconych=self._skrajny(rozegrane, lambda w: w.stracone or 0),
            najdluzsza_seria_zwyciestw=kalkulator.najdluzsza_seria(
                w.rezultat == RezultatMeczu.WYGRANA for w in rozegrane
            ),
            najdluzsza_seria_bez_porazki=kalkulator.najdluzsza_seria(
                w.rezultat != RezultatMeczu.PORAZKA for w in rozegrane
            ),
        )

    @staticmethod
    def _roznica(wystep: WystepDruzyny) -> int:
        return (wystep.bramki or 0) - (wystep.stracone or 0)

    @staticmethod
    def _skrajny(
        wystepy: Sequence[WystepDruzyny], klucz: Callable[[WystepDruzyny], int]
    ) -> WystepDruzyny | None:
        return max(wystepy, key=klucz, default=None)
