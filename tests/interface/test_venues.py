import pytest
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe

from handball.app_factory import AplikacjaFactory
from handball.domain.catalogs import FiltryKatalogu, PozycjaHali, StronaKatalogu
from handball.domain.errors import BladOdczytuDanych
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class HalaStubRepository:
    def __init__(self) -> None:
        self.pozycje = [PozycjaHali(7, "Hala Testowa", "Kielce", "Sportowa 1", 4200, 18)]
        self.filtry: FiltryKatalogu | None = None
        self.awaria = False

    def pobierz_hale(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaHali]:
        if self.awaria:
            raise BladOdczytuDanych("Test błędu")
        self.filtry = filtry
        return StronaKatalogu(self.pozycje, len(self.pozycje), filtry.strona, filtry.rozmiar_strony)


@pytest.fixture()
def repozytorium() -> HalaStubRepository:
    return HalaStubRepository()


@pytest.fixture()
def klient_hal(repozytorium: HalaStubRepository) -> FlaskClient:
    zaleznosci = ZaleznosciZadaniaFactory(fabryka_katalogu_hal=lambda: repozytorium)
    return (
        AplikacjaFactory(ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci))
        .utworz()
        .test_client()
    )


def test_lista_renderuje_dane_i_aktywna_nawigacje(klient_hal: FlaskClient) -> None:
    odpowiedz = klient_hal.get("/administracja/hale")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Hala Testowa" in tresc and "Sportowa 1" in tresc
    assert '<a class="active" href="/administracja/hale">' in tresc
    assert 'href="/administracja/hale/7"' in tresc
    assert '<th scope="col">Akcje</th>' in tresc
    assert "<td>18</td>" in tresc


def test_filtry_docieraja_do_serwisu(
    klient_hal: FlaskClient, repozytorium: HalaStubRepository
) -> None:
    odpowiedz = klient_hal.get(
        "/administracja/hale?szukaj=Arena&miasto=Kielce&pojemnosc_min=1000"
        "&sortowanie=-liczba_meczow&strona=2&rozmiar_strony=50"
    )
    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryKatalogu(
        szukaj="Arena",
        miasto="Kielce",
        pojemnosc_min=1000,
        sortowanie="-liczba_meczow",
        strona=2,
        rozmiar_strony=50,
    )


@pytest.mark.parametrize(
    "parametry",
    [
        "pojemnosc_min=-1",
        "strona=0",
        "rozmiar_strony=101",
        "sortowanie=niedozwolone",
        "szukaj=" + "x" * 201,
    ],
)
def test_odrzuca_bledne_parametry(klient_hal: FlaskClient, parametry: str) -> None:
    assert klient_hal.get("/administracja/hale?" + parametry).status_code == 400


def test_rozroznia_pusty_wynik_i_blad_bazy(
    klient_hal: FlaskClient, repozytorium: HalaStubRepository
) -> None:
    repozytorium.pozycje = []
    tresc = klient_hal.get("/administracja/hale").get_data(as_text=True)
    assert "Brak hal spełniających wybrane filtry." in tresc
    repozytorium.awaria = True
    assert klient_hal.get("/administracja/hale").status_code == 503


def test_escapuje_dane_i_nie_udostepnia_zapisu(
    klient_hal: FlaskClient, repozytorium: HalaStubRepository
) -> None:
    repozytorium.pozycje = [PozycjaHali(8, "<script>x</script>", None, None, None, 0)]
    tresc = klient_hal.get("/administracja/hale").get_data(as_text=True)
    assert "<script>x</script>" not in tresc
    assert "&lt;script&gt;x&lt;/script&gt;" in tresc
    assert klient_hal.post("/administracja/hale").status_code == 405
