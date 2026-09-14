from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, func, or_, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from handball.domain.matches import FiltryMeczow
from handball.infrastructure.database.models.competitions import Rozgrywki
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.teams import ZespolSezon
from handball.infrastructure.repositories.competition_repository import (
    RozgrywkiSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository

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
    silnik.dispose()


@wymaga_bazy
def test_pobierz_liste_zwraca_strone_dla_istniejacego_sezonu(sesja: Session) -> None:
    repozytorium = MeczSQLAlchemyRepository(sesja)

    strona = repozytorium.pobierz_liste(FiltryMeczow(id_sezon=195, rozmiar_strony=5))

    assert strona.liczba_wszystkich > 0
    assert len(strona.pozycje) <= 5
    assert strona.strona == 1
    assert strona.rozmiar_strony == 5
    sesja.rollback()


@wymaga_bazy
def test_pobierz_liste_dla_pustego_sezonu_zwraca_pusta_strone(sesja: Session) -> None:
    repozytorium = MeczSQLAlchemyRepository(sesja)

    strona = repozytorium.pobierz_liste(FiltryMeczow(id_sezon=-1))

    assert strona.liczba_wszystkich == 0
    assert strona.pozycje == []
    sesja.rollback()


@wymaga_bazy
def test_polaczenie_jest_tylko_do_odczytu(sesja: Session) -> None:
    with pytest.raises(DBAPIError):
        sesja.execute(text("CREATE TEMPORARY TABLE proba_zapisu_read_only (id integer)"))
    sesja.rollback()


@wymaga_bazy
def test_szukaj_druzyny_znajduje_zespol_we_wszystkich_sezonach(sesja: Session) -> None:
    kandydaci = sesja.execute(
        select(ZespolSezon.id_zespol, func.array_agg(func.distinct(ZespolSezon.nazwa)))
        .group_by(ZespolSezon.id_zespol)
        .having(func.count(func.distinct(ZespolSezon.nazwa)) >= 2)
        .order_by(ZespolSezon.id_zespol)
    ).all()

    # Krotkie/generyczne nazwy historyczne moga pasowac tez do innych, niepowiazanych
    # zespolow (np. rezerw czy drużyn mlodziezowych) - szukamy pierwszej nazwy, ktora
    # jednoznacznie wskazuje dokladnie jeden zespol, zeby test nie byl przypadkowo kruchy.
    wybrany_zespol: int | None = None
    wybrana_nazwa: str | None = None
    for id_zespol, nazwy in kandydaci:
        for nazwa in nazwy:
            dopasowane = (
                sesja.execute(
                    select(func.distinct(ZespolSezon.id_zespol)).where(
                        ZespolSezon.nazwa.ilike(f"%{nazwa}%")
                    )
                )
                .scalars()
                .all()
            )
            if dopasowane == [id_zespol]:
                wybrany_zespol, wybrana_nazwa = id_zespol, nazwa
                break
        if wybrany_zespol is not None:
            break

    if wybrany_zespol is None or wybrana_nazwa is None:
        pytest.skip("brak zespolu z jednoznaczna historyczna nazwa w danych")

    liczba_oczekiwana = sesja.scalar(
        select(func.count(func.distinct(Mecz.id))).where(
            or_(Mecz.id_zespol_gosp == wybrany_zespol, Mecz.id_zespol_gosc == wybrany_zespol)
        )
    )

    repozytorium = MeczSQLAlchemyRepository(sesja)
    strona = repozytorium.pobierz_liste(
        FiltryMeczow(szukaj_druzyny=wybrana_nazwa, rozmiar_strony=1)
    )
    sesja.rollback()

    assert liczba_oczekiwana is not None and liczba_oczekiwana > 0
    assert strona.liczba_wszystkich == liczba_oczekiwana


@wymaga_bazy
def test_pobierz_nazwy_rozgrywek_sa_unikalne(sesja: Session) -> None:
    repozytorium = RozgrywkiSQLAlchemyRepository(sesja)

    nazwy = repozytorium.pobierz_nazwy(id_sezon=None)
    sesja.rollback()

    assert len(nazwy) > 0
    assert len(nazwy) == len(set(nazwy))


@wymaga_bazy
def test_filtr_rozgrywki_po_nazwie_obejmuje_wiele_sezonow(sesja: Session) -> None:
    nazwa_w_wielu_sezonach = sesja.execute(
        select(Rozgrywki.nazwa)
        .group_by(Rozgrywki.nazwa)
        .having(func.count(func.distinct(Rozgrywki.id_sezon)) >= 2)
        .order_by(Rozgrywki.nazwa)
        .limit(1)
    ).scalar()
    if nazwa_w_wielu_sezonach is None:
        pytest.skip("brak nazwy rozgrywek powtarzajacej sie w kilku sezonach")

    liczba_sezonow_z_ta_nazwa = sesja.scalar(
        select(func.count(func.distinct(Rozgrywki.id_sezon))).where(
            Rozgrywki.nazwa == nazwa_w_wielu_sezonach
        )
    )

    repozytorium = MeczSQLAlchemyRepository(sesja)
    strona = repozytorium.pobierz_liste(
        FiltryMeczow(rozgrywki=nazwa_w_wielu_sezonach, rozmiar_strony=1)
    )
    sezony_w_wynikach = sesja.scalars(
        select(func.distinct(Mecz.id_sezon))
        .select_from(Mecz)
        .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
        .where(Rozgrywki.nazwa == nazwa_w_wielu_sezonach)
    ).all()
    sesja.rollback()

    assert strona.liczba_wszystkich > 0
    assert liczba_sezonow_z_ta_nazwa is not None and liczba_sezonow_z_ta_nazwa >= 2
    assert len(sezony_w_wynikach) == liczba_sezonow_z_ta_nazwa
