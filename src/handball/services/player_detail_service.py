from handball.contracts.player_detail_repository import SzczegolyZawodnikaReadRepository
from handball.domain.player_details import (
    FiltryMeczowZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
)


class SzczegolyZawodnikaService:
    def __init__(self, repozytorium: SzczegolyZawodnikaReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_szczegoly(self, id_zawodnik: int) -> SzczegolyZawodnika:
        return self._repozytorium.pobierz_szczegoly(id_zawodnik)

    def pobierz_mecze(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> StronaMeczowZawodnika:
        return self._repozytorium.pobierz_mecze(id_zawodnik, filtry)
