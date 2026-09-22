from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from handball.domain.classifications import FiltryKlasyfikacji
from handball.infrastructure.repositories.classification_repository import (
    KlasyfikacjaSQLAlchemyRepository,
)

wymaga_bazy = pytest.mark.skipif(
    not os.environ.get("BAZA_HASLO"),
    reason="Wymaga zmiennej BAZA_HASLO (polaczenie tylko do odczytu z realna baza zprp)",
)


@pytest.fixture()
def sesja() -> Session:
    adres = (
        f"postgresql+psycopg://{os.environ.get('BAZA_UZYTKOWNIK', 'postgres')}"
        f":{os.environ.get('BAZA_HASLO', '')}"
        f"@{os.environ.get('BAZA_HOST', 'localhost')}:{os.environ.get('BAZA_PORT', '5432')}"
        f"/{os.environ.get('BAZA_NAZWA', 'zprp')}"
    )
    silnik = create_engine(adres, execution_options={"postgresql_readonly": True})
    with Session(silnik) as otwarta_sesja:
        yield otwarta_sesja
        otwarta_sesja.rollback()
    silnik.dispose()


@wymaga_bazy
def test_pobierz_sklady_zwraca_grupowana_strone(sesja: Session) -> None:
    repozytorium = KlasyfikacjaSQLAlchemyRepository(sesja)

    strona = repozytorium.pobierz_sklady(FiltryKlasyfikacji(rozmiar_strony=5))

    assert strona.liczba_wszystkich > 0
    assert len(strona.pozycje) == 5
    assert all(pozycja.id_zespol_sezon > 0 for pozycja in strona.pozycje)
    assert any(pozycja.rozgrywki for pozycja in strona.pozycje)
