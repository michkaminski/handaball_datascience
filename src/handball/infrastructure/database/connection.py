from __future__ import annotations

from flask import Flask

from handball.settings import Ustawienia


class PolaczenieConfigurator:
    def __init__(self, ustawienia: Ustawienia) -> None:
        self._ustawienia = ustawienia

    def skonfiguruj_odczyt(self, aplikacja: Flask) -> None:
        aplikacja.config["SQLALCHEMY_DATABASE_URI"] = self._ustawienia.adres_bazy_danych
        aplikacja.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "execution_options": {"postgresql_readonly": True},
        }
