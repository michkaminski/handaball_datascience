from dataclasses import dataclass


@dataclass(frozen=True)
class MeczAktualnosciViewModel:
    id_mecz: int
    dzien: str
    godzina: str
    gospodarz: str
    gosc: str
    wynik: str
    zwyciezca: str | None
    rozgrywki: str | None = None


@dataclass(frozen=True)
class StrzelecAktualnosciViewModel:
    pozycja: int
    id_zawodnik: int
    zawodnik: str
    druzyna: str
    mecze: int
    bramki: int
    srednia: str


@dataclass(frozen=True)
class SekcjaAktualnosciViewModel:
    klucz: str
    etykieta: str
    rozgrywki: str
    liczba_rozegranych: int
    srednia_bramek: str
    mecze: list[MeczAktualnosciViewModel]
    strzelcy: list[StrzelecAktualnosciViewModel]


@dataclass(frozen=True)
class CiekawostkaViewModel:
    tytul: str
    wartosc: str
    opis: str
    id_mecz: int | None = None
    id_zawodnik: int | None = None


@dataclass(frozen=True)
class AktualnosciViewModel:
    sezon: str | None
    id_sezon: int | None
    stan_danych: str
    liczba_rozegranych: int
    suma_bramek: int
    srednia_bramek: str
    sekcje: list[SekcjaAktualnosciViewModel]
    pozostale_mecze: list[MeczAktualnosciViewModel]
    ciekawostki: list[CiekawostkaViewModel]
