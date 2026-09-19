from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from handball.domain.matches import FiltryMeczow
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository


@pytest.mark.parametrize("zamiana", [True, False, None])
@pytest.mark.parametrize("wynik", [(46, 19), (0, 0), (None, 19)])
@pytest.mark.parametrize("etapy", [("Runda zasadnicza", "Kolejka 1"), (None, None)])
def test_lista_zamienia_druzyny_wraz_z_wynikiem(
    zamiana: bool | None,
    wynik: tuple[int | None, int | None],
    etapy: tuple[str | None, str | None],
) -> None:
    mecz = Mecz(id=1, zamiana=zamiana, wynik_gosp_full=wynik[0], wynik_gosc_full=wynik[1])
    wiersz = Mock()
    wiersz.Mecz = mecz
    dane = [
        mecz,
        "2026/2027",
        "Superliga",
        "Wisła Płock",
        "MMTS Kwidzyn",
        "Hala",
        etapy[0],
        etapy[1],
    ]
    wiersz.__getitem__ = Mock(side_effect=dane.__getitem__)
    sesja = Mock(spec=Session)
    sesja.scalar.return_value = 1
    sesja.execute.return_value.all.return_value = [wiersz]
    pozycja = MeczSQLAlchemyRepository(sesja).pobierz_liste(FiltryMeczow()).pozycje[0]
    assert pozycja.runda == etapy[0]
    assert pozycja.kolejka == etapy[1]
    assert pozycja.gospodarz == ("MMTS Kwidzyn" if zamiana else "Wisła Płock")
    assert pozycja.gosc == ("Wisła Płock" if zamiana else "MMTS Kwidzyn")
    if None in wynik:
        assert pozycja.wynik == "- : -"
    elif zamiana:
        assert pozycja.wynik == f"{wynik[1]} : {wynik[0]}"
    else:
        assert pozycja.wynik == f"{wynik[0]} : {wynik[1]}"


def test_zapytanie_filtruje_etapy_bez_zwielokrotniania_meczow() -> None:
    sesja = Mock(spec=Session)
    sesja.scalar.return_value = 0
    sesja.execute.return_value.all.return_value = []
    repo = MeczSQLAlchemyRepository(sesja)
    repo.pobierz_liste(FiltryMeczow(runda="Play-off", kolejka="Kolejka 2"))
    zapytanie = sesja.execute.call_args.args[0]
    sql = str(zapytanie)
    parametry = zapytanie.compile().params
    assert "LEFT OUTER JOIN public.kolejki ON public.kolejki.id = public.mecze.id_kolejka" in sql
    assert "LEFT OUTER JOIN public.rundy ON public.rundy.id = public.kolejki.id_runda" in sql
    assert "public.rundy.nazwa =" in sql and "public.kolejki.nazwa =" in sql
    assert "Play-off" in parametry.values() and "Kolejka 2" in parametry.values()
    licznik = str(sesja.scalar.call_args.args[0])
    assert "public.rundy.nazwa =" in licznik and "public.kolejki.nazwa =" in licznik
