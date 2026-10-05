from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from handball.domain.match_preview import SezonKadry, WystepSezonuZawodnika, ZawodnikKadry


class KadraRaportuReadRepository(Protocol):
    def pobierz_kadre(
        self, id_zespol: int, id_sezon: int, przed: datetime
    ) -> list[ZawodnikKadry]: ...

    def pobierz_sklad_sezonu(self, id_zespol: int, id_sezon: int) -> list[ZawodnikKadry]: ...

    def pobierz_poprzedni_sezon(self, id_sezon: int) -> SezonKadry | None: ...

    def pobierz_wystepy_zawodnikow(
        self, id_zawodnikow: Sequence[int], id_sezon: int, przed: datetime
    ) -> list[WystepSezonuZawodnika]: ...
