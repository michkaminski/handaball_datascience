from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from handball.domain.matches import DaneMeczu
from handball.domain.options import OpcjaWyboru


@dataclass(frozen=True)
class WyborTerminarza:
    id_sezon: int | None = None
    id_rozgrywki: int | None = None
    id_runda: int | None = None
    id_kolejka: int | None = None


@dataclass(frozen=True)
class FiltryTerminarza:
    id_sezon: int
    id_rozgrywki: int
    id_runda: int | None = None
    id_kolejka: int | None = None


@dataclass(frozen=True)
class OpcjeTerminarza:
    wybor: WyborTerminarza
    sezony: list[OpcjaWyboru] = field(default_factory=list)
    rozgrywki: list[OpcjaWyboru] = field(default_factory=list)
    rundy: list[OpcjaWyboru] = field(default_factory=list)
    kolejki: list[OpcjaWyboru] = field(default_factory=list)

    @property
    def filtry(self) -> FiltryTerminarza | None:
        if self.wybor.id_sezon is None or self.wybor.id_rozgrywki is None:
            return None
        return FiltryTerminarza(
            self.wybor.id_sezon,
            self.wybor.id_rozgrywki,
            self.wybor.id_runda,
            self.wybor.id_kolejka,
        )


@dataclass(frozen=True)
class PozycjaTerminarza:
    id_mecz: int
    mecz: DaneMeczu
    gospodarz: str | None
    gosc: str | None
    hala: str | None
    id_runda: int | None = None
    runda: str | None = None
    id_kolejka: int | None = None
    kolejka: str | None = None
    nr_kolejki: int | None = None

    @property
    def termin(self) -> datetime | None:
        return self.mecz.data_faktyczna or self.mecz.data_propozycji

    @property
    def godzina_znana(self) -> bool:
        return self.mecz.data_faktyczna is not None


@dataclass(frozen=True)
class DzienTerminarza:
    dzien: date | None
    mecze: tuple[PozycjaTerminarza, ...]


@dataclass(frozen=True)
class KolejkaTerminarza:
    id_kolejka: int | None
    nazwa: str | None
    nr: int | None
    dni: tuple[DzienTerminarza, ...]

    @property
    def liczba_meczow(self) -> int:
        return sum(len(dzien.mecze) for dzien in self.dni)


@dataclass(frozen=True)
class RundaTerminarza:
    id_runda: int | None
    nazwa: str | None
    kolejki: tuple[KolejkaTerminarza, ...]


@dataclass(frozen=True)
class Terminarz:
    filtry: FiltryTerminarza
    rundy: tuple[RundaTerminarza, ...]

    @property
    def liczba_meczow(self) -> int:
        return sum(kolejka.liczba_meczow for runda in self.rundy for kolejka in runda.kolejki)
