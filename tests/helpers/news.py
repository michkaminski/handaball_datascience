from datetime import datetime

from handball.domain.matches import DaneMeczu
from handball.domain.news import (
    MeczAktualnosci,
    RozgrywkiAktualnosci,
    SezonAktualnosci,
    StrzelecAktualnosci,
    WystepAktualnosci,
)

SUPERLIGA_M = RozgrywkiAktualnosci(1, "LOTTO Superliga", "M")
SUPERLIGA_K = RozgrywkiAktualnosci(2, "LOTTO Superliga kobiet", "K")
LIGA_CENTRALNA_M = RozgrywkiAktualnosci(3, "Liga Centralna Mężczyzn", "M")
LIGA_CENTRALNA_K = RozgrywkiAktualnosci(4, "Liga Centralna Kobiet", "K")
SUPERPUCHAR_K = RozgrywkiAktualnosci(5, "Superpuchar Polski kobiet", "K")
I_LIGA = RozgrywkiAktualnosci(6, "I Liga Mężczyzn Grupa A", "M")
SEZON = SezonAktualnosci(195, "2026/2027")


def mecz(
    id_mecz: int,
    id_rozgrywki: int,
    dzien: int,
    wynik: tuple[int, int],
    druzyny: tuple[str, str] = ("Gospodarz", "Gość"),
    zamiana: bool = False,
) -> MeczAktualnosci:
    return MeczAktualnosci(
        id_mecz=id_mecz,
        termin=datetime(2026, 9, dzien, 18, 0),
        id_rozgrywki=id_rozgrywki,
        gospodarz=druzyny[0],
        gosc=druzyny[1],
        mecz=DaneMeczu(
            id=id_mecz, wynik_gosp_full=wynik[0], wynik_gosc_full=wynik[1], zamiana=zamiana
        ),
    )


class AktualnosciInMemoryRepository:
    def __init__(
        self,
        sezon: SezonAktualnosci | None = SEZON,
        rozgrywki: tuple[RozgrywkiAktualnosci, ...] = (
            SUPERLIGA_M,
            SUPERLIGA_K,
            LIGA_CENTRALNA_M,
            LIGA_CENTRALNA_K,
            SUPERPUCHAR_K,
            I_LIGA,
        ),
        mecze: tuple[MeczAktualnosci, ...] = (),
        strzelcy: tuple[StrzelecAktualnosci, ...] = (),
        wystepy: tuple[WystepAktualnosci, ...] = (),
    ) -> None:
        self.sezon = sezon
        self.rozgrywki = rozgrywki
        self.mecze = mecze
        self.strzelcy = strzelcy
        self.wystepy = wystepy

    def pobierz_biezacy_sezon(self) -> SezonAktualnosci | None:
        return self.sezon

    def pobierz_rozgrywki(self, id_sezon: int) -> tuple[RozgrywkiAktualnosci, ...]:
        return self.rozgrywki

    def pobierz_rozegrane_mecze(self, id_sezon: int) -> tuple[MeczAktualnosci, ...]:
        return tuple(sorted(self.mecze, key=lambda m: (m.termin, m.id_mecz), reverse=True))

    def pobierz_strzelcow(
        self, id_sezon: int, limit_na_rozgrywki: int
    ) -> tuple[StrzelecAktualnosci, ...]:
        return self.strzelcy

    def pobierz_najlepsze_wystepy(self, id_sezon: int, limit: int) -> tuple[WystepAktualnosci, ...]:
        return self.wystepy[:limit]
