from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpcjaWyboru:
    wartosc: int
    etykieta: str
