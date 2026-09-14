from __future__ import annotations

from handball.domain.options import OpcjaWyboru


class HalaInMemoryRepository:
    def __init__(self, opcje: list[OpcjaWyboru] | None = None) -> None:
        self._opcje = opcje or []

    def pobierz_wszystkie(self) -> list[OpcjaWyboru]:
        return self._opcje
