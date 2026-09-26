from __future__ import annotations

from typing import Protocol

from handball.domain.options import OpcjaWyboru
from handball.domain.schedule import FiltryTerminarza, PozycjaTerminarza


class TerminarzReadRepository(Protocol):
    def pobierz_rozgrywki(self, id_sezon: int) -> list[OpcjaWyboru]: ...

    def pobierz_rundy(self, id_rozgrywki: int) -> list[OpcjaWyboru]: ...

    def pobierz_kolejki(self, id_rozgrywki: int, id_runda: int | None) -> list[OpcjaWyboru]: ...

    def pobierz_mecze(self, filtry: FiltryTerminarza) -> list[PozycjaTerminarza]: ...
