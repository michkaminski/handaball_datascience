from __future__ import annotations

from flask import Flask

from handball.extensions import baza_danych
from handball.import_factory import ImportRegistrar
from handball.infrastructure.database.connection import PolaczenieConfigurator
from handball.interface.navigation import zarejestruj_kontekst_nawigacji
from handball.interface.registration import WidokiRegistrar
from handball.settings import Ustawienia


class AplikacjaFactory:
    def __init__(
        self,
        ustawienia: Ustawienia,
        rejestrator_widokow: WidokiRegistrar | None = None,
        konfigurator_polaczenia: PolaczenieConfigurator | None = None,
    ) -> None:
        self._ustawienia = ustawienia
        self._rejestrator_widokow = rejestrator_widokow or WidokiRegistrar()
        self._konfigurator_polaczenia = konfigurator_polaczenia or PolaczenieConfigurator(
            ustawienia
        )

    def utworz(self) -> Flask:
        self._ustawienia.waliduj()
        aplikacja = Flask(
            "handball",
            template_folder="interface/templates",
            static_folder="interface/static",
            static_url_path="/statyczne",
        )
        aplikacja.config["SECRET_KEY"] = self._ustawienia.tajny_klucz
        aplikacja.config["DEBUG"] = self._ustawienia.tryb_debugowania
        self._konfigurator_polaczenia.skonfiguruj_odczyt(aplikacja)
        baza_danych.init_app(aplikacja)
        zarejestruj_kontekst_nawigacji(aplikacja)
        self._rejestrator_widokow.zarejestruj(aplikacja)
        ImportRegistrar().zarejestruj(aplikacja)
        return aplikacja
