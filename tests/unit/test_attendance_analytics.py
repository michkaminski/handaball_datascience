import pytest

from handball.domain.attendance_aggregate import AgregatFrekwencji, polacz_agregaty
from handball.domain.attendance_analytics import (
    FiltryFrekwencji,
    FrekwencjaCalculator,
    KlubFrekwencji,
    PodsumowanieFrekwencji,
    SezonFrekwencji,
    SredniaKlubuSezonu,
    percentyl,
    zmiana_wzgledna,
)
from handball.domain.attendance_calendar import (
    DaneKalendarza,
    KalendarzFrekwencjiCalculator,
    KomorkaKalendarza,
    WierszKalendarza,
)
from handball.domain.attendance_opponents import (
    PrzeciwnicyFrekwencjiCalculator,
    PrzeciwnikFrekwencji,
)

kalkulator = FrekwencjaCalculator()
kalkulator_przeciwnikow = PrzeciwnicyFrekwencjiCalculator()
kalkulator_kalendarza = KalendarzFrekwencjiCalculator()


def _przeciwnik(
    id_zespol: int, nazwa: str, rozegrane: int, znane: int, suma: int, maksimum: int | None
) -> PrzeciwnikFrekwencji:
    return PrzeciwnikFrekwencji(
        rozegrane=rozegrane,
        znane=znane,
        suma=suma,
        maksimum=maksimum,
        id_zespol=id_zespol,
        nazwa=nazwa,
    )


def _wiersz(klucz: int | str, rozegrane: int, znane: int, suma: int) -> WierszKalendarza:
    return WierszKalendarza(
        rozegrane=rozegrane,
        znane=znane,
        suma=suma,
        maksimum=suma // znane if znane else None,
        klucz=klucz,
    )


def _sezon(id_sezon: int, nazwa: str, rok: int, wartosci: list[int | None]) -> SezonFrekwencji:
    return SezonFrekwencji(id_sezon, nazwa, rok, kalkulator.podsumuj(wartosci))


def test_null_nie_jest_zerem_a_zero_jest_znane() -> None:
    assert kalkulator.znane_wartosci([None, 0, 500, -5]) == (0, 500)
    assert kalkulator.znane_wartosci([None, 0, 500], bez_zer=True) == (500,)

    podsumowanie = kalkulator.podsumuj([None, 0, 1000, 2000, 3000])

    assert podsumowanie.rozegrane == 5
    assert podsumowanie.znane == 4
    assert podsumowanie.pominiete == 1
    assert podsumowanie.suma == 6000
    assert podsumowanie.srednia == 1500
    assert podsumowanie.mediana == 1500
    assert (podsumowanie.q1, podsumowanie.q3) == (750, 2250)
    assert (podsumowanie.minimum, podsumowanie.maksimum) == (0, 3000)
    assert podsumowanie.mecze_zero == 1
    assert podsumowanie.pokrycie == 0.8
    assert podsumowanie.pokrycie_etykieta == "80.0%"


def test_braki_nie_obnizaja_sredniej() -> None:
    assert kalkulator.podsumuj([None, None, 1000]).srednia == 1000
    assert kalkulator.podsumuj([0, 1000]).srednia == 500


def test_bez_zer_pomija_mecze_bez_publicznosci() -> None:
    podsumowanie = kalkulator.podsumuj([0, 0, 1000], bez_zer=True)

    assert podsumowanie.znane == 1
    assert podsumowanie.srednia == 1000
    assert podsumowanie.mecze_zero == 2
    assert podsumowanie.pokrycie == pytest.approx(1 / 3)


def test_pusta_i_nieznana_proba_nie_ma_miar() -> None:
    pusta = kalkulator.podsumuj([])
    nieznana = kalkulator.podsumuj([None, None])

    assert pusta.pokrycie is None
    assert pusta.pokrycie_etykieta == "—"
    assert pusta.srednia is None
    assert pusta.mediana_etykieta == "—"
    assert pusta.maksimum_etykieta == "—"
    assert nieznana.rozegrane == 2
    assert nieznana.znane == 0
    assert nieznana.srednia is None
    assert nieznana.suma == 0
    assert percentyl([], 0.5) is None


def test_percentyle_interpoluja_jak_percentile_cont() -> None:
    assert percentyl([10], 0.25) == 10
    assert percentyl([1, 2, 3, 4], 0.5) == 2.5
    assert percentyl([1, 2, 3, 4, 5], 0.25) == 2
    assert percentyl([1, 2, 3, 4, 5], 0.75) == 4
    with pytest.raises(ValueError):
        percentyl([1], 1.5)


def test_podsumowanie_odrzuca_niespojnie_liczby() -> None:
    with pytest.raises(ValueError):
        PodsumowanieFrekwencji(1, 2, 0, None, None, None, None, None, None)


def test_zmiana_rok_do_roku() -> None:
    assert zmiana_wzgledna(110, 100) == pytest.approx(0.1)
    assert zmiana_wzgledna(90, 100) == pytest.approx(-0.1)
    assert zmiana_wzgledna(None, 100) is None
    assert zmiana_wzgledna(100, None) is None
    assert zmiana_wzgledna(100, 0) is None


def test_srednia_kroczaca_i_nachylenie() -> None:
    assert kalkulator.srednia_kroczaca([100, 200, None, 400], okno=2) == (100, 150, None, 400)
    assert kalkulator.nachylenie([(2020, 100.0), (2021, 200.0), (2022, 300.0)]) == pytest.approx(
        100
    )
    assert kalkulator.nachylenie([(2020, 100.0), (2021, None)]) is None
    assert kalkulator.nachylenie([(2020, 100.0), (2020, 200.0)]) is None
    with pytest.raises(ValueError):
        kalkulator.srednia_kroczaca([1], okno=0)


def test_trend_sortuje_sezony_i_liczy_yoy() -> None:
    trend = kalkulator.zbuduj_trend(
        [
            _sezon(3, "2022/2023", 2022, [3000]),
            _sezon(1, "2020/2021", 2020, [1000]),
            _sezon(2, "2021/2022", 2021, [None]),
        ]
    )

    assert [punkt.sezon.nazwa for punkt in trend.punkty] == [
        "2020/2021",
        "2021/2022",
        "2022/2023",
    ]
    assert [punkt.zmiana for punkt in trend.punkty] == [None, None, None]
    assert trend.nachylenie == pytest.approx(1000)

    stabilny = kalkulator.zbuduj_trend([_sezon(1, "a", 2020, [1000]), _sezon(2, "b", 2021, [1500])])
    assert stabilny.punkty[1].zmiana == pytest.approx(0.5)
    assert stabilny.punkty[1].zmiana_etykieta == "+50.0%"
    assert stabilny.punkty[1].srednia_kroczaca == 1250


def test_para_sezonow_bierze_wybrany_albo_najnowszy_znany() -> None:
    trend = kalkulator.zbuduj_trend(
        [
            _sezon(1, "2021/2022", 2021, [1000]),
            _sezon(2, "2022/2023", 2022, [1500]),
            _sezon(3, "2023/2024", 2023, [None]),
        ]
    )

    para = kalkulator.para_sezonow(trend, 2)
    assert para is not None
    assert para.cel.sezon.id_sezon == 2
    assert para.poprzedni.sezon.id_sezon == 1
    assert para.zmiana == pytest.approx(0.5)

    najnowsza = kalkulator.para_sezonow(trend, None)
    assert najnowsza is not None
    assert najnowsza.cel.sezon.id_sezon == 2

    assert kalkulator.para_sezonow(trend, 99) is None


def test_ranking_tylko_kluby_ze_srednia_i_yoy() -> None:
    kluby = (
        KlubFrekwencji(1, "Beta", kalkulator.podsumuj([1000, 1200])),
        KlubFrekwencji(2, "Alfa", kalkulator.podsumuj([2000])),
        KlubFrekwencji(3, "Gamma", kalkulator.podsumuj([None, None])),
    )
    trend = kalkulator.zbuduj_trend(
        [_sezon(10, "2021/2022", 2021, [1000]), _sezon(11, "2022/2023", 2022, [1500])]
    )
    para = kalkulator.para_sezonow(trend, 11)
    ranking = kalkulator.uloz_ranking(
        kluby,
        (
            SredniaKlubuSezonu(2, 10, 1000),
            SredniaKlubuSezonu(2, 11, 2000),
            SredniaKlubuSezonu(1, 10, 1100),
            SredniaKlubuSezonu(1, 11, 1100),
        ),
        para,
    )

    assert [wiersz.klub.nazwa for wiersz in ranking] == ["Alfa", "Beta"]
    assert ranking[0].pozycja == 1
    assert ranking[0].zmiana == pytest.approx(1.0)
    assert ranking[1].zmiana == pytest.approx(0.0)


def test_filtr_plci_przyjmuje_tylko_m_i_k() -> None:
    assert FiltryFrekwencji(plec="K").plec == "K"
    with pytest.raises(ValueError):
        FiltryFrekwencji(plec="X")


def test_agregat_odrzuca_niespojne_liczby_i_laczy_grupy() -> None:
    with pytest.raises(ValueError):
        AgregatFrekwencji(rozegrane=1, znane=2, suma=0, maksimum=None)

    razem = polacz_agregaty(
        [
            AgregatFrekwencji(rozegrane=3, znane=2, suma=5000, maksimum=3000),
            AgregatFrekwencji(rozegrane=2, znane=0, suma=0, maksimum=None),
            AgregatFrekwencji(rozegrane=1, znane=1, suma=4000, maksimum=4000),
        ]
    )

    assert (razem.rozegrane, razem.znane, razem.suma, razem.maksimum) == (6, 3, 9000, 4000)
    assert razem.srednia == 3000
    assert razem.pokrycie == 0.5
    assert polacz_agregaty([]).srednia is None
    assert polacz_agregaty([]).maksimum is None


def test_ranking_przeciwnikow_liczy_roznice_vs_srednia_gospodarza() -> None:
    ranking = kalkulator_przeciwnikow.uloz(
        [
            _przeciwnik(1, "Beta", 3, 2, 5000, 3000),
            _przeciwnik(2, "Alfa", 2, 2, 7000, 4000),
            _przeciwnik(3, "Gamma", 2, 0, 0, None),
            _przeciwnik(4, "Delta", 1, 1, 2500, 2500),
        ],
        srednia_gospodarza=3000,
    )

    assert ranking.aktywny
    assert ranking.uwaga is None
    assert [wiersz.przeciwnik.nazwa for wiersz in ranking.wiersze] == ["Alfa", "Beta", "Delta"]
    assert [wiersz.pozycja for wiersz in ranking.wiersze] == [1, 2, 3]
    assert [wiersz.roznica for wiersz in ranking.wiersze] == [500, -500, -500]
    assert ranking.wiersze[0].roznica_etykieta == "+500"
    assert ranking.wiersze[1].roznica_etykieta == "-500"
    assert ranking.wiersze[1].przeciwnik.pokrycie_etykieta == "66.7%"
    assert ranking.wiersze[2].przeciwnik.mala_proba


def test_ranking_przeciwnikow_bez_sredniej_gospodarza_i_limit() -> None:
    przeciwnicy = [_przeciwnik(i, f"Klub {i}", 1, 1, 1000 + i, 1000 + i) for i in range(1, 6)]

    ranking = kalkulator_przeciwnikow.uloz(przeciwnicy, None, limit=2)

    assert [wiersz.przeciwnik.id_zespol for wiersz in ranking.wiersze] == [5, 4]
    assert all(wiersz.roznica is None for wiersz in ranking.wiersze)
    assert all(wiersz.roznica_etykieta == "—" for wiersz in ranking.wiersze)


def test_ranking_przeciwnikow_nieaktywny_bez_klubu() -> None:
    ranking = kalkulator_przeciwnikow.nieaktywny()

    assert not ranking.aktywny
    assert ranking.wiersze == ()
    assert ranking.uwaga is not None
    assert "Gospodarz" in ranking.uwaga


def test_kalendarz_etykietuje_grupy_i_liczy_weekend() -> None:
    kalendarz = kalkulator_kalendarza.zbuduj(
        DaneKalendarza(
            miesiace=(_wiersz(1, 4, 4, 8000), _wiersz(12, 2, 0, 0)),
            dni=(
                _wiersz(1, 3, 3, 6000),
                _wiersz(5, 2, 1, 2000),
                _wiersz(6, 4, 4, 12000),
                _wiersz(7, 2, 2, 5000),
            ),
            godziny=(_wiersz(15, 2, 2, 5000), _wiersz(18, 6, 5, 10000)),
            rundy=(_wiersz("Runda zasadnicza", 8, 7, 14000),),
        )
    )

    assert [grupa.etykieta for grupa in kalendarz.miesiace] == ["styczeń", "grudzień"]
    assert kalendarz.miesiace[1].srednia is None
    assert [grupa.etykieta for grupa in kalendarz.dni_tygodnia] == [
        "poniedziałek",
        "piątek",
        "sobota",
        "niedziela",
    ]
    assert [grupa.etykieta for grupa in kalendarz.godziny] == ["15:00", "18:00"]
    roboczy, weekend = kalendarz.weekend
    assert roboczy.etykieta == "dzień roboczy"
    assert (roboczy.rozegrane, roboczy.znane, roboczy.suma) == (5, 4, 8000)
    assert roboczy.srednia == 2000
    assert weekend.etykieta == "weekend"
    assert (weekend.rozegrane, weekend.znane, weekend.suma) == (6, 6, 17000)
    assert weekend.srednia == pytest.approx(17000 / 6)
    assert kalendarz.rundy[0].etykieta == "Runda zasadnicza"
    assert kalendarz.ma_dane


def test_kalendarz_heatmapa_ma_posortowane_godziny_i_komorki() -> None:
    def komorka(dzien: int, godzina: int, znane: int, suma: int) -> KomorkaKalendarza:
        return KomorkaKalendarza(
            rozegrane=znane, znane=znane, suma=suma, maksimum=suma, dzien=dzien, godzina=godzina
        )

    kalendarz = kalkulator_kalendarza.zbuduj(
        DaneKalendarza(
            komorki=(komorka(6, 18, 2, 7000), komorka(3, 15, 1, 2000), komorka(3, 18, 3, 9000))
        )
    )
    heatmapa = kalendarz.heatmapa

    assert heatmapa.godziny == (15, 18)
    assert heatmapa.etykiety_godzin == ("15:00", "18:00")
    assert len(heatmapa.dni) == 7
    assert [(k.dzien, k.godzina) for k in heatmapa.komorki] == [(3, 15), (3, 18), (6, 18)]
    wieczor = heatmapa.komorka(3, 18)
    assert wieczor is not None
    assert wieczor.srednia == 3000
    assert heatmapa.komorka(1, 1) is None
    assert heatmapa.ma_dane


def test_pusty_kalendarz_nie_ma_danych() -> None:
    kalendarz = kalkulator_kalendarza.zbuduj(DaneKalendarza())

    assert not kalendarz.ma_dane
    assert kalendarz.weekend == ()
    assert not kalendarz.heatmapa.ma_dane
    assert kalendarz.heatmapa.godziny == ()
