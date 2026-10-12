from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

SEZON_IMPORTU = 195
NAZWA_SEZONU_IMPORTU = "2026/2027"
TRYBY_IMPORTU = {
    "pelny": "Pełny",
    "uzupelniajacy": "Uzupełniający",
    "tabele": "Tylko tabele",
    "mecz": "Jeden mecz",
    "mecze": "Wybrane mecze",
}
LIMIT_WYBRANYCH_MECZOW = 80
LIGI_IMPORTU = {
    12007: "Superliga mężczyzn",
    12009: "Superliga kobiet",
    12010: "Liga Centralna mężczyzn",
    12011: "Liga Centralna kobiet",
    12012: "I liga kobiet grupa A",
    12013: "I liga kobiet grupa B",
    12014: "I liga kobiet grupa C",
    12015: "I liga mężczyzn grupa D",
    12016: "I liga mężczyzn grupa A",
    12017: "I liga mężczyzn grupa B",
    12018: "I liga mężczyzn grupa C",
    12019: "Superpuchar Polski kobiet",
    12020: "Superpuchar Polski mężczyzn",
    12021: "Puchar Polski mężczyzn - eliminacje wojewódzkie (lubuskie)",
    12023: "II liga mężczyzn grupa 4",
    12024: "II liga kobiet grupa 4",
    12025: "II liga mężczyzn grupa 2",
    12026: "II liga kobiet grupa 2",
    12030: "Puchar Polski mężczyzn (lubelskie)",
    12038: "II liga mężczyzn grupa 1",
    12043: "II liga mężczyzn grupa 3",
    12100: "Puchar Polski mężczyzn - eliminacje wojewódzkie (pomorskie)",
    12112: "II liga kobiet grupa 1",
    12119: "Puchar Polski mężczyzn - eliminacje wojewódzkie (małopolskie)",
    12120: "Puchar Polski kobiet (mazowieckie)",
    12121: "Puchar Polski mężczyzn (mazowieckie)",
    12133: "Puchar Polski mężczyzn - eliminacje wojewódzkie (zachodniopomorskie)",
    12136: "II liga kobiet grupa 3",
}


class BladImportu(Exception):
    pass


@dataclass(frozen=True)
class OpcjaImportu:
    id: int
    nazwa: str


@dataclass(frozen=True)
class OpcjeImportuTabel:
    sezony: list[OpcjaImportu]
    wybrany_sezon: OpcjaImportu | None
    rozgrywki: list[OpcjaImportu]


@dataclass(frozen=True)
class MeczImportu:
    id: int
    id_rozgrywki: int
    id_kolejka: int
    nazwa_rozgrywek: str
    opis: str
    id_sezon: int = SEZON_IMPORTU
    nazwa_sezonu: str = NAZWA_SEZONU_IMPORTU


@dataclass
class RekordImportu:
    tabela: str
    klucz: dict[str, Any]
    dane: dict[str, Any]
    zrodlo: str
    uzupelnij: bool = False
    zrodla: list[str] = field(default_factory=list)
    poprzednio: dict[str, Any] | None = None
    zmiany: dict[str, Any] = field(default_factory=dict)


@dataclass
class ZadaniePobrania:
    endpoint: str
    parametry: dict[str, int]
    rodzaj: str
    kontekst: dict[str, int] = field(default_factory=dict)


@dataclass
class PrzebiegImportu:
    id: str
    ligi: list[int]
    rozpoczecie: str
    status: str = "POBIERANIE"
    kolejka: list[ZadaniePobrania] = field(default_factory=list)
    wykonane: list[str] = field(default_factory=list)
    skroty_zrodel: dict[str, str] = field(default_factory=dict)
    rekordy: list[RekordImportu] = field(default_factory=list)
    blad: str | None = None
    id_przebieg_bazy: int | None = None
    tryb: str = "pelny"
    nieudane_probowania: dict[str, int] = field(default_factory=dict)
    pominiete: list[dict[str, Any]] = field(default_factory=list)
    id_sezon: int = SEZON_IMPORTU
    nazwa_sezonu: str = NAZWA_SEZONU_IMPORTU
    nazwy_lig: dict[str, str] = field(default_factory=dict)
    id_mecz: int | None = None
    opis: str | None = None
    id_mecze: list[int] = field(default_factory=list)
    opisy_meczow: list[str] = field(default_factory=list)

    @property
    def nazwa_trybu(self) -> str:
        return TRYBY_IMPORTU.get(self.tryb, TRYBY_IMPORTU["pelny"])

    @property
    def pary_meczow(self) -> list[tuple[int, str]]:
        return list(zip(self.id_mecze, self.opisy_meczow, strict=False))

    @property
    def dopisek_meczow(self) -> str | None:
        if self.id_mecz:
            return f"mecz {self.id_mecz}"
        liczba = len(self.id_mecze)
        if liczba == 0:
            return None
        if liczba == 1:
            return f"mecz {self.id_mecze[0]}"
        if liczba % 100 not in (12, 13, 14) and liczba % 10 in (2, 3, 4):
            return f"{liczba} mecze"
        return f"{liczba} meczów"

    @property
    def nazwy_rozgrywek(self) -> list[str]:
        return [self.nazwy_lig.get(str(i)) or LIGI_IMPORTU.get(i) or str(i) for i in self.ligi]

    @property
    def adres_id(self) -> str:
        return str(UUID(self.id))

    @property
    def podsumowanie(self) -> dict[str, int]:
        return {
            "nowe": sum(r.poprzednio is None for r in self.rekordy),
            "zmienione": sum(r.poprzednio is not None and bool(r.zmiany) for r in self.rekordy),
            "bez_zmian": sum(r.poprzednio is not None and not r.zmiany for r in self.rekordy),
        }
