from typing import Protocol

from handball.domain.team_details import (
    DaneZestawieniaDruzyny,
    FiltryDruzyny,
    FiltryZawodnikowDruzyny,
    FiltryZestawieniaDruzyny,
    MeczDruzyny,
    OpcjeFiltrowDruzyny,
    StronaMeczowDruzyny,
    StronaZawodnikowDruzyny,
    SzczegolyDruzyny,
)


class SzczegolyDruzynyReadRepository(Protocol):
    def pobierz_szczegoly(self, id_zespol: int) -> SzczegolyDruzyny: ...

    def pobierz_opcje_filtrow(self, id_zespol: int) -> OpcjeFiltrowDruzyny: ...

    def pobierz_mecze(self, id_zespol: int, filtry: FiltryDruzyny) -> StronaMeczowDruzyny: ...

    def pobierz_wszystkie_mecze(
        self, id_zespol: int, filtry: FiltryDruzyny
    ) -> tuple[MeczDruzyny, ...]: ...

    def pobierz_zestawienie(
        self, id_zespol: int, filtry: FiltryZestawieniaDruzyny
    ) -> DaneZestawieniaDruzyny: ...

    def pobierz_zawodnikow(
        self, id_zespol: int, filtry: FiltryZawodnikowDruzyny
    ) -> StronaZawodnikowDruzyny: ...
