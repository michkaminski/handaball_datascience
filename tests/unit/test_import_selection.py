from unittest.mock import Mock

import pytest
from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from handball.domain.imports import BladImportu, PrzebiegImportu, RekordImportu
from handball.infrastructure.repositories.import_repository import ImportSQLAlchemyRepository


def test_wybor_kandydatow_odczytuje_baze_i_przygotowuje_zadania() -> None:
    silnik = Mock(spec=Engine)
    polaczenie = silnik.connect.return_value.execution_options.return_value
    polaczenie.__enter__ = Mock(return_value=polaczenie)
    polaczenie.__exit__ = Mock(return_value=False)
    polaczenie.execute.return_value.mappings.return_value.all.return_value = [
        {"id": 206511, "id_rozgrywki": 12007, "id_kolejka": 66727}
    ]
    repo = ImportSQLAlchemyRepository(silnik, Mock())
    zadania = repo.pobierz_brakujace([12007])
    silnik.connect.return_value.execution_options.assert_called_once_with(
        postgresql_readonly=True, isolation_level="REPEATABLE READ"
    )
    polaczenie.rollback.assert_called_once()
    assert len(zadania) == 1
    assert zadania[0].parametry == {"Zawody": 206511}
    assert zadania[0].kontekst == {"mid": 206511, "cid": 12007, "did": 66727}
    assert polaczenie.execute.call_args.args[1] == {"sezon": 195, "ligi": [12007]}


def test_blad_odczytu_kandydatow_konczy_transakcje() -> None:
    silnik = Mock(spec=Engine)
    polaczenie = silnik.connect.return_value.execution_options.return_value
    polaczenie.__enter__ = Mock(return_value=polaczenie)
    polaczenie.__exit__ = Mock(return_value=False)
    polaczenie.execute.side_effect = SQLAlchemyError("awaria")
    with pytest.raises(BladImportu, match="odczytać"):
        ImportSQLAlchemyRepository(silnik, Mock()).pobierz_brakujace([12007])
    polaczenie.rollback.assert_called_once()


def test_uzupelnienie_zachowuje_wynik_i_uzupelnia_tylko_null() -> None:
    silnik = Mock(spec=Engine)
    polaczenie = silnik.connect.return_value.execution_options.return_value
    polaczenie.__enter__ = Mock(return_value=polaczenie)
    polaczenie.__exit__ = Mock(return_value=False)
    repo = ImportSQLAlchemyRepository(silnik, Mock())
    tabela = Table("mecze", MetaData(), Column("id", Integer))
    repo._tabele = Mock(return_value={"mecze": tabela})
    repo._wiersz = Mock(return_value={"id": 1, "wynik_gosp_full": 0, "wynik_gosc_full": None})
    przebieg = PrzebiegImportu("test", [12007], "2026-09-19", tryb="uzupelniajacy")
    rekord = RekordImportu(
        "mecze",
        {"id": 1},
        {"id": 1, "wynik_gosp_full": 46, "wynik_gosc_full": 19},
        "zrodlo",
        uzupelnij=True,
    )
    przebieg.rekordy = [rekord]
    repo.porownaj(przebieg)
    assert rekord.zmiany == {"wynik_gosc_full": 19}
