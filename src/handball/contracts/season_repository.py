from __future__ import annotations

from typing import Protocol

from handball.domain.options import OpcjaWyboru


class SezonReadRepository(Protocol):
    def pobierz_wszystkie(self) -> list[OpcjaWyboru]: ...
