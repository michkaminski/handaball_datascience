from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.domain.players import FiltryZawodnikow
from handball.infrastructure.repositories.player_repository import ZawodnikSQLAlchemyRepository


def test_materializuje_dane_i_ogranicza_strone() -> None:
    sesja = Mock(spec=Session)
    sesja.scalar.return_value = 21
    wiersz = {
        "id": 1,
        "imie": None,
        "nazwisko": "Test",
        "rocznik": None,
        "pozycje": ["RO", None, "BR"],
        "druzyny": [None, "B", "A"],
        "wzrost": Decimal("192.0"),
        "waga": Decimal("94.5"),
    }
    sesja.execute.return_value.mappings.return_value = [wiersz]
    wynik = ZawodnikSQLAlchemyRepository(sesja).pobierz_liste(
        FiltryZawodnikow(strona=999, sortowanie="-waga")
    )
    assert wynik.strona == 2
    assert wynik.liczba_wszystkich == 21
    assert wynik.pozycje[0].pozycje == ("BR", "RO")
    assert wynik.pozycje[0].druzyny == ("A", "B")
    assert wynik.pozycje[0].wzrost == Decimal("192.0")
    assert wynik.pozycje[0].waga == Decimal("94.5")
    assert wynik.pozycje[0].rocznik is None
    wiersz["waga"] = Decimal("99.0")
    assert wynik.pozycje[0].waga == Decimal("94.5")
    zapytanie = sesja.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "DESC NULLS LAST, public.zawodnicy.id ASC" in str(zapytanie)
    assert 20 in zapytanie.params.values()
    sesja.commit.assert_not_called()
    sesja.flush.assert_not_called()


def test_pusty_wynik_ma_strone_pierwsza() -> None:
    sesja = Mock(spec=Session)
    sesja.scalar.return_value = 0
    sesja.execute.return_value.mappings.return_value = []
    wynik = ZawodnikSQLAlchemyRepository(sesja).pobierz_liste(FiltryZawodnikow(strona=999))
    assert wynik.strona == 1
    assert wynik.pozycje == []


def test_zapytanie_parametryzuje_filtry_i_wybiera_ostatnie_pomiary() -> None:
    repozytorium = ZawodnikSQLAlchemyRepository(Mock(spec=Session))
    zapytanie = repozytorium._zapytanie(
        FiltryZawodnikow(
            id_sezon=195,
            rozgrywki="Liga",
            druzyna="A%_",
            pozycja="BR",
            rocznik=1998,
            szukaj="Jan Test",
        )
    ).compile(dialect=postgresql.dialect())
    sql = str(zapytanie)
    assert "DISTINCT ON (public.sklady.id_zawodnik)" in sql
    assert "ostatni_wzrost" in sql and "ostatni_waga" in sql
    assert "public.sklady.wzrost IS NOT NULL" in sql
    assert "public.sklady.waga IS NOT NULL" in sql
    assert "sezony.rok_rozpoczecia DESC NULLS LAST" in sql
    assert "zespoly_sezony.id_sezon = wpisy_zawodnikow.id_sezon" in sql
    assert "statystyki_zawodnikow.id_zawodnik IS NOT NULL" in sql
    assert {"Liga", "A/%/_", "BR", 1998, "Jan", "Test"}.issubset(set(zapytanie.params.values()))
    assert "A%_" not in sql


def test_bez_filtrow_zachowuje_zawodnikow_bez_meczow() -> None:
    zapytanie = ZawodnikSQLAlchemyRepository(Mock(spec=Session))._zapytanie(FiltryZawodnikow())
    sql = str(zapytanie.compile(dialect=postgresql.dialect()))
    assert "LEFT OUTER JOIN statystyki_zawodnikow" in sql
    assert "statystyki_zawodnikow.id_zawodnik IS NOT NULL" not in sql


@pytest.mark.parametrize("operacja", ["lista", "pozycje"])
def test_blad_sql_jest_bledem_odczytu(operacja: str) -> None:
    sesja = Mock(spec=Session)
    sesja.scalar.side_effect = SQLAlchemyError("test")
    sesja.scalars.side_effect = SQLAlchemyError("test")
    repozytorium = ZawodnikSQLAlchemyRepository(sesja)
    with pytest.raises(BladOdczytuDanych):
        if operacja == "lista":
            repozytorium.pobierz_liste(FiltryZawodnikow())
        else:
            repozytorium.pobierz_pozycje()
