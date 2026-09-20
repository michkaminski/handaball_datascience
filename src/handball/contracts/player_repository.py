from typing import Protocol

from handball.domain.players import FiltryZawodnikow, StronaZawodnikow


class ZawodnikReadRepository(Protocol):
    def pobierz_liste(self, filtry: FiltryZawodnikow) -> StronaZawodnikow: ...

    def pobierz_pozycje(self) -> list[str]: ...
