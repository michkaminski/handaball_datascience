from datetime import date, datetime

import pytest
from tests.helpers.match_predictions import (
    MeczeLigoweInMemoryRepository,
    mecz_ligowy,
    mecze_dwoch_sezonow,
)
from tests.helpers.match_tips import TypowaniaInMemoryRepository
from tests.helpers.schedule import TerminarzInMemoryRepository, pozycja

from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.errors import NieznanyModelPrognoz
from handball.domain.match_predictions import (
    KwalifikacjaMeczuPolicy,
    OcenaPrognozyPolicy,
    PowodWykluczenia,
    ProgiTrafnosci,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.domain.match_tips import PozycjaTypowania, WyborTypowan
from handball.domain.schedule import FiltryTerminarza
from handball.services.match_prediction_service import (
    BacktestPrognozService,
    KatalogModeliPrognoz,
    PodzialSezonowPolicy,
    PrognozaZapowiedziService,
)
from handball.services.match_tip_service import RaportTypowanService, TypowaniaKolejkiService


class ZegarStaly:
    def teraz(self) -> datetime:
        return datetime(2025, 9, 8, 9)


def prognozy(ligowe: MeczeLigoweInMemoryRepository) -> PrognozaZapowiedziService:
    wzorce = WzorceNazwLig()
    katalog = KatalogModeliPrognoz()
    backtest = BacktestPrognozService(
        ligowe,
        katalog,
        KwalifikacjaMeczuPolicy(wzorce),
        OcenaPrognozyPolicy(ProgiTrafnosci()),
        PodzialSezonowPolicy(ZakresBacktestu()),
        wzorce,
    )
    return PrognozaZapowiedziService(backtest, katalog, KwalifikacjaMeczuPolicy(wzorce))


def ligowe() -> MeczeLigoweInMemoryRepository:
    return MeczeLigoweInMemoryRepository(
        [
            *mecze_dwoch_sezonow(),
            mecz_ligowy(204, datetime(2025, 9, 22, 18), 30, 10, None, None, kolejka=2),
            mecz_ligowy(205, datetime(2025, 9, 23, 18), 40, 10, None, None, walkower=True),
        ]
    )


def raport(repozytorium: TypowaniaInMemoryRepository | None = None) -> RaportTypowanService:
    return RaportTypowanService(
        repozytorium or TypowaniaInMemoryRepository(),
        prognozy(ligowe()),
        KatalogModeliPrognoz(),
        WzorceNazwLig(),
        ZegarStaly(),
        KolejnoscRozgrywekPolicy(),
    )


def test_prognozy_wielu_meczow_licza_model_raz_i_rozrozniaja_tryby() -> None:
    repozytorium = ligowe()
    wynik = prognozy(repozytorium).pobierz_wiele("team_strength_v1", [201, 204, 205, 999])
    assert repozytorium.liczba_odczytow == 1
    assert wynik[201].po_meczu is not None and wynik[201].po_meczu.mecz.id_mecz == 201
    biezaca = wynik[204].biezaca
    assert biezaca is not None
    assert biezaca.liczba_meczow_ligi == 6
    assert biezaca.ostatni_mecz_ligi == datetime(2025, 9, 15, 18)
    assert wynik[205].powod_braku is PowodWykluczenia.WALKOWER
    assert wynik[999].powod_braku is PowodWykluczenia.NIEZNANA_LIGA


def test_prognoza_pojedyncza_zgodna_z_wieloma() -> None:
    serwis = prognozy(ligowe())
    pojedyncza = serwis.pobierz("team_strength_v1", 204).biezaca
    zbiorcza = serwis.pobierz_wiele("team_strength_v1", [204])[204].biezaca
    assert pojedyncza is not None and zbiorcza is not None
    assert pojedyncza.prognoza == zbiorcza.prognoza


def test_filtry_domyslnie_dzis_i_domyslny_model() -> None:
    filtry = raport().filtry(WyborTypowan())
    assert (filtry.data_od, filtry.data_do) == (date(2025, 9, 8), date(2025, 9, 8))
    assert filtry.wersja_modelu == "team_strength_v1"
    assert filtry.rozgrywki == frozenset()


def test_filtry_jedna_data_uzupelnia_druga_i_odrzucaja_bledne() -> None:
    serwis = raport()
    filtry = serwis.filtry(WyborTypowan(data_od=date(2025, 9, 1)))
    assert filtry.data_do == date(2025, 9, 1)
    with pytest.raises(ValueError):
        serwis.filtry(WyborTypowan(date(2025, 9, 9), date(2025, 9, 1)))
    with pytest.raises(NieznanyModelPrognoz):
        serwis.filtry(WyborTypowan(wersja_modelu="xyz"))


def test_raport_grupuje_po_lidze_rundzie_kolejce_i_czasie() -> None:
    serwis = raport()
    wynik = serwis.pobierz_raport(serwis.filtry(WyborTypowan(date(2025, 9, 1), date(2026, 2, 28))))
    assert [(g.runda, g.kolejka) for g in wynik.grupy] == [
        ("I runda", "Seria 1"),
        ("I runda", "Seria 2"),
        ("II runda", "Seria 3"),
    ]
    assert [t.pozycja.id_mecz for t in wynik.grupy[0].typowania] == [201, 202, 203]
    assert wynik.liczba_meczow == 5
    assert wynik.grupy[0].typowania[0].prognoza.po_meczu is not None
    assert wynik.grupy[1].typowania[0].prognoza.biezaca is not None
    assert wynik.grupy[2].typowania[0].prognoza.powod_braku is PowodWykluczenia.NIEZNANA_LIGA
    assert wynik.dostepne_rozgrywki == ("ORLEN Superliga",)


def test_raport_sortuje_mecze_grupy_po_terminie() -> None:
    pozycje = [
        PozycjaTypowania(
            501,
            "ORLEN Superliga",
            "2025/2026",
            pozycja(2, datetime(2025, 9, 1, 20), "A", "B", None),
        ),
        PozycjaTypowania(
            501,
            "ORLEN Superliga",
            "2025/2026",
            pozycja(1, datetime(2025, 9, 1, 18), "C", "D", None),
        ),
    ]
    serwis = raport(TypowaniaInMemoryRepository(pozycje))
    wynik = serwis.pobierz_raport(serwis.filtry(WyborTypowan(date(2025, 9, 1))))
    assert [t.pozycja.id_mecz for t in wynik.grupy[0].typowania] == [1, 2]


def test_raport_przekazuje_rozgrywki_i_pusty_okres_nie_liczy_modelu() -> None:
    repozytorium = TypowaniaInMemoryRepository()
    liga = ligowe()
    serwis = RaportTypowanService(
        repozytorium,
        prognozy(liga),
        KatalogModeliPrognoz(),
        WzorceNazwLig(),
        ZegarStaly(),
        KolejnoscRozgrywekPolicy(),
    )
    wynik = serwis.pobierz_raport(
        serwis.filtry(WyborTypowan(date(2025, 10, 1), rozgrywki=frozenset({"ORLEN Superliga"})))
    )
    assert repozytorium.zapytania == [
        (date(2025, 10, 1), date(2025, 10, 1), frozenset({"ORLEN Superliga"}))
    ]
    assert wynik.grupy == ()
    assert liga.liczba_odczytow == 0


def test_typowania_kolejki() -> None:
    serwis = TypowaniaKolejkiService(
        TerminarzInMemoryRepository(), prognozy(ligowe()), KatalogModeliPrognoz()
    )
    wynik = serwis.pobierz(FiltryTerminarza(5, 501, id_kolejka=112), "team_strength_v1")
    assert (wynik.kolejka, wynik.nr_kolejki) == ("Seria 2", 2)
    assert [t.pozycja.id_mecz for t in wynik.typowania] == [204]
    assert wynik.typowania[0].prognoza.biezaca is not None
    pusta = serwis.pobierz(FiltryTerminarza(5, 502, id_kolejka=112), "team_strength_v1")
    assert pusta.typowania == () and pusta.kolejka is None


def test_kolejnosc_rozgrywek_wedlug_poziomu() -> None:
    kolejnosc = KolejnoscRozgrywekPolicy()
    nazwy = [
        "III Liga Mężczyzn",
        "I Liga Kobiet Grupa A",
        "Puchar Polski",
        "Liga Centralna Kobiet",
        "II Liga Kobiet",
        "ORLEN Superliga Kobiet",
        "LOTTO Superliga",
        "Liga Centralna Mężczyzn",
    ]
    assert sorted(nazwy, key=kolejnosc.klucz) == [
        "LOTTO Superliga",
        "ORLEN Superliga Kobiet",
        "Liga Centralna Kobiet",
        "Liga Centralna Mężczyzn",
        "I Liga Kobiet Grupa A",
        "II Liga Kobiet",
        "III Liga Mężczyzn",
        "Puchar Polski",
    ]


def test_raport_uklada_grupy_i_opcje_od_superligi() -> None:
    def wpis(id_mecz: int, id_rozgrywki: int, nazwa: str) -> PozycjaTypowania:
        return PozycjaTypowania(
            id_rozgrywki,
            nazwa,
            "2025/2026",
            pozycja(id_mecz, datetime(2025, 9, 1, 18), "A", "B", None),
        )

    pozycje = [
        wpis(1, 700, "I Liga Mężczyzn Grupa A"),
        wpis(2, 600, "Liga Centralna Mężczyzn"),
        wpis(3, 500, "ORLEN Superliga"),
    ]
    serwis = raport(TypowaniaInMemoryRepository(pozycje))
    wynik = serwis.pobierz_raport(serwis.filtry(WyborTypowan(date(2025, 9, 1))))
    assert [g.rozgrywki for g in wynik.grupy] == [
        "ORLEN Superliga",
        "Liga Centralna Mężczyzn",
        "I Liga Mężczyzn Grupa A",
    ]
    assert wynik.dostepne_rozgrywki == (
        "ORLEN Superliga",
        "Liga Centralna Mężczyzn",
        "I Liga Mężczyzn Grupa A",
    )
