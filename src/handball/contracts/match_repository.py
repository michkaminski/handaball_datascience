from __future__ import annotations

from typing import Protocol

from handball.domain.matches import FiltryMeczow, StronaMeczow


class MeczReadRepository(Protocol):
    def pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow: ...
