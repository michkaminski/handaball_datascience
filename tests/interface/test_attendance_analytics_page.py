import json
from datetime import datetime

from flask import Flask
from tests.conftest import ustawienia_testowe

from handball.app_factory import AplikacjaFactory
from handball.domain.attendance_aggregate import AgregatFrekwencji, MiaryRozkladu
from handball.domain.attendance_analytics import (
    FiltryFrekwencji,
    FrekwencjaCalculator,
    KlubFrekwencji,
    OpcjaFiltrow,
    OpcjeFiltrowFrekwencji,
    PodsumowanieFrekwencji,
    RekordFrekwencji,
    SezonFrekwencji,
    SredniaKlubuSezonu,
)
from handball.domain.attendance_calendar import (
    DaneKalendarza,
    KomorkaKalendarza,
    WierszKalendarza,
)
from handball.domain.attendance_cities import DaneMiast, MiastoFrekwencji, WkladMiasta
from handball.domain.attendance_city_breakdowns import HalaMiasta, RozgrywkiMiasta, SezonMiasta
from handball.domain.attendance_opponents import PrzeciwnikFrekwencji
from handball.domain.attendance_records import RekordyRozszerzoneFrekwencji
from handball.domain.attendance_sample import LIMIT_PROBKI, MeczProbki
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory

kalkulator = FrekwencjaCalculator()


def _rekord(id_mecz: int, sezon: str, gospodarz: str, gosc: str, widzowie: int) -> RekordFrekwencji:
    return RekordFrekwencji(
        id_mecz,
        datetime(2025, 10, 1, 18, 30),
        sezon,
        "Superliga",
        gospodarz,
        gosc,
        30,
        28,
        "Orlen Arena",
        widzowie,
    )


def _probka() -> tuple[MeczProbki, ...]:
    return tuple(
        MeczProbki(
            id_mecz=100 + indeks,
            widzowie=2000 + indeks * 150,
            termin=termin,
            dzien_tygodnia=termin.isoweekday(),
            godzina=termin.hour,
            miesiac=termin.month,
            id_gospodarza=10,
            id_goscia=11 + indeks % 3,
            gospodarz="Wisła Płock",
            gosc=("Kielce", "Azoty Puławy", "Zagłębie Lubin")[indeks % 3],
            bramki_gospodarza=28 + indeks % 5,
            bramki_goscia=26 + indeks % 4,
        )
        for indeks, termin in enumerate(datetime(2025, 10, 1 + dzien, 18, 0) for dzien in range(12))
    )


class FrekwencjaPamieciowa:
    def __init__(self) -> None:
        self.filtry: FiltryFrekwencji | None = None
        self.limit_rekordow: int | None = None
        self.limit_probki: int | None = None

    def pobierz_opcje(self) -> OpcjeFiltrowFrekwencji:
        return OpcjeFiltrowFrekwencji(
            sezony=(OpcjaFiltrow("195", "2025/2026"), OpcjaFiltrow("194", "2024/2025")),
            rozgrywki=(OpcjaFiltrow("Superliga", "Superliga"),),
            kluby=(OpcjaFiltrow("10", "Wisła Płock"),),
            hale=(OpcjaFiltrow("3", "Orlen Arena"),),
        )

    def pobierz_podsumowanie(self, filtry: FiltryFrekwencji) -> PodsumowanieFrekwencji:
        self.filtry = filtry
        return kalkulator.podsumuj([None, 0, 2500, 3500], bez_zer=filtry.bez_zer)

    def pobierz_sezony(self, filtry: FiltryFrekwencji) -> tuple[SezonFrekwencji, ...]:
        return (
            SezonFrekwencji(194, "2024/2025", 2024, kalkulator.podsumuj([2000, 2200])),
            SezonFrekwencji(195, "2025/2026", 2025, kalkulator.podsumuj([2500, 3500])),
        )

    def pobierz_kluby(self, filtry: FiltryFrekwencji) -> tuple[KlubFrekwencji, ...]:
        return (
            KlubFrekwencji(10, "Wisła Płock", kalkulator.podsumuj([3000, 3500])),
            KlubFrekwencji(11, "Kielce", kalkulator.podsumuj([2800])),
        )

    def pobierz_srednie_klubow(self, filtry: FiltryFrekwencji) -> tuple[SredniaKlubuSezonu, ...]:
        return (
            SredniaKlubuSezonu(10, 194, 2500),
            SredniaKlubuSezonu(10, 195, 3250),
            SredniaKlubuSezonu(11, 194, 2400),
            SredniaKlubuSezonu(11, 195, 2800),
        )

    def pobierz_rekordy(self, filtry: FiltryFrekwencji, limit: int) -> tuple[RekordFrekwencji, ...]:
        return (_rekord(7, "2025/2026", "Wisła Płock", "Kielce", 3500),)[:limit]

    def pobierz_przeciwnikow(self, filtry: FiltryFrekwencji) -> tuple[PrzeciwnikFrekwencji, ...]:
        return (
            PrzeciwnikFrekwencji(
                rozegrane=3, znane=2, suma=6000, maksimum=3500, id_zespol=11, nazwa="Kielce"
            ),
            PrzeciwnikFrekwencji(
                rozegrane=2, znane=2, suma=4000, maksimum=2200, id_zespol=12, nazwa="Azoty Puławy"
            ),
        )

    def pobierz_kalendarz(self, filtry: FiltryFrekwencji) -> DaneKalendarza:
        return DaneKalendarza(
            miesiace=(WierszKalendarza(rozegrane=4, znane=3, suma=9000, maksimum=3500, klucz=10),),
            dni=(
                WierszKalendarza(rozegrane=2, znane=2, suma=5000, maksimum=3000, klucz=3),
                WierszKalendarza(rozegrane=2, znane=1, suma=3500, maksimum=3500, klucz=6),
            ),
            godziny=(WierszKalendarza(rozegrane=4, znane=3, suma=8500, maksimum=3500, klucz=18),),
            rundy=(
                WierszKalendarza(
                    rozegrane=4, znane=3, suma=8500, maksimum=3500, klucz="Runda zasadnicza"
                ),
            ),
            komorki=(
                KomorkaKalendarza(
                    rozegrane=2, znane=2, suma=5000, maksimum=3000, dzien=3, godzina=18
                ),
                KomorkaKalendarza(
                    rozegrane=2, znane=1, suma=3500, maksimum=3500, dzien=6, godzina=15
                ),
            ),
        )

    def pobierz_miasta(self, filtry: FiltryFrekwencji) -> DaneMiast:
        return DaneMiast(
            miasta=(
                MiastoFrekwencji(
                    rozegrane=5,
                    znane=4,
                    suma=12000,
                    maksimum=4000,
                    miasto="Kielce",
                    liczba_klubow=2,
                    liczba_rozgrywek=2,
                    rozklad=MiaryRozkladu(mediana=3100.0, dominanta=3000, minimum=1800),
                ),
                MiastoFrekwencji(
                    rozegrane=3,
                    znane=3,
                    suma=6000,
                    maksimum=2500,
                    miasto="Płock",
                    liczba_klubow=1,
                    liczba_rozgrywek=1,
                ),
            ),
            wklady=(
                WkladMiasta(
                    "Kielce",
                    11,
                    "Industria Kielce",
                    "Superliga",
                    AgregatFrekwencji(rozegrane=3, znane=2, suma=8000, maksimum=4000),
                ),
                WkladMiasta(
                    "Kielce",
                    13,
                    "Iskra Kielce",
                    "Puchar Polski",
                    AgregatFrekwencji(rozegrane=2, znane=2, suma=4000, maksimum=2200),
                ),
                WkladMiasta(
                    "Płock",
                    10,
                    "Wisła Płock",
                    "Superliga",
                    AgregatFrekwencji(rozegrane=3, znane=3, suma=6000, maksimum=2500),
                ),
            ),
            mecze_bez_miasta=4,
            sezony=(
                SezonMiasta(
                    "kielce",
                    "2024/2025",
                    2024,
                    AgregatFrekwencji(rozegrane=2, znane=2, suma=5000, maksimum=2600),
                    MiaryRozkladu(mediana=2500.0, dominanta=2400, minimum=2400),
                ),
                SezonMiasta(
                    "kielce",
                    "2023/2024",
                    2023,
                    AgregatFrekwencji(rozegrane=3, znane=2, suma=7000, maksimum=4000),
                    MiaryRozkladu(mediana=3500.0, dominanta=3000, minimum=3000),
                ),
            ),
            rozgrywki=(
                RozgrywkiMiasta(
                    "kielce",
                    "Superliga",
                    1,
                    AgregatFrekwencji(rozegrane=3, znane=2, suma=8000, maksimum=4000),
                    MiaryRozkladu(mediana=4000.0, dominanta=4000, minimum=4000),
                ),
            ),
            hale=(
                HalaMiasta(
                    "kielce",
                    5,
                    "Hala Legionów",
                    "Chęciny",
                    AgregatFrekwencji(rozegrane=4, znane=4, suma=12000, maksimum=4000),
                    MiaryRozkladu(mediana=3100.0, dominanta=3000, minimum=1800),
                ),
            ),
        )

    def pobierz_rekordy_rozszerzone(
        self, filtry: FiltryFrekwencji, limit: int
    ) -> RekordyRozszerzoneFrekwencji:
        self.limit_rekordow = limit
        return RekordyRozszerzoneFrekwencji(
            sezony=(_rekord(21, "2025/2026", "Wisła Płock", "Kielce", 3500),),
            kluby=(_rekord(22, "2025/2026", "Klub Rekordowy", "Gość Klubu", 3400),),
            hale=(_rekord(23, "2024/2025", "Gospodarz Hali", "Gość Hali", 3300),),
            finaly=(_rekord(24, "2024/2025", "Finalista A", "Finalista B", 3200),),
            pary=(_rekord(25, "2023/2024", "Para Pierwsza", "Para Druga", 3100),),
        )

    def pobierz_probke(self, filtry: FiltryFrekwencji, limit: int) -> tuple[MeczProbki, ...]:
        self.limit_probki = limit
        return _probka()


def aplikacja(repozytorium: FrekwencjaPamieciowa | None = None) -> Flask:
    zaleznosci = ZaleznosciZadaniaFactory(
        fabryka_frekwencji=lambda: repozytorium or FrekwencjaPamieciowa()
    )
    return AplikacjaFactory(
        ustawienia_testowe(), rejestrator_widokow=WidokiRegistrar(zaleznosci)
    ).utworz()


def test_frekwencja_jest_w_katalogu_i_sidebarze() -> None:
    klient = aplikacja().test_client()
    katalog = klient.get("/administracja/raporty").get_data(as_text=True)
    assert 'href="/administracja/raporty/frekwencja"' in katalog
    assert "Frekwencja" in katalog
    strona = klient.get("/administracja/raporty/frekwencja")
    tresc = strona.get_data(as_text=True)
    assert strona.status_code == 200
    assert ">Frekwencja</span>" in tresc
    assert 'class="active"' in tresc


def test_dashboard_frekwencji_renderuje_kpi_trendy_ranking_i_rekordy() -> None:
    repozytorium = FrekwencjaPamieciowa()
    klient = aplikacja(repozytorium).test_client()
    odpowiedz = klient.get(
        "/administracja/raporty/frekwencja"
        "?id_sezon=195&rozgrywki=Superliga&plec=M&id_zespol=10&id_hala=3"
    )
    tresc = odpowiedz.get_data(as_text=True)

    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryFrekwencji(195, "Superliga", "M", 10, 3, False)
    assert "Łącznie widzów" in tresc
    assert "Trendy sezonowe" in tresc
    assert "Frekwencja gospodarzy według klubu" in tresc
    assert "Rekordy frekwencji" in tresc
    assert "data-attendance-chart" in tresc
    assert "attendance-chart-data" in tresc
    assert "Wisła Płock" in tresc
    assert "Orlen Arena" in tresc
    assert "3 500" in tresc
    assert 'href="/administracja/mecze/7"' in tresc


def test_dashboard_ma_zakladki_i_panele() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)

    assert 'role="tablist"' in tresc
    assert "data-attendance-tabs" in tresc
    etykiety = (
        "Podsumowanie",
        "Trendy",
        "Kluby",
        "Miasta",
        "Rekordy",
        "Przeciwnicy",
        "Kalendarz",
        "Rekordy+",
        "Data Science",
    )
    klucze = (
        "overview",
        "trends",
        "clubs",
        "cities",
        "records",
        "opponents",
        "calendar",
        "extended",
        "science",
    )
    for klucz, etykieta in zip(klucze, etykiety, strict=True):
        assert f'data-tab="{klucz}"' in tresc
        assert f'aria-controls="att-panel-{klucz}"' in tresc
        assert f'id="att-panel-{klucz}"' in tresc
        assert f'data-attendance-panel="{klucz}"' in tresc
        assert f">{etykieta}</button>" in tresc
    assert 'data-tab="overview" aria-controls="att-panel-overview" aria-selected="true"' in tresc


def test_dashboard_wybiera_zakladke_z_parametru() -> None:
    klient = aplikacja().test_client()

    adres = "/administracja/raporty/frekwencja"
    polska = klient.get(f"{adres}?zakladka=calendar").get_data(as_text=True)
    angielska = klient.get(f"{adres}?tab=science").get_data(as_text=True)
    nieznana = klient.get(f"{adres}?zakladka=nie-ma").get_data(as_text=True)

    assert 'data-active-tab="calendar"' in polska
    assert 'aria-controls="att-panel-calendar" aria-selected="true"' in polska
    assert 'name="zakladka" value="calendar"' in polska
    assert 'data-active-tab="science"' in angielska
    assert 'data-active-tab="overview"' in nieznana


def test_dashboard_renderuje_hosty_wykresow() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?id_zespol=10").get_data(as_text=True)

    for wykres in (
        "trend",
        "coverage",
        "clubs",
        "cities",
        "heatmap",
        "months",
        "weekdays",
        "hours",
        "opponents",
        "histogram",
        "weekdayEffect",
    ):
        assert f'data-chart="{wykres}"' in tresc
    for atrybut in (
        "data-attendance-chart-coverage",
        "data-attendance-chart-clubs",
        "data-attendance-chart-cities",
        "data-attendance-chart-months",
        "data-attendance-chart-weekdays",
        "data-attendance-chart-hours",
        "data-attendance-chart-opponents",
        "data-attendance-chart-weekday-effect",
    ):
        assert atrybut in tresc


def test_dane_wykresow_zawieraja_nowe_serie() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?id_zespol=10").get_data(as_text=True)

    klucze = (
        "kluby",
        "miasta",
        "miesiace",
        "dni",
        "godziny",
        "przeciwnicy",
        "pokrycie",
        "efektDnia",
    )
    for klucz in klucze:
        assert f'"{klucz}"' in tresc
    assert '"roznica"' in tresc
    assert '"pokrycie"' in tresc


def test_dashboard_renderuje_zakladke_miast() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?zakladka=cities").get_data(as_text=True)

    assert 'data-active-tab="cities"' in tresc
    assert 'id="miasta"' in tresc
    assert "Frekwencja według miasta klubu gospodarza" in tresc
    assert "zespoly_sezony.miasto" in tresc
    assert "Mecze bez miasta klubu" in tresc
    assert "Ranking miast" in tresc
    assert "Skąd pochodzi frekwencja" in tresc
    assert "Szukaj miasta" in tresc
    assert "Szukaj klubu, miasta lub rozgrywek" in tresc
    assert 'data-chart="cities"' in tresc
    assert '<th scope="row">Kielce</th>' in tresc
    assert "Industria Kielce" in tresc
    assert "Puchar Polski" in tresc
    assert 'href="/administracja/druzyny/13"' in tresc
    assert 'data-filter-miasto="kielce"' in tresc
    assert "4 rozegranych meczów pominięto" in tresc


def test_zakladka_miast_renderuje_mediane_dominante_i_rozbicia() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?zakladka=cities").get_data(as_text=True)

    for naglowek in (
        "Sezony w miastach",
        "Rozgrywki w miastach",
        "Hale w miastach",
        "Wybrane miasto: sezony, rozgrywki i hale",
        "Dominanta",
        "Mediana",
    ):
        assert naglowek in tresc
    for atrybut in (
        'data-chart="citySeasons"',
        'data-chart="cityCompetitions"',
        'data-chart="cityHalls"',
        "data-city-select",
        "data-attendance-city-seasons",
        "data-attendance-city-competitions",
        "data-attendance-city-halls",
    ):
        assert atrybut in tresc
    assert "<td>2023/2024</td>" in tresc
    assert "<td>Hala Legionów</td>" in tresc
    assert "<td>Chęciny</td>" in tresc
    assert '<option value="kielce">Kielce</option>' in tresc
    assert 'data-filter-text="kielce kielce"' in tresc
    assert tresc.count('data-filter-miasto="kielce"') >= 6
    assert "3 100" in tresc


def test_kolejnosc_sezonow_miasta_jest_chronologiczna_w_tabeli() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?zakladka=cities").get_data(as_text=True)

    assert tresc.index("<td>2023/2024</td>") < tresc.index("<td>2024/2025</td>")


def test_dane_wykresu_miast_zawieraja_miary_i_szczegoly_wybranego_miasta() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)
    wykres = json.loads(tresc.split('id="attendance-chart-data">', 1)[1].split("</script>", 1)[0])

    kielce = wykres["miasta"][0]
    assert kielce["klucz"] == "kielce"
    assert kielce["mediana"] == 3100.0
    assert kielce["dominanta"] == 3000
    szczegoly = {pozycja["klucz"]: pozycja for pozycja in wykres["miastaSzczegoly"]}
    assert [sezon["sezon"] for sezon in szczegoly["kielce"]["sezony"]] == [
        "2023/2024",
        "2024/2025",
    ]
    assert szczegoly["kielce"]["rozgrywki"][0]["nazwa"] == "Superliga"
    assert szczegoly["kielce"]["hale"][0]["nazwa"] == "Hala Legionów (Chęciny)"
    assert szczegoly["płock"]["sezony"] == []


def test_dane_wykresu_miast_sa_posortowane_wedlug_sumy() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)
    wykres = json.loads(tresc.split('id="attendance-chart-data">', 1)[1].split("</script>", 1)[0])

    assert [miasto["nazwa"] for miasto in wykres["miasta"]] == ["Kielce", "Płock"]
    assert [miasto["suma"] for miasto in wykres["miasta"]] == [12000, 6000]


def test_wykres_przeciwnikow_pusty_bez_klubu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)

    assert 'data-chart="opponents"' not in tresc
    assert '"przeciwnicy": []' in tresc or '"przeciwnicy":[]' in tresc


def test_dashboard_renderuje_przeciwnikow_dla_wybranego_klubu() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?id_zespol=10").get_data(as_text=True)

    assert 'id="przeciwnicy"' in tresc
    assert "<h2>Przeciwnicy</h2>" in tresc
    assert "Różnica vs średnia gospodarza" in tresc
    assert "Azoty Puławy" in tresc
    assert 'href="/administracja/druzyny/11"' in tresc
    assert "wymaga wybrania klubu" not in tresc


def test_dashboard_bez_klubu_podpowiada_filtr_gospodarza() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)

    assert "<h2>Przeciwnicy</h2>" in tresc
    assert "wymaga wybrania klubu" in tresc
    assert "Różnica vs średnia gospodarza" not in tresc
    assert "Efekt przeciwnika" in tresc
    assert "tylko po wybraniu klubu" in tresc


def test_dashboard_renderuje_kalendarz_i_heatmape() -> None:
    klient = aplikacja().test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)

    assert "<h2>Kalendarz</h2>" in tresc
    for naglowek in ("Miesiąc", "Dzień tygodnia", "Godzina rozpoczęcia", "Runda / faza rozgrywek"):
        assert naglowek in tresc
    assert "październik" in tresc
    assert "środa" in tresc
    assert "dzień roboczy" in tresc
    assert "weekend" in tresc
    assert "Runda zasadnicza" in tresc
    assert "data-attendance-heatmap" in tresc
    assert "Mapa cieplna" in tresc
    assert '"heatmapa"' in tresc
    assert '"komorki"' in tresc


def test_dashboard_renderuje_rozszerzone_rekordy_z_linkami() -> None:
    repozytorium = FrekwencjaPamieciowa()
    klient = aplikacja(repozytorium).test_client()
    tresc = klient.get("/administracja/raporty/frekwencja").get_data(as_text=True)

    assert repozytorium.limit_rekordow == 30
    assert "<h2>Rozszerzone rekordy</h2>" in tresc
    for naglowek in ("Rekordy sezonów", "Rekordy klubów", "Rekordy hal", "Finały", "Pary drużyn"):
        assert naglowek in tresc
    for id_mecz in (21, 22, 23, 24, 25):
        assert f'href="/administracja/mecze/{id_mecz}"' in tresc
    assert "Finalista A" in tresc
    assert "Para Pierwsza" in tresc


def test_dashboard_renderuje_sekcje_data_science() -> None:
    repozytorium = FrekwencjaPamieciowa()
    klient = aplikacja(repozytorium).test_client()
    tresc = klient.get("/administracja/raporty/frekwencja?id_zespol=10").get_data(as_text=True)

    assert repozytorium.limit_probki == LIMIT_PROBKI
    assert "<h2>Data Science</h2>" in tresc
    for naglowek in (
        "Rozkład frekwencji i percentyle",
        "Rozrzut: odchylenie standardowe i współczynnik zmienności",
        "Anomalie (reguła IQR)",
        "Efekt dnia tygodnia",
        "Efekt przeciwnika",
        "Korelacja Pearsona",
        "Prognoza liniowa (OLS, eksperyment)",
    ):
        assert naglowek in tresc
    assert "data-attendance-histogram" in tresc
    assert '"histogram"' in tresc
    assert "p95" in tresc
    assert "nie przyczynę" in tresc
    assert "Prognoza pominięta" in tresc
    assert "wymagane co najmniej 40" in tresc


def test_filtr_bez_zer_trafia_do_serwisu() -> None:
    repozytorium = FrekwencjaPamieciowa()
    klient = aplikacja(repozytorium).test_client()
    odpowiedz = klient.get("/administracja/raporty/frekwencja?bez_zer=y")

    assert odpowiedz.status_code == 200
    assert repozytorium.filtry == FiltryFrekwencji(bez_zer=True)
    assert "pominięto filtrem" in odpowiedz.get_data(as_text=True)
