from __future__ import annotations

from dataclasses import dataclass

from handball.interface.view_models.match_predictions import PrognozaZapowiedziViewModel


@dataclass(frozen=True)
class MeczTerminarzaViewModel:
    id_mecz: int
    godzina: str
    gospodarz: str
    gosc: str
    wynik: str
    dopisek: str | None
    status: str
    etykieta_statusu: str
    hala: str
    termin_proponowany: bool


@dataclass(frozen=True)
class DzienTerminarzaViewModel:
    data: str
    mecze: tuple[MeczTerminarzaViewModel, ...]


@dataclass(frozen=True)
class KolejkaTerminarzaViewModel:
    id_kolejka: int | None
    nazwa: str
    zakres_dat: str
    liczba_meczow: int
    liczba_zakonczonych: int
    dni: tuple[DzienTerminarzaViewModel, ...]


@dataclass(frozen=True)
class RundaTerminarzaViewModel:
    nazwa: str
    kolejki: tuple[KolejkaTerminarzaViewModel, ...]


@dataclass(frozen=True)
class TerminarzViewModel:
    liczba_meczow: int
    rundy: tuple[RundaTerminarzaViewModel, ...]


@dataclass(frozen=True)
class WierszPorownaniaViewModel:
    etykieta: str
    gospodarz: str
    gosc: str
    przewaga: str = ""


@dataclass(frozen=True)
class ZnakFormyViewModel:
    litera: str
    klasa: str
    opis: str


@dataclass(frozen=True)
class WierszWystepuViewModel:
    id_mecz: int
    data: str
    rozgrywki: str
    rywal: str
    miejsce: str
    wynik: str
    rezultat: str
    klasa: str


@dataclass(frozen=True)
class FormaDruzynyViewModel:
    druzyna: str
    znaki: tuple[ZnakFormyViewModel, ...]
    wiersze: tuple[WierszWystepuViewModel, ...]


@dataclass(frozen=True)
class ZawodnikKadryViewModel:
    id_zawodnik: int
    numer: str
    nazwa: str
    pozycja: str
    mecze: str
    bramki: str
    srednia: str
    poprzedni: str
    poprzedni_mecze: str
    uwagi_poprzednie: tuple[str, ...] = ()
    miejsce_strzelca: int | None = None
    data_urodzenia: str | None = None


@dataclass(frozen=True)
class GrupaKadryViewModel:
    nazwa: str
    zawodnicy: tuple[ZawodnikKadryViewModel, ...]


@dataclass(frozen=True)
class KadraDruzynyViewModel:
    druzyna: str
    liczba_zawodnikow: int
    grupy: tuple[GrupaKadryViewModel, ...]
    ze_skladu: bool = False

    @property
    def najlepsi_strzelcy(self) -> tuple[ZawodnikKadryViewModel, ...]:
        strzelcy = [
            zawodnik
            for grupa in self.grupy
            for zawodnik in grupa.zawodnicy
            if zawodnik.miejsce_strzelca is not None
        ]
        return tuple(sorted(strzelcy, key=lambda zawodnik: zawodnik.miejsce_strzelca or 0))


@dataclass(frozen=True)
class BezposrednieMeczeViewModel:
    liczba: int
    wygrane_gospodarza: int
    remisy: int
    wygrane_goscia: int
    bramki: str
    okres: str
    wiersze: tuple[WierszWystepuViewModel, ...]


@dataclass(frozen=True)
class ZapowiedzMeczuViewModel:
    id_mecz: int
    gospodarz: str
    gosc: str
    id_gospodarza: int | None
    id_goscia: int | None
    termin: str
    hala: str
    kontekst: str
    status: str
    etykieta_statusu: str
    wynik: str | None
    stan_na: str
    zamiana: bool
    porownanie: tuple[WierszPorownaniaViewModel, ...]
    formy: tuple[FormaDruzynyViewModel, ...]
    bezposrednie: BezposrednieMeczeViewModel
    kadry: tuple[KadraDruzynyViewModel, ...]
    sezon: str
    sezon_poprzedni: str | None
    kadra_z_poprzednim: bool
    lata_bezposrednich: str
    prognoza: PrognozaZapowiedziViewModel
