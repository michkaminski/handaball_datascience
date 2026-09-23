from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.infrastructure.repositories.news_repository import AktualnosciSQLAlchemyRepository


def _sesja(wiersze: list[tuple[object, ...]]) -> Mock:
    sesja = Mock(spec=Session)
    sesja.execute.return_value.all.return_value = wiersze
    sesja.execute.return_value.first.return_value = wiersze[0] if wiersze else None
    return sesja


def test_rozegrane_mecze_zachowuja_surowe_strony_i_flage_zamiany() -> None:
    sesja = _sesja([(5, datetime(2026, 9, 20, 18), 12007, "Płock", "Kielce", 30, 28, True)])
    wynik = AktualnosciSQLAlchemyRepository(sesja).pobierz_rozegrane_mecze(195)
    assert len(wynik) == 1
    mecz = wynik[0]
    assert (mecz.gospodarz, mecz.gosc) == ("Płock", "Kielce")
    assert (mecz.mecz.wynik_gosp_full, mecz.mecz.wynik_gosc_full, mecz.mecz.zamiana) == (
        30,
        28,
        True,
    )
    assert mecz.suma_bramek == 58 and mecz.roznica_bramek == 2


def test_strzelcy_i_wystepy_zamieniaja_agregaty_na_liczby_calkowite() -> None:
    repozytorium = AktualnosciSQLAlchemyRepository(_sesja([(12007, 7, "Jan Nowak", "KS", 3, 27)]))
    strzelec = repozytorium.pobierz_strzelcow(195, 5)[0]
    assert (strzelec.mecze, strzelec.bramki, strzelec.druzyna) == (3, 27, "KS")
    wystep_repo = AktualnosciSQLAlchemyRepository(
        _sesja([(12007, 5, datetime(2026, 9, 20), 7, "Jan Nowak", None, 15)])
    )
    wystep = wystep_repo.pobierz_najlepsze_wystepy(195, 3)[0]
    assert (wystep.id_mecz, wystep.bramki, wystep.druzyna) == (5, 15, None)


def test_brak_rozegranego_sezonu_daje_none() -> None:
    assert AktualnosciSQLAlchemyRepository(_sesja([])).pobierz_biezacy_sezon() is None


def test_blad_bazy_zamienia_sie_na_blad_odczytu() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.side_effect = SQLAlchemyError("awaria")
    with pytest.raises(BladOdczytuDanych):
        AktualnosciSQLAlchemyRepository(sesja).pobierz_rozgrywki(195)
