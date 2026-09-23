from datetime import datetime

from handball.domain.opponent_defense import MeczLigowy, WystapienieZDanymiLigowymi


class DefensywaRywalaPustyRepozytorium:
    def pobierz_wystapienia(self, id_zawodnik: int) -> tuple[WystapienieZDanymiLigowymi, ...]:
        return ()

    def pobierz_mecze_ligowe(
        self, identyfikatory_rozgrywek: frozenset[int]
    ) -> tuple[MeczLigowy, ...]:
        return ()

    def pobierz_poprzednie_rozgrywki(
        self, rozgrywki_do_sprawdzenia: frozenset[tuple[int, str, int]]
    ) -> dict[int, int]:
        return {}

    def pobierz_zespoly_o_nazwie(self, fraza: str) -> frozenset[int]:
        return frozenset()


def _wystapienie(
    id_mecz: int, dzien: int, bramki: int, przeciwnik: int
) -> WystapienieZDanymiLigowymi:
    return WystapienieZDanymiLigowymi(
        id_mecz=id_mecz,
        termin=datetime(2026, 9, dzien),
        id_sezon=195,
        sezon="2026/2027",
        rok_rozpoczecia_sezonu=2026,
        id_rozgrywki=1,
        rozgrywki="Liga",
        id_zespol_zawodnika=1,
        druzyna_zawodnika="Nasza Drużyna",
        id_zespol_przeciwnika=przeciwnik,
        przeciwnik=f"Rywal {przeciwnik}",
        miejsce="dom",
        bramki_zawodnika=bramki,
        wynik_druzyny_zawodnika=25,
        wynik_przeciwnika=24,
        dane_pelne=True,
    )


class DefensywaRywalaTestoweRepozytorium:
    def __init__(self) -> None:
        self.wystapienia = tuple(
            _wystapienie(1000 + i, 10 + i, bramki, 500 + (i % 3))
            for i, bramki in enumerate((2, 4, 6, 8, 5, 3))
        )
        self.mecze_ligowe = tuple(
            MeczLigowy(1, 500 + rywal, datetime(2026, 9, dzien), 28 + rywal)
            for rywal in range(3)
            for dzien in range(1, 5)
        )

    def pobierz_wystapienia(self, id_zawodnik: int) -> tuple[WystapienieZDanymiLigowymi, ...]:
        return self.wystapienia

    def pobierz_mecze_ligowe(
        self, identyfikatory_rozgrywek: frozenset[int]
    ) -> tuple[MeczLigowy, ...]:
        return tuple(m for m in self.mecze_ligowe if m.id_rozgrywki in identyfikatory_rozgrywek)

    def pobierz_poprzednie_rozgrywki(
        self, rozgrywki_do_sprawdzenia: frozenset[tuple[int, str, int]]
    ) -> dict[int, int]:
        return {}

    def pobierz_zespoly_o_nazwie(self, fraza: str) -> frozenset[int]:
        return frozenset()
