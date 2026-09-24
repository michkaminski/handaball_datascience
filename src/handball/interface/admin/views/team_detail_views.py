from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoDruzyny
from handball.interface.admin.forms.team_filters import DruzynaFilterForm
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory

ZAKLADKI_MECZOW = {"id_sezon", "rozgrywki", "przeciwnik", "strona", "sortowanie", "zakonczone"}
ZAKLADKI_ZAWODNIKOW = {"zawodnik", "strona_zawodnikow", "sortowanie_zawodnikow"}
ZAKLADKI_ZESTAWIENIA = {"sezon_zestawienia", "rozgrywki_zestawienia", "przeciwnik_zestawienia"}


class DruzynaSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_szczegolow_druzyny()

    def get(self, id_zespol: int) -> str:
        serwis = self._fabryka.utworz_serwis_szczegolow_druzyny()
        analityka = self._fabryka.utworz_analityke_druzyny()
        formularz = DruzynaFilterForm(request.args)
        try:
            szczegoly = serwis.pobierz_szczegoly(id_zespol)
            opcje = serwis.pobierz_opcje_filtrow(id_zespol)
            formularz.id_sezon.choices = [("", "Wszystkie")] + [
                (str(s.wartosc), s.etykieta) for s in opcje.sezony
            ]
            formularz.rozgrywki.choices = [("", "Wszystkie")] + [(n, n) for n in opcje.rozgrywki]
            formularz.sezon_zestawienia.choices = [
                (str(s.wartosc), s.etykieta) for s in opcje.sezony
            ]
            formularz.rozgrywki_zestawienia.choices = formularz.rozgrywki.choices
            if not formularz.validate():
                abort(400, description=str(formularz.errors))
            try:
                filtry = formularz.do_filtrow()
                filtry_zawodnikow = formularz.do_filtrow_zawodnikow()
                filtry_zestawienia = formularz.do_filtrow_zestawienia(
                    opcje.sezony[0].wartosc if opcje.sezony else None
                )
            except ValueError as wyjatek:
                abort(400, description=str(wyjatek))
            mecze = serwis.pobierz_mecze(id_zespol, filtry)
            zawodnicy = serwis.pobierz_zawodnikow(id_zespol, filtry_zawodnikow)
            zestawienie = (
                self._fabryka.utworz_zestawienie_druzyny().pobierz_zestawienie(
                    id_zespol, filtry_zestawienia
                )
                if filtry_zestawienia
                else None
            )
            historia = analityka.pobierz_historie(id_zespol, szczegoly.sezony)
            wynik_analityki = analityka.pobierz_analityke(id_zespol, filtry, szczegoly.sezony)
        except (NieZnalezionoDruzyny, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        zakladka = formularz.zakladka.data
        if "zakladka" not in request.args:
            if ZAKLADKI_ZESTAWIENIA & request.args.keys():
                zakladka = "zestawienie"
            elif ZAKLADKI_ZAWODNIKOW & request.args.keys():
                zakladka = "zawodnicy"
            elif ZAKLADKI_MECZOW & request.args.keys():
                zakladka = "mecze"
        parametry = request.args.to_dict()
        return render_template(
            "admin/teams/detail.html",
            sekcja_aktywna="druzyny",
            szczegoly=self._presenter.przygotuj_szczegoly(szczegoly),
            frekwencja=self._presenter.przygotuj_frekwencje(historia.bilans.frekwencja),
            frekwencja_meczow=self._presenter.przygotuj_frekwencje(
                wynik_analityki.podsumowanie.bilans.frekwencja
            ),
            sezony=self._presenter.przygotuj_sezony(historia.sezony),
            strona=self._presenter.przygotuj_mecze(mecze),
            zawodnicy=self._presenter.przygotuj_zawodnikow(zawodnicy),
            zestawienie=(
                self._presenter.przygotuj_zestawienie(
                    zestawienie,
                    next(
                        (
                            s.etykieta
                            for s in opcje.sezony
                            if s.wartosc == filtry_zestawienia.id_sezon
                        ),
                        "—",
                    ),
                )
                if zestawienie is not None and filtry_zestawienia is not None
                else None
            ),
            sezon_zestawienia=str(filtry_zestawienia.id_sezon) if filtry_zestawienia else "",
            podsumowanie=self._presenter.przygotuj_podsumowanie(wynik_analityki.podsumowanie),
            bramki=self._presenter.przygotuj_analize_bramek(
                wynik_analityki.zdobyte, wynik_analityki.stracone, wynik_analityki.roznica
            ),
            filtry=filtry,
            filtry_zawodnikow=filtry_zawodnikow,
            formularz=formularz,
            aktywna_zakladka=zakladka,
            parametry_meczow={**parametry, "id_zespol": id_zespol, "zakladka": "mecze"},
            parametry_zawodnikow={**parametry, "id_zespol": id_zespol, "zakladka": "zawodnicy"},
        )
