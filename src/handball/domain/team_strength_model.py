from __future__ import annotations

import math
from collections import deque

from handball.domain.match_predictions import (
    AktualizacjaEwma,
    AktualizacjaRatingu,
    KonfiguracjaSilyDruzyn,
    MeczDoPrognozy,
    MeczPrzyszly,
    PrognozaPunktowa,
    RatingPrzedMeczem,
    RegresjaSezonowa,
    SezonPrognoz,
    StanPrzedMeczem,
    Typ1X2,
)


class RownaniaSilyDruzyn:
    def __init__(self, konfiguracja: KonfiguracjaSilyDruzyn) -> None:
        self._k = konfiguracja

    def roznica_ratingow(self, rating_gospodarza: float, rating_goscia: float) -> float:
        return rating_gospodarza - rating_goscia + self._k.przewaga_wlasnego_parkietu

    def przewidywana_roznica(self, roznica_ratingow: float) -> float:
        return self._k.wyraz_wolny_roznicy + self._k.nachylenie_roznicy * roznica_ratingow

    def przewidywane_bramki(self, suma: float, roznica: float) -> tuple[float, float]:
        return ((suma + roznica) / 2, (suma - roznica) / 2)

    def typ(self, przewidywana_roznica: float) -> Typ1X2:
        if przewidywana_roznica > self._k.prog_remisu:
            return Typ1X2.GOSPODARZ
        if przewidywana_roznica < -self._k.prog_remisu:
            return Typ1X2.GOSC
        return Typ1X2.REMIS

    def poprawka_ratingu(self, reszta_roznicy: float) -> float:
        return self._k.wspolczynnik_k * math.tanh(reszta_roznicy / self._k.skala_roznicy)

    def regresja(self, rating: float) -> float:
        poczatkowy = self._k.rating_poczatkowy
        return poczatkowy + self._k.zachowanie_miedzy_sezonami * (rating - poczatkowy)

    def ewma(self, stan: float, suma_bramek: float) -> float:
        return self._k.alfa_ewma * suma_bramek + (1 - self._k.alfa_ewma) * stan


class ModelSilyDruzyn:
    DLUGOSC_HISTORII_EWMA = 5

    def __init__(
        self, konfiguracja: KonfiguracjaSilyDruzyn, rownania: RownaniaSilyDruzyn | None = None
    ) -> None:
        self._konfiguracja = konfiguracja
        self._rownania = rownania or RownaniaSilyDruzyn(konfiguracja)
        self._ratingi: dict[int, float] = {}
        self._regresje: dict[int, RegresjaSezonowa] = {}
        self._sezon: SezonPrognoz | None = None
        self._suma_ewma = konfiguracja.poczatkowa_suma_bramek
        self._historia_ewma: deque[AktualizacjaEwma] = deque(maxlen=self.DLUGOSC_HISTORII_EWMA)
        self._stan_oczekujacy: tuple[int, StanPrzedMeczem] | None = None

    @property
    def konfiguracja(self) -> KonfiguracjaSilyDruzyn:
        return self._konfiguracja

    def rating(self, id_zespol: int) -> float | None:
        return self._ratingi.get(id_zespol)

    def stan_przed_meczem(self, mecz: MeczDoPrognozy | MeczPrzyszly) -> StanPrzedMeczem:
        self._przejdz_do_sezonu(mecz.sezon)
        stan = StanPrzedMeczem(
            gospodarz=self._rating_przed_meczem(mecz.gospodarz.id_zespol),
            gosc=self._rating_przed_meczem(mecz.gosc.id_zespol),
            oczekiwana_suma_ligi=self._suma_ewma,
            ostatnie_aktualizacje_ewma=tuple(self._historia_ewma),
        )
        self._stan_oczekujacy = (mecz.id_mecz, stan)
        return stan

    def prognozuj(self, stan: StanPrzedMeczem) -> PrognozaPunktowa:
        roznica_ratingow = self._rownania.roznica_ratingow(stan.gospodarz.rating, stan.gosc.rating)
        roznica = self._rownania.przewidywana_roznica(roznica_ratingow)
        bramki_gospodarza, bramki_goscia = self._rownania.przewidywane_bramki(
            stan.oczekiwana_suma_ligi, roznica
        )
        return PrognozaPunktowa(
            roznica_ratingow=roznica_ratingow,
            przewidywana_roznica=roznica,
            przewidywana_suma=stan.oczekiwana_suma_ligi,
            bramki_gospodarza=bramki_gospodarza,
            bramki_goscia=bramki_goscia,
            typ=self._rownania.typ(roznica),
        )

    def aktualizuj(self, mecz: MeczDoPrognozy, prognoza: PrognozaPunktowa) -> AktualizacjaRatingu:
        if self._stan_oczekujacy is None or self._stan_oczekujacy[0] != mecz.id_mecz:
            raise ValueError("Aktualizacja wymaga wcześniejszego odczytu stanu i prognozy meczu.")
        stan = self._stan_oczekujacy[1]
        self._stan_oczekujacy = None
        reszta = (mecz.bramki_gospodarza - mecz.bramki_goscia) - prognoza.przewidywana_roznica
        poprawka = self._rownania.poprawka_ratingu(reszta)
        rating_gospodarza = stan.gospodarz.rating + poprawka
        rating_goscia = stan.gosc.rating - poprawka
        self._ratingi[mecz.gospodarz.id_zespol] = rating_gospodarza
        self._ratingi[mecz.gosc.id_zespol] = rating_goscia
        self._regresje.pop(mecz.gospodarz.id_zespol, None)
        self._regresje.pop(mecz.gosc.id_zespol, None)
        suma = mecz.bramki_gospodarza + mecz.bramki_goscia
        suma_po = self._rownania.ewma(self._suma_ewma, suma)
        self._historia_ewma.append(
            AktualizacjaEwma(
                mecz.id_mecz, self._suma_ewma, suma, self._konfiguracja.alfa_ewma, suma_po
            )
        )
        self._suma_ewma = suma_po
        return AktualizacjaRatingu(reszta, poprawka, rating_gospodarza, rating_goscia, suma_po)

    def _rating_przed_meczem(self, id_zespol: int) -> RatingPrzedMeczem:
        rating = self._ratingi.get(id_zespol)
        if rating is None:
            return RatingPrzedMeczem(self._konfiguracja.rating_poczatkowy, True, None)
        return RatingPrzedMeczem(rating, False, self._regresje.get(id_zespol))

    def _przejdz_do_sezonu(self, sezon: SezonPrognoz) -> None:
        if self._sezon is None:
            self._sezon = sezon
            return
        if sezon.klucz <= self._sezon.klucz:
            return
        for id_zespol, rating in self._ratingi.items():
            po_regresji = self._rownania.regresja(rating)
            poprzednia = self._regresje.get(id_zespol)
            self._regresje[id_zespol] = RegresjaSezonowa(
                poprzednia.rating_konca_sezonu if poprzednia else rating,
                po_regresji,
                poprzednia.sezon_poprzedni if poprzednia else self._sezon.nazwa,
                poprzednia.liczba_regresji + 1 if poprzednia else 1,
            )
            self._ratingi[id_zespol] = po_regresji
        self._sezon = sezon
