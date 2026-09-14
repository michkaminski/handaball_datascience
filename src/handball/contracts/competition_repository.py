from __future__ import annotations

from typing import Protocol


class RozgrywkiReadRepository(Protocol):
    def pobierz_nazwy(self, id_sezon: int | None) -> list[str]: ...
