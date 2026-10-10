from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.attendance_analytics import FiltryFrekwencji, RaportFrekwencji
from handball.domain.errors import BladOdczytuDanych
from handball.interface.admin.forms.attendance_analytics_filters import FrekwencjaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.interface.presenters.attendance_tabs import (
    ZAKLADKI_FREKWENCJI,
    WyborZakladkiFrekwencji,
)
from handball.request_dependencies import ZaleznosciZadaniaFactory


class FrekwencjaView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._wybor_zakladki = WyborZakladkiFrekwencji()

    def get(self) -> str:
        formularz = FrekwencjaFilterForm(request.args)
        try:
            serwis = self._fabryka.utworz_serwis_frekwencji()
            formularz.zastosuj_opcje(serwis.pobierz_opcje())
            filtry = self._filtry(formularz)
            raport = serwis.pobierz_raport(filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/reports/attendance/dashboard.html",
            sekcja_aktywna="frekwencja",
            sekcja_glowna="raporty",
            formularz=formularz,
            raport=raport,
            wykres=self._wykres(raport),
            zakladki=ZAKLADKI_FREKWENCJI,
            aktywna_zakladka=self._wybor_zakladki.wybierz(request.args),
            modele_maf=self._fabryka.utworz_serwis_atrakcyjnosci().modele(),
        )

    def _filtry(self, formularz: FrekwencjaFilterForm) -> FiltryFrekwencji:
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        return formularz.do_filtrow()

    def _wykres(self, raport: RaportFrekwencji) -> dict[str, object]:
        return self._fabryka.utworz_presenter_frekwencji().przygotuj(raport)
