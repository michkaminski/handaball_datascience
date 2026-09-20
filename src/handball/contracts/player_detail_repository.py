from typing import Protocol

from handball.domain.player_details import (
    FiltryMeczowZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
)


class SzczegolyZawodnikaReadRepository(Protocol):
    def pobierz_szczegoly(self, id_zawodnik: int) -> SzczegolyZawodnika: ...

    def pobierz_mecze(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> StronaMeczowZawodnika: ...
