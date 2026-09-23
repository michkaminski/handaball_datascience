from typing import Protocol

from handball.domain.opponent_defense import MeczLigowy, WystapienieZDanymiLigowymi


class DefensywaRywalaReadRepository(Protocol):
    def pobierz_wystapienia(self, id_zawodnik: int) -> tuple[WystapienieZDanymiLigowymi, ...]: ...

    def pobierz_mecze_ligowe(
        self, identyfikatory_rozgrywek: frozenset[int]
    ) -> tuple[MeczLigowy, ...]: ...

    def pobierz_poprzednie_rozgrywki(
        self, rozgrywki_do_sprawdzenia: frozenset[tuple[int, str, int]]
    ) -> dict[int, int]: ...

    def pobierz_zespoly_o_nazwie(self, fraza: str) -> frozenset[int]: ...
