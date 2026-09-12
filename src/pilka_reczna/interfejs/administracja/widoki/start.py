from __future__ import annotations

from flask import render_template, url_for
from flask.views import MethodView


class WidokStartowy(MethodView):
    def get(self) -> str:
        pozycje_nawigacji = [
            {"etykieta": "Start", "adres": url_for("administracja.start"), "aktywna": True},
        ]
        return render_template("administracja/start.html", pozycje_nawigacji=pozycje_nawigacji)
