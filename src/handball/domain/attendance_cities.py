from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import chain

from handball.domain.attendance_aggregate import (
    AgregatFrekwencji,
    MiaryRozkladu,
    polacz_agregaty,
)
from handball.domain.attendance_city_breakdowns import (
    LIMIT_HAL_MIAST,
    LIMIT_HAL_NA_MIASTO,
    LIMIT_ROZGRYWEK_MIAST,
    LIMIT_ROZGRYWEK_NA_MIASTO,
    LIMIT_SEZONOW_MIAST,
    HalaMiasta,
    RozgrywkiMiasta,
    SezonMiasta,
    porzadek_hal,
    porzadek_rozgrywek,
    porzadek_sezonow,
    przydziel_do_miast,
)
from handball.domain.attendance_city_names import klucz_miasta, najczestsza_pisownia
from handball.domain.attendance_formatting import formatuj_calkowita

LIMIT_MIAST = 100
LIMIT_WKLADOW_MIAST = 300
UWAGA_O_ZRODLE_MIASTA = (
    "Miasto pochodzi wyłącznie z sezonowej karty klubu gospodarza (zespoly_sezony.miasto), "
    "nie z hali. Mecze klubów bez wpisanego miasta nie wchodzą do rankingu miast. "
    "Pisownia miasta jest porównywana bez względu na wielkość liter i nadmiarowe spacje."
)
UWAGA_O_HALACH_MIASTA = (
    "Hale to obiekty, w których rozegrano mecze u siebie klubów z danego miasta; "
    "przypisanie do miasta nadal wynika z klubu gospodarza, nie z miasta hali."
)


@dataclass(frozen=True)
class MiastoFrekwencji(AgregatFrekwencji):
    miasto: str
    liczba_klubow: int
    liczba_rozgrywek: int
    rozklad: MiaryRozkladu = field(default_factory=MiaryRozkladu)

    @property
    def klucz(self) -> str:
        return klucz_miasta(self.miasto)

    @property
    def liczba_klubow_etykieta(self) -> str:
        return formatuj_calkowita(self.liczba_klubow)

    @property
    def liczba_rozgrywek_etykieta(self) -> str:
        return formatuj_calkowita(self.liczba_rozgrywek)


@dataclass(frozen=True)
class WkladMiasta:
    miasto: str
    id_zespol: int
    klub: str
    rozgrywki: str
    agregat: AgregatFrekwencji


@dataclass(frozen=True)
class DaneMiast:
    miasta: tuple[MiastoFrekwencji, ...]
    wklady: tuple[WkladMiasta, ...]
    mecze_bez_miasta: int
    sezony: tuple[SezonMiasta, ...] = ()
    rozgrywki: tuple[RozgrywkiMiasta, ...] = ()
    hale: tuple[HalaMiasta, ...] = ()


@dataclass(frozen=True)
class LimityRozbiciaMiast:
    sezony: int = LIMIT_SEZONOW_MIAST
    rozgrywki: int = LIMIT_ROZGRYWEK_MIAST
    rozgrywki_na_miasto: int = LIMIT_ROZGRYWEK_NA_MIASTO
    hale: int = LIMIT_HAL_MIAST
    hale_na_miasto: int = LIMIT_HAL_NA_MIASTO


@dataclass(frozen=True)
class WierszMiasta:
    pozycja: int
    miasto: MiastoFrekwencji
    wklady: tuple[WkladMiasta, ...]
    sezony: tuple[SezonMiasta, ...] = ()
    wg_rozgrywek: tuple[RozgrywkiMiasta, ...] = ()
    hale: tuple[HalaMiasta, ...] = ()


@dataclass(frozen=True)
class RaportMiast:
    ranking: tuple[WierszMiasta, ...]
    mecze_bez_miasta: int
    uwaga: str = UWAGA_O_ZRODLE_MIASTA
    uwaga_o_halach: str = UWAGA_O_HALACH_MIASTA

    @property
    def wklady(self) -> tuple[WkladMiasta, ...]:
        return tuple(chain.from_iterable(wiersz.wklady for wiersz in self.ranking))

    @property
    def sezony(self) -> tuple[SezonMiasta, ...]:
        return tuple(chain.from_iterable(wiersz.sezony for wiersz in self.ranking))

    @property
    def wg_rozgrywek(self) -> tuple[RozgrywkiMiasta, ...]:
        return tuple(chain.from_iterable(wiersz.wg_rozgrywek for wiersz in self.ranking))

    @property
    def hale(self) -> tuple[HalaMiasta, ...]:
        return tuple(chain.from_iterable(wiersz.hale for wiersz in self.ranking))

    @property
    def rozgrywki(self) -> tuple[str, ...]:
        return tuple(sorted({wklad.rozgrywki for wklad in self.wklady}, key=str.casefold))

    @property
    def ma_dane(self) -> bool:
        return bool(self.ranking)

    @property
    def mecze_bez_miasta_etykieta(self) -> str:
        return formatuj_calkowita(self.mecze_bez_miasta)

    @property
    def uwaga_o_brakach(self) -> str | None:
        if not self.mecze_bez_miasta:
            return None
        return (
            f"{self.mecze_bez_miasta_etykieta} rozegranych meczów pominięto, "
            "bo klub gospodarza nie ma wpisanego miasta."
        )


def porzadek_wkladow(wklad: WkladMiasta) -> tuple[int, str, str, int]:
    return (
        -wklad.agregat.suma,
        wklad.klub.casefold(),
        wklad.rozgrywki.casefold(),
        wklad.id_zespol,
    )


class MiastaMerger:
    def scal(self, miasta: Iterable[MiastoFrekwencji]) -> tuple[MiastoFrekwencji, ...]:
        grupy: dict[str, list[MiastoFrekwencji]] = {}
        for miasto in miasta:
            if miasto.klucz:
                grupy.setdefault(miasto.klucz, []).append(miasto)
        return tuple(self._scal_grupe(grupa) for grupa in grupy.values())

    @staticmethod
    def _scal_grupe(grupa: list[MiastoFrekwencji]) -> MiastoFrekwencji:
        if len(grupa) == 1:
            return grupa[0]
        agregat = polacz_agregaty(grupa)
        minima = [m.rozklad.minimum for m in grupa if m.rozklad.minimum is not None]
        return MiastoFrekwencji(
            rozegrane=agregat.rozegrane,
            znane=agregat.znane,
            suma=agregat.suma,
            maksimum=agregat.maksimum,
            miasto=najczestsza_pisownia((m.miasto, m.rozegrane) for m in grupa),
            liczba_klubow=max(m.liczba_klubow for m in grupa),
            liczba_rozgrywek=max(m.liczba_rozgrywek for m in grupa),
            rozklad=MiaryRozkladu(minimum=min(minima) if minima else None),
        )


class MiastaFrekwencjiCalculator:
    def __init__(self, merger: MiastaMerger | None = None) -> None:
        self._merger = merger or MiastaMerger()

    def zbuduj(
        self,
        dane: DaneMiast,
        limit_miast: int = LIMIT_MIAST,
        limit_wkladow: int = LIMIT_WKLADOW_MIAST,
        limity_rozbicia: LimityRozbiciaMiast | None = None,
    ) -> RaportMiast:
        limity = limity_rozbicia or LimityRozbiciaMiast()
        miasta = self._uloz_miasta(self._merger.scal(dane.miasta), limit_miast)
        klucze = tuple(miasto.klucz for miasto in miasta)
        wklady = przydziel_do_miast(
            dane.wklady, klucze, lambda w: w.miasto, porzadek_wkladow, limit_wkladow
        )
        sezony = przydziel_do_miast(
            dane.sezony, klucze, lambda w: w.klucz, porzadek_sezonow, limity.sezony
        )
        rozgrywki = przydziel_do_miast(
            dane.rozgrywki,
            klucze,
            lambda w: w.klucz,
            porzadek_rozgrywek,
            limity.rozgrywki,
            limity.rozgrywki_na_miasto,
        )
        hale = przydziel_do_miast(
            dane.hale,
            klucze,
            lambda w: w.klucz,
            porzadek_hal,
            limity.hale,
            limity.hale_na_miasto,
        )
        wiersze = tuple(
            WierszMiasta(
                pozycja=pozycja,
                miasto=miasto,
                wklady=wklady[miasto.klucz],
                sezony=sezony[miasto.klucz],
                wg_rozgrywek=rozgrywki[miasto.klucz],
                hale=hale[miasto.klucz],
            )
            for pozycja, miasto in enumerate(miasta, start=1)
        )
        return RaportMiast(
            ranking=wiersze,
            mecze_bez_miasta=dane.mecze_bez_miasta + self._rozegrane_bez_miasta(dane.miasta),
        )

    @staticmethod
    def _uloz_miasta(
        miasta: Iterable[MiastoFrekwencji], limit: int
    ) -> tuple[MiastoFrekwencji, ...]:
        kwalifikujace = sorted(
            (miasto for miasto in miasta if miasto.znane > 0),
            key=lambda miasto: (
                -miasto.suma,
                -(miasto.srednia or 0.0),
                miasto.miasto.casefold(),
            ),
        )
        return tuple(kwalifikujace[:limit])

    @staticmethod
    def _rozegrane_bez_miasta(miasta: Iterable[MiastoFrekwencji]) -> int:
        return sum(miasto.rozegrane for miasto in miasta if not miasto.klucz)
