import pytest

from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    LiniaWyniku,
    rodzaj_serii,
    serie_z_wynikow,
    zbuduj_serie,
)


def test_seria_wypelnia_luki_i_liczy_udzial_oraz_dominante() -> None:
    seria = zbuduj_serie({10: 1, 12: 3})

    assert [pozycja.bramki for pozycja in seria.pozycje] == [10, 11, 12]
    assert [pozycja.mecze for pozycja in seria.pozycje] == [1, 0, 3]
    assert seria.liczba_meczow == 4
    assert seria.pozycje[2].udzial == 0.75
    assert seria.pozycje[2].narastajaco == 1
    assert seria.pozycje[1].szerokosc == 0
    assert seria.pozycje[2].szerokosc == 100
    assert seria.dominanty == (12,)
    assert seria.pozycje[2].czy_dominanta is True
    assert seria.srednia == 11.5
    assert seria.mediana == 12
    assert seria.minimum == 10
    assert seria.maksimum == 12


def test_mediana_parzystej_proby_jest_srednia_dwoch_srodkowych() -> None:
    seria = zbuduj_serie({1: 1, 3: 1})

    assert seria.mediana == 2
    assert seria.dominanty == ()


def test_pusta_seria_nie_ma_miar() -> None:
    seria = zbuduj_serie({})

    assert seria.liczba_meczow == 0
    assert seria.pozycje == ()
    assert seria.srednia is None
    assert seria.mediana is None
    assert seria.dominanty_etykieta == "—"
    assert seria.zakres_etykieta == "—"


def test_wyniki_rozkladaja_sie_na_sume_gospodarzy_i_gosci() -> None:
    suma, gospodarze, goscie = serie_z_wynikow(
        (LiniaWyniku(30, 28, 4), LiniaWyniku(25, 25, 2))
    )

    assert suma.liczba_meczow == 6
    assert {pozycja.bramki: pozycja.mecze for pozycja in suma.pozycje if pozycja.mecze} == {
        58: 4,
        50: 2,
    }
    assert {pozycja.bramki: pozycja.mecze for pozycja in gospodarze.pozycje if pozycja.mecze} == {
        30: 4,
        25: 2,
    }
    assert {pozycja.bramki: pozycja.mecze for pozycja in goscie.pozycje if pozycja.mecze} == {
        28: 4,
        25: 2,
    }
    assert suma.pozycje[-1].narastajaco == 1


def test_ujemne_bramki_i_pusta_linia_sa_odrzucone() -> None:
    with pytest.raises(ValueError):
        LiniaWyniku(-1, 20, 1)
    with pytest.raises(ValueError):
        LiniaWyniku(20, 20, 0)


def test_filtr_plci_przyjmuje_tylko_m_i_k() -> None:
    assert FiltryRozkladuBramek(plec="K").plec == "K"
    with pytest.raises(ValueError):
        FiltryRozkladuBramek(plec="X")
    with pytest.raises(ValueError):
        rodzaj_serii("dogrywka")
