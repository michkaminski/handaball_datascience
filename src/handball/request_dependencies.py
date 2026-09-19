from __future__ import annotations

from collections.abc import Callable
from typing import cast

from sqlalchemy.orm import Session

from handball.contracts.competition_repository import RozgrywkiReadRepository
from handball.contracts.match_repository import MeczReadRepository
from handball.contracts.match_stage_repository import EtapMeczowReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.contracts.venue_repository import HalaReadRepository
from handball.extensions import baza_danych
from handball.infrastructure.repositories.competition_repository import (
    RozgrywkiSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository
from handball.infrastructure.repositories.match_stage_repository import (
    EtapMeczowSQLAlchemyRepository,
)
from handball.infrastructure.repositories.season_repository import SezonSQLAlchemyRepository
from handball.infrastructure.repositories.venue_repository import HalaSQLAlchemyRepository
from handball.services.match_dictionary_service import SlownikiMeczowService
from handball.services.match_service import MeczService


class ZaleznosciZadaniaFactory:
    def __init__(
        self,
        fabryka_repozytorium_meczow: Callable[[], MeczReadRepository] | None = None,
        fabryka_repozytorium_sezonow: Callable[[], SezonReadRepository] | None = None,
        fabryka_repozytorium_rozgrywek: Callable[[], RozgrywkiReadRepository] | None = None,
        fabryka_repozytorium_hal: Callable[[], HalaReadRepository] | None = None,
        fabryka_repozytorium_etapow: Callable[[], EtapMeczowReadRepository] | None = None,
    ) -> None:
        self._fabryka_repozytorium_meczow = fabryka_repozytorium_meczow or (
            lambda: MeczSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_sezonow = fabryka_repozytorium_sezonow or (
            lambda: SezonSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_rozgrywek = fabryka_repozytorium_rozgrywek or (
            lambda: RozgrywkiSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_hal = fabryka_repozytorium_hal or (
            lambda: HalaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )

        self._fabryka_repozytorium_etapow = fabryka_repozytorium_etapow or (
            lambda: EtapMeczowSQLAlchemyRepository(cast(Session, baza_danych.session))
        )

    def utworz_serwis_meczow(self) -> MeczService:
        return MeczService(self._fabryka_repozytorium_meczow())

    def utworz_serwis_slownikow(self) -> SlownikiMeczowService:
        return SlownikiMeczowService(
            self._fabryka_repozytorium_sezonow(),
            self._fabryka_repozytorium_rozgrywek(),
            self._fabryka_repozytorium_hal(),
            self._fabryka_repozytorium_etapow(),
        )
