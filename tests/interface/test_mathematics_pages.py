from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from mathlib.registry import default_registry


def test_strona_glowna_pokazuje_wszystkie_dzialy(klient: FlaskClient) -> None:
    tresc = klient.get("/matematyka/").get_data(as_text=True)
    for dzial in default_registry().categories:
        assert dzial.name in tresc


@pytest.mark.parametrize(
    "adres",
    [pojecie for pojecie in (default_registry().url(c.id) for c in default_registry().articles())],
)
def test_kazdy_artykul_jest_dostepny(klient: FlaskClient, adres: str) -> None:
    odpowiedz = klient.get(adres)
    assert odpowiedz.status_code == 200
    tresc = odpowiedz.get_data(as_text=True)
    assert "katex.min.js" in tresc and 'class="ml-toc"' in tresc


def test_nieznany_artykul_i_dzial_daja_404(klient: FlaskClient) -> None:
    assert klient.get("/matematyka/brak/").status_code == 404
    assert klient.get("/matematyka/podstawy-statystyki/brak/").status_code == 404
    assert klient.get("/matematyka/rozklady-prawdopodobienstwa/mediana/").status_code == 404
