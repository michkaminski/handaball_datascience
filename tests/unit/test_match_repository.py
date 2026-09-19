from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.domain.matches import DaneMeczu
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository
from handball.request_dependencies import ZaleznosciZadaniaFactory


def test_repozytorium_zachowuje_typy_braki_i_zrodlowe_strony() -> None:
    termin = datetime(2026, 9, 12, 18, 0)
    mecz = Mecz(id=1, zamiana=True, wynik_gosp_full=32, wynik_gosc_full=28, data_faktyczna=termin)
    gospodarz = MeczZawodnik(
        strona="gosp",
        nr_koszulki=10,
        bramki=7,
        pozycja="RO",
        imie="Jan",
        nazwisko="Kowalski",
        upomnienie=False,
    )
    gosc = MeczZawodnik(strona="gosc", nr_koszulki=None, bramki=None, imie="Adam")
    sesja = Mock(spec=Session)
    sesja.execute.return_value.first.return_value = (
        mecz,
        "2026/2027",
        "Liga",
        "A",
        "B",
        None,
        None,
        None,
        None,
        3,
        None,
        None,
    )
    sesja.execute.return_value.scalars.return_value.all.return_value = [gospodarz, gosc]
    dane = MeczSQLAlchemyRepository(sesja).pobierz_szczegoly(1)
    assert isinstance(dane.mecz, DaneMeczu)
    assert dane.mecz.data_faktyczna == termin
    assert dane.mecz.wynik_gosp_full == 32
    assert dane.nazwa_gospodarz == "A"
    assert dane.nazwa_hala is None
    assert dane.sklad_gospodarz[0].nr_koszulki == 10
    assert dane.sklad_gospodarz[0].bramki == 7
    assert dane.sklad_gospodarz[0].upomnienie is False
    assert dane.sklad_gosc[0].bramki is None
    assert not hasattr(dane.sklad_gospodarz[0], "kolor_pozycji")
    mecz.wynik_gosp_full = 99
    gospodarz.bramki = 99
    assert dane.mecz.wynik_gosp_full == 32
    assert dane.sklad_gospodarz[0].bramki == 7
    widok = ZaleznosciZadaniaFactory().utworz_presenter_meczow().przygotuj_szczegoly(dane)
    assert widok.gospodarz == "B"
    assert widok.wynik_naglowek == "28 : 32"
    assert widok.termin == "12.09.2026 18:00"
    assert widok.kolejka == "Kolejka 3"
    assert widok.hala == "—"
    assert widok.sklad_gospodarz[0].bramki == "—"
    assert widok.sklad_gosc[0].bramki == "7"
    assert widok.sklad_gosc[0].upomnienie == "Nie"


def test_szczegoly_brak_rekordu() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value.first.return_value = None
    with pytest.raises(NieZnalezionoMeczu):
        MeczSQLAlchemyRepository(sesja).pobierz_szczegoly(1)


def test_szczegoly_blad_odczytu() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.side_effect = SQLAlchemyError()
    with pytest.raises(BladOdczytuDanych):
        MeczSQLAlchemyRepository(sesja).pobierz_szczegoly(1)
