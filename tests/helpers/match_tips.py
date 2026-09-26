from datetime import date

from handball.domain.match_predictions import WzorceNazwLig
from handball.domain.match_tips import PozycjaTypowania
from tests.helpers.schedule import pozycje_terminarza


def pozycje_typowan() -> list[PozycjaTypowania]:
    return [
        PozycjaTypowania(501, "ORLEN Superliga", "2025/2026", pozycja)
        for pozycja in pozycje_terminarza()
    ]


class TypowaniaInMemoryRepository:
    def __init__(self, pozycje: list[PozycjaTypowania] | None = None) -> None:
        self._pozycje = pozycje if pozycje is not None else pozycje_typowan()
        self.zapytania: list[tuple[date, date, frozenset[str]]] = []

    def pobierz_rozgrywki(self, data_od: date, data_do: date, wzorce: WzorceNazwLig) -> list[str]:
        return sorted({p.rozgrywki for p in self._w_okresie(data_od, data_do)})

    def pobierz_mecze(
        self,
        data_od: date,
        data_do: date,
        rozgrywki: frozenset[str],
        wzorce: WzorceNazwLig,
    ) -> list[PozycjaTypowania]:
        self.zapytania.append((data_od, data_do, rozgrywki))
        return [
            p
            for p in self._w_okresie(data_od, data_do)
            if not rozgrywki or p.rozgrywki in rozgrywki
        ]

    def _w_okresie(self, data_od: date, data_do: date) -> list[PozycjaTypowania]:
        return [
            p
            for p in self._pozycje
            if p.pozycja.termin is not None and data_od <= p.pozycja.termin.date() <= data_do
        ]
