from handball.contracts.catalog_repository import KatalogReadRepository
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


class KatalogService:
    def __init__(self, repozytorium: KatalogReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_sezony(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSezonu]:
        return self._repozytorium.pobierz_sezony(filtry)

    def pobierz_rozgrywki(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaRozgrywek]:
        return self._repozytorium.pobierz_rozgrywki(filtry)

    def pobierz_druzyny(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaDruzyny]:
        return self._repozytorium.pobierz_druzyny(filtry)

    def pobierz_sedziow(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSedziego]:
        return self._repozytorium.pobierz_sedziow(filtry)

    def pobierz_hale(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaHali]:
        return self._repozytorium.pobierz_hale(filtry)

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        return self._repozytorium.pobierz_opcje_sezonow()
