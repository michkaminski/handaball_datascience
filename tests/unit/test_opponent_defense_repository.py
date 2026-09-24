from datetime import datetime
from unittest.mock import Mock

from sqlalchemy.orm import Session

from handball.infrastructure.repositories.opponent_defense_repository import (
    DefensywaRywalaSQLAlchemyRepository,
)


def test_wystapienia_rozwiazuje_druzyne_i_przeciwnika_z_miejsca() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [
        (
            101,
            datetime(2026, 9, 20),
            195,
            "2026/2027",
            2026,
            1,
            "Liga",
            10,
            "Drużyna A",
            20,
            "Drużyna B",
            25,
            24,
            None,
            None,
            None,
            "dom",
            1,
            7,
        )
    ]
    wynik = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_wystapienia(7)
    assert len(wynik) == 1
    w = wynik[0]
    assert w.id_zespol_zawodnika == 10 and w.druzyna_zawodnika == "Drużyna A"
    assert w.id_zespol_przeciwnika == 20 and w.przeciwnik == "Drużyna B"
    assert w.miejsce == "dom"
    assert w.bramki_zawodnika == 7
    assert w.dane_pelne is True


def test_wystapienia_przy_zamianie_strona_wpisu_wskazuje_kolumne_goscia() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [
        (
            101,
            datetime(2026, 9, 20),
            195,
            "2026/2027",
            2026,
            1,
            "Liga",
            10,
            "Drużyna A",
            20,
            "Drużyna B",
            25,
            24,
            None,
            None,
            True,
            "dom",
            1,
            7,
        )
    ]
    w = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_wystapienia(7)[0]
    assert w.id_zespol_zawodnika == 20 and w.druzyna_zawodnika == "Drużyna B"
    assert w.id_zespol_przeciwnika == 10 and w.przeciwnik == "Drużyna A"
    assert (w.wynik_druzyny_zawodnika, w.wynik_przeciwnika) == (24, 25)
    assert w.miejsce == "dom"


def test_wystapienia_pomija_mecz_z_niejednoznaczna_strona() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [
        (
            101,
            datetime(2026, 9, 20),
            195,
            "2026/2027",
            2026,
            1,
            "Liga",
            10,
            "Drużyna A",
            20,
            "Drużyna B",
            25,
            24,
            None,
            None,
            None,
            "wyjazd",
            2,
            7,
        )
    ]
    wynik = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_wystapienia(7)
    assert wynik == ()


def test_wystapienia_dane_pelne_false_dla_walkowera() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [
        (
            101,
            datetime(2026, 9, 20),
            195,
            "2026/2027",
            2026,
            1,
            "Liga",
            10,
            "Drużyna A",
            20,
            "Drużyna B",
            None,
            None,
            None,
            30,
            None,
            "dom",
            1,
            None,
        )
    ]
    wynik = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_wystapienia(7)
    assert wynik[0].dane_pelne is False


def test_mecze_ligowe_unpivotuje_kazdy_mecz_na_dwa_wpisy() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [(1, 10, 20, 25, 24, datetime(2026, 9, 20))]
    wynik = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_mecze_ligowe(frozenset({1}))
    assert len(wynik) == 2
    assert {(m.id_zespol, m.bramki_stracone) for m in wynik} == {(10, 24), (20, 25)}


def test_mecze_ligowe_pusty_zbior_nie_wykonuje_zapytania() -> None:
    sesja = Mock(spec=Session)
    wynik = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_mecze_ligowe(frozenset())
    assert wynik == ()
    sesja.execute.assert_not_called()


def test_poprzednie_rozgrywki_tylko_dla_jednoznacznego_dopasowania() -> None:
    sesja = Mock(spec=Session)
    wynik_jednoznaczny = Mock()
    wynik_jednoznaczny.scalars.return_value.all.return_value = [5]
    wynik_wieloznaczny = Mock()
    wynik_wieloznaczny.scalars.return_value.all.return_value = [5, 6]
    sesja.execute.side_effect = [wynik_jednoznaczny, wynik_wieloznaczny]
    wynik = DefensywaRywalaSQLAlchemyRepository(sesja).pobierz_poprzednie_rozgrywki(
        frozenset({(1, "Liga", 2026), (2, "Puchar", 2026)})
    )
    assert wynik in ({1: 5}, {2: 5})
    assert len(wynik) == 1
