from handball.contracts.referee_detail_repository import SzczegolySedziegoReadRepository
from handball.domain.referee_details import (
    FiltryMeczowSedziego,
    StatystykiSedziego,
    StronaMeczowSedziego,
    SzczegolySedziego,
)


class SzczegolySedziegoService:
    def __init__(self, repozytorium: SzczegolySedziegoReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_szczegoly(self, id_sedzia: int) -> SzczegolySedziego:
        return self._repozytorium.pobierz_szczegoly(id_sedzia)

    def pobierz_mecze(self, id_sedzia: int, filtry: FiltryMeczowSedziego) -> StronaMeczowSedziego:
        return self._repozytorium.pobierz_mecze(id_sedzia, filtry)

    def pobierz_statystyki(
        self, id_sedzia: int, filtry: FiltryMeczowSedziego
    ) -> StatystykiSedziego:
        return self._repozytorium.pobierz_statystyki(id_sedzia, filtry)
