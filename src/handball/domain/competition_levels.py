from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from handball.domain.options import OpcjaWyboru


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
