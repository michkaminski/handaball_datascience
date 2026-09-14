from __future__ import annotations

from handball.contracts.match_repository import MeczReadRepository
from handball.domain.matches import FiltryMeczow, StronaMeczow


class MeczService:
    def __init__(self, repozytorium: MeczReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow:
        return self._repozytorium.pobierz_liste(filtry)
