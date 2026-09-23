from __future__ import annotations

from html import unescape

import pytest
from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.news import (
    I_LIGA,
    LIGA_CENTRALNA_K,
    SUPERLIGA_K,
    SUPERLIGA_M,
    AktualnosciInMemoryRepository,
    mecz,
)

from handball.app_factory import AplikacjaFactory
from handball.domain.errors import BladOdczytuDanych
from handball.domain.news import SezonAktualnosci, StrzelecAktualnosci
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class AktualnosciBlednaBaza(AktualnosciInMemoryRepository):
    def pobierz_biezacy_sezon(self) -> SezonAktualnosci | None:
        raise BladOdczytuDanych("Brak połączenia.")


def _aplikacja(repozytorium: AktualnosciInMemoryRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(fabryka_aktualnosci=lambda: repozytorium)
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def _repozytorium() -> AktualnosciInMemoryRepository:
    return AktualnosciInMemoryRepository(
        mecze=(
            mecz(11, SUPERLIGA_M.id_rozgrywki, 20, (37, 24), ("ORLEN Wisła Płock", "Legionowo")),
            mecz(12, SUPERLIGA_K.id_rozgrywki, 16, (28, 29), ("Radom", "Energa Start Elbląg")),
            mecz(13, I_LIGA.id_rozgrywki, 19, (43, 34), ("SPR Grunwald", "MOS <Śląsk>")),
        ),
        strzelcy=(
            StrzelecAktualnosci(SUPERLIGA_M.id_rozgrywki, 7, "Mikołaj CZAPLIŃSKI", "PGE", 3, 27),
        ),
    )


def test_start_pokazuje_aktualnosci_z_ligami_priorytetowymi() -> None:
    odpowiedz = _aplikacja(_repozytorium()).test_client().get("/administracja/")
    tresc = unescape(odpowiedz.get_data(as_text=True))
    assert odpowiedz.status_code == 200
    assert "<h1>Aktualności</h1>" in tresc
    assert "Sezon <b>2026/2027</b>" in tresc
    for etykieta in ("Superliga mężczyzn", "Superliga kobiet", "Liga Centralna mężczyzn"):
        assert etykieta in tresc
    assert tresc.index("Superliga mężczyzn") < tresc.index("Superliga kobiet")
    assert 'href="/administracja/mecze/11"' in tresc and ">37:24<" in tresc
    assert "news-winner" in tresc
    assert "Pozostałe rozgrywki" in tresc and I_LIGA.nazwa in tresc
    assert "/administracja/mecze?id_sezon=195&rozgrywki=LOTTO+Superliga" in tresc
    assert "Ciekawostki sezonu" in tresc and "Najwięcej bramek w meczu" in tresc
    assert "Najlepsi strzelcy" in tresc and 'href="/administracja/zawodnicy/7"' in tresc
    assert "nie oficjalnej klasyfikacji strzelców" in tresc
    assert LIGA_CENTRALNA_K.nazwa in tresc


def test_start_escapuje_nazwy_z_bazy() -> None:
    tresc = _aplikacja(_repozytorium()).test_client().get("/administracja/").get_data(as_text=True)
    assert "MOS &lt;Śląsk&gt;" in tresc and "MOS <Śląsk>" not in tresc


def test_start_bez_rozegranych_meczow_pokazuje_komunikat() -> None:
    tresc = (
        _aplikacja(AktualnosciInMemoryRepository(sezon=None))
        .test_client()
        .get("/administracja/")
        .get_data(as_text=True)
    )
    assert "Brak rozegranych meczów w bazie." in tresc
    assert "news-layout" not in tresc


def test_start_przy_bledzie_odczytu_zwraca_503() -> None:
    odpowiedz = _aplikacja(AktualnosciBlednaBaza()).test_client().get("/administracja/")
    assert odpowiedz.status_code == 503


def test_start_renderuje_uklad_bazowy() -> None:
    tresc = _aplikacja(_repozytorium()).test_client().get("/administracja/").get_data(as_text=True)
    assert "Handball DataScience" in tresc
    assert 'class="nav"' in tresc


@pytest.mark.parametrize("plik", ["css/admin.css", "js/admin.js"])
def test_start_udostepnia_przeniesione_zasoby(plik: str) -> None:
    klient = _aplikacja(_repozytorium()).test_client()
    adres = f"/statyczne/{plik}"
    assert adres in klient.get("/administracja/").get_data(as_text=True)
    odpowiedz = klient.get(adres)
    assert odpowiedz.status_code == 200
    assert odpowiedz.data
