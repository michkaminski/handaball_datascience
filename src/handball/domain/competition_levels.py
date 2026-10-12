from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from handball.domain.options import OpcjaWyboru


class GrupaRozgrywek(StrEnum):
    SUPERLIGA = "superliga"
    LIGA_CENTRALNA = "liga_centralna"
    I_LIGA = "i_liga"
    II_LIGA = "ii_liga"
    PUCHAR_POLSKI = "puchar_polski"


_POZIOM_GRUPY = {
    0: GrupaRozgrywek.SUPERLIGA,
    1: GrupaRozgrywek.LIGA_CENTRALNA,
    2: GrupaRozgrywek.I_LIGA,
    3: GrupaRozgrywek.II_LIGA,
}


@dataclass(frozen=True)
class KolejnoscRozgrywekPolicy:
    wzorce: tuple[str, ...] = (
        "superliga|superligę|ekstraklasa",
        r"liga\s+centralna",
        r"(^|[^a-ząćęłńóśźż])i\s+liga",
        r"(^|[^a-ząćęłńóśźż])ii\s+liga",
        r"(^|[^a-ząćęłńóśźż])iii\s+liga",
        r"(^|[^a-ząćęłńóśźż])iv\s+liga",
    )

    def poziom(self, nazwa: str) -> int:
        for indeks, wzorzec in enumerate(self.wzorce):
            if re.search(wzorzec, nazwa, re.IGNORECASE):
                return indeks
        return len(self.wzorce)

    def klucz(self, nazwa: str) -> tuple[int, bool, str]:
        return (self.poziom(nazwa), self.baraz(nazwa), nazwa.casefold())

    def baraz(self, nazwa: str) -> bool:
        return nazwa.strip().casefold().startswith("baraż")

    def uporzadkuj_nazwy(self, nazwy: Iterable[str]) -> list[str]:
        return sorted(nazwy, key=self.klucz)

    def uporzadkuj_opcje(self, opcje: Iterable[OpcjaWyboru]) -> list[OpcjaWyboru]:
        return sorted(opcje, key=lambda opcja: (*self.klucz(opcja.etykieta), opcja.wartosc))


class DopasowanieGrupRozgrywek:
    def __init__(self, kolejnosc: KolejnoscRozgrywekPolicy | None = None) -> None:
        self._kolejnosc = kolejnosc or KolejnoscRozgrywekPolicy()

    def pasuje(self, nazwa: str | None, grupy: frozenset[GrupaRozgrywek]) -> bool:
        if not grupy:
            return True
        return self.grupa(nazwa or "") in grupy

    def grupa(self, nazwa: str) -> GrupaRozgrywek | None:
        zlozona = nazwa.casefold()
        if "superpuchar" not in zlozona and re.search(r"puchar\s+polski", zlozona):
            return GrupaRozgrywek.PUCHAR_POLSKI
        return _POZIOM_GRUPY.get(self._kolejnosc.poziom(nazwa))
