import re

import pytest

from handball.infrastructure.repositories.attendance_cities_queries import (
    ZESTAWY_MIAST,
    ZestawZapytanMiast,
)
from handball.infrastructure.repositories.attendance_city_rows import (
    hala_z_wiersza,
    miasto_z_wiersza,
    rozgrywki_z_wiersza,
    sezon_z_wiersza,
    wklad_z_wiersza,
)

ZAPYTANIA = ("miasta", "wklady", "sezony", "rozgrywki", "hale", "bez_miasta")
ZAPYTANIA_Z_MIASTEM = ("miasta", "wklady", "sezony", "rozgrywki", "hale")
ZAPISY = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE)\b", re.IGNORECASE)


def _tekst(zestaw: ZestawZapytanMiast, nazwa: str) -> str:
    return " ".join(str(getattr(zestaw, nazwa)).split())


@pytest.mark.parametrize("bez_zer", [False, True])
@pytest.mark.parametrize("nazwa", ZAPYTANIA)
def test_zapytania_miast_sa_tylko_do_odczytu(bez_zer: bool, nazwa: str) -> None:
    tresc = _tekst(ZESTAWY_MIAST[bez_zer], nazwa)

    assert tresc.startswith("SELECT")
    assert ZAPISY.search(tresc) is None


@pytest.mark.parametrize("nazwa", ZAPYTANIA_Z_MIASTEM)
def test_zapytania_miast_grupuja_po_znormalizowanym_kluczu(nazwa: str) -> None:
    tresc = _tekst(ZESTAWY_MIAST[False], nazwa)

    assert "lower(NULLIF(btrim(regexp_replace(zg.miasto, '\\s+', ' ', 'g')), ''))" in tresc
    assert "GROUP BY 1" in tresc


def test_ranking_miast_wybiera_najczestsza_pisownie_i_miary_rozkladu() -> None:
    tresc = _tekst(ZESTAWY_MIAST[False], "miasta")

    assert "mode() WITHIN GROUP (ORDER BY NULLIF(btrim(regexp_replace(zg.miasto" in tresc
    assert "AS miasto" in tresc
    assert "percentile_cont(0.5) WITHIN GROUP (ORDER BY m.widzowie)" in tresc
    assert "mode() WITHIN GROUP (ORDER BY m.widzowie)" in tresc
    for alias in ("AS mediana", "AS dominanta", "AS minimum", "AS liczba_klubow"):
        assert alias in tresc


def test_miary_rozkladu_licza_tylko_mecze_ze_znana_frekwencja() -> None:
    zwykle = _tekst(ZESTAWY_MIAST[False], "miasta")
    bez_zer = _tekst(ZESTAWY_MIAST[True], "miasta")

    assert "FILTER (WHERE m.widzowie >= 0)" in zwykle
    assert "FILTER (WHERE m.widzowie > 0)" in bez_zer
    assert "FILTER (WHERE m.widzowie >= 0)" not in bez_zer


@pytest.mark.parametrize("nazwa", ["sezony", "rozgrywki", "hale"])
def test_rozbicia_licza_mediane_i_dominante(nazwa: str) -> None:
    tresc = _tekst(ZESTAWY_MIAST[False], nazwa)

    assert "AS mediana" in tresc
    assert "AS dominanta" in tresc
    assert "AS klucz" in tresc


def test_zapytanie_hal_laczy_hale_i_pomija_mecze_bez_hali() -> None:
    tresc = _tekst(ZESTAWY_MIAST[False], "hale")

    assert "LEFT JOIN public.hale h ON h.id = m.id_hala" in tresc
    assert "h.id IS NOT NULL" in tresc
    assert "AS miasto_hali" in tresc
    assert "AS hala" in tresc


def test_zapytanie_sezonow_grupuje_po_sezonie() -> None:
    tresc = _tekst(ZESTAWY_MIAST[False], "sezony")

    assert "AS sezon" in tresc
    assert "AS rok_poczatku" in tresc
    assert "GROUP BY 1, 2, 3, 4" in tresc


def test_mecze_bez_miasta_uzywaja_tego_samego_klucza() -> None:
    tresc = _tekst(ZESTAWY_MIAST[False], "bez_miasta")

    assert "lower(NULLIF(btrim(regexp_replace(zg.miasto" in tresc
    assert ") IS NULL" in tresc


def _wiersz_miary(**dodatkowe: object) -> dict[str, object]:
    return {
        "rozegrane": 5,
        "znane": 4,
        "suma": 12000,
        "maksimum": 4000,
        "mediana": 3000.0,
        "dominanta": 2500,
        "minimum": 2000,
        **dodatkowe,
    }


def test_wiersz_miasta_mapuje_mediane_dominante_i_minimum() -> None:
    miasto = miasto_z_wiersza(
        _wiersz_miary(klucz="gdańsk", miasto="Gdańsk", liczba_klubow=2, liczba_rozgrywek=3)
    )

    assert miasto.miasto == "Gdańsk"
    assert miasto.klucz == "gdańsk"
    assert miasto.suma == 12000
    assert miasto.rozklad.mediana == 3000.0
    assert miasto.rozklad.dominanta == 2500
    assert miasto.rozklad.minimum == 2000
    assert miasto.liczba_klubow == 2


def test_wiersz_miasta_bez_znanych_meczow_ma_puste_miary() -> None:
    miasto = miasto_z_wiersza(
        _wiersz_miary(
            klucz="x",
            miasto="X",
            liczba_klubow=0,
            liczba_rozgrywek=0,
            znane=0,
            mediana=None,
            dominanta=None,
            minimum=None,
            maksimum=None,
        )
    )

    assert miasto.rozklad.mediana is None
    assert miasto.rozklad.dominanta_etykieta == "—"


def test_wiersz_wkladu_mapuje_klub_i_agregat() -> None:
    wklad = wklad_z_wiersza(
        {
            "miasto": "Kielce",
            "id_zespol": 11,
            "klub": "Industria",
            "rozgrywki": "Superliga",
            "rozegrane": 3,
            "znane": 2,
            "suma": 8000,
            "maksimum": 4000,
        }
    )

    assert (wklad.miasto, wklad.id_zespol, wklad.klub, wklad.rozgrywki) == (
        "Kielce",
        11,
        "Industria",
        "Superliga",
    )
    assert wklad.agregat.suma == 8000


def test_wiersz_sezonu_mapuje_rok_i_rozklad() -> None:
    sezon = sezon_z_wiersza(
        _wiersz_miary(klucz="kielce", id_sezon=195, sezon="2025/2026", rok_poczatku=2025)
    )
    bez_roku = sezon_z_wiersza(
        _wiersz_miary(klucz="kielce", id_sezon=1, sezon="stary", rok_poczatku=None)
    )

    assert (sezon.klucz, sezon.sezon, sezon.rok_poczatku) == ("kielce", "2025/2026", 2025)
    assert sezon.agregat.srednia == 3000
    assert sezon.rozklad.mediana == 3000.0
    assert bez_roku.rok_poczatku is None


def test_wiersz_rozgrywek_mapuje_liczbe_klubow() -> None:
    pozycja = rozgrywki_z_wiersza(
        _wiersz_miary(klucz="kielce", rozgrywki="Superliga", liczba_klubow=2)
    )

    assert pozycja.rozgrywki == "Superliga"
    assert pozycja.liczba_klubow == 2
    assert pozycja.rozklad.dominanta == 2500


def test_wiersz_hali_mapuje_nazwe_miasto_hali_i_rozklad() -> None:
    hala = hala_z_wiersza(
        _wiersz_miary(klucz="kielce", id_hala=7, hala="Hala Legionów", miasto_hali="Chęciny")
    )

    assert (hala.id_hala, hala.hala, hala.miasto_hali) == (7, "Hala Legionów", "Chęciny")
    assert hala.miasto_hali_inne is True
    assert hala.rozklad.minimum == 2000
