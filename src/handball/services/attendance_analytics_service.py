from handball.contracts.attendance_analytics_repository import FrekwencjaReadRepository
from handball.domain.attendance_analytics import (
    LIMIT_RANKINGU,
    LIMIT_REKORDOW,
    FiltryFrekwencji,
    FrekwencjaCalculator,
    OpcjeFiltrowFrekwencji,
    PodsumowanieFrekwencji,
    RaportFrekwencji,
)
from handball.domain.attendance_calendar import KalendarzFrekwencjiCalculator
from handball.domain.attendance_cities import MiastaFrekwencjiCalculator
from handball.domain.attendance_data_science import FrekwencjaDataScienceCalculator
from handball.domain.attendance_opponents import (
    LIMIT_PRZECIWNIKOW,
    PrzeciwnicyFrekwencjiCalculator,
    RankingPrzeciwnikow,
)
from handball.domain.attendance_records import LIMIT_REKORDOW_GRUPOWYCH
from handball.domain.attendance_sample import LIMIT_PROBKI


class FrekwencjaService:
    def __init__(
        self,
        repozytorium: FrekwencjaReadRepository,
        kalkulator: FrekwencjaCalculator,
        przeciwnicy: PrzeciwnicyFrekwencjiCalculator,
        kalendarz: KalendarzFrekwencjiCalculator,
        data_science: FrekwencjaDataScienceCalculator,
        miasta: MiastaFrekwencjiCalculator,
    ) -> None:
        self._repozytorium = repozytorium
        self._kalkulator = kalkulator
        self._przeciwnicy = przeciwnicy
        self._kalendarz = kalendarz
        self._data_science = data_science
        self._miasta = miasta

    def pobierz_opcje(self) -> OpcjeFiltrowFrekwencji:
        return self._repozytorium.pobierz_opcje()

    def pobierz_raport(self, filtry: FiltryFrekwencji) -> RaportFrekwencji:
        podsumowanie = self._repozytorium.pobierz_podsumowanie(filtry)
        trend = self._kalkulator.zbuduj_trend(self._repozytorium.pobierz_sezony(filtry))
        para = self._kalkulator.para_sezonow(trend, filtry.id_sezon)
        srednie_klubow = self._repozytorium.pobierz_srednie_klubow(filtry) if para else ()
        ranking = self._kalkulator.uloz_ranking(
            self._repozytorium.pobierz_kluby(filtry), srednie_klubow, para, LIMIT_RANKINGU
        )
        probka = self._repozytorium.pobierz_probke(filtry, LIMIT_PROBKI)
        return RaportFrekwencji(
            filtry=filtry,
            podsumowanie=podsumowanie,
            trend=trend,
            para_sezonow=para,
            ranking=ranking,
            rekordy=self._repozytorium.pobierz_rekordy(filtry, LIMIT_REKORDOW),
            rekordy_rozszerzone=self._repozytorium.pobierz_rekordy_rozszerzone(
                filtry, LIMIT_REKORDOW_GRUPOWYCH
            ),
            przeciwnicy=self._ranking_przeciwnikow(filtry, podsumowanie),
            kalendarz=self._kalendarz.zbuduj(self._repozytorium.pobierz_kalendarz(filtry)),
            data_science=self._data_science.analizuj(probka, podsumowanie.znane, filtry.id_zespol),
            miasta=self._miasta.zbuduj(self._repozytorium.pobierz_miasta(filtry)),
        )

    def _ranking_przeciwnikow(
        self, filtry: FiltryFrekwencji, podsumowanie: PodsumowanieFrekwencji
    ) -> RankingPrzeciwnikow:
        if filtry.id_zespol is None:
            return self._przeciwnicy.nieaktywny()
        return self._przeciwnicy.uloz(
            self._repozytorium.pobierz_przeciwnikow(filtry),
            podsumowanie.srednia,
            LIMIT_PRZECIWNIKOW,
        )
