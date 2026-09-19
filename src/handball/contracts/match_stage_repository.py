from typing import Protocol


class EtapMeczowReadRepository(Protocol):
    def pobierz_rundy(self) -> list[str]: ...

    def pobierz_kolejki(self) -> list[str]: ...
