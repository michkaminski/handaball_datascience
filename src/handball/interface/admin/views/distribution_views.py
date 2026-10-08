from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych
from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    OpcjeFiltrowRozkladu,
    rodzaj_serii,
)
from handball.interface.admin.forms.goal_distribution_filters import RozkladBramekFilterForm
from handball.interface.distribution_catalog import KATALOG_ROZKLADOW
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class RozkladyListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        return render_template(
            "admin/reports/distributions/list.html",
            sekcja_aktywna="rozkłady",
            sekcja_glowna="raporty",
            rozklady=KATALOG_ROZKLADOW,
        )


class RozkladBramekView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = RozkladBramekFilterForm(request.args)
        try:
            serwis = self._fabryka.utworz_serwis_rozkladu_bramek()
            filtry = _filtry_z_zapytania(formularz, serwis.pobierz_opcje())
            raport = serwis.pobierz_raport(filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/reports/distributions/goals.html",
            sekcja_aktywna="rozkłady",
            sekcja_glowna="raporty",
            formularz=formularz,
            raport=raport,
        )


class MeczeRozkladuBramekView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = RozkladBramekFilterForm(request.args)
        try:
            rodzaj = rodzaj_serii(request.args.get("seria"))
            bramki = _liczba_bramek(request.args.get("bramki"))
            serwis = self._fabryka.utworz_serwis_rozkladu_bramek()
            filtry = _filtry_z_zapytania(formularz, serwis.pobierz_opcje())
            mecze = serwis.pobierz_mecze(filtry, rodzaj, bramki)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/reports/distributions/goal_matches.html",
            mecze=mecze,
        )


def _filtry_z_zapytania(
    formularz: RozkladBramekFilterForm, opcje: OpcjeFiltrowRozkladu
) -> FiltryRozkladuBramek:
    formularz.id_sezon.choices = [("", "Wszystkie")] + [
        (opcja.wartosc, opcja.etykieta) for opcja in opcje.sezony
    ]
    formularz.rozgrywki.choices = [("", "Wszystkie")] + [
        (opcja.wartosc, opcja.etykieta) for opcja in opcje.rozgrywki
    ]
    if not formularz.validate():
        abort(400, description=str(formularz.errors))
    return formularz.do_filtrow()


def _liczba_bramek(tekst: str | None) -> int:
    if tekst is None or not tekst.isdigit():
        raise ValueError("nieobsługiwana liczba bramek")
    return int(tekst)
