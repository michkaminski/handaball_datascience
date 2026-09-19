from __future__ import annotations

import pytest

from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository


@pytest.mark.parametrize(
    (
        "zamiana",
        "dogrywka_karne_gosp",
        "dogrywka_karne_gosc",
        "dogrywka_1_full_gosp",
        "dogrywka_1_full_gosc",
        "oczekiwany",
    ),
    [
        (False, None, None, None, None, None),
        (False, 6, 7, 35, 33, "k 6-7"),
        (True, 6, 7, 35, 33, "k 7-6"),
        (False, None, None, 35, 33, "dogrywka"),
        (True, None, None, 35, 33, "dogrywka"),
        (False, 0, 0, None, None, "k 0-0"),
    ],
)
def test_dopisek_wyniku(
    zamiana: bool,
    dogrywka_karne_gosp: int | None,
    dogrywka_karne_gosc: int | None,
    dogrywka_1_full_gosp: int | None,
    dogrywka_1_full_gosc: int | None,
    oczekiwany: str | None,
) -> None:
    mecz = Mecz(
        zamiana=zamiana,
        dogrywka_karne_gosp=dogrywka_karne_gosp,
        dogrywka_karne_gosc=dogrywka_karne_gosc,
        dogrywka_1_full_gosp=dogrywka_1_full_gosp,
        dogrywka_1_full_gosc=dogrywka_1_full_gosc,
    )

    assert MeczSQLAlchemyRepository._dopisek_wyniku(mecz) == oczekiwany
