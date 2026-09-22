from dataclasses import replace
from html import unescape

import pytest
from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.player_details import (
    MECZ_ZAWODNIKA,
    SzczegolyZawodnikaInMemoryRepository,
)
from tests.helpers.season_repository import SezonInMemoryRepository
from tests.interface.test_players import ZAWODNIK, ZawodnikStubRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.errors import BladOdczytuDanych
from handball.domain.options import OpcjaWyboru
from handball.domain.player_details import StronaMeczowZawodnika, WpisMeczowyZawodnika
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


def aplikacja_z_karta(repo: SzczegolyZawodnikaInMemoryRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_sezonow=lambda: SezonInMemoryRepository(
            [OpcjaWyboru(195, "2026/2027"), OpcjaWyboru(194, "2025/2026")]
        ),
        fabryka_repozytorium_rozgrywek=lambda: RozgrywkiInMemoryRepository(["Liga"]),
        fabryka_repozytorium_zawodnikow=lambda: ZawodnikStubRepository([ZAWODNIK]),
        fabryka_szczegolow_zawodnika=lambda: repo,
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_lista_ma_przycisk_i_adres_dwukliku() -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    tresc = klient.get("/administracja/zawodnicy").get_data(as_text=True)
    assert 'data-player-href="/administracja/zawodnicy/7"' in tresc
    assert 'href="/administracja/zawodnicy/7" target="_blank" rel="noopener">◎ Szczegóły' in tresc
    assert 'id="player-detail-dialog"' in tresc
    assert "js/player_details.js" in tresc


def test_karta_pokazuje_historie_bez_nadpisywania_danych() -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Jan Testowy" in tresc and "02.01.1998" in tresc
    assert "192.0" in tresc and "94.5" in tresc
    assert "190.0" not in tresc
    assert "Drużyna A" in tresc and "Drużyna B" in tresc
    assert "Liga" in tresc and "120" in tresc and "20/30" in tresc
    assert "2 min: 10 · U: 2 · D: 1" in tresc
    assert "<td>5</td><td>BR</td>" in tresc
    assert 'data-active-tab="profil"' in tresc
    assert "Wyniki 1–20 z 23" in tresc


def test_karta_ma_dodatkowe_podsumowanie_analityczne() -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7?zakladka=podsumowanie")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert 'data-active-tab="podsumowanie"' in tresc
    assert "Podsumowanie analityczne" in tresc
    assert "Mecze z wpisem" in tresc and ">23<" in tresc
    assert "Pokrycie danych o bramkach" in tresc and "23/23" in tresc
    assert "data-player-trend-wszystkie" in tresc
    assert "data-player-trend-dom" in tresc and "data-player-trend-wyjazd" in tresc
    assert "data-player-distribution" in tresc
    assert "wszystkie" in tresc.lower()
    assert "U siebie" in tresc and "Na wyjeździe" in tresc
    assert "vendor/echarts/echarts.min.js" in tresc


def test_karta_ma_zakladke_formy_i_regularnosci() -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    odpowiedz = klient.get("/administracja/zawodnicy/7?zakladka=forma")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert 'data-active-tab="forma"' in tresc
    assert "Forma i regularność" in tresc
    assert "Bramki i karne" not in tresc and "Jakość danych" not in tresc
    assert "data-player-form-dom" in tresc and "data-player-form-wyjazd" in tresc
    assert "data-player-boxplot" in tresc
    assert "Współczynnik zmienności" in tresc and "Średnia ucięta 10%" in tresc


def test_paginacja_i_filtry_meczow_zachowuja_zawodnika_i_zakladke() -> None:
    repo = SzczegolyZawodnikaInMemoryRepository()
    klient = aplikacja_z_karta(repo).test_client()
    tresc = unescape(
        klient.get(
            "/administracja/zawodnicy/7?id_sezon=195&rozgrywki=Liga&przeciwnik=Rywal&zakladka=mecze"
        ).get_data(as_text=True)
    )
    assert 'data-active-tab="mecze"' in tresc
    assert "/administracja/zawodnicy/7?" in tresc and "strona=2" in tresc
    assert "przeciwnik=Rywal" in tresc and "sortowanie=data" in tresc
    assert repo.filtry is not None and repo.filtry.przeciwnik == "Rywal"
    tresc = klient.get("/administracja/zawodnicy/7?strona=2&zakladka=mecze").get_data(as_text=True)
    assert "Wyniki 21–23 z 23" in tresc
    assert "Następna »" not in tresc
    assert "/administracja/mecze/121" in tresc


@pytest.mark.parametrize(
    "query",
    [
        "strona=0",
        "strona=x",
        "rozmiar_strony=101",
        "sortowanie=foo",
        "id_sezon=abc",
        "rozgrywki=nieznane",
        "zakladka=nieznana",
    ],
)
def test_bledne_parametry_karty_zwracaja_400(query: str) -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    assert klient.get("/administracja/zawodnicy/7?" + query).status_code == 400


def test_pusty_wynik_nie_usuwa_profilu_ani_historii() -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    tresc = klient.get("/administracja/zawodnicy/7?przeciwnik=Nieistniejacy").get_data(as_text=True)
    assert "Brak meczów zawodnika" in tresc and "192.0" in tresc
    assert 'data-active-tab="mecze"' in tresc


def test_404_i_brak_zapisu() -> None:
    klient = aplikacja_z_karta(SzczegolyZawodnikaInMemoryRepository()).test_client()
    assert klient.get("/administracja/zawodnicy/999").status_code == 404
    assert klient.post("/administracja/zawodnicy/7").status_code == 405


def test_503_przy_bledzie_odczytu(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = SzczegolyZawodnikaInMemoryRepository()

    def awaria(id_zawodnik: int) -> None:
        raise BladOdczytuDanych()

    monkeypatch.setattr(repo, "pobierz_szczegoly", awaria)
    assert (
        aplikacja_z_karta(repo).test_client().get("/administracja/zawodnicy/7").status_code == 503
    )


def test_presenter_nie_zamienia_brakow_karnych_na_zero_i_zachowuje_druzyne() -> None:
    mecz = replace(
        MECZ_ZAWODNIKA,
        mecz=replace(MECZ_ZAWODNIKA.mecz, mecz=replace(MECZ_ZAWODNIKA.mecz.mecz, zamiana=True)),
    )
    presenter = ZaleznosciZadaniaFactory().utworz_presenter_szczegolow_zawodnika()
    widok = presenter.przygotuj_mecze(StronaMeczowZawodnika([mecz], 1, 1, 20)).pozycje[0]
    assert widok.mecz.wynik == "25 : 30"
    assert widok.wpisy[0].druzyna == "Drużyna A"
    assert widok.wpisy[0].przeciwnik == "Rywal B"
    assert widok.wpisy[0].karne == "0/—"
    assert widok.wpisy[0].upomnienie == "Nie"
    assert widok.wpisy[0].dyskwalifikacja == "—"


def test_wiele_stron_ma_osobne_statystyki() -> None:
    drugi = WpisMeczowyZawodnika("gosc", replace(MECZ_ZAWODNIKA.wpisy[0].statystyki, bramki=5))
    mecz = replace(MECZ_ZAWODNIKA, wpisy=(*MECZ_ZAWODNIKA.wpisy, drugi))
    presenter = ZaleznosciZadaniaFactory().utworz_presenter_szczegolow_zawodnika()
    widok = presenter.przygotuj_mecze(StronaMeczowZawodnika([mecz], 1, 1, 20)).pozycje[0]
    assert widok.wiele_stron and len(widok.wpisy) == 2
    assert [w.bramki for w in widok.wpisy] == ["0", "5"]
