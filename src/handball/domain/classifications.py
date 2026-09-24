from dataclasses import dataclass
from decimal import Decimal
from typing import TypeVar


@dataclass(frozen=True)
class FiltryKlasyfikacji:
    szukaj: str | None = None
    id_sezon: int | None = None
    id_rozgrywki: int | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "sezon"


@dataclass(frozen=True)
class PozycjaSkladu:
    id_zawodnik: int
    sezon: str
    druzyna: str | None
    zawodnik: str
    nr_koszulki: int | None
    pozycja: str | None
    wzrost: Decimal | None
    waga: Decimal | None


@dataclass(frozen=True)
class Sklad:
    id_zespol_sezon: int
    sezon: str
    druzyna: str | None
    rozgrywki: str | None


@dataclass(frozen=True)
class SzczegolySkladu:
    sklad: Sklad
    zawodnicy: list[PozycjaSkladu]


@dataclass(frozen=True)
class PozycjaStrzelca:
    id: int
    id_zawodnik: int
    sezon: str
    rozgrywki: str
    zawodnik: str
    druzyna: str | None
    miejsce: int | None
    mecze: int | None
    bramki: int | None
    srednia: Decimal | None
    karne_bramki: int | None
    karne_liczba: int | None
    karne_skutecznosc: Decimal | None
    dwie_minuty: int | None


@dataclass(frozen=True)
class PozycjaTabeli:
    id: int
    sezon: str
    rozgrywki: str
    tabela: str | None
    grupa: str | None
    id_zespol: int
    druzyna: str | None
    miejsce: int | None
    mecze: int | None
    zwyciestwa: int | None
    remisy: int | None
    remis_wygrane: int | None
    remis_przegrane: int | None
    przegrane: int | None
    bramki_zdobyte: int | None
    bramki_stracone: int | None
    punkty: int | None
    punkty_bonusowe: int | None


@dataclass(frozen=True)
class Klasyfikacja:
    id_tabela_grupa: int
    sezon: str
    rozgrywki: str
    tabela: str | None
    grupa: str | None


@dataclass(frozen=True)
class SzczegolyTabeli:
    tabela: Klasyfikacja
    pozycje: list[PozycjaTabeli]

    @property
    def ma_punkty_bonusowe(self) -> bool:
        return any(pozycja.punkty_bonusowe is not None for pozycja in self.pozycje)


T = TypeVar("T")


@dataclass(frozen=True)
class StronaKlasyfikacji[T]:
    pozycje: list[T]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int
