import re
from html import unescape

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.core_catalog_repository import KatalogPodstawowyInMemoryRepository
from tests.helpers.team_details import SzczegolyDruzynyInMemoryRepository
from tests.interface.test_core_catalogs import aplikacja_z_katalogiem

from handball.app_factory import AplikacjaFactory
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


def aplikacja(repo: SzczegolyDruzynyInMemoryRepository) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(fabryka_szczegolow_druzyny=lambda: repo)
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def pobierz(adres: str, repo: SzczegolyDruzynyInMemoryRepository | None = None) -> tuple[int, str]:
    odpowiedz = aplikacja(repo or SzczegolyDruzynyInMemoryRepository()).test_client().get(adres)
    return odpowiedz.status_code, odpowiedz.get_data(as_text=True)


def test_karta_ma_siedem_zakladek_i_dane_podstawowe() -> None:
    status, tresc = pobierz("/administracja/druzyny/272")
    assert status == 200
    assert tresc.count('role="tab"') == 7
    assert 'data-active-tab="dane"' in tresc
    for etykieta in (
        "Dane podstawowe",
        "Sezony",
        "Mecze",
        "Zawodnicy",
        "Zestawienie sezonu",
        "Podsumowanie",
        "Forma i regularność",
    ):
        assert f">{etykieta}</button>" in tresc
    assert "Stara Wisła" in tresc and "2024/2025" in tresc
    assert "Mężczyźni" in tresc
    assert "/administracja/sklady/12" in tresc
    assert "/administracja/hale/43" in tresc
    assert "js/goal_charts.js" in tresc and "js/team_details.js" in tresc


def test_nieistniejaca_druzyna_zwraca_404_a_zle_sortowanie_400() -> None:
    assert pobierz("/administracja/druzyny/1")[0] == 404
    assert pobierz("/administracja/druzyny/272?sortowanie_zawodnikow=xx")[0] == 400


def test_sezony_pokazuja_bilans_i_rozstrzygniecie_karnych() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=sezony")
    assert "karne: W 1 / P 0" in tresc
    assert "bez wyniku: 1" in tresc
    assert "Wszystkie rozgrywki (2)" in tresc


def test_mecze_z_perspektywy_druzyny_i_escapowanie() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=mecze")
    assert 'data-active-tab="mecze"' in tresc
    assert "31:27" in tresc
    assert "Zwycięstwo" in tresc and "Remis" in tresc and "Bez wyniku" in tresc
    assert "wygrana po karnych" in tresc
    assert "Rywal &lt;b&gt;" in tresc and "Rywal <b>" not in tresc


def test_zawodnicy_maja_osobna_paginacje_i_sortowanie() -> None:
    repo = SzczegolyDruzynyInMemoryRepository()
    _, tresc = pobierz(
        "/administracja/druzyny/272?strona_zawodnikow=2&sortowanie_zawodnikow=-srednia", repo
    )
    assert 'data-active-tab="zawodnicy"' in tresc
    assert repo.filtry_zawodnikow is not None
    assert repo.filtry_zawodnikow.strona == 2
    assert repo.filtry_zawodnikow.sortowanie == "-srednia"
    assert repo.filtry_meczow is not None and repo.filtry_meczow.strona == 1
    tresc = unescape(tresc)
    assert "strona_zawodnikow=1" in tresc
    assert "/administracja/zawodnicy/7" in tresc
    assert "4.50" in tresc


def test_podsumowanie_pokazuje_razem_bramki_zdobyte_i_stracone() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=podsumowanie")
    podsumowanie = tresc.split('id="team-panel-podsumowanie"')[1].split('id="team-panel-forma"')[0]
    for atrybut in (
        "data-team-results",
        "data-team-season-means",
        "data-team-means-toggle",
        "data-team-season-sums",
        "data-team-distribution",
        'data-team-place-toggle="distribution"',
        "data-team-seasons-data",
    ):
        assert atrybut in podsumowanie
    assert "Najwięcej straconych bramek" in podsumowanie
    assert "Miary bramek na mecz w rozegranych meczach" in podsumowanie
    assert re.search(
        r">Średnia na mecz</th><td[^>]*>29\.7</td><td[^>]*>26\.7</td><td[^>]*>3\.0<", podsumowanie
    )
    assert re.search(r">Mediana u siebie</th><td[^>]*>30\.5</td><td[^>]*>26\.0</td>", podsumowanie)
    assert "Mecze z tyloma straconymi" in podsumowanie
    assert "data-team-series" not in tresc and 'name="seria"' not in tresc
    assert 'aria-label="Liczba zwycięstw, remisów i porażek drużyny' in podsumowanie


def test_forma_laczy_zdobyte_stracone_i_roznice() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=forma")
    forma = tresc.split('id="team-panel-forma"')[1]
    for atrybut in (
        "data-team-matches",
        "data-team-balance",
        "data-team-rolling",
        "data-team-boxplot",
        "data-team-matches-data",
        "data-team-spread-data",
        'data-team-place-toggle="rolling"',
    ):
        assert atrybut in forma
    assert forma.count("<caption>") == 3
    assert re.search(r">Mediana</th><td[^>]*>30\.0</td><td[^>]*>27\.0</td><td[^>]*>4\.0<", forma)
    assert re.search(
        r">Współczynnik zmienności</th><td[^>]*>[^<]+</td><td[^>]*>[^<]+</td><td[^>]*>—<", forma
    )
    assert "Udział 6+ bramek" not in forma
    assert "Dane mecz po meczu i formy kroczącej: u siebie (2)" in forma
    assert "+5" in forma and "Rywal &lt;b&gt;" in forma


def test_filtr_rozgrywek_przelacza_na_mecze_i_zaweza_analize() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?rozgrywki=Puchar")
    assert 'data-active-tab="mecze"' in tresc
    assert (
        "Remis" not in tresc.split('id="team-panel-zawodnicy"')[0].split('id="team-panel-mecze"')[1]
    )


def test_lista_druzyn_linkuje_do_karty() -> None:
    tresc = (
        aplikacja_z_katalogiem(KatalogPodstawowyInMemoryRepository())
        .test_client()
        .get("/administracja/druzyny")
        .get_data(as_text=True)
    )
    assert re.search(r'href="/administracja/druzyny/\d+"[^>]*>▣ Szczegóły</a>', tresc)


def test_frekwencja_w_danych_podstawowych_sezonach_i_meczach() -> None:
    _, tresc = pobierz("/administracja/druzyny/272")
    dane = tresc.split('id="team-panel-dane"')[1].split('id="team-panel-sezony"')[0]
    assert "Frekwencja w całej historii" in dane
    assert re.search(r"Średnio widzów u siebie</span><b>1\u00a0000</b>", dane)
    assert re.search(
        r"Rekord u siebie</span><b><a href=\"/administracja/mecze/1\"[^>]*>2\u00a0000</a>", dane
    )
    assert "Mecze u siebie z frekwencją</span><b>2/2</b>" in dane
    assert "Średnio widzów na wyjeździe</span><b>5\u00a0100</b>" in dane
    assert ">1\u00a0850</td>" in dane
    sezony = tresc.split('id="team-panel-sezony"')[1].split('id="team-panel-mecze"')[0]
    assert (
        "Widzowie dom śr.</th>" in sezony
        and "Średnia liczba widzów w meczach u siebie" in sezony
        and ">5\u00a0100</td>" in sezony
    )
    mecze = tresc.split('id="team-panel-mecze"')[1].split('id="team-panel-zawodnicy"')[0]
    assert "Frekwencja w wybranym zakresie" in mecze
    assert '<td class="team-num">900</td>' in mecze and '<td class="team-num">0</td>' in mecze


def test_frekwencja_meczow_zalezy_od_filtrow() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=mecze&rozgrywki=Puchar")
    mecze = tresc.split('id="team-panel-mecze"')[1].split('id="team-panel-zawodnicy"')[0]
    assert "Średnio widzów u siebie</span><b>0</b>" in mecze
    assert "Mecze wyjazdowe z frekwencją</span><b>0/0</b>" in mecze


def test_mecze_maja_domyslnie_zaznaczone_tylko_zakonczone() -> None:
    repo = SzczegolyDruzynyInMemoryRepository()
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=mecze", repo)
    mecze = tresc.split('id="team-panel-mecze"')[1].split('id="team-panel-zawodnicy"')[0]
    assert 'name="zakonczone" value="1" checked' in mecze
    assert '<input type="hidden" name="zakonczone" value="0">' in mecze
    assert repo.filtry_meczow is not None and repo.filtry_meczow.tylko_zakonczone is True


def test_odznaczone_tylko_zakonczone_trafia_do_repozytorium_i_linkow() -> None:
    repo = SzczegolyDruzynyInMemoryRepository()
    _, tresc = pobierz("/administracja/druzyny/272?zakonczone=0", repo)
    assert 'data-active-tab="mecze"' in tresc
    assert repo.filtry_meczow is not None and repo.filtry_meczow.tylko_zakonczone is False
    mecze = tresc.split('id="team-panel-mecze"')[1].split('id="team-panel-zawodnicy"')[0]
    assert 'name="zakonczone" value="1" checked' not in mecze
    assert "zakonczone=0" in unescape(mecze)


def test_zestawienie_sezonu_ma_mecze_w_kolumnach_i_zawodnikow_w_wierszach() -> None:
    repo = SzczegolyDruzynyInMemoryRepository()
    status, tresc = pobierz("/administracja/druzyny/272?zakladka=zestawienie", repo)
    assert status == 200
    assert repo.filtry_zestawienia is not None and repo.filtry_zestawienia.id_sezon == 195
    panel = tresc.split('id="team-panel-zestawienie"')[1].split('id="team-panel-podsumowanie"')[0]
    assert "Zestawienie sezonu 2026/2027" in panel
    assert 'name="sezon_zestawienia" required' in panel
    assert (
        '<option value="">' not in panel.split('name="sezon_zestawienia"')[1].split("</select>")[0]
    )
    assert panel.count('class="team-sheet-match"') == 3
    assert 'href="/administracja/mecze/3"' in panel and "31:27" in panel
    bramkarz, wiersz = panel.split("<tbody>")[1].split("</tbody>")[0].split("<tr>")[1:]
    assert "Bramkarz &lt;b&gt;" in bramkarz and "Jan Testowy" in wiersz
    wiersze = [wiersz, bramkarz]
    assert (
        "data-player-modal-link" in wiersze[0] and 'href="/administracja/zawodnicy/7"' in wiersze[0]
    )
    assert '<td class="team-sheet-pos">Rozgrywający, Skrzydłowy</td>' in wiersze[0]
    assert (
        '<b>6</b><span class="team-sheet-pen">1×2′</span><span class="team-sheet-7m">2/3</span>'
        in wiersze[0]
    )
    assert '<span class="team-sheet-pen">U</span>' in wiersze[0]
    podsumowanie = wiersze[0].split('<td class="team-sheet-sum team-sheet-sum-first">')[1]
    assert podsumowanie.startswith('3</td><td class="team-sheet-sum"><b>15</b></td>')
    assert '<td class="team-sheet-sum team-sheet-pen-sum">1×2′ U</td>' in podsumowanie
    assert '<td class="team-sheet-sum">3/4</td>' in podsumowanie
    assert wiersze[1].count("team-sheet-empty") == 2 and "<b>—</b>" in wiersze[1]
    assert "Suma drużyny" in panel
    assert "data-player-modal-dialog" in tresc and tresc.index(
        "js/player_details.js"
    ) < tresc.index("js/team_details.js")


def test_zestawienie_przyjmuje_sezon_i_rozgrywki_oraz_otwiera_zakladke() -> None:
    repo = SzczegolyDruzynyInMemoryRepository()
    _, tresc = pobierz(
        "/administracja/druzyny/272?sezon_zestawienia=194&rozgrywki_zestawienia=Puchar", repo
    )
    assert 'data-active-tab="zestawienie"' in tresc
    assert repo.filtry_zestawienia is not None
    assert (repo.filtry_zestawienia.id_sezon, repo.filtry_zestawienia.rozgrywki) == (194, "Puchar")
    panel = tresc.split('id="team-panel-zestawienie"')[1].split('id="team-panel-podsumowanie"')[0]
    assert panel.count('class="team-sheet-match"') == 1
    assert pobierz("/administracja/druzyny/272?sezon_zestawienia=999")[0] == 400


def test_linki_zawodnikow_w_zakladce_zawodnicy_otwieraja_okno() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=zawodnicy")
    zawodnicy = tresc.split('id="team-panel-zawodnicy"')[1].split('id="team-panel-zestawienie"')[0]
    assert (
        'href="/administracja/zawodnicy/7" target="_blank" rel="noopener" data-player-modal-link'
        in zawodnicy
    )


def test_zestawienie_ma_naglowek_podsumowania_i_brak_przewijania_pionowego() -> None:
    _, tresc = pobierz("/administracja/druzyny/272?zakladka=zestawienie")
    panel = tresc.split('id="team-panel-zestawienie"')[1].split('id="team-panel-podsumowanie"')[0]
    grupa = 'colspan="4" class="team-sheet-sum team-sheet-sum-first team-sheet-sum-group">'
    assert grupa + "Podsumowanie sezonu" in panel
    for etykieta in (">Mecze</th>", ">Bramki</th>", ">Kary</th>", "wyk./wsz."):
        assert etykieta in panel
