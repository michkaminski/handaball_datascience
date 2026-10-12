import random
from dataclasses import replace
from datetime import datetime, timedelta

import pytest
from tests.helpers.match_predictions import MeczeLigoweInMemoryRepository, mecz_ligowy
from tests.helpers.schedule import mecz_zapowiedzi, wystep

from handball.domain.match_predictions import (
    KwalifikacjaMeczuPolicy,
    MeczLigowy,
    OcenaPrognozyPolicy,
    ProgiTrafnosci,
    PrognozaMeczu,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.domain.match_preview import ZawodnikKadry
from handball.domain.match_report import (
    AnalizaModeluCalculator,
    AtakDruzynyCalculator,
    PunktRatingu,
    SciezkaRatingu,
    StrzelecRaportu,
    TloSezonuCalculator,
)
from handball.domain.matches import ZawodnikMeczu
from handball.interface.match_report_charts import (
    HistogramResztBuilder,
    WykresRatinguBuilder,
    WykresSezonuBuilder,
    liczba,
    ze_znakiem,
)
from handball.services.match_prediction_service import (
    BacktestPrognozService,
    KatalogModeliPrognoz,
    PodzialSezonowPolicy,
)


def liga_syntetyczna() -> list[MeczLigowy]:
    losowanie = random.Random(7)
    sila = {10: 4.0, 20: 2.0, 30: -1.0, 40: -3.0}
    mecze = []
    numer = 1000
    for id_sezon, start in ((4, datetime(2024, 9, 1, 18)), (5, datetime(2025, 9, 1, 18))):
        for kolejka in range(40):
            gosp, gosc = losowanie.sample(list(sila), 2)
            roznica = round(sila[gosp] - sila[gosc] + losowanie.gauss(1, 5))
            suma = 56 + losowanie.randint(-4, 4)
            a = (suma + roznica) // 2
            numer += 1
            mecze.append(
                mecz_ligowy(
                    numer,
                    start + timedelta(days=3 * kolejka),
                    gosp,
                    gosc,
                    a,
                    suma - a,
                    id_sezon=id_sezon,
                    kolejka=kolejka + 1,
                )
            )
    return mecze


@pytest.fixture(scope="module")
def prognozy() -> tuple[PrognozaMeczu, ...]:
    wzorce = WzorceNazwLig()
    backtest = BacktestPrognozService(
        MeczeLigoweInMemoryRepository(liga_syntetyczna()),
        KatalogModeliPrognoz(),
        KwalifikacjaMeczuPolicy(wzorce),
        OcenaPrognozyPolicy(ProgiTrafnosci()),
        PodzialSezonowPolicy(ZakresBacktestu()),
        wzorce,
    )
    return backtest.uruchom("team_strength_v1").prognozy


def test_analiza_modelu_prawdopodobienstwa_percentyl_i_ranking(
    prognozy: tuple[PrognozaMeczu, ...],
) -> None:
    ostatni = prognozy[-1]
    analiza = AnalizaModeluCalculator().analizuj(prognozy, ostatni.mecz.id_mecz)

    assert analiza is not None
    assert analiza.sigma is not None and analiza.sigma > 0
    assert len(analiza.reszty_ligi) == 39
    szanse = analiza.prawdopodobienstwa
    assert szanse is not None and sum(szanse) == pytest.approx(1)
    assert all(0 < p < 1 for p in szanse)
    assert 0 <= (analiza.percentyl_zaskoczenia or 0) <= 1
    assert analiza.reszta == pytest.approx(ostatni.aktualizacja.reszta_roznicy)
    assert analiza.zmiana_ratingu == pytest.approx(ostatni.aktualizacja.poprawka)
    assert analiza.ranking_gospodarza is not None and analiza.ranking_gospodarza.liczba == 4
    sciezka = analiza.sciezka_gospodarza
    assert len(sciezka.punkty) == AnalizaModeluCalculator.DLUGOSC_SCIEZKI + 1
    assert sciezka.punkty[-1].analizowany
    assert sciezka.punkty[-1].sezon == "2025/2026"
    assert {p.sezon for p in sciezka.punkty} <= {"2024/2025", "2025/2026"}


def test_analiza_modelu_bez_meczu_i_bez_proby(prognozy: tuple[PrognozaMeczu, ...]) -> None:
    kalkulator = AnalizaModeluCalculator()
    assert kalkulator.analizuj(prognozy, 1) is None
    analiza = kalkulator.analizuj(prognozy[:5], prognozy[4].mecz.id_mecz)
    assert analiza is not None
    assert analiza.sigma is None and analiza.prawdopodobienstwa is None
    assert analiza.percentyl_zaskoczenia is None


def test_tlo_ligi_z_sezonu_meczu(prognozy: tuple[PrognozaMeczu, ...]) -> None:
    ostatni = prognozy[-1].mecz
    tlo = AnalizaModeluCalculator().tlo_ligi(prognozy, ostatni.id_mecz)

    assert tlo is not None and tlo.liczba_meczow == 40
    assert tlo.suma_meczu == ostatni.bramki_gospodarza + ostatni.bramki_goscia
    assert 0 <= tlo.percentyl_sumy < 1
    assert 0 < tlo.udzial_wygranych_gospodarzy < 1


def test_atak_koncentracja_i_srednia_sezonu() -> None:
    sklad = [
        ZawodnikMeczu(zawodnik="A", bramki=6, id_zawodnik=1),
        ZawodnikMeczu(zawodnik="B", bramki=3, id_zawodnik=2),
        ZawodnikMeczu(zawodnik="C", bramki=3, id_zawodnik=3),
        ZawodnikMeczu(zawodnik="D", bramki=0, id_zawodnik=4),
        ZawodnikMeczu(zawodnik="E", bramki=None),
    ]
    kadra = [ZawodnikKadry(1, "A", "A", (), None, 10, 20)]
    atak = AtakDruzynyCalculator().oblicz(sklad, kadra, 12)

    assert [s.zawodnik for s in atak.strzelcy] == ["A", "B", "C"]
    assert atak.efektywna_liczba_strzelcow == pytest.approx(144 / 54)
    assert atak.udzial_trzech == 1
    assert atak.zawodnicy_bez_bramki == 1
    assert atak.strzelcy[0].udzial == 0.5
    assert atak.strzelcy[0].srednia_sezonu == 2
    assert atak.strzelcy[0].ponad_srednia == 4
    assert atak.strzelcy[1].srednia_sezonu is None


def test_poisson_wystepu() -> None:
    strzelec = StrzelecRaportu("A", 7, None, 5, None, None, None, 0.2, 20, 22)
    p = strzelec.prawdopodobienstwo_wystepu(5)
    assert p == pytest.approx(0.0054, abs=0.0002)
    assert strzelec.prawdopodobienstwo_wystepu(25) is None
    assert replace(strzelec, bramki=1).prawdopodobienstwo_wystepu(5) is None


def test_tlo_sezonu_filtruje_sezon_rozgrywki_i_ten_mecz() -> None:
    mecz = mecz_zapowiedzi(204, wynik=(30, 27))
    wystepy = [
        wystep(1, datetime(2025, 9, 1), 30, 10, "X", 25, 30),
        wystep(2, datetime(2025, 9, 8), 30, 10, "X", 35, 20),
        wystep(3, datetime(2025, 9, 9), 30, 10, "X", 40, 20, id_rozgrywki=900),
        wystep(204, datetime(2025, 9, 22), 30, 10, "X", 30, 27),
    ]
    tlo = TloSezonuCalculator().oblicz(wystepy, mecz, 30, 27)

    assert tlo.zdobyte_sezonu == (25, 35)
    assert tlo.srednia_zdobytych == 30
    assert tlo.percentyl_zdobytych == 0.5
    assert tlo.percentyl_straconych == 0.5


def test_histogram_ogon_i_znacznik() -> None:
    histogram = HistogramResztBuilder().zbuduj([-6.0, -1.0, 0.5, 1.5, 7.0], 5.0, 4.0)
    ogon = [s for s in histogram.slupki if s.ogon]
    assert ogon and all(s.x < histogram.zero_x - 30 or s.x > histogram.zero_x + 30 for s in ogon)
    assert histogram.znacznik_x > histogram.zero_x
    assert histogram.znacznik_etykieta == "ten mecz +5,0"


def test_wykres_ratingu_dzieli_sezony() -> None:
    def punkty(sezon: str, start: datetime, ratingi: list[float]) -> list[PunktRatingu]:
        return [
            PunktRatingu(start + timedelta(days=i), r, i, False, sezon)
            for i, r in enumerate(ratingi)
        ]

    gospodarz = SciezkaRatingu(
        1,
        tuple(
            punkty("2024/2025", datetime(2024, 9, 1), [1500, 1510, 1520])
            + punkty("2025/2026", datetime(2025, 9, 1), [1490, 1505])
        ),
    )
    gosc = SciezkaRatingu(2, tuple(punkty("2025/2026", datetime(2025, 9, 1), [1500, 1480])))
    wykres = WykresRatinguBuilder().zbuduj([("home", gospodarz, "A"), ("away", gosc, "B")])

    assert wykres is not None
    assert len(wykres.linie[0].odcinki) == 2
    assert len(wykres.separatory) == 1
    assert [p.etykieta for p in wykres.os_x] == ["sezon 2024/2025", "sezon 2025/2026"]
    assert wykres.srednia_y is not None


def test_wykres_sezonu_wyroznia_ten_mecz() -> None:
    wykres = WykresSezonuBuilder().zbuduj([("zdobyte", [25, 25, 30], 33)])
    assert wykres is not None
    kropki = wykres.rzedy[0].kropki
    assert sum(k.biezaca for k in kropki) == 1
    assert kropki[0].y != kropki[1].y
    assert WykresSezonuBuilder().zbuduj([("zdobyte", [], None)]) is None


def test_formatowanie_liczb() -> None:
    assert liczba(-2.25) == "−2,2"
    assert ze_znakiem(3.04) == "+3,0"
    assert ze_znakiem(0.01) == "0,0"
