from typing import Protocol

from handball.domain.player_details import (
    AnalitykaMeczuZawodnika,
    FiltryMeczowZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
)


class SzczegolyZawodnikaReadRepository(Protocol):
    def pobierz_szczegoly(self, id_zawodnik: int) -> SzczegolyZawodnika: ...

    def pobierz_mecze(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> StronaMeczowZawodnika: ...

    def pobierz_analityke(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> tuple[AnalitykaMeczuZawodnika, ...]: ...
