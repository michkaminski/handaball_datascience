from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

DOZWOLONE_PLCI = frozenset({"M", "K"})


def _calkowita(wartosc: int) -> str:
    return f"{wartosc:,}".replace(",", " ")


def _ulamek(wartosc: float | None) -> str:
    if wartosc is None:
        return "—"
    return f"{wartosc:.1f}"


def _procent(udzial: float) -> str:
    return f"{udzial * 100:.1f}%"


@dataclass(frozen=True)
class FiltryRozkladuBramek:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    plec: str | None = None

    def __post_init__(self) -> None:
        if self.plec is not None and self.plec not in DOZWOLONE_PLCI:
            raise ValueError("nieobsługiwana płeć")


@dataclass(frozen=True)
class OpcjaFiltrow:
    wartosc: str
    etykieta: str


@dataclass(frozen=True)
class OpcjeFiltrowRozkladu:
    sezony: tuple[OpcjaFiltrow, ...]
    rozgrywki: tuple[OpcjaFiltrow, ...]


@dataclass(frozen=True)
class LiniaWyniku:
    gospodarz: int
    gosc: int
    mecze: int

    def __post_init__(self) -> None:
        if self.mecze < 1:
            raise ValueError("liczba meczów musi być dodatnia")
        if self.gospodarz < 0 or self.gosc < 0:
            raise ValueError("liczba bramek nie może być ujemna")


@dataclass(frozen=True)
class PozycjaRozkladu:
    bramki: int
    mecze: int
    udzial: float
    narastajaco: float
    szerokosc: float
    czy_dominanta: bool

    @property
    def mecze_etykieta(self) -> str:
        return _calkowita(self.mecze)

    @property
    def udzial_etykieta(self) -> str:
        return _procent(self.udzial)

    @property
    def narastajaco_etykieta(self) -> str:
        return _procent(self.narastajaco)


@dataclass(frozen=True)
class SeriaRozkladu:
    liczba_meczow: int
    srednia: float | None
    mediana: float | None
    dominanty: tuple[int, ...]
    minimum: int | None
    maksimum: int | None
    pozycje: tuple[PozycjaRozkladu, ...]

    @property
    def liczba_meczow_etykieta(self) -> str:
        return _calkowita(self.liczba_meczow)

    @property
    def srednia_etykieta(self) -> str:
        return _ulamek(self.srednia)

    @property
    def mediana_etykieta(self) -> str:
        return _ulamek(self.mediana)

    @property
    def dominanty_etykieta(self) -> str:
        if not self.dominanty:
            return "—"
        return ", ".join(str(wartosc) for wartosc in self.dominanty)

    @property
    def zakres_etykieta(self) -> str:
        if self.minimum is None or self.maksimum is None:
            return "—"
        return f"{self.minimum}–{self.maksimum}"


@dataclass(frozen=True)
class RaportRozkladuBramek:
    filtry: FiltryRozkladuBramek
    suma: SeriaRozkladu
    gospodarze: SeriaRozkladu
    goscie: SeriaRozkladu


class RodzajSerii(StrEnum):
    SUMA = "suma"
    GOSPODARZE = "gospodarze"
    GOSCIE = "goscie"


@dataclass(frozen=True)
class MeczRozkladu:
    id_mecz: int
    termin: datetime | None
    sezon: str
    rozgrywki: str
    gospodarz: str
    gosc: str
    bramki_gospodarza: int
    bramki_goscia: int

    @property
    def data_etykieta(self) -> str:
        if self.termin is None:
            return "—"
        if self.termin.hour or self.termin.minute:
            return self.termin.strftime("%Y-%m-%d %H:%M")
        return self.termin.strftime("%Y-%m-%d")

    @property
    def wynik_etykieta(self) -> str:
        return f"{self.bramki_gospodarza}:{self.bramki_goscia}"


def rodzaj_serii(tekst: str | None) -> RodzajSerii:
    try:
        return RodzajSerii(tekst or "")
    except ValueError as wyjatek:
        raise ValueError("nieobsługiwana seria") from wyjatek


def sprawdz_liczbe_bramek(bramki: int) -> int:
    if bramki < 0:
        raise ValueError("liczba bramek nie może być ujemna")
    return bramki


def zbuduj_serie(liczniki: Mapping[int, int]) -> SeriaRozkladu:
    czyste = {int(bramki): int(mecze) for bramki, mecze in liczniki.items() if mecze > 0}
    liczba = sum(czyste.values())
    if liczba == 0:
        return SeriaRozkladu(0, None, None, (), None, None, ())
    najczesciej = max(czyste.values())
    dominanty = (
        tuple(sorted(bramki for bramki, mecze in czyste.items() if mecze == najczesciej))
        if najczesciej > 1
        else ()
    )
    zbior_dominant = set(dominanty)
    minimum = min(czyste)
    maksimum = max(czyste)
    pozycje: list[PozycjaRozkladu] = []
    narastajaco = 0
    for bramki in range(minimum, maksimum + 1):
        mecze = czyste.get(bramki, 0)
        narastajaco += mecze
        pozycje.append(
            PozycjaRozkladu(
                bramki=bramki,
                mecze=mecze,
                udzial=mecze / liczba,
                narastajaco=narastajaco / liczba,
                szerokosc=100 * mecze / najczesciej,
                czy_dominanta=bramki in zbior_dominant,
            )
        )
    return SeriaRozkladu(
        liczba_meczow=liczba,
        srednia=sum(bramki * mecze for bramki, mecze in czyste.items()) / liczba,
        mediana=_mediana(czyste, liczba),
        dominanty=dominanty,
        minimum=minimum,
        maksimum=maksimum,
        pozycje=tuple(pozycje),
    )


def serie_z_wynikow(
    wyniki: Sequence[LiniaWyniku],
) -> tuple[SeriaRozkladu, SeriaRozkladu, SeriaRozkladu]:
    sumy: dict[int, int] = {}
    gospodarze: dict[int, int] = {}
    goscie: dict[int, int] = {}
    for wynik in wyniki:
        _dodaj(sumy, wynik.gospodarz + wynik.gosc, wynik.mecze)
        _dodaj(gospodarze, wynik.gospodarz, wynik.mecze)
        _dodaj(goscie, wynik.gosc, wynik.mecze)
    return zbuduj_serie(sumy), zbuduj_serie(gospodarze), zbuduj_serie(goscie)


def _dodaj(liczniki: dict[int, int], bramki: int, mecze: int) -> None:
    liczniki[bramki] = liczniki.get(bramki, 0) + mecze


def _mediana(liczniki: Mapping[int, int], liczba: int) -> float:
    if liczba % 2 == 1:
        pozostale = [liczba // 2 + 1]
    else:
        pozostale = [liczba // 2, liczba // 2 + 1]
    znalezione: list[int] = []
    przebyte = 0
    for bramki in sorted(liczniki):
        przebyte += liczniki[bramki]
        while pozostale and przebyte >= pozostale[0]:
            znalezione.append(bramki)
            pozostale.pop(0)
        if not pozostale:
            break
    return sum(znalezione) / len(znalezione)
