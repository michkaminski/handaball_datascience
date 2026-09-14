from __future__ import annotations

from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.interface.admin.forms.match_filters import MeczFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class MeczListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka_zaleznosci = fabryka_zaleznosci

    def get(self) -> str:
        id_sezon_wybrany = request.args.get("id_sezon", type=int)
        serwis_slownikow = self._fabryka_zaleznosci.utworz_serwis_slownikow()
        try:
            opcje = serwis_slownikow.pobierz_opcje(id_sezon_wybrany)
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)

        formularz = MeczFilterForm(request.args)
        formularz.id_sezon.choices = [("", "Wszystkie")] + [
            (str(opcja.wartosc), opcja.etykieta) for opcja in opcje.sezony
        ]
        formularz.rozgrywki.choices = [("", "Wszystkie")] + [
            (nazwa, nazwa) for nazwa in opcje.rozgrywki
        ]
        formularz.id_hala.choices = [("", "Wszystkie")] + [
            (str(opcja.wartosc), opcja.etykieta) for opcja in opcje.hale
        ]

        if not formularz.validate():
            abort(400, description=str(formularz.errors))

        try:
            filtry = formularz.do_filtrow()
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))

        serwis = self._fabryka_zaleznosci.utworz_serwis_meczow()
        try:
            strona = serwis.pobierz_liste(filtry)
        except (NieZnalezionoMeczu, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)

        return render_template(
            "admin/matches/list.html",
            sekcja_aktywna="mecze",
            strona=strona,
            filtry=filtry,
            opcje=opcje,
            formularz=formularz,
        )
