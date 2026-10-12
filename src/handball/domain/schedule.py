from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime

from handball.domain.match_rules import MeczPolicy, StatusMeczu
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
class FiltryPobierania:
    id_sezon: int
    id_rozgrywki: int | None = None
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


class ZakresPobierania:
    def __init__(self, reguly: MeczPolicy) -> None:
        self._reguly = reguly

    def zakonczone_kolejki(self, terminarz: Terminarz) -> Terminarz:
        return self._rundy(terminarz, lambda kolejka: self._zakonczona(kolejka), None)

    def tylko_mecze(self, terminarz: Terminarz, identyfikatory: set[int]) -> Terminarz:
        return self._rundy(terminarz, lambda _kolejka: True, identyfikatory)

    def _zakonczona(self, kolejka: KolejkaTerminarza) -> bool:
        mecze = [pozycja for dzien in kolejka.dni for pozycja in dzien.mecze]
        return bool(mecze) and all(
            self._reguly.status(pozycja.mecz) is not StatusMeczu.ZAPLANOWANY for pozycja in mecze
        )

    def _rundy(
        self,
        terminarz: Terminarz,
        zostaw_kolejke: Callable[[KolejkaTerminarza], bool],
        identyfikatory: set[int] | None,
    ) -> Terminarz:
        rundy: list[RundaTerminarza] = []
        for runda in terminarz.rundy:
            kolejki: list[KolejkaTerminarza] = []
            for kolejka in runda.kolejki:
                if not zostaw_kolejke(kolejka):
                    continue
                dni = self._dni(kolejka, identyfikatory)
                if dni:
                    kolejki.append(
                        KolejkaTerminarza(kolejka.id_kolejka, kolejka.nazwa, kolejka.nr, tuple(dni))
                    )
            if kolejki:
                rundy.append(RundaTerminarza(runda.id_runda, runda.nazwa, tuple(kolejki)))
        return Terminarz(terminarz.filtry, tuple(rundy))

    def _dni(
        self, kolejka: KolejkaTerminarza, identyfikatory: set[int] | None
    ) -> list[DzienTerminarza]:
        dni: list[DzienTerminarza] = []
        for dzien in kolejka.dni:
            mecze = dzien.mecze
            if identyfikatory is not None:
                mecze = tuple(pozycja for pozycja in mecze if pozycja.id_mecz in identyfikatory)
            if mecze:
                dni.append(DzienTerminarza(dzien.dzien, mecze))
        return dni
