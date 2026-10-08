from typing import Protocol

from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    LiniaWyniku,
    MeczRozkladu,
    OpcjeFiltrowRozkladu,
    RodzajSerii,
)


class RozkladBramekReadRepository(Protocol):
    def pobierz_opcje(self) -> OpcjeFiltrowRozkladu: ...

    def pobierz_wyniki(self, filtry: FiltryRozkladuBramek) -> tuple[LiniaWyniku, ...]: ...

    def pobierz_mecze(
        self, filtry: FiltryRozkladuBramek, rodzaj: RodzajSerii, bramki: int
    ) -> tuple[MeczRozkladu, ...]: ...
