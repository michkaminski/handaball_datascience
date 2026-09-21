from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoSedziego
from handball.interface.admin.forms.referee_detail_filters import MeczeSedziegoFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class SedziaSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_szczegolow_sedziego()

    def get(self, id_sedzia: int) -> str:
        formularz = MeczeSedziegoFilterForm(request.args)
        try:
            sezony, rozgrywki = self._fabryka.utworz_slowniki_zawodnikow().pobierz_opcje()
            formularz.sezon.choices = [("", "Wszystkie")] + [
                (str(sezon.wartosc), sezon.etykieta) for sezon in sezony
            ]
            formularz.rozgrywki.choices = [("", "Wszystkie")] + [
                (nazwa, nazwa) for nazwa in rozgrywki
            ]
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            filtry = formularz.do_filtrow()
            serwis = self._fabryka.utworz_serwis_szczegolow_sedziego()
            szczegoly = serwis.pobierz_szczegoly(id_sedzia)
            mecze = serwis.pobierz_mecze(id_sedzia, filtry)
            statystyki = serwis.pobierz_statystyki(id_sedzia, filtry)
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except (NieZnalezionoSedziego, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        aktywna_zakladka = request.args.get("zakladka", "dane")
        if aktywna_zakladka not in {"dane", "mecze", "statystyki"}:
            abort(400, description="Niepoprawna zakładka.")
        return render_template(
            "admin/referees/detail.html",
            sekcja_aktywna="sedziowie",
            szczegoly=self._presenter.przygotuj_szczegoly(szczegoly),
            mecze=self._presenter.przygotuj_mecze(mecze),
            statystyki=self._presenter.przygotuj_statystyki(statystyki),
            formularz=formularz,
            filtry=filtry,
            aktywna_zakladka=aktywna_zakladka,
            parametry=request.args.to_dict(),
        )
