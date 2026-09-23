from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from handball.domain.matches import DaneMeczu


class KategoriaRozgrywek(Enum):
    SUPERLIGA_M = "superliga_m"
    SUPERLIGA_K = "superliga_k"
    LIGA_CENTRALNA_M = "liga_centralna_m"
    LIGA_CENTRALNA_K = "liga_centralna_k"
    POZOSTALE = "pozostale"

    @property
    def priorytetowa(self) -> bool:
        return self is not KategoriaRozgrywek.POZOSTALE

    @property
    def kolejnosc(self) -> int:
        return list(KategoriaRozgrywek).index(self)

    @property
    def etykieta(self) -> str:
        return {
            KategoriaRozgrywek.SUPERLIGA_M: "Superliga mężczyzn",
            KategoriaRozgrywek.SUPERLIGA_K: "Superliga kobiet",
            KategoriaRozgrywek.LIGA_CENTRALNA_M: "Liga Centralna mężczyzn",
            KategoriaRozgrywek.LIGA_CENTRALNA_K: "Liga Centralna kobiet",
            KategoriaRozgrywek.POZOSTALE: "Pozostałe rozgrywki",
        }[self]


@dataclass(frozen=True)
class SezonAktualnosci:
    id_sezon: int
    nazwa: str


@dataclass(frozen=True)
class RozgrywkiAktualnosci:
    id_rozgrywki: int
    nazwa: str
    plec: str | None


@dataclass(frozen=True)
class MeczAktualnosci:
    id_mecz: int
    termin: datetime | None
    id_rozgrywki: int
    gospodarz: str | None
    gosc: str | None
    mecz: DaneMeczu

    @property
    def suma_bramek(self) -> int:
        return (self.mecz.wynik_gosp_full or 0) + (self.mecz.wynik_gosc_full or 0)

    @property
    def roznica_bramek(self) -> int:
        return abs((self.mecz.wynik_gosp_full or 0) - (self.mecz.wynik_gosc_full or 0))


@dataclass(frozen=True)
class StrzelecAktualnosci:
    id_rozgrywki: int
    id_zawodnik: int
    zawodnik: str
    druzyna: str | None
    mecze: int
    bramki: int


@dataclass(frozen=True)
class WystepAktualnosci:
    id_rozgrywki: int
    id_mecz: int
    termin: datetime | None
    id_zawodnik: int
    zawodnik: str
    druzyna: str | None
    bramki: int


@dataclass(frozen=True)
class SekcjaRozgrywek:
    kategoria: KategoriaRozgrywek
    rozgrywki: RozgrywkiAktualnosci
    liczba_rozegranych: int
    srednia_bramek: float | None
    ostatnie_mecze: tuple[MeczAktualnosci, ...]
    strzelcy: tuple[StrzelecAktualnosci, ...]


@dataclass(frozen=True)
class RekordMeczu:
    mecz: MeczAktualnosci
    rozgrywki: RozgrywkiAktualnosci
    wartosc: int


@dataclass(frozen=True)
class WystepZRozgrywkami:
    wystep: WystepAktualnosci
    rozgrywki: RozgrywkiAktualnosci


@dataclass(frozen=True)
class PozostalyMecz:
    mecz: MeczAktualnosci
    rozgrywki: RozgrywkiAktualnosci


@dataclass(frozen=True)
class Aktualnosci:
    sezon: SezonAktualnosci | None
    sekcje: tuple[SekcjaRozgrywek, ...]
    pozostale_mecze: tuple[PozostalyMecz, ...]
    liczba_rozegranych: int
    suma_bramek: int
    ostatni_termin: datetime | None
    najwiecej_bramek: RekordMeczu | None
    najwyzsze_zwyciestwo: RekordMeczu | None
    najlepsze_wystepy: tuple[WystepZRozgrywkami, ...]
    najbardziej_bramkostrzelna: SekcjaRozgrywek | None
