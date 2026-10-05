from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ZawodnikProtokoluViewModel:
    numer: str
    nazwa: str
    nowa_grupa: bool = False
    pozycja: str = ""
    rocznik: str = ""
    mecze: str = ""
    bramki: str = ""
    srednia: str = ""
    wyroznij_bramki: bool = False


@dataclass(frozen=True)
class DruzynaProtokoluViewModel:
    litera: str
    druzyna: str
    zawodnicy: tuple[ZawodnikProtokoluViewModel, ...]
    ze_skladu: bool = False


@dataclass(frozen=True)
class SedziaProtokoluViewModel:
    funkcja: str
    nazwisko: str
    miasto: str


@dataclass(frozen=True)
class UkladProtokoluViewModel:
    wysokosc_zawodnika_mm: float
    czcionka_zawodnika_pt: float
    wiersze_przebiegu: int


@dataclass(frozen=True)
class ProtokolMeczuViewModel:
    id_mecz: int
    gospodarz: str
    gosc: str
    rozgrywki: str
    sezon: str
    etap: str
    data: str
    godzina: str
    hala: str
    adres: str
    pojemnosc: str
    stan_na: str
    druzyny: tuple[DruzynaProtokoluViewModel, ...]
    sedziowie: tuple[SedziaProtokoluViewModel, ...]
    uklad: UkladProtokoluViewModel
