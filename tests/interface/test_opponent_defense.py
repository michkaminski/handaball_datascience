from html import unescape

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.opponent_defense import (
    DefensywaRywalaPustyRepozytorium,
    DefensywaRywalaTestoweRepozytorium,
)
from tests.helpers.player_details import SzczegolyZawodnikaInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository
from tests.interface.test_players import ZAWODNIK, ZawodnikStubRepository

from handball.app_factory import AplikacjaFactory
from handball.contracts.opponent_defense_repository import DefensywaRywalaReadRepository
from handball.domain.options import OpcjaWyboru
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


def _aplikacja(defensywa_repo: DefensywaRywalaReadRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_sezonow=lambda: SezonInMemoryRepository(
            [OpcjaWyboru(195, "2026/2027")]
        ),
        fabryka_repozytorium_rozgrywek=lambda: RozgrywkiInMemoryRepository(["Liga"]),
        fabryka_repozytorium_zawodnikow=lambda: ZawodnikStubRepository([ZAWODNIK]),
        fabryka_szczegolow_zawodnika=lambda: SzczegolyZawodnikaInMemoryRepository(),
        fabryka_defensywy_rywala=lambda: defensywa_repo,
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_szczegolowa_strona_pokazuje_glowne_sekcje_i_wykresy() -> None:
    klient = _aplikacja(DefensywaRywalaTestoweRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7/defensywa-rywali")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Bramki zawodnika a poziom defensywy rywali" in tresc
    assert "Spis treści analizy" in tresc
    assert "data-defense-klasy" in tresc and "data-defense-boxplot" in tresc
    assert "data-defense-prawdopodobienstwa" in tresc and "data-defense-scatter" in tresc
    assert "data-defense-sortable" in tresc
    assert "← Powrót do karty zawodnika" in tresc
    assert "Interpretacja matematyczna" in tresc
    assert "Ograniczenia analizy" in tresc
    assert "vendor/echarts/echarts.min.js" in tresc
    assert "js/opponent_defense.js" in tresc


def test_przyklad_jednego_meczu_mozna_wybrac_parametrem() -> None:
    klient = _aplikacja(DefensywaRywalaTestoweRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7/defensywa-rywali?id_mecz_przykladu=1003")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "GA_team" in tresc
    assert "Klasa defensywy" in tresc


def test_404_dla_nieznanego_zawodnika() -> None:
    klient = _aplikacja(DefensywaRywalaPustyRepozytorium()).test_client()
    assert klient.get("/administracja/zawodnicy/999/defensywa-rywali").status_code == 404


def test_400_przy_niepoprawnym_filtrze() -> None:
    klient = _aplikacja(DefensywaRywalaTestoweRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7/defensywa-rywali?miejsce=nieznane")
    assert odpowiedz.status_code == 400


def test_brak_danych_pokazuje_komunikat_zamiast_bledu() -> None:
    klient = _aplikacja(DefensywaRywalaPustyRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7/defensywa-rywali")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Brak meczu z wyznaczonym Defense Factor" in tresc


def test_karta_zawodnika_ma_defensywe_rywali_w_formie_z_przyciskiem_szczegoly() -> None:
    klient = _aplikacja(DefensywaRywalaTestoweRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7?zakladka=forma")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert 'data-active-tab="forma"' in tresc
    assert 'data-player-tab="statystyki"' not in tresc
    sekcja = tresc.split('id="player-forma-defensywa"')[1]
    assert "data-defense-summary" in sekcja
    assert "Dane wykresu defensywy rywali" in sekcja
    assert "Bramki zawodnika a poziom defensywy rywali" in sekcja
    assert '/administracja/zawodnicy/7/defensywa-rywali" target="_blank"' in sekcja
    assert "Pokaż szczegóły" in tresc


def test_defensywa_w_formie_uwzglednia_filtry_karty_i_przekazuje_je_do_szczegolow() -> None:
    klient = _aplikacja(DefensywaRywalaTestoweRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7?zakladka=forma&przeciwnik=Nieznany")
    tresc = unescape(odpowiedz.get_data(as_text=True))
    assert odpowiedz.status_code == 200
    sekcja = tresc.split('id="player-forma-defensywa"')[1]
    assert "data-defense-summary-data" not in sekcja
    assert "Za mało meczów z wyznaczoną jakością defensywy rywala" in sekcja
    assert "/administracja/zawodnicy/7/defensywa-rywali?przeciwnik=Nieznany" in sekcja


def test_szczegoly_defensywy_przyjmuja_przeciwnika_i_wracaja_do_formy() -> None:
    klient = _aplikacja(DefensywaRywalaTestoweRepozytorium()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7/defensywa-rywali?przeciwnik=Nieznany")
    tresc = unescape(odpowiedz.get_data(as_text=True))
    assert odpowiedz.status_code == 200
    assert "przeciwnik: Nieznany" in tresc
    assert "zakladka=forma#player-forma-defensywa" in tresc
