from datetime import datetime

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.match_predictions import MeczeLigoweInMemoryRepository, mecz_ligowy

from handball.app_factory import AplikacjaFactory
from handball.domain.errors import BladOdczytuDanych
from handball.domain.match_predictions import MeczLigowy, WzorceNazwLig
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class NiedostepneMeczeLigoweRepository:
    def pobierz_mecze(self, wzorce: WzorceNazwLig) -> list[MeczLigowy]:
        raise BladOdczytuDanych("brak bazy")


def aplikacja(repo: object | None = None) -> Flask:
    repozytorium = repo or MeczeLigoweInMemoryRepository()
    zaleznosci = ZaleznosciZadaniaFactory(fabryka_meczow_ligowych=lambda: repozytorium)
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_katalog_raportow_i_nawigacja() -> None:
    tresc = aplikacja().test_client().get("/administracja/raporty").get_data(as_text=True)
    assert "Katalog raportów" in tresc
    assert "Prognozy meczów — siła drużyn" in tresc
    assert 'href="/administracja/raporty/prognozy-meczow"' in tresc
    assert '<a href="/administracja/raporty" class="active">Raporty</a>' in tresc


def test_raport_renderuje_tabele_podsumowanie_i_klikalne_wiersze() -> None:
    odpowiedz = aplikacja().test_client().get("/administracja/raporty/prognozy-meczow")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Prognozy meczów — siła drużyn" in tresc
    assert "Dynamic Team Strength V1" in tresc and "team_strength_v1" in tresc
    for kolumna in ("Rating H", "Δ rating", "Prog. różn.", "Score error", "Wynik 1X2", "Ocena"):
        assert kolumna in tresc
    for wskaznik in ("Liczba prognoz", "Trafność 1X2", "MAE sumy", "Mediana score_error"):
        assert wskaznik in tresc
    assert "score_error ≤ 2" in tresc and "score_error ≤ 6" in tresc
    assert 'data-href="/administracja/raporty/prognozy-meczow/203' in tresc
    assert "Industria Kielce" in tresc
    assert "Zakres raportu: <b>2025/2026</b>" in tresc
    assert "Rozgrzewka: <b>2024/2025</b>" in tresc
    assert "HOME_ADVANTAGE" in tresc and "SEASON_RETENTION" in tresc
    assert '<a class="active" href="/administracja/raporty/prognozy-meczow">' in tresc
    assert "js/match_predictions.js" in tresc


def test_filtry_raportu_i_bledne_parametry() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get(
        "/administracja/raporty/prognozy-meczow?plec=M&poziom=superliga&sezon=5&druzyna=Górnik&trafnosc=trafione"
    ).get_data(as_text=True)
    assert "Brak prognoz" in tresc or "/administracja/raporty/prognozy-meczow/201" in tresc
    assert "/administracja/raporty/prognozy-meczow/203?" not in tresc
    assert klient.get("/administracja/raporty/prognozy-meczow?plec=X").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?ocena=zla").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?sezon=4").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?sezon=abc").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?model=xyz").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?rozmiar=7").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?strona=0").status_code == 400
    assert klient.post("/administracja/raporty/prognozy-meczow").status_code == 405


def test_szczegoly_prognozy_pokazuja_kroki_wzory_i_podstawienia() -> None:
    klient = aplikacja().test_client()
    odpowiedz = klient.get("/administracja/raporty/prognozy-meczow/202?plec=M")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Industria Kielce — Zagłębie Lubin" in tresc
    assert "zamiana = true" in tresc
    for sekcja in (
        "Wynik prognozy",
        "Dane wejściowe przed meczem",
        "Krok 1 — różnica ratingów",
        "Krok 2 — przewidywana różnica bramek",
        "Krok 3 — przewidywana suma bramek",
        "Krok 4 — przewidywane bramki",
        "Krok 5 — typ 1X2",
        "Krok 6 — rzeczywisty mecz",
        "Krok 7 — błędy prognozy",
        "Krok 8 — aktualizacja ratingów",
        "Co oznacza aktualizacja?",
        "Stan ratingów przed i po",
        "Historia ratingu",
        "Definicje modelu",
    ):
        assert sekcja in tresc
    assert "rating_diff =" in tresc and "+ HOME_ADVANTAGE" in tresc
    assert "tanh(margin_residual / MARGIN_SCALE)" in tresc
    assert "actual_margin = 35 − 24 = +11" in tresc
    assert "&#34;model_version&#34;: &#34;team_strength_v1&#34;" in tresc
    assert "&#34;season_retention&#34;: 0.7" in tresc
    assert "Model spodziewał się" in tresc
    assert 'href="/administracja/raporty/prognozy-meczow?plec=M"' in tresc
    assert 'href="/administracja/mecze/202"' in tresc
    assert "/administracja/raporty/prognozy-meczow/102?model=team_strength_v1" in tresc


def test_szczegoly_meczu_z_rozgrzewki_i_bledy() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/prognozy-meczow/101").get_data(as_text=True)
    assert "okresu rozgrzewki" in tresc
    assert "pierwszy mecz w danych modelu" in tresc
    assert "Brak wcześniejszych meczów ligi w modelu" in tresc
    assert klient.get("/administracja/raporty/prognozy-meczow/999").status_code == 404
    assert klient.get("/administracja/raporty/prognozy-meczow/101?model=xyz").status_code == 400


def test_niedostepna_baza_daje_503() -> None:
    klient = aplikacja(NiedostepneMeczeLigoweRepository()).test_client()
    assert klient.get("/administracja/raporty/prognozy-meczow").status_code == 503
    assert klient.get("/administracja/raporty/prognozy-meczow/101").status_code == 503


def test_kolumna_oceny_wyniku_i_checkboxy_filtrow() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/prognozy-meczow").get_data(as_text=True)
    assert "Ocena wyniku" in tresc and "Dokładna różnica bramek" in tresc
    assert 'type="checkbox" name="dokladny_wynik"' in tresc
    assert 'type="checkbox" name="poprawna_roznica"' in tresc
    assert 'name="ocena_wyniku" value="dokladna_roznica"' in tresc
    assert 'name="ocena" value="bardzo_trafna"' in tresc
    assert 'class="prediction-grade wynik-' in tresc
    filtrowane = klient.get(
        "/administracja/raporty/prognozy-meczow?poprawna_roznica=y&ocena_wyniku=dokladny_wynik"
        "&ocena_wyniku=dokladna_roznica&ocena=trafna&ocena=przecietna"
    )
    assert filtrowane.status_code == 200
    html = filtrowane.get_data(as_text=True)
    assert 'name="poprawna_roznica" value="y" checked' in html
    assert 'value="dokladna_roznica" checked' in html and 'value="przecietna" checked' in html
    assert klient.get("/administracja/raporty/prognozy-meczow?ocena_wyniku=xyz").status_code == 400


def test_linki_zachowuja_wielokrotne_wartosci_filtrow() -> None:
    klient = aplikacja().test_client()
    html = klient.get(
        "/administracja/raporty/prognozy-meczow?rozmiar=50&ocena=trafna&ocena=przecietna"
        "&ocena=slaba&ocena=bardzo_slaba&ocena=bardzo_trafna"
    ).get_data(as_text=True)
    assert "ocena=trafna&amp;ocena=przecietna" in html


def test_kolumna_kierunku_i_filtry_wyniku_1x2() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/prognozy-meczow").get_data(as_text=True)
    assert ">Typ prognozy</th>" in tresc and "Poprawny typ prognozy" in tresc
    assert ">Typ modelu</th>" in tresc and "Kierunek" not in tresc
    assert 'name="typ_prognozy" value="poprawny"' in tresc
    assert 'name="typ_prognozy" value="nieprzewidziany"' in tresc
    assert 'name="wynik_1x2" value="X"' in tresc
    assert "X — remis" in tresc and ">Trafiony<select" in tresc.replace("\n", "")
    html = klient.get(
        "/administracja/raporty/prognozy-meczow?wynik_1x2=X&typ_prognozy=nieprzewidziany&trafnosc=nietrafione"
    ).get_data(as_text=True)
    assert 'value="X" checked' in html and 'value="nieprzewidziany" checked' in html
    assert "/administracja/raporty/prognozy-meczow/202?" not in html
    assert klient.get("/administracja/raporty/prognozy-meczow?wynik_1x2=Z").status_code == 400
    assert klient.get("/administracja/raporty/prognozy-meczow?typ_prognozy=zly").status_code == 400
    obie = klient.get(
        "/administracja/raporty/prognozy-meczow?typ_prognozy=poprawny&typ_prognozy=nieprzewidziany"
    ).get_data(as_text=True)
    assert obie.count("data-href=") == 3
    szczegoly = klient.get("/administracja/raporty/prognozy-meczow/203").get_data(as_text=True)
    assert "Typ prognozy" in szczegoly and "typ prognozy: " in szczegoly
    assert "Typ modelu" in szczegoly


def test_wybor_liczby_sezonow_raportu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/prognozy-meczow").get_data(as_text=True)
    assert 'name="sezony_raportu"' in tresc
    assert '<option selected value="10">10</option>' in tresc
    assert '<option value="wszystkie">Wszystkie</option>' in tresc
    wszystkie = klient.get(
        "/administracja/raporty/prognozy-meczow?sezony_raportu=wszystkie"
    ).get_data(as_text=True)
    assert "Rozgrzewka: <b>2024/2025</b>" in wszystkie
    assert "sezony_raportu=wszystkie" in wszystkie
    assert klient.get("/administracja/raporty/prognozy-meczow?sezony_raportu=7").status_code == 400
    szczegoly = klient.get("/administracja/raporty/prognozy-meczow/203?sezony_raportu=3").get_data(
        as_text=True
    )
    assert "sezony_raportu=3" in szczegoly
    assert (
        klient.get("/administracja/raporty/prognozy-meczow/203?sezony_raportu=x").status_code == 400
    )


def test_filtry_poziomu_i_plci_oraz_skrot_ligi() -> None:
    mecze = [
        mecz_ligowy(1, datetime(2025, 9, 1), 10, 20, 30, 28),
        mecz_ligowy(
            2,
            datetime(2025, 9, 2),
            30,
            40,
            25,
            24,
            nazwa_rozgrywek="I Liga Kobiet Grupa B",
            plec="K",
        ),
    ]
    klient = aplikacja(MeczeLigoweInMemoryRepository(mecze)).test_client()
    tresc = klient.get("/administracja/raporty/prognozy-meczow").get_data(as_text=True)
    assert 'name="poziom"' in tresc and 'name="plec"' in tresc
    assert '<option value="liga_centralna">Liga Centralna</option>' in tresc
    assert "<td>SL M</td>" in tresc and "<td>1L K</td>" in tresc
    tylko_i_liga = klient.get("/administracja/raporty/prognozy-meczow?poziom=i_liga").get_data(
        as_text=True
    )
    assert "<td>1L K</td>" in tylko_i_liga and "<td>SL M</td>" not in tylko_i_liga
    szczegoly = klient.get("/administracja/raporty/prognozy-meczow/2").get_data(as_text=True)
    assert "I Liga kobiet" in szczegoly
    assert klient.get("/administracja/raporty/prognozy-meczow?poziom=ii_liga").status_code == 400
