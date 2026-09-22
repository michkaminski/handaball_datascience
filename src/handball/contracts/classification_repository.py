from typing import Protocol

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


class KlasyfikacjaReadRepository(Protocol):
    def pobierz_sklady(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Sklad]: ...
    def pobierz_szczegoly_skladu(self, id_zespol_sezon: int) -> SzczegolySkladu | None: ...
    def pobierz_strzelcow(
        self, filtry: FiltryKlasyfikacji
    ) -> StronaKlasyfikacji[PozycjaStrzelca]: ...
    def pobierz_tabele(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Klasyfikacja]: ...
    def pobierz_szczegoly_tabeli(self, id_tabela_grupa: int) -> SzczegolyTabeli | None: ...
    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]: ...
    def pobierz_opcje_rozgrywek(self, id_sezon: int | None) -> list[OpcjaWyboru]: ...
