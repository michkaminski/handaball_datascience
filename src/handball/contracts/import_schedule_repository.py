from typing import Protocol

from handball.domain.schedule import FiltryPobierania, PozycjaTerminarza


class PobieranieMeczowReadRepository(Protocol):
    def pobierz(self, filtry: FiltryPobierania) -> list[tuple[PozycjaTerminarza, bool]]: ...
