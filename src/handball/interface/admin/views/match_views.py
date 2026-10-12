from __future__ import annotations

from pathlib import Path

from flask import Response, abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.interface.admin.forms.match_filters import MeczFilterForm
from handball.interface.admin.views.schedule_views import PdfResponseBuilder
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class MeczListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka_zaleznosci = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_meczow()

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

        formularz.runda.choices = [("", "Wszystkie")] + [(nazwa, nazwa) for nazwa in opcje.rundy]
        formularz.kolejka.choices = [("", "Wszystkie")] + [
            (nazwa, nazwa) for nazwa in opcje.kolejki
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
            strona=self._presenter.przygotuj_liste(strona),
            filtry=filtry,
            opcje=opcje,
            formularz=formularz,
        )


class MeczSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka_zaleznosci = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_meczow()
        self._presenter_statystyk = fabryka_zaleznosci.utworz_presenter_statystyk_meczu()

    def get(self, id_mecz: int) -> str:
        serwis = self._fabryka_zaleznosci.utworz_serwis_statystyk_meczu()
        try:
            statystyki = serwis.pobierz(id_mecz)
        except (NieZnalezionoMeczu, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)

        return render_template(
            "admin/matches/detail.html",
            sekcja_aktywna="mecze",
            szczegoly=self._presenter.przygotuj_szczegoly(statystyki.szczegoly),
            statystyki=self._presenter_statystyk.przygotuj(statystyki),
        )


class RaportMeczuPdfView(MethodView):
    ARKUSZ = Path("css") / "match_report_pdf.css"
    LIMIT_SKROCONY = 16

    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka_zaleznosci = fabryka_zaleznosci
        self._pdf = PdfResponseBuilder(fabryka_zaleznosci)

    def get(self, id_mecz: int) -> Response | str:
        serwis = self._fabryka_zaleznosci.utworz_serwis_raportu_meczu()
        wersja = self._fabryka_zaleznosci.utworz_katalog_modeli_prognoz().domyslna_wersja
        skrocony = request.args.get("wariant") == "skrocony"
        try:
            raport = serwis.pobierz(id_mecz, wersja, z_modelem=not skrocony)
        except (NieZnalezionoMeczu, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        presenter = self._fabryka_zaleznosci.utworz_presenter_raportu_meczu()
        html = render_template(
            "admin/matches/report_pdf.html",
            raport=presenter.przygotuj(raport, self.LIMIT_SKROCONY if skrocony else None),
            skrocony=skrocony,
        )
        if request.args.get("format") == "html":
            return html
        nazwa = f"raport-meczu-{id_mecz}{'-skrocony' if skrocony else ''}.pdf"
        return self._pdf.odpowiedz(html, self.ARKUSZ, nazwa)
