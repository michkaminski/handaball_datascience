from __future__ import annotations

from handball.domain.errors import NieZnalezionoMeczu
from handball.domain.matches import FiltryMeczow, PozycjaListyMeczow, StronaMeczow, SzczegolyMeczu


class MeczInMemoryRepository:
    def __init__(
        self,
        pozycje: list[PozycjaListyMeczow] | None = None,
        szczegoly: dict[int, SzczegolyMeczu] | None = None,
    ) -> None:
        self._pozycje = pozycje or []
        self._szczegoly = szczegoly or {}

    def pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow:
        self.ostatnie_filtry = filtry
        poczatek = (filtry.strona - 1) * filtry.rozmiar_strony
        koniec = poczatek + filtry.rozmiar_strony
        pasujace = [
            pozycja
            for pozycja in self._pozycje
            if (not filtry.runda or pozycja.runda == filtry.runda)
            and (not filtry.kolejka or pozycja.kolejka == filtry.kolejka)
        ]
        wybrane = pasujace[poczatek:koniec]
        return StronaMeczow(
            pozycje=wybrane,
            liczba_wszystkich=len(pasujace),
            strona=filtry.strona,
            rozmiar_strony=filtry.rozmiar_strony,
        )

    def pobierz_szczegoly(self, id_mecz: int) -> SzczegolyMeczu:
        try:
            return self._szczegoly[id_mecz]
        except KeyError as wyjatek:
            raise NieZnalezionoMeczu(f"Nie znaleziono meczu o id {id_mecz}") from wyjatek
