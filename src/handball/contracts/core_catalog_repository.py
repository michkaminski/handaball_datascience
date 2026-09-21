from typing import Protocol

from handball.domain.catalogs import (
    FiltryKatalogu,
    PozycjaDruzyny,
    PozycjaRozgrywek,
    PozycjaSezonu,
    StronaKatalogu,
)
from handball.domain.options import OpcjaWyboru


class KatalogPodstawowyReadRepository(Protocol):
    def pobierz_sezony(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSezonu]: ...

    def pobierz_rozgrywki(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaRozgrywek]: ...

    def pobierz_druzyny(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaDruzyny]: ...

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]: ...
