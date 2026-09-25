from typing import Protocol

from handball.domain.match_predictions import MeczLigowy, WzorceNazwLig


class MeczeLigoweReadRepository(Protocol):
    def pobierz_mecze(self, wzorce: WzorceNazwLig) -> list[MeczLigowy]: ...
