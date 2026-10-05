from datetime import datetime

import pytest

from handball.domain.match_preview import WystepSezonuZawodnika
from handball.domain.team_details import KolejnoscPozycjiPolicy
from handball.domain.team_report import (
    KolejnoscZawodnikowRaportuPolicy,
    MiejscaPolicy,
    PoprzedniSezonZawodnikaRaportu,
    ZawodnikRaportu,
)
from handball.interface.presenters.team_report_presenter import (
    UkladRaportuPolicy,
    UkladZestawieniaPolicy,
    procent,
    rocznik,
    skrot_pozycji,
)


def zawodnik(id_zawodnik: int, pozycja: str | None, numery: tuple[int, ...]) -> ZawodnikRaportu:
    return ZawodnikRaportu(
        id_zawodnik, "Jan", f"Nazwisko{id_zawodnik}", numery, pozycja, None, None
    )


def test_miejsca_dziela_ex_aequo() -> None:
    miejsca = MiejscaPolicy()
    assert miejsca.miejsca({1: 10, 2: 10, 3: 8, 4: 5}) == {1: 1, 2: 1, 3: 3, 4: 4}
    assert miejsca.najlepsi({1: 10, 2: 10, 3: 8, 4: 8}, 3) == frozenset({1, 2, 3, 4})


def test_kolejnosc_zawodnikow_od_bramkarzy_potem_numer() -> None:
    kolejnosc = KolejnoscZawodnikowRaportuPolicy(KolejnoscPozycjiPolicy())
    wynik = kolejnosc.uporzadkuj(
        [
            zawodnik(1, "Obrotowy", (5,)),
            zawodnik(2, "Rozgrywający", (11,)),
            zawodnik(3, "Bramkarz", (16,)),
            zawodnik(4, "Rozgrywający", (3,)),
            zawodnik(5, None, ()),
        ]
    )
    assert [z.id_zawodnik for z in wynik] == [3, 4, 2, 1, 5]


def test_uklad_raportu_miesci_kadre_w_granicach() -> None:
    uklad = UkladRaportuPolicy()
    assert uklad.uklad(10).wysokosc_wiersza_mm == UkladRaportuPolicy.NAJWYZSZY_WIERSZ_MM
    assert uklad.uklad(55).wysokosc_wiersza_mm == round(205 / 55 - 0.7, 2)
    assert uklad.uklad(200).wysokosc_wiersza_mm == UkladRaportuPolicy.NAJNIZSZY_WIERSZ_MM


def test_uklad_zestawienia_zweza_kolumny_przy_wielu_meczach() -> None:
    uklad = UkladZestawieniaPolicy()
    malo = uklad.uklad(15, 5)
    duzo = uklad.uklad(30, 36)
    assert malo.szerokosc_meczu_mm == UkladZestawieniaPolicy.NAJSZERSZY_MECZ_MM
    assert duzo.szerokosc_meczu_mm == round(178 / 36, 2)
    assert duzo.wysokosc_wiersza_mm < malo.wysokosc_wiersza_mm


@pytest.mark.parametrize(
    ("pozycja", "skrot"),
    [
        ("Bramkarz", "B"),
        ("rozgrywający lewy", "R"),
        ("Skrzydłowy", "S"),
        ("Obrotowy", "O"),
        (None, ""),
    ],
)
def test_skroty_pozycji(pozycja: str | None, skrot: str) -> None:
    assert skrot_pozycji(pozycja) == skrot


def test_format_procentu_i_rocznika() -> None:
    assert procent(4, 5) == "80%"
    assert procent(0, None) == ""
    assert rocznik(datetime(1999, 5, 1).date()) == "1999"
    assert rocznik(None) == ""


def test_poprzedni_sezon_sumuje_wystepy() -> None:
    poprzedni = PoprzedniSezonZawodnikaRaportu(
        (
            WystepSezonuZawodnika(7, 272, "A", "Liga", 10, 30),
            WystepSezonuZawodnika(7, 272, "A", "Puchar", 2, 4),
        )
    )
    assert poprzedni.zagral and poprzedni.mecze == 12 and poprzedni.bramki == 34
    assert not PoprzedniSezonZawodnikaRaportu().zagral
