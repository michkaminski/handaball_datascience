from typing import Protocol

from handball.domain.news import (
    MeczAktualnosci,
    RozgrywkiAktualnosci,
    SezonAktualnosci,
    StrzelecAktualnosci,
    WystepAktualnosci,
)


class AktualnosciReadRepository(Protocol):
    def pobierz_biezacy_sezon(self) -> SezonAktualnosci | None: ...

    def pobierz_rozgrywki(self, id_sezon: int) -> tuple[RozgrywkiAktualnosci, ...]: ...

    def pobierz_rozegrane_mecze(self, id_sezon: int) -> tuple[MeczAktualnosci, ...]: ...

    def pobierz_strzelcow(
        self, id_sezon: int, limit_na_rozgrywki: int
    ) -> tuple[StrzelecAktualnosci, ...]: ...

    def pobierz_najlepsze_wystepy(
        self, id_sezon: int, limit: int
    ) -> tuple[WystepAktualnosci, ...]: ...
