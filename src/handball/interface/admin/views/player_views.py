from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych
from handball.interface.admin.forms.player_filters import ZawodnikFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class ZawodnikListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_zawodnikow()

    def get(self) -> str:
        formularz = ZawodnikFilterForm(request.args)
        serwis = self._fabryka.utworz_serwis_zawodnikow()
        try:
            sezony, rozgrywki = self._fabryka.utworz_slowniki_zawodnikow().pobierz_opcje()
            formularz.id_sezon.choices = [("", "Wszystkie")] + [
                (str(opcja.wartosc), opcja.etykieta) for opcja in sezony
            ]
            formularz.rozgrywki.choices = [("", "Wszystkie")] + [(n, n) for n in rozgrywki]
            formularz.pozycja.choices = [("", "Wszystkie")] + [
                (p, p) for p in serwis.pobierz_pozycje()
            ]
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            try:
                filtry = formularz.do_filtrow()
            except ValueError as wyjatek:
                abort(400, description=str(wyjatek))
            strona = serwis.pobierz_liste(filtry)
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/players/list.html",
            sekcja_aktywna="zawodnicy",
            formularz=formularz,
            filtry=filtry,
            strona=self._presenter.przygotuj_liste(strona),
        )
