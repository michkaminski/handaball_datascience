from __future__ import annotations

from flask import render_template
from flask.views import MethodView


class StartView(MethodView):
    def get(self) -> str:
        return render_template("admin/start.html", sekcja_aktywna="start")
