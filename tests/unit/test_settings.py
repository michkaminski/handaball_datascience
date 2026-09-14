from __future__ import annotations

import pytest

from handball.settings import Ustawienia


def test_z_srodowiska_uzywa_wartosci_domyslnych(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)

    ustawienia = Ustawienia.z_srodowiska()

    assert ustawienia.tryb_debugowania is False
    assert ustawienia.tajny_klucz == "dev"


def test_z_srodowiska_odczytuje_zmienne(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "sekret-testowy")
    monkeypatch.setenv("FLASK_DEBUG", "1")

    ustawienia = Ustawienia.z_srodowiska()

    assert ustawienia.tryb_debugowania is True
    assert ustawienia.tajny_klucz == "sekret-testowy"


def test_waliduj_odrzuca_pusty_klucz() -> None:
    ustawienia = Ustawienia(
        tryb_debugowania=False,
        tajny_klucz="",
        host_bazy="localhost",
        port_bazy=5432,
        nazwa_bazy="zprp",
        uzytkownik_bazy="postgres",
        haslo_bazy="",
    )

    with pytest.raises(ValueError):
        ustawienia.waliduj()


def test_adres_bazy_danych_buduje_url_polaczenia() -> None:
    ustawienia = Ustawienia(
        tryb_debugowania=False,
        tajny_klucz="dev",
        host_bazy="localhost",
        port_bazy=5432,
        nazwa_bazy="zprp",
        uzytkownik_bazy="postgres",
        haslo_bazy="tajne",
    )

    assert ustawienia.adres_bazy_danych == "postgresql+psycopg://postgres:tajne@localhost:5432/zprp"
