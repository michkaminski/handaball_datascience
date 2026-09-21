from datetime import datetime

import pytest
from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.match_repository import MeczInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository
from tests.helpers.venue_details import SzczegolyHaliInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow
from handball.domain.options import OpcjaWyboru
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

MECZ = PozycjaListyMeczow(
    101,
    datetime(2026, 2, 1, 18),
    "2025/2026",
    "Liga",
    "Drużyna A",
    "Drużyna B",
    DaneMeczu(id=101, wynik_gosp_full=30, wynik_gosc_full=27),
    "Hala Testowa",
)


def aplikacja_z_karta(repo: SzczegolyHaliInMemoryRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_szczegolow_hali=lambda: repo,
        fabryka_repozytorium_meczow=lambda: MeczInMemoryRepository([MECZ]),
        fabryka_repozytorium_sezonow=lambda: SezonInMemoryRepository(
            [OpcjaWyboru(195, "2025/2026")]
        ),
        fabryka_repozytorium_rozgrywek=lambda: RozgrywkiInMemoryRepository(["Liga"]),
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_karta_renderuje_cztery_zakladki_i_podsumowanie() -> None:
    tresc = (
        aplikacja_z_karta(SzczegolyHaliInMemoryRepository())
        .test_client()
        .get("/administracja/hale/7")
        .get_data(as_text=True)
    )
    assert "Hala Testowa" in tresc and "Sportowa 1" in tresc and "4200" in tresc
    assert 'data-venue-tab="dane"' in tresc
    assert 'data-venue-tab="mecze"' in tresc
    assert 'data-venue-tab="zawodnicy"' in tresc
    assert 'data-venue-tab="statystyki"' in tresc
    assert "01.09.2020" in tresc and "20.05.2026" in tresc
    assert "Drużyna A" in tresc and "/administracja/mecze/101" in tresc
    assert "Jan Bramkowy" in tresc and "/administracja/zawodnicy/9" in tresc


def test_filtry_zawodnikow_i_aktywna_zakladka() -> None:
    repo = SzczegolyHaliInMemoryRepository()
    odpowiedz = (
        aplikacja_z_karta(repo)
        .test_client()
        .get(
            "/administracja/hale/7?zakladka=zawodnicy&z_szukaj=Jan"
            "&z_sortowanie=-srednia_bramek&z_strona=2&z_rozmiar=50"
        )
    )
    assert odpowiedz.status_code == 200
    assert 'data-active-tab="zawodnicy"' in odpowiedz.get_data(as_text=True)
    assert repo.filtry is not None
    assert repo.filtry.szukaj == "Jan"
    assert repo.filtry.sortowanie == "-srednia_bramek"
    assert repo.filtry.strona == 2 and repo.filtry.rozmiar_strony == 50


def test_rankingi_domyslnie_maja_top_10_i_mozna_je_rozszerzyc() -> None:
    repo = SzczegolyHaliInMemoryRepository()
    klient = aplikacja_z_karta(repo).test_client()
    tresc = klient.get("/administracja/hale/7?zakladka=statystyki").get_data(as_text=True)
    assert repo.limity is not None and repo.limity.druzyny == 10
    assert "Drużyna 10" in tresc and "Drużyna 11" not in tresc
    assert "Pokaż wszystkie" in tresc and "Pokaż wszystkich" in tresc
    tresc = klient.get("/administracja/hale/7?zakladka=statystyki&wszystkie_druzyny=1").get_data(
        as_text=True
    )
    assert repo.limity is not None and repo.limity.druzyny is None
    assert "Drużyna 11" in tresc


def test_statystyki_renderuja_analizy_wykresy_i_rekordy() -> None:
    tresc = (
        aplikacja_z_karta(SzczegolyHaliInMemoryRepository())
        .test_client()
        .get("/administracja/hale/7?zakladka=statystyki")
        .get_data(as_text=True)
    )
    assert 'href="#venue-trends"' in tresc
    assert "Trendy sezonowe" in tresc and "Średnia suma bramek" in tresc
    assert "Profil wyników" in tresc and "57.1" in tresc and "42–71" in tresc
    assert "Sezon × miesiąc" in tresc and 'data-level="4"' in tresc
    assert "Dane: 18 (90.0%)" in tresc and "Śr. wypełnienie" in tresc
    assert "Najwięcej bramek" in tresc and "/administracja/mecze/101" in tresc
    assert 'href="/administracja/mecze/101" target="_blank" rel="noopener"' in tresc


@pytest.mark.parametrize(
    "query",
    [
        "zakladka=inna",
        "m_sezon=x",
        "m_rozgrywki=inna",
        "m_strona=0",
        "m_sortowanie=inna",
        "z_strona=0",
        "z_rozmiar=101",
        "z_sortowanie=inna",
    ],
)
def test_bledne_parametry_zwracaja_400(query: str) -> None:
    klient = aplikacja_z_karta(SzczegolyHaliInMemoryRepository()).test_client()
    assert klient.get("/administracja/hale/7?" + query).status_code == 400


def test_brak_hali_i_brak_zapisu() -> None:
    klient = aplikacja_z_karta(SzczegolyHaliInMemoryRepository()).test_client()
    assert klient.get("/administracja/hale/999").status_code == 404
    assert klient.post("/administracja/hale/7").status_code == 405
