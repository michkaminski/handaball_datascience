from typing import Protocol

from handball.domain.catalogs import (
    FiltryKatalogu,
    PozycjaDruzyny,
    PozycjaHali,
    PozycjaRozgrywek,
    PozycjaSedziego,
    PozycjaSezonu,
    StronaKatalogu,
)
from handball.domain.options import OpcjaWyboru


class KatalogReadRepository(Protocol):
    def pobierz_sezony(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSezonu]: ...
    def pobierz_rozgrywki(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaRozgrywek]: ...
    def pobierz_druzyny(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaDruzyny]: ...
    def pobierz_sedziow(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSedziego]: ...
    def pobierz_hale(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaHali]: ...
    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]: ...
