from handball.contracts.database_stats_repository import StatystykiBazyReadRepository
from handball.domain.database_stats import (
    FiltryStatystykBazy,
    StronaStatystykBazy,
    przefiltruj_tabele,
)


class StatystykiBazyService:
    def __init__(self, repozytorium: StatystykiBazyReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_strone(self, filtry: FiltryStatystykBazy) -> StronaStatystykBazy:
        snapshot = self._repozytorium.pobierz_snapshot()
        pozycje = przefiltruj_tabele(snapshot.tabele, filtry)
        return StronaStatystykBazy(
            podsumowanie=snapshot.podsumowanie,
            pozycje=pozycje,
            schematy=snapshot.schematy,
            filtry=filtry,
            liczba_przefiltrowanych=len(pozycje),
        )
