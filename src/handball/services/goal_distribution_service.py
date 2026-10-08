from handball.contracts.goal_distribution_repository import RozkladBramekReadRepository
from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    MeczRozkladu,
    OpcjeFiltrowRozkladu,
    RaportRozkladuBramek,
    RodzajSerii,
    serie_z_wynikow,
    sprawdz_liczbe_bramek,
)


class RozkladBramekService:
    def __init__(self, repozytorium: RozkladBramekReadRepository) -> None:
        self._repozytorium = repozytorium

    def pobierz_opcje(self) -> OpcjeFiltrowRozkladu:
        return self._repozytorium.pobierz_opcje()

    def pobierz_raport(self, filtry: FiltryRozkladuBramek) -> RaportRozkladuBramek:
        suma, gospodarze, goscie = serie_z_wynikow(self._repozytorium.pobierz_wyniki(filtry))
        return RaportRozkladuBramek(filtry, suma, gospodarze, goscie)

    def pobierz_mecze(
        self, filtry: FiltryRozkladuBramek, rodzaj: RodzajSerii, bramki: int
    ) -> tuple[MeczRozkladu, ...]:
        return self._repozytorium.pobierz_mecze(filtry, rodzaj, sprawdz_liczbe_bramek(bramki))
