from __future__ import annotations

import re
from dataclasses import replace
from datetime import datetime
from html import unescape

import pytest
from flask import Flask
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.match_repository import MeczInMemoryRepository
from tests.helpers.match_stage_repository import EtapMeczowInMemoryRepository
from tests.helpers.match_statistics_repository import FormaMeczuInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository
from tests.helpers.venue_repository import HalaInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow, SzczegolyMeczu
from handball.domain.options import OpcjaWyboru
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

POZYCJA_TESTOWA = PozycjaListyMeczow(
    id_mecz=12543,
    termin=datetime(2026, 9, 12, 18, 0),
    sezon="2026/2027",
    rozgrywki="ORLEN Superliga",
    gospodarz="Industria Kielce",
    gosc="Orlen Wisła Płock",
    mecz=DaneMeczu(id=12543, wynik_gosp_full=32, wynik_gosc_full=28),
    hala="Hala Legionów",
    runda="Runda zasadnicza",
    kolejka="Kolejka 1",
)

SZCZEGOLY_TESTOWE = SzczegolyMeczu(
    mecz=DaneMeczu(
        id=12543,
        wynik_gosp_full=32,
        wynik_gosc_full=28,
        wynik_gosp_pol=16,
        wynik_gosc_pol=13,
        dogrywka_1_full_gosp=32,
        dogrywka_1_full_gosc=28,
        data_faktyczna=datetime(2026, 9, 12, 18, 0),
    ),
    nazwa_gospodarz="Industria Kielce",
    nazwa_gosc="Orlen Wisła Płock",
    nazwa_sezon="2026/2027",
    nazwa_rozgrywki="ORLEN Superliga",
    nazwa_kolejka="Kolejka 1",
    nazwa_hala="Hala Legionów",
)

SEZONY_TESTOWE = [OpcjaWyboru(195, "2026/2027")]


def _aplikacja_z_repozytorium(
    pozycje: list[PozycjaListyMeczow] | None = None,
    szczegoly: dict[int, SzczegolyMeczu] | None = None,
) -> Flask:
    fabryka_zaleznosci = ZaleznosciZadaniaFactory(
        lambda: MeczInMemoryRepository(pozycje, szczegoly),
        lambda: SezonInMemoryRepository(SEZONY_TESTOWE),
        lambda: RozgrywkiInMemoryRepository(),
        lambda: HalaInMemoryRepository(),
        lambda: EtapMeczowInMemoryRepository(),
        fabryka_formy_meczu=lambda: FormaMeczuInMemoryRepository(),
    )
    fabryka = AplikacjaFactory(
        ustawienia_testowe(),
        rejestrator_widokow=WidokiRegistrar(fabryka_zaleznosci),
    )
    return fabryka.utworz()


@pytest.fixture()
def klient_z_danymi() -> FlaskClient:
    return _aplikacja_z_repozytorium([POZYCJA_TESTOWA]).test_client()


@pytest.fixture()
def klient_bez_danych() -> FlaskClient:
    return _aplikacja_z_repozytorium([]).test_client()


def test_lista_meczow_bez_filtrow_dziala(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc


def test_lista_meczow_odrzuca_niepoprawny_id_sezon(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?id_sezon=abc")

    assert odpowiedz.status_code == 400


def test_lista_meczow_odrzuca_niepoprawna_date(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?data_meczu=2026-13")

    assert odpowiedz.status_code == 400


def test_lista_meczow_przyjmuje_czesciowa_date(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?data_meczu=2026-09")

    assert odpowiedz.status_code == 200


def test_lista_meczow_zwraca_dane(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze?id_sezon=195")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc
    assert "32 : 28" in tresc
    assert "Hala Legionów" in tresc
    assert "2026/2027" in tresc
    assert "ORLEN Superliga" in tresc


def test_lista_meczow_sortowanie_jest_linkiem_w_naglowku(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert "sortowanie=-data" in tresc
    assert 'name="sortowanie"' not in tresc


def test_lista_meczow_pusty_wynik(klient_bez_danych: FlaskClient) -> None:
    odpowiedz = klient_bez_danych.get("/administracja/mecze?id_sezon=195")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Brak meczów spełniających wybrane filtry." in tresc


def test_runda_i_kolejka_filtruja_lacznie() -> None:
    pozycje = [
        POZYCJA_TESTOWA,
        replace(POZYCJA_TESTOWA, id_mecz=2, gospodarz="Inna kolejka", kolejka="Kolejka 2"),
        replace(POZYCJA_TESTOWA, id_mecz=3, gospodarz="Inna runda", runda="Play-off"),
    ]
    klient = _aplikacja_z_repozytorium(pozycje).test_client()
    odpowiedz = klient.get(
        "/administracja/mecze", query_string={"runda": "Runda zasadnicza", "kolejka": "Kolejka 1"}
    )
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc
    assert "Inna kolejka" not in tresc
    assert "Inna runda" not in tresc
    assert '<option selected value="Runda zasadnicza">' in tresc
    assert '<option selected value="Kolejka 1">' in tresc
    assert 'data-match-column="runda" hidden>Runda zasadnicza</td>' in tresc
    assert 'data-match-column="kolejka" hidden>Kolejka 1</td>' in tresc
    assert 'id="match-columns-dialog"' in tresc
    assert 'aria-haspopup="dialog"' in tresc
    assert "js/matches.js" in tresc


@pytest.mark.parametrize("pole", ["runda", "kolejka"])
def test_nieznana_opcja_etapu_zwraca_400(klient_z_danymi: FlaskClient, pole: str) -> None:
    assert (
        klient_z_danymi.get(
            "/administracja/mecze", query_string={pole: "nieistniejaca"}
        ).status_code
        == 400
    )


def test_filtry_etapow_sa_zachowane_w_sortowaniu_i_paginacji() -> None:
    klient = _aplikacja_z_repozytorium([POZYCJA_TESTOWA] * 25).test_client()
    odpowiedz = klient.get(
        "/administracja/mecze", query_string={"runda": "Runda zasadnicza", "kolejka": "Kolejka 1"}
    )
    tresc = unescape(odpowiedz.get_data(as_text=True))
    from html.parser import HTMLParser

    class LinkParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.adresy: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag == "a":
                adres = dict(attrs).get("href")
                if adres:
                    self.adresy.append(adres)

    parser = LinkParser()
    parser.feed(tresc)
    adresy = [a for a in parser.adresy if "sortowanie=-data" in a or "strona=2" in a]
    assert len(adresy) == 2
    assert all("runda=Runda+zasadnicza" in a and "kolejka=Kolejka+1" in a for a in adresy)


def test_lista_meczow_ma_link_do_szczegolow(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert "/administracja/mecze/12543" in tresc
    assert "Szczegóły" in tresc


def test_lista_meczow_wiersz_ma_adres_do_dwuklikniecia(klient_z_danymi: FlaskClient) -> None:
    odpowiedz = klient_z_danymi.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert 'data-href="/administracja/mecze/12543"' in tresc


def test_lista_meczow_pokazuje_dopisek_wyniku() -> None:
    pozycja = replace(
        POZYCJA_TESTOWA,
        mecz=replace(POZYCJA_TESTOWA.mecz, dogrywka_karne_gosp=6, dogrywka_karne_gosc=7),
    )
    klient = _aplikacja_z_repozytorium([pozycja]).test_client()

    odpowiedz = klient.get("/administracja/mecze")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "k 6-7" in tresc


def test_szczegoly_meczu_wyswietla_dane() -> None:
    klient = _aplikacja_z_repozytorium([POZYCJA_TESTOWA], {12543: SZCZEGOLY_TESTOWE}).test_client()

    odpowiedz = klient.get("/administracja/mecze/12543")
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert "Industria Kielce" in tresc
    assert "Orlen Wisła Płock" in tresc
    assert "32 : 28" in tresc
    assert "do przerwy 16 : 13" in tresc
    assert "dogrywka" in tresc
    assert "Rozegrany" in tresc


def test_szczegoly_meczu_nieistniejacego_zwraca_404() -> None:
    klient = _aplikacja_z_repozytorium([POZYCJA_TESTOWA], {}).test_client()

    odpowiedz = klient.get("/administracja/mecze/999999")

    assert odpowiedz.status_code == 404


def test_tylko_zakonczone_jest_domyslnie_zaznaczone_i_zachowuje_stan() -> None:
    repozytorium = MeczInMemoryRepository([POZYCJA_TESTOWA] * 25)
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_meczow=lambda: repozytorium,
        fabryka_repozytorium_sezonow=lambda: SezonInMemoryRepository(
            [OpcjaWyboru(195, "2026/2027")]
        ),
        fabryka_repozytorium_rozgrywek=lambda: RozgrywkiInMemoryRepository(["ORLEN Superliga"]),
        fabryka_repozytorium_hal=lambda: HalaInMemoryRepository([]),
        fabryka_repozytorium_etapow=lambda: EtapMeczowInMemoryRepository(),
    )
    klient = (
        AplikacjaFactory(ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci))
        .utworz()
        .test_client()
    )

    tresc = unescape(klient.get("/administracja/mecze").get_data(as_text=True))
    assert 'name="zakonczone" value="1" checked> Tylko zakończone' in tresc
    assert repozytorium.ostatnie_filtry.tylko_zakonczone is True

    tresc = unescape(klient.get("/administracja/mecze?zakonczone=0").get_data(as_text=True))
    assert 'name="zakonczone" value="1"> Tylko zakończone' in tresc
    assert repozytorium.ostatnie_filtry.tylko_zakonczone is False
    linki = re.findall(r'href="([^"]*sortowanie=[^"]*)"', tresc) + re.findall(
        r'href="([^"]*strona=2[^"]*)"', tresc
    )
    assert len(linki) == 2 and all("zakonczone=0" in link for link in linki)

    klient.get("/administracja/mecze?zakonczone=1&zakonczone=0")
    assert repozytorium.ostatnie_filtry.tylko_zakonczone is True


def test_lista_meczow_pokazuje_widzow_z_separatorem_i_brak_danych() -> None:
    z_widzami = replace(
        POZYCJA_TESTOWA,
        mecz=replace(POZYCJA_TESTOWA.mecz, widzowie=4250),
    )
    bez_danych = replace(POZYCJA_TESTOWA, id_mecz=12544, mecz=DaneMeczu(id=12544))
    tresc = (
        _aplikacja_z_repozytorium([z_widzami, bez_danych])
        .test_client()
        .get("/administracja/mecze")
        .get_data(as_text=True)
    )
    assert ">Widzowie</th>" in tresc
    assert '<td class="num">4 250</td>' in tresc
    assert '<td class="num">—</td>' in tresc
    assert 'colspan="11"' not in tresc


def test_szczegoly_meczu_maja_zakladke_analizy() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        mecz=replace(SZCZEGOLY_TESTOWE.mecz, id_zespol_gosp=1, id_zespol_gosc=2),
    )
    klient = _aplikacja_z_repozytorium([], {12543: szczegoly}).test_client()

    tresc = klient.get("/administracja/mecze/12543").get_data(as_text=True)

    assert 'id="match-panel-analysis"' in tresc
    assert "Porównanie drużyn" in tresc
    assert "--home-share: 53%" in tresc
    assert "Brak rozegranych meczów w sezonie." in tresc
    assert tresc.index('id="match-tab-basic"') < tresc.index('id="match-tab-analysis"')
    assert tresc.index('id="match-tab-analysis"') < tresc.index('id="match-tab-stats"')


def test_szczegoly_meczu_bez_wyniku_pokazuja_informacje() -> None:
    szczegoly = replace(SZCZEGOLY_TESTOWE, mecz=DaneMeczu(id=12543))
    klient = _aplikacja_z_repozytorium([], {12543: szczegoly}).test_client()

    tresc = klient.get("/administracja/mecze/12543").get_data(as_text=True)

    assert "Mecz nie ma jeszcze wyniku" in tresc
    assert "Porównanie drużyn" not in tresc
