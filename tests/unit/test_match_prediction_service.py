from dataclasses import replace
from datetime import datetime

import pytest
from tests.helpers.match_predictions import (
    MeczeLigoweInMemoryRepository,
    mecz_ligowy,
    mecze_dwoch_sezonow,
)

from handball.domain.errors import NieZnalezionoPrognozy, NieznanyModelPrognoz
from handball.domain.match_predictions import (
    FiltryPrognoz,
    KlasaTrafnosci,
    KlasaWyniku,
    KonfiguracjaSilyDruzyn,
    KwalifikacjaMeczuPolicy,
    Liga,
    MeczLigowy,
    OcenaPrognozyPolicy,
    OpisModeluPrognoz,
    Plec,
    PowodWykluczenia,
    PoziomRozgrywek,
    ProgiTrafnosci,
    Typ1X2,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.services.match_prediction_service import (
    BacktestPrognozService,
    DefinicjaModeluPrognoz,
    KatalogModeliPrognoz,
    PodsumowaniePrognozCalculator,
    PodzialSezonowPolicy,
    RaportPrognozService,
    SzczegolyPrognozyService,
)


def backtest(
    mecze: list[MeczLigowy] | None = None,
    zakres: ZakresBacktestu | None = None,
    katalog: KatalogModeliPrognoz | None = None,
) -> BacktestPrognozService:
    return BacktestPrognozService(
        MeczeLigoweInMemoryRepository(mecze),
        katalog or KatalogModeliPrognoz(),
        KwalifikacjaMeczuPolicy(WzorceNazwLig()),
        OcenaPrognozyPolicy(ProgiTrafnosci()),
        PodzialSezonowPolicy(zakres or ZakresBacktestu()),
        WzorceNazwLig(),
    )


def raport(mecze: list[MeczLigowy] | None = None) -> RaportPrognozService:
    return RaportPrognozService(
        backtest(mecze), KatalogModeliPrognoz(), PodsumowaniePrognozCalculator(ProgiTrafnosci())
    )


def test_repozytorium_dostaje_wzorce_nazw_superligi() -> None:
    repozytorium = MeczeLigoweInMemoryRepository()
    BacktestPrognozService(
        repozytorium,
        KatalogModeliPrognoz(),
        KwalifikacjaMeczuPolicy(WzorceNazwLig()),
        OcenaPrognozyPolicy(ProgiTrafnosci()),
        PodzialSezonowPolicy(ZakresBacktestu()),
        WzorceNazwLig(),
    ).uruchom("team_strength_v1")
    assert repozytorium.wzorce == WzorceNazwLig()


def test_backtest_sortuje_chronologicznie_i_nie_przecieka_z_przyszlosci() -> None:
    mecze = list(reversed(mecze_dwoch_sezonow()))
    wynik = backtest(mecze).uruchom("team_strength_v1")
    assert [p.mecz.id_mecz for p in wynik.prognozy] == [101, 102, 103, 201, 202, 203]
    zmienione = [replace(m, wynik_gosp=45, wynik_gosc=15) if m.id_mecz == 203 else m for m in mecze]
    po_zmianie = backtest(zmienione).uruchom("team_strength_v1")
    for przed, po in zip(wynik.prognozy[:-1], po_zmianie.prognozy[:-1], strict=True):
        assert przed.stan == po.stan and przed.prognoza == po.prognoza
    assert wynik.prognozy[-1].prognoza == po_zmianie.prognozy[-1].prognoza
    assert wynik.prognozy[-1].aktualizacja != po_zmianie.prognozy[-1].aktualizacja


def test_rating_przed_meczem_to_rating_po_poprzednim_meczu_druzyny() -> None:
    wynik = backtest().uruchom("team_strength_v1")
    pierwszy, drugi = wynik.prognozy[0], wynik.prognozy[1]
    assert drugi.stan.gosc.rating == pierwszy.aktualizacja.rating_gospodarza_po
    assert drugi.stan.gospodarz.rating == pierwszy.aktualizacja.rating_goscia_po


def test_zamiana_daje_przewage_parkietu_druzynie_z_kolumny_goscia() -> None:
    wynik = backtest().uruchom("team_strength_v1")
    zamieniony = next(p for p in wynik.prognozy if p.mecz.id_mecz == 202)
    assert zamieniony.mecz.gospodarz.id_zespol == 20
    assert (zamieniony.mecz.bramki_gospodarza, zamieniony.mecz.bramki_goscia) == (35, 24)
    assert zamieniony.prognoza.roznica_ratingow == pytest.approx(
        zamieniony.stan.gospodarz.rating - zamieniony.stan.gosc.rating + 50
    )


def test_ligi_maja_osobne_srednie_sumy_bramek() -> None:
    mecze = [
        mecz_ligowy(1, datetime(2025, 9, 1), 10, 20, 40, 40),
        mecz_ligowy(2, datetime(2025, 9, 2), 30, 40, 20, 20, plec="K"),
        mecz_ligowy(3, datetime(2025, 9, 3), 10, 20, 30, 30),
        mecz_ligowy(4, datetime(2025, 9, 4), 30, 40, 25, 25, plec="K"),
    ]
    wynik = backtest(mecze).uruchom("team_strength_v1")
    sumy = {p.mecz.id_mecz: p.stan.oczekiwana_suma_ligi for p in wynik.prognozy}
    assert sumy[1] == 58 and sumy[2] == 58
    assert sumy[3] == pytest.approx(0.08 * 80 + 0.92 * 58)
    assert sumy[4] == pytest.approx(0.08 * 40 + 0.92 * 58)


def test_wykluczenia_sa_liczone_wedlug_powodu() -> None:
    mecze = [
        *mecze_dwoch_sezonow(),
        mecz_ligowy(301, datetime(2025, 10, 1), 10, 20, 30, 20, walkower=True),
        mecz_ligowy(302, datetime(2025, 10, 2), 10, None, 30, 20),
        mecz_ligowy(303, None, 10, 20, 30, 20),
        mecz_ligowy(304, datetime(2025, 10, 3), 10, 20, None, None, wycofany=True),
    ]
    wynik = backtest(mecze).uruchom("team_strength_v1")
    assert len(wynik.prognozy) == 6
    assert wynik.wykluczenia == {
        PowodWykluczenia.WALKOWER: 1,
        PowodWykluczenia.BRAK_GOSCIA: 1,
        PowodWykluczenia.BRAK_DATY: 1,
        PowodWykluczenia.WYCOFANY: 1,
    }


def test_podzial_sezonow_na_rozgrzewke_raport_i_sezon_w_toku() -> None:
    mecze = [
        mecz_ligowy(id_sezon, datetime(2020 + id_sezon, 10, 1), 10, 20, 30, 28, id_sezon=id_sezon)
        for id_sezon in (1, 2, 3, 4)
    ] + [
        mecz_ligowy(51, datetime(2025, 10, 1), 10, 20, 30, 28, id_sezon=5),
        mecz_ligowy(52, datetime(2026, 3, 1), 10, 20, None, None, id_sezon=5),
    ]
    wynik = backtest(mecze, ZakresBacktestu(2)).uruchom("team_strength_v1")
    assert [s.nazwa for s in wynik.sezony_rozgrzewki] == ["2021/2022", "2022/2023"]
    assert [s.nazwa for s in wynik.sezony_raportu] == ["2023/2024", "2024/2025", "2025/2026"]
    assert wynik.sezon_w_toku is not None and wynik.sezon_w_toku.nazwa == "2025/2026"
    assert [p.mecz.id_mecz for p in wynik.prognozy_raportu] == [3, 4, 51]
    bez_biezacego = backtest(mecze, ZakresBacktestu(1, False)).uruchom("team_strength_v1")
    assert [s.nazwa for s in bez_biezacego.sezony_raportu] == ["2024/2025"]


def mecze_pieciu_sezonow() -> list[MeczLigowy]:
    return [
        mecz_ligowy(id_sezon, datetime(2020 + id_sezon, 10, 1), 10, 20, 30, 28, id_sezon=id_sezon)
        for id_sezon in (1, 2, 3, 4, 5)
    ]


@pytest.mark.parametrize(
    ("liczba", "raport", "rozgrzewka"),
    [
        (1, [5], [1, 2, 3, 4]),
        (3, [3, 4, 5], [1, 2]),
        (10, [2, 3, 4, 5], [1]),
        (None, [2, 3, 4, 5], [1]),
    ],
)
def test_liczba_sezonow_raportu_zostawia_co_najmniej_jeden_sezon_rozgrzewki(
    liczba: int | None, raport: list[int], rozgrzewka: list[int]
) -> None:
    wynik = backtest(mecze_pieciu_sezonow(), ZakresBacktestu(liczba)).uruchom("team_strength_v1")
    assert [s.id_sezon for s in wynik.sezony_raportu] == raport
    assert [s.id_sezon for s in wynik.sezony_rozgrzewki] == rozgrzewka


def test_zakres_przekazany_do_uruchomienia_zastepuje_domyslny_i_nie_zmienia_prognoz() -> None:
    serwis = backtest(mecze_pieciu_sezonow(), ZakresBacktestu(1))
    domyslny = serwis.uruchom("team_strength_v1")
    wszystkie = serwis.uruchom("team_strength_v1", ZakresBacktestu(None))
    assert [s.id_sezon for s in domyslny.sezony_raportu] == [5]
    assert [s.id_sezon for s in wszystkie.sezony_raportu] == [2, 3, 4, 5]
    assert [p.prognoza for p in domyslny.prognozy] == [p.prognoza for p in wszystkie.prognozy]


def test_raport_i_szczegoly_uzywaja_zakresu_z_filtrow() -> None:
    mecze = mecze_pieciu_sezonow()
    wynik = RaportPrognozService(
        backtest(mecze), KatalogModeliPrognoz(), PodsumowaniePrognozCalculator(ProgiTrafnosci())
    ).pobierz_raport(FiltryPrognoz(zakres=ZakresBacktestu(3)))
    assert [s.id_sezon for s in wynik.sezony] == [5, 4, 3]
    assert wynik.strona.liczba_wszystkich == 3
    szczegoly = SzczegolyPrognozyService(backtest(mecze), KatalogModeliPrognoz())
    assert not szczegoly.pobierz("team_strength_v1", 2, ZakresBacktestu(3)).prognoza.w_raporcie
    assert szczegoly.pobierz("team_strength_v1", 2, ZakresBacktestu(None)).prognoza.w_raporcie


def test_jeden_pelny_sezon_trafia_do_raportu_bez_rozgrzewki() -> None:
    wynik = backtest([mecz_ligowy(1, datetime(2025, 10, 1), 10, 20, 30, 28)]).uruchom(
        "team_strength_v1"
    )
    assert wynik.sezony_rozgrzewki == ()
    assert [s.nazwa for s in wynik.sezony_raportu] == ["2025/2026"]
    assert wynik.sezon_w_toku is None


def test_katalog_modeli_odrzuca_nieznana_wersje_i_przekazuje_parametry() -> None:
    with pytest.raises(NieznanyModelPrognoz):
        backtest().uruchom("xyz")
    katalog = KatalogModeliPrognoz(
        [
            DefinicjaModeluPrognoz(
                OpisModeluPrognoz("test_v9", "Test"),
                KonfiguracjaSilyDruzyn(wersja_modelu="test_v9", przewaga_wlasnego_parkietu=0),
            )
        ]
    )
    wynik = backtest(katalog=katalog).uruchom("test_v9")
    assert wynik.prognozy[0].wersja_modelu == "test_v9"
    assert wynik.prognozy[0].prognoza.roznica_ratingow == 0


def test_raport_filtruje_stronicuje_i_podsumowuje() -> None:
    serwis = raport()
    calosc = serwis.pobierz_raport(FiltryPrognoz())
    assert calosc.strona.liczba_wszystkich == 3
    assert [p.mecz.id_mecz for p in calosc.strona.pozycje] == [203, 202, 201]
    assert calosc.podsumowanie.liczba == 3
    assert calosc.podsumowanie.trafnosc == pytest.approx(calosc.podsumowanie.trafione / 3)
    assert calosc.podsumowanie.mediana_bledu_wyniku is not None
    assert [s.nazwa for s in calosc.sezony] == ["2025/2026"]
    druzyna = serwis.pobierz_raport(FiltryPrognoz(druzyna="górnik"))
    assert [p.mecz.id_mecz for p in druzyna.strona.pozycje] == [201]
    strona = serwis.pobierz_raport(FiltryPrognoz(strona=9, rozmiar_strony=2))
    assert strona.strona.strona == 2 and len(strona.strona.pozycje) == 1
    assert serwis.pobierz_raport(FiltryPrognoz(plec=Plec.KOBIET)).podsumowanie.liczba == 0
    assert serwis.pobierz_raport(FiltryPrognoz(plec=Plec.KOBIET)).podsumowanie.trafnosc is None


def test_raport_filtruje_trafnosc_i_klase() -> None:
    serwis = raport()
    calosc = serwis.pobierz_raport(FiltryPrognoz())
    trafione = serwis.pobierz_raport(FiltryPrognoz(trafiony=True))
    nietrafione = serwis.pobierz_raport(FiltryPrognoz(trafiony=False))
    assert trafione.podsumowanie.liczba + nietrafione.podsumowanie.liczba == 3
    assert all(p.ocena.trafiony for p in trafione.strona.pozycje)
    klasa = calosc.strona.pozycje[0].ocena.klasa
    wg_klasy = serwis.pobierz_raport(FiltryPrognoz(klasy=frozenset({klasa})))
    assert {p.ocena.klasa for p in wg_klasy.strona.pozycje} == {klasa}
    inna = next(
        k for k in KlasaTrafnosci if k not in {p.ocena.klasa for p in calosc.strona.pozycje}
    )
    assert (
        serwis.pobierz_raport(FiltryPrognoz(klasy=frozenset({inna}))).strona.liczba_wszystkich == 0
    )
    obie = serwis.pobierz_raport(FiltryPrognoz(klasy=frozenset({klasa, inna})))
    assert obie.strona.liczba_wszystkich == wg_klasy.strona.liczba_wszystkich


def test_raport_odrzuca_sezon_spoza_zakresu() -> None:
    with pytest.raises(ValueError):
        raport().pobierz_raport(FiltryPrognoz(id_sezon=4))


def test_podsumowanie_liczy_progi_score_error() -> None:
    podsumowanie = raport().pobierz_raport(FiltryPrognoz()).podsumowanie
    assert [licznik.prog for licznik in podsumowanie.progi] == [2.0, 4.0, 6.0]
    assert all(
        a.liczba <= b.liczba
        for a, b in zip(podsumowanie.progi, podsumowanie.progi[1:], strict=False)
    )


def test_szczegoly_zwracaja_snapshot_i_historie_druzyn() -> None:
    serwis = SzczegolyPrognozyService(backtest(), KatalogModeliPrognoz())
    szczegoly = serwis.pobierz("team_strength_v1", 203)
    assert szczegoly.prognoza.mecz.id_mecz == 203
    assert szczegoly.model.nazwa == "Dynamic Team Strength V1"
    assert [p.mecz.id_mecz for p in szczegoly.historia_gospodarza] == [202, 102, 101]
    assert [p.mecz.id_mecz for p in szczegoly.historia_goscia] == [201, 102, 101]
    rozgrzewka = serwis.pobierz("team_strength_v1", 101)
    assert not rozgrzewka.prognoza.w_raporcie and rozgrzewka.historia_gospodarza == ()
    with pytest.raises(NieZnalezionoPrognozy):
        serwis.pobierz("team_strength_v1", 999)


def test_raport_filtruje_ocene_wyniku_prezentowanego_i_ja_podsumowuje() -> None:
    serwis = raport()
    calosc = serwis.pobierz_raport(FiltryPrognoz())
    oceny = [p.ocena for p in calosc.strona.pozycje]
    assert calosc.podsumowanie.dokladne_wyniki == sum(o.dokladny_wynik for o in oceny)
    assert calosc.podsumowanie.poprawne_roznice == sum(o.poprawna_roznica for o in oceny)
    assert calosc.podsumowanie.roznice_do_1 == sum(o.blad_roznicy_prezentowanej <= 1 for o in oceny)
    roznica = serwis.pobierz_raport(FiltryPrognoz(tylko_poprawna_roznica=True))
    assert all(p.ocena.poprawna_roznica for p in roznica.strona.pozycje)
    assert roznica.strona.liczba_wszystkich == calosc.podsumowanie.poprawne_roznice
    dokladne = serwis.pobierz_raport(FiltryPrognoz(tylko_dokladny_wynik=True))
    assert dokladne.strona.liczba_wszystkich == calosc.podsumowanie.dokladne_wyniki
    klasy = {o.klasa_wyniku for o in oceny}
    wybrane = serwis.pobierz_raport(FiltryPrognoz(klasy_wyniku=frozenset(klasy)))
    assert wybrane.strona.liczba_wszystkich == 3
    brak = next(k for k in KlasaWyniku if k not in klasy)
    assert (
        serwis.pobierz_raport(FiltryPrognoz(klasy_wyniku=frozenset({brak}))).podsumowanie.liczba
        == 0
    )


def test_raport_filtruje_kierunek_i_wynik_1x2() -> None:
    serwis = raport()
    calosc = serwis.pobierz_raport(FiltryPrognoz())
    poprawne = serwis.pobierz_raport(FiltryPrognoz(poprawny_typ_prognozy=True))
    bledne = serwis.pobierz_raport(FiltryPrognoz(poprawny_typ_prognozy=False))
    assert poprawne.strona.liczba_wszystkich == calosc.podsumowanie.poprawne_typy_prognozy
    assert poprawne.strona.liczba_wszystkich + bledne.strona.liczba_wszystkich == 3
    assert all(not p.ocena.poprawny_typ_prognozy for p in bledne.strona.pozycje)
    remisy = serwis.pobierz_raport(FiltryPrognoz(typy_wyniku=frozenset({Typ1X2.REMIS})))
    assert [p.mecz.id_mecz for p in remisy.strona.pozycje] == [203]
    bez_remisow = serwis.pobierz_raport(
        FiltryPrognoz(typy_wyniku=frozenset({Typ1X2.GOSPODARZ, Typ1X2.GOSC}))
    )
    assert [p.mecz.id_mecz for p in bez_remisow.strona.pozycje] == [202, 201]


@pytest.mark.parametrize(
    ("nazwa", "poziom"),
    [
        ("PGNiG Superliga Mężczyzn", PoziomRozgrywek.SUPERLIGA),
        ("Baraż o ORLEN Superligę Kobiet", PoziomRozgrywek.SUPERLIGA),
        ("Ekstraklasa Kobiet", PoziomRozgrywek.SUPERLIGA),
        ("Liga Centralna", PoziomRozgrywek.LIGA_CENTRALNA),
        ("Liga Centralna Mężczyzn", PoziomRozgrywek.LIGA_CENTRALNA),
        ("I Liga Mężczyzn Grupa A", PoziomRozgrywek.I_LIGA),
        ("I Liga Kobiet - Rozgrywki Finałowe", PoziomRozgrywek.I_LIGA),
        ("i  liga kobiet", PoziomRozgrywek.I_LIGA),
        ("II Liga Mężczyzn gr. 1", None),
        ("II liga Mężczyzn gr. III A", None),
        ("Pomorska II LIGA  Grupa A", None),
        ("III Liga Mężczyzn", None),
        ("Śląska III Liga Kobiet", None),
        ("Baraż o Ligę Centralną Mężczyzn", None),
        ("ORLEN Puchar Polski Kobiet", None),
        (None, None),
    ],
)
def test_wzorce_rozpoznaja_poziom_rozgrywek(
    nazwa: str | None, poziom: PoziomRozgrywek | None
) -> None:
    assert WzorceNazwLig().poziom(nazwa) == poziom


def test_kazda_liga_ma_osobny_model_i_filtr_poziomu() -> None:
    mecze = [
        mecz_ligowy(1, datetime(2025, 9, 1), 10, 20, 40, 20),
        mecz_ligowy(
            2, datetime(2025, 9, 2), 10, 20, 30, 28, nazwa_rozgrywek="I Liga Mężczyzn Grupa A"
        ),
        mecz_ligowy(
            3, datetime(2025, 9, 3), 10, 20, 30, 28, nazwa_rozgrywek="Liga Centralna Mężczyzn"
        ),
        mecz_ligowy(
            4, datetime(2025, 9, 4), 10, 20, 30, 28, nazwa_rozgrywek="II Liga Mężczyzn gr. 1"
        ),
        mecz_ligowy(
            5,
            datetime(2025, 9, 5),
            10,
            20,
            30,
            28,
            nazwa_rozgrywek="I Liga Kobiet Grupa A",
            plec="K",
        ),
    ]
    wynik = backtest(mecze).uruchom("team_strength_v1")
    prognozy = {p.mecz.id_mecz: p for p in wynik.prognozy}
    assert set(prognozy) == {1, 2, 3, 5}
    assert wynik.wykluczenia == {PowodWykluczenia.NIEZNANA_LIGA: 1}
    assert prognozy[2].mecz.liga == Liga(PoziomRozgrywek.I_LIGA, Plec.MEZCZYZN)
    assert prognozy[5].mecz.liga == Liga(PoziomRozgrywek.I_LIGA, Plec.KOBIET)
    for id_mecz in (2, 3, 5):
        assert prognozy[id_mecz].stan.gospodarz.rating == prognozy[1].stan.gospodarz.rating
        assert prognozy[id_mecz].stan.oczekiwana_suma_ligi == prognozy[1].stan.oczekiwana_suma_ligi
    serwis = raport(mecze)
    assert (
        serwis.pobierz_raport(FiltryPrognoz(poziom=PoziomRozgrywek.I_LIGA)).strona.liczba_wszystkich
        == 2
    )
    assert (
        serwis.pobierz_raport(
            FiltryPrognoz(poziom=PoziomRozgrywek.I_LIGA, plec=Plec.KOBIET)
        ).strona.liczba_wszystkich
        == 1
    )
