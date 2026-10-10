from __future__ import annotations

from collections.abc import Iterable


def uporzadkuj_pisownie(nazwa: str | None) -> str:
    if not nazwa:
        return ""
    return " ".join(nazwa.split())


def klucz_miasta(nazwa: str | None) -> str:
    return uporzadkuj_pisownie(nazwa).casefold()


def najczestsza_pisownia(pisownie: Iterable[tuple[str, int]]) -> str:
    wagi: dict[str, int] = {}
    for pisownia, waga in pisownie:
        uporzadkowana = uporzadkuj_pisownie(pisownia)
        if uporzadkowana:
            wagi[uporzadkowana] = wagi.get(uporzadkowana, 0) + waga
    if not wagi:
        return ""
    return min(wagi, key=lambda pisownia: (-wagi[pisownia], pisownia))
