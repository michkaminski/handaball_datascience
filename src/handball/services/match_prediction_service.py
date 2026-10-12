from __future__ import annotations

import statistics
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from handball.contracts.match_prediction_repository import MeczeLigoweReadRepository
from handball.domain.errors import NieZnalezionoPrognozy, NieznanyModelPrognoz
from handball.domain.match_predictions import (
    FiltryPrognoz,
    KonfiguracjaSilyDruzyn,
    KwalifikacjaMeczuPolicy,
    LicznikProgu,
    Liga,
    MeczDoPrognozy,
    MeczLigowy,
    OcenaPrognozyPolicy,
    OpisModeluPrognoz,
    PodsumowaniePrognoz,
    PowodWykluczenia,
    ProgiTrafnosci,
    PrognozaBiezaca,
    PrognozaMeczu,
    PrognozaZapowiedzi,
    RaportPrognoz,
    SezonPrognoz,
    StronaPrognoz,
    SzczegolyPrognozy,
    WynikBacktestu,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.domain.team_strength_model import ModelSilyDruzyn


@dataclass(frozen=True)
class DefinicjaModeluPrognoz:
    opis: OpisModeluPrognoz
    konfiguracja: KonfiguracjaSilyDruzyn


class KatalogModeliPrognoz:
    def __init__(self, definicje: Sequence[DefinicjaModeluPrognoz] | None = None) -> None:
        domyslne = definicje or (
            DefinicjaModeluPrognoz(
                OpisModeluPrognoz("team_strength_v1", "Dynamic Team Strength V1"),
                KonfiguracjaSilyDruzyn(),
            ),
        )
        self._definicje = {definicja.opis.wersja: definicja for definicja in domyslne}

    @property
    def domyslna_wersja(self) -> str:
        return next(iter(self._definicje))

    def modele(self) -> tuple[OpisModeluPrognoz, ...]:
        return tuple(definicja.opis for definicja in self._definicje.values())

    def definicja(self, wersja: str) -> DefinicjaModeluPrognoz:
        try:
            return self._definicje[wersja]
        except KeyError as wyjatek:
            raise NieznanyModelPrognoz(f"Nieznany model prognoz: {wersja}.") from wyjatek

    def utworz_model(self, wersja: str) -> ModelSilyDruzyn:
        return ModelSilyDruzyn(self.definicja(wersja).konfiguracja)


@dataclass(frozen=True)
class PodzialSezonow:
    rozgrzewka: tuple[SezonPrognoz, ...]
    raport: tuple[SezonPrognoz, ...]
    w_toku: SezonPrognoz | None


class PodzialSezonowPolicy:
    def __init__(self, zakres: ZakresBacktestu) -> None:
        self._zakres = zakres

    def podziel(
        self, mecze: Iterable[MeczLigowy], zakres: ZakresBacktestu | None = None
    ) -> PodzialSezonow:
        zakres = zakres or self._zakres
        sezony: dict[int, SezonPrognoz] = {}
        nierozegrane: set[int] = set()
        for mecz in mecze:
            sezony.setdefault(
                mecz.id_sezon, SezonPrognoz(mecz.id_sezon, mecz.sezon, mecz.rok_sezonu)
            )
            if (
                (mecz.wynik_gosp is None or mecz.wynik_gosc is None)
                and not mecz.wycofany
                and not mecz.walkower
            ):
                nierozegrane.add(mecz.id_sezon)
        kolejne = sorted(sezony.values(), key=lambda sezon: sezon.klucz)
        if not kolejne:
            return PodzialSezonow((), (), None)
        w_toku = kolejne[-1] if kolejne[-1].id_sezon in nierozegrane else None
        pelne = kolejne[:-1] if w_toku else kolejne
        liczba = self._liczba_sezonow_raportu(len(pelne), zakres)
        raport = tuple(pelne[-liczba:]) if pelne else ()
        rozgrzewka = tuple(pelne[: len(pelne) - len(raport)])
        if w_toku and zakres.uwzglednij_sezon_w_toku:
            raport = (*raport, w_toku)
        return PodzialSezonow(rozgrzewka, raport, w_toku)

    def _liczba_sezonow_raportu(self, liczba_pelnych: int, zakres: ZakresBacktestu) -> int:
        dostepne = max(1, liczba_pelnych - 1)
        docelowa = zakres.docelowa_liczba_sezonow_raportu
        return dostepne if docelowa is None else min(docelowa, dostepne)


@dataclass(frozen=True)
class StanLigi:
    liczba_meczow: int
    ostatni_mecz: datetime


@dataclass(frozen=True)
class PrzeliczenieModelu:
    wynik: WynikBacktestu
    modele: Mapping[Liga, ModelSilyDruzyn]
    mecze: tuple[MeczLigowy, ...]


class BacktestPrognozService:
    def __init__(
        self,
        repozytorium: MeczeLigoweReadRepository,
        katalog: KatalogModeliPrognoz,
        kwalifikacja: KwalifikacjaMeczuPolicy,
        ocena: OcenaPrognozyPolicy,
        podzial: PodzialSezonowPolicy,
        wzorce: WzorceNazwLig,
    ) -> None:
        self._repozytorium = repozytorium
        self._katalog = katalog
        self._kwalifikacja = kwalifikacja
        self._ocena = ocena
        self._podzial = podzial
        self._wzorce = wzorce

    def uruchom(self, wersja_modelu: str, zakres: ZakresBacktestu | None = None) -> WynikBacktestu:
        return self.przelicz(wersja_modelu, zakres).wynik

    def przelicz(
        self, wersja_modelu: str, zakres: ZakresBacktestu | None = None
    ) -> PrzeliczenieModelu:
        definicja = self._katalog.definicja(wersja_modelu)
        surowe = self._repozytorium.pobierz_mecze(self._wzorce)
        wykluczenia: Counter[PowodWykluczenia] = Counter()
        mecze: list[MeczDoPrognozy] = []
        for surowy in surowe:
            powod = self._kwalifikacja.powod_wykluczenia(surowy)
            if powod is None:
                mecze.append(self._kwalifikacja.do_prognozy(surowy))
            else:
                wykluczenia[powod] += 1
        podzial = self._podzial.podziel(surowe, zakres)
        sezony_raportu = {sezon.id_sezon for sezon in podzial.raport}
        modele: dict[Liga, ModelSilyDruzyn] = {}
        prognozy: list[PrognozaMeczu] = []
        for mecz in sorted(mecze, key=lambda m: m.klucz_chronologii):
            if mecz.liga not in modele:
                modele[mecz.liga] = self._katalog.utworz_model(wersja_modelu)
            model = modele[mecz.liga]
            stan = model.stan_przed_meczem(mecz)
            prognoza = model.prognozuj(stan)
            ocena = self._ocena.ocen(prognoza, mecz)
            aktualizacja = model.aktualizuj(mecz, prognoza)
            prognozy.append(
                PrognozaMeczu(
                    mecz=mecz,
                    stan=stan,
                    prognoza=prognoza,
                    ocena=ocena,
                    aktualizacja=aktualizacja,
                    parametry=definicja.konfiguracja,
                    w_raporcie=mecz.sezon.id_sezon in sezony_raportu,
                )
            )
        return PrzeliczenieModelu(
            wynik=WynikBacktestu(
                prognozy=tuple(prognozy),
                sezony_raportu=podzial.raport,
                sezony_rozgrzewki=podzial.rozgrzewka,
                sezon_w_toku=podzial.w_toku,
                wykluczenia=dict(wykluczenia),
                parametry=definicja.konfiguracja,
            ),
            modele=modele,
            mecze=tuple(surowe),
        )


class PodsumowaniePrognozCalculator:
    def __init__(self, progi: ProgiTrafnosci) -> None:
        self._progi = progi

    def oblicz(self, prognozy: Sequence[PrognozaMeczu]) -> PodsumowaniePrognoz:
        liczba = len(prognozy)
        trafione = sum(1 for p in prognozy if p.ocena.trafiony)
        bledy_wyniku = [p.ocena.blad_wyniku for p in prognozy]
        return PodsumowaniePrognoz(
            liczba=liczba,
            trafione=trafione,
            trafnosc=trafione / liczba if liczba else None,
            mae_gospodarza=self._srednia(p.ocena.blad_gospodarza for p in prognozy),
            mae_goscia=self._srednia(p.ocena.blad_goscia for p in prognozy),
            mae_roznicy=self._srednia(p.ocena.blad_roznicy for p in prognozy),
            mae_sumy=self._srednia(p.ocena.blad_sumy for p in prognozy),
            sredni_blad_wyniku=self._srednia(bledy_wyniku),
            mediana_bledu_wyniku=statistics.median(bledy_wyniku) if bledy_wyniku else None,
            progi=tuple(
                LicznikProgu(
                    prog,
                    sum(1 for blad in bledy_wyniku if blad <= prog),
                    sum(1 for blad in bledy_wyniku if blad <= prog) / liczba if liczba else None,
                )
                for prog in self._progi.progi_podsumowania
            ),
            dokladne_wyniki=sum(1 for p in prognozy if p.ocena.dokladny_wynik),
            poprawne_roznice=sum(1 for p in prognozy if p.ocena.poprawna_roznica),
            roznice_do_1=sum(1 for p in prognozy if p.ocena.blad_roznicy_prezentowanej <= 1),
            poprawne_typy_prognozy=sum(1 for p in prognozy if p.ocena.poprawny_typ_prognozy),
        )

    def _srednia(self, wartosci: Iterable[float]) -> float | None:
        lista = list(wartosci)
        return statistics.fmean(lista) if lista else None


class RaportPrognozService:
    def __init__(
        self,
        backtest: BacktestPrognozService,
        katalog: KatalogModeliPrognoz,
        podsumowanie: PodsumowaniePrognozCalculator,
    ) -> None:
        self._backtest = backtest
        self._katalog = katalog
        self._podsumowanie = podsumowanie

    def pobierz_raport(self, filtry: FiltryPrognoz) -> RaportPrognoz:
        wynik = self._backtest.uruchom(filtry.wersja_modelu, filtry.zakres)
        if filtry.id_sezon is not None and filtry.id_sezon not in {
            sezon.id_sezon for sezon in wynik.sezony_raportu
        }:
            raise ValueError("Wybrany sezon nie należy do zakresu raportu.")
        pasujace = sorted(
            (p for p in wynik.prognozy_raportu if self._pasuje(p, filtry)),
            key=lambda p: p.mecz.klucz_chronologii,
            reverse=True,
        )
        liczba = len(pasujace)
        ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
        numer = min(filtry.strona, ostatnia)
        poczatek = (numer - 1) * filtry.rozmiar_strony
        return RaportPrognoz(
            model=self._katalog.definicja(filtry.wersja_modelu).opis,
            modele=self._katalog.modele(),
            strona=StronaPrognoz(
                tuple(pasujace[poczatek : poczatek + filtry.rozmiar_strony]),
                liczba,
                numer,
                filtry.rozmiar_strony,
            ),
            podsumowanie=self._podsumowanie.oblicz(pasujace),
            sezony=tuple(sorted(wynik.sezony_raportu, key=lambda s: s.klucz, reverse=True)),
            sezony_rozgrzewki=wynik.sezony_rozgrzewki,
            sezon_w_toku=wynik.sezon_w_toku,
            wykluczenia=wynik.wykluczenia,
            parametry=wynik.parametry,
        )

    def _pasuje(self, prognoza: PrognozaMeczu, filtry: FiltryPrognoz) -> bool:
        mecz = prognoza.mecz
        if filtry.poziom is not None and mecz.liga.poziom != filtry.poziom:
            return False
        if filtry.plec is not None and mecz.liga.plec != filtry.plec:
            return False
        if filtry.id_sezon is not None and mecz.sezon.id_sezon != filtry.id_sezon:
            return False
        if filtry.druzyna:
            szukane = filtry.druzyna.casefold()
            if not any(
                szukane in nazwa.casefold() for nazwa in (mecz.gospodarz.nazwa, mecz.gosc.nazwa)
            ):
                return False
        ocena = prognoza.ocena
        if filtry.trafiony is not None and ocena.trafiony != filtry.trafiony:
            return False
        if filtry.poprawny_typ_prognozy is not None and (
            ocena.poprawny_typ_prognozy != filtry.poprawny_typ_prognozy
        ):
            return False
        if filtry.typy_wyniku and ocena.typ not in filtry.typy_wyniku:
            return False
        if filtry.tylko_dokladny_wynik and not ocena.dokladny_wynik:
            return False
        if filtry.tylko_poprawna_roznica and not ocena.poprawna_roznica:
            return False
        if filtry.klasy and ocena.klasa not in filtry.klasy:
            return False
        return not filtry.klasy_wyniku or ocena.klasa_wyniku in filtry.klasy_wyniku


class SzczegolyPrognozyService:
    DLUGOSC_HISTORII = 10

    def __init__(self, backtest: BacktestPrognozService, katalog: KatalogModeliPrognoz) -> None:
        self._backtest = backtest
        self._katalog = katalog

    def pobierz(
        self, wersja_modelu: str, id_mecz: int, zakres: ZakresBacktestu | None = None
    ) -> SzczegolyPrognozy:
        wynik = self._backtest.uruchom(wersja_modelu, zakres)
        for indeks, prognoza in enumerate(wynik.prognozy):
            if prognoza.mecz.id_mecz == id_mecz:
                wczesniejsze = wynik.prognozy[:indeks]
                return SzczegolyPrognozy(
                    model=self._katalog.definicja(wersja_modelu).opis,
                    prognoza=prognoza,
                    historia_gospodarza=self._historia(
                        wczesniejsze, prognoza.mecz.gospodarz.id_zespol
                    ),
                    historia_goscia=self._historia(wczesniejsze, prognoza.mecz.gosc.id_zespol),
                )
        raise NieZnalezionoPrognozy(id_mecz)

    def _historia(
        self, prognozy: Sequence[PrognozaMeczu], id_zespol: int
    ) -> tuple[PrognozaMeczu, ...]:
        druzyny = [p for p in prognozy if p.dotyczy_druzyny(id_zespol)]
        return tuple(reversed(druzyny[-self.DLUGOSC_HISTORII :]))


class PrognozyModeluService:
    def __init__(self, backtest: BacktestPrognozService, katalog: KatalogModeliPrognoz) -> None:
        self._backtest = backtest
        self._katalog = katalog

    def nazwa(self, wersja_modelu: str) -> str:
        return self._katalog.definicja(wersja_modelu).opis.nazwa

    def prognozy(self, wersja_modelu: str) -> tuple[PrognozaMeczu, ...]:
        return self._backtest.uruchom(wersja_modelu).prognozy


class PrognozaZapowiedziService:
    def __init__(
        self,
        backtest: BacktestPrognozService,
        katalog: KatalogModeliPrognoz,
        kwalifikacja: KwalifikacjaMeczuPolicy,
    ) -> None:
        self._backtest = backtest
        self._katalog = katalog
        self._kwalifikacja = kwalifikacja

    def pobierz(self, wersja_modelu: str, id_mecz: int) -> PrognozaZapowiedzi:
        return self.pobierz_wiele(wersja_modelu, (id_mecz,))[id_mecz]

    def pobierz_wiele(
        self, wersja_modelu: str, id_meczow: Iterable[int]
    ) -> dict[int, PrognozaZapowiedzi]:
        opis = self._katalog.definicja(wersja_modelu).opis
        przeliczenie = self._backtest.przelicz(wersja_modelu)
        prognozy = {p.mecz.id_mecz: p for p in przeliczenie.wynik.prognozy}
        surowe = {m.id_mecz: m for m in przeliczenie.mecze}
        ligi = self._stan_lig(przeliczenie.wynik.prognozy)
        return {
            id_mecz: self._rozstrzygnij(
                wersja_modelu,
                opis,
                przeliczenie,
                ligi,
                prognozy.get(id_mecz),
                surowe.get(id_mecz),
            )
            for id_mecz in id_meczow
        }

    def _stan_lig(self, prognozy: Sequence[PrognozaMeczu]) -> dict[Liga, StanLigi]:
        ligi: dict[Liga, StanLigi] = {}
        for prognoza in prognozy:
            poprzedni = ligi.get(prognoza.mecz.liga)
            ligi[prognoza.mecz.liga] = StanLigi(
                (poprzedni.liczba_meczow if poprzedni else 0) + 1, prognoza.mecz.data
            )
        return ligi

    def _rozstrzygnij(
        self,
        wersja_modelu: str,
        opis: OpisModeluPrognoz,
        przeliczenie: PrzeliczenieModelu,
        ligi: Mapping[Liga, StanLigi],
        prognoza: PrognozaMeczu | None,
        surowy: MeczLigowy | None,
    ) -> PrognozaZapowiedzi:
        if prognoza is not None:
            return PrognozaZapowiedzi(opis, po_meczu=prognoza)
        if surowy is None:
            return PrognozaZapowiedzi(opis, powod_braku=PowodWykluczenia.NIEZNANA_LIGA)
        if surowy.wynik_gosp is not None and surowy.wynik_gosc is not None:
            return PrognozaZapowiedzi(
                opis, powod_braku=self._kwalifikacja.powod_wykluczenia(surowy)
            )
        powod = self._kwalifikacja.powod_braku_zapowiedzi(surowy)
        if powod is not None:
            return PrognozaZapowiedzi(opis, powod_braku=powod)
        return PrognozaZapowiedzi(
            opis, biezaca=self._biezaca(wersja_modelu, przeliczenie, ligi, surowy)
        )

    def _biezaca(
        self,
        wersja_modelu: str,
        przeliczenie: PrzeliczenieModelu,
        ligi: Mapping[Liga, StanLigi],
        surowy: MeczLigowy,
    ) -> PrognozaBiezaca:
        mecz = self._kwalifikacja.do_zapowiedzi(surowy)
        model = przeliczenie.modele.get(mecz.liga) or self._katalog.utworz_model(wersja_modelu)
        stan = model.stan_przed_meczem(mecz)
        liga = ligi.get(mecz.liga)
        return PrognozaBiezaca(
            mecz=mecz,
            stan=stan,
            prognoza=model.prognozuj(stan),
            parametry=model.konfiguracja,
            liczba_meczow_ligi=liga.liczba_meczow if liga else 0,
            ostatni_mecz_ligi=liga.ostatni_mecz if liga else None,
        )
