from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Ustawienia:
    tryb_debugowania: bool
    tajny_klucz: str

    @classmethod
    def z_srodowiska(cls) -> Ustawienia:
        return cls(
            tryb_debugowania=os.environ.get("FLASK_DEBUG", "0") == "1",
            tajny_klucz=os.environ.get("SECRET_KEY", "dev"),
        )

    def waliduj(self) -> None:
        if not self.tajny_klucz:
            raise ValueError("SECRET_KEY nie moze byc puste")
