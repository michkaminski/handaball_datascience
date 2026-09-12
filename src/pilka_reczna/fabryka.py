from __future__ import annotations

from flask import Flask

from pilka_reczna.interfejs.rejestracja import RejestratorWidokow
from pilka_reczna.ustawienia import Ustawienia


class FabrykaAplikacji:
    def __init__(
        self,
        ustawienia: Ustawienia,
        rejestrator_widokow: RejestratorWidokow | None = None,
    ) -> None:
        self._ustawienia = ustawienia
        self._rejestrator_widokow = rejestrator_widokow or RejestratorWidokow()

    def utworz(self) -> Flask:
        self._ustawienia.waliduj()
        aplikacja = Flask("pilka_reczna")
        aplikacja.config["SECRET_KEY"] = self._ustawienia.tajny_klucz
        aplikacja.config["DEBUG"] = self._ustawienia.tryb_debugowania
        self._rejestrator_widokow.zarejestruj(aplikacja)
        return aplikacja
