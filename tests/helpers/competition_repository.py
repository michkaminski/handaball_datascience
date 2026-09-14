from __future__ import annotations


class RozgrywkiInMemoryRepository:
    def __init__(self, nazwy: list[str] | None = None) -> None:
        self._nazwy = nazwy or []

    def pobierz_nazwy(self, id_sezon: int | None) -> list[str]:
        return self._nazwy
