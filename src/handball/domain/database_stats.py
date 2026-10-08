from __future__ import annotations

from dataclasses import dataclass


DOZWOLONE_SORTOWANIA = frozenset(
    {
        "schema",
        "-schema",
        "tabela",
        "-tabela",
        "rekordy",
        "-rekordy",
        "rozmiar",
        "-rozmiar",
        "dane",
        "-dane",
        "indeksy",
        "-indeksy",
    }
)
DOZWOLONE_ZAPELNIENIA = frozenset({"puste", "niepuste"})
DOMYSLNE_SORTOWANIE = "-rozmiar"


def formatuj_bajty(bajty: int) -> str:
    wartosc = float(max(0, bajty))
    for jednostka in ("B", "KB", "MB", "GB", "TB"):
        if wartosc < 1024 or jednostka == "TB":
            if jednostka == "B":
                return f"{int(wartosc)} {jednostka}"
            tekst = f"{wartosc:.1f}".rstrip("0").rstrip(".")
            return f"{tekst} {jednostka}"
        wartosc /= 1024
    return f"{int(bajty)} B"


def formatuj_liczbe(wartosc: int) -> str:
    return f"{wartosc:,}".replace(",", " ")


@dataclass(frozen=True)
class FiltryStatystykBazy:
    szukaj: str | None = None
    schemat: str | None = None
    zapelnienie: str | None = None
    min_rekordow: int | None = None
    sortowanie: str = DOMYSLNE_SORTOWANIE

    def __post_init__(self) -> None:
        if self.sortowanie not in DOZWOLONE_SORTOWANIA:
            raise ValueError("nieobsługiwane sortowanie")
        if self.zapelnienie is not None and self.zapelnienie not in DOZWOLONE_ZAPELNIENIA:
            raise ValueError("zapelnienie must be puste or niepuste")
        if self.min_rekordow is not None and self.min_rekordow < 0:
            raise ValueError("min_rekordow must be >= 0")


@dataclass(frozen=True)
class PozycjaTabeliBazy:
    schemat: str
    tabela: str
    rekordy: int
    rozmiar_bajty: int
    dane_bajty: int
    indeksy_bajty: int

    @property
    def nazwa_pelna(self) -> str:
        return f"{self.schemat}.{self.tabela}"

    @property
    def rekordy_etykieta(self) -> str:
        return formatuj_liczbe(self.rekordy)

    @property
    def rozmiar_etykieta(self) -> str:
        return formatuj_bajty(self.rozmiar_bajty)

    @property
    def dane_etykieta(self) -> str:
        return formatuj_bajty(self.dane_bajty)

    @property
    def indeksy_etykieta(self) -> str:
        return formatuj_bajty(self.indeksy_bajty)


@dataclass(frozen=True)
class PodsumowanieBazy:
    nazwa: str
    rozmiar_bajty: int
    liczba_tabel: int
    suma_rekordow: int
    suma_rozmiarow_bajty: int
    suma_indeksow_bajty: int

    @property
    def rozmiar_etykieta(self) -> str:
        return formatuj_bajty(self.rozmiar_bajty)

    @property
    def suma_rekordow_etykieta(self) -> str:
        return formatuj_liczbe(self.suma_rekordow)

    @property
    def suma_rozmiarow_etykieta(self) -> str:
        return formatuj_bajty(self.suma_rozmiarow_bajty)

    @property
    def suma_indeksow_etykieta(self) -> str:
        return formatuj_bajty(self.suma_indeksow_bajty)

    @property
    def liczba_tabel_etykieta(self) -> str:
        return formatuj_liczbe(self.liczba_tabel)


@dataclass(frozen=True)
class SnapshotStatystykBazy:
    podsumowanie: PodsumowanieBazy
    tabele: tuple[PozycjaTabeliBazy, ...]
    schematy: tuple[str, ...]


@dataclass(frozen=True)
class StronaStatystykBazy:
    podsumowanie: PodsumowanieBazy
    pozycje: tuple[PozycjaTabeliBazy, ...]
    schematy: tuple[str, ...]
    filtry: FiltryStatystykBazy
    liczba_przefiltrowanych: int

    @property
    def liczba_przefiltrowanych_etykieta(self) -> str:
        return formatuj_liczbe(self.liczba_przefiltrowanych)


def przefiltruj_tabele(
    tabele: tuple[PozycjaTabeliBazy, ...],
    filtry: FiltryStatystykBazy,
) -> tuple[PozycjaTabeliBazy, ...]:
    wynik = list(tabele)
    if filtry.szukaj:
        wzorzec = filtry.szukaj.casefold()
        wynik = [
            tabela
            for tabela in wynik
            if wzorzec in tabela.schemat.casefold()
            or wzorzec in tabela.tabela.casefold()
            or wzorzec in tabela.nazwa_pelna.casefold()
        ]
    if filtry.schemat:
        wynik = [tabela for tabela in wynik if tabela.schemat == filtry.schemat]
    if filtry.zapelnienie == "puste":
        wynik = [tabela for tabela in wynik if tabela.rekordy == 0]
    elif filtry.zapelnienie == "niepuste":
        wynik = [tabela for tabela in wynik if tabela.rekordy > 0]
    if filtry.min_rekordow is not None:
        wynik = [tabela for tabela in wynik if tabela.rekordy >= filtry.min_rekordow]
    odwrotnie = filtry.sortowanie.startswith("-")
    pole = filtry.sortowanie.lstrip("-")
    klucz = {
        "schema": lambda t: t.schemat.casefold(),
        "tabela": lambda t: t.tabela.casefold(),
        "rekordy": lambda t: t.rekordy,
        "rozmiar": lambda t: t.rozmiar_bajty,
        "dane": lambda t: t.dane_bajty,
        "indeksy": lambda t: t.indeksy_bajty,
    }[pole]
    wynik.sort(key=klucz, reverse=odwrotnie)
    return tuple(wynik)
