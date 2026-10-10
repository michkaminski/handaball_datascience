from __future__ import annotations

import math
from collections.abc import Sequence

PROG_MALEJ_PROBY = 5


def formatuj_calkowita(wartosc: int) -> str:
    return f"{wartosc:,}".replace(",", " ")


def formatuj_opcjonalna_calkowita(wartosc: int | None) -> str:
    if wartosc is None:
        return "—"
    return formatuj_calkowita(wartosc)


def formatuj_zaokraglona(wartosc: float | None) -> str:
    if wartosc is None:
        return "—"
    return formatuj_calkowita(round(wartosc))


def formatuj_udzial(udzial: float | None) -> str:
    if udzial is None:
        return "—"
    return f"{udzial * 100:.1f}%"


def formatuj_procent(procent: float | None) -> str:
    if procent is None:
        return "—"
    return f"{procent:.1f}%"


def formatuj_zmiane(zmiana: float | None) -> str:
    if zmiana is None:
        return "—"
    return f"{zmiana * 100:+.1f}%"


def formatuj_roznice(roznica: float | None) -> str:
    if roznica is None:
        return "—"
    return f"{roznica:+,.0f}".replace(",", " ")


def formatuj_wspolczynnik(wartosc: float | None) -> str:
    if wartosc is None:
        return "—"
    return f"{wartosc:+.2f}"


def formatuj_dziesietna(wartosc: float | None, miejsca: int = 1) -> str:
    if wartosc is None:
        return "—"
    return f"{wartosc:.{miejsca}f}"


def zmiana_wzgledna(aktualna: float | None, poprzednia: float | None) -> float | None:
    if aktualna is None or poprzednia is None or poprzednia == 0:
        return None
    return (aktualna - poprzednia) / poprzednia


def wypelnienie_procent(widzowie: float, pojemnosc: float) -> float | None:
    if pojemnosc <= 0:
        return None
    return widzowie / pojemnosc * 100


def percentyl(wartosci: Sequence[float], ulamek: float) -> float | None:
    if not wartosci:
        return None
    if not 0 <= ulamek <= 1:
        raise ValueError("ułamek musi mieścić się w przedziale 0–1")
    uporzadkowane = sorted(wartosci)
    pozycja = ulamek * (len(uporzadkowane) - 1)
    dolna = math.floor(pozycja)
    gorna = math.ceil(pozycja)
    if dolna == gorna:
        return float(uporzadkowane[dolna])
    return uporzadkowane[dolna] + (uporzadkowane[gorna] - uporzadkowane[dolna]) * (pozycja - dolna)
