from datetime import datetime, timedelta

import pytest

from handball.domain.attendance_data_science import (
    FrekwencjaDataScienceCalculator,
    pearson,
)
from handball.domain.attendance_forecast import (
    MIN_MECZOW_PROGNOZY,
    PrognozaFrekwencjiCalculator,
    RegresjaOLS,
)
from handball.domain.attendance_sample import MeczProbki

prognoza = PrognozaFrekwencjiCalculator(RegresjaOLS())
kalkulator = FrekwencjaDataScienceCalculator(prognoza)


def _mecz(
    id_mecz: int,
    widzowie: int,
    termin: datetime | None = None,
    id_gospodarza: int | None = 1,
    id_goscia: int | None = 2,
    gosc: str = "Gość",
    bramki: tuple[int | None, int | None] = (30, 28),
) -> MeczProbki:
    return MeczProbki(
        id_mecz=id_mecz,
        widzowie=widzowie,
        termin=termin,
        dzien_tygodnia=termin.isoweekday() if termin else None,
        godzina=termin.hour if termin else None,
        miesiac=termin.month if termin else None,
        id_gospodarza=id_gospodarza,
        id_goscia=id_goscia,
        gospodarz="Gospodarz",
        gosc=gosc,
        bramki_gospodarza=bramki[0],
        bramki_goscia=bramki[1],
    )


def _z_dniem(id_mecz: int, widzowie: int, dzien: int) -> MeczProbki:
    return _mecz(id_mecz, widzowie, datetime(2025, 10, 5 + dzien, 18, 0))


def test_histogram_zlicza_wszystkie_mecze_i_liczy_percentyle() -> None:
    histogram = kalkulator.histogram([float(wartosc) for wartosc in range(1, 101)])

    assert histogram is not None
    assert len(histogram.przedzialy) == 10
    assert sum(przedzial.liczba for przedzial in histogram.przedzialy) == 100
    assert histogram.przedzialy[0].od == 1
    assert histogram.przedzialy[-1].do == pytest.approx(100)
    assert [percentyl.procent for percentyl in histogram.percentyle] == [10, 25, 50, 75, 90, 95]
    wartosci = {percentyl.procent: percentyl.wartosc for percentyl in histogram.percentyle}
    assert wartosci[50] == pytest.approx(50.5)
    assert wartosci[10] == pytest.approx(10.9)
    assert wartosci[95] == pytest.approx(95.05)


def test_histogram_pusty_i_o_stalej_wartosci() -> None:
    assert kalkulator.histogram([]) is None

    stala = kalkulator.histogram([2000.0, 2000.0, 2000.0])
    assert stala is not None
    assert len(stala.przedzialy) == 1
    assert stala.przedzialy[0].liczba == 3
    assert all(percentyl.wartosc == 2000 for percentyl in stala.percentyle)


def test_rozrzut_liczy_odchylenie_probkowe_i_cv() -> None:
    rozrzut = kalkulator.rozrzut([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])

    assert rozrzut.n == 8
    assert rozrzut.srednia == 5
    assert rozrzut.odchylenie == pytest.approx((32 / 7) ** 0.5)
    assert rozrzut.wspolczynnik_zmiennosci == pytest.approx((32 / 7) ** 0.5 / 5)
    assert not rozrzut.mala_proba
    assert rozrzut.ostrzezenie is None


def test_rozrzut_ostrzega_przy_malej_probie_i_brakach() -> None:
    mala = kalkulator.rozrzut([1000.0, 2000.0, 3000.0, 4000.0])
    assert mala.mala_proba
    assert mala.ostrzezenie is not None
    assert "n=4" in mala.ostrzezenie

    jeden = kalkulator.rozrzut([1000.0])
    assert jeden.odchylenie is None
    assert jeden.wspolczynnik_zmiennosci is None
    assert jeden.wspolczynnik_etykieta == "—"

    pusty = kalkulator.rozrzut([])
    assert (pusty.n, pusty.srednia, pusty.odchylenie) == (0, None, None)

    zerowa = kalkulator.rozrzut([0.0, 0.0, 0.0, 0.0, 0.0])
    assert zerowa.odchylenie == 0
    assert zerowa.wspolczynnik_zmiennosci is None


def test_anomalie_iqr_wskazuja_wysokie_i_niskie() -> None:
    wartosci = [1000, 1010, 1020, 1030, 1040, 1050, 1060, 5000, 10]
    probka = [_mecz(indeks, widzowie) for indeks, widzowie in enumerate(wartosci, start=1)]

    anomalie = kalkulator.anomalie(probka)

    assert anomalie.ma_dane
    assert (anomalie.q1, anomalie.q3) == (1010, 1050)
    assert (anomalie.dolna_granica, anomalie.gorna_granica) == (950, 1110)
    assert [anomalia.mecz.widzowie for anomalia in anomalie.wysokie] == [5000]
    assert [anomalia.mecz.widzowie for anomalia in anomalie.niskie] == [10]
    assert anomalie.wysokie[0].odchylenie == 3890
    assert anomalie.niskie[0].odchylenie == -940
    assert (anomalie.liczba_wysokich, anomalie.liczba_niskich) == (1, 1)


def test_anomalie_wymagaja_czterech_meczow_i_ograniczaja_liste() -> None:
    assert not kalkulator.anomalie([_mecz(1, 1000), _mecz(2, 9000), _mecz(3, 10)]).ma_dane
    assert not kalkulator.anomalie([]).ma_dane

    probka = [_mecz(indeks, 1000) for indeks in range(1, 61)] + [
        _mecz(100 + indeks, 5000 + indeks) for indeks in range(20)
    ]
    anomalie = kalkulator.anomalie(probka)

    assert anomalie.liczba_wysokich == 20
    assert len(anomalie.wysokie) == 15
    assert anomalie.wysokie[0].mecz.widzowie == 5019


def test_efekt_dnia_tygodnia_liczy_n_srednia_i_roznice() -> None:
    probka = [
        _z_dniem(1, 3000, 1),
        _z_dniem(2, 3200, 1),
        _z_dniem(3, 3100, 1),
        _z_dniem(4, 2000, 3),
        _z_dniem(5, 2200, 3),
        _mecz(6, 9999),
    ]

    dni = kalkulator.efekt_dnia_tygodnia(probka)

    assert [grupa.etykieta for grupa in dni] == ["poniedziałek", "środa"]
    assert [grupa.n for grupa in dni] == [3, 2]
    assert dni[0].srednia == pytest.approx(3100)
    assert dni[0].mediana == 3100
    ogolna = (3000 + 3200 + 3100 + 2000 + 2200 + 9999) / 6
    assert dni[0].roznica == pytest.approx(3100 - ogolna)
    assert all(grupa.mala_proba for grupa in dni)


def test_efekt_dnia_tygodnia_bez_malej_proby_przy_pieciu_meczach() -> None:
    probka = [_z_dniem(indeks, 2000 + indeks, 2) for indeks in range(5)]

    grupa = kalkulator.efekt_dnia_tygodnia(probka)[0]

    assert grupa.n == 5
    assert not grupa.mala_proba
    assert kalkulator.efekt_dnia_tygodnia([]) == ()


def test_efekt_przeciwnika_sortuje_wg_sredniej_i_pomija_nieznanych() -> None:
    probka = [
        _mecz(1, 3000, id_goscia=11, gosc="Kielce"),
        _mecz(2, 3400, id_goscia=11, gosc="Kielce"),
        _mecz(3, 2000, id_goscia=12, gosc="Puławy"),
        _mecz(4, 4000, id_goscia=None, gosc="—"),
    ]

    przeciwnicy = kalkulator.efekt_przeciwnika(probka)

    assert [grupa.etykieta for grupa in przeciwnicy] == ["Kielce", "Puławy"]
    assert przeciwnicy[0].srednia == 3200
    assert przeciwnicy[0].n == 2
    assert przeciwnicy[1].roznica == pytest.approx(2000 - 3100)


def test_analizuj_liczy_efekt_przeciwnika_tylko_przy_wybranym_klubie() -> None:
    probka = [_mecz(1, 3000), _mecz(2, 2500)]

    bez_klubu = kalkulator.analizuj(probka, znane_w_filtrze=2, id_zespol=None)
    z_klubem = kalkulator.analizuj(probka, znane_w_filtrze=2, id_zespol=1)

    assert bez_klubu.przeciwnicy is None
    assert z_klubem.przeciwnicy is not None
    assert len(z_klubem.przeciwnicy) == 1
    assert not bez_klubu.ucieta
    assert bez_klubu.uwaga_o_probce is None


def test_analizuj_oznacza_przycieta_probke_i_pusty_zbior() -> None:
    przycieta = kalkulator.analizuj([_mecz(1, 3000)], znane_w_filtrze=9000, id_zespol=None)
    pusta = kalkulator.analizuj([], znane_w_filtrze=0, id_zespol=None)

    assert przycieta.ucieta
    assert przycieta.uwaga_o_probce is not None
    assert not pusta.ma_dane
    assert pusta.histogram is None
    assert pusta.rozrzut.n == 0
    assert pusta.prognoza.prognoza is None


def test_pearson_liczy_wspolczynnik_i_odrzuca_przypadki_graniczne() -> None:
    assert pearson([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
    assert pearson([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)
    assert pearson([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]) == pytest.approx(0.8)
    assert pearson([1, 2, 3], [5, 5, 5]) is None
    assert pearson([1, 2], [1, 2]) is None
    assert pearson([1, 2, 3], [1, 2]) is None


def test_korelacje_widzow_z_bramkami_pomijaja_mecze_bez_wyniku() -> None:
    probka = [
        _mecz(1, 1000, bramki=(25, 25)),
        _mecz(2, 2000, bramki=(28, 26)),
        _mecz(3, 3000, bramki=(31, 27)),
        _mecz(4, 4000, bramki=(34, 28)),
        _mecz(5, 9000, bramki=(None, None)),
    ]

    roznica, suma = kalkulator.korelacje(probka)

    assert roznica.n == suma.n == 4
    assert roznica.wspolczynnik == pytest.approx(1.0)
    assert suma.wspolczynnik == pytest.approx(1.0)
    assert suma.sila == "silna"
    assert suma.kierunek == "dodatnia"
    assert suma.wspolczynnik_etykieta == "+1.00"


def test_korelacja_bez_zmiennosci_nie_ma_wartosci() -> None:
    probka = [_mecz(indeks, 1000 * indeks, bramki=(30, 30)) for indeks in range(1, 6)]

    roznica, _suma = kalkulator.korelacje(probka)

    assert roznica.wspolczynnik is None
    assert roznica.sila == "brak danych"
    assert roznica.kierunek == "—"
    assert roznica.wspolczynnik_etykieta == "—"


def test_regresja_ols_odtwarza_dokladna_zaleznosc() -> None:
    cechy = [[float(x), float(x % 3)] for x in range(10)]
    cele = [2.0 + 3.0 * wiersz[0] - 1.5 * wiersz[1] for wiersz in cechy]

    wspolczynniki = RegresjaOLS().dopasuj(cechy, cele)

    assert wspolczynniki is not None
    assert wspolczynniki[0] == pytest.approx(2.0, abs=1e-3)
    assert wspolczynniki[1] == pytest.approx(3.0, abs=1e-3)
    assert wspolczynniki[2] == pytest.approx(-1.5, abs=1e-3)


def test_regresja_ols_odrzuca_puste_i_niespojne_dane() -> None:
    assert RegresjaOLS().dopasuj([], []) is None
    assert RegresjaOLS().dopasuj([[1.0]], [1.0, 2.0]) is None


def _seria(liczba: int, godzina: int = 18) -> list[MeczProbki]:
    poczatek = datetime(2025, 9, 1, godzina, 0)
    mecze = []
    for indeks in range(liczba):
        termin = poczatek + timedelta(days=indeks)
        widzowie = 2000 + (800 if termin.isoweekday() >= 6 else 0)
        mecze.append(_mecz(indeks + 1, widzowie, termin, id_gospodarza=1 + indeks % 4))
    return mecze


def test_prognoza_jest_pomijana_ponizej_progu() -> None:
    wynik = prognoza.prognozuj(_seria(MIN_MECZOW_PROGNOZY - 1))

    assert wynik.prognoza is None
    assert wynik.powod_pominiecia is not None
    assert f"wymagane co najmniej {MIN_MECZOW_PROGNOZY}" in wynik.powod_pominiecia


def test_prognoza_dzieli_chronologicznie_80_20_i_porownuje_z_punktami_odniesienia() -> None:
    wynik = prognoza.prognozuj(list(reversed(_seria(80))))

    assert wynik.powod_pominiecia is None
    assert wynik.prognoza is not None
    model = wynik.prognoza
    assert model.n_uczace + model.n_testowe == 79
    assert model.n_testowe == int(79 * 0.2)
    assert model.mae <= model.rmse
    assert model.lepsza_od_sredniej
    nazwy = {wspolczynnik.nazwa: wspolczynnik.wartosc for wspolczynnik in model.wspolczynniki}
    assert "Godzina rozpoczęcia (godziny)" not in nazwy
    assert nazwy["Weekend (sobota lub niedziela)"] > 0


def test_cecha_sredniej_gospodarza_uzywa_tylko_wczesniejszych_meczow() -> None:
    termin = datetime(2025, 10, 1, 18, 0)
    mecze = [
        _mecz(1, 1000, termin, id_gospodarza=1),
        _mecz(2, 1500, termin, id_gospodarza=2),
        _mecz(3, 2000, termin + timedelta(days=1), id_gospodarza=1),
        _mecz(4, 9000, termin + timedelta(days=2), id_gospodarza=1),
        _mecz(5, 8000, termin + timedelta(days=3), id_gospodarza=3),
    ]

    wiersze = prognoza._wiersze(list(reversed(mecze)))

    assert [wiersz.mecz.id_mecz for wiersz in wiersze] == [3, 4, 5]
    assert wiersze[0].srednia_kroczaca == 1000
    assert wiersze[1].srednia_kroczaca == pytest.approx((1000 + 2000) / 2)
    assert wiersze[2].srednia_kroczaca == pytest.approx((1000 + 1500 + 2000 + 9000) / 4)


def test_prognoza_pomija_mecze_bez_terminu() -> None:
    mecze = _seria(MIN_MECZOW_PROGNOZY - 1) + [_mecz(999, 5000)]

    wynik = prognoza.prognozuj(mecze)

    assert wynik.prognoza is None
