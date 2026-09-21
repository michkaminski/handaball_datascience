from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.referee_details import SzczegolySedziegoInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.options import OpcjaWyboru
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


def aplikacja_z_karta(repo: SzczegolySedziegoInMemoryRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_szczegolow_sedziego=lambda: repo,
        fabryka_repozytorium_sezonow=lambda: SezonInMemoryRepository(
            [OpcjaWyboru(195, "2025/2026")]
        ),
        fabryka_repozytorium_rozgrywek=lambda: RozgrywkiInMemoryRepository(["Superliga"]),
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_karta_renderuje_zakladki_mecz_i_statystyki() -> None:
    tresc = (
        aplikacja_z_karta(SzczegolySedziegoInMemoryRepository())
        .test_client()
        .get("/administracja/sedziowie/11")
        .get_data(as_text=True)
    )
    assert "Kowalski Jan" in tresc and "Płock" in tresc
    assert 'data-referee-tab="dane"' in tresc and 'data-referee-tab="mecze"' in tresc
    assert 'data-referee-tab="statystyki"' in tresc
    assert "Wisła Płock" in tresc and "31:28" in tresc
    assert "/administracja/mecze/101" in tresc
    assert "/administracja/sedziowie/12" in tresc
    assert "Najczęściej sędziowane drużyny" in tresc


def test_filtry_docieraja_do_meczow_i_statystyk() -> None:
    repo = SzczegolySedziegoInMemoryRepository()
    odpowiedz = (
        aplikacja_z_karta(repo)
        .test_client()
        .get(
            "/administracja/sedziowie/11?zakladka=statystyki&sezon=195&rozgrywki=Superliga&druzyna=Wisła&strona_meczu=gospodarz&data_od=2026-01-01&data_do=2026-06-30&sortowanie=data"
        )
    )
    assert odpowiedz.status_code == 200
    assert repo.filtry_meczow == repo.filtry_statystyk
    assert repo.filtry_meczow is not None
    assert repo.filtry_meczow.id_sezon == 195 and repo.filtry_meczow.rozgrywki == "Superliga"
    assert repo.filtry_meczow.strona_meczu == "gospodarz"


def test_brak_sedziego_i_bledne_parametry() -> None:
    klient = aplikacja_z_karta(SzczegolySedziegoInMemoryRepository()).test_client()
    assert klient.get("/administracja/sedziowie/999").status_code == 404
    assert klient.get("/administracja/sedziowie/11?zakladka=inna").status_code == 400
    assert klient.get("/administracja/sedziowie/11?strona=0").status_code == 400
    assert klient.post("/administracja/sedziowie/11").status_code == 405
