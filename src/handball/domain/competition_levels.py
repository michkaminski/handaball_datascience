from __future__ import annotations

import re
from dataclasses import dataclass


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

    def klucz(self, nazwa: str) -> tuple[int, str]:
        return (self.poziom(nazwa), nazwa.casefold())
