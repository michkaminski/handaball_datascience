from typing import Protocol

from handball.domain.imports import PrzebiegImportu, ZadaniePobrania


class ImportRepository(Protocol):
    def pobierz_brakujace(self, ligi: list[int]) -> list[ZadaniePobrania]: ...

    def porownaj(self, przebieg: PrzebiegImportu) -> None: ...

    def zastosuj(self, przebieg: PrzebiegImportu) -> int: ...
