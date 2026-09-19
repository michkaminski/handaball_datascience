from __future__ import annotations

from typing import Protocol

from handball.domain.matches import FiltryMeczow, StronaMeczow, SzczegolyMeczu


class MeczReadRepository(Protocol):
    def pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow: ...

    def pobierz_szczegoly(self, id_mecz: int) -> SzczegolyMeczu: ...
