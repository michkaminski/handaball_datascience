from __future__ import annotations

from flask.testing import FlaskClient


def test_start_zwraca_200(klient: FlaskClient) -> None:
    odpowiedz = klient.get("/administracja/")

    assert odpowiedz.status_code == 200
