from __future__ import annotations

from handball.domain.match_statistics import MeczFormy


class FormaMeczuInMemoryRepository:
    def __init__(self, mecze: dict[int, list[MeczFormy]] | None = None) -> None:
        self._mecze = mecze or {}
        self.zapytania: list[tuple[int, int]] = []

    def pobierz_forme(self, id_mecz: int, id_zespol: int) -> list[MeczFormy]:
        self.zapytania.append((id_mecz, id_zespol))
        return list(self._mecze.get(id_zespol, []))
