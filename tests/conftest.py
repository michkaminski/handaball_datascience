from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from handball import create_app
from handball.settings import Ustawienia


def ustawienia_testowe(
    *, tryb_debugowania: bool = False, tajny_klucz: str = "test-klucz"
) -> Ustawienia:
    return Ustawienia(
        tryb_debugowania=tryb_debugowania,
        tajny_klucz=tajny_klucz,
        host_bazy="localhost",
        port_bazy=5432,
        nazwa_bazy="zprp",
        uzytkownik_bazy="postgres",
        haslo_bazy="",
    )


@pytest.fixture()
def aplikacja() -> Flask:
    return create_app()


@pytest.fixture()
def klient(aplikacja: Flask) -> FlaskClient:
    return aplikacja.test_client()
