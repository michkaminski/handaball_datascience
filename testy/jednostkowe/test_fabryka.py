from __future__ import annotations

import pytest

from pilka_reczna.fabryka import FabrykaAplikacji
from pilka_reczna.ustawienia import Ustawienia


def test_utworz_zwraca_skonfigurowana_aplikacje() -> None:
    ustawienia = Ustawienia(tryb_debugowania=True, tajny_klucz="test-klucz")
    fabryka = FabrykaAplikacji(ustawienia)

    aplikacja = fabryka.utworz()

    assert aplikacja.config["SECRET_KEY"] == "test-klucz"
    assert aplikacja.config["DEBUG"] is True


def test_utworz_odrzuca_niepoprawne_ustawienia() -> None:
    ustawienia = Ustawienia(tryb_debugowania=False, tajny_klucz="")
    fabryka = FabrykaAplikacji(ustawienia)

    with pytest.raises(ValueError):
        fabryka.utworz()
