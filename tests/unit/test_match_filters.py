from __future__ import annotations

from datetime import datetime

import pytest

from handball.domain.matches import FiltryMeczow, zakres_z_czesciowej_daty


def test_filtry_domyslne_sa_poprawne() -> None:
    filtry = FiltryMeczow(id_sezon=195)

    assert filtry.strona == 1
    assert filtry.rozmiar_strony == 20
    assert filtry.sortowanie == "data"


def test_filtry_bez_sezonu_oznaczaja_wszystkie_sezony() -> None:
    filtry = FiltryMeczow()

    assert filtry.id_sezon is None


def test_zakres_z_czesciowej_daty_sam_rok() -> None:
    start, koniec = zakres_z_czesciowej_daty("2026")

    assert (start, koniec) == (datetime(2026, 1, 1), datetime(2027, 1, 1))


def test_zakres_z_czesciowej_daty_rok_i_miesiac() -> None:
    start, koniec = zakres_z_czesciowej_daty("2026-01")

    assert (start, koniec) == (datetime(2026, 1, 1), datetime(2026, 2, 1))


def test_zakres_z_czesciowej_daty_grudzien_przechodzi_do_kolejnego_roku() -> None:
    start, koniec = zakres_z_czesciowej_daty("2026-12")

    assert (start, koniec) == (datetime(2026, 12, 1), datetime(2027, 1, 1))


def test_zakres_z_czesciowej_daty_pelna_data() -> None:
    start, koniec = zakres_z_czesciowej_daty("2026-01-15")

    assert (start, koniec) == (datetime(2026, 1, 15), datetime(2026, 1, 16))


@pytest.mark.parametrize("tekst", ["", "abc", "2026-13", "2026-01-32", "26-01-01", "2026/01/01"])
def test_zakres_z_czesciowej_daty_odrzuca_niepoprawny_format(tekst: str) -> None:
    with pytest.raises(ValueError):
        zakres_z_czesciowej_daty(tekst)


@pytest.mark.parametrize("strona", [0, -1])
def test_filtry_odrzucaja_niepoprawna_strone(strona: int) -> None:
    with pytest.raises(ValueError):
        FiltryMeczow(id_sezon=195, strona=strona)


@pytest.mark.parametrize("rozmiar_strony", [0, 101, -5])
def test_filtry_odrzucaja_niepoprawny_rozmiar_strony(rozmiar_strony: int) -> None:
    with pytest.raises(ValueError):
        FiltryMeczow(id_sezon=195, rozmiar_strony=rozmiar_strony)


def test_filtry_odrzucaja_niedozwolone_sortowanie() -> None:
    with pytest.raises(ValueError):
        FiltryMeczow(id_sezon=195, sortowanie="losowe")
