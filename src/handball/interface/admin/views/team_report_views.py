from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Response, abort, render_template, request
from flask.views import MethodView

from handball.domain.catalogs import FiltryKatalogu, StronaKatalogu
from handball.domain.errors import BladOdczytuDanych, NieZnalezionoDruzyny
from handball.interface.admin.forms.team_report_filters import RaportDruzynyForm
from handball.interface.admin.views.catalog_views import DruzynaListView
from handball.interface.admin.views.schedule_views import PdfResponseBuilder
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory
from handball.services.catalog_service import KatalogService

ARKUSZ_RAPORTU = Path("css") / "team_report_pdf.css"


class RaportDruzynyPdfView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._pdf = PdfResponseBuilder(fabryka_zaleznosci)

    def get(self, id_zespol: int) -> Response:
        formularz = RaportDruzynyForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            raport = self._fabryka.utworz_serwis_raportu_druzyny().pobierz_raport(
                id_zespol, formularz.do_sezonu(), formularz.do_liczby_meczow()
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except (NieZnalezionoDruzyny, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        html = render_template(
            "admin/teams/report_pdf.html",
            raport=self._fabryka.utworz_presenter_raportu_druzyny().przygotuj_raport(raport),
        )
        return self._pdf.odpowiedz(
            html, ARKUSZ_RAPORTU, f"raport-druzyny-{id_zespol}-{formularz.do_sezonu()}.pdf"
        )


class ZestawieniaDruzynyPdfView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._pdf = PdfResponseBuilder(fabryka_zaleznosci)

    def get(self, id_zespol: int) -> Response:
        formularz = RaportDruzynyForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            zestawienia = self._fabryka.utworz_serwis_raportu_druzyny().pobierz_zestawienia(
                id_zespol, formularz.do_sezonu()
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except (NieZnalezionoDruzyny, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        html = render_template(
            "admin/teams/season_sheets_pdf.html",
            zestawienia=self._fabryka.utworz_presenter_raportu_druzyny().przygotuj_zestawienia(
                zestawienia
            ),
        )
        return self._pdf.odpowiedz(
            html, ARKUSZ_RAPORTU, f"zestawienia-druzyny-{id_zespol}-{formularz.do_sezonu()}.pdf"
        )


class RaportyDruzynListView(DruzynaListView):
    szablon = "admin/reports/teams.html"
    sekcja = "raporty_druzyn"
    sekcja_glowna = "raporty"

    def pobierz_strone(self, serwis: KatalogService, filtry: FiltryKatalogu) -> StronaKatalogu[Any]:
        return serwis.pobierz_druzyny(filtry)
