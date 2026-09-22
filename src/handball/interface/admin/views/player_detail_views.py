from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoZawodnika
from handball.interface.admin.forms.player_match_filters import MeczeZawodnikaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class ZawodnikSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_szczegolow_zawodnika()

    def get(self, id_zawodnik: int) -> str:
        serwis = self._fabryka.utworz_serwis_szczegolow_zawodnika()
        analityka_serwis = self._fabryka.utworz_analityke_szczegolow_zawodnika()
        formularz = MeczeZawodnikaFilterForm(request.args)
        try:
            szczegoly = serwis.pobierz_szczegoly(id_zawodnik)
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
            mecze = serwis.pobierz_mecze(id_zawodnik, filtry)
            podsumowanie = analityka_serwis.pobierz_podsumowanie(id_zawodnik, filtry)
            forma = analityka_serwis.pobierz_forme(id_zawodnik, filtry)
        except (NieZnalezionoZawodnika, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        zakladka = formularz.zakladka.data
        if "zakladka" not in request.args and request.args:
            zakladka = "mecze"
        return render_template(
            "admin/players/detail.html",
            sekcja_aktywna="zawodnicy",
            szczegoly=self._presenter.przygotuj_szczegoly(szczegoly),
            strona=self._presenter.przygotuj_mecze(mecze),
            podsumowanie=self._presenter.przygotuj_podsumowanie(podsumowanie),
            forma=self._presenter.przygotuj_forme(forma),
            filtry=filtry,
            formularz=formularz,
            aktywna_zakladka=zakladka,
            parametry_paginacji={
                **request.args.to_dict(),
                "id_zawodnik": id_zawodnik,
                "zakladka": "mecze",
            },
        )
