from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpcjaViewModel:
    wartosc: str
    etykieta: str


@dataclass(frozen=True)
class PozycjaPrognozyViewModel:
    id_mecz: int
    data: str
    sezon: str
    liga: str
    kolejka: str
    gospodarz: str
    gosc: str
    rating_gospodarza: str
    rating_goscia: str
    roznica_ratingow: str
    prognoza: str
    wynik: str
    prognoza_gospodarza: str
    bramki_gospodarza: str
    blad_gospodarza: str
    prognoza_goscia: str
    bramki_goscia: str
    blad_goscia: str
    prognoza_roznicy: str
    roznica: str
    blad_roznicy: str
    prognoza_sumy: str
    suma: str
    blad_sumy: str
    typ: str
    typ_rzeczywisty: str
    trafiony: bool
    trafiony_tekst: str
    blad_wyniku: str
    ocena: str
    klasa_oceny: str
    ocena_wyniku: str
    klasa_oceny_wyniku: str
    opis_oceny_wyniku: str
    poprawny_typ_prognozy: bool
    typ_prognozy: str
    ocena_typu_prognozy: str


@dataclass(frozen=True)
class PrognozaPrzyszlaViewModel:
    liga: str
    rating_gospodarza: str
    rating_goscia: str
    roznica_ratingow: str
    prognoza: str
    prognoza_gospodarza: str
    prognoza_goscia: str
    prognoza_roznicy: str
    prognoza_sumy: str
    typ: str
    typ_prognozy: str


@dataclass(frozen=True)
class StronaPrognozViewModel:
    pozycje: tuple[PozycjaPrognozyViewModel, ...]
    liczba_wszystkich: int
    strona: int
    rozmiar_strony: int

    @property
    def zakres_wierszy(self) -> str:
        if not self.pozycje:
            return f"0 z {self.liczba_wszystkich}"
        poczatek = (self.strona - 1) * self.rozmiar_strony + 1
        return f"{poczatek}–{poczatek + len(self.pozycje) - 1} z {self.liczba_wszystkich}"


@dataclass(frozen=True)
class WskaznikViewModel:
    etykieta: str
    wartosc: str
    opis: str | None = None


@dataclass(frozen=True)
class RaportPrognozViewModel:
    tytul_modelu: str
    wersja_modelu: str
    strona: StronaPrognozViewModel
    wskazniki: tuple[WskaznikViewModel, ...]
    progi: tuple[WskaznikViewModel, ...]
    zakres_raportu: str
    zakres_rozgrzewki: str
    sezon_w_toku: str | None
    wykluczenia: tuple[WskaznikViewModel, ...]
    parametry: tuple[WskaznikViewModel, ...]


@dataclass(frozen=True)
class KrokObliczeniaViewModel:
    kotwica: str
    tytul: str
    definicja: str
    wzor: str
    podstawienie: str
    wynik: str
    interpretacja: str


@dataclass(frozen=True)
class WierszRatinguViewModel:
    druzyna: str
    przed: str
    zmiana: str
    po: str
    klasa_zmiany: str


@dataclass(frozen=True)
class WierszHistoriiViewModel:
    id_mecz: int
    data: str
    sezon: str
    rywal: str
    miejsce: str
    wynik: str
    przed: str
    zmiana: str
    po: str
    klasa_zmiany: str


@dataclass(frozen=True)
class HistoriaDruzynyViewModel:
    druzyna: str
    wiersze: tuple[WierszHistoriiViewModel, ...]


@dataclass(frozen=True)
class DefinicjaPojeciaViewModel:
    pojecie: str
    opis: str


@dataclass(frozen=True)
class SzczegolyPrognozyViewModel:
    id_mecz: int
    tytul_modelu: str
    wersja_modelu: str
    naglowek: str
    kontekst: str
    zamiana: str | None
    okres: str
    wynik_prognozy: tuple[WskaznikViewModel, ...]
    trafiony: bool
    klasa_oceny: str
    klasa_oceny_wyniku: str
    bledy: tuple[WskaznikViewModel, ...]
    dane_wejsciowe: tuple[WskaznikViewModel, ...]
    uwagi_ratingow: tuple[str, ...]
    ostatnie_ewma: tuple[str, ...]
    kroki: tuple[KrokObliczeniaViewModel, ...]
    znaczenie_aktualizacji: tuple[str, ...]
    ratingi: tuple[WierszRatinguViewModel, ...]
    historia: tuple[HistoriaDruzynyViewModel, ...]
    parametry: str
    definicje: tuple[DefinicjaPojeciaViewModel, ...]


@dataclass(frozen=True)
class WskaznikZapowiedziViewModel:
    etykieta: str
    wartosc: str
    klasa: str = ""


@dataclass(frozen=True)
class PrognozaZapowiedziViewModel:
    tryb: str
    tytul_modelu: str
    wersja_modelu: str
    opis: str
    wskazniki: tuple[WskaznikZapowiedziViewModel, ...] = ()
    ratingi: tuple[WierszRatinguViewModel, ...] = ()
    uwagi: tuple[str, ...] = ()
    kroki: tuple[KrokObliczeniaViewModel, ...] = ()
    id_mecz_raportu: int | None = None

    @property
    def dostepna(self) -> bool:
        return self.tryb != "brak"
