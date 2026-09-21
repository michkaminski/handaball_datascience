from handball.domain.referee_details import (
    StatystykiSedziego,
    StronaMeczowSedziego,
    SzczegolySedziego,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.view_models.referee_details import (
    MeczSedziegoViewModel,
    PasekSedziegoViewModel,
    StatystykiSedziegoViewModel,
    StronaMeczowSedziegoViewModel,
    SzczegolySedziegoViewModel,
)


class SzczegolySedziegoPresenter:
    def __init__(self, formatowanie: MeczFormat) -> None:
        self._format = formatowanie

    def przygotuj_szczegoly(self, dane: SzczegolySedziego) -> SzczegolySedziegoViewModel:
        return SzczegolySedziegoViewModel(
            dane.id_sedzia,
            dane.nazwa or f"Sędzia #{dane.id_sedzia}",
            self._format.tekst(dane.miasto),
            self._format.data(dane.pierwszy_mecz),
            self._format.data(dane.ostatni_mecz),
            dane.liczba_meczow,
            dane.liczba_sezonow,
            dane.liczba_rozgrywek,
            dane.liczba_druzyn,
        )

    def przygotuj_mecze(self, dane: StronaMeczowSedziego) -> StronaMeczowSedziegoViewModel:
        return StronaMeczowSedziegoViewModel(
            [
                MeczSedziegoViewModel(
                    mecz.id_mecz,
                    self._format.data(mecz.data),
                    mecz.sezon,
                    mecz.rozgrywki,
                    self._format.tekst(mecz.gospodarz),
                    f"{mecz.wynik_gospodarza}:{mecz.wynik_goscia}"
                    if mecz.wynik_gospodarza is not None and mecz.wynik_goscia is not None
                    else "—",
                    self._format.tekst(mecz.gosc),
                    mecz.partnerzy,
                )
                for mecz in dane.pozycje
            ],
            dane.liczba_wszystkich,
            dane.strona,
            dane.rozmiar_strony,
        )

    def przygotuj_statystyki(self, dane: StatystykiSedziego) -> StatystykiSedziegoViewModel:
        return StatystykiSedziegoViewModel(
            dane.liczba_meczow,
            dane.liczba_sezonow,
            dane.liczba_rozgrywek,
            dane.liczba_druzyn,
            dane.sezony,
            dane.rozgrywki,
            dane.sezon_rozgrywki,
            dane.druzyny,
            dane.partnerzy,
            self._paski([(x.sezon, x.mecze) for x in dane.sezony]),
            self._paski([(x.rozgrywki, x.mecze) for x in dane.rozgrywki[:10]]),
            self._paski([(x.druzyna, x.mecze) for x in dane.druzyny[:10]]),
            self._paski([(x.sedzia, x.wspolne_mecze) for x in dane.partnerzy[:10]]),
        )

    def _paski(self, dane: list[tuple[str, int]]) -> list[PasekSedziegoViewModel]:
        maksimum = max((wartosc for _, wartosc in dane), default=0)
        return [
            PasekSedziegoViewModel(
                etykieta,
                wartosc,
                max(3, round(wartosc * 100 / maksimum)) if maksimum else 0,
            )
            for etykieta, wartosc in dane
        ]
