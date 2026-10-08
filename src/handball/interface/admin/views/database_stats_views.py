from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.database_stats import DOZWOLONE_SORTOWANIA, DOMYSLNE_SORTOWANIE
from handball.domain.errors import BladOdczytuDanych
from handball.interface.admin.forms.database_stats_filters import StatystykiBazyFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class StatystykiBazyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = StatystykiBazyFilterForm(request.args)
        formularz.sortowanie.choices = [(pole, pole) for pole in sorted(DOZWOLONE_SORTOWANIA)]
        schemat = (request.args.get("schemat") or "").strip()
        formularz.schemat.choices = [("", "Wszystkie")] + (
            [(schemat, schemat)] if schemat else []
        )
        if not request.args.get("sortowanie"):
            formularz.sortowanie.data = DOMYSLNE_SORTOWANIE
        try:
            serwis = self._fabryka.utworz_serwis_statystyk_bazy()
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            filtry = formularz.do_filtrow()
            strona = serwis.pobierz_strone(filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        formularz.schemat.choices = [("", "Wszystkie")] + [
            (nazwa, nazwa) for nazwa in strona.schematy
        ]
        return render_template(
            "admin/database_stats/list.html",
            sekcja_aktywna="statystyki_bazy",
            formularz=formularz,
            filtry=filtry,
            strona=strona,
        )
