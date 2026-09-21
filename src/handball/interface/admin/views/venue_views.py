from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych
from handball.interface.admin.forms.venue_filters import HalaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class HalaListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = HalaFilterForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            filtry = formularz.do_filtrow()
            strona = self._fabryka.utworz_serwis_hal().pobierz_liste(filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/venues/list.html",
            sekcja_aktywna="hale",
            formularz=formularz,
            filtry=filtry,
            strona=strona,
        )
