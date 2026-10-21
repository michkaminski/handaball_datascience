from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

from flask import Response, abort, current_app, render_template, request
from flask.views import MethodView

from handball.contracts.pdf_renderer import GeneratorPdfNiedostepny
from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.interface.admin.forms.match_tip_filters import TypowaniaKolejkiForm
from handball.interface.admin.forms.schedule_filters import TerminarzFilterForm, ZapowiedzOpcjeForm
from handball.interface.errors import obsluz_blad_domeny
from handball.interface.view_models.schedule import ZapowiedzMeczuViewModel
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


class ZapowiedzMeczuOdczyt:
    PARAMETRY_POWROTU = frozenset({"id_sezon", "id_rozgrywki", "id_runda", "id_kolejka"})

    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def pobierz(self, id_mecz: int) -> tuple[ZapowiedzMeczuViewModel, ZapowiedzOpcjeForm]:
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
        return (
            self._fabryka.utworz_presenter_zapowiedzi_meczu().przygotuj(zapowiedz),
            formularz,
        )

    def parametry_powrotu(self) -> dict[str, str]:
        return {
            klucz: wartosc
            for klucz, wartosc in request.args.items()
            if klucz in self.PARAMETRY_POWROTU
        }


class ZapowiedzMeczuView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._odczyt = ZapowiedzMeczuOdczyt(fabryka_zaleznosci)

    def get(self, id_mecz: int) -> str:
        zapowiedz, formularz = self._odczyt.pobierz(id_mecz)
        return render_template(
            "admin/schedule/preview.html",
            sekcja_aktywna="terminarz",
            sekcja_glowna="mecze",
            zapowiedz=zapowiedz,
            parametry_powrotu=self._odczyt.parametry_powrotu(),
            formularz=formularz,
            model=request.args.get("model"),
        )


class PdfResponseBuilder:
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def odpowiedz(self, html: str, arkusz: Path, nazwa_pliku: str) -> Response:
        katalog_statyczny = Path(current_app.static_folder or "")
        try:
            pdf = self._fabryka.utworz_renderer_pdf().renderuj(html, [katalog_statyczny / arkusz])
        except GeneratorPdfNiedostepny as wyjatek:
            abort(503, description=str(wyjatek))
        return Response(
            pdf,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{nazwa_pliku}"'},
        )


class ZapowiedzMeczuPdfView(MethodView):
    ARKUSZ = Path("css") / "preview_pdf.css"

    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._odczyt = ZapowiedzMeczuOdczyt(fabryka_zaleznosci)
        self._pdf = PdfResponseBuilder(fabryka_zaleznosci)

    def get(self, id_mecz: int) -> Response:
        zapowiedz, formularz = self._odczyt.pobierz(id_mecz)
        html = render_template(
            "admin/schedule/preview_pdf.html",
            zapowiedz=zapowiedz,
            bez_uwag=bool(formularz.bez_uwag.data),
        )
        return self._pdf.odpowiedz(html, self.ARKUSZ, f"zapowiedz-meczu-{id_mecz}.pdf")


class ProtokolMeczuPdfView(MethodView):
    ARKUSZ = Path("css") / "protocol_pdf.css"

    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._pdf = PdfResponseBuilder(fabryka_zaleznosci)

    def get(self, id_mecz: int) -> Response:
        formularz = ZapowiedzOpcjeForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            protokol = self._fabryka.utworz_serwis_protokolu_meczu().pobierz(
                id_mecz, formularz.do_opcji(), formularz.do_kolejnosci_protokolu()
            )
        except (NieZnalezionoMeczu, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        html = render_template(
            "admin/schedule/protocol_pdf.html",
            protokol=self._fabryka.utworz_presenter_protokolu_meczu().przygotuj(protokol),
        )
        return self._pdf.odpowiedz(html, self.ARKUSZ, f"protokol-meczu-{id_mecz}.pdf")


class ZipResponseBuilder:
    def odpowiedz(self, pliki: dict[str, str], nazwa_pliku: str) -> Response:
        archiwum = BytesIO()
        with zipfile.ZipFile(archiwum, "w", zipfile.ZIP_DEFLATED) as zip_:
            for nazwa, tresc in pliki.items():
                zip_.writestr(nazwa, tresc)
        return Response(
            archiwum.getvalue(),
            mimetype="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{nazwa_pliku}"',
                "Cache-Control": "no-store",
            },
        )


class ProtokolMeczuLiveView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._zip = ZipResponseBuilder()

    def get(self, id_mecz: int) -> Response:
        formularz = ZapowiedzOpcjeForm(request.args)
        if not formularz.validate():
            abort(400, description=str(formularz.errors))
        try:
            protokol = self._fabryka.utworz_serwis_protokolu_meczu().pobierz(
                id_mecz, formularz.do_opcji(), formularz.do_kolejnosci_protokolu()
            )
        except (NieZnalezionoMeczu, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        plik = self._fabryka.utworz_presenter_protokolu_live().przygotuj(protokol)
        html = render_template(
            "admin/schedule/protocol_live.html", dokument=plik.dokument, plik_json=plik.nazwa_json
        )
        return self._zip.odpowiedz(
            {
                f"{plik.nazwa_bazowa}/{plik.nazwa_html}": html,
                f"{plik.nazwa_bazowa}/{plik.nazwa_json}": json.dumps(
                    plik.dokument, ensure_ascii=False, indent=1
                ),
            },
            plik.nazwa_zip,
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
