from typing import Any, cast

import pytest
from sqlalchemy import Table, create_engine, event, insert, select
from sqlalchemy.engine import Engine

from handball.infrastructure.database.match_sides import StronyMeczuSql
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik


@pytest.fixture
def silnik() -> Engine:
    silnik = create_engine("sqlite://")

    @event.listens_for(silnik, "connect")
    def dolacz_schemat(polaczenie: Any, _: object) -> None:
        polaczenie.execute("ATTACH DATABASE ':memory:' AS public")

    with silnik.begin() as polaczenie:
        cast(Table, Mecz.__table__).create(polaczenie)
        cast(Table, MeczZawodnik.__table__).create(polaczenie)
        polaczenie.execute(
            insert(Mecz),
            [
                {
                    "id": 1,
                    "id_sezon": 1,
                    "id_rozgrywki": 1,
                    "id_kolejka": 1,
                    "id_zespol_gosp": 10,
                    "id_zespol_gosc": 20,
                    "zamiana": False,
                },
                {
                    "id": 2,
                    "id_sezon": 1,
                    "id_rozgrywki": 1,
                    "id_kolejka": 1,
                    "id_zespol_gosp": 10,
                    "id_zespol_gosc": 20,
                    "zamiana": True,
                },
                {
                    "id": 3,
                    "id_sezon": 1,
                    "id_rozgrywki": 1,
                    "id_kolejka": 1,
                    "id_zespol_gosp": 10,
                    "id_zespol_gosc": 20,
                    "zamiana": None,
                },
            ],
        )
        polaczenie.execute(
            insert(MeczZawodnik),
            [
                {"id_mecz": mecz, "strona": strona, "id_zawodnik": numer}
                for numer, (mecz, strona) in enumerate(
                    [(1, "gosp"), (1, "gosc"), (2, "gosp"), (2, "gosc"), (3, "gosp"), (3, "inne")]
                )
            ],
        )
    return silnik


def test_strona_wpisu_wskazuje_druzyne_po_zamianie(silnik: Engine) -> None:
    zapytanie = (
        select(
            MeczZawodnik.id_mecz,
            MeczZawodnik.strona,
            StronyMeczuSql.zespol(MeczZawodnik.strona),
            StronyMeczuSql.rywal(MeczZawodnik.strona),
        )
        .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
        .order_by(MeczZawodnik.id_mecz, MeczZawodnik.strona)
    )
    with silnik.connect() as polaczenie:
        wynik = [tuple(wiersz) for wiersz in polaczenie.execute(zapytanie)]
    assert wynik == [
        (1, "gosc", 20, 10),
        (1, "gosp", 10, 20),
        (2, "gosc", 10, 20),
        (2, "gosp", 20, 10),
        (3, "gosp", 10, 20),
        (3, "inne", None, None),
    ]
