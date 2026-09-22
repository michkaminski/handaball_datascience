from handball.contracts.classification_repository import KlasyfikacjaReadRepository
from handball.domain.classifications import (
    FiltryKlasyfikacji,
    Klasyfikacja,
    PozycjaStrzelca,
    Sklad,
    StronaKlasyfikacji,
    SzczegolySkladu,
    SzczegolyTabeli,
)
from handball.domain.options import OpcjaWyboru


class KlasyfikacjaService:
    def __init__(self, repozytorium: KlasyfikacjaReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_sklady(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Sklad]:
        return self._repozytorium.pobierz_sklady(filtry)

    def pobierz_szczegoly_skladu(self, id_zespol_sezon: int) -> SzczegolySkladu | None:
        return self._repozytorium.pobierz_szczegoly_skladu(id_zespol_sezon)

    def pobierz_strzelcow(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[PozycjaStrzelca]:
        return self._repozytorium.pobierz_strzelcow(filtry)

    def pobierz_tabele(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Klasyfikacja]:
        return self._repozytorium.pobierz_tabele(filtry)

    def pobierz_szczegoly_tabeli(self, id_tabela_grupa: int) -> SzczegolyTabeli | None:
        return self._repozytorium.pobierz_szczegoly_tabeli(id_tabela_grupa)

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        return self._repozytorium.pobierz_opcje_sezonow()

    def pobierz_opcje_rozgrywek(self, id_sezon: int | None) -> list[OpcjaWyboru]:
        return self._repozytorium.pobierz_opcje_rozgrywek(id_sezon)
