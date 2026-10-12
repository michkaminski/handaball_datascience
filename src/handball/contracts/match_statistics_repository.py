from __future__ import annotations

from typing import Protocol

from handball.domain.match_statistics import MeczFormy


class FormaMeczuReadRepository(Protocol):
    def pobierz_forme(self, id_mecz: int, id_zespol: int) -> list[MeczFormy]: ...
