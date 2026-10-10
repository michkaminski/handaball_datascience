import pytest

from handball.domain.attendance_city_names import (
    klucz_miasta,
    najczestsza_pisownia,
    uporzadkuj_pisownie,
)


@pytest.mark.parametrize(
    "nazwa",
    ["Gdańsk", "GDAŃSK", "gdańsk", "  Gdańsk  ", "Gdańsk\t", "\nGDAŃSK "],
)
def test_klucz_miasta_ignoruje_wielkosc_liter_i_spacje_na_brzegach(nazwa: str) -> None:
    assert klucz_miasta(nazwa) == "gdańsk"


def test_klucz_miasta_zwija_wewnetrzne_biale_znaki() -> None:
    assert klucz_miasta("Nowy   Sącz") == klucz_miasta(" NOWY\tSĄCZ ") == "nowy sącz"


def test_klucz_miasta_zachowuje_polskie_znaki() -> None:
    assert klucz_miasta("Gdańsk") != klucz_miasta("Gdansk")
    assert klucz_miasta("Łódź") == klucz_miasta("ŁÓDŹ") == "łódź"


@pytest.mark.parametrize("nazwa", [None, "", "   ", "\t\n"])
def test_pusta_nazwa_ma_pusty_klucz(nazwa: str | None) -> None:
    assert klucz_miasta(nazwa) == ""
    assert uporzadkuj_pisownie(nazwa) == ""


def test_najczestsza_pisownia_wybiera_najwieksza_wage_z_zachowaniem_diakrytykow() -> None:
    assert najczestsza_pisownia([("GDAŃSK", 2), ("Gdańsk", 7), ("gdańsk", 1)]) == "Gdańsk"


def test_najczestsza_pisownia_sumuje_wagi_po_zwinieciu_spacji() -> None:
    assert najczestsza_pisownia([("Nowy  Sącz", 2), ("Nowy Sącz", 2), ("NOWY SĄCZ", 3)]) == (
        "Nowy Sącz"
    )


def test_najczestsza_pisownia_przy_remisie_jest_deterministyczna() -> None:
    assert najczestsza_pisownia([("GDAŃSK", 3), ("Gdańsk", 3)]) == najczestsza_pisownia(
        [("Gdańsk", 3), ("GDAŃSK", 3)]
    )


def test_najczestsza_pisownia_bez_danych_zwraca_pusty_tekst() -> None:
    assert najczestsza_pisownia([]) == ""
    assert najczestsza_pisownia([("  ", 5)]) == ""
