from datetime import datetime

from tests.helpers.news import I_LIGA, SUPERLIGA_M, AktualnosciInMemoryRepository, mecz

from handball.domain.news import StrzelecAktualnosci, WystepAktualnosci
from handball.interface.presenters.news_presenter import AktualnosciPresenter
from handball.interface.view_models.news import AktualnosciViewModel
from handball.services.news_service import AktualnosciService


def _przygotuj(repozytorium: AktualnosciInMemoryRepository) -> AktualnosciViewModel:
    return AktualnosciPresenter().przygotuj(AktualnosciService(repozytorium).pobierz_aktualnosci())


def test_mecz_stosuje_zamiane_stron_i_oznacza_zwyciezce() -> None:
    widok = _przygotuj(
        AktualnosciInMemoryRepository(
            mecze=(
                mecz(1, SUPERLIGA_M.id_rozgrywki, 20, (20, 31), ("Wisła  Płock ", "Kielce"), True),
            )
        )
    )
    wiersz = widok.sekcje[0].mecze[0]
    assert (wiersz.gospodarz, wiersz.wynik, wiersz.gosc) == ("Kielce", "31:20", "Wisła Płock")
    assert wiersz.zwyciezca == "gospodarz"
    assert (wiersz.dzien, wiersz.godzina) == ("20.09", "18:00")


def test_remis_nie_ma_zwyciezcy_a_pozostale_mecze_maja_nazwe_rozgrywek() -> None:
    widok = _przygotuj(
        AktualnosciInMemoryRepository(mecze=(mecz(2, I_LIGA.id_rozgrywki, 19, (25, 25)),))
    )
    wiersz = widok.pozostale_mecze[0]
    assert wiersz.zwyciezca is None
    assert wiersz.rozgrywki == I_LIGA.nazwa


def test_ciekawostki_maja_poprawna_odmiane_i_linki() -> None:
    wystep = WystepAktualnosci(
        I_LIGA.id_rozgrywki, 3, datetime(2026, 9, 3), 77, "Jan  NOWAK ", "KS Start ", 22
    )
    widok = _przygotuj(
        AktualnosciInMemoryRepository(
            mecze=(
                mecz(3, I_LIGA.id_rozgrywki, 3, (12, 10)),
                mecz(4, SUPERLIGA_M.id_rozgrywki, 4, (1, 0)),
            ),
            wystepy=(wystep,),
        )
    )
    ciekawostki = {c.tytul: c for c in widok.ciekawostki}
    assert ciekawostki["Sezon w liczbach"].wartosc == "23 bramki"
    assert ciekawostki["Najwięcej bramek w meczu"].wartosc == "22 bramki"
    assert ciekawostki["Najwięcej bramek w meczu"].id_mecz == 3
    assert ciekawostki["Najwyższe zwycięstwo"].wartosc == "różnica 2 bramki"
    najlepszy = ciekawostki["Najlepszy występ indywidualny"]
    assert najlepszy.wartosc == "22 bramki w meczu"
    assert najlepszy.opis.startswith("Jan NOWAK (KS Start) · I Liga")
    assert najlepszy.id_zawodnik == 77 and najlepszy.id_mecz == 3
    assert ciekawostki["Najbardziej bramkostrzelna liga"].wartosc == "1,0 bramki na mecz"


def test_strzelec_ma_srednia_i_brak_druzyny_jako_kreske() -> None:
    widok = _przygotuj(
        AktualnosciInMemoryRepository(
            strzelcy=(
                StrzelecAktualnosci(SUPERLIGA_M.id_rozgrywki, 5, "Adam Wiśniewski", None, 4, 26),
            )
        )
    )
    strzelec = widok.sekcje[0].strzelcy[0]
    assert (strzelec.pozycja, strzelec.bramki, strzelec.srednia, strzelec.druzyna) == (
        1,
        26,
        "6,5",
        "—",
    )
