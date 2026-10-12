from dataclasses import replace

from tests.interface.test_matches import (
    SZCZEGOLY_TESTOWE,
    _aplikacja_z_repozytorium,
)

from handball.domain.matches import ZawodnikMeczu
from handball.request_dependencies import ZaleznosciZadaniaFactory


def zawodnik(pozycja: str, bramki: str, numer: str = "1") -> ZawodnikMeczu:
    return ZawodnikMeczu(
        nr_koszulki=int(numer),
        zawodnik="Zawodnik",
        pozycja=pozycja if pozycja != "—" else None,
        bramki=int(bramki) if bramki != "—" else None,
    )


def test_sklady_grupowane_po_pozycji_i_numerze_z_brakami_na_koncu() -> None:
    sklad = [
        zawodnik("—", "—"),
        zawodnik("RO", "2", "10"),
        zawodnik("BR", "0"),
        zawodnik("RO", "3", "2"),
    ]
    szczegoly = replace(SZCZEGOLY_TESTOWE, sklad_gospodarz=sklad)
    wynik = ZaleznosciZadaniaFactory().utworz_presenter_meczow().przygotuj_szczegoly(szczegoly)
    assert [(z.pozycja, z.nr_koszulki) for z in wynik.sklad_gospodarz] == [
        ("BR", "1"),
        ("RO", "2"),
        ("RO", "10"),
        ("—", "1"),
    ]
    assert szczegoly.sklad_gospodarz == sklad
    assert wynik.sklad_gospodarz[-1].kolor_pozycji is None


def test_liderzy_obu_druzyn_ex_aequo_bez_doliczania_serii_karnych() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        sklad_gospodarz=[zawodnik("RO", "10"), zawodnik("BR", "2")],
        sklad_gosc=[
            zawodnik("RO", "10"),
            replace(zawodnik("BR", "9"), karne_bramki_seria=5, karne_liczba_seria=5),
        ],
        sklad_inne=[zawodnik("RO", "99")],
    )
    wynik = ZaleznosciZadaniaFactory().utworz_presenter_meczow().przygotuj_szczegoly(szczegoly)
    liderzy = [z for z in wynik.sklad_gospodarz + wynik.sklad_gosc if z.najlepszy_strzelec]
    assert len(liderzy) == 2
    assert all(z.bramki == "10" for z in liderzy)
    assert liderzy[0].kolor_pozycji == liderzy[1].kolor_pozycji
    assert not wynik.sklad_inne[0].najlepszy_strzelec


def test_zero_i_braki_nie_sa_wyrozniane() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        sklad_gospodarz=[zawodnik("BR", "0"), zawodnik("RO", "—")],
    )
    wynik = ZaleznosciZadaniaFactory().utworz_presenter_meczow().przygotuj_szczegoly(szczegoly)
    assert not any(z.najlepszy_strzelec for z in wynik.sklad_gospodarz)


def test_widok_renderuje_kolory_lidera_i_fragment_modalu() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        sklad_gospodarz=[zawodnik("RO", "12")],
        sklad_gosc=[zawodnik("BR", "2")],
    )
    klient = _aplikacja_z_repozytorium([], {12543: szczegoly}).test_client()
    odpowiedz = klient.get("/administracja/mecze/12543")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "data-match-detail" in tresc
    assert tresc.count('class="top-scorer"') == 2
    assert "--position-hue:" in tresc
    lista = klient.get("/administracja/mecze").get_data(as_text=True)
    assert 'id="match-detail-dialog"' in lista


def test_liderzy_wyznaczani_osobno_dla_druzyn_z_remisem() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        sklad_gospodarz=[zawodnik("RO", "12"), zawodnik("BR", "1")],
        sklad_gosc=[zawodnik("RO", "5"), zawodnik("SK", "5"), zawodnik("BR", "2")],
    )
    wynik = ZaleznosciZadaniaFactory().utworz_presenter_meczow().przygotuj_szczegoly(szczegoly)
    assert [z.bramki for z in wynik.sklad_gospodarz if z.najlepszy_strzelec] == ["12"]
    assert [z.bramki for z in wynik.sklad_gosc if z.najlepszy_strzelec] == ["5", "5"]


def test_zakladki_i_legenda_ponizej_tabel() -> None:
    klient = _aplikacja_z_repozytorium([], {12543: SZCZEGOLY_TESTOWE}).test_client()
    tresc = klient.get("/administracja/mecze/12543").get_data(as_text=True)
    assert tresc.count('role="tab"') == 4
    assert 'id="match-panel-rosters"' in tresc
    assert tresc.index('class="roster-legend"') > tresc.rindex("</table>")
    assert "najlepszy strzelec danej drużyny" in tresc
    assert "js/matches.js" in tresc


def test_zawodnik_w_skladzie_otwiera_okno_i_karte() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        sklad_gospodarz=[replace(zawodnik("RO", "5"), id_zawodnik=77, zawodnik="Jan Test")],
        sklad_gosc=[zawodnik("BR", "1")],
    )
    klient = _aplikacja_z_repozytorium([], {12543: szczegoly}).test_client()
    tresc = klient.get("/administracja/mecze/12543").get_data(as_text=True)
    assert 'href="/administracja/zawodnicy/77"' in tresc
    assert "data-player-modal-link" in tresc and ">Jan Test</a>" in tresc
    assert tresc.count("data-player-modal-link ") == 1
    korzen = tresc.split("data-match-detail>")[1]
    assert "data-player-modal-dialog" in korzen and "data-player-content" in korzen
    assert tresc.index("js/player_details.js") < tresc.index("js/matches.js")
    lista = klient.get("/administracja/mecze").get_data(as_text=True)
    assert "js/goal_charts.js" in lista and "js/player_details.js" in lista


def test_druzyny_w_naglowku_otwieraja_okno_i_karte_z_uwzglednieniem_zamiany() -> None:
    szczegoly = replace(
        SZCZEGOLY_TESTOWE,
        mecz=replace(SZCZEGOLY_TESTOWE.mecz, id_zespol_gosp=11, id_zespol_gosc=22, zamiana=True),
    )
    klient = _aplikacja_z_repozytorium([], {12543: szczegoly}).test_client()
    tresc = klient.get("/administracja/mecze/12543").get_data(as_text=True)
    gospodarz = tresc.split('class="team-box home"')[1].split('class="result-box"')[0]
    gosc = tresc.split('class="team-box right away"')[1].split('class="hero-meta"')[0]
    assert 'href="/administracja/druzyny/22"' in gospodarz and ">Orlen Wisła Płock</a>" in gospodarz
    assert 'href="/administracja/druzyny/11"' in gosc and ">Industria Kielce</a>" in gosc
    assert tresc.count("data-team-modal-link ") == 2
    korzen = tresc.split("data-match-detail>")[1]
    assert "data-team-modal-dialog" in korzen and "data-team-content" in korzen
    assert tresc.index("js/team_details.js") < tresc.index("js/classification_details.js")
    assert tresc.index("js/classification_details.js") < tresc.index("js/matches.js")
    lista = klient.get("/administracja/mecze").get_data(as_text=True)
    assert "js/team_details.js" in lista and "js/classification_details.js" in lista


def test_druzyna_bez_identyfikatora_nie_jest_linkiem() -> None:
    klient = _aplikacja_z_repozytorium([], {12543: SZCZEGOLY_TESTOWE}).test_client()
    tresc = klient.get("/administracja/mecze/12543").get_data(as_text=True)
    assert "data-team-modal-link " not in tresc
    assert '<div class="team-name">Industria Kielce</div>' in tresc
