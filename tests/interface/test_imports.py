import base64
from pathlib import Path
from uuid import UUID

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.import_data import ImportTestClient
from tests.unit.test_import_service import ImportTestRepository

from handball.app_factory import AplikacjaFactory
from handball.infrastructure.import_store import ImportFileStore
from handball.interface.admin.views.import_views import ImportPanelView
from handball.services.import_service import ImportService


def test_uprawnienia_csrf_zatwierdzenie_i_ponowienie(tmp_path: Path) -> None:
    aplikacja: Flask = AplikacjaFactory(ustawienia_testowe()).utworz()
    repo = ImportTestRepository()
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), repo)
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, "testowe-haslo"
    )
    klient = aplikacja.test_client()
    adres = "/administracja/import"
    assert klient.get(adres).status_code == 401
    assert klient.post(adres).status_code == 401
    naglowki = {"Authorization": "Basic " + base64.b64encode(b"admin:testowe-haslo").decode()}
    assert klient.get(adres, headers=naglowki).status_code == 200
    assert klient.post(adres, headers=naglowki).status_code == 400
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        adres,
        headers=naglowki,
        data={
            "csrf": csrf,
            "akcja": "rozpocznij",
            "sezon": "195",
            "ligi": "12007",
        },
    )
    assert odpowiedz.status_code == 303
    adres = odpowiedz.headers["Location"]
    assert klient.get(adres, headers=naglowki).status_code == 200
    ident = UUID(adres.rsplit("/", 1)[1]).hex
    for _ in range(20):
        if serwis.krok(ident).status == "PODGLAD":
            break
    assert repo.zapisy == 0
    assert (
        klient.post(adres, headers=naglowki, data={"csrf": csrf, "akcja": "zastosuj"}).status_code
        == 400
    )
    assert (
        klient.post(
            adres,
            headers=naglowki,
            data={"csrf": csrf, "akcja": "zastosuj", "potwierdzenie": "tak"},
        ).status_code
        == 303
    )
    assert repo.zapisy == 1
    assert b"ZAPISANO" in klient.get(adres, headers=naglowki).data


def test_import_bez_konfiguracji_jest_zablokowany(tmp_path: Path) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, ""
    )
    assert aplikacja.test_client().get("/administracja/import").status_code == 503


def test_przycisk_uzupelnienia_i_pusty_wynik(tmp_path: Path) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    klient_api = ImportTestClient()
    repo = ImportTestRepository()
    serwis = ImportService(ImportFileStore(tmp_path), klient_api, repo)
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, "testowe-haslo"
    )
    klient = aplikacja.test_client()
    naglowki = {"Authorization": "Basic " + base64.b64encode(b"admin:testowe-haslo").decode()}
    html = klient.get("/administracja/import", headers=naglowki).get_data(as_text=True)
    assert 'name="tryb" value="pelny"' in html
    assert 'name="tryb" value="uzupelniajacy"' in html
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={
            "csrf": csrf,
            "akcja": "rozpocznij",
            "sezon": "195",
            "ligi": "12007",
            "tryb": "uzupelniajacy",
        },
    )
    assert odpowiedz.status_code == 303
    html = klient.get(odpowiedz.headers["Location"], headers=naglowki).get_data(as_text=True)
    assert "Uzupełniający" in html
    assert "Nie znaleziono meczów wymagających uzupełnienia" in html
    assert 'id="pobieranie"' not in html
    assert 'value="zastosuj"' not in html
    assert klient_api.zapytania == []
    assert repo.zapisy == 0
