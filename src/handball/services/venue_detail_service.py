from handball.contracts.venue_detail_repository import SzczegolyHaliReadRepository
from handball.domain.venue_details import (
    FiltryZawodnikowHali,
    LimityStatystykHali,
    StatystykiHali,
    StronaZawodnikowHali,
    SzczegolyHali,
)


class SzczegolyHaliService:
    def __init__(self, repozytorium: SzczegolyHaliReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_szczegoly(self, id_hala: int) -> SzczegolyHali:
        return self._repozytorium.pobierz_szczegoly(id_hala)

    def pobierz_zawodnikow(
        self, id_hala: int, filtry: FiltryZawodnikowHali
    ) -> StronaZawodnikowHali:
        return self._repozytorium.pobierz_zawodnikow(id_hala, filtry)

    def pobierz_statystyki(self, id_hala: int, limity: LimityStatystykHali) -> StatystykiHali:
        return self._repozytorium.pobierz_statystyki(id_hala, limity)
