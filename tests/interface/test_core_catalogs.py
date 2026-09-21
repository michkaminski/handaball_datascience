import pytest
from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.core_catalog_repository import KatalogPodstawowyInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.catalogs import FiltryKatalogu
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


def aplikacja_z_katalogiem(repo: KatalogPodstawowyInMemoryRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(fabryka_katalogu_podstawowego=lambda: repo)
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


@pytest.mark.parametrize(
    ("adres", "tekst", "sekcja"),
    [
        ("/administracja/sezony", "2025/2026", "Sezony"),
        ("/administracja/rozgrywki", "Superliga", "Rozgrywki"),
        ("/administracja/druzyny", "Drużyna Testowa", "Drużyny"),
    ],
)
def test_listy_renderuja_dane_i_aktywne_menu(adres: str, tekst: str, sekcja: str) -> None:
    odpowiedz = (
        aplikacja_z_katalogiem(KatalogPodstawowyInMemoryRepository()).test_client().get(adres)
    )
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert tekst in tresc and f">{sekcja}</span>" in tresc
    assert "Akcje" in tresc and ">Mecze</a>" in tresc


def test_filtry_rozgrywek_docieraja_do_repozytorium() -> None:
    repo = KatalogPodstawowyInMemoryRepository()
    odpowiedz = (
        aplikacja_z_katalogiem(repo)
        .test_client()
        .get("/administracja/rozgrywki?szukaj=Liga&id_sezon=195&plec=M&sortowanie=-nazwa")
    )
    assert odpowiedz.status_code == 200
    assert repo.filtry == FiltryKatalogu(szukaj="Liga", id_sezon=195, plec="M", sortowanie="-nazwa")


def test_filtry_druzyn_i_link_do_meczow_zachowuja_sezon() -> None:
    repo = KatalogPodstawowyInMemoryRepository()
    tresc = (
        aplikacja_z_katalogiem(repo)
        .test_client()
        .get("/administracja/druzyny?miasto=Kielce&wycofany=0")
        .get_data(as_text=True)
    )
    assert repo.filtry is not None
    assert repo.filtry.miasto == "Kielce" and repo.filtry.wycofany is False
    assert "/administracja/mecze?id_sezon=195&amp;druzyna=Dru%C5%BCyna+Testowa" in tresc


@pytest.mark.parametrize(
    "adres",
    [
        "/administracja/sezony?sortowanie=inne",
        "/administracja/rozgrywki?id_sezon=999",
        "/administracja/druzyny?plec=X",
        "/administracja/druzyny?strona=0",
    ],
)
def test_bledne_parametry_zwracaja_400(adres: str) -> None:
    klient = aplikacja_z_katalogiem(KatalogPodstawowyInMemoryRepository()).test_client()
    assert klient.get(adres).status_code == 400
