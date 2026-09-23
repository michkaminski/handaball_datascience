from dataclasses import dataclass


@dataclass(frozen=True)
class KlasaKartaViewModel:
    klasa: str
    srednia: str
    n: str


@dataclass(frozen=True)
class DefensywaRywalaKartaViewModel:
    id_zawodnik: int
    liczba_meczow: str
    klasy: list[KlasaKartaViewModel]
    wykres: list[dict[str, str | float | int]]
    ma_wystarczajaco_danych: bool


@dataclass(frozen=True)
class KlasaSzczegolyViewModel:
    klasa: str
    n: str
    suma_bramek: str
    srednia: str
    mediana: str
    minimum: str
    maksimum: str
    kwartyl_pierwszy: str
    kwartyl_trzeci: str
    wariancja: str
    odchylenie_standardowe: str
    mala_proba: bool
    udzialy_progowe: list[dict[str, str]]


@dataclass(frozen=True)
class KrokPrzykladuViewModel:
    opis: str
    wartosc: str


@dataclass(frozen=True)
class PrzykladMeczuViewModel:
    id_mecz: int
    etykieta: str
    kroki: list[KrokPrzykladuViewModel]


@dataclass(frozen=True)
class DefensywaRywalaSzczegolyViewModel:
    id_zawodnik: int
    nazwa_zawodnika: str
    liczba_meczow: str
    liczba_ze_znanymi_bramkami: str
    liczba_z_defense_factor: str
    zakres_sezonow: str
    zakres_rozgrywek: str
    opis_filtrow: str
    mala_proba_ostrzezenie: bool
    klasy: list[KlasaSzczegolyViewModel]
    wykres_klas: list[dict[str, str | float | int | None]]
    wykres_prawdopodobienstw: list[dict[str, object]]
    mecze: list[dict[str, str | int | float | None]]
    punkty_scatter: list[dict[str, str | int | float | None]]
    boxplot_klas: list[dict[str, object]]
    r_pearson: str
    interpretacja_pearson: str
    rho_spearman: str
    roznica_pearson_spearman: str
    wyraz_wolny: str
    wspolczynnik_kierunkowy: str
    r_kwadrat: str
    przedzial_ufnosci: str
    delta_10: str
    konfiguracja: dict[str, str]
    poprzedni_sezon_uzyty: bool
    przyklad: PrzykladMeczuViewModel | None
    opcje_przykladu: list[dict[str, str]]
    interpretacja_koncowa: str
    komentarz_automatyczny: str
