from dataclasses import dataclass
from datetime import datetime

KLASY_DEFENSYWY = ("Bardzo mocna", "Mocna", "Przeciętna", "Słaba", "Bardzo słaba")


@dataclass(frozen=True)
class KonfiguracjaDefensywyRywala:
    k_shrinkage: float = 5.0
    w_poprzedni_sezon: float = 3.0
    uzyj_poprzedniego_sezonu: bool = False
    granica_bardzo_mocna: float = 0.90
    granica_mocna: float = 0.97
    granica_slaba: float = 1.03
    granica_bardzo_slaba: float = 1.10
    prog_malej_proby: int = 10
    progi_prawdopodobienstwa: tuple[int, ...] = (1, 3, 5, 8, 10)

    def __post_init__(self) -> None:
        if self.k_shrinkage < 0 or self.w_poprzedni_sezon < 0:
            raise ValueError("Wagi wygładzania nie mogą być ujemne.")
        granice = (
            self.granica_bardzo_mocna,
            self.granica_mocna,
            self.granica_slaba,
            self.granica_bardzo_slaba,
        )
        if list(granice) != sorted(granice):
            raise ValueError("Granice klas defensywy muszą rosnąć.")
        if self.prog_malej_proby < 1:
            raise ValueError("Próg małej próby musi być dodatni.")


@dataclass(frozen=True)
class FiltryDefensywyRywala:
    id_sezon: int | None = None
    rozgrywki: str | None = None
    liczba_ostatnich_sezonow: int | None = None
    miejsce: str | None = None
    tylko_pelne_dane: bool = True
    przeciwnik: str | None = None

    def __post_init__(self) -> None:
        if self.miejsce is not None and self.miejsce not in {"dom", "wyjazd"}:
            raise ValueError("Niepoprawne miejsce.")
        if self.liczba_ostatnich_sezonow is not None and self.liczba_ostatnich_sezonow < 1:
            raise ValueError("Niepoprawna liczba sezonów.")


@dataclass(frozen=True)
class WystapienieZDanymiLigowymi:
    id_mecz: int
    termin: datetime | None
    id_sezon: int
    sezon: str
    rok_rozpoczecia_sezonu: int | None
    id_rozgrywki: int
    rozgrywki: str
    id_zespol_zawodnika: int
    druzyna_zawodnika: str | None
    id_zespol_przeciwnika: int
    przeciwnik: str | None
    miejsce: str
    bramki_zawodnika: int | None
    wynik_druzyny_zawodnika: int | None
    wynik_przeciwnika: int | None
    dane_pelne: bool


@dataclass(frozen=True)
class MeczLigowy:
    id_rozgrywki: int
    id_zespol: int
    termin: datetime
    bramki_stracone: int


@dataclass(frozen=True)
class MeczZDefensywaRywala:
    id_mecz: int
    termin: datetime | None
    sezon: str
    rozgrywki: str
    druzyna_zawodnika: str | None
    przeciwnik: str | None
    miejsce: str
    bramki_zawodnika: int | None
    wynik_druzyny_zawodnika: int | None
    wynik_przeciwnika: int | None
    ga_team: float | None
    ga_previous: float | None
    ga_smoothed: float | None
    ga_league: float | None
    n_meczy_rywala: int
    defense_factor: float | None
    klasa_defensywy: str | None


@dataclass(frozen=True)
class StatystykiKlasyDefensywy:
    klasa: str
    n: int
    suma_bramek: int
    srednia: float | None
    mediana: float | None
    minimum: int | None
    maksimum: int | None
    kwartyl_pierwszy: float | None
    kwartyl_trzeci: float | None
    wariancja: float | None
    odchylenie_standardowe: float | None
    udzialy_progowe: tuple[tuple[int, float], ...]
    minimum_wewnetrzne: int | None
    maksimum_wewnetrzne: int | None
    wartosci_odstajace: tuple[int, ...]


@dataclass(frozen=True)
class WspolczynnikiKorelacji:
    r_pearson: float | None
    rho_spearman: float | None
    n: int


@dataclass(frozen=True)
class WynikRegresji:
    wyraz_wolny: float | None
    wspolczynnik_kierunkowy: float | None
    r_kwadrat: float | None
    przedzial_ufnosci_beta1: tuple[float, float] | None
    n: int


@dataclass(frozen=True)
class AnalizaDefensywyRywala:
    id_zawodnik: int
    mecze: tuple[MeczZDefensywaRywala, ...]
    klasy: tuple[StatystykiKlasyDefensywy, ...]
    korelacja: WspolczynnikiKorelacji
    regresja: WynikRegresji
    konfiguracja: KonfiguracjaDefensywyRywala
    liczba_wystapien: int
    liczba_meczow_ze_znanymi_bramkami: int
    liczba_meczow_z_defense_factor: int
