from typing import Protocol

from handball.domain.catalogs import FiltryKatalogu, PozycjaHali, StronaKatalogu


class HalaKatalogReadRepository(Protocol):
    def pobierz_hale(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaHali]: ...
