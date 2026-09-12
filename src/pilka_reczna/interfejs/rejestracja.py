from __future__ import annotations

from flask import Flask

from pilka_reczna.interfejs.administracja import blueprint_administracji


class RejestratorWidokow:
    def zarejestruj(self, aplikacja: Flask) -> None:
        aplikacja.register_blueprint(blueprint_administracji)
