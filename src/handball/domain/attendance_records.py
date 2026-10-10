from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from handball.domain.attendance_formatting import formatuj_calkowita

LIMIT_REKORDOW_GRUPOWYCH = 30


@dataclass(frozen=True)
class RekordFrekwencji:
    id_mecz: int
    termin: datetime | None
    sezon: str
    rozgrywki: str
    gospodarz: str
    gosc: str
    bramki_gospodarza: int | None
    bramki_goscia: int | None
    hala: str | None
    widzowie: int

    @property
    def data_etykieta(self) -> str:
        if self.termin is None:
            return "—"
        return self.termin.strftime("%Y-%m-%d")

    @property
    def wynik_etykieta(self) -> str:
        if self.bramki_gospodarza is None or self.bramki_goscia is None:
            return "—"
        return f"{self.bramki_gospodarza}:{self.bramki_goscia}"

    @property
    def hala_etykieta(self) -> str:
        return self.hala or "—"

    @property
    def widzowie_etykieta(self) -> str:
        return formatuj_calkowita(self.widzowie)


@dataclass(frozen=True)
class RekordyRozszerzoneFrekwencji:
    sezony: tuple[RekordFrekwencji, ...] = ()
    kluby: tuple[RekordFrekwencji, ...] = ()
    hale: tuple[RekordFrekwencji, ...] = ()
    finaly: tuple[RekordFrekwencji, ...] = ()
    pary: tuple[RekordFrekwencji, ...] = ()

    @property
    def ma_dane(self) -> bool:
        return any((self.sezony, self.kluby, self.hale, self.finaly, self.pary))
