from typing import Protocol

from handball.domain.venue_details import (
    FiltryZawodnikowHali,
    LimityStatystykHali,
    StatystykiHali,
    StronaZawodnikowHali,
    SzczegolyHali,
)


class SzczegolyHaliReadRepository(Protocol):
    def pobierz_szczegoly(self, id_hala: int) -> SzczegolyHali: ...

    def pobierz_zawodnikow(
        self, id_hala: int, filtry: FiltryZawodnikowHali
    ) -> StronaZawodnikowHali: ...

    def pobierz_statystyki(self, id_hala: int, limity: LimityStatystykHali) -> StatystykiHali: ...
