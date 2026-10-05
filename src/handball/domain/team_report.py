from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime

from handball.domain.match_preview import WystepSezonuZawodnika
from handball.domain.team_details import (
    BilansDruzyny,
    BilansSezonuDruzyny,
    KolejnoscPozycjiPolicy,
    SezonDruzyny,
    SzczegolyDruzyny,
    WystepDruzyny,
    ZawodnikDruzyny,
    ZestawienieSezonuDruzyny,
)

DOMYSLNA_LICZBA_MECZOW = 15


@dataclass(frozen=True)
class PoprzedniSezonZawodnikaRaportu:
    wystepy: tuple[WystepSezonuZawodnika, ...] = ()

    @property
    def zagral(self) -> bool:
        return bool(self.wystepy)

    @property
    def mecze(self) -> int:
        return sum(w.mecze for w in self.wystepy)

    @property
    def bramki(self) -> int:
        return sum(w.bramki for w in self.wystepy)


@dataclass(frozen=True)
class ZawodnikRaportu:
    id_zawodnik: int
    imie: str | None
    nazwisko: str | None
    numery: tuple[int, ...]
    pozycja: str | None
    data_urodzenia: date | None
    sezon: ZawodnikDruzyny | None
    poprzedni: PoprzedniSezonZawodnikaRaportu = field(
        default_factory=PoprzedniSezonZawodnikaRaportu
    )


@dataclass(frozen=True)
class StrzelecMeczu:
    nazwisko: str
    bramki: int


@dataclass(frozen=True)
class MeczRaportu:
    wystep: WystepDruzyny
    strzelcy: tuple[StrzelecMeczu, ...] = ()
    karne_bramki: int | None = None
    karne_liczba: int | None = None
    dwie_minuty: int | None = None


@dataclass(frozen=True)
class RaportDruzyny:
    szczegoly: SzczegolyDruzyny
    sezon: SezonDruzyny
    poprzedni_sezon: str | None
    rozgrywki: tuple[str, ...]
    bilans: BilansDruzyny
    sezony: tuple[BilansSezonuDruzyny, ...]
    zawodnicy: tuple[ZawodnikRaportu, ...]
    ze_skladu: bool
    mecze: tuple[MeczRaportu, ...]
    stan_na: datetime


@dataclass(frozen=True)
class StronaZestawien:
    sezon: str
    nazwa_druzyny: str | None
    rozgrywki: tuple[str, ...]
    bilans: BilansDruzyny | None
    zestawienie: ZestawienieSezonuDruzyny | None
    roczniki: Mapping[int, date | None] = field(default_factory=dict)


@dataclass(frozen=True)
class ZestawieniaDruzyny:
    szczegoly: SzczegolyDruzyny
    strony: tuple[StronaZestawien, ...]
    stan_na: datetime


class KolejnoscZawodnikowRaportuPolicy:
    BEZ_NUMERU = 10_000

    def __init__(self, pozycje: KolejnoscPozycjiPolicy) -> None:
        self._pozycje = pozycje

    def grupa(self, zawodnik: ZawodnikRaportu) -> int:
        return self.grupa_pozycji((zawodnik.pozycja,) if zawodnik.pozycja else ())

    def grupa_pozycji(self, pozycje: tuple[str, ...]) -> int:
        return self._pozycje.pozycja(pozycje)

    def uporzadkuj(self, zawodnicy: Sequence[ZawodnikRaportu]) -> tuple[ZawodnikRaportu, ...]:
        return tuple(
            sorted(
                zawodnicy,
                key=lambda z: (
                    self.grupa(z),
                    min(z.numery) if z.numery else self.BEZ_NUMERU,
                    (z.nazwisko or "").casefold(),
                    (z.imie or "").casefold(),
                ),
            )
        )


class MiejscaPolicy:
    def miejsca[K](self, wartosci: Mapping[K, float]) -> dict[K, int]:
        return {
            klucz: 1 + sum(1 for inna in wartosci.values() if inna > wartosc)
            for klucz, wartosc in wartosci.items()
        }

    def najlepsi[K](self, wartosci: Mapping[K, float], limit: int) -> frozenset[K]:
        return frozenset(
            klucz for klucz, miejsce in self.miejsca(wartosci).items() if miejsce <= limit
        )
