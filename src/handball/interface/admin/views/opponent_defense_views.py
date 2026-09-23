from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoZawodnika
from handball.interface.admin.forms.opponent_defense_filters import DefensywaRywalaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class DefensywaRywalaZawodnikaView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self, id_zawodnik: int) -> str:
        serwis_zawodnika = self._fabryka.utworz_serwis_szczegolow_zawodnika()
        serwis = self._fabryka.utworz_serwis_defensywy_rywala()
        presenter = self._fabryka.utworz_presenter_defensywy_rywala()
        formularz = DefensywaRywalaFilterForm(request.args)
        try:
            szczegoly = serwis_zawodnika.pobierz_szczegoly(id_zawodnik)
            sezony, rozgrywki = self._fabryka.utworz_slowniki_zawodnikow().pobierz_opcje()
            formularz.id_sezon.choices = [("", "Wszystkie")] + [
                (str(s.wartosc), s.etykieta) for s in sezony
            ]
            formularz.rozgrywki.choices = [("", "Wszystkie")] + [(n, n) for n in rozgrywki]
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            try:
                filtry = formularz.do_filtrow()
            except ValueError as wyjatek:
                abort(400, description=str(wyjatek))
            analiza = serwis.pobierz_analize(id_zawodnik, filtry)
        except (NieZnalezionoZawodnika, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        nazwa = " ".join(n for n in (szczegoly.imie, szczegoly.nazwisko) if n) or (
            f"Zawodnik #{id_zawodnik}"
        )
        widok = presenter.przygotuj_szczegoly(
            analiza, nazwa, filtry, formularz.id_mecz_przykladu.data
        )
        return render_template(
            "admin/players/defensywa_rywali.html",
            sekcja_aktywna="zawodnicy",
            id_zawodnik=id_zawodnik,
            analiza=widok,
            formularz=formularz,
        )
