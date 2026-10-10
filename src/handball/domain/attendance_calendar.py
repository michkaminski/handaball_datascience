from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from handball.domain.attendance_aggregate import AgregatFrekwencji, polacz_agregaty

NAZWY_MIESIECY = (
    "styczeń",
    "luty",
    "marzec",
    "kwiecień",
    "maj",
    "czerwiec",
    "lipiec",
    "sierpień",
    "wrzesień",
    "październik",
    "listopad",
    "grudzień",
)
NAZWY_DNI = (
    "poniedziałek",
    "wtorek",
    "środa",
    "czwartek",
    "piątek",
    "sobota",
    "niedziela",
)
PIERWSZY_DZIEN_WEEKENDU = 6
LIMIT_FAZ = 40
UWAGA_O_KALENDARZU = (
    "Terminy to COALESCE(data_faktyczna, data_propozycji) zapisane jako czas lokalny "
    "Europe/Warsaw. Mecze bez terminu są pominięte, a godzina 00:00 oznacza brak godziny "
    "i nie wchodzi do rozkładu godzin ani mapy cieplnej."
)


def nazwa_dnia(dzien: int) -> str:
    return NAZWY_DNI[dzien - 1]


def nazwa_miesiaca(miesiac: int) -> str:
    return NAZWY_MIESIECY[miesiac - 1]


def etykieta_godziny(godzina: int) -> str:
    return f"{godzina:02d}:00"


@dataclass(frozen=True)
class WierszKalendarza(AgregatFrekwencji):
    klucz: int | str


@dataclass(frozen=True)
class KomorkaKalendarza(AgregatFrekwencji):
    dzien: int
    godzina: int


@dataclass(frozen=True)
class DaneKalendarza:
    miesiace: tuple[WierszKalendarza, ...] = ()
    dni: tuple[WierszKalendarza, ...] = ()
    godziny: tuple[WierszKalendarza, ...] = ()
    rundy: tuple[WierszKalendarza, ...] = ()
    komorki: tuple[KomorkaKalendarza, ...] = ()


@dataclass(frozen=True)
class GrupaKalendarza(AgregatFrekwencji):
    klucz: int | str
    etykieta: str


@dataclass(frozen=True)
class HeatmapaFrekwencji:
    dni: tuple[str, ...]
    godziny: tuple[int, ...]
    komorki: tuple[KomorkaKalendarza, ...]

    @property
    def ma_dane(self) -> bool:
        return any(komorka.srednia is not None for komorka in self.komorki)

    @property
    def etykiety_godzin(self) -> tuple[str, ...]:
        return tuple(etykieta_godziny(godzina) for godzina in self.godziny)

    def komorka(self, dzien: int, godzina: int) -> KomorkaKalendarza | None:
        for kandydat in self.komorki:
            if kandydat.dzien == dzien and kandydat.godzina == godzina:
                return kandydat
        return None


@dataclass(frozen=True)
class KalendarzFrekwencji:
    miesiace: tuple[GrupaKalendarza, ...]
    dni_tygodnia: tuple[GrupaKalendarza, ...]
    godziny: tuple[GrupaKalendarza, ...]
    weekend: tuple[GrupaKalendarza, ...]
    rundy: tuple[GrupaKalendarza, ...]
    heatmapa: HeatmapaFrekwencji

    @property
    def ma_dane(self) -> bool:
        return any((self.miesiace, self.dni_tygodnia, self.godziny, self.rundy))

    @property
    def uwaga(self) -> str:
        return UWAGA_O_KALENDARZU


class KalendarzFrekwencjiCalculator:
    def zbuduj(self, dane: DaneKalendarza) -> KalendarzFrekwencji:
        dni = self._grupy(dane.dni, lambda klucz: nazwa_dnia(int(klucz)))
        return KalendarzFrekwencji(
            miesiace=self._grupy(dane.miesiace, lambda klucz: nazwa_miesiaca(int(klucz))),
            dni_tygodnia=dni,
            godziny=self._grupy(dane.godziny, lambda klucz: etykieta_godziny(int(klucz))),
            weekend=self._weekend(dni),
            rundy=self._grupy(dane.rundy, str)[:LIMIT_FAZ],
            heatmapa=self._heatmapa(dane.komorki),
        )

    def _grupy(
        self, wiersze: Sequence[WierszKalendarza], nazwij: Callable[[int | str], str]
    ) -> tuple[GrupaKalendarza, ...]:
        return tuple(self._grupa(wiersz, wiersz.klucz, nazwij(wiersz.klucz)) for wiersz in wiersze)

    def _weekend(self, dni: Sequence[GrupaKalendarza]) -> tuple[GrupaKalendarza, ...]:
        robocze = [dzien for dzien in dni if int(dzien.klucz) < PIERWSZY_DZIEN_WEEKENDU]
        weekendowe = [dzien for dzien in dni if int(dzien.klucz) >= PIERWSZY_DZIEN_WEEKENDU]
        czesci = (("roboczy", "dzień roboczy", robocze), ("weekend", "weekend", weekendowe))
        return tuple(
            self._grupa(polacz_agregaty(czesc), klucz, etykieta)
            for klucz, etykieta, czesc in czesci
            if czesc
        )

    @staticmethod
    def _grupa(agregat: AgregatFrekwencji, klucz: int | str, etykieta: str) -> GrupaKalendarza:
        return GrupaKalendarza(
            rozegrane=agregat.rozegrane,
            znane=agregat.znane,
            suma=agregat.suma,
            maksimum=agregat.maksimum,
            klucz=klucz,
            etykieta=etykieta,
        )

    def _heatmapa(self, komorki: Sequence[KomorkaKalendarza]) -> HeatmapaFrekwencji:
        godziny = tuple(sorted({komorka.godzina for komorka in komorki}))
        uporzadkowane = tuple(sorted(komorki, key=lambda komorka: (komorka.dzien, komorka.godzina)))
        return HeatmapaFrekwencji(dni=NAZWY_DNI, godziny=godziny, komorki=uporzadkowane)
