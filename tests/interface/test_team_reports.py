from collections.abc import Sequence
from pathlib import Path

from flask import Flask
from tests.conftest import ustawienia_testowe
from tests.helpers.core_catalog_repository import KatalogPodstawowyInMemoryRepository
from tests.helpers.schedule import ZegarTestowy
from tests.helpers.team_details import SzczegolyDruzynyInMemoryRepository
from tests.helpers.team_reports import KadraRaportuInMemoryRepository

from handball.app_factory import AplikacjaFactory
from handball.contracts.pdf_renderer import GeneratorPdfNiedostepny
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class PdfRendererTestowy:
    def __init__(self, dostepny: bool = True) -> None:
        self.dostepny = dostepny
        self.html = ""
        self.arkusze: list[Path] = []

    def renderuj(self, html: str, arkusze: Sequence[Path]) -> bytes:
        if not self.dostepny:
            raise GeneratorPdfNiedostepny("Brak bibliotek Pango.")
        self.html = html
        self.arkusze = list(arkusze)
        return b"%PDF-testowy"


def aplikacja(
    renderer: PdfRendererTestowy,
    kadry: KadraRaportuInMemoryRepository | None = None,
) -> Flask:
    druzyny = SzczegolyDruzynyInMemoryRepository()
    katalog = KatalogPodstawowyInMemoryRepository()
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_szczegolow_druzyny=lambda: druzyny,
        fabryka_kadr_raportu=lambda: kadry or KadraRaportuInMemoryRepository(),
        fabryka_katalogu_podstawowego=lambda: katalog,
        renderer_pdf=renderer,
        zegar=ZegarTestowy(),
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_raport_druzyny_to_pdf_z_kadra_poprzednim_sezonem_i_meczami() -> None:
    renderer = PdfRendererTestowy()
    odpowiedz = (
        aplikacja(renderer).test_client().get("/administracja/druzyny/272/raport?id_sezon=195")
    )
    assert odpowiedz.status_code == 200
    assert odpowiedz.mimetype == "application/pdf"
    assert odpowiedz.headers["Content-Disposition"] == (
        'inline; filename="raport-druzyny-272-195.pdf"'
    )
    assert [a.name for a in renderer.arkusze] == ["team_report_pdf.css"]
    assert all(a.is_file() for a in renderer.arkusze)
    html = renderer.html
    assert "<script" not in html
    assert "Wisła Test" in html and "2026/2027" in html
    assert "Testowy Jan" in html and "1999" in html
    assert "Bramkarz &lt;b&gt;" in html
    assert "Bramkarze" in html and "Rozgrywający" in html
    assert "ten sam klub" in html
    assert "Inny Klub · I Liga" in html
    assert "Ostatnie mecze (3)" in html
    assert "J. Testowy 5" in html
    assert ".report .grid td{height:" in html


def test_raport_wymaga_sezonu_druzyny_i_zglasza_brak_generatora() -> None:
    klient = aplikacja(PdfRendererTestowy()).test_client()
    assert klient.get("/administracja/druzyny/272/raport").status_code == 400
    assert klient.get("/administracja/druzyny/272/raport?id_sezon=7").status_code == 400
    assert klient.get("/administracja/druzyny/272/raport?id_sezon=195&mecze=2").status_code == 400
    assert klient.get("/administracja/druzyny/999/raport?id_sezon=195").status_code == 404
    niedostepny = aplikacja(PdfRendererTestowy(dostepny=False)).test_client()
    assert niedostepny.get("/administracja/druzyny/272/raport?id_sezon=195").status_code == 503


def test_zestawienia_maja_strone_sezonu_i_poprzedniego() -> None:
    renderer = PdfRendererTestowy()
    odpowiedz = (
        aplikacja(renderer).test_client().get("/administracja/druzyny/272/zestawienia?id_sezon=195")
    )
    assert odpowiedz.status_code == 200
    assert odpowiedz.headers["Content-Disposition"] == (
        'inline; filename="zestawienia-druzyny-272-195.pdf"'
    )
    html = renderer.html
    assert "<script" not in html
    assert html.count('class="sheet-page"') == 2
    assert "Zestawienie sezonu 2026/2027" in html and "Zestawienie sezonu 2025/2026" in html
    assert "Testowy Jan" in html and "1999" in html
    assert 'class="sum hl"' in html
    assert "2/3" in html


def test_zestawienie_sezonu_bez_wpisu_druzyny_ma_komunikat() -> None:
    renderer = PdfRendererTestowy()
    aplikacja(renderer).test_client().get("/administracja/druzyny/272/zestawienia?id_sezon=193")
    assert "nie ma wpisu w sezonie 2010/2011" in renderer.html


def test_lista_raportow_druzyn_ma_linki_do_wydrukow() -> None:
    odpowiedz = aplikacja(PdfRendererTestowy()).test_client().get("/administracja/raporty/druzyny")
    tresc = odpowiedz.get_data(as_text=True)
    assert odpowiedz.status_code == 200
    assert "/administracja/druzyny/5/raport?id_sezon=195" in tresc
    assert "/administracja/druzyny/5/zestawienia?id_sezon=195" in tresc
    assert "Raporty drużyn" in tresc


def test_katalog_raportow_i_karta_druzyny_prowadza_do_wydrukow() -> None:
    klient = aplikacja(PdfRendererTestowy()).test_client()
    katalog = klient.get("/administracja/raporty").get_data(as_text=True)
    assert "/administracja/raporty/druzyny" in katalog
    karta = klient.get("/administracja/druzyny/272").get_data(as_text=True)
    assert "/administracja/druzyny/272/raport?id_sezon=195" in karta
    assert "/administracja/druzyny/272/zestawienia?id_sezon=195" in karta
