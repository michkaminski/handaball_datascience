from datetime import datetime

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.match_predictions import (
    MeczeLigoweInMemoryRepository,
    mecz_ligowy,
    mecze_dwoch_sezonow,
)
from tests.helpers.match_tips import TypowaniaInMemoryRepository
from tests.helpers.schedule import ZegarTestowy

from handball.app_factory import AplikacjaFactory
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

ADRES = "/administracja/raporty/typowania-meczow"


def aplikacja(repozytorium: TypowaniaInMemoryRepository | None = None) -> Flask:
    typowania = repozytorium or TypowaniaInMemoryRepository()
    ligowe = MeczeLigoweInMemoryRepository(
        [*mecze_dwoch_sezonow(), mecz_ligowy(204, datetime(2025, 9, 22, 18), 30, 10, None, None)]
    )
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_meczow_ligowych=lambda: ligowe,
        fabryka_typowan=lambda: typowania,
        zegar=ZegarTestowy(),
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_raport_w_sidebarze_i_katalogu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get(ADRES).get_data(as_text=True)
    assert f'<a class="active" href="{ADRES}">' in tresc
    assert f'href="{ADRES}"' in klient.get("/administracja/raporty").get_data(as_text=True)


def test_domyslnie_dzisiaj_i_wszystkie_ligi() -> None:
    repozytorium = TypowaniaInMemoryRepository()
    tresc = aplikacja(repozytorium).test_client().get(ADRES).get_data(as_text=True)
    assert 'name="data_od" value="2025-09-20"' in tresc
    assert 'name="data_do" value="2025-09-20"' in tresc
    assert repozytorium.zapytania[0][2] == frozenset()
    assert "data-tips-empty" in tresc
    assert "js/match_predictions.js" in tresc


def test_tabela_laczy_rozegrane_przyszle_i_bez_prognozy() -> None:
    tresc = (
        aplikacja()
        .test_client()
        .get(f"{ADRES}?data_od=2025-09-01&data_do=2026-02-28")
        .get_data(as_text=True)
    )
    assert "Historia prognoz" not in tresc
    naglowki = [
        tresc.index(n)
        for n in (
            "ORLEN Superliga · 2025/2026 · I runda · Seria 1",
            "ORLEN Superliga · 2025/2026 · I runda · Seria 2",
            "ORLEN Superliga · 2025/2026 · II runda · Seria 3",
        )
    ]
    assert naglowki == sorted(naglowki)
    assert tresc.count('data-tips-mode="po_meczu"') == 3
    assert tresc.count('data-tips-mode="biezaca"') == 1
    assert tresc.count('data-tips-mode="brak"') == 1
    assert 'data-href="/administracja/raporty/prognozy-meczow/201"' in tresc
    assert 'data-href="/administracja/terminarz/204"' in tresc
    assert "Score error" in tresc and "Przed meczem" in tresc and "Prognoza niedostępna" in tresc
    assert "Meczów: <b>5</b>" in tresc and "Rozegrane: <b>3</b>" in tresc
    assert '<option value="ORLEN Superliga">ORLEN Superliga</option>' in tresc


def test_wybrane_rozgrywki_zostaja_zaznaczone() -> None:
    repozytorium = TypowaniaInMemoryRepository()
    tresc = (
        aplikacja(repozytorium)
        .test_client()
        .get(f"{ADRES}?data_od=2025-09-01&data_do=2025-09-30&rozgrywki=ORLEN+Superliga")
        .get_data(as_text=True)
    )
    assert repozytorium.zapytania[0][2] == frozenset({"ORLEN Superliga"})
    assert '<option value="ORLEN Superliga" selected>' in tresc


def test_bledne_filtry_raportu() -> None:
    klient = aplikacja().test_client()
    assert klient.get(f"{ADRES}?data_od=abc").status_code == 400
    assert klient.get(f"{ADRES}?data_od=2025-09-10&data_do=2025-09-01").status_code == 400
    assert klient.get(f"{ADRES}?model=xyz").status_code == 400
    assert klient.post(ADRES).status_code == 405


def test_przycisk_druku_tabeli_typowan() -> None:
    tresc = (
        aplikacja()
        .test_client()
        .get(f"{ADRES}?data_od=2025-09-01&data_do=2026-02-28&rozgrywki=ORLEN+Superliga")
        .get_data(as_text=True)
    )
    assert 'data-print-table="#tips-table"' in tresc
    assert 'data-print-title="Typowania meczów"' in tresc
    assert "Rozgrywki: ORLEN Superliga" in tresc and "Meczów: 5" in tresc
    assert "js/print_table.js" in tresc
