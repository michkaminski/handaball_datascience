from handball.contracts.venue_catalog_repository import HalaKatalogReadRepository
from handball.domain.catalogs import FiltryKatalogu, PozycjaHali, StronaKatalogu


class HalaService:
    def __init__(self, repozytorium: HalaKatalogReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_liste(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaHali]:
        return self._repozytorium.pobierz_hale(filtry)
