from dataclasses import dataclass


@dataclass(frozen=True)
class WierszPorownaniaViewModel:
    etykieta: str
    gospodarz: str
    gosc: str
    udzial_gospodarza: int | None = None
    przewaga: str | None = None


@dataclass(frozen=True)
class StrzelecMeczuViewModel:
    zawodnik: str
    bramki: str
    karne: str


@dataclass(frozen=True)
class MeczFormyViewModel:
    id_mecz: int
    rezultat: str
    klasa: str
    wynik: str
    dopisek: str
    rywal: str
    data: str
    miejsce: str
    rozgrywki: str
    analizowany: bool


@dataclass(frozen=True)
class FormaDruzynyViewModel:
    mecze: list[MeczFormyViewModel]
    bilans: str
    bramki: str


@dataclass(frozen=True)
class StatystykiMeczuViewModel:
    rozegrany: bool
    wnioski: list[str]
    porownanie: list[WierszPorownaniaViewModel]
    strzelcy_gospodarz: list[StrzelecMeczuViewModel]
    strzelcy_gosc: list[StrzelecMeczuViewModel]
    forma_gospodarz: FormaDruzynyViewModel | None
    forma_gosc: FormaDruzynyViewModel | None
    limit_formy: int
