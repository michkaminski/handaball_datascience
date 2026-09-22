from typing import Any

from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.classifications import FiltryKlasyfikacji, StronaKlasyfikacji
from handball.domain.errors import BladOdczytuDanych
from handball.interface.admin.forms.classification_filters import KlasyfikacjaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory
from handball.services.classification_service import KlasyfikacjaService


class KlasyfikacjaListView(MethodView):
    szablon: str
    sekcja: str
    sortowanie: tuple[str, ...]
    domyslne_sortowanie: str

    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = KlasyfikacjaFilterForm(request.args)
        formularz.sortowanie.choices = [(k + p, k + p) for p in self.sortowanie for k in ("", "-")]
        try:
            serwis = self._fabryka.utworz_serwis_klasyfikacji()
            formularz.id_sezon.choices = [("", "Wszystkie")] + [
                (o.wartosc, o.etykieta) for o in serwis.pobierz_opcje_sezonow()
            ]
            formularz.id_rozgrywki.choices = [("", "Wszystkie")] + [
                (o.wartosc, o.etykieta)
                for o in serwis.pobierz_opcje_rozgrywek(formularz.id_sezon.data)
            ]
            if not request.args.get("sortowanie"):
                formularz.sortowanie.data = self.domyslne_sortowanie
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            filtry = formularz.do_filtrow()
            strona = self.pobierz_strone(serwis, filtry)
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            self.szablon,
            sekcja_aktywna=self.sekcja,
            formularz=formularz,
            filtry=filtry,
            strona=strona,
        )

    def pobierz_strone(
        self, serwis: KlasyfikacjaService, filtry: FiltryKlasyfikacji
    ) -> StronaKlasyfikacji[Any]:
        raise NotImplementedError


class SkladListView(KlasyfikacjaListView):
    szablon = "admin/rosters/list.html"
    sekcja = "sklady"
    sortowanie = ("sezon", "druzyna", "rozgrywki")
    domyslne_sortowanie = "-sezon"

    def pobierz_strone(
        self, serwis: KlasyfikacjaService, filtry: FiltryKlasyfikacji
    ) -> StronaKlasyfikacji[Any]:
        return serwis.pobierz_sklady(filtry)


class StrzelecListView(KlasyfikacjaListView):
    szablon = "admin/scorers/list.html"
    sekcja = "strzelcy"
    sortowanie = (
        "sezon",
        "rozgrywki",
        "miejsce",
        "zawodnik",
        "druzyna",
        "mecze",
        "bramki",
        "srednia",
    )
    domyslne_sortowanie = "miejsce"

    def pobierz_strone(
        self, serwis: KlasyfikacjaService, filtry: FiltryKlasyfikacji
    ) -> StronaKlasyfikacji[Any]:
        return serwis.pobierz_strzelcow(filtry)


class TabelaListView(KlasyfikacjaListView):
    szablon = "admin/standings/list.html"
    sekcja = "tabele"
    sortowanie = ("sezon", "rozgrywki", "tabela", "grupa")
    domyslne_sortowanie = "-sezon"

    def pobierz_strone(
        self, serwis: KlasyfikacjaService, filtry: FiltryKlasyfikacji
    ) -> StronaKlasyfikacji[Any]:
        return serwis.pobierz_tabele(filtry)


class SkladSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self, id_zespol_sezon: int) -> str:
        try:
            serwis = self._fabryka.utworz_serwis_klasyfikacji()
            szczegoly = serwis.pobierz_szczegoly_skladu(id_zespol_sezon)
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        if szczegoly is None:
            abort(404)
        return render_template(
            "admin/rosters/detail.html",
            sekcja_aktywna="sklady",
            szczegoly=self._fabryka.utworz_presenter_skladu().przygotuj(szczegoly),
        )


class TabelaSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self, id_tabela_grupa: int) -> str:
        try:
            serwis = self._fabryka.utworz_serwis_klasyfikacji()
            szczegoly = serwis.pobierz_szczegoly_tabeli(id_tabela_grupa)
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        if szczegoly is None:
            abort(404)
        return render_template(
            "admin/standings/detail.html", sekcja_aktywna="tabele", szczegoly=szczegoly
        )
