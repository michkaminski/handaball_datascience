from __future__ import annotations

from handball.contracts.match_repository import MeczReadRepository
from handball.contracts.match_statistics_repository import FormaMeczuReadRepository
from handball.domain.match_rules import MeczPolicy
from handball.domain.match_statistics import (
    FormaDruzyny,
    StatystykiMeczu,
    StatystykiMeczuCalculator,
)


class StatystykiMeczuService:
    def __init__(
        self,
        mecze: MeczReadRepository,
        forma: FormaMeczuReadRepository,
        kalkulator: StatystykiMeczuCalculator,
        reguly: MeczPolicy,
    ) -> None:
        self._mecze = mecze
        self._forma = forma
        self._kalkulator = kalkulator
        self._reguly = reguly

    def pobierz(self, id_mecz: int) -> StatystykiMeczu:
        szczegoly = self._mecze.pobierz_szczegoly(id_mecz)
        mecz = szczegoly.mecz
        id_gospodarza, id_goscia = self._reguly.para(mecz, mecz.id_zespol_gosp, mecz.id_zespol_gosc)
        return self._kalkulator.oblicz(
            szczegoly,
            self._forma_druzyny(id_mecz, id_gospodarza),
            self._forma_druzyny(id_mecz, id_goscia),
        )

    def _forma_druzyny(self, id_mecz: int, id_zespol: int | None) -> FormaDruzyny | None:
        if id_zespol is None:
            return None
        mecze = tuple(self._forma.pobierz_forme(id_mecz, id_zespol))
        return FormaDruzyny(id_zespol, mecze, id_mecz)
