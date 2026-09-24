from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoZawodnika
from handball.domain.player_details import FiltryMeczowZawodnika
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.rosters import SkladSezonowy
from handball.infrastructure.repositories.player_detail_repository import (
    SzczegolyZawodnikaSQLAlchemyRepository,
)


def test_historia_zachowuje_sezony_liczby_i_braki() -> None:
    sesja = Mock(spec=Session)
    sesja.get.return_value = Zawodnik(
        id=7, imie="Jan", nazwisko="Test", data_urodzenia=date(1998, 1, 2), foto_url=None
    )
    nowszy = SkladSezonowy(
        id_zespol_sezon=1,
        id_zawodnik=7,
        wzrost=Decimal("192.0"),
        waga=Decimal("94.5"),
        nr_koszulki=9,
        pozycja_nazwa="RO",
    )
    starszy = SkladSezonowy(
        id_zespol_sezon=2,
        id_zawodnik=7,
        wzrost=Decimal("190.0"),
        waga=None,
        nr_koszulki=5,
        pozycja_nazwa=None,
    )
    historia = Mock()
    historia.all.return_value = [
        (nowszy, "2026/2027", "A", "Rozgrywający", 195, 10),
        (starszy, "2025/2026", "B", "BR", 194, 11),
    ]
    statystyki = Mock()
    statystyki.all.return_value = [
        (195, 10, "Liga", 120, 20, 30, 10, 2, 1),
        (195, 10, "Puchar", 15, 1, 2, 2, 0, 0),
    ]
    sesja.execute.side_effect = [historia, statystyki]
    wynik = SzczegolyZawodnikaSQLAlchemyRepository(sesja).pobierz_szczegoly(7)
    assert [s.rozgrywki for s in wynik.sezony] == ["Liga", "Puchar", None]
    assert [s.wzrost for s in wynik.sezony] == [
        Decimal("192.0"),
        Decimal("192.0"),
        Decimal("190.0"),
    ]
    assert wynik.sezony[2].waga is None
    assert wynik.sezony[2].pozycja == "BR"
    assert wynik.sezony[0].bramki == 120
    assert wynik.sezony[0].karne_bramki == 20
    assert wynik.sezony[0].karne_liczba == 30
    assert wynik.sezony[0].dwie_minuty == 10
    assert wynik.sezony[0].upomnienia == 2
    assert wynik.sezony[0].dyskwalifikacje == 1
    nowszy.waga = Decimal("99.0")
    assert wynik.sezony[0].waga == Decimal("94.5")
    statystyki_sql = str(
        sesja.execute.call_args_list[1].args[0].compile(dialect=postgresql.dialect())
    )
    assert "GROUP BY" in statystyki_sql
    assert "mecze.id_sezon" in statystyki_sql
    assert "rozgrywki.nazwa" in statystyki_sql
    sesja.commit.assert_not_called()


def test_brak_zawodnika_i_awaria_nie_sa_pusta_karta() -> None:
    sesja = Mock(spec=Session)
    repo = SzczegolyZawodnikaSQLAlchemyRepository(sesja)
    sesja.get.return_value = None
    with pytest.raises(NieZnalezionoZawodnika):
        repo.pobierz_szczegoly(99)
    sesja.get.side_effect = SQLAlchemyError()
    with pytest.raises(BladOdczytuDanych):
        repo.pobierz_szczegoly(7)


def test_mecze_sa_paginowane_przed_pobraniem_wpisow() -> None:
    sesja = Mock(spec=Session)
    sesja.scalar.return_value = 21
    mecz = Mecz(id=101, data_faktyczna=datetime(2026, 9, 20), zamiana=True)
    sesja.execute.return_value.all.return_value = [(mecz, "2026/2027", "Liga", "A", "B")]
    sesja.scalars.return_value = [
        MeczZawodnik(id_mecz=101, id_zawodnik=7, strona="gosp", bramki=0),
        MeczZawodnik(id_mecz=101, id_zawodnik=7, strona="gosc", bramki=5),
    ]
    wynik = SzczegolyZawodnikaSQLAlchemyRepository(sesja).pobierz_mecze(
        7, FiltryMeczowZawodnika(strona=999)
    )
    assert wynik.strona == 2 and wynik.liczba_wszystkich == 21
    assert len(wynik.pozycje) == 1 and len(wynik.pozycje[0].wpisy) == 2
    assert [w.statystyki.bramki for w in wynik.pozycje[0].wpisy] == [0, 5]
    sql = str(sesja.execute.call_args.args[0].compile(dialect=postgresql.dialect()))
    assert "EXISTS (SELECT" in sql and "LIMIT" in sql and "OFFSET" in sql
    assert "JOIN public.mecze_zawodnicy" not in sql
    assert "DESC NULLS LAST, public.mecze.id" in sql
    sesja.commit.assert_not_called()
    sesja.flush.assert_not_called()


def test_przeciwnik_uwzglednia_strone_zawodnika_i_parametry() -> None:
    repo = SzczegolyZawodnikaSQLAlchemyRepository(Mock(spec=Session))
    wynik = repo._zapytanie_meczow(
        7, FiltryMeczowZawodnika(id_sezon=195, rozgrywki="Liga", przeciwnik="Test%_")
    ).compile(dialect=postgresql.dialect())
    assert {"gosp", "gosc", "Test/%/_", 195, "Liga", 7}.issubset(set(wynik.params.values()))
    sql = str(wynik)
    assert "public.mecze.zamiana IS true" in sql and "public.mecze.zamiana IS NOT true" in sql
    assert "THEN public.mecze.id_zespol_gosc WHEN" in sql and "END IN (" in sql
    assert "Test%_" not in sql


def test_pusta_strona_nie_pobiera_wpisow() -> None:
    sesja = Mock(spec=Session)
    sesja.scalar.return_value = 0
    sesja.execute.return_value.all.return_value = []
    wynik = SzczegolyZawodnikaSQLAlchemyRepository(sesja).pobierz_mecze(
        7, FiltryMeczowZawodnika(strona=20)
    )
    assert wynik.pozycje == [] and wynik.strona == 1
    sesja.scalars.assert_not_called()


def test_analityka_agreguje_do_jednego_wiersza_na_mecz() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [
        (101, datetime(2026, 9, 20), "2026/2027", "Liga", 7, 2, 3, 1, 0, 0, "dom", 1)
    ]
    wynik = SzczegolyZawodnikaSQLAlchemyRepository(sesja).pobierz_analityke(
        7, FiltryMeczowZawodnika(id_sezon=195, rozgrywki="Liga", przeciwnik="Rywal")
    )
    assert len(wynik) == 1
    assert wynik[0].id_mecz == 101 and wynik[0].bramki == 7
    assert wynik[0].miejsce == "dom"
    zapytanie = sesja.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    sql = str(zapytanie)
    assert "GROUP BY public.mecze.id" in sql
    assert "sum(public.mecze_zawodnicy.bramki)" in sql
    assert "public.mecze.id_sezon" in sql and "public.rozgrywki.nazwa" in sql
    assert "public.mecze.zamiana IS true" in sql and "END IN (" in sql
    sesja.commit.assert_not_called()
    sesja.flush.assert_not_called()


def test_analityka_miejsce_jest_none_dla_niejednoznacznych_stron() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value = [
        (101, datetime(2026, 9, 20), "2026/2027", "Liga", 7, 2, 3, 1, 0, 0, "wyjazd", 2),
        (102, datetime(2026, 9, 21), "2026/2027", "Liga", 3, None, None, 0, 0, 0, "wyjazd", 1),
    ]
    wynik = SzczegolyZawodnikaSQLAlchemyRepository(sesja).pobierz_analityke(
        7, FiltryMeczowZawodnika()
    )
    assert wynik[0].miejsce is None
    assert wynik[1].miejsce == "wyjazd"
