from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from handball.domain.match_preview import (
    MeczZapowiedzi,
    SezonKadry,
    WystepSezonuZawodnika,
    WystepZapowiedzi,
    ZawodnikKadry,
)


class ZapowiedzMeczuReadRepository(Protocol):
    def pobierz_mecz(self, id_mecz: int) -> MeczZapowiedzi: ...

    def pobierz_wystepy(self, id_zespol: int, przed: datetime) -> list[WystepZapowiedzi]: ...

    def pobierz_kadre(
        self, id_zespol: int, id_sezon: int, przed: datetime
    ) -> list[ZawodnikKadry]: ...

    def pobierz_poprzedni_sezon(self, id_sezon: int) -> SezonKadry | None: ...

    def pobierz_wystepy_zawodnikow(
        self, id_zawodnikow: Sequence[int], id_sezon: int, przed: datetime
    ) -> list[WystepSezonuZawodnika]: ...
