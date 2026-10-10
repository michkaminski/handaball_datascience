from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from handball.domain.attendance_formatting import (
    PROG_MALEJ_PROBY,
    formatuj_calkowita,
    formatuj_opcjonalna_calkowita,
    formatuj_udzial,
    formatuj_zaokraglona,
)


@dataclass(frozen=True)
class AgregatFrekwencji:
    rozegrane: int
    znane: int
    suma: int
    maksimum: int | None

    def __post_init__(self) -> None:
        if self.rozegrane < 0 or self.znane < 0:
            raise ValueError("liczba meczów nie może być ujemna")
        if self.znane > self.rozegrane:
            raise ValueError("mecze ze znaną frekwencją nie mogą przekraczać rozegranych")

    @property
    def srednia(self) -> float | None:
        if self.znane == 0:
            return None
        return self.suma / self.znane

    @property
    def pokrycie(self) -> float | None:
        if self.rozegrane == 0:
            return None
        return self.znane / self.rozegrane

    @property
    def mala_proba(self) -> bool:
        return 0 < self.znane < PROG_MALEJ_PROBY

    @property
    def rozegrane_etykieta(self) -> str:
        return formatuj_calkowita(self.rozegrane)

    @property
    def znane_etykieta(self) -> str:
        return formatuj_calkowita(self.znane)

    @property
    def suma_etykieta(self) -> str:
        return formatuj_calkowita(self.suma)

    @property
    def srednia_etykieta(self) -> str:
        return formatuj_zaokraglona(self.srednia)

    @property
    def maksimum_etykieta(self) -> str:
        return formatuj_opcjonalna_calkowita(self.maksimum)

    @property
    def pokrycie_etykieta(self) -> str:
        return formatuj_udzial(self.pokrycie)


@dataclass(frozen=True)
class MiaryRozkladu:
    mediana: float | None = None
    dominanta: int | None = None
    minimum: int | None = None

    @property
    def mediana_etykieta(self) -> str:
        return formatuj_zaokraglona(self.mediana)

    @property
    def dominanta_etykieta(self) -> str:
        return formatuj_opcjonalna_calkowita(self.dominanta)

    @property
    def minimum_etykieta(self) -> str:
        return formatuj_opcjonalna_calkowita(self.minimum)


def polacz_agregaty(agregaty: Sequence[AgregatFrekwencji]) -> AgregatFrekwencji:
    maksima = [agregat.maksimum for agregat in agregaty if agregat.maksimum is not None]
    return AgregatFrekwencji(
        rozegrane=sum(agregat.rozegrane for agregat in agregaty),
        znane=sum(agregat.znane for agregat in agregaty),
        suma=sum(agregat.suma for agregat in agregaty),
        maksimum=max(maksima) if maksima else None,
    )
