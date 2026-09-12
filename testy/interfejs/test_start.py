from __future__ import annotations

from flask.testing import FlaskClient


def test_start_zwraca_200(klient: FlaskClient) -> None:
    odpowiedz = klient.get("/administracja/")

    assert odpowiedz.status_code == 200


def test_start_renderuje_uklad_bazowy(klient: FlaskClient) -> None:
    odpowiedz = klient.get("/administracja/")
    tresc = odpowiedz.get_data(as_text=True)

    assert "Handball DataScience" in tresc
    assert 'class="nav"' in tresc
