from __future__ import annotations

from handball.contracts.competition_repository import RozgrywkiReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.contracts.venue_repository import HalaReadRepository
from handball.domain.matches import OpcjeFiltrowMeczow


class SlownikiMeczowService:
    def __init__(
        self,
        repozytorium_sezonow: SezonReadRepository,
        repozytorium_rozgrywek: RozgrywkiReadRepository,
        repozytorium_hal: HalaReadRepository,
    ) -> None:
        self._repozytorium_sezonow = repozytorium_sezonow
        self._repozytorium_rozgrywek = repozytorium_rozgrywek
        self._repozytorium_hal = repozytorium_hal

    def pobierz_opcje(self, id_sezon: int | None) -> OpcjeFiltrowMeczow:
        return OpcjeFiltrowMeczow(
            sezony=self._repozytorium_sezonow.pobierz_wszystkie(),
            rozgrywki=self._repozytorium_rozgrywek.pobierz_nazwy(id_sezon),
            hale=self._repozytorium_hal.pobierz_wszystkie(),
        )
