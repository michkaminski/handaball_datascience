from datetime import datetime

import pytest
from tests.helpers.team_details import (
    MECZE_DRUZYNY,
    SZCZEGOLY_DRUZYNY,
    SzczegolyDruzynyInMemoryRepository,
    mecz_druzyny,
)

from handball.domain.match_rules import MeczPolicy, StatusMeczu
from handball.domain.team_details import (
    FiltryDruzyny,
    KolejnoscPozycjiPolicy,
    RezultatMeczu,
    RodzajBramek,
    RozstrzygniecieRemisu,
    WystepDruzynyPolicy,
)
from handball.services.goal_statistics import StatystykiBramekCalculator
from handball.services.team_detail_service import (
    AnalitykaDruzynyService,
    BilansDruzynyCalculator,
    FrekwencjaDruzynyCalculator,
)

REGULY = WystepDruzynyPolicy(MeczPolicy())


def serwis(repo: SzczegolyDruzynyInMemoryRepository) -> AnalitykaDruzynyService:
    return AnalitykaDruzynyService(
        repo,
        REGULY,
        BilansDruzynyCalculator(FrekwencjaDruzynyCalculator()),
        StatystykiBramekCalculator(),
    )


def test_wystep_bierze_wynik_z_kolumny_druzyny_a_miejsce_z_zamiany() -> None:
    gosc_z_zamiana = REGULY.wystep(MECZE_DRUZYNY[2])
    assert (gosc_z_zamiana.bramki, gosc_z_zamiana.stracone) == (31, 27)
    assert gosc_z_zamiana.miejsce == "dom"
    assert gosc_z_zamiana.rezultat == RezultatMeczu.WYGRANA
    gospodarz = REGULY.wystep(MECZE_DRUZYNY[0])
    assert (gospodarz.miejsce, gospodarz.przeciwnik) == ("dom", "Rywal <b>")
    assert REGULY.wystep(MECZE_DRUZYNY[1]).miejsce == "wyjazd"


def test_remis_z_pelnego_wyniku_i_rozstrzygniecie_osobno() -> None:
    karne = REGULY.wystep(MECZE_DRUZYNY[1])
    assert karne.rezultat == RezultatMeczu.REMIS
    assert karne.rozstrzygniecie == RozstrzygniecieRemisu.WYGRANA_PO_KARNYCH
    dogrywka = REGULY.wystep(
        mecz_druzyny(
            9,
            datetime(2026, 1, 1),
            "2025/2026",
            "gosp",
            (30, 30),
            dogrywka_1_full_gosp=33,
            dogrywka_1_full_gosc=35,
        )
    )
    assert dogrywka.rozstrzygniecie == RozstrzygniecieRemisu.PORAZKA_PO_DOGRYWCE


def test_walkower_i_brak_wyniku_nie_daja_bramek_ani_rezultatu() -> None:
    walkower = REGULY.wystep(
        mecz_druzyny(9, datetime(2026, 1, 1), "2025/2026", "gosp", (10, 0), id_zespol_walkower=5)
    )
    assert (walkower.status, walkower.bramki, walkower.rezultat) == (
        StatusMeczu.WALKOWER,
        None,
        None,
    )
    assert REGULY.wystep(MECZE_DRUZYNY[3]).status == StatusMeczu.ZAPLANOWANY


def test_bilans_liczy_wyniki_bramki_i_pozostale_mecze() -> None:
    bilans = BilansDruzynyCalculator(FrekwencjaDruzynyCalculator()).bilans(
        [REGULY.wystep(m) for m in MECZE_DRUZYNY]
    )
    assert (bilans.mecze, bilans.rozegrane) == (4, 3)
    assert (bilans.wygrane, bilans.remisy, bilans.porazki) == (2, 1, 0)
    assert bilans.remisy_wygrane_po_karnych == 1
    assert (bilans.bramki_zdobyte, bilans.bramki_stracone) == (89, 80)
    assert bilans.bez_wyniku == 1


def test_sezony_w_kolejnosci_karty_z_nazwa_druzyny_i_podzialem_rozgrywek() -> None:
    historia = serwis(SzczegolyDruzynyInMemoryRepository()).pobierz_historie(
        272, SZCZEGOLY_DRUZYNY.sezony
    )
    sezony = historia.sezony
    assert historia.bilans.mecze == 4
    assert [s.sezon for s in sezony] == ["2026/2027", "2025/2026", "2024/2025"]
    assert sezony[2].nazwa_druzyny == "Stara Wisła"
    assert [r.rozgrywki for r in sezony[0].rozgrywki] == ["Puchar", "Liga"]
    assert sezony[0].bilans.rozegrane == 1


def test_podsumowanie_tylko_z_rozegranych_meczow() -> None:
    wynik = serwis(SzczegolyDruzynyInMemoryRepository()).pobierz_analityke(
        272, FiltryDruzyny(), SZCZEGOLY_DRUZYNY.sezony
    )
    podsumowanie = wynik.podsumowanie
    assert len(podsumowanie.rozegrane) == 3
    assert podsumowanie.najwyzsze_zwyciestwo is not None
    assert podsumowanie.najwyzsze_zwyciestwo.id_mecz == 1
    assert podsumowanie.najwyzsza_porazka is None
    assert podsumowanie.najwiecej_zdobytych is not None
    assert podsumowanie.najwiecej_zdobytych.id_mecz == 3
    assert podsumowanie.najwiecej_straconych is not None
    assert podsumowanie.najwiecej_straconych.id_mecz == 2
    assert podsumowanie.najdluzsza_seria_zwyciestw == 1
    assert podsumowanie.najdluzsza_seria_bez_porazki == 3


def test_serie_zdobytych_i_straconych_licza_te_same_miary() -> None:
    wynik = serwis(SzczegolyDruzynyInMemoryRepository()).pobierz_analityke(
        272, FiltryDruzyny(), SZCZEGOLY_DRUZYNY.sezony
    )
    zdobyte, stracone = wynik.zdobyte, wynik.stracone
    assert (zdobyte.rodzaj, stracone.rodzaj) == (RodzajBramek.ZDOBYTE, RodzajBramek.STRACONE)
    assert [m.bramki for m in zdobyte.mecze] == [30, 28, 31]
    assert [m.bramki for m in stracone.mecze] == [25, 28, 27]
    assert (zdobyte.statystyki.mediana, stracone.statystyki.mediana) == (30, 27)
    assert (stracone.mediana_dom, stracone.mediana_wyjazd) == (26, 28)
    assert zdobyte.mediana_dom == 30.5
    assert [p.bramki for p in stracone.forma.wszystkie.punkty] == [25, 28, 27]
    assert [p.bramki for p in stracone.forma.dom.punkty] == [25, 27]
    assert stracone.statystyki_sezonow[0].statystyki.suma == 25
    assert stracone.forma.liczba_meczow == 3
    assert [m.bramki for m in wynik.roznica.mecze] == [5, 0, 4]
    assert wynik.roznica.statystyki.srednia == 3.0
    assert wynik.roznica.forma.minimum == 0


def test_filtr_rozgrywek_zaweza_analityke() -> None:
    wynik = serwis(SzczegolyDruzynyInMemoryRepository()).pobierz_analityke(
        272, FiltryDruzyny(rozgrywki="Puchar"), SZCZEGOLY_DRUZYNY.sezony
    )
    assert wynik.podsumowanie.bilans.mecze == 1
    assert wynik.zdobyte.forma.liczba_znanych == 1
    assert wynik.stracone.statystyki.suma == 27


def test_frekwencja_u_siebie_i_na_wyjezdzie_tylko_z_rozegranych_meczow() -> None:
    wystepy = [REGULY.wystep(m) for m in MECZE_DRUZYNY]
    frekwencja = FrekwencjaDruzynyCalculator().frekwencja(wystepy)
    assert (frekwencja.dom.mecze, frekwencja.dom.znane) == (2, 2)
    assert (frekwencja.dom.suma, frekwencja.dom.srednia, frekwencja.dom.mediana) == (
        2000,
        1000.0,
        1000.0,
    )
    assert frekwencja.dom.rekord is not None and frekwencja.dom.rekord.id_mecz == 1
    assert (frekwencja.wyjazd.znane, frekwencja.wyjazd.srednia) == (1, 5100.0)
    assert wystepy[3].widzowie is None


def test_brak_frekwencji_nie_jest_zerem() -> None:
    wystep = REGULY.wystep(mecz_druzyny(9, datetime(2026, 1, 1), "2025/2026", "gosp", (30, 20)))
    frekwencja = FrekwencjaDruzynyCalculator().frekwencja([wystep])
    assert (frekwencja.dom.mecze, frekwencja.dom.znane, frekwencja.dom.srednia) == (1, 0, None)
    assert frekwencja.dom.rekord is None


@pytest.mark.parametrize(
    ("pozycje", "grupa"),
    [
        (("Bramkarz",), 0),
        (("Rozgrywający", "Bramkarz"), 1),
        (("Skrzydłowy",), 2),
        (("Obrotowy",), 3),
        (("Trener",), 4),
        ((), 5),
    ],
)
def test_kolejnosc_pozycji_stawia_bramkarzy_na_gorze(pozycje: tuple[str, ...], grupa: int) -> None:
    assert KolejnoscPozycjiPolicy().pozycja(pozycje) == grupa
