from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


class GeneratorPdfNiedostepny(Exception):
    pass


class DokumentPdfRenderer(Protocol):
    def renderuj(self, html: str, arkusze: Sequence[Path]) -> bytes: ...
