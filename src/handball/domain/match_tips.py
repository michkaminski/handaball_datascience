from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from handball.domain.match_predictions import OpisModeluPrognoz, PrognozaZapowiedzi
from handball.domain.schedule import PozycjaTerminarza


@dataclass(frozen=True)
class WyborTypowan:
    data_od: date | None = None
    data_do: date | None = None
    rozgrywki: frozenset[str] = frozenset()
    wersja_modelu: str | None = None


@dataclass(frozen=True)
class FiltryTypowan:
    data_od: date
    data_do: date
    wersja_modelu: str
    rozgrywki: frozenset[str] = frozenset()


@dataclass(frozen=True)
class PozycjaTypowania:
    id_rozgrywki: int
    rozgrywki: str
    sezon: str
    pozycja: PozycjaTerminarza


@dataclass(frozen=True)
class TypowanieMeczu:
    pozycja: PozycjaTerminarza
    prognoza: PrognozaZapowiedzi


@dataclass(frozen=True)
class GrupaTypowan:
    rozgrywki: str
    sezon: str
    runda: str | None
    kolejka: str | None
    nr_kolejki: int | None
    typowania: tuple[TypowanieMeczu, ...]


@dataclass(frozen=True)
class RaportTypowan:
    filtry: FiltryTypowan
    model: OpisModeluPrognoz
    modele: tuple[OpisModeluPrognoz, ...]
    dostepne_rozgrywki: tuple[str, ...]
    grupy: tuple[GrupaTypowan, ...]

    @property
    def liczba_meczow(self) -> int:
        return sum(len(grupa.typowania) for grupa in self.grupy)


@dataclass(frozen=True)
class TypowaniaKolejki:
    model: OpisModeluPrognoz
    kolejka: str | None
    nr_kolejki: int | None
    typowania: tuple[TypowanieMeczu, ...]
