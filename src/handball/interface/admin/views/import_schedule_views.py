from __future__ import annotations

from flask import Response, abort, make_response, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych
from handball.domain.imports import LIMIT_WYBRANYCH_MECZOW
from handball.interface.admin.forms.import_schedule_filters import PobieranieMeczowFilterForm
from handball.interface.admin.import_access import (
    logowanie_importu_poprawne,
    odmowa_logowania_importu,
)
from handball.interface.admin.import_csrf import token_importu
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class PobieranieMeczowView(MethodView):
    def __init__(self, fabryka: ZaleznosciZadaniaFactory, haslo: str) -> None:
        self._fabryka = fabryka
        self._haslo = haslo

    def get(self) -> Response | str:
        if not self._haslo:
            return make_response(
                render_template(
                    "admin/import/panel.html",
                    sekcja_aktywna="import",
                    ligi={},
                    przebieg=None,
                    historia=[],
                    konfiguracja=False,
                ),
                503,
            )
        if not logowanie_importu_poprawne(self._haslo):
            return odmowa_logowania_importu()
        formularz = PobieranieMeczowFilterForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            opcje = self._fabryka.utworz_serwis_terminarza().pobierz_opcje(formularz.do_wyboru())
            lista = self._fabryka.utworz_serwis_pobierania_meczow().pobierz(
                opcje.wybor,
                bool(formularz.wynik_bez_danych.data),
                bool(formularz.kolejki_zakonczone.data),
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/import/schedule.html",
            sekcja_aktywna="pobieranie_meczow",
            sekcja_glowna="import",
            opcje=opcje,
            terminarz=(
                self._fabryka.utworz_presenter_terminarza().przygotuj(lista) if lista else None
            ),
            wynik_bez_danych=bool(formularz.wynik_bez_danych.data),
            kolejki_zakonczone=bool(formularz.kolejki_zakonczone.data),
            csrf_importu=token_importu() if lista and lista.rundy else None,
            limit_meczow=LIMIT_WYBRANYCH_MECZOW,
        )
