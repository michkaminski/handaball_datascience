from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoPrognozy
from handball.interface.admin.forms.match_prediction_filters import (
    PrognozyMeczowFilterForm,
    ZakresRaportuForm,
)
from handball.interface.admin.forms.match_tip_filters import TypowaniaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.interface.report_catalog import KATALOG_RAPORTOW
from handball.request_dependencies import ZaleznosciZadaniaFactory


class RaportyListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        return render_template(
            "admin/reports/list.html",
            sekcja_aktywna="raporty",
            sekcja_glowna="raporty",
            raporty=KATALOG_RAPORTOW,
        )


class PrognozyMeczowListView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        katalog = self._fabryka.utworz_katalog_modeli_prognoz()
        presenter = self._fabryka.utworz_presenter_prognoz_meczow()
        formularz = PrognozyMeczowFilterForm(request.args)
        formularz.model.choices = [(opis.wersja, opis.nazwa) for opis in katalog.modele()]
        formularz.poziom.choices = [("", "Wszystkie")] + [
            (opcja.wartosc, opcja.etykieta) for opcja in presenter.opcje_poziomow()
        ]
        formularz.plec.choices = [("", "Wszystkie")] + [
            (opcja.wartosc, opcja.etykieta) for opcja in presenter.opcje_plci()
        ]
        formularz.ocena.choices = [
            (opcja.wartosc, opcja.etykieta) for opcja in presenter.opcje_klas()
        ]
        formularz.wynik_1x2.choices = [
            (opcja.wartosc, opcja.etykieta) for opcja in presenter.opcje_typow()
        ]
        formularz.ocena_wyniku.choices = [
            (opcja.wartosc, opcja.etykieta) for opcja in presenter.opcje_klas_wyniku()
        ]
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            filtry = formularz.do_filtrow(katalog.domyslna_wersja)
            raport = self._fabryka.utworz_raport_prognoz_meczow().pobierz_raport(filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        formularz.sezon.choices = [("", "Wszystkie")] + [
            (opcja.wartosc, opcja.etykieta) for opcja in presenter.opcje_sezonow(raport.sezony)
        ]
        model_widoku = presenter.przygotuj_raport(raport)
        return render_template(
            "admin/reports/match_predictions/list.html",
            sekcja_aktywna="prognozy_meczow",
            sekcja_glowna="raporty",
            raport=model_widoku,
            formularz=formularz,
            filtry=filtry,
            strona=model_widoku.strona,
            parametry=request.args.to_dict(flat=False),
        )


class PrognozaMeczuSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self, id_mecz: int) -> str:
        katalog = self._fabryka.utworz_katalog_modeli_prognoz()
        wersja = request.args.get("model") or katalog.domyslna_wersja
        formularz = ZakresRaportuForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            szczegoly = self._fabryka.utworz_szczegoly_prognozy_meczu().pobierz(
                wersja, id_mecz, formularz.do_zakresu()
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except (NieZnalezionoPrognozy, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/reports/match_predictions/detail.html",
            sekcja_aktywna="prognozy_meczow",
            sekcja_glowna="raporty",
            szczegoly=self._fabryka.utworz_presenter_prognoz_meczow().przygotuj_szczegoly(
                szczegoly
            ),
            parametry_powrotu=request.args.to_dict(flat=False),
            sezony_raportu=formularz.sezony_raportu.data,
        )


class TypowaniaMeczowView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = TypowaniaFilterForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        serwis = self._fabryka.utworz_raport_typowan()
        try:
            filtry = serwis.filtry(formularz.do_wyboru())
            raport = serwis.pobierz_raport(filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/reports/match_tips/list.html",
            sekcja_aktywna="typowania_meczow",
            sekcja_glowna="raporty",
            raport=self._fabryka.utworz_presenter_typowan().przygotuj_raport(raport),
            filtry=filtry,
        )
