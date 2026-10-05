from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from handball.domain.match_preview import (
    CzlonekKadry,
    KadraDruzyny,
    MeczZapowiedzi,
    OpcjeZapowiedzi,
)


class KolejnoscProtokolu(StrEnum):
    POZYCJE = "pozycje"
    NUMERY = "numery"


@dataclass(frozen=True)
class SedziaProtokolu:
    rola: str
    nazwisko: str | None
    miasto: str | None


@dataclass(frozen=True)
class HalaProtokolu:
    nazwa: str | None
    miasto: str | None
    ulica: str | None
    numer: str | None
    pojemnosc: int | None


@dataclass(frozen=True)
class DaneProtokolu:
    hala: HalaProtokolu | None
    sedziowie: tuple[SedziaProtokolu, ...] = ()

    def sedzia(self, rola: str) -> SedziaProtokolu | None:
        return next((s for s in self.sedziowie if s.rola == rola), None)


@dataclass(frozen=True)
class ProtokolMeczu:
    mecz: MeczZapowiedzi
    stan_na: datetime
    gospodarz: KadraDruzyny
    gosc: KadraDruzyny
    dane: DaneProtokolu
    opcje: OpcjeZapowiedzi = OpcjeZapowiedzi()
    kolejnosc: KolejnoscProtokolu = KolejnoscProtokolu.POZYCJE


@dataclass(frozen=True)
class WierszZawodnikaProtokolu:
    czlonek: CzlonekKadry
    nowa_grupa: bool = False


class KolejnoscZawodnikowProtokoluPolicy:
    BEZ_NUMERU = 10_000

    def wiersze(
        self, kadra: KadraDruzyny, kolejnosc: KolejnoscProtokolu
    ) -> tuple[WierszZawodnikaProtokolu, ...]:
        if kolejnosc is KolejnoscProtokolu.NUMERY:
            czlonkowie = [c for grupa in kadra.grupy for c in grupa.czlonkowie]
            return tuple(WierszZawodnikaProtokolu(c) for c in self._wedlug_numerow(czlonkowie))
        return tuple(
            WierszZawodnikaProtokolu(czlonek, nowa_grupa=indeks_grupy > 0 and indeks == 0)
            for indeks_grupy, grupa in enumerate(kadra.grupy)
            for indeks, czlonek in enumerate(self._wedlug_numerow(grupa.czlonkowie))
        )

    def _wedlug_numerow(self, czlonkowie: Sequence[CzlonekKadry]) -> list[CzlonekKadry]:
        return sorted(
            czlonkowie,
            key=lambda c: (
                min(c.numery) if c.numery else self.BEZ_NUMERU,
                (c.nazwisko or "").casefold(),
                (c.imie or "").casefold(),
                c.id_zawodnik,
            ),
        )
