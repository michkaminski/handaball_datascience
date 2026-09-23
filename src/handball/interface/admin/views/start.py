from __future__ import annotations

from flask import render_template
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class StartView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_aktualnosci()

    def get(self) -> str:
        try:
            aktualnosci = self._fabryka.utworz_serwis_aktualnosci().pobierz_aktualnosci()
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/start.html",
            sekcja_aktywna="start",
            aktualnosci=self._presenter.przygotuj(aktualnosci),
        )
