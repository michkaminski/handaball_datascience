from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FiltryMeczowSedziego:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    druzyna: str | None = None
    strona_meczu: str | None = None
    data_od: datetime | None = None
    data_do: datetime | None = None
    strona: int = 1
    rozmiar_strony: int = 20
    sortowanie: str = "-data"

    def __post_init__(self) -> None:
        if self.id_sezon is not None and self.id_sezon < 1:
            raise ValueError("Niepoprawny sezon.")
        if self.strona_meczu not in {None, "gospodarz", "gosc"}:
            raise ValueError("Niepoprawna strona meczu.")
        if self.strona_meczu and not self.druzyna:
            raise ValueError("Filtr strony wymaga podania drużyny.")
        if self.data_od and self.data_do and self.data_od > self.data_do:
            raise ValueError("Data od nie może być późniejsza niż data do.")
        if self.strona < 1 or not 1 <= self.rozmiar_strony <= 100:
            raise ValueError("Niepoprawny numer lub rozmiar strony.")
        if self.sortowanie not in {"data", "-data"}:
            raise ValueError("Niepoprawne sortowanie.")


@dataclass(frozen=True)
class SzczegolySedziego:
    id_sedzia: int
    nazwa: str | None
    miasto: str | None
    pierwszy_mecz: datetime | None
    ostatni_mecz: datetime | None
    liczba_meczow: int
    liczba_sezonow: int
    liczba_rozgrywek: int
    liczba_druzyn: int


@dataclass(frozen=True)
class MeczSedziego:
    id_mecz: int
    data: datetime | None
    sezon: str
    rozgrywki: str
    gospodarz: str | None
    wynik_gospodarza: int | None
    wynik_goscia: int | None
    gosc: str | None
    partnerzy: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class StronaMeczowSedziego:
    pozycje: list[MeczSedziego]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class AktywnoscSezonuSedziego:
    id_sezon: int
    sezon: str
    mecze: int
    rozgrywki: tuple[str, ...]


@dataclass(frozen=True)
class StatystykaRozgrywekSedziego:
    rozgrywki: str
    mecze: int


@dataclass(frozen=True)
class StatystykaSezonRozgrywkiSedziego:
    sezon: str
    rozgrywki: str
    mecze: int


@dataclass(frozen=True)
class StatystykaDruzynySedziego:
    id_zespol: int
    druzyna: str
    mecze: int
    jako_gospodarz: int
    jako_gosc: int


@dataclass(frozen=True)
class StatystykaPartneraSedziego:
    id_sedzia: int
    sedzia: str
    wspolne_mecze: int


@dataclass(frozen=True)
class StatystykiSedziego:
    liczba_meczow: int
    liczba_sezonow: int
    liczba_rozgrywek: int
    liczba_druzyn: int
    sezony: list[AktywnoscSezonuSedziego]
    rozgrywki: list[StatystykaRozgrywekSedziego]
    sezon_rozgrywki: list[StatystykaSezonRozgrywkiSedziego]
    druzyny: list[StatystykaDruzynySedziego]
    partnerzy: list[StatystykaPartneraSedziego]
