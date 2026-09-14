from __future__ import annotations

from handball.domain.matches import FiltryMeczow, PozycjaListyMeczow, StronaMeczow


class MeczInMemoryRepository:
    def __init__(self, pozycje: list[PozycjaListyMeczow] | None = None) -> None:
        self._pozycje = pozycje or []

    def pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow:
        poczatek = (filtry.strona - 1) * filtry.rozmiar_strony
        koniec = poczatek + filtry.rozmiar_strony
        wybrane = self._pozycje[poczatek:koniec]
        return StronaMeczow(
            pozycje=wybrane,
            liczba_wszystkich=len(self._pozycje),
            strona=filtry.strona,
            rozmiar_strony=filtry.rozmiar_strony,
        )
