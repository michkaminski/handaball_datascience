from __future__ import annotations

from handball.contracts.competition_repository import RozgrywkiReadRepository
from handball.contracts.match_stage_repository import EtapMeczowReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.contracts.venue_repository import HalaReadRepository
from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.matches import OpcjeFiltrowMeczow


class SlownikiMeczowService:
    def __init__(
        self,
        repozytorium_sezonow: SezonReadRepository,
        repozytorium_rozgrywek: RozgrywkiReadRepository,
        repozytorium_hal: HalaReadRepository,
        repozytorium_etapow: EtapMeczowReadRepository,
        kolejnosc: KolejnoscRozgrywekPolicy,
    ) -> None:
        self._kolejnosc = kolejnosc
        self._repozytorium_sezonow = repozytorium_sezonow
        self._repozytorium_rozgrywek = repozytorium_rozgrywek
        self._repozytorium_hal = repozytorium_hal
        self._repozytorium_etapow = repozytorium_etapow

    def pobierz_opcje(self, id_sezon: int | None) -> OpcjeFiltrowMeczow:
        return OpcjeFiltrowMeczow(
            sezony=self._repozytorium_sezonow.pobierz_wszystkie(),
            rozgrywki=self._kolejnosc.uporzadkuj_nazwy(
                self._repozytorium_rozgrywek.pobierz_nazwy(id_sezon)
            ),
            hale=self._repozytorium_hal.pobierz_wszystkie(),
            rundy=self._repozytorium_etapow.pobierz_rundy(),
            kolejki=self._repozytorium_etapow.pobierz_kolejki(),
        )
