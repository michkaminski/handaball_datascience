from typing import Protocol

from handball.domain.referee_details import (
    FiltryMeczowSedziego,
    StatystykiSedziego,
    StronaMeczowSedziego,
    SzczegolySedziego,
)


class SzczegolySedziegoReadRepository(Protocol):
    def pobierz_szczegoly(self, id_sedzia: int) -> SzczegolySedziego: ...

    def pobierz_mecze(
        self, id_sedzia: int, filtry: FiltryMeczowSedziego
    ) -> StronaMeczowSedziego: ...

    def pobierz_statystyki(
        self, id_sedzia: int, filtry: FiltryMeczowSedziego
    ) -> StatystykiSedziego: ...
