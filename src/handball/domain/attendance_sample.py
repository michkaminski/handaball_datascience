from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from handball.domain.attendance_calendar import PIERWSZY_DZIEN_WEEKENDU
from handball.domain.attendance_formatting import formatuj_calkowita

LIMIT_PROBKI = 8000


@dataclass(frozen=True)
class MeczProbki:
    id_mecz: int
    widzowie: int
    termin: datetime | None
    dzien_tygodnia: int | None
    godzina: int | None
    miesiac: int | None
    id_gospodarza: int | None
    id_goscia: int | None
    gospodarz: str
    gosc: str
    bramki_gospodarza: int | None
    bramki_goscia: int | None

    def __post_init__(self) -> None:
        if self.widzowie < 0:
            raise ValueError("widzowie nie mogą być ujemni")
        if self.dzien_tygodnia is not None and not 1 <= self.dzien_tygodnia <= 7:
            raise ValueError("dzień tygodnia musi mieścić się w przedziale 1–7")
        if self.godzina is not None and not 0 <= self.godzina <= 23:
            raise ValueError("godzina musi mieścić się w przedziale 0–23")
        if self.miesiac is not None and not 1 <= self.miesiac <= 12:
            raise ValueError("miesiąc musi mieścić się w przedziale 1–12")

    @property
    def roznica_bramek(self) -> int | None:
        if self.bramki_gospodarza is None or self.bramki_goscia is None:
            return None
        return self.bramki_gospodarza - self.bramki_goscia

    @property
    def suma_bramek(self) -> int | None:
        if self.bramki_gospodarza is None or self.bramki_goscia is None:
            return None
        return self.bramki_gospodarza + self.bramki_goscia

    @property
    def dzien(self) -> int | None:
        if self.dzien_tygodnia is not None:
            return self.dzien_tygodnia
        return self.termin.isoweekday() if self.termin is not None else None

    @property
    def numer_miesiaca(self) -> int | None:
        if self.miesiac is not None:
            return self.miesiac
        return self.termin.month if self.termin is not None else None

    @property
    def weekend(self) -> bool | None:
        dzien = self.dzien
        if dzien is None:
            return None
        return dzien >= PIERWSZY_DZIEN_WEEKENDU

    @property
    def widzowie_etykieta(self) -> str:
        return formatuj_calkowita(self.widzowie)

    @property
    def etykieta(self) -> str:
        return f"{self.gospodarz} – {self.gosc}"

    @property
    def data_etykieta(self) -> str:
        if self.termin is None:
            return "—"
        return self.termin.strftime("%Y-%m-%d")
