from handball.contracts.core_catalog_repository import KatalogPodstawowyReadRepository
from handball.domain.catalogs import (
    FiltryKatalogu,
    PozycjaDruzyny,
    PozycjaRozgrywek,
    PozycjaSezonu,
    StronaKatalogu,
)
from handball.domain.options import OpcjaWyboru


class KatalogService:
    def __init__(self, repozytorium: KatalogPodstawowyReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_sezony(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSezonu]:
        return self._repozytorium.pobierz_sezony(filtry)

    def pobierz_rozgrywki(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaRozgrywek]:
        return self._repozytorium.pobierz_rozgrywki(filtry)

    def pobierz_druzyny(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaDruzyny]:
        return self._repozytorium.pobierz_druzyny(filtry)

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        return self._repozytorium.pobierz_opcje_sezonow()
