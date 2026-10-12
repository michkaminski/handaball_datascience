from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from handball.domain.match_predictions import KlasaTrafnosci, PrognozaMeczu
from handball.domain.match_preview import (
    BezposrednieMecze,
    MeczZapowiedzi,
    WystepZapowiedzi,
    ZawodnikKadry,
)
from handball.domain.match_statistics import StatystykiMeczu
from handball.domain.matches import ZawodnikMeczu


@dataclass(frozen=True)
class PunktRatingu:
    data: datetime
    rating: float
    id_mecz: int | None
    analizowany: bool = False
    sezon: str = ""


@dataclass(frozen=True)
class SciezkaRatingu:
    id_zespol: int
    punkty: tuple[PunktRatingu, ...]


@dataclass(frozen=True)
class MiejsceRankingu:
    miejsce: int
    liczba: int


@dataclass(frozen=True)
class AnalizaModelu:
    rating_gospodarza: float
    rating_goscia: float
    rating_gospodarza_po: float
    rating_goscia_po: float
    przewaga_parkietu: float
    oczekiwane_gospodarza: float
    oczekiwane_goscia: float
    oczekiwana_roznica: float
    roznica: int
    reszta: float
    klasa: KlasaTrafnosci
    sigma: float | None
    reszty_ligi: tuple[float, ...]
    sciezka_gospodarza: SciezkaRatingu
    sciezka_goscia: SciezkaRatingu
    ranking_gospodarza: MiejsceRankingu | None
    ranking_goscia: MiejsceRankingu | None

    @property
    def zmiana_ratingu(self) -> float:
        return self.rating_gospodarza_po - self.rating_gospodarza

    @property
    def z(self) -> float | None:
        return self.reszta / self.sigma if self.sigma else None

    @property
    def prawdopodobienstwa(self) -> tuple[float, float, float] | None:
        if not self.sigma:
            return None
        gospodarz = 1 - _dystrybuanta((0.5 - self.oczekiwana_roznica) / self.sigma)
        gosc = _dystrybuanta((-0.5 - self.oczekiwana_roznica) / self.sigma)
        return gospodarz, 1 - gospodarz - gosc, gosc

    @property
    def percentyl_zaskoczenia(self) -> float | None:
        if not self.reszty_ligi:
            return None
        mniejsze = sum(1 for r in self.reszty_ligi if abs(r) < abs(self.reszta))
        return mniejsze / len(self.reszty_ligi)


def _dystrybuanta(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


@dataclass(frozen=True)
class TloLigi:
    sumy: tuple[int, ...]
    suma_meczu: int
    wygrane_gospodarzy: int

    @property
    def liczba_meczow(self) -> int:
        return len(self.sumy)

    @property
    def srednia_sumy(self) -> float:
        return statistics.fmean(self.sumy)

    @property
    def percentyl_sumy(self) -> float:
        return sum(1 for s in self.sumy if s < self.suma_meczu) / len(self.sumy)

    @property
    def udzial_wygranych_gospodarzy(self) -> float:
        return self.wygrane_gospodarzy / len(self.sumy)


class AnalizaModeluCalculator:
    MINIMUM_PROBY = 30
    DLUGOSC_SCIEZKI = 20

    def analizuj(self, prognozy: Sequence[PrognozaMeczu], id_mecz: int) -> AnalizaModelu | None:
        indeks = next((i for i, p in enumerate(prognozy) if p.mecz.id_mecz == id_mecz), None)
        if indeks is None:
            return None
        biezaca = prognozy[indeks]
        mecz = biezaca.mecz
        liga = [p for p in prognozy if p.mecz.liga == mecz.liga and p.w_raporcie]
        reszty = tuple(p.aktualizacja.reszta_roznicy for p in liga if p.mecz.id_mecz != id_mecz)
        sigma = statistics.pstdev(reszty) if len(reszty) >= self.MINIMUM_PROBY else None
        dotychczasowe = [
            p
            for p in prognozy[: indeks + 1]
            if p.mecz.liga == mecz.liga and p.mecz.sezon.id_sezon == mecz.sezon.id_sezon
        ]
        ranking = self._ranking(dotychczasowe)
        historia = [p for p in prognozy[: indeks + 1] if p.mecz.liga == mecz.liga]
        return AnalizaModelu(
            rating_gospodarza=biezaca.stan.gospodarz.rating,
            rating_goscia=biezaca.stan.gosc.rating,
            rating_gospodarza_po=biezaca.aktualizacja.rating_gospodarza_po,
            rating_goscia_po=biezaca.aktualizacja.rating_goscia_po,
            przewaga_parkietu=biezaca.parametry.przewaga_wlasnego_parkietu,
            oczekiwane_gospodarza=biezaca.prognoza.bramki_gospodarza,
            oczekiwane_goscia=biezaca.prognoza.bramki_goscia,
            oczekiwana_roznica=biezaca.prognoza.przewidywana_roznica,
            roznica=biezaca.ocena.roznica,
            reszta=biezaca.aktualizacja.reszta_roznicy,
            klasa=biezaca.ocena.klasa,
            sigma=sigma,
            reszty_ligi=reszty if sigma else (),
            sciezka_gospodarza=self._sciezka(historia, mecz.gospodarz.id_zespol, id_mecz),
            sciezka_goscia=self._sciezka(historia, mecz.gosc.id_zespol, id_mecz),
            ranking_gospodarza=ranking.get(mecz.gospodarz.id_zespol),
            ranking_goscia=ranking.get(mecz.gosc.id_zespol),
        )

    def tlo_ligi(self, prognozy: Sequence[PrognozaMeczu], id_mecz: int) -> TloLigi | None:
        biezaca = next((p for p in prognozy if p.mecz.id_mecz == id_mecz), None)
        if biezaca is None:
            return None
        sezon = [
            p.mecz
            for p in prognozy
            if p.mecz.liga == biezaca.mecz.liga
            and p.mecz.sezon.id_sezon == biezaca.mecz.sezon.id_sezon
        ]
        return TloLigi(
            sumy=tuple(m.bramki_gospodarza + m.bramki_goscia for m in sezon),
            suma_meczu=biezaca.mecz.bramki_gospodarza + biezaca.mecz.bramki_goscia,
            wygrane_gospodarzy=sum(1 for m in sezon if m.bramki_gospodarza > m.bramki_goscia),
        )

    def _sciezka(
        self, prognozy: Sequence[PrognozaMeczu], id_zespol: int, id_mecz: int
    ) -> SciezkaRatingu:
        punkty: list[PunktRatingu] = []
        mecze = [p for p in prognozy if p.dotyczy_druzyny(id_zespol)][-self.DLUGOSC_SCIEZKI :]
        for p in mecze:
            gospodarz = p.mecz.gospodarz.id_zespol == id_zespol
            if not punkty:
                przed = p.stan.gospodarz if gospodarz else p.stan.gosc
                punkty.append(
                    PunktRatingu(p.mecz.data, przed.rating, None, False, p.mecz.sezon.nazwa)
                )
            po = (
                p.aktualizacja.rating_gospodarza_po
                if gospodarz
                else p.aktualizacja.rating_goscia_po
            )
            punkty.append(
                PunktRatingu(
                    p.mecz.data,
                    po,
                    p.mecz.id_mecz,
                    p.mecz.id_mecz == id_mecz,
                    p.mecz.sezon.nazwa,
                )
            )
        return SciezkaRatingu(id_zespol, tuple(punkty))

    def _ranking(self, prognozy: Sequence[PrognozaMeczu]) -> dict[int, MiejsceRankingu]:
        ratingi: dict[int, float] = {}
        for p in prognozy:
            ratingi[p.mecz.gospodarz.id_zespol] = p.aktualizacja.rating_gospodarza_po
            ratingi[p.mecz.gosc.id_zespol] = p.aktualizacja.rating_goscia_po
        kolejnosc = sorted(ratingi, key=lambda id_zespol: -ratingi[id_zespol])
        return {
            id_zespol: MiejsceRankingu(miejsce, len(kolejnosc))
            for miejsce, id_zespol in enumerate(kolejnosc, start=1)
        }


@dataclass(frozen=True)
class StrzelecRaportu:
    zawodnik: str
    nr_koszulki: int | None
    pozycja: str | None
    bramki: int
    karne_bramki: int | None
    karne_liczba: int | None
    dwie_minuty: int | None
    udzial: float
    mecze_sezonu: int
    bramki_sezonu: int

    @property
    def srednia_sezonu(self) -> float | None:
        return self.bramki_sezonu / self.mecze_sezonu if self.mecze_sezonu else None

    @property
    def ponad_srednia(self) -> float | None:
        srednia = self.srednia_sezonu
        return self.bramki - srednia if srednia is not None else None

    def prawdopodobienstwo_wystepu(self, minimum_meczow: int) -> float | None:
        srednia = self.srednia_sezonu
        if srednia is None or self.mecze_sezonu < minimum_meczow or self.bramki <= srednia:
            return None
        if srednia <= 0:
            return 0.0
        ponizej = sum(
            math.exp(-srednia) * srednia**k / math.factorial(k) for k in range(self.bramki)
        )
        return max(0.0, 1 - ponizej)


@dataclass(frozen=True)
class AtakDruzyny:
    strzelcy: tuple[StrzelecRaportu, ...]
    bramki_druzyny: int | None
    zawodnicy_bez_bramki: int

    @property
    def suma_indywidualna(self) -> int:
        return sum(s.bramki for s in self.strzelcy)

    @property
    def efektywna_liczba_strzelcow(self) -> float | None:
        kwadraty = sum(s.bramki**2 for s in self.strzelcy)
        return self.suma_indywidualna**2 / kwadraty if kwadraty else None

    @property
    def udzial_trzech(self) -> float | None:
        suma = self.suma_indywidualna
        return sum(s.bramki for s in self.strzelcy[:3]) / suma if suma else None


class AtakDruzynyCalculator:
    def oblicz(
        self,
        sklad: Sequence[ZawodnikMeczu],
        kadra_przed: Sequence[ZawodnikKadry],
        bramki_druzyny: int | None,
    ) -> AtakDruzyny:
        sezon = {z.id_zawodnik: z for z in kadra_przed}
        suma = sum(z.bramki or 0 for z in sklad)
        strzelcy = [
            self._strzelec(z, sezon.get(z.id_zawodnik) if z.id_zawodnik else None, suma)
            for z in sklad
            if (z.bramki or 0) > 0
        ]
        strzelcy.sort(key=lambda s: (-s.bramki, s.zawodnik.casefold()))
        return AtakDruzyny(
            strzelcy=tuple(strzelcy),
            bramki_druzyny=bramki_druzyny,
            zawodnicy_bez_bramki=sum(1 for z in sklad if z.bramki == 0) if suma else 0,
        )

    def _strzelec(
        self, zawodnik: ZawodnikMeczu, sezon: ZawodnikKadry | None, suma: int
    ) -> StrzelecRaportu:
        bramki = zawodnik.bramki or 0
        return StrzelecRaportu(
            zawodnik=(zawodnik.zawodnik or "—").strip(),
            nr_koszulki=zawodnik.nr_koszulki,
            pozycja=zawodnik.pozycja,
            bramki=bramki,
            karne_bramki=zawodnik.karne_bramki,
            karne_liczba=zawodnik.karne_liczba,
            dwie_minuty=zawodnik.dwie_minuty,
            udzial=bramki / suma if suma else 0.0,
            mecze_sezonu=sezon.mecze if sezon else 0,
            bramki_sezonu=sezon.bramki if sezon else 0,
        )


@dataclass(frozen=True)
class TloSezonuDruzyny:
    zdobyte_sezonu: tuple[int, ...]
    stracone_sezonu: tuple[int, ...]
    bramki_meczu: int | None
    stracone_meczu: int | None

    @property
    def mecze(self) -> int:
        return len(self.zdobyte_sezonu)

    @property
    def srednia_zdobytych(self) -> float | None:
        return statistics.fmean(self.zdobyte_sezonu) if self.zdobyte_sezonu else None

    @property
    def srednia_straconych(self) -> float | None:
        return statistics.fmean(self.stracone_sezonu) if self.stracone_sezonu else None

    @property
    def percentyl_zdobytych(self) -> float | None:
        return _percentyl(self.zdobyte_sezonu, self.bramki_meczu)

    @property
    def percentyl_straconych(self) -> float | None:
        return _percentyl(self.stracone_sezonu, self.stracone_meczu)

    @property
    def roznica_zdobytych(self) -> float | None:
        if self.srednia_zdobytych is None or self.bramki_meczu is None:
            return None
        return self.bramki_meczu - self.srednia_zdobytych

    @property
    def roznica_straconych(self) -> float | None:
        if self.srednia_straconych is None or self.stracone_meczu is None:
            return None
        return self.stracone_meczu - self.srednia_straconych


def _percentyl(proba: Sequence[int], wartosc: int | None) -> float | None:
    if not proba or wartosc is None:
        return None
    mniejsze = sum(1 for x in proba if x < wartosc)
    rowne = sum(1 for x in proba if x == wartosc)
    return (mniejsze + rowne / 2) / len(proba)


class TloSezonuCalculator:
    def oblicz(
        self,
        wystepy: Sequence[WystepZapowiedzi],
        mecz: MeczZapowiedzi,
        zdobyte: int | None,
        stracone: int | None,
    ) -> TloSezonuDruzyny:
        sezon = [
            w
            for w in wystepy
            if w.id_sezon == mecz.id_sezon
            and w.id_rozgrywki == mecz.id_rozgrywki
            and w.id_mecz != mecz.id_mecz
        ]
        return TloSezonuDruzyny(
            zdobyte_sezonu=tuple(w.bramki_zdobyte for w in sezon),
            stracone_sezonu=tuple(w.bramki_stracone for w in sezon),
            bramki_meczu=zdobyte,
            stracone_meczu=stracone,
        )


@dataclass(frozen=True)
class RaportMeczu:
    statystyki: StatystykiMeczu
    mecz: MeczZapowiedzi
    model: AnalizaModelu | None
    nazwa_modelu: str
    liga: TloLigi | None
    atak_gospodarza: AtakDruzyny
    atak_goscia: AtakDruzyny
    tlo_gospodarza: TloSezonuDruzyny | None
    tlo_goscia: TloSezonuDruzyny | None
    widzowie: int | None
    bezposrednie: BezposrednieMecze | None = None
