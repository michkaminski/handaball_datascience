from decimal import Decimal

import pytest
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe

from handball.app_factory import AplikacjaFactory
from handball.domain.classifications import (
    FiltryKlasyfikacji,
    Klasyfikacja,
    PozycjaSkladu,
    PozycjaStrzelca,
    PozycjaTabeli,
    Sklad,
    StronaKlasyfikacji,
    SzczegolySkladu,
    SzczegolyTabeli,
)
from handball.domain.options import OpcjaWyboru
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class KlasyfikacjaStubRepository:
    def __init__(self) -> None:
        self.filtry: FiltryKlasyfikacji | None = None
        self.punkty_bonusowe: int | None = 1

    def pobierz_sklady(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Sklad]:
        self.filtry = filtry
        return StronaKlasyfikacji(
            [Sklad(30, "2025/2026", "Test Kielce", "Superliga, Puchar Polski")],
            1,
            filtry.strona,
            filtry.rozmiar_strony,
        )

    def pobierz_szczegoly_skladu(self, id_zespol_sezon: int) -> SzczegolySkladu | None:
        if id_zespol_sezon != 30:
            return None
        return SzczegolySkladu(
            Sklad(30, "2025/2026", "Test Kielce", "Superliga, Puchar Polski"),
            [
                PozycjaSkladu(
                    7,
                    "2025/2026",
                    "Test Kielce",
                    "Jan Kowalski",
                    9,
                    "Rozgrywający",
                    Decimal("190.0"),
                    Decimal("88.0"),
                ),
                PozycjaSkladu(
                    8,
                    "2025/2026",
                    "Test Kielce",
                    "Adam Nowak",
                    1,
                    "Bramkarz",
                    Decimal("195.0"),
                    Decimal("92.0"),
                ),
            ],
        )

    def pobierz_strzelcow(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[PozycjaStrzelca]:
        self.filtry = filtry
        return StronaKlasyfikacji(
            [
                PozycjaStrzelca(
                    1,
                    7,
                    "2025/2026",
                    "Superliga",
                    "Jan Kowalski",
                    "Test Kielce",
                    1,
                    20,
                    120,
                    Decimal("6.00"),
                    20,
                    25,
                    Decimal("80.00"),
                    8,
                )
            ],
            1,
            filtry.strona,
            filtry.rozmiar_strony,
        )

    def pobierz_tabele(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Klasyfikacja]:
        self.filtry = filtry
        return StronaKlasyfikacji(
            [Klasyfikacja(40, "2025/2026", "Superliga", "Tabela główna", "Grupa A")],
            1,
            filtry.strona,
            filtry.rozmiar_strony,
        )

    def pobierz_szczegoly_tabeli(self, id_tabela_grupa: int) -> SzczegolyTabeli | None:
        if id_tabela_grupa != 40:
            return None
        return SzczegolyTabeli(
            Klasyfikacja(40, "2025/2026", "Superliga", "Tabela główna", "Grupa A"),
            [
                PozycjaTabeli(
                    1,
                    "2025/2026",
                    "Superliga",
                    "Tabela główna",
                    "Grupa A",
                    77,
                    "Test Kielce",
                    1,
                    20,
                    18,
                    0,
                    1,
                    0,
                    1,
                    650,
                    500,
                    55,
                    self.punkty_bonusowe,
                )
            ],
        )

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        return [OpcjaWyboru(10, "2025/2026")]

    def pobierz_opcje_rozgrywek(self, id_sezon: int | None) -> list[OpcjaWyboru]:
        return [OpcjaWyboru(20, "Superliga")]


@pytest.fixture()
def repozytorium() -> KlasyfikacjaStubRepository:
    return KlasyfikacjaStubRepository()


@pytest.fixture()
def klient_klasyfikacji(repozytorium: KlasyfikacjaStubRepository) -> FlaskClient:
    zaleznosci = ZaleznosciZadaniaFactory(fabryka_klasyfikacji=lambda: repozytorium)
    return (
        AplikacjaFactory(ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci))
        .utworz()
        .test_client()
    )


@pytest.mark.parametrize(
    "adres,tekst,aktywny",
    [
        ("/administracja/sklady", "Puchar Polski", "/administracja/sklady"),
        ("/administracja/strzelcy", "6.00", "/administracja/strzelcy"),
        ("/administracja/tabele", "Tabela główna", "/administracja/tabele"),
    ],
)
def test_zakladki_renderuja_dane_i_aktywne_menu(
    klient_klasyfikacji: FlaskClient, adres: str, tekst: str, aktywny: str
) -> None:
    odpowiedz = klient_klasyfikacji.get(adres)
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert tekst in tresc
    assert f'<a class="active" href="{aktywny}">' in tresc


def test_filtry_docieraja_do_repozytorium(
    klient_klasyfikacji: FlaskClient, repozytorium: KlasyfikacjaStubRepository
) -> None:
    odpowiedz = klient_klasyfikacji.get(
        "/administracja/strzelcy?szukaj=Jan&id_sezon=10&id_rozgrywki=20&sortowanie=-bramki&strona=2&rozmiar_strony=50"
    )
    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryKlasyfikacji("Jan", 10, 20, 2, 50, "-bramki")


@pytest.mark.parametrize(
    "parametry",
    ["strona=0", "rozmiar_strony=101", "sortowanie=brak", "id_sezon=999", "id_rozgrywki=999"],
)
def test_odrzuca_bledne_parametry(klient_klasyfikacji: FlaskClient, parametry: str) -> None:
    assert klient_klasyfikacji.get("/administracja/tabele?" + parametry).status_code == 400


def test_puste_wartosci_filtrow_oznaczaja_wszystkie(
    klient_klasyfikacji: FlaskClient, repozytorium: KlasyfikacjaStubRepository
) -> None:
    odpowiedz = klient_klasyfikacji.get(
        "/administracja/sklady?id_sezon=&id_rozgrywki=&sortowanie=-sezon"
    )
    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryKlasyfikacji(sortowanie="-sezon")


def test_listy_maja_grupowane_wiersze_i_akcje_szczegolow(
    klient_klasyfikacji: FlaskClient,
) -> None:
    sklad = klient_klasyfikacji.get("/administracja/sklady").get_data(as_text=True)
    tabela = klient_klasyfikacji.get("/administracja/tabele").get_data(as_text=True)
    assert "Superliga, Puchar Polski" in sklad
    assert 'data-detail-href="/administracja/sklady/30"' in sklad
    assert 'data-detail-href="/administracja/tabele/40"' in tabela
    assert "Grupa A" in tabela
    assert "Szczegóły" in sklad
    assert "Szczegóły" in tabela


@pytest.mark.parametrize(
    "adres,tekst",
    [
        ("/administracja/sklady/30", "Jan Kowalski"),
        ("/administracja/tabele/40", "Test Kielce"),
    ],
)
def test_szczegoly_renderuja_zawartosc(
    klient_klasyfikacji: FlaskClient, adres: str, tekst: str
) -> None:
    odpowiedz = klient_klasyfikacji.get(adres)
    assert odpowiedz.status_code == 200
    assert tekst in odpowiedz.get_data(as_text=True)


@pytest.mark.parametrize("adres", ["/administracja/sklady/999", "/administracja/tabele/999"])
def test_brak_szczegolow_zwraca_404(klient_klasyfikacji: FlaskClient, adres: str) -> None:
    assert klient_klasyfikacji.get(adres).status_code == 404


def test_sklad_sortuje_i_koloruje_zawodnikow_wedlug_pozycji(
    klient_klasyfikacji: FlaskClient,
) -> None:
    tresc = klient_klasyfikacji.get("/administracja/sklady/30").get_data(as_text=True)
    assert tresc.index("Adam Nowak") < tresc.index("Jan Kowalski")
    assert tresc.count('class="roster-player"') == 2
    assert tresc.count("--position-hue:") == 2
    assert 'class="roster-legend"' in tresc


def test_szczegoly_tabeli_bez_kryteriow_z_linkiem_do_druzyny(
    klient_klasyfikacji: FlaskClient,
) -> None:
    tresc = klient_klasyfikacji.get("/administracja/tabele/40").get_data(as_text=True)
    assert "Kryteria" not in tresc
    assert "<th>Bonus</th>" in tresc
    assert 'href="/administracja/druzyny/77"' in tresc
    assert "data-team-modal-link" in tresc
    assert "data-team-modal-dialog" in tresc


@pytest.mark.parametrize("punkty_bonusowe,widoczny", [(None, False), (0, True), (2, True)])
def test_kolumna_bonus_ukryta_gdy_brak_wartosci(
    klient_klasyfikacji: FlaskClient,
    repozytorium: KlasyfikacjaStubRepository,
    punkty_bonusowe: int | None,
    widoczny: bool,
) -> None:
    repozytorium.punkty_bonusowe = punkty_bonusowe
    tresc = klient_klasyfikacji.get("/administracja/tabele/40").get_data(as_text=True)
    assert ("<th>Bonus</th>" in tresc) is widoczny
