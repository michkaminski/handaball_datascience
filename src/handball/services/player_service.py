from handball.contracts.player_repository import ZawodnikReadRepository
from handball.domain.players import FiltryZawodnikow, StronaZawodnikow


class ZawodnikService:
    def __init__(self, repozytorium: ZawodnikReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_liste(self, filtry: FiltryZawodnikow) -> StronaZawodnikow:
        return self._repozytorium.pobierz_liste(filtry)

    def pobierz_pozycje(self) -> list[str]:
        return self._repozytorium.pobierz_pozycje()
