from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from html import unescape

import pytest
from flask import Flask
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.match_repository import MeczInMemoryRepository
from tests.helpers.match_stage_repository import EtapMeczowInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository
from tests.helpers.venue_repository import HalaInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.matches import PozycjaListyMeczow, SzczegolyMeczu
from handball.domain.options import OpcjaWyboru
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

POZYCJA_TESTOWA = PozycjaListyMeczow(
    id_mecz=12543,
    termin=datetime(2026, 9, 12, 18, 0),
    sezon="2026/2027",
    rozgrywki="ORLEN Superliga",
    gospodarz="Industria Kielce",
    gosc="Orlen Wisła Płock",
    wynik="32 : 28",
    hala="Hala Legionów",
    runda="Runda zasadnicza",
    kolejka="Kolejka 1",
)

SZCZEGOLY_TESTOWE = SzczegolyMeczu(
    id_mecz=12543,
    gospodarz="Industria Kielce",
    gosc="Orlen Wisła Płock",
    wynik_naglowek="32 : 28",
    wynik_do_przerwy="do przerwy 16 : 13",
    dopisek_wyniku="dogrywka",
    rozgrywki="ORLEN Superliga",
    kolejka="Kolejka 1",
    termin="12.09.2026 18:00",
    hala="Hala Legionów",
    status="Rozegrany",
    dane_podstawowe=[("Sezon", "2026/2027")],
    statystyki=[("Wynik (pełny)", "32", "28")],
    sklad_gospodarz=[],
    sklad_gosc=[],
    sklad_inne=[],
)

SEZONY_TESTOWE = [OpcjaWyboru(195, "2026/2027")]


def _aplikacja_z_repozytorium(
    pozycje: list[PozycjaListyMeczow] | None = None,
    szczegoly: dict[int, SzczegolyMeczu] | None = None,
) -> Flask:
    fabryka_zaleznosci = ZaleznosciZadaniaFactory(
        lambda: MeczInMemoryRepository(pozycje, szczegoly),
        lambda: SezonInMemoryRepository(SEZONY_TESTOWE),
        lambda: RozgrywkiInMemoryRepository(),
        lambda: HalaInMemoryRepository(),
        lambda: EtapMeczowInMemoryRepository(),
    )
    fabryka = AplikacjaFactory(
        ustawienia_testowe(),
        rejestrator_widokow=WidokiRegistrar(fabryka_zaleznosci),
    )
    return fabryka.utworz()


@pytest.fixture()
def klient_z_danymi() -> FlaskClient:
    return _aplikacja_z_repozytorium([POZYCJA_TESTOWA]).test_client()


@pytest.fixture()
def klient_bez_danych() -> FlaskClient:
    return _aplikacja_z_repozytorium([]).test_client()


def test_lista_meczow_bez_filtrow_dziala(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc


def test_lista_meczow_odrzuca_niepoprawny_id_sezon(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?id_sezon=abc")

    assert odpowiedz.status_code == 400


def test_lista_meczow_odrzuca_niepoprawna_date(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?data_meczu=2026-13")

    assert odpowiedz.status_code == 400


def test_lista_meczow_przyjmuje_czesciowa_date(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?data_meczu=2026-09")

    assert odpowiedz.status_code == 200


def test_lista_meczow_zwraca_dane(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?id_sezon=195")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc
    assert "32 : 28" in tresc
    assert "Hala Legionów" in tresc
    assert "2026/2027" in tresc
    assert "ORLEN Superliga" in tresc


def test_lista_meczow_sortowanie_jest_linkiem_w_naglowku(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert "sortowanie=-data" in tresc
    assert 'name="sortowanie"' not in tresc


def test_lista_meczow_pusty_wynik(klient_bez_danych: FlaskClient) -> None:
    odpowiedz = klient_bez_danych.get("/administracja/mecze?id_sezon=195")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Brak meczów spełniających wybrane filtry." in tresc


def test_runda_i_kolejka_filtruja_lacznie() -> None:
    pozycje = [
        POZYCJA_TESTOWA,
        replace(POZYCJA_TESTOWA, id_mecz=2, gospodarz="Inna kolejka", kolejka="Kolejka 2"),
        replace(POZYCJA_TESTOWA, id_mecz=3, gospodarz="Inna runda", runda="Play-off"),
    ]
    klient = _aplikacja_z_repozytorium(pozycje).test_client()
    odpowiedz = klient.get(
        "/administracja/mecze", query_string={"runda": "Runda zasadnicza", "kolejka": "Kolejka 1"}
    )
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc
    assert "Inna kolejka" not in tresc
    assert "Inna runda" not in tresc
    assert '<option selected value="Runda zasadnicza">' in tresc
    assert '<option selected value="Kolejka 1">' in tresc
    assert 'data-match-column="runda" hidden>Runda zasadnicza</td>' in tresc
    assert 'data-match-column="kolejka" hidden>Kolejka 1</td>' in tresc
    assert 'id="match-columns-dialog"' in tresc
    assert 'aria-haspopup="dialog"' in tresc
    assert "js/matches.js" in tresc


@pytest.mark.parametrize("pole", ["runda", "kolejka"])
def test_nieznana_opcja_etapu_zwraca_400(klient_z_danymi: FlaskClient, pole: str) -> None:
    assert (
        klient_z_danymi.get(
            "/administracja/mecze", query_string={pole: "nieistniejaca"}
        ).status_code
        == 400
    )


def test_filtry_etapow_sa_zachowane_w_sortowaniu_i_paginacji() -> None:
    klient = _aplikacja_z_repozytorium([POZYCJA_TESTOWA] * 25).test_client()
    odpowiedz = klient.get(
        "/administracja/mecze", query_string={"runda": "Runda zasadnicza", "kolejka": "Kolejka 1"}
    )
    tresc = unescape(odpowiedz.get_data(as_text=True))
    from html.parser import HTMLParser

    class LinkParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.adresy: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag == "a":
                adres = dict(attrs).get("href")
                if adres:
                    self.adresy.append(adres)

    parser = LinkParser()
    parser.feed(tresc)
    adresy = [a for a in parser.adresy if "sortowanie=-data" in a or "strona=2" in a]
    assert len(adresy) == 2
    assert all("runda=Runda+zasadnicza" in a and "kolejka=Kolejka+1" in a for a in adresy)


def test_lista_meczow_ma_link_do_szczegolow(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert "/administracja/mecze/12543" in tresc
    assert "Szczegóły" in tresc


def test_lista_meczow_wiersz_ma_adres_do_dwuklikniecia(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert 'data-href="/administracja/mecze/12543"' in tresc


def test_lista_meczow_pokazuje_dopisek_wyniku() -> None:
    pozycja = replace(POZYCJA_TESTOWA, dopisek_wyniku="k 6-7")
    klient = _aplikacja_z_repozytorium([pozycja]).test_client()

    odpowiedz = klient.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "k 6-7" in tresc


def test_szczegoly_meczu_wyswietla_dane() -> None:
    klient = _aplikacja_z_repozytorium(
        [POZYCJA_TESTOWA], {12543: SZCZEGOLY_TESTOWE}
    ).test_client()

    odpowiedz = klient.get("/administracja/mecze/12543")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc
    assert "Orlen Wisła Płock" in tresc
    assert "32 : 28" in tresc
    assert "do przerwy 16 : 13" in tresc
    assert "dogrywka" in tresc
    assert "Rozegrany" in tresc


def test_szczegoly_meczu_nieistniejacego_zwraca_404() -> None:
    klient = _aplikacja_z_repozytorium([POZYCJA_TESTOWA], {}).test_client()

    odpowiedz = klient.get("/administracja/mecze/999999")

    assert odpowiedz.status_code == 404
