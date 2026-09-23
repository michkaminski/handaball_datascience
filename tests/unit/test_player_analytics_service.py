from datetime import datetime

import pytest

from handball.domain.player_details import AnalitykaMeczuZawodnika, FiltryMeczowZawodnika
from handball.services.player_detail_service import SzczegolyZawodnikaAnalyticsService


class AnalitykaRepository:
    def __init__(
        self,
        bramki: tuple[int | None, ...],
        sezony: tuple[str, ...] | None = None,
        miejsca: tuple[str | None, ...] | None = None,
        rozgrywki: tuple[str, ...] | None = None,
    ) -> None:
        self.bramki = bramki
        self.sezony = sezony or tuple("2025/2026" for _ in bramki)
        self.miejsca = miejsca or tuple(None for _ in bramki)
        self.rozgrywki = rozgrywki or tuple("Liga" for _ in bramki)

    def pobierz_analityke(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> tuple[AnalitykaMeczuZawodnika, ...]:
        return tuple(
            AnalitykaMeczuZawodnika(
                id_mecz=indeks,
                termin=datetime(2026, 1, indeks),
                sezon=self.sezony[indeks - 1],
                rozgrywki=self.rozgrywki[indeks - 1],
                bramki=bramki,
                karne_bramki=1 if indeks == 1 else None,
                karne_liczba=2 if indeks == 1 else None,
                dwie_minuty=0 if indeks == 1 else None,
                upomnienia=None,
                dyskwalifikacje=None,
                miejsce=self.miejsca[indeks - 1],
            )
            for indeks, bramki in enumerate(self.bramki, 1)
        )

    def pobierz_szczegoly(self, id_zawodnik: int) -> None:
        raise NotImplementedError

    def pobierz_mecze(self, id_zawodnik: int, filtry: FiltryMeczowZawodnika) -> None:
        raise NotImplementedError


def test_podsumowanie_liczy_mediane_kwartyle_i_wiele_dominant() -> None:
    serwis = SzczegolyZawodnikaAnalyticsService(AnalitykaRepository((0, 1, 1, 2, 2, None)))
    wynik = serwis.pobierz_podsumowanie(7, FiltryMeczowZawodnika())
    assert wynik.liczba_meczow == 6
    assert wynik.liczba_znanych_bramek == 5
    assert wynik.suma_bramek == 6
    assert wynik.srednia_bramek == 1.2
    assert wynik.mediana_bramek == 1
    assert wynik.dominanty_bramek == (1, 2)
    assert wynik.kwartyl_pierwszy == 1
    assert wynik.kwartyl_trzeci == 2
    assert wynik.mecze_z_bramka == 4
    assert wynik.karne_bramki == 1 and wynik.karne_liczba == 2
    assert wynik.dwie_minuty == 0


def test_podsumowanie_liczy_statystyki_sezonu_z_podzialem_na_rozgrywki() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository(
            (2, 4, 4, None, 7, 1, 3),
            sezony=("2024/2025",) * 5 + ("2025/2026",) * 2,
            rozgrywki=("Liga", "Liga", "Liga", "Liga", "Puchar", "Liga", "Liga"),
        )
    ).pobierz_podsumowanie(7, FiltryMeczowZawodnika())
    sezony = wynik.statystyki_sezonow
    assert [s.sezon for s in sezony] == ["2024/2025", "2025/2026"]
    caly_sezon = sezony[0].statystyki
    assert caly_sezon.liczba_meczow == 5 and caly_sezon.liczba_znanych == 4
    assert caly_sezon.suma == 17
    assert caly_sezon.srednia == pytest.approx(17 / 4)
    assert caly_sezon.mediana == 4.0 and caly_sezon.dominanty == (4,)
    assert caly_sezon.minimum == 2 and caly_sezon.maksimum == 7
    assert [r.rozgrywki for r in sezony[0].rozgrywki] == ["Liga", "Puchar"]
    liga = sezony[0].rozgrywki[0].statystyki
    assert liga.liczba_meczow == 4 and liga.liczba_znanych == 3 and liga.suma == 10
    assert liga.srednia == pytest.approx(10 / 3)
    assert sezony[0].rozgrywki[1].statystyki.suma == 7
    assert sezony[1].statystyki.dominanty == (1, 3) and sezony[1].statystyki.mediana == 2.0


def test_podsumowanie_nie_zamienia_brakow_na_zera() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository((None, None))
    ).pobierz_podsumowanie(7, FiltryMeczowZawodnika())
    assert wynik.suma_bramek is None
    assert wynik.srednia_bramek is None
    assert wynik.mediana_bramek is None
    assert wynik.dominanty_bramek == ()
    assert wynik.kwartyl_pierwszy is None and wynik.kwartyl_trzeci is None


def test_forma_kroczaca_mediana_i_srednia_liczy_sie_od_piatego_meczu() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository((1, 2, 3, 4, 5, 6), miejsca=("dom",) * 6)
    ).pobierz_forme(7, FiltryMeczowZawodnika())
    assert wynik.liczba_znanych == 6
    assert wynik.dom.liczba_znanych == 6
    assert wynik.dom.wystarczajaco_na_trend_5 is True
    assert wynik.dom.wystarczajaco_na_trend_10 is False
    assert wynik.wyjazd.liczba_znanych == 0 and wynik.wyjazd.punkty == ()
    punkty = wynik.dom.punkty
    assert all(p.mediana_kroczaca_5 is None for p in punkty[:4])
    assert punkty[4].mediana_kroczaca_5 == 3
    assert punkty[4].srednia_kroczaca_5 == 3
    assert punkty[5].mediana_kroczaca_5 == 4
    assert all(p.mediana_kroczaca_10 is None for p in punkty)


def test_forma_pomija_nieznane_bramki_w_oknie_kroczacym() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository((1, 2, None, 3, 4, 5), miejsca=("dom",) * 6)
    ).pobierz_forme(7, FiltryMeczowZawodnika())
    punkty = wynik.dom.punkty
    assert punkty[2].bramki is None and punkty[2].mediana_kroczaca_5 is None
    assert punkty[5].mediana_kroczaca_5 == 3


def test_forma_liczy_okno_kroczace_osobno_dla_domu_i_wyjazdu() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository(
            (1, 10, 2, 11, 3, 12, 4, 13, 5, 14),
            miejsca=("dom", "wyjazd") * 5,
        )
    ).pobierz_forme(7, FiltryMeczowZawodnika())
    assert wynik.dom.liczba_znanych == 5 and wynik.wyjazd.liczba_znanych == 5
    assert wynik.dom.wystarczajaco_na_trend_5 is True
    assert wynik.wyjazd.wystarczajaco_na_trend_5 is True
    assert [p.bramki for p in wynik.dom.punkty] == [1, 2, 3, 4, 5]
    assert [p.bramki for p in wynik.wyjazd.punkty] == [10, 11, 12, 13, 14]
    assert wynik.dom.punkty[4].mediana_kroczaca_5 == 3
    assert wynik.wyjazd.punkty[4].mediana_kroczaca_5 == 12


def test_forma_liczy_okno_kroczace_ze_wszystkich_meczow_niezaleznie_od_miejsca() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository(
            (1, 10, 2, 11, 3, 12, 4, 13, 5, 14, 6),
            miejsca=("dom", "wyjazd") * 5 + (None,),
        )
    ).pobierz_forme(7, FiltryMeczowZawodnika())
    assert wynik.wszystkie.liczba_znanych == 11
    assert wynik.wszystkie.wystarczajaco_na_trend_10 is True
    assert [p.bramki for p in wynik.wszystkie.punkty] == [1, 10, 2, 11, 3, 12, 4, 13, 5, 14, 6]
    assert wynik.wszystkie.punkty[4].mediana_kroczaca_5 == 3
    assert wynik.wszystkie.punkty[4].srednia_kroczaca_5 == pytest.approx(27 / 5)
    assert wynik.wszystkie.punkty[10].mediana_kroczaca_10 == 8


def test_forma_statystyki_opisowe_nie_zamieniaja_brakow_na_zera() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository((0, 1, 2, 3, None, 10))
    ).pobierz_forme(7, FiltryMeczowZawodnika())
    assert wynik.liczba_meczow == 6 and wynik.liczba_znanych == 5
    assert wynik.minimum == 0 and wynik.maksimum == 10
    assert wynik.udzial_0_bramek == pytest.approx(20.0)
    assert wynik.udzial_1_2_bramki == pytest.approx(40.0)
    assert wynik.udzial_3_5_bramek == pytest.approx(20.0)
    assert wynik.udzial_6_plus_bramek == pytest.approx(20.0)
    assert wynik.mad is not None and wynik.rozstep_miedzykwartylowy is not None


def test_wspolczynnik_zmiennosci_pomijany_przy_sredniej_bliskiej_zera() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(AnalitykaRepository((0, 0, 0, 0, 0))).pobierz_forme(
        7, FiltryMeczowZawodnika()
    )
    assert wynik.srednia == 0
    assert wynik.wspolczynnik_zmiennosci is None


def test_forma_grupuje_rozstep_wedlug_sezonu_i_oznacza_odstajace() -> None:
    wynik = SzczegolyZawodnikaAnalyticsService(
        AnalitykaRepository(
            (1, 2, 2, 3, 30, 1, 2, 3),
            sezony=(
                "2024/2025",
                "2024/2025",
                "2024/2025",
                "2024/2025",
                "2024/2025",
                "2025/2026",
                "2025/2026",
                "2025/2026",
            ),
        )
    ).pobierz_forme(7, FiltryMeczowZawodnika())
    sezony = {s.sezon: s for s in wynik.sezony}
    assert set(sezony) == {"2024/2025", "2025/2026"}
    poprzedni = sezony["2024/2025"]
    assert poprzedni.liczba_znanych == 5
    assert poprzedni.mala_proba is False
    assert 30 in poprzedni.wartosci_odstajace
    assert poprzedni.maksimum < 30
    biezacy = sezony["2025/2026"]
    assert biezacy.liczba_znanych == 3 and biezacy.wartosci_odstajace == ()
    assert biezacy.mala_proba is True
