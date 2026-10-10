from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from handball.domain.attendance_aggregate import AgregatFrekwencji
from handball.domain.attendance_formatting import formatuj_roznice

LIMIT_PRZECIWNIKOW = 100
UWAGA_O_WYBORZE_GOSPODARZA = (
    "Ranking przeciwników wymaga wybrania klubu w filtrze „Gospodarz”: "
    "pokazuje frekwencję na meczach tego klubu u siebie według rywala."
)


@dataclass(frozen=True)
class PrzeciwnikFrekwencji(AgregatFrekwencji):
    id_zespol: int
    nazwa: str


@dataclass(frozen=True)
class WierszPrzeciwnika:
    pozycja: int
    przeciwnik: PrzeciwnikFrekwencji
    roznica: float | None

    @property
    def roznica_etykieta(self) -> str:
        return formatuj_roznice(self.roznica)


@dataclass(frozen=True)
class RankingPrzeciwnikow:
    aktywny: bool
    srednia_gospodarza: float | None
    wiersze: tuple[WierszPrzeciwnika, ...]

    @property
    def uwaga(self) -> str | None:
        if self.aktywny:
            return None
        return UWAGA_O_WYBORZE_GOSPODARZA


class PrzeciwnicyFrekwencjiCalculator:
    def nieaktywny(self) -> RankingPrzeciwnikow:
        return RankingPrzeciwnikow(aktywny=False, srednia_gospodarza=None, wiersze=())

    def uloz(
        self,
        przeciwnicy: Sequence[PrzeciwnikFrekwencji],
        srednia_gospodarza: float | None,
        limit: int = LIMIT_PRZECIWNIKOW,
    ) -> RankingPrzeciwnikow:
        kwalifikujacy = sorted(
            (przeciwnik for przeciwnik in przeciwnicy if przeciwnik.srednia is not None),
            key=lambda przeciwnik: (
                -(przeciwnik.srednia or 0.0),
                -przeciwnik.znane,
                przeciwnik.nazwa.casefold(),
                przeciwnik.id_zespol,
            ),
        )
        wiersze = tuple(
            WierszPrzeciwnika(
                pozycja=pozycja,
                przeciwnik=przeciwnik,
                roznica=self._roznica(przeciwnik.srednia, srednia_gospodarza),
            )
            for pozycja, przeciwnik in enumerate(kwalifikujacy[:limit], start=1)
        )
        return RankingPrzeciwnikow(
            aktywny=True, srednia_gospodarza=srednia_gospodarza, wiersze=wiersze
        )

    @staticmethod
    def _roznica(srednia: float | None, srednia_gospodarza: float | None) -> float | None:
        if srednia is None or srednia_gospodarza is None:
            return None
        return srednia - srednia_gospodarza
