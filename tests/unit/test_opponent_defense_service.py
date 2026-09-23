from datetime import datetime

import pytest

from handball.domain.opponent_defense import (
    FiltryDefensywyRywala,
    KonfiguracjaDefensywyRywala,
    MeczLigowy,
    WystapienieZDanymiLigowymi,
)
from handball.services.opponent_defense_service import (
    DefensywaRywalaService,
    klasyfikuj_defense_factor,
    pearson,
    regresja_liniowa,
    spearman,
)

ROZGRYWKI = 1
SEZON = 195
OPPONENT = 501
INNI_RYWALE = (601, 602, 603, 604, 605)


class DefensywaRepozytoriumTestowe:
    def __init__(
        self,
        wystapienia: tuple[WystapienieZDanymiLigowymi, ...],
        mecze_ligowe: tuple[MeczLigowy, ...] = (),
        poprzednie_rozgrywki: dict[int, int] | None = None,
        mecze_ligowe_poprzednie: tuple[MeczLigowy, ...] = (),
        zespoly_o_nazwie: dict[str, frozenset[int]] | None = None,
    ) -> None:
        self.wystapienia = wystapienia
        self.mecze_ligowe = mecze_ligowe
        self.poprzednie_rozgrywki = poprzednie_rozgrywki or {}
        self.mecze_ligowe_poprzednie = mecze_ligowe_poprzednie
        self.zespoly_o_nazwie = zespoly_o_nazwie or {}

    def pobierz_wystapienia(self, id_zawodnik: int) -> tuple[WystapienieZDanymiLigowymi, ...]:
        return self.wystapienia

    def pobierz_mecze_ligowe(
        self, identyfikatory_rozgrywek: frozenset[int]
    ) -> tuple[MeczLigowy, ...]:
        wynik = tuple(m for m in self.mecze_ligowe if m.id_rozgrywki in identyfikatory_rozgrywek)
        wynik += tuple(
            m for m in self.mecze_ligowe_poprzednie if m.id_rozgrywki in identyfikatory_rozgrywek
        )
        return wynik

    def pobierz_poprzednie_rozgrywki(
        self, rozgrywki_do_sprawdzenia: frozenset[tuple[int, str, int]]
    ) -> dict[int, int]:
        return self.poprzednie_rozgrywki

    def pobierz_zespoly_o_nazwie(self, fraza: str) -> frozenset[int]:
        return self.zespoly_o_nazwie.get(fraza, frozenset())


def _wystapienie(
    id_mecz: int,
    termin: datetime,
    bramki: int | None,
    id_zespol_przeciwnika: int = OPPONENT,
    id_rozgrywki: int = ROZGRYWKI,
    id_sezon: int = SEZON,
    sezon: str = "2025/2026",
    rok: int = 2025,
    miejsce: str = "dom",
    dane_pelne: bool = True,
) -> WystapienieZDanymiLigowymi:
    return WystapienieZDanymiLigowymi(
        id_mecz=id_mecz,
        termin=termin,
        id_sezon=id_sezon,
        sezon=sezon,
        rok_rozpoczecia_sezonu=rok,
        id_rozgrywki=id_rozgrywki,
        rozgrywki="Liga",
        id_zespol_zawodnika=1,
        druzyna_zawodnika="Nasza Drużyna",
        id_zespol_przeciwnika=id_zespol_przeciwnika,
        przeciwnik="Rywal",
        miejsce=miejsce,
        bramki_zawodnika=bramki,
        wynik_druzyny_zawodnika=25,
        wynik_przeciwnika=25,
        dane_pelne=dane_pelne,
    )


def _mecz_ligowy(id_zespol: int, dzien: int, bramki_stracone: int) -> MeczLigowy:
    return MeczLigowy(ROZGRYWKI, id_zespol, datetime(2025, 9, dzien), bramki_stracone)


def test_klasyfikacja_pieciu_klas_wedlug_granic() -> None:
    cfg = KonfiguracjaDefensywyRywala()
    assert klasyfikuj_defense_factor(0.85, cfg) == "Bardzo mocna"
    assert klasyfikuj_defense_factor(0.90, cfg) == "Mocna"
    assert klasyfikuj_defense_factor(0.96, cfg) == "Mocna"
    assert klasyfikuj_defense_factor(0.97, cfg) == "Przeciętna"
    assert klasyfikuj_defense_factor(1.03, cfg) == "Przeciętna"
    assert klasyfikuj_defense_factor(1.031, cfg) == "Słaba"
    assert klasyfikuj_defense_factor(1.10, cfg) == "Słaba"
    assert klasyfikuj_defense_factor(1.11, cfg) == "Bardzo słaba"


def test_konfiguracja_wymaga_rosnacych_granic() -> None:
    with pytest.raises(ValueError):
        KonfiguracjaDefensywyRywala(granica_mocna=0.5, granica_bardzo_mocna=0.9)


def test_pearson_i_spearman_na_znanym_przykladzie() -> None:
    pary = [(1.0, 2.0), (2.0, 4.0), (3.0, 5.0), (4.0, 4.0), (5.0, 5.0)]
    r = pearson(pary)
    rho = spearman(pary)
    assert r is not None and 0.7 < r < 0.9
    assert rho is not None and 0.5 < rho < 1.0


def test_pearson_brak_zaleznosci_gdy_stala_wartosc_x() -> None:
    assert pearson([(1.0, 2.0), (1.0, 3.0), (1.0, 4.0)]) is None


def test_regresja_liniowa_na_prostej_zaleznosci() -> None:
    pary = [(0.8, 1.0), (0.9, 2.0), (1.0, 3.0), (1.1, 4.0), (1.2, 5.0)]
    wynik = regresja_liniowa(pary)
    assert wynik.wspolczynnik_kierunkowy == pytest.approx(10.0)
    assert wynik.wyraz_wolny == pytest.approx(-7.0)
    assert wynik.r_kwadrat == pytest.approx(1.0)
    assert wynik.n == 5
    assert wynik.przedzial_ufnosci_beta1 is not None


def test_regresja_zbyt_mala_proba_zwraca_none() -> None:
    wynik = regresja_liniowa([(1.0, 2.0)])
    assert wynik.wspolczynnik_kierunkowy is None
    assert wynik.n == 1


def test_ga_team_i_shrinkage_z_przykladu_specyfikacji() -> None:
    mecze_ligowe = tuple(_mecz_ligowy(OPPONENT, dzien, 31) for dzien in range(1, 9)) + tuple(
        _mecz_ligowy(rywal, 1, 30) for rywal in INNI_RYWALE
    )
    wystapienia = (_wystapienie(900, datetime(2025, 9, 20), bramki=7),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe)
    wynik = DefensywaRywalaService(repo).pobierz_analize(
        7, FiltryDefensywyRywala(), KonfiguracjaDefensywyRywala(k_shrinkage=5)
    )
    mecz = wynik.mecze[0]
    assert mecz.ga_team == pytest.approx(31.0)
    assert mecz.n_meczy_rywala == 8


def test_shrinkage_male_n_przesuwa_w_strone_sredniej_ligi() -> None:
    mecze_ligowe = tuple(_mecz_ligowy(OPPONENT, d, 35) for d in (1, 2)) + tuple(
        _mecz_ligowy(rywal, d, 30) for rywal in INNI_RYWALE for d in (1, 2, 3)
    )
    wystapienia = (_wystapienie(901, datetime(2025, 9, 20), bramki=5),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe)
    wynik = DefensywaRywalaService(repo).pobierz_analize(
        7, FiltryDefensywyRywala(), KonfiguracjaDefensywyRywala(k_shrinkage=5)
    )
    mecz = wynik.mecze[0]
    ga_league_oczekiwane = (2 * 35 + len(INNI_RYWALE) * 3 * 30) / (2 + len(INNI_RYWALE) * 3)
    ga_smoothed_oczekiwane = (2 * 35 + 5 * ga_league_oczekiwane) / (2 + 5)
    assert mecz.ga_team == pytest.approx(35.0)
    assert mecz.ga_league == pytest.approx(ga_league_oczekiwane)
    assert mecz.ga_smoothed == pytest.approx(ga_smoothed_oczekiwane)
    assert mecz.ga_smoothed is not None
    assert ga_league_oczekiwane < mecz.ga_smoothed < 35.0


def test_pierwszy_mecz_sezonu_n_zero_daje_defense_factor_neutralny() -> None:
    mecze_ligowe = tuple(_mecz_ligowy(rywal, 1, 30) for rywal in INNI_RYWALE)
    wystapienia = (_wystapienie(902, datetime(2025, 9, 20), bramki=6),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe)
    wynik = DefensywaRywalaService(repo).pobierz_analize(7, FiltryDefensywyRywala())
    mecz = wynik.mecze[0]
    assert mecz.n_meczy_rywala == 0
    assert mecz.ga_team is None
    assert mecz.ga_smoothed == pytest.approx(30.0)
    assert mecz.defense_factor == pytest.approx(1.0)
    assert mecz.klasa_defensywy == "Przeciętna"


def test_brak_wczesniejszych_meczow_w_rozgrywkach_daje_brak_defense_factor() -> None:
    wystapienia = (_wystapienie(903, datetime(2025, 9, 20), bramki=4),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe=())
    wynik = DefensywaRywalaService(repo).pobierz_analize(7, FiltryDefensywyRywala())
    mecz = wynik.mecze[0]
    assert mecz.ga_league is None
    assert mecz.ga_smoothed is None
    assert mecz.defense_factor is None
    assert mecz.klasa_defensywy is None


def test_defense_factor_przyklady_liczbowe() -> None:
    mecze_ligowe = (
        _mecz_ligowy(OPPONENT, 1, 27),
        _mecz_ligowy(601, 1, 30),
        _mecz_ligowy(601, 2, 30),
        _mecz_ligowy(601, 3, 30),
        _mecz_ligowy(602, 1, 30),
        _mecz_ligowy(602, 2, 30),
        _mecz_ligowy(602, 3, 30),
        _mecz_ligowy(603, 1, 30),
        _mecz_ligowy(603, 2, 30),
        _mecz_ligowy(604, 1, 33),
    )
    wystapienia = (_wystapienie(904, datetime(2025, 9, 20), bramki=3),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe)
    wynik = DefensywaRywalaService(repo).pobierz_analize(
        7, FiltryDefensywyRywala(), KonfiguracjaDefensywyRywala(k_shrinkage=0)
    )
    mecz = wynik.mecze[0]
    assert mecz.ga_team == pytest.approx(27.0)
    assert mecz.ga_league == pytest.approx(30.0)
    assert mecz.ga_smoothed == pytest.approx(27.0)
    assert mecz.defense_factor == pytest.approx(0.90)
    assert mecz.klasa_defensywy == "Mocna"


def test_nie_uzywa_meczow_po_dacie_analizowanego_meczu() -> None:
    mecze_ligowe = (
        _mecz_ligowy(OPPONENT, 1, 20),
        _mecz_ligowy(OPPONENT, 25, 40),
    ) + tuple(_mecz_ligowy(rywal, 1, 30) for rywal in INNI_RYWALE)
    wystapienia = (_wystapienie(905, datetime(2025, 9, 10), bramki=5),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe)
    wynik = DefensywaRywalaService(repo).pobierz_analize(7, FiltryDefensywyRywala())
    mecz = wynik.mecze[0]
    assert mecz.n_meczy_rywala == 1
    assert mecz.ga_team == pytest.approx(20.0)


def test_filtr_sezonu_i_ostatnich_n_sezonow() -> None:
    wystapienia = (
        _wystapienie(1, datetime(2023, 9, 1), 3, id_sezon=193, sezon="2023/2024", rok=2023),
        _wystapienie(2, datetime(2024, 9, 1), 4, id_sezon=194, sezon="2024/2025", rok=2024),
        _wystapienie(3, datetime(2025, 9, 1), 5, id_sezon=195, sezon="2025/2026", rok=2025),
    )
    repo = DefensywaRepozytoriumTestowe(wystapienia)
    serwis = DefensywaRywalaService(repo)
    wynik_sezon = serwis.pobierz_analize(7, FiltryDefensywyRywala(id_sezon=194))
    assert [m.id_mecz for m in wynik_sezon.mecze] == [2]
    wynik_ostatnie_2 = serwis.pobierz_analize(7, FiltryDefensywyRywala(liczba_ostatnich_sezonow=2))
    assert {m.id_mecz for m in wynik_ostatnie_2.mecze} == {2, 3}


def test_filtr_przeciwnika_zaweza_mecze_zawodnika_bez_zmiany_kontekstu_ligowego() -> None:
    wystapienia = (
        _wystapienie(1, datetime(2025, 9, 1), 3, id_zespol_przeciwnika=OPPONENT),
        _wystapienie(2, datetime(2025, 9, 8), 4, id_zespol_przeciwnika=INNI_RYWALE[0]),
    )
    repo = DefensywaRepozytoriumTestowe(
        wystapienia, zespoly_o_nazwie={"Rywal": frozenset({OPPONENT})}
    )
    serwis = DefensywaRywalaService(repo)
    wynik = serwis.pobierz_analize(7, FiltryDefensywyRywala(przeciwnik="Rywal"))
    assert [m.id_mecz for m in wynik.mecze] == [1]
    pelny = serwis.pobierz_analize(7, FiltryDefensywyRywala())
    assert wynik.mecze[0].ga_team == pelny.mecze[0].ga_team
    assert wynik.mecze[0].defense_factor == pelny.mecze[0].defense_factor
    brak = serwis.pobierz_analize(7, FiltryDefensywyRywala(przeciwnik="Nieznany"))
    assert brak.mecze == ()


def test_filtr_miejsca_dom_i_wyjazd() -> None:
    wystapienia = (
        _wystapienie(1, datetime(2025, 9, 1), 3, miejsce="dom"),
        _wystapienie(2, datetime(2025, 9, 8), 4, miejsce="wyjazd"),
    )
    repo = DefensywaRepozytoriumTestowe(wystapienia)
    serwis = DefensywaRywalaService(repo)
    wynik_dom = serwis.pobierz_analize(7, FiltryDefensywyRywala(miejsce="dom"))
    assert [m.id_mecz for m in wynik_dom.mecze] == [1]
    wynik_wyjazd = serwis.pobierz_analize(7, FiltryDefensywyRywala(miejsce="wyjazd"))
    assert [m.id_mecz for m in wynik_wyjazd.mecze] == [2]


def test_filtr_tylko_pelne_dane_domyslnie_wlaczony() -> None:
    wystapienia = (
        _wystapienie(1, datetime(2025, 9, 1), 3, dane_pelne=True),
        _wystapienie(2, datetime(2025, 9, 8), None, dane_pelne=False),
    )
    repo = DefensywaRepozytoriumTestowe(wystapienia)
    serwis = DefensywaRywalaService(repo)
    assert [m.id_mecz for m in serwis.pobierz_analize(7, FiltryDefensywyRywala()).mecze] == [1]
    wynik_wszystkie = serwis.pobierz_analize(7, FiltryDefensywyRywala(tylko_pelne_dane=False))
    assert {m.id_mecz for m in wynik_wszystkie.mecze} == {1, 2}


def test_prawdopodobienstwa_progowe_w_klasie() -> None:
    mecze_ligowe = tuple(_mecz_ligowy(OPPONENT, d, 27) for d in range(1, 6)) + tuple(
        _mecz_ligowy(rywal, d, 30) for rywal in INNI_RYWALE for d in (1, 2, 3, 4, 5)
    )
    bramki_meczow = [2, 3, 5, 5, 8, 1, 3, 5, 8, 10]
    wystapienia = tuple(
        _wystapienie(1000 + i, datetime(2025, 9, 20 + i), bramki=b, id_rozgrywki=ROZGRYWKI)
        for i, b in enumerate(bramki_meczow)
    )
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe)
    wynik = DefensywaRywalaService(repo).pobierz_analize(
        7, FiltryDefensywyRywala(), KonfiguracjaDefensywyRywala(k_shrinkage=0)
    )
    klasa_mocna = next(k for k in wynik.klasy if k.klasa == "Mocna")
    assert klasa_mocna.n == len(bramki_meczow)
    udzialy = dict(klasa_mocna.udzialy_progowe)
    assert udzialy[5] == pytest.approx(6 / 10)
    assert udzialy[8] == pytest.approx(3 / 10)
    assert klasa_mocna.mediana == pytest.approx(5.0)
    assert klasa_mocna.minimum == 1 and klasa_mocna.maksimum == 10


def test_statystyki_klasy_bez_meczow_sa_puste() -> None:
    wystapienia = (_wystapienie(1, datetime(2025, 9, 1), bramki=3),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe=())
    wynik = DefensywaRywalaService(repo).pobierz_analize(7, FiltryDefensywyRywala())
    for klasa in wynik.klasy:
        assert klasa.n == 0
        assert klasa.srednia is None


def test_poprzedni_sezon_uzywany_jako_prior_gdy_wlaczony() -> None:
    poprzednie_id_rozgrywki = 2
    mecze_ligowe_biezace = tuple(_mecz_ligowy(rywal, 1, 30) for rywal in INNI_RYWALE)
    mecze_ligowe_poprzednie = tuple(
        MeczLigowy(poprzednie_id_rozgrywki, OPPONENT, datetime(2024, 9, d), 28) for d in (1, 2, 3)
    )
    wystapienia = (_wystapienie(1, datetime(2025, 9, 20), bramki=5),)
    repo = DefensywaRepozytoriumTestowe(
        wystapienia,
        mecze_ligowe_biezace,
        poprzednie_rozgrywki={ROZGRYWKI: poprzednie_id_rozgrywki},
        mecze_ligowe_poprzednie=mecze_ligowe_poprzednie,
    )
    cfg = KonfiguracjaDefensywyRywala(
        k_shrinkage=5, w_poprzedni_sezon=3, uzyj_poprzedniego_sezonu=True
    )
    wynik = DefensywaRywalaService(repo).pobierz_analize(7, FiltryDefensywyRywala(), cfg)
    mecz = wynik.mecze[0]
    assert mecz.ga_previous == pytest.approx(28.0)
    assert mecz.n_meczy_rywala == 0
    assert mecz.ga_league == pytest.approx(30.0)
    oczekiwane = (0 * 0 + 3 * 28.0 + 5 * 30.0) / (0 + 3 + 5)
    assert mecz.ga_smoothed == pytest.approx(oczekiwane)


def test_poprzedni_sezon_nieuzyty_gdy_wylaczony_domyslnie() -> None:
    wystapienia = (_wystapienie(1, datetime(2025, 9, 20), bramki=5),)
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe=())
    wynik = DefensywaRywalaService(repo).pobierz_analize(7, FiltryDefensywyRywala())
    assert wynik.mecze[0].ga_previous is None


def test_liczba_wystapien_i_znanych_bramek_liczona_poprawnie() -> None:
    wystapienia = (
        _wystapienie(1, datetime(2025, 9, 1), bramki=3),
        _wystapienie(2, datetime(2025, 9, 8), bramki=None),
    )
    repo = DefensywaRepozytoriumTestowe(wystapienia, mecze_ligowe=())
    wynik = DefensywaRywalaService(repo).pobierz_analize(
        7, FiltryDefensywyRywala(tylko_pelne_dane=False)
    )
    assert wynik.liczba_wystapien == 2
    assert wynik.liczba_meczow_ze_znanymi_bramkami == 1
    assert wynik.liczba_meczow_z_defense_factor == 0
