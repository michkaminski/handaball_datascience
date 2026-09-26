from __future__ import annotations

from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.interface.admin.forms.match_tip_filters import TypowaniaKolejkiForm
from handball.interface.admin.forms.schedule_filters import TerminarzFilterForm, ZapowiedzOpcjeForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class TerminarzView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = TerminarzFilterForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        serwis = self._fabryka.utworz_serwis_terminarza()
        try:
            opcje = serwis.pobierz_opcje(formularz.do_wyboru())
            filtry = opcje.filtry
            terminarz = serwis.pobierz_terminarz(filtry) if filtry else None
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            "admin/schedule/list.html",
            sekcja_aktywna="terminarz",
            sekcja_glowna="mecze",
            opcje=opcje,
            terminarz=(
                self._fabryka.utworz_presenter_terminarza().przygotuj(terminarz)
                if terminarz
                else None
            ),
            parametry=request.args.to_dict(),
        )


class ZapowiedzMeczuView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self, id_mecz: int) -> str:
        katalog = self._fabryka.utworz_katalog_modeli_prognoz()
        wersja = request.args.get("model") or katalog.domyslna_wersja
        formularz = ZapowiedzOpcjeForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            zapowiedz = self._fabryka.utworz_serwis_zapowiedzi_meczu().pobierz(
                id_mecz, wersja, formularz.do_opcji()
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except (NieZnalezionoMeczu, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        parametry_powrotu = {
            klucz: wartosc
            for klucz, wartosc in request.args.items()
            if klucz in {"id_sezon", "id_rozgrywki", "id_runda", "id_kolejka"}
        }
        return render_template(
            "admin/schedule/preview.html",
            sekcja_aktywna="terminarz",
            sekcja_glowna="mecze",
            zapowiedz=self._fabryka.utworz_presenter_zapowiedzi_meczu().przygotuj(zapowiedz),
            parametry_powrotu=parametry_powrotu,
            formularz=formularz,
            model=request.args.get("model"),
        )


class TypowaniaKolejkiView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = TypowaniaKolejkiForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        katalog = self._fabryka.utworz_katalog_modeli_prognoz()
        try:
            typowania = self._fabryka.utworz_typowania_kolejki().pobierz(
                formularz.do_filtrow(), formularz.model.data or katalog.domyslna_wersja
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        parametry_powrotu = {
            klucz: wartosc
            for klucz, wartosc in request.args.items()
            if klucz in {"id_sezon", "id_rozgrywki", "id_runda"}
        }
        return render_template(
            "admin/schedule/tips.html",
            sekcja_aktywna="terminarz",
            sekcja_glowna="mecze",
            typowania=self._fabryka.utworz_presenter_typowan().przygotuj_kolejke(typowania),
            parametry_powrotu=parametry_powrotu,
        )
