from __future__ import annotations

from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.match_repository import MeczInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository
from tests.helpers.venue_repository import HalaInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.matches import PozycjaListyMeczow
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
)

SEZONY_TESTOWE = [OpcjaWyboru(195, "2026/2027")]


def _aplikacja_z_repozytorium(pozycje: list[PozycjaListyMeczow] | None = None) -> Flask:
    fabryka_zaleznosci = ZaleznosciZadaniaFactory(
        lambda: MeczInMemoryRepository(pozycje),
        lambda: SezonInMemoryRepository(SEZONY_TESTOWE),
        lambda: RozgrywkiInMemoryRepository(),
        lambda: HalaInMemoryRepository(),
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
