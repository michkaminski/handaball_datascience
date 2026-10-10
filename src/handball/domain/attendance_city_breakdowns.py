from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol

from handball.domain.attendance_aggregate import AgregatFrekwencji, MiaryRozkladu
from handball.domain.attendance_city_names import klucz_miasta

LIMIT_SEZONOW_MIAST = 600
LIMIT_ROZGRYWEK_MIAST = 400
LIMIT_ROZGRYWEK_NA_MIASTO = 15
LIMIT_HAL_MIAST = 300
LIMIT_HAL_NA_MIASTO = 10


class MaAgregat(Protocol):
    @property
    def agregat(self) -> AgregatFrekwencji: ...


@dataclass(frozen=True)
class SezonMiasta:
    klucz: str
    sezon: str
    rok_poczatku: int | None
    agregat: AgregatFrekwencji
    rozklad: MiaryRozkladu = field(default_factory=MiaryRozkladu)


@dataclass(frozen=True)
class RozgrywkiMiasta:
    klucz: str
    rozgrywki: str
    liczba_klubow: int
    agregat: AgregatFrekwencji
    rozklad: MiaryRozkladu = field(default_factory=MiaryRozkladu)


@dataclass(frozen=True)
class HalaMiasta:
    klucz: str
    id_hala: int
    hala: str
    miasto_hali: str | None
    agregat: AgregatFrekwencji
    rozklad: MiaryRozkladu = field(default_factory=MiaryRozkladu)

    @property
    def miasto_hali_inne(self) -> bool:
        if not self.miasto_hali or not self.miasto_hali.strip():
            return False
        return klucz_miasta(self.miasto_hali) != klucz_miasta(self.klucz)

    @property
    def miasto_hali_etykieta(self) -> str:
        return self.miasto_hali.strip() if self.miasto_hali and self.miasto_hali_inne else "—"

    @property
    def etykieta(self) -> str:
        if self.miasto_hali_inne:
            return f"{self.hala} ({self.miasto_hali_etykieta})"
        return self.hala


def porzadek_sezonow(wiersz: SezonMiasta) -> tuple[int, str, str]:
    return (
        wiersz.rok_poczatku if wiersz.rok_poczatku is not None else -1,
        wiersz.sezon.casefold(),
        wiersz.sezon,
    )


def porzadek_rozgrywek(wiersz: RozgrywkiMiasta) -> tuple[int, str]:
    return (-wiersz.agregat.suma, wiersz.rozgrywki.casefold())


def porzadek_hal(wiersz: HalaMiasta) -> tuple[int, str, int]:
    return (-wiersz.agregat.suma, wiersz.hala.casefold(), wiersz.id_hala)


def przydziel_do_miast[T: MaAgregat](
    wiersze: Iterable[T],
    klucze_rankingu: Sequence[str],
    klucz_wiersza: Callable[[T], str],
    porzadek: Callable[[T], tuple[object, ...]],
    limit_ogolny: int,
    limit_na_miasto: int | None = None,
) -> dict[str, tuple[T, ...]]:
    grupy: dict[str, list[T]] = {klucz: [] for klucz in klucze_rankingu}
    for wiersz in wiersze:
        grupa = grupy.get(klucz_miasta(klucz_wiersza(wiersz)))
        if grupa is not None and wiersz.agregat.znane > 0:
            grupa.append(wiersz)
    pozostalo = limit_ogolny
    wynik: dict[str, tuple[T, ...]] = {}
    for klucz in klucze_rankingu:
        uporzadkowane = sorted(grupy[klucz], key=porzadek)
        if limit_na_miasto is not None:
            uporzadkowane = uporzadkowane[:limit_na_miasto]
        przypisane = tuple(uporzadkowane[: max(pozostalo, 0)])
        pozostalo -= len(przypisane)
        wynik[klucz] = przypisane
    return wynik
