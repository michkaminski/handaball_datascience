from datetime import datetime

from flask import Flask
from tests.conftest import ustawienia_testowe

from handball.app_factory import AplikacjaFactory
from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    LiniaWyniku,
    MeczRozkladu,
    OpcjaFiltrow,
    OpcjeFiltrowRozkladu,
    RodzajSerii,
)
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory


class RozkladPamieciowy:
    def __init__(self) -> None:
        self.filtry: FiltryRozkladuBramek | None = None

    def pobierz_opcje(self) -> OpcjeFiltrowRozkladu:
        return OpcjeFiltrowRozkladu(
            sezony=(OpcjaFiltrow("195", "2025/2026"),),
            rozgrywki=(OpcjaFiltrow("Superliga", "Superliga"),),
        )

    def pobierz_wyniki(self, filtry: FiltryRozkladuBramek) -> tuple[LiniaWyniku, ...]:
        self.filtry = filtry
        return (LiniaWyniku(30, 28, 4), LiniaWyniku(25, 25, 2))

    def pobierz_mecze(
        self, filtry: FiltryRozkladuBramek, rodzaj: RodzajSerii, bramki: int
    ) -> tuple[MeczRozkladu, ...]:
        self.wybor = (filtry, rodzaj, bramki)
        return (
            MeczRozkladu(
                7,
                datetime(2026, 3, 1, 18, 30),
                "2025/2026",
                "Superliga",
                "Kielce",
                "Wisła",
                30,
                28,
            ),
        )


def aplikacja(repozytorium: RozkladPamieciowy | None = None) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_rozkladu_bramek=lambda: repozytorium or RozkladPamieciowy()
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_katalog_rozkladow_jest_w_raportach_i_ma_tabele() -> None:
    klient = aplikacja().test_client()
    katalog = klient.get("/administracja/raporty").get_data(as_text=True)
    assert 'href="/administracja/raporty/rozklady"' in katalog
    strona = klient.get("/administracja/raporty/rozklady")
    tresc = strona.get_data(as_text=True)
    assert strona.status_code == 200
    assert "Katalog rozkładów" in tresc
    assert "Rozkład bramek na mecz" in tresc
    assert 'href="/administracja/raporty/rozklady/bramki"' in tresc
    assert 'class="active"' in tresc
    assert ">Rozkłady</span>" in tresc


def test_rozklad_bramek_renderuje_wykres_tabele_i_filtry() -> None:
    repozytorium = RozkladPamieciowy()
    klient = aplikacja(repozytorium).test_client()
    assert klient.get("/administracja/raporty/rozklady/bramki").status_code == 200
    odpowiedz = klient.get(
        "/administracja/raporty/rozklady/bramki?id_sezon=195&rozgrywki=Superliga&plec=M"
    )
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryRozkladuBramek(195, "Superliga", "M")
    assert "Suma bramek w meczu" in tresc
    assert "Bramki gospodarzy" in tresc
    assert "Bramki gości" in tresc
    assert "goal-dist-chart" in tresc
    assert "data-goal-bar" in tresc
    assert "data-goal-dialog" in tresc
    assert 'role="group"' in tresc
    assert "<th scope=\"col\">Bramki</th>" in tresc
    assert "Narastająco" in tresc
    assert "2025/2026" in tresc
    assert ">58<" in tresc
    assert ">50<" in tresc
    assert "goal-dist-mode" in tresc
    for fragment in ("4", "66.7%", "100.0%"):
        assert fragment in tresc


def test_klikniecie_slupka_zwraca_mecze_tej_liczby_bramek() -> None:
    repozytorium = RozkladPamieciowy()
    klient = aplikacja(repozytorium).test_client()

    odpowiedz = klient.get(
        "/administracja/raporty/rozklady/bramki/mecze?seria=suma&bramki=58&id_sezon=195"
    )
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert repozytorium.wybor == (FiltryRozkladuBramek(195, None, None), RodzajSerii.SUMA, 58)
    assert "Kielce" in tresc
    assert "30:28" in tresc
    assert 'href="/administracja/mecze/7"' in tresc
    zla_seria = klient.get(
        "/administracja/raporty/rozklady/bramki/mecze?seria=dogrywka&bramki=1"
    )
    assert zla_seria.status_code == 400


def test_nieznana_plec_zwraca_400() -> None:
    odpowiedz = aplikacja().test_client().get("/administracja/raporty/rozklady/bramki?plec=X")

    assert odpowiedz.status_code == 400
