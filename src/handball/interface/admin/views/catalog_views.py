from typing import Any

from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.catalogs import FiltryKatalogu, StronaKatalogu
from handball.domain.errors import BladOdczytuDanych
from handball.interface.admin.forms.catalog_filters import KatalogFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory
from handball.services.catalog_service import KatalogService


class KatalogListView(MethodView):
    szablon: str
    sekcja: str
    sortowanie: tuple[str, ...]
    domyslne_sortowanie = "nazwa"

    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> str:
        formularz = KatalogFilterForm(request.args)
        formularz.sortowanie.choices = [
            (kierunek + pole, kierunek + pole) for pole in self.sortowanie for kierunek in ("", "-")
        ]
        try:
            serwis = self._fabryka.utworz_serwis_katalogu()
            formularz.id_sezon.choices = [("", "Wszystkie")] + [
                (opcja.wartosc, opcja.etykieta) for opcja in serwis.pobierz_opcje_sezonow()
            ]
            if not request.args.get("sortowanie"):
                formularz.sortowanie.data = self.domyslne_sortowanie
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            filtry = formularz.do_filtrow()
            strona = self.pobierz_strone(serwis, filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except BladOdczytuDanych as wyjatek:
            obsluz_blad_domeny(wyjatek)
        return render_template(
            self.szablon,
            sekcja_aktywna=self.sekcja,
            formularz=formularz,
            filtry=filtry,
            strona=strona,
        )

    def pobierz_strone(self, serwis: KatalogService, filtry: FiltryKatalogu) -> StronaKatalogu[Any]:
        raise NotImplementedError


class SezonListView(KatalogListView):
    szablon = "admin/seasons/list.html"
    sekcja = "sezony"
    sortowanie = ("id", "nazwa", "rok_rozpoczecia", "liczba_rozgrywek", "stan", "liczba_meczow")
    domyslne_sortowanie = "-rok_rozpoczecia"

    def pobierz_strone(self, serwis: KatalogService, filtry: FiltryKatalogu) -> StronaKatalogu[Any]:
        return serwis.pobierz_sezony(filtry)


class RozgrywkiListView(KatalogListView):
    szablon = "admin/competitions/list.html"
    sekcja = "rozgrywki"
    sortowanie = ("id", "sezon", "nazwa", "plec", "liczba_zespolow", "liczba_meczow")

    def pobierz_strone(self, serwis: KatalogService, filtry: FiltryKatalogu) -> StronaKatalogu[Any]:
        return serwis.pobierz_rozgrywki(filtry)


class DruzynaListView(KatalogListView):
    szablon = "admin/teams/list.html"
    sekcja = "druzyny"
    sortowanie = ("id", "sezon", "nazwa", "plec", "miasto", "wycofany", "liczba_meczow")

    def pobierz_strone(self, serwis: KatalogService, filtry: FiltryKatalogu) -> StronaKatalogu[Any]:
        return serwis.pobierz_druzyny(filtry)


class SedziaListView(KatalogListView):
    szablon = "admin/referees/list.html"
    sekcja = "sedziowie"
    sortowanie = ("id", "nazwisko", "miasto", "liczba_meczow")
    domyslne_sortowanie = "nazwisko"

    def pobierz_strone(self, serwis: KatalogService, filtry: FiltryKatalogu) -> StronaKatalogu[Any]:
        return serwis.pobierz_sedziow(filtry)
