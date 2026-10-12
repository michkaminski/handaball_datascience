from __future__ import annotations

from dataclasses import replace
from datetime import datetime

import pytest
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe
from tests.helpers.match_predictions import (
    MeczeLigoweInMemoryRepository,
    mecz_ligowy,
    mecze_dwoch_sezonow,
)
from tests.helpers.match_repository import MeczInMemoryRepository
from tests.helpers.match_statistics_repository import FormaMeczuInMemoryRepository
from tests.helpers.schedule import ZapowiedzMeczuInMemoryRepository, mecz_zapowiedzi
from tests.interface.test_schedule import PdfRendererTestowy

from handball.app_factory import AplikacjaFactory
from handball.domain.match_predictions import KlasaTrafnosci
from handball.domain.match_report import (
    AnalizaModelu,
    AtakDruzyny,
    RaportMeczu,
    SciezkaRatingu,
    StrzelecRaportu,
)
from handball.domain.match_rules import MeczPolicy
from handball.domain.match_statistics import StatystykiMeczuCalculator
from handball.domain.matches import DaneMeczu, SzczegolyMeczu, ZawodnikMeczu
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

TERMIN = datetime(2025, 9, 22, 18)


def szczegoly(
    id_mecz: int = 204, wynik: tuple[int | None, int | None] = (30, 27)
) -> SzczegolyMeczu:
    return SzczegolyMeczu(
        mecz=DaneMeczu(
            id=id_mecz,
            wynik_gosp_full=wynik[0],
            wynik_gosc_full=wynik[1],
            wynik_gosp_pol=14,
            wynik_gosc_pol=15,
            id_zespol_gosp=30,
            id_zespol_gosc=10,
            data_faktyczna=TERMIN,
            widzowie=2450,
        ),
        nazwa_gospodarz="Górnik Zabrze",
        nazwa_gosc="Wisła Płock",
        sklad_gospodarz=[
            ZawodnikMeczu(zawodnik="Jan KOWALSKI", bramki=9, id_zawodnik=7, nr_koszulki=7),
            ZawodnikMeczu(zawodnik="Maria Cristina OLIVEIRA FERNANDES", bramki=4, nr_koszulki=3),
        ],
        sklad_gosc=[ZawodnikMeczu(zawodnik="Piotr LIS", bramki=8, id_zawodnik=9)],
    )


def klient(
    mecze_ligowe: list | None = None, dane: SzczegolyMeczu | None = None
) -> tuple[FlaskClient, PdfRendererTestowy]:
    renderer = PdfRendererTestowy()
    dane = dane or szczegoly()
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_repozytorium_meczow=lambda: MeczInMemoryRepository(szczegoly={dane.mecz.id: dane}),
        fabryka_formy_meczu=lambda: FormaMeczuInMemoryRepository(),
        fabryka_zapowiedzi_meczu=lambda: ZapowiedzMeczuInMemoryRepository(
            [mecz_zapowiedzi(204, wynik=(30, 27)), mecz_zapowiedzi(205)]
        ),
        fabryka_meczow_ligowych=lambda: MeczeLigoweInMemoryRepository(
            mecze_ligowe if mecze_ligowe is not None else mecze_dwoch_sezonow()
        ),
        renderer_pdf=renderer,
    )
    aplikacja = AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()
    return aplikacja.test_client(), renderer


def test_raport_zwraca_pdf_z_arkuszem_i_podpisem() -> None:
    test_klient, renderer = klient()
    odpowiedz = test_klient.get("/administracja/mecze/204/raport")

    assert odpowiedz.status_code == 200
    assert odpowiedz.mimetype == "application/pdf"
    assert 'filename="raport-meczu-204.pdf"' in odpowiedz.headers["Content-Disposition"]
    assert renderer.arkusze[0].name == "match_report_pdf.css"
    assert "Raport meczowy" in renderer.html
    assert "30:27" in renderer.html


def test_raport_bez_modelu_ma_strukture_ataku_i_historie() -> None:
    tresc = klient()[0].get("/administracja/mecze/204/raport?format=html").get_data(as_text=True)

    assert "Struktura ataku" in tresc
    assert "Model siły drużyn" not in tresc
    assert "Historia spotkań" in tresc
    assert "J. Kowalski" in tresc
    assert "M. Oliveira Fernandes" in tresc
    assert "★" not in tresc
    assert "2 450" in tresc


def test_raport_z_modelem_ma_sekcje_modelu_i_wykres_ratingu() -> None:
    ligowe = [*mecze_dwoch_sezonow(), mecz_ligowy(204, TERMIN, 30, 10, 30, 27, kolejka=4)]
    tresc = (
        klient(ligowe)[0].get("/administracja/mecze/204/raport?format=html").get_data(as_text=True)
    )

    assert "Model siły drużyn" in tresc
    assert "Siła drużyn w czasie" in tresc
    assert "Struktura ataku" not in tresc
    assert 'class="rating"' in tresc


def test_raport_meczu_bez_wyniku_zwraca_404() -> None:
    test_klient, _ = klient(dane=szczegoly(205, (None, None)))
    assert test_klient.get("/administracja/mecze/205/raport").status_code == 404
    assert test_klient.get("/administracja/mecze/999/raport").status_code == 404


def test_strona_meczu_ma_przycisk_raportu_tylko_po_meczu() -> None:
    tresc = klient()[0].get("/administracja/mecze/204").get_data(as_text=True)
    assert 'href="/administracja/mecze/204/raport"' in tresc
    bez_wyniku = klient(dane=szczegoly(205, (None, None)))[0]
    tresc_bez = bez_wyniku.get("/administracja/mecze/205").get_data(as_text=True)
    assert "/mecze/205/raport" not in tresc_bez


def model(prawdopodobienstwo_niskie: bool) -> AnalizaModelu:
    pusta = SciezkaRatingu(30, ())
    return AnalizaModelu(
        rating_gospodarza=1450,
        rating_goscia=1550,
        rating_gospodarza_po=1465,
        rating_goscia_po=1535,
        przewaga_parkietu=50,
        oczekiwane_gospodarza=26.0 if prawdopodobienstwo_niskie else 31.0,
        oczekiwane_goscia=30.0 if prawdopodobienstwo_niskie else 26.0,
        oczekiwana_roznica=-4.0 if prawdopodobienstwo_niskie else 5.0,
        roznica=3,
        reszta=7.0 if prawdopodobienstwo_niskie else -2.0,
        klasa=KlasaTrafnosci.SLABA,
        sigma=5.0,
        reszty_ligi=tuple(float(x) for x in range(-10, 11)),
        sciezka_gospodarza=pusta,
        sciezka_goscia=pusta,
        ranking_gospodarza=None,
        ranking_goscia=None,
    )


@pytest.mark.parametrize(
    ("niespodzianka", "poczatek"),
    [
        (True, "Niespodzianka: Górnik Zabrze wygrywa 30:27"),
        (False, "Górnik Zabrze wygrywa 30:27 —"),
    ],
)
def test_naglowek_i_kafelki_wedlug_modelu(niespodzianka: bool, poczatek: str) -> None:
    statystyki = StatystykiMeczuCalculator(MeczPolicy()).oblicz(szczegoly())
    strzelec = StrzelecRaportu("Jan KOWALSKI", 7, None, 9, None, None, None, 0.7, 10, 20)
    raport = RaportMeczu(
        statystyki=statystyki,
        mecz=mecz_zapowiedzi(204, wynik=(30, 27)),
        model=model(niespodzianka),
        nazwa_modelu="Dynamic Team Strength V1",
        liga=None,
        atak_gospodarza=AtakDruzyny((strzelec,), 30, 0),
        atak_goscia=AtakDruzyny((), 27, 0),
        tlo_gospodarza=None,
        tlo_goscia=None,
        widzowie=None,
    )
    widok = ZaleznosciZadaniaFactory().utworz_presenter_raportu_meczu().przygotuj(raport)

    assert widok.naglowek.startswith(poczatek)
    assert widok.kafelki[0].etykieta == "Szansa zwycięzcy"
    assert (widok.kafelki[0].klasa == "hot") is niespodzianka
    assert widok.model is not None
    assert (
        widok.model.szansa_gospodarza + widok.model.szansa_remisu + widok.model.szansa_goscia == 100
    )
    assert any("Poissona" in w for w in widok.wnioski)
    assert widok.przypisy[0].startswith("★")
    assert widok.druzyny[0].atak is not None and widok.druzyny[0].atak.strzelcy[0].wyjatkowy
    assert replace(widok, wnioski=[]).wnioski == []


def test_raport_skrocony_bez_modelu_naglowka_i_kafelkow() -> None:
    ligowe = [*mecze_dwoch_sezonow(), mecz_ligowy(204, TERMIN, 30, 10, 30, 27, kolejka=4)]
    test_klient, renderer = klient(ligowe)
    odpowiedz = test_klient.get("/administracja/mecze/204/raport?wariant=skrocony")
    tresc = renderer.html

    assert odpowiedz.status_code == 200
    assert 'filename="raport-meczu-204-skrocony.pdf"' in odpowiedz.headers["Content-Disposition"]
    assert 'class="skrocony"' in tresc
    assert "Raport meczowy · skrót" in tresc
    assert "Porównanie drużyn" in tresc
    assert "Historia spotkań" in tresc
    assert "Superliga" in tresc
    assert "Strzelcy" in tresc
    for pominiete in (
        "Model siły drużyn",
        "Siła drużyn w czasie",
        'class="headline"',
        'class="kpis"',
    ):
        assert pominiete not in tresc
    assert "Forma</span>" not in tresc


def test_strona_meczu_ma_przycisk_raportu_skroconego() -> None:
    tresc = klient()[0].get("/administracja/mecze/204").get_data(as_text=True)
    assert "/administracja/mecze/204/raport?wariant=skrocony" in tresc
