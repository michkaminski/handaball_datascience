from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ZakladkaFrekwencji:
    klucz: str
    etykieta: str


ZAKLADKI_FREKWENCJI = (
    ZakladkaFrekwencji("overview", "Podsumowanie"),
    ZakladkaFrekwencji("trends", "Trendy"),
    ZakladkaFrekwencji("clubs", "Kluby"),
    ZakladkaFrekwencji("cities", "Miasta"),
    ZakladkaFrekwencji("records", "Rekordy"),
    ZakladkaFrekwencji("opponents", "Przeciwnicy"),
    ZakladkaFrekwencji("calendar", "Kalendarz"),
    ZakladkaFrekwencji("extended", "Rekordy+"),
    ZakladkaFrekwencji("science", "Data Science"),
    ZakladkaFrekwencji("maf", "Atrakcyjność (MAF)"),
)
PARAMETRY_ZAKLADKI = ("zakladka", "tab")


class WyborZakladkiFrekwencji:
    def __init__(self, zakladki: tuple[ZakladkaFrekwencji, ...] = ZAKLADKI_FREKWENCJI) -> None:
        self._klucze = tuple(zakladka.klucz for zakladka in zakladki)

    def wybierz(self, parametry: Mapping[str, str]) -> str:
        for nazwa in PARAMETRY_ZAKLADKI:
            klucz = parametry.get(nazwa, "").strip().lower()
            if klucz in self._klucze:
                return klucz
        return self._klucze[0]
