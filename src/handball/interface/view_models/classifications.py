from dataclasses import dataclass
from decimal import Decimal

from handball.domain.classifications import Sklad


@dataclass(frozen=True)
class PozycjaSkladuViewModel:
    id_zawodnik: int
    zawodnik: str
    nr_koszulki: int | None
    pozycja: str | None
    wzrost: Decimal | None
    waga: Decimal | None
    kolor_pozycji: int | None


@dataclass(frozen=True)
class SzczegolySkladuViewModel:
    sklad: Sklad
    zawodnicy: list[PozycjaSkladuViewModel]
