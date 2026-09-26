from datetime import datetime

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.match_predictions import (
    MeczeLigoweInMemoryRepository,
    mecz_ligowy,
    mecze_dwoch_sezonow,
)
from tests.helpers.schedule import (
    SezonyTerminarza,
    TerminarzInMemoryRepository,
    ZapowiedzMeczuInMemoryRepository,
    ZegarTestowy,
    mecz_zapowiedzi,
)

from handball.app_factory import AplikacjaFactory
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


def aplikacja() -> Flask:
    terminarz = TerminarzInMemoryRepository()
    zapowiedzi = ZapowiedzMeczuInMemoryRepository(
        [
            mecz_zapowiedzi(),
            mecz_zapowiedzi(
                201,
                wynik=(31, 26),
                data=datetime(2025, 9, 1, 18),
                gosp=(10, "Wisła Płock"),
                gosc=(30, "Górnik Zabrze"),
            ),
            mecz_zapowiedzi(999, gosp=(501, "Klub Spoza Ligi"), gosc=(502, "Inny Klub"), data=None),
        ]
    )
    ligowe = MeczeLigoweInMemoryRepository(
        [*mecze_dwoch_sezonow(), mecz_ligowy(204, datetime(2025, 9, 22, 18), 30, 10, None, None)]
    )
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_sezonow=lambda: SezonyTerminarza(),
        fabryka_terminarza=lambda: terminarz,
        fabryka_zapowiedzi_meczu=lambda: zapowiedzi,
        fabryka_meczow_ligowych=lambda: ligowe,
        zegar=ZegarTestowy(),
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_sidebar_ma_terminarz_pod_meczami() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz").get_data(as_text=True)
    mecze = tresc.index('href="/administracja/mecze"><span>◈</span><span>Mecze</span>')
    terminarz = tresc.index('<a class="active" href="/administracja/terminarz">')
    assert mecze < terminarz
    assert '<a href="/administracja/mecze" class="active">Dane</a>' in tresc


def test_bez_rozgrywek_terminarz_prosi_o_wybor() -> None:
    odpowiedz = aplikacja().test_client().get("/administracja/terminarz")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "data-schedule-prompt" in tresc
    assert '<option value="5" selected>2025/2026</option>' in tresc
    assert '<option value="501">ORLEN Superliga</option>' in tresc
    assert "js/schedule.js" in tresc


def test_terminarz_grupuje_i_pokazuje_wyniki() -> None:
    tresc = (
        aplikacja()
        .test_client()
        .get("/administracja/terminarz?id_sezon=5&id_rozgrywki=501")
        .get_data(as_text=True)
    )
    naglowki = [
        tresc.index(n)
        for n in (
            '<h2 class="schedule-round">I runda</h2>',
            'data-tips-link title="Typowania meczów kolejki">Seria 1</a></h3>',
            'data-tips-link title="Typowania meczów kolejki">Seria 2</a></h3>',
            '<h2 class="schedule-round">II runda</h2>',
        )
    ]
    assert naglowki == sorted(naglowki)
    assert ">Seria 3</a></h3>" in tresc
    assert '<h4 class="schedule-day">pon. 01.09.2025</h4>' in tresc
    assert "<table" not in tresc
    assert "pon. 01.09.2025" in tresc and "wt. 02.09.2025" in tresc
    assert "31 : 26" in tresc
    assert 'title="Zagłębie Lubin">Zagłębie Lubin</span>' in tresc and "24 : 35" in tresc
    assert "– : –" in tresc and "Zaplanowany" in tresc and "Zakończony" in tresc
    assert "prop.</small>" in tresc
    assert "zakończone 3/3" in tresc
    assert 'href="/administracja/terminarz/204?id_sezon=5&amp;id_rozgrywki=501"' in tresc
    assert "Meczów w terminarzu: <b>5</b>" in tresc


def test_filtr_kolejki_i_puste_rozgrywki() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get(
        "/administracja/terminarz?id_sezon=5&id_rozgrywki=501&id_runda=11&id_kolejka=112"
    ).get_data(as_text=True)
    assert "Seria 2</a></h3>" in tresc and "Seria 1</a></h3>" not in tresc
    tresc = klient.get("/administracja/terminarz?id_sezon=5&id_rozgrywki=502").get_data(
        as_text=True
    )
    assert "data-schedule-empty" in tresc


def test_bledne_parametry_terminarza() -> None:
    klient = aplikacja().test_client()
    assert klient.get("/administracja/terminarz?id_sezon=abc").status_code == 400
    assert klient.get("/administracja/terminarz?id_sezon=77").status_code == 400
    assert klient.post("/administracja/terminarz").status_code == 405


def test_zapowiedz_nierozegranego_meczu_ma_prognoze_na_teraz() -> None:
    odpowiedz = aplikacja().test_client().get("/administracja/terminarz/204?id_sezon=5")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "Zapowiedź meczu" in tresc
    assert 'data-preview-forecast="biezaca"' in tresc
    assert "Prognoza na teraz" in tresc and "po 6 rozegranych meczach" in tresc
    assert "Krok 1 — różnica ratingów" in tresc and "Krok 6" not in tresc
    for sekcja in ("Porównanie drużyn", "Forma — ostatnie mecze", "Mecze bezpośrednie"):
        assert sekcja in tresc
    assert "Jan Kowalski" in tresc
    assert 'href="/administracja/terminarz?id_sezon=5"' in tresc
    assert 'href="/administracja/druzyny/30"' in tresc


def test_zapowiedz_zakonczonego_meczu_ma_prognoze_jak_w_raporcie() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz/201").get_data(as_text=True)
    assert 'data-preview-forecast="po_meczu"' in tresc
    assert "31 : 26" in tresc and "Rzeczywisty wynik" in tresc and "score_error" in tresc
    assert "/administracja/raporty/prognozy-meczow/201" in tresc


def test_zapowiedz_meczu_spoza_modelu_i_brak_meczu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/terminarz/999").get_data(as_text=True)
    assert 'data-preview-forecast="brak"' in tresc and "Prognoza niedostępna" in tresc
    assert klient.get("/administracja/terminarz/12345").status_code == 404
    assert klient.get("/administracja/terminarz/204?model=xyz").status_code == 400


def test_kolejka_otwiera_okno_typowan() -> None:
    tresc = (
        aplikacja()
        .test_client()
        .get("/administracja/terminarz?id_sezon=5&id_rozgrywki=501")
        .get_data(as_text=True)
    )
    assert (
        'href="/administracja/terminarz/typowania?id_sezon=5&amp;id_rozgrywki=501&amp;id_kolejka=112"'
        in tresc
    )
    assert "data-tips-dialog" in tresc and "data-tips-content" in tresc


def test_typowania_kolejki_nierozegranej_pokazuja_tylko_prognoze() -> None:
    odpowiedz = (
        aplikacja()
        .test_client()
        .get("/administracja/terminarz/typowania?id_sezon=5&id_rozgrywki=501&id_kolejka=112")
    )
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "data-schedule-tips" in tresc
    assert '<h3 id="tips-match-204">Górnik Zabrze — Wisła Płock</h3>' in tresc
    etykiety = [
        "Prognoza wyniku",
        "Typ modelu",
        "Typ prognozy",
        "Przewidywana różnica",
        "Przewidywana suma",
        "Δ rating (z HOME_ADVANTAGE)",
    ]
    pozycje = [tresc.index(f"<dt>{etykieta}</dt>") for etykieta in etykiety]
    assert pozycje == sorted(pozycje)
    assert tresc.count("<dt>") == 6
    assert "Rzeczywisty wynik" not in tresc and "score_error" not in tresc


def test_typowania_kolejki_zakonczonej_i_spoza_modelu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get(
        "/administracja/terminarz/typowania?id_sezon=5&id_rozgrywki=501&id_kolejka=111"
    ).get_data(as_text=True)
    assert tresc.count("<article") == 3 and tresc.count("<dt>") == 18
    assert "Wisła Płock — Górnik Zabrze" in tresc
    tresc = klient.get(
        "/administracja/terminarz/typowania?id_sezon=5&id_rozgrywki=501&id_kolejka=121"
    ).get_data(as_text=True)
    assert "Prognoza niedostępna" in tresc and "<dt>" not in tresc


def test_typowania_kolejki_bledne_parametry() -> None:
    klient = aplikacja().test_client()
    assert klient.get("/administracja/terminarz/typowania?id_sezon=5").status_code == 400
    assert (
        klient.get(
            "/administracja/terminarz/typowania?id_sezon=5&id_rozgrywki=501&id_kolejka=112&model=x"
        ).status_code
        == 400
    )


def test_zapowiedz_ma_sekcje_w_nowej_kolejnosci() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz/204").get_data(as_text=True)
    kolejnosc = [
        tresc.index(f'<section class="panel" id="{sekcja}"')
        for sekcja in ("kadra", "forma", "porownanie", "bezposrednie", "prognoza")
    ]
    assert kolejnosc == sorted(kolejnosc)
    spis = [
        tresc.index(f'<li><a href="#{sekcja}">')
        for sekcja in ("kadra", "forma", "porownanie", "bezposrednie", "prognoza")
    ]
    assert spis == sorted(spis)
    assert "Najlepsi strzelcy" not in tresc
    assert "js/match_preview.js" in tresc


def test_kadra_w_sezonie_od_bramkarzy_z_numerami() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz/204").get_data(as_text=True)
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert "Kadra w sezonie 2025/2026" in kadra
    grupy = [kadra.index(f">{nazwa}</th>") for nazwa in ("Bramkarze", "Rozgrywający", "Skrzydłowi")]
    assert grupy == sorted(grupy)
    assert '<td class="num">1/12</td>' in kadra and "Adam Nowak" in kadra
    assert "Pozycja nieznana" in kadra
    assert "(4 zawodników)" in kadra
    assert "w sezonie 2024/2025 zagrali w tej drużynie co najmniej 1 mecz" in kadra
    assert "Olaf Stary" not in kadra


def test_kadra_z_poprzednim_sezonem() -> None:
    tresc = (
        aplikacja()
        .test_client()
        .get("/administracja/terminarz/204?kadra_poprzedni=y&id_sezon=5")
        .get_data(as_text=True)
    )
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert "Olaf Stary" in kadra and "(5 zawodników)" in kadra
    assert "Karol Rezerwa" not in kadra
    assert (
        'name="kadra_poprzedni" value="y" form="preview-options" data-preview-auto checked' in kadra
    )
    assert '<input type="hidden" name="id_sezon" value="5">' in tresc


def test_mecze_bezposrednie_z_wybranego_okresu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/terminarz/204").get_data(as_text=True)
    sekcja = tresc[tresc.index('id="bezposrednie"') : tresc.index('id="prognoza"')]
    assert '<option value="10" selected>10 lat</option>' in sekcja
    assert "ostatnie 10 lat (od 22.09.2015)" in sekcja
    tresc = klient.get("/administracja/terminarz/204?lata=wszystkie").get_data(as_text=True)
    assert "wszystkie spotkania w bazie" in tresc
    assert klient.get("/administracja/terminarz/204?lata=7").status_code == 400


def test_kadra_zaznacza_najlepszych_strzelcow_i_srednia() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz/204").get_data(as_text=True)
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert 'title="1. strzelec drużyny w sezonie 2025/2026">★ 1</span>' in kadra
    assert "★ 2</span>" in kadra
    assert kadra.count('class="preview-scorer-row"') == 2
    assert '<td class="num top-scorer" aria-label="13 — 1. strzelec drużyny">13</td>' in kadra
    assert '<td class="num">6.50</td>' in kadra
    assert "pięciu najlepszych strzelców" in kadra


def test_kadra_poprzedni_sezon_bramki_srednia_klub_i_liga() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz/204").get_data(as_text=True)
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert "2024/2025<br><small>br. / śr.</small>" in kadra
    assert '20 / 6.67 <small class="muted">(3 mecze)</small></td>' in kadra
    assert (
        '<small class="preview-prev-note">inny klub: Industria Kielce — 1 bramka, 4 mecze</small>'
        in kadra
    )
    assert (
        '<small class="preview-prev-note">inny klub: KPR Legionowo — 36 bramek, 6 meczów</small>'
        in kadra
    )
    assert '<small class="preview-prev-note">inna liga: I Liga Mężczyzn Grupa A</small>' in kadra
    assert "inna liga: Puchar Polski" not in kadra
    assert "36 / 6.00" in kadra


def test_dodany_zawodnik_ma_poprzedni_sezon_tylko_dla_tej_druzyny() -> None:
    tresc = (
        aplikacja()
        .test_client()
        .get("/administracja/terminarz/204?kadra_poprzedni=y")
        .get_data(as_text=True)
    )
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    wiersz = kadra[kadra.index("Olaf Stary") : kadra.index("</tr>", kadra.index("Olaf Stary"))]
    assert '6 / 1.50 <small class="muted">(4 mecze w tej drużynie)</small>' in wiersz
    assert "inny klub: Górnik Zabrze — 5 bramek, 2 mecze" in wiersz


def test_kadra_ma_date_urodzenia_i_druk_skladow() -> None:
    tresc = aplikacja().test_client().get("/administracja/terminarz/204").get_data(as_text=True)
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert (
        'Jan Kowalski</a> <small class="preview-birth" title="Data urodzenia">(02.01.1998)</small>'
        in kadra
    )
    assert 'Adam Nowak</a> <small class="preview-birth"' not in kadra
    assert 'data-print-section="#kadra-druk"' in kadra and 'id="kadra-druk"' in kadra
    assert 'data-print-styles="/statyczne/css/admin.css"' in kadra
    assert "Drukuj składy</button>" in kadra
    assert "js/print_table.js" in tresc


def test_kadra_checkbox_ukrywa_uwagi_o_klubie_i_lidze() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/terminarz/204").get_data(as_text=True)
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert "Ukryj informacje o innym klubie i innej lidze" in kadra
    assert 'data-preview-notes-toggle="#kadra-druk">' in kadra
    assert '<div class="preview-grid" id="kadra-druk">' in kadra
    tresc = klient.get("/administracja/terminarz/204?bez_uwag=y").get_data(as_text=True)
    kadra = tresc[tresc.index('id="kadra"') : tresc.index('id="forma"')]
    assert 'data-preview-notes-toggle="#kadra-druk" checked>' in kadra
    assert '<div class="preview-grid preview-hide-notes" id="kadra-druk">' in kadra
