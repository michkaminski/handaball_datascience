import base64
from pathlib import Path
from uuid import UUID

import pytest
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


def test_import_bez_hasla_jest_otwarty(tmp_path: Path) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, ""
    )
    assert aplikacja.test_client().get("/administracja/import").status_code == 200


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


def test_panel_ma_import_tabel_z_wyborem_sezonu(tmp_path: Path) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    klient_api = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient_api, ImportTestRepository())
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, "testowe-haslo"
    )
    klient = aplikacja.test_client()
    naglowki = {"Authorization": "Basic " + base64.b64encode(b"admin:testowe-haslo").decode()}
    html = klient.get("/administracja/import", headers=naglowki).get_data(as_text=True)
    assert 'value="rozpocznij_tabele"' in html
    assert '<option value="195" selected>2026/2027 (bieżący)</option>' in html
    assert 'value="12007" data-nazwa="LOTTO Superliga" checked' in html
    assert 'value="12016" data-nazwa="I Liga Grupa A">' in html
    html = klient.get("/administracja/import?sezon_tabel=194", headers=naglowki).get_data(
        as_text=True
    )
    assert "Rozgrywki sezonu 2025/2026" in html and 'value="11592"' in html
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_tabele", "sezon_tabel": "194", "ligi": "11592"},
    )
    assert odpowiedz.status_code == 303
    html = klient.get(odpowiedz.headers["Location"], headers=naglowki).get_data(as_text=True)
    assert "Tylko tabele" in html and "sezon <strong>2025/2026</strong>" in html
    zle = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_tabele", "sezon_tabel": "194", "ligi": "12007"},
    )
    assert zle.status_code == 400


@pytest.mark.parametrize(
    "wpis",
    ["206511", " 206511 ", "https://rozgrywki.zprp.pl/?Sezon=195&Rozgrywki=12007&Zawody=206511"],
)
def test_import_jednego_meczu_z_panelu(tmp_path: Path, wpis: str) -> None:
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
    assert 'id="import-meczu"' in html and 'value="rozpocznij_mecz"' in html
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_mecz", "mecz": wpis},
    )
    assert odpowiedz.status_code == 303
    adres = odpowiedz.headers["Location"]
    serwis.krok(UUID(adres.rsplit("/", 1)[1]).hex)
    html = klient.get(adres, headers=naglowki).get_data(as_text=True)
    assert "Jeden mecz" in html and "Mecz <strong>206511</strong>: A – B" in html
    assert 'value="zastosuj"' in html
    assert klient_api.zapytania == ["pokaz_mecze_szczegoly.php"]
    klient.post(
        adres, headers=naglowki, data={"csrf": csrf, "akcja": "zastosuj", "potwierdzenie": "tak"}
    )
    html = klient.get(adres, headers=naglowki).get_data(as_text=True)
    assert "/mecze/206511" in html and "mecz 206511" in html
    assert repo.zapisy == 1


@pytest.mark.parametrize(
    "wpis",
    ["206511\n206512", "206511, 206512", "206511 206512"],
)
def test_import_listy_meczow_z_panelu(tmp_path: Path, wpis: str) -> None:
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
    assert "Pobieranie meczów" in html and "<textarea" in html
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_mecz", "mecz": wpis},
    )
    assert odpowiedz.status_code == 303
    adres = odpowiedz.headers["Location"]
    identyfikator = UUID(adres.rsplit("/", 1)[1]).hex
    for _ in range(5):
        if serwis.krok(identyfikator).status != "POBIERANIE":
            break
    html = klient.get(adres, headers=naglowki).get_data(as_text=True)
    assert "Wybrane mecze" in html and "206512 — C – D" in html and "206511 — A – B" in html
    assert klient_api.zapytania == ["pokaz_mecze_szczegoly.php", "pokaz_mecze_szczegoly.php"]
    klient.post(
        adres, headers=naglowki, data={"csrf": csrf, "akcja": "zastosuj", "potwierdzenie": "tak"}
    )
    html = klient.get(adres, headers=naglowki).get_data(as_text=True)
    assert "2 mecze" in html and repo.zapisy == 1


def test_import_zaznaczonych_meczow_z_terminarza(tmp_path: Path) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    klient_api = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient_api, ImportTestRepository())
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, "testowe-haslo"
    )
    klient = aplikacja.test_client()
    naglowki = {"Authorization": "Basic " + base64.b64encode(b"admin:testowe-haslo").decode()}
    klient.get("/administracja/import", headers=naglowki)
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_mecze", "mecze": ["206511", "206512"]},
    )
    assert odpowiedz.status_code == 303
    assert klient_api.zapytania == []
    assert serwis.magazyn.historia()[0].id_mecze == [206511, 206512]


def test_import_zaznaczenia_odrzuca_pusta_liste(tmp_path: Path) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    serwis = ImportService(ImportFileStore(tmp_path), ImportTestClient(), ImportTestRepository())
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, "testowe-haslo"
    )
    klient = aplikacja.test_client()
    naglowki = {"Authorization": "Basic " + base64.b64encode(b"admin:testowe-haslo").decode()}
    klient.get("/administracja/import", headers=naglowki)
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_mecze"},
    )
    assert odpowiedz.status_code == 400
    assert "Zaznacz przynajmniej jeden mecz." in odpowiedz.get_data(as_text=True)


@pytest.mark.parametrize("wpis", ["", "abc", "999999"])
def test_import_jednego_meczu_odrzuca_bledny_numer(tmp_path: Path, wpis: str) -> None:
    aplikacja = AplikacjaFactory(ustawienia_testowe()).utworz()
    klient_api = ImportTestClient()
    serwis = ImportService(ImportFileStore(tmp_path), klient_api, ImportTestRepository())
    aplikacja.view_functions["administracja.import_danych"] = ImportPanelView.as_view(
        "test_import", serwis, "testowe-haslo"
    )
    klient = aplikacja.test_client()
    naglowki = {"Authorization": "Basic " + base64.b64encode(b"admin:testowe-haslo").decode()}
    klient.get("/administracja/import", headers=naglowki)
    with klient.session_transaction() as sesja:
        csrf = sesja["import_csrf"]
    odpowiedz = klient.post(
        "/administracja/import",
        headers=naglowki,
        data={"csrf": csrf, "akcja": "rozpocznij_mecz", "mecz": wpis},
    )
    assert odpowiedz.status_code == 400
    assert klient_api.zapytania == []
