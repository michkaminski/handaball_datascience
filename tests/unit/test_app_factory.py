from __future__ import annotations

import pytest
from tests.conftest import ustawienia_testowe

from handball.app_factory import AplikacjaFactory


def test_utworz_zwraca_skonfigurowana_aplikacje() -> None:
    ustawienia = ustawienia_testowe(tryb_debugowania=True)
    fabryka = AplikacjaFactory(ustawienia)

    aplikacja = fabryka.utworz()

    assert aplikacja.config["SECRET_KEY"] == "test-klucz"
    assert aplikacja.config["DEBUG"] is True
    assert aplikacja.config["SQLALCHEMY_DATABASE_URI"] == ustawienia.adres_bazy_danych


def test_utworz_odrzuca_niepoprawne_ustawienia() -> None:
    ustawienia = ustawienia_testowe(tajny_klucz="")
    fabryka = AplikacjaFactory(ustawienia)

    with pytest.raises(ValueError):
        fabryka.utworz()
