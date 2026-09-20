from dataclasses import replace
from decimal import Decimal
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

import pytest
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe
from tests.helpers.competition_repository import RozgrywkiInMemoryRepository
from tests.helpers.season_repository import SezonInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.domain.errors import BladOdczytuDanych
from handball.domain.options import OpcjaWyboru
from handball.domain.players import FiltryZawodnikow, PozycjaListyZawodnikow, StronaZawodnikow
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

ZAWODNIK = PozycjaListyZawodnikow(
    7,
    "Jan",
    "Testowy",
    1998,
    ("BR", "RO"),
    ("Drużyna A", "Drużyna B"),
    Decimal("192.0"),
    Decimal("94.5"),
)


class ZawodnikStubRepository:
    def __init__(self, pozycje: list[PozycjaListyZawodnikow]) -> None:
        self.pozycje = pozycje
        self.filtry: FiltryZawodnikow | None = None
        self.awaria = False

    def pobierz_pozycje(self) -> list[str]:
        return ["BR", "RO"]

    def pobierz_liste(self, filtry: FiltryZawodnikow) -> StronaZawodnikow:
        if self.awaria:
            raise BladOdczytuDanych("Test błędu")
        self.filtry = filtry
        return StronaZawodnikow(self.pozycje[:20], len(self.pozycje), filtry.strona, 20)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.adresy: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        adres = dict(attrs).get("href")
        if tag == "a" and adres:
            self.adresy.append(adres)


@pytest.fixture()
def repozytorium() -> ZawodnikStubRepository:
    return ZawodnikStubRepository([ZAWODNIK])


@pytest.fixture()
def klient_zawodnikow(repozytorium: ZawodnikStubRepository) -> FlaskClient:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_sezonow=lambda: SezonInMemoryRepository(
            [OpcjaWyboru(195, "2026/2027")]
        ),
        fabryka_repozytorium_rozgrywek=lambda: RozgrywkiInMemoryRepository(["Liga"]),
        fabryka_repozytorium_zawodnikow=lambda: repozytorium,
    )
    return (
        AplikacjaFactory(ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci))
        .utworz()
        .test_client()
    )


def test_lista_i_nawigacja(klient_zawodnikow: FlaskClient) -> None:
    odpowiedz = klient_zawodnikow.get("/administracja/zawodnicy")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Testowy" in tresc
    assert "Drużyna A, Drużyna B" in tresc
    assert "Mecze w składzie" not in tresc
    assert "Bramki" not in tresc
    assert "192.0 cm" in tresc and "94.5 kg" in tresc
    assert '<a class="active" href="/administracja/zawodnicy">' in tresc
    assert 'href="/administracja/mecze" class="active">Dane' in tresc
    assert 'name="sortowanie" value="nazwisko"' in tresc
    assert "<select" not in tresc.split('name="sortowanie"')[0].split("<form")[-1]
    assert "Dodaj zawodnika" not in tresc


def test_filtry_docieraja_do_serwisu(
    klient_zawodnikow: FlaskClient, repozytorium: ZawodnikStubRepository
) -> None:
    odpowiedz = klient_zawodnikow.get(
        "/administracja/zawodnicy",
        query_string={
            "id_sezon": "195",
            "rozgrywki": "Liga",
            "druzyna": " A ",
            "pozycja": "BR",
            "rocznik": "1998",
            "szukaj": " Jan ",
            "sortowanie": "-waga",
            "strona": "2",
            "rozmiar_strony": "50",
        },
    )
    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryZawodnikow(
        id_sezon=195,
        rozgrywki="Liga",
        druzyna="A",
        pozycja="BR",
        rocznik=1998,
        szukaj="Jan",
        sortowanie="-waga",
        strona=2,
        rozmiar_strony=50,
    )


@pytest.mark.parametrize(
    "parametry",
    [
        {"id_sezon": "abc"},
        {"id_sezon": "-1"},
        {"rozgrywki": "Nieznana"},
        {"pozycja": "Nieznana"},
        {"rocznik": "abc"},
        {"rocznik": "0"},
        {"rocznik": "10000"},
        {"strona": "0"},
        {"strona": "abc"},
        {"strona": ""},
        {"rozmiar_strony": "0"},
        {"rozmiar_strony": "101"},
        {"rozmiar_strony": "x"},
        {"sortowanie": "--nazwisko"},
        {"sortowanie": "niedozwolone"},
        {"szukaj": "x" * 201},
    ],
)
def test_odrzuca_bledne_parametry(
    klient_zawodnikow: FlaskClient, parametry: dict[str, str]
) -> None:
    assert (
        klient_zawodnikow.get("/administracja/zawodnicy", query_string=parametry).status_code == 400
    )


def test_puste_pola_sa_opcjonalne(klient_zawodnikow: FlaskClient) -> None:
    assert (
        klient_zawodnikow.get(
            "/administracja/zawodnicy?rocznik=&id_sezon=&pozycja=&szukaj="
        ).status_code
        == 200
    )


def test_pusty_wynik_i_blad_bazy_sa_rozne(
    klient_zawodnikow: FlaskClient, repozytorium: ZawodnikStubRepository
) -> None:
    repozytorium.pozycje = []
    odpowiedz = klient_zawodnikow.get("/administracja/zawodnicy")
    assert odpowiedz.status_code == 200
    assert "Brak zawodników spełniających wybrane filtry." in odpowiedz.get_data(as_text=True)
    assert 'class="toolbar paginacja"' not in odpowiedz.get_data(as_text=True)
    repozytorium.awaria = True
    assert klient_zawodnikow.get("/administracja/zawodnicy").status_code == 503


def test_linki_zachowuja_filtry_i_sortowanie_resetuje_strone(
    klient_zawodnikow: FlaskClient, repozytorium: ZawodnikStubRepository
) -> None:
    repozytorium.pozycje = [ZAWODNIK] * 45
    odpowiedz = klient_zawodnikow.get(
        "/administracja/zawodnicy?szukaj=Jan&sortowanie=-waga&strona=2"
    )
    parser = LinkParser()
    parser.feed(odpowiedz.get_data(as_text=True))
    parametry = [parse_qs(urlparse(a).query) for a in parser.adresy if "strona=" in a]
    assert len(parametry) == 8
    assert all(p["szukaj"] == ["Jan"] for p in parametry)
    assert any(p["strona"] == ["3"] and p["sortowanie"] == ["-waga"] for p in parametry)
    assert any(p["strona"] == ["1"] and p["sortowanie"] == ["waga"] for p in parametry)


def test_braki_niepelne_sumy_i_escapowanie(
    klient_zawodnikow: FlaskClient, repozytorium: ZawodnikStubRepository
) -> None:
    repozytorium.pozycje = [
        replace(ZAWODNIK, imie="<script>alert(1)</script>", rocznik=None, wzrost=None),
        replace(ZAWODNIK, id_zawodnik=8, waga=None, druzyny=(), pozycje=()),
    ]
    tresc = klient_zawodnikow.get("/administracja/zawodnicy").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in tresc
    assert "&lt;script&gt;" in tresc
    assert "<td>192.0 cm</td>" in tresc
    assert "<td>—</td>" in tresc


@pytest.mark.parametrize("sortowanie", ["mecze", "-mecze", "bramki", "-bramki"])
def test_stare_linki_sortowania_pokazuja_nowa_liste(
    klient_zawodnikow: FlaskClient,
    repozytorium: ZawodnikStubRepository,
    sortowanie: str,
) -> None:
    odpowiedz = klient_zawodnikow.get(
        "/administracja/zawodnicy", query_string={"sortowanie": sortowanie}
    )
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert repozytorium.filtry is not None
    assert repozytorium.filtry.sortowanie == "nazwisko"
    assert "Mecze w składzie" not in tresc and "192.0 cm" in tresc


def test_lista_nie_udostepnia_zapisu(klient_zawodnikow: FlaskClient) -> None:
    assert klient_zawodnikow.post("/administracja/zawodnicy").status_code == 405
