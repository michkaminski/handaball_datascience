from dataclasses import dataclass


@dataclass(frozen=True)
class SzczegolySedziegoViewModel:
    id_sedzia: int
    nazwa: str
    miasto: str
    pierwszy_mecz: str
    ostatni_mecz: str
    liczba_meczow: int
    liczba_sezonow: int
    liczba_rozgrywek: int
    liczba_druzyn: int


@dataclass(frozen=True)
class MeczSedziegoViewModel:
    id_mecz: int
    data: str
    sezon: str
    rozgrywki: str
    gospodarz: str
    wynik: str
    gosc: str
    partnerzy: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class StronaMeczowSedziegoViewModel:
    pozycje: list[MeczSedziegoViewModel]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int


@dataclass(frozen=True)
class PasekSedziegoViewModel:
    etykieta: str
    wartosc: int
    szerokosc: int


@dataclass(frozen=True)
class StatystykiSedziegoViewModel:
    liczba_meczow: int
    liczba_sezonow: int
    liczba_rozgrywek: int
    liczba_druzyn: int
    sezony: object
    rozgrywki: object
    sezon_rozgrywki: object
    druzyny: object
    partnerzy: object
    paski_sezonow: list[PasekSedziegoViewModel]
    paski_rozgrywek: list[PasekSedziegoViewModel]
    paski_druzyn: list[PasekSedziegoViewModel]
    paski_partnerow: list[PasekSedziegoViewModel]
