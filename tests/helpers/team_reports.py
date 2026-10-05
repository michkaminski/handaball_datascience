from collections.abc import Sequence
from datetime import date, datetime

from handball.domain.match_preview import SezonKadry, WystepSezonuZawodnika, ZawodnikKadry

KADRY = {
    (272, 195): [
        ZawodnikKadry(7, "Jan", "Testowy", (9,), "Rozgrywający", 3, 9, 3, date(1999, 5, 1)),
        ZawodnikKadry(8, "Adam", "Bramkarz <b>", (1,), "Bramkarz", 2, 0, 2, date(1990, 1, 1)),
    ],
    (272, 194): [
        ZawodnikKadry(7, "Jan", "Testowy", (9,), "Rozgrywający", 1, 4, 1, date(1999, 5, 1)),
    ],
}

SKLADY = {
    (272, 193): [
        ZawodnikKadry(12, "Piotr", "Zgłoszony", (5,), "Skrzydłowy", 0, 0, 0, date(2004, 2, 2)),
    ],
}

POPRZEDNIE_SEZONY = {
    195: SezonKadry(194, "2025/2026"),
    194: SezonKadry(193, "2024/2025"),
    193: SezonKadry(150, "2010/2011"),
}

WYSTEPY_ZAWODNIKOW = {
    194: [
        WystepSezonuZawodnika(7, 272, "Wisła Test", "Liga", 10, 30),
        WystepSezonuZawodnika(7, 272, "Wisła Test", "Puchar", 2, 4),
        WystepSezonuZawodnika(8, 99, "Inny Klub", "I Liga", 12, 0),
    ],
}


class KadraRaportuInMemoryRepository:
    def __init__(self, kadry: dict[tuple[int, int], list[ZawodnikKadry]] | None = None) -> None:
        self._kadry = KADRY if kadry is None else kadry
        self.kadry: list[tuple[int, int, datetime]] = []
        self.wystepy: list[tuple[tuple[int, ...], int]] = []
        self.sklady: list[tuple[int, int]] = []

    def pobierz_kadre(self, id_zespol: int, id_sezon: int, przed: datetime) -> list[ZawodnikKadry]:
        self.kadry.append((id_zespol, id_sezon, przed))
        return list(self._kadry.get((id_zespol, id_sezon), []))

    def pobierz_sklad_sezonu(self, id_zespol: int, id_sezon: int) -> list[ZawodnikKadry]:
        self.sklady.append((id_zespol, id_sezon))
        return list(SKLADY.get((id_zespol, id_sezon), []))

    def pobierz_poprzedni_sezon(self, id_sezon: int) -> SezonKadry | None:
        return POPRZEDNIE_SEZONY.get(id_sezon)

    def pobierz_wystepy_zawodnikow(
        self, id_zawodnikow: Sequence[int], id_sezon: int, przed: datetime
    ) -> list[WystepSezonuZawodnika]:
        self.wystepy.append((tuple(id_zawodnikow), id_sezon))
        return [w for w in WYSTEPY_ZAWODNIKOW.get(id_sezon, []) if w.id_zawodnik in id_zawodnikow]
