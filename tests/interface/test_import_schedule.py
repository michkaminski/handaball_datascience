import base64
from dataclasses import replace

import pytest
from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.schedule import SezonyTerminarza, TerminarzInMemoryRepository, pozycje_terminarza

from handball.app_factory import AplikacjaFactory
from handball.domain.schedule import FiltryPobierania, PozycjaTerminarza
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class MeczeDoPobrania:
    def pobierz(self, filtry: FiltryPobierania) -> list[tuple[PozycjaTerminarza, bool]]:
        self.filtry = filtry
        return [
            (
                replace(
                    pozycja,
                    nazwa_rozgrywek=(
                        "LOTTO Superliga" if pozycja.id_mecz < 300 else "II Liga Mężczyzn"
                    ),
                ),
                pozycja.id_mecz == 201,
            )
            for pozycja in pozycje_terminarza()
        ]


def aplikacja(haslo: str) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_sezonow=lambda: SezonyTerminarza(),
        fabryka_terminarza=lambda: TerminarzInMemoryRepository(),
        fabryka_pobierania_meczow=lambda: MeczeDoPobrania(),
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def naglowki(haslo: str) -> dict[str, str]:
    token = base64.b64encode(f"admin:{haslo}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_bez_hasla_pobieranie_jest_otwarte(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HDS_IMPORT_PASSWORD", raising=False)
    odpowiedz = (
        aplikacja("").test_client().get("/administracja/import/mecze?id_sezon=5&id_rozgrywki=501")
    )
    assert odpowiedz.status_code == 200
    assert "data-import-z-terminarza" in odpowiedz.get_data(as_text=True)


def test_pobieranie_wymaga_logowania(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    assert (
        aplikacja("testowe-haslo").test_client().get("/administracja/import/mecze").status_code
        == 401
    )


def test_lista_ma_zaznaczenie_i_filtry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    klient = aplikacja("testowe-haslo").test_client()
    tresc = klient.get(
        "/administracja/import/mecze?id_sezon=5&id_rozgrywki=501",
        headers=naglowki("testowe-haslo"),
    ).get_data(as_text=True)
    assert "data-import-z-terminarza" in tresc
    assert 'name="akcja" value="rozpocznij_mecze"' in tresc
    assert 'name="mecze" value="201"' in tresc
    assert "Zaznacz wszystko" in tresc
    assert "Odznacz wszystko" in tresc
    assert "Zaznacz kolejkę" in tresc
    assert "Tylko mecze bez wyników" in tresc
    assert "Wynik bez danych" in tresc
    assert "Kolejki zakończone" in tresc
    assert "Superligi" in tresc
    assert "Ligi centralne" in tresc
    assert "Puchary Polski" in tresc
    assert "js/import_pobieranie.js" in tresc
    assert "Pobieranie meczów" in tresc
    assert '<a class="active" href="/administracja/import/mecze">' in tresc


def test_wynik_bez_danych_zostawia_mecz_do_aktualizacji(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    tresc = (
        aplikacja("testowe-haslo")
        .test_client()
        .get(
            "/administracja/import/mecze?id_sezon=5&id_rozgrywki=501&wynik_bez_danych=y",
            headers=naglowki("testowe-haslo"),
        )
        .get_data(as_text=True)
    )
    assert 'name="mecze" value="201"' in tresc
    assert 'name="mecze" value="202"' not in tresc
    assert 'name="mecze" value="204"' not in tresc


def test_kolejki_zakonczone_pomijaja_niedokonczona_kolejke(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    tresc = (
        aplikacja("testowe-haslo")
        .test_client()
        .get(
            "/administracja/import/mecze?id_sezon=5&kolejki_zakonczone=y",
            headers=naglowki("testowe-haslo"),
        )
        .get_data(as_text=True)
    )
    assert 'name="mecze" value="201"' in tresc
    assert 'name="mecze" value="204"' not in tresc
    assert 'name="mecze" value="301"' not in tresc


def test_bez_rozgrywek_i_filtra_prosi_o_wybor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    tresc = (
        aplikacja("testowe-haslo")
        .test_client()
        .get("/administracja/import/mecze?id_sezon=5", headers=naglowki("testowe-haslo"))
        .get_data(as_text=True)
    )
    assert "data-schedule-prompt" in tresc
    assert "data-import-z-terminarza" not in tresc


def test_bez_wynikow_zostawia_mecze_zaplanowane(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    tresc = (
        aplikacja("testowe-haslo")
        .test_client()
        .get(
            "/administracja/import/mecze?id_sezon=5&bez_wynikow=y",
            headers=naglowki("testowe-haslo"),
        )
        .get_data(as_text=True)
    )
    assert 'name="mecze" value="204"' in tresc
    assert 'name="mecze" value="301"' in tresc
    assert 'name="mecze" value="201"' not in tresc


def test_poziom_ii_ligi_zostawia_te_rozgrywki(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDS_IMPORT_PASSWORD", "testowe-haslo")
    tresc = (
        aplikacja("testowe-haslo")
        .test_client()
        .get(
            "/administracja/import/mecze?id_sezon=5&grupa=ii_liga",
            headers=naglowki("testowe-haslo"),
        )
        .get_data(as_text=True)
    )
    assert 'name="mecze" value="301"' in tresc
    assert 'name="mecze" value="201"' not in tresc
    assert 'value="ii_liga" checked' in tresc
