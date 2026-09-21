from flask import abort, render_template, request
from flask.views import MethodView

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoHali
from handball.domain.matches import FiltryMeczow
from handball.domain.venue_details import LimityStatystykHali
from handball.interface.admin.forms.venue_detail_filters import (
    MeczeHaliFilterForm,
    ZawodnicyHaliFilterForm,
)
from handball.interface.errors import obsluz_blad_domeny
from handball.request_dependencies import ZaleznosciZadaniaFactory


class HalaSzczegolyView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci
        self._presenter = fabryka_zaleznosci.utworz_presenter_szczegolow_hali()
        self._mecz_presenter = fabryka_zaleznosci.utworz_presenter_meczow()

    def get(self, id_hala: int) -> str:
        formularz_meczow = MeczeHaliFilterForm(request.args)
        formularz_zawodnikow = ZawodnicyHaliFilterForm(request.args)
        try:
            sezony, rozgrywki = self._fabryka.utworz_slowniki_zawodnikow().pobierz_opcje()
            formularz_meczow.m_sezon.choices = [("", "Wszystkie")] + [
                (str(s.wartosc), s.etykieta) for s in sezony
            ]
            formularz_meczow.m_rozgrywki.choices = [("", "Wszystkie")] + [(n, n) for n in rozgrywki]
            if not formularz_meczow.validate() or not formularz_zawodnikow.validate():
                abort(
                    400,
                    description=str(
                        {
                            **formularz_meczow.errors,
                            **formularz_zawodnikow.errors,
                        }
                    ),
                )
            filtry_meczow = formularz_meczow.do_filtrow()
            filtry_zawodnikow = formularz_zawodnikow.do_filtrow()
            serwis = self._fabryka.utworz_serwis_szczegolow_hali()
            szczegoly = serwis.pobierz_szczegoly(id_hala)
            mecze = self._fabryka.utworz_serwis_meczow().pobierz_liste(
                FiltryMeczow(
                    id_sezon=filtry_meczow.id_sezon,
                    rozgrywki=filtry_meczow.rozgrywki,
                    id_hala=id_hala,
                    szukaj_druzyny=filtry_meczow.druzyna,
                    strona=filtry_meczow.strona,
                    rozmiar_strony=filtry_meczow.rozmiar_strony,
                    sortowanie=filtry_meczow.sortowanie,
                    tylko_rozegrane=True,
                )
            )
            zawodnicy = serwis.pobierz_zawodnikow(id_hala, filtry_zawodnikow)
            statystyki = serwis.pobierz_statystyki(
                id_hala,
                LimityStatystykHali(
                    druzyny=None if request.args.get("wszystkie_druzyny") == "1" else 10,
                    rozgrywki=None if request.args.get("wszystkie_rozgrywki") == "1" else 10,
                    zawodnicy=None if request.args.get("wszyscy_zawodnicy") == "1" else 10,
                    skuteczni_zawodnicy=(
                        None if request.args.get("wszyscy_skuteczni") == "1" else 10
                    ),
                ),
            )
        except ValueError as wyjatek:
            abort(400, description=str(wyjatek))
        except (NieZnalezionoHali, BladOdczytuDanych) as wyjatek:
            obsluz_blad_domeny(wyjatek)
        aktywna_zakladka = request.args.get("zakladka", "dane")
        if aktywna_zakladka not in {"dane", "mecze", "zawodnicy", "statystyki"}:
            abort(400, description="Niepoprawna zakładka.")
        return render_template(
            "admin/venues/detail.html",
            sekcja_aktywna="hale",
            szczegoly=self._presenter.przygotuj_szczegoly(szczegoly),
            mecze=self._mecz_presenter.przygotuj_liste(mecze),
            zawodnicy=self._presenter.przygotuj_zawodnikow(zawodnicy),
            statystyki=self._presenter.przygotuj_statystyki(statystyki),
            formularz_meczow=formularz_meczow,
            formularz_zawodnikow=formularz_zawodnikow,
            filtry_meczow=filtry_meczow,
            filtry_zawodnikow=filtry_zawodnikow,
            aktywna_zakladka=aktywna_zakladka,
            parametry=request.args.to_dict(),
        )
