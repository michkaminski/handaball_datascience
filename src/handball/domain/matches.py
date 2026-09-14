from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from handball.domain.options import OpcjaWyboru

SORTOWANIA_DOZWOLONE = frozenset({"data", "-data"})
JEDEN_DZIEN = timedelta(days=1)

WZORZEC_CZESCIOWEJ_DATY = re.compile(r"^(?P<rok>\d{4})(-(?P<miesiac>\d{2})(-(?P<dzien>\d{2}))?)?$")


def zakres_z_czesciowej_daty(tekst: str) -> tuple[datetime, datetime]:
    dopasowanie = WZORZEC_CZESCIOWEJ_DATY.match(tekst.strip())
    if not dopasowanie:
        raise ValueError(f"niepoprawny format daty: {tekst!r}")

    rok = int(dopasowanie.group("rok"))
    miesiac = dopasowanie.group("miesiac")
    dzien = dopasowanie.group("dzien")

    if dzien is not None:
        start = datetime(rok, int(miesiac), int(dzien))
        koniec = start + JEDEN_DZIEN
        return start, koniec

    if miesiac is not None:
        miesiac_int = int(miesiac)
        start = datetime(rok, miesiac_int, 1)
        if miesiac_int == 12:
            koniec = datetime(rok + 1, 1, 1)
        else:
            koniec = datetime(rok, miesiac_int + 1, 1)
        return start, koniec

    return datetime(rok, 1, 1), datetime(rok + 1, 1, 1)


@dataclass(frozen=True)
class FiltryMeczow:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    id_hala: int | None = None
    szukaj_druzyny: str | None = None
    data_od: datetime | None = None
    data_do: datetime | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "data"

    def __post_init__(self) -> None:
        if self.strona < 1:
            raise ValueError("strona musi byc >= 1")
        if not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("rozmiar_strony musi byc w zakresie 1-100")
        if self.sortowanie not in SORTOWANIA_DOZWOLONE:
            raise ValueError(f"niedozwolone sortowanie: {self.sortowanie}")


@dataclass(frozen=True)
class PozycjaListyMeczow:
    id_mecz: int
    termin: datetime | None
    sezon: str | None
    rozgrywki: str | None
    gospodarz: str | None
    gosc: str | None
    wynik: str
    hala: str | None


@dataclass(frozen=True)
class StronaMeczow:
    pozycje: list[PozycjaListyMeczow]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class OpcjeFiltrowMeczow:
    sezony: list[OpcjaWyboru] = field(default_factory=list)
    rozgrywki: list[str] = field(default_factory=list)
    hale: list[OpcjaWyboru] = field(default_factory=list)
