from __future__ import annotations

from datetime import date
from typing import Protocol

from handball.domain.match_predictions import WzorceNazwLig
from handball.domain.match_tips import PozycjaTypowania


class TypowaniaReadRepository(Protocol):
    def pobierz_rozgrywki(
        self, data_od: date, data_do: date, wzorce: WzorceNazwLig
    ) -> list[str]: ...

    def pobierz_mecze(
        self,
        data_od: date,
        data_do: date,
        rozgrywki: frozenset[str],
        wzorce: WzorceNazwLig,
    ) -> list[PozycjaTypowania]: ...
