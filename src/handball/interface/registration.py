from __future__ import annotations

from flask import Flask

from handball.interface.admin import utworz_blueprint_administracji
from handball.interface.mathematics import utworz_blueprint_matematyki
from handball.request_dependencies import ZaleznosciZadaniaFactory


class WidokiRegistrar:
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory | None = None) -> None:
        self._fabryka_zaleznosci = fabryka_zaleznosci or ZaleznosciZadaniaFactory()

    def zarejestruj(self, aplikacja: Flask) -> None:
        aplikacja.register_blueprint(utworz_blueprint_administracji(self._fabryka_zaleznosci))
        aplikacja.register_blueprint(utworz_blueprint_matematyki(self._fabryka_zaleznosci))
