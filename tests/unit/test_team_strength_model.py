import math
from dataclasses import replace
from datetime import datetime

import pytest
from tests.helpers.match_predictions import mecz_ligowy

from handball.domain.match_predictions import (
    KlasaTrafnosci,
    KlasaWyniku,
    KonfiguracjaSilyDruzyn,
    KwalifikacjaMeczuPolicy,
    MeczDoPrognozy,
    OcenaPrognozyPolicy,
    PowodWykluczenia,
    ProgiTrafnosci,
    ProgiWyniku,
    PrognozaPunktowa,
    Typ1X2,
    WzorceNazwLig,
)
from handball.domain.team_strength_model import ModelSilyDruzyn, RownaniaSilyDruzyn

KONFIGURACJA = KonfiguracjaSilyDruzyn()
ROWNANIA = RownaniaSilyDruzyn(KONFIGURACJA)
KWALIFIKACJA = KwalifikacjaMeczuPolicy(WzorceNazwLig())


def mecz(
    id_mecz: int, dzien: int, gosp: int, gosc: int, wynik: tuple[int, int], **opcje: object
) -> MeczDoPrognozy:
    return KWALIFIKACJA.do_prognozy(
        mecz_ligowy(id_mecz, datetime(2025, 9, dzien, 18), gosp, gosc, wynik[0], wynik[1], **opcje)
    )


def test_roznica_ratingow_i_przewidywana_roznica_z_przykladu() -> None:
    roznica_ratingow = ROWNANIA.roznica_ratingow(1700, 1580)
    assert roznica_ratingow == 170
    assert ROWNANIA.przewidywana_roznica(roznica_ratingow) == pytest.approx(4.25)


def test_przewidywane_bramki_i_zaokraglenie_prezentacji() -> None:
    gospodarz, gosc = ROWNANIA.przewidywane_bramki(60.2, 4.4)
    assert gospodarz == pytest.approx(32.3) and gosc == pytest.approx(27.9)
    prognoza = PrognozaPunktowa(0, 4.4, 60.2, gospodarz, gosc, Typ1X2.GOSPODARZ)
    assert (prognoza.bramki_gospodarza_prezentowane, prognoza.bramki_goscia_prezentowane) == (
        32,
        28,
    )
    polowka = PrognozaPunktowa(0, 0, 57, 28.5, 28.5, Typ1X2.REMIS)
    assert polowka.bramki_gospodarza_prezentowane == 29


def test_typ_wedlug_progu_remisu() -> None:
    assert ROWNANIA.typ(0.76) is Typ1X2.GOSPODARZ
    assert ROWNANIA.typ(-0.76) is Typ1X2.GOSC
    assert ROWNANIA.typ(0.75) is Typ1X2.REMIS
    assert ROWNANIA.typ(-0.75) is Typ1X2.REMIS


def test_poprawka_tanh_z_przykladu_i_ograniczenie_skali() -> None:
    assert ROWNANIA.poprawka_ratingu(8 - 3.5) == pytest.approx(15.88, abs=0.01)
    assert abs(ROWNANIA.poprawka_ratingu(45 - 20)) < KONFIGURACJA.wspolczynnik_k
    assert ROWNANIA.poprawka_ratingu(-4.5) == pytest.approx(-ROWNANIA.poprawka_ratingu(4.5))


def test_regresja_miedzy_sezonami_i_ewma() -> None:
    assert ROWNANIA.regresja(1700) == pytest.approx(1640)
    assert ROWNANIA.regresja(1400) == pytest.approx(1430)
    assert ROWNANIA.ewma(59.52, 62) == pytest.approx(0.08 * 62 + 0.92 * 59.52)


def test_model_prognozuje_z_ratingow_sprzed_aktualizacji() -> None:
    model = ModelSilyDruzyn(KONFIGURACJA)
    pierwszy = mecz(1, 1, 10, 20, (35, 20))
    stan = model.stan_przed_meczem(pierwszy)
    assert stan.gospodarz.rating == 1500 and stan.gospodarz.nowa_druzyna
    prognoza = model.prognozuj(stan)
    assert prognoza.roznica_ratingow == 50
    assert prognoza.przewidywana_roznica == pytest.approx(1.25)
    assert prognoza.przewidywana_suma == 58
    aktualizacja = model.aktualizuj(pierwszy, prognoza)
    assert aktualizacja.poprawka == pytest.approx(25 * math.tanh(13.75 / 6))
    assert aktualizacja.rating_gospodarza_po + aktualizacja.rating_goscia_po == pytest.approx(3000)
    drugi = mecz(2, 8, 20, 10, (30, 30))
    stan_drugi = model.stan_przed_meczem(drugi)
    assert stan_drugi.gospodarz.rating == aktualizacja.rating_goscia_po
    assert stan_drugi.gosc.rating == aktualizacja.rating_gospodarza_po
    assert not stan_drugi.gospodarz.nowa_druzyna
    assert stan_drugi.oczekiwana_suma_ligi == pytest.approx(0.08 * 55 + 0.92 * 58)
    assert [a.id_mecz for a in stan_drugi.ostatnie_aktualizacje_ewma] == [1]


def test_aktualizacja_wymaga_wczesniejszej_prognozy_tego_meczu() -> None:
    model = ModelSilyDruzyn(KONFIGURACJA)
    pierwszy, drugi = mecz(1, 1, 10, 20, (30, 20)), mecz(2, 2, 30, 40, (30, 20))
    prognoza = model.prognozuj(model.stan_przed_meczem(pierwszy))
    with pytest.raises(ValueError):
        model.aktualizuj(drugi, prognoza)
    model.aktualizuj(pierwszy, prognoza)
    with pytest.raises(ValueError):
        model.aktualizuj(pierwszy, prognoza)


def test_regresja_przy_nowym_sezonie_jest_widoczna_w_stanie() -> None:
    model = ModelSilyDruzyn(KONFIGURACJA)
    stary = mecz(1, 1, 10, 20, (40, 20), id_sezon=4)
    model.aktualizuj(stary, model.prognozuj(model.stan_przed_meczem(stary)))
    rating_konca = model.rating(10)
    assert rating_konca is not None
    nowy = mecz(2, 2, 10, 30, (30, 30), id_sezon=5)
    stan = model.stan_przed_meczem(nowy)
    assert stan.gospodarz.rating == pytest.approx(1500 + 0.7 * (rating_konca - 1500))
    assert stan.gospodarz.regresja is not None
    assert stan.gospodarz.regresja.rating_konca_sezonu == rating_konca
    assert stan.gospodarz.regresja.sezon_poprzedni == "2024/2025"
    assert stan.gosc.nowa_druzyna and stan.gosc.rating == 1500
    model.aktualizuj(nowy, model.prognozuj(stan))
    kolejny = mecz(3, 3, 10, 20, (30, 30), id_sezon=5)
    assert model.stan_przed_meczem(kolejny).gospodarz.regresja is None
    assert model.stan_przed_meczem(kolejny).gosc.regresja is not None


def test_kwalifikacja_zamiana_wyznacza_faktycznego_gospodarza_bez_odwracania_wyniku() -> None:
    zwykly = KWALIFIKACJA.do_prognozy(
        mecz_ligowy(1, datetime(2025, 9, 1), 10, 20, 30, 25, zamiana=None)
    )
    assert (zwykly.gospodarz.id_zespol, zwykly.bramki_gospodarza) == (10, 30)
    zamieniony = KWALIFIKACJA.do_prognozy(
        mecz_ligowy(2, datetime(2025, 9, 1), 10, 20, 30, 25, zamiana=True)
    )
    assert zamieniony.zamiana
    assert (zamieniony.gospodarz.id_zespol, zamieniony.gospodarz.nazwa) == (20, "Industria Kielce")
    assert (zamieniony.bramki_gospodarza, zamieniony.bramki_goscia) == (25, 30)
    assert zamieniony.gosc.id_zespol == 10


@pytest.mark.parametrize(
    ("zmiana", "powod"),
    [
        ({"plec": None}, PowodWykluczenia.NIEZNANA_LIGA),
        ({"wycofany": True}, PowodWykluczenia.WYCOFANY),
        ({"walkower": True}, PowodWykluczenia.WALKOWER),
        ({"id_zespol_gosp": None}, PowodWykluczenia.BRAK_GOSPODARZA),
        ({"id_zespol_gosc": None}, PowodWykluczenia.BRAK_GOSCIA),
        ({"wynik_gosc": None}, PowodWykluczenia.BRAK_WYNIKU),
        ({"data": None}, PowodWykluczenia.BRAK_DATY),
        ({"data": datetime(1970, 1, 1)}, PowodWykluczenia.NIEPRAWIDLOWA_DATA),
    ],
)
def test_kwalifikacja_wyklucza_mecze_bez_wyniku_sportowego(
    zmiana: dict[str, object], powod: PowodWykluczenia
) -> None:
    dane = replace(mecz_ligowy(1, datetime(2026, 2, 1), 10, 20, 30, 28), **zmiana)
    assert KWALIFIKACJA.powod_wykluczenia(dane) is powod
    with pytest.raises(ValueError):
        KWALIFIKACJA.do_prognozy(dane)


def test_ocena_prognozy_liczy_bledy_na_wartosciach_dokladnych() -> None:
    ocena = OcenaPrognozyPolicy(ProgiTrafnosci()).ocen(
        PrognozaPunktowa(0, 3.6, 59.2, 31.4, 27.8, Typ1X2.GOSPODARZ),
        mecz(1, 1, 10, 20, (30, 29)),
    )
    assert ocena.blad_wyniku == pytest.approx(2.6)
    assert ocena.blad_roznicy == pytest.approx(2.6)
    assert ocena.blad_sumy == pytest.approx(0.2)
    assert ocena.typ is Typ1X2.GOSPODARZ and ocena.trafiony
    assert ocena.klasa is KlasaTrafnosci.TRAFNA


@pytest.mark.parametrize(
    ("blad", "klasa"),
    [
        (2.0, KlasaTrafnosci.BARDZO_TRAFNA),
        (4.0, KlasaTrafnosci.TRAFNA),
        (6.99, KlasaTrafnosci.PRZECIETNA),
        (10.0, KlasaTrafnosci.SLABA),
        (10.01, KlasaTrafnosci.BARDZO_SLABA),
    ],
)
def test_progi_klasy_trafnosci(blad: float, klasa: KlasaTrafnosci) -> None:
    assert ProgiTrafnosci().klasyfikuj(blad) is klasa


def test_snapshot_parametrow_ma_nazwy_z_kontraktu() -> None:
    assert KONFIGURACJA.wersja_modelu == "team_strength_v1"
    assert KONFIGURACJA.jako_slownik() == {
        "initial_rating": 1500,
        "home_advantage": 50,
        "margin_intercept": 0,
        "margin_slope": 0.025,
        "initial_expected_total": 58,
        "ewma_alpha": 0.08,
        "k_factor": 25,
        "margin_scale": 6,
        "season_retention": 0.7,
        "draw_margin_threshold": 0.75,
    }


def test_ocena_wyniku_prezentowanego_uznaje_dokladna_roznice() -> None:
    policy = OcenaPrognozyPolicy(ProgiTrafnosci())
    prognoza = PrognozaPunktowa(0, -0.4, 59.2, 29.4, 29.8, Typ1X2.REMIS)
    assert (prognoza.bramki_gospodarza_prezentowane, prognoza.bramki_goscia_prezentowane) == (
        29,
        30,
    )
    assert prognoza.roznica_prezentowana == -1
    ocena = policy.ocen(prognoza, mecz(1, 1, 10, 20, (30, 31)))
    assert ocena.poprawna_roznica and not ocena.dokladny_wynik
    assert ocena.klasa_wyniku is KlasaWyniku.DOKLADNA_ROZNICA
    dokladna = policy.ocen(prognoza, mecz(2, 2, 10, 20, (29, 30)))
    assert dokladna.dokladny_wynik and dokladna.poprawna_roznica
    assert dokladna.klasa_wyniku is KlasaWyniku.DOKLADNY_WYNIK
    odlegla = policy.ocen(prognoza, mecz(3, 3, 10, 20, (33, 28)))
    assert odlegla.blad_roznicy_prezentowanej == 6
    assert odlegla.klasa_wyniku is KlasaWyniku.ROZNICA_4_PLUS


@pytest.mark.parametrize(
    ("dokladny", "blad", "klasa"),
    [
        (True, 0, KlasaWyniku.DOKLADNY_WYNIK),
        (False, 0, KlasaWyniku.DOKLADNA_ROZNICA),
        (False, 1, KlasaWyniku.ROZNICA_1),
        (False, 2, KlasaWyniku.ROZNICA_2_3),
        (False, 3, KlasaWyniku.ROZNICA_2_3),
        (False, 4, KlasaWyniku.ROZNICA_4_PLUS),
    ],
)
def test_progi_oceny_wyniku(dokladny: bool, blad: int, klasa: KlasaWyniku) -> None:
    assert ProgiWyniku().klasyfikuj(dokladny, blad) is klasa


def test_kierunek_wyniku_prezentowanego() -> None:
    policy = OcenaPrognozyPolicy(ProgiTrafnosci())
    prognoza = PrognozaPunktowa(0, 18, 58, 38, 20, Typ1X2.GOSPODARZ)
    odwrotny = policy.ocen(prognoza, mecz(1, 1, 10, 20, (20, 38)))
    assert odwrotny.typ_prezentowany is Typ1X2.GOSPODARZ and odwrotny.typ is Typ1X2.GOSC
    assert not odwrotny.poprawny_typ_prognozy
    assert policy.ocen(prognoza, mecz(2, 2, 10, 20, (25, 24))).poprawny_typ_prognozy
    remis = PrognozaPunktowa(0, 0.4, 58, 29.2, 28.8, Typ1X2.REMIS)
    assert remis.roznica_prezentowana == 0
    assert policy.ocen(remis, mecz(3, 3, 10, 20, (27, 27))).poprawny_typ_prognozy
    assert not policy.ocen(remis, mecz(4, 4, 10, 20, (28, 27))).poprawny_typ_prognozy
