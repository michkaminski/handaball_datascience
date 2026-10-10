from typing import Protocol

from handball.domain.attendance_analytics import (
    FiltryFrekwencji,
    KlubFrekwencji,
    OpcjeFiltrowFrekwencji,
    PodsumowanieFrekwencji,
    SezonFrekwencji,
    SredniaKlubuSezonu,
)
from handball.domain.attendance_calendar import DaneKalendarza
from handball.domain.attendance_cities import DaneMiast
from handball.domain.attendance_opponents import PrzeciwnikFrekwencji
from handball.domain.attendance_records import RekordFrekwencji, RekordyRozszerzoneFrekwencji
from handball.domain.attendance_sample import MeczProbki


class FrekwencjaReadRepository(Protocol):
    def pobierz_opcje(self) -> OpcjeFiltrowFrekwencji: ...

    def pobierz_podsumowanie(self, filtry: FiltryFrekwencji) -> PodsumowanieFrekwencji: ...

    def pobierz_sezony(self, filtry: FiltryFrekwencji) -> tuple[SezonFrekwencji, ...]: ...

    def pobierz_kluby(self, filtry: FiltryFrekwencji) -> tuple[KlubFrekwencji, ...]: ...

    def pobierz_srednie_klubow(
        self, filtry: FiltryFrekwencji
    ) -> tuple[SredniaKlubuSezonu, ...]: ...

    def pobierz_rekordy(
        self, filtry: FiltryFrekwencji, limit: int
    ) -> tuple[RekordFrekwencji, ...]: ...

    def pobierz_przeciwnikow(
        self, filtry: FiltryFrekwencji
    ) -> tuple[PrzeciwnikFrekwencji, ...]: ...

    def pobierz_kalendarz(self, filtry: FiltryFrekwencji) -> DaneKalendarza: ...

    def pobierz_miasta(self, filtry: FiltryFrekwencji) -> DaneMiast: ...

    def pobierz_rekordy_rozszerzone(
        self, filtry: FiltryFrekwencji, limit: int
    ) -> RekordyRozszerzoneFrekwencji: ...

    def pobierz_probke(self, filtry: FiltryFrekwencji, limit: int) -> tuple[MeczProbki, ...]: ...
