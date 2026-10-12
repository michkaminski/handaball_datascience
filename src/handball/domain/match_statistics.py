from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from handball.domain.match_rules import MeczPolicy
from handball.domain.matches import DaneMeczu, SzczegolyMeczu, ZawodnikMeczu


class RezultatFormy(StrEnum):
    WYGRANA = "W"
    REMIS = "R"
    PORAZKA = "P"


@dataclass(frozen=True)
class MeczFormy:
    id_mecz: int
    data: datetime | None
    rywal: str | None
    u_siebie: bool
    bramki_zdobyte: int
    bramki_stracone: int
    seria_zdobyte: int | None = None
    seria_stracone: int | None = None
    dogrywka_zdobyte: int | None = None
    dogrywka_stracone: int | None = None
    rozgrywki: str | None = None

    @property
    def roznica(self) -> int:
        return self.bramki_zdobyte - self.bramki_stracone

    @property
    def remis_regulaminowy(self) -> bool:
        return self.bramki_zdobyte == self.bramki_stracone

    @property
    def seria_karnych(self) -> bool:
        return self.seria_zdobyte is not None and self.seria_stracone is not None

    @property
    def dogrywka(self) -> bool:
        return self.dogrywka_zdobyte is not None and self.dogrywka_stracone is not None

    @property
    def rezultat(self) -> RezultatFormy:
        return _rezultat(self.bramki_zdobyte, self.bramki_stracone)

    @property
    def rozstrzygniecie(self) -> RezultatFormy | None:
        if not self.remis_regulaminowy:
            return None
        if self.dogrywka and self.dogrywka_zdobyte != self.dogrywka_stracone:
            return _rezultat(self.dogrywka_zdobyte or 0, self.dogrywka_stracone or 0)
        if self.seria_karnych and self.seria_zdobyte != self.seria_stracone:
            return _rezultat(self.seria_zdobyte or 0, self.seria_stracone or 0)
        return None


def _rezultat(zdobyte: int, stracone: int) -> RezultatFormy:
    if zdobyte > stracone:
        return RezultatFormy.WYGRANA
    if zdobyte < stracone:
        return RezultatFormy.PORAZKA
    return RezultatFormy.REMIS


@dataclass(frozen=True)
class FormaDruzyny:
    id_zespol: int | None
    mecze: tuple[MeczFormy, ...]
    id_analizowany: int

    def ostatnie(self, limit: int) -> tuple[MeczFormy, ...]:
        return self.mecze[-limit:] if limit > 0 else ()

    def bilans(self, limit: int) -> dict[RezultatFormy, int]:
        wynik = dict.fromkeys(RezultatFormy, 0)
        for mecz in self.ostatnie(limit):
            wynik[mecz.rezultat] += 1
        return wynik


@dataclass(frozen=True)
class StrzelecMeczu:
    zawodnik: str
    bramki: int
    karne_bramki: int | None


@dataclass(frozen=True)
class StatystykiDruzynyMeczu:
    nazwa: str | None
    id_zespol: int | None
    bramki: int | None
    bramki_do_przerwy: int | None
    karne_trafione: int | None
    karne_wykonane: int | None
    timeouty: tuple[str, ...] | None
    dwie_minuty: int | None
    upomnienia: int | None
    dyskwalifikacje: int | None
    strzelcy: tuple[StrzelecMeczu, ...]

    @property
    def bramki_druga_polowa(self) -> int | None:
        if self.bramki is None or self.bramki_do_przerwy is None:
            return None
        return self.bramki - self.bramki_do_przerwy

    @property
    def skutecznosc_karnych(self) -> float | None:
        if self.karne_trafione is None or not self.karne_wykonane:
            return None
        return self.karne_trafione / self.karne_wykonane


@dataclass(frozen=True)
class StatystykiMeczu:
    szczegoly: SzczegolyMeczu
    gospodarz: StatystykiDruzynyMeczu
    gosc: StatystykiDruzynyMeczu
    seria_gospodarz: int | None
    seria_gosc: int | None
    dogrywka_gospodarz: int | None
    dogrywka_gosc: int | None
    wnioski: tuple[str, ...]
    forma_gospodarza: FormaDruzyny | None
    forma_goscia: FormaDruzyny | None

    @property
    def rozegrany(self) -> bool:
        return self.gospodarz.bramki is not None and self.gosc.bramki is not None


class StatystykiMeczuCalculator:
    LIMIT_STRZELCOW = 5

    def __init__(self, reguly: MeczPolicy) -> None:
        self._reguly = reguly

    def oblicz(
        self,
        szczegoly: SzczegolyMeczu,
        forma_gospodarza: FormaDruzyny | None = None,
        forma_goscia: FormaDruzyny | None = None,
    ) -> StatystykiMeczu:
        mecz = szczegoly.mecz
        para = self._reguly.para
        nazwy = para(mecz, szczegoly.nazwa_gospodarz, szczegoly.nazwa_gosc)
        identyfikatory = para(mecz, mecz.id_zespol_gosp, mecz.id_zespol_gosc)
        bramki = para(mecz, mecz.wynik_gosp_full, mecz.wynik_gosc_full)
        polowa = para(mecz, mecz.wynik_gosp_pol, mecz.wynik_gosc_pol)
        karne_trafione = para(mecz, mecz.karne_bramki_gosp, mecz.karne_bramki_gosc)
        karne_wykonane = para(mecz, mecz.karne_ile_gosp, mecz.karne_ile_gosc)
        timeouty = self._timeouty(mecz)
        sklady = (szczegoly.sklad_gospodarz, szczegoly.sklad_gosc)
        druzyny = [
            self._druzyna(
                nazwy[i],
                identyfikatory[i],
                bramki[i],
                polowa[i],
                karne_trafione[i],
                karne_wykonane[i],
                timeouty[i] if timeouty else None,
                sklady[i],
            )
            for i in (0, 1)
        ]
        seria = para(mecz, mecz.dogrywka_karne_gosp, mecz.dogrywka_karne_gosc)
        dogrywka = self._dogrywka(mecz)
        wynik = StatystykiMeczu(
            szczegoly,
            druzyny[0],
            druzyny[1],
            seria[0],
            seria[1],
            dogrywka[0],
            dogrywka[1],
            (),
            forma_gospodarza,
            forma_goscia,
        )
        return replace(wynik, wnioski=WnioskiMeczuGenerator().wnioski(wynik))

    def _druzyna(
        self,
        nazwa: str | None,
        id_zespol: int | None,
        bramki: int | None,
        do_przerwy: int | None,
        karne_trafione: int | None,
        karne_wykonane: int | None,
        timeouty: tuple[str, ...] | None,
        sklad: Sequence[ZawodnikMeczu],
    ) -> StatystykiDruzynyMeczu:
        indywidualne = sum(z.bramki or 0 for z in sklad) > 0
        if karne_wykonane is None and indywidualne:
            znane = [z for z in sklad if z.karne_liczba is not None]
            if znane:
                karne_wykonane = sum(z.karne_liczba or 0 for z in znane)
                karne_trafione = sum(z.karne_bramki or 0 for z in znane)
        strzelcy = sorted(
            (
                StrzelecMeczu(z.zawodnik or "—", z.bramki or 0, z.karne_bramki)
                for z in sklad
                if indywidualne and (z.bramki or 0) > 0
            ),
            key=lambda s: (-s.bramki, s.zawodnik.casefold()),
        )
        return StatystykiDruzynyMeczu(
            nazwa=nazwa.strip() if nazwa else nazwa,
            id_zespol=id_zespol,
            bramki=bramki,
            bramki_do_przerwy=do_przerwy,
            karne_trafione=karne_trafione if karne_wykonane is not None else None,
            karne_wykonane=karne_wykonane,
            timeouty=timeouty,
            dwie_minuty=self._suma(sklad, "dwie_minuty") if indywidualne else None,
            upomnienia=self._suma(sklad, "upomnienie") if indywidualne else None,
            dyskwalifikacje=self._suma(sklad, "dyskwalifikacja") if indywidualne else None,
            strzelcy=tuple(strzelcy[: self.LIMIT_STRZELCOW]),
        )

    def _suma(self, sklad: Sequence[ZawodnikMeczu], pole: str) -> int | None:
        wartosci = [getattr(z, pole) for z in sklad if getattr(z, pole) is not None]
        return sum(int(w) for w in wartosci) if wartosci else None

    def _timeouty(self, mecz: DaneMeczu) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
        gosp = tuple(t for t in (mecz.timeout1_gosp, mecz.timeout2_gosp, mecz.timeout3_gosp) if t)
        gosc = tuple(t for t in (mecz.timeout1_gosc, mecz.timeout2_gosc, mecz.timeout3_gosc) if t)
        if not gosp and not gosc:
            return None
        return self._reguly.para(mecz, gosp, gosc)

    def _dogrywka(self, mecz: DaneMeczu) -> tuple[int | None, int | None]:
        if mecz.dogrywka_2_full_gosp is not None and mecz.dogrywka_2_full_gosc is not None:
            return self._reguly.para(mecz, mecz.dogrywka_2_full_gosp, mecz.dogrywka_2_full_gosc)
        return self._reguly.para(mecz, mecz.dogrywka_1_full_gosp, mecz.dogrywka_1_full_gosc)


class WnioskiMeczuGenerator:
    LIMIT = 3

    def wnioski(self, statystyki: StatystykiMeczu) -> tuple[str, ...]:
        if not statystyki.rozegrany:
            return ()
        kandydaci = [
            self._rozstrzygniecie(statystyki),
            self._przebieg(statystyki),
            self._strzelec(statystyki),
            self._karne(statystyki),
            self._kary(statystyki),
        ]
        return tuple(w for w in kandydaci if w)[: self.LIMIT]

    def _rozstrzygniecie(self, s: StatystykiMeczu) -> str | None:
        if s.gospodarz.bramki != s.gosc.bramki:
            return None
        if s.dogrywka_gospodarz is not None and s.dogrywka_gosc is not None:
            if s.dogrywka_gospodarz != s.dogrywka_gosc:
                zwyciezca = s.gospodarz if s.dogrywka_gospodarz > s.dogrywka_gosc else s.gosc
                return (
                    f"Po 60 minutach remis {s.gospodarz.bramki}:{s.gosc.bramki}; "
                    f"dogrywkę ({s.dogrywka_gospodarz}:{s.dogrywka_gosc}) wygrała drużyna "
                    f"{zwyciezca.nazwa}."
                )
        if s.seria_gospodarz is not None and s.seria_gosc is not None:
            if s.seria_gospodarz != s.seria_gosc:
                zwyciezca = s.gospodarz if s.seria_gospodarz > s.seria_gosc else s.gosc
                return (
                    f"Po 60 minutach remis {s.gospodarz.bramki}:{s.gosc.bramki}; "
                    f"serię rzutów karnych {s.seria_gospodarz}:{s.seria_gosc} wygrała drużyna "
                    f"{zwyciezca.nazwa}."
                )
        return f"Mecz zakończył się remisem {s.gospodarz.bramki}:{s.gosc.bramki}."

    def _przebieg(self, s: StatystykiMeczu) -> str | None:
        a, b = s.gospodarz, s.gosc
        if a.bramki_do_przerwy is None or b.bramki_do_przerwy is None:
            return None
        if a.bramki is None or b.bramki is None:
            return None
        przerwa = a.bramki_do_przerwy - b.bramki_do_przerwy
        koniec = a.bramki - b.bramki
        druga_a, druga_b = a.bramki_druga_polowa, b.bramki_druga_polowa
        if przerwa * koniec < 0 or (przerwa != 0 and koniec == 0):
            goniacy = b if przerwa > 0 else a
            return (
                f"Drużyna {goniacy.nazwa} odrobiła stratę {abs(przerwa)} "
                f"{'bramki' if abs(przerwa) == 1 else 'bramek'} z przerwy "
                f"({a.bramki_do_przerwy}:{b.bramki_do_przerwy}); "
                f"druga połowa {druga_a}:{druga_b}."
            )
        if druga_a is None or druga_b is None or druga_a == druga_b:
            return None
        lepsza = a if druga_a > druga_b else b
        return (
            f"Do przerwy {a.bramki_do_przerwy}:{b.bramki_do_przerwy}, druga połowa "
            f"{druga_a}:{druga_b} — lepiej w niej grała drużyna {lepsza.nazwa}."
        )

    def _strzelec(self, s: StatystykiMeczu) -> str | None:
        najlepsi = [
            (strzelec, druzyna)
            for druzyna in (s.gospodarz, s.gosc)
            for strzelec in druzyna.strzelcy[:1]
        ]
        if not najlepsi:
            return None
        strzelec, druzyna = max(najlepsi, key=lambda p: p[0].bramki)
        if sum(1 for p in najlepsi if p[0].bramki == strzelec.bramki) > 1:
            return None
        udzial = (
            f" ({strzelec.bramki / druzyna.bramki:.0%} bramek drużyny)" if druzyna.bramki else ""
        )
        return (
            f"Najlepszy strzelec meczu: {strzelec.zawodnik} ({druzyna.nazwa}) — "
            f"{strzelec.bramki} {self._bramki_slowo(strzelec.bramki)}{udzial}."
        )

    def _karne(self, s: StatystykiMeczu) -> str | None:
        a, b = s.gospodarz, s.gosc
        if not a.karne_wykonane or not b.karne_wykonane:
            return None
        if a.karne_trafione is None or b.karne_trafione is None:
            return None
        return (
            f"Rzuty karne: {a.nazwa} {a.karne_trafione}/{a.karne_wykonane}, "
            f"{b.nazwa} {b.karne_trafione}/{b.karne_wykonane}."
        )

    def _kary(self, s: StatystykiMeczu) -> str | None:
        a, b = s.gospodarz.dwie_minuty, s.gosc.dwie_minuty
        if a is None or b is None or abs(a - b) < 2:
            return None
        wiecej = s.gospodarz if a > b else s.gosc
        return f"Więcej kar 2 min miała drużyna {wiecej.nazwa} ({max(a, b)} wobec {min(a, b)})."

    @staticmethod
    def _bramki_slowo(liczba: int) -> str:
        if liczba == 1:
            return "bramka"
        if liczba % 10 in (2, 3, 4) and liczba % 100 not in (12, 13, 14):
            return "bramki"
        return "bramek"
