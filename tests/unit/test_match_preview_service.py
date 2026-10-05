from datetime import datetime

import pytest
from tests.helpers.match_predictions import (
    MeczeLigoweInMemoryRepository,
    mecz_ligowy,
    mecze_dwoch_sezonow,
)
from tests.helpers.schedule import (
    KADRY,
    SKLADY,
    WYSTEPY,
    WYSTEPY_ZAWODNIKOW,
    ZapowiedzMeczuInMemoryRepository,
    mecz_zapowiedzi,
    wystep,
)

from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.match_predictions import (
    KwalifikacjaMeczuPolicy,
    MeczLigowy,
    OcenaPrognozyPolicy,
    OpisModeluPrognoz,
    PowodWykluczenia,
    ProgiTrafnosci,
    PrognozaZapowiedzi,
    Typ1X2,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.domain.match_preview import (
    Bilans,
    DruzynaZapowiedzi,
    KadraDruzyny,
    KadraZapowiedziCalculator,
    KlubPoprzedniegoSezonu,
    OpcjeZapowiedzi,
    PoprzedniSezonZawodnika,
    RezultatDruzyny,
    StatystykiZapowiedziCalculator,
    ZawodnikKadry,
)
from handball.domain.team_details import KolejnoscPozycjiPolicy
from handball.domain.team_strength_model import ModelSilyDruzyn
from handball.services.match_prediction_service import (
    BacktestPrognozService,
    KatalogModeliPrognoz,
    PodzialSezonowPolicy,
    PrognozaZapowiedziService,
)
from handball.services.match_preview_service import ZapowiedzMeczuService


class ZegarStaly:
    def __init__(self, chwila: datetime) -> None:
        self.chwila = chwila

    def teraz(self) -> datetime:
        return self.chwila


class PrognozyStale:
    def __init__(self) -> None:
        self.wywolania: list[tuple[str, int]] = []

    def pobierz(self, wersja_modelu: str, id_mecz: int) -> PrognozaZapowiedzi:
        self.wywolania.append((wersja_modelu, id_mecz))
        return PrognozaZapowiedzi(OpisModeluPrognoz(wersja_modelu, "Model"))


def prognozy_zapowiedzi(mecze: list[MeczLigowy] | None = None) -> PrognozaZapowiedziService:
    wzorce = WzorceNazwLig()
    katalog = KatalogModeliPrognoz()
    kwalifikacja = KwalifikacjaMeczuPolicy(wzorce)
    backtest = BacktestPrognozService(
        MeczeLigoweInMemoryRepository(mecze),
        katalog,
        kwalifikacja,
        OcenaPrognozyPolicy(ProgiTrafnosci()),
        PodzialSezonowPolicy(ZakresBacktestu()),
        wzorce,
    )
    return PrognozaZapowiedziService(backtest, katalog, kwalifikacja)


def serwis(
    repo: ZapowiedzMeczuInMemoryRepository, prognozy: PrognozyStale, zegar: ZegarStaly
) -> ZapowiedzMeczuService:
    return ZapowiedzMeczuService(
        repo,
        StatystykiZapowiedziCalculator(),
        KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy()),
        prognozy,
        zegar,
    )


def test_bilans_i_rezultat_z_perspektywy_druzyny() -> None:
    wystepy = tuple(WYSTEPY[10])
    bilans = Bilans.z_wystepow(wystepy)
    assert (bilans.mecze, bilans.wygrane, bilans.remisy, bilans.porazki) == (3, 1, 1, 1)
    assert (bilans.bramki_zdobyte, bilans.bramki_stracone, bilans.roznica) == (82, 80, 2)
    assert wystepy[2].rezultat is RezultatDruzyny.PORAZKA
    assert Bilans.z_wystepow(()).srednia_zdobytych is None


def test_profil_forma_od_najnowszych_i_bilans_tylko_z_rozgrywek() -> None:
    kalkulator = StatystykiZapowiedziCalculator()
    profil = kalkulator.profil(
        DruzynaZapowiedzi(30, "Górnik Zabrze"),
        tuple(WYSTEPY[30]),
        501,
        True,
        KadraDruzyny(DruzynaZapowiedzi(30, "Górnik Zabrze"), ()),
    )
    assert [w.id_mecz for w in profil.forma] == [201, 90, 103]
    assert profil.bilans_rozgrywek.mecze == 2
    assert profil.bilans_miejsca.mecze == 1 and profil.bilans_miejsca.remisy == 1
    assert profil.mediana_zdobytych == 26.5
    assert profil.seria is not None and profil.seria.rezultat is RezultatDruzyny.PORAZKA


def test_seria_liczy_kolejne_takie_same_rezultaty() -> None:
    wystepy = tuple(
        wystep(i, datetime(2025, 9, i, 18), 10, 20, "X", 30, 20 + (i == 1) * 20)
        for i in range(1, 5)
    )
    seria = StatystykiZapowiedziCalculator().seria(tuple(reversed(wystepy)))
    assert seria is not None and (seria.rezultat, seria.dlugosc) == (RezultatDruzyny.WYGRANA, 3)


def test_bezposrednie_mecze_gospodarza_z_gosciem() -> None:
    h2h = StatystykiZapowiedziCalculator().bezposrednie(tuple(WYSTEPY[30]), 10)
    assert [w.id_mecz for w in h2h.mecze] == [201]
    assert h2h.bilans.porazki == 1
    assert StatystykiZapowiedziCalculator().bezposrednie(tuple(WYSTEPY[30]), None).mecze == ()


def test_mecz_zapowiedzi_uwzglednia_zamiane_stron() -> None:
    mecz = mecz_zapowiedzi(wynik=(24, 35), zamiana=True)
    assert mecz.gospodarz.nazwa == "Wisła Płock" and mecz.gosc.nazwa == "Górnik Zabrze"
    assert (mecz.bramki_gospodarza, mecz.bramki_goscia) == (35, 24)
    assert mecz.rozegrany


def test_serwis_liczy_statystyki_sprzed_terminu_meczu() -> None:
    repo = ZapowiedzMeczuInMemoryRepository()
    prognozy = PrognozyStale()
    zapowiedz = serwis(repo, prognozy, ZegarStaly(datetime(2030, 1, 1))).pobierz(
        204, "team_strength_v1"
    )
    assert zapowiedz.stan_na == datetime(2025, 9, 22, 18)
    assert {przed for _, przed in repo.odczyty} == {datetime(2025, 9, 22, 18)}
    assert zapowiedz.gosc.kadra.liczba_zawodnikow == 4
    assert repo.kadry == [(30, 5, datetime(2025, 9, 22, 18)), (10, 5, datetime(2025, 9, 22, 18))]
    assert zapowiedz.gosc.bilans_miejsca.mecze == 1
    assert [w.id_mecz for w in zapowiedz.bezposrednie.mecze] == [201]
    assert prognozy.wywolania == [("team_strength_v1", 204)]


def test_serwis_bez_terminu_uzywa_biezacej_chwili() -> None:
    repo = ZapowiedzMeczuInMemoryRepository([mecz_zapowiedzi(data=None)])
    chwila = datetime(2025, 9, 10, 12)
    zapowiedz = serwis(repo, PrognozyStale(), ZegarStaly(chwila)).pobierz(204, "team_strength_v1")
    assert zapowiedz.stan_na == chwila
    assert [w.id_mecz for w in zapowiedz.gosc.forma] == [201, 88]


def test_prognoza_zakonczonego_meczu_jest_taka_jak_w_raporcie() -> None:
    wynik = prognozy_zapowiedzi().pobierz("team_strength_v1", 203)
    assert wynik.biezaca is None and wynik.po_meczu is not None
    assert wynik.po_meczu.mecz.id_mecz == 203


def test_prognoza_nierozegranego_meczu_ze_stanu_modelu_po_wszystkich_wynikach() -> None:
    mecze = [
        *mecze_dwoch_sezonow(),
        mecz_ligowy(204, datetime(2025, 9, 22, 18), 30, 10, None, None),
    ]
    wynik = prognozy_zapowiedzi(mecze).pobierz("team_strength_v1", 204)
    assert wynik.po_meczu is None and wynik.biezaca is not None
    biezaca = wynik.biezaca
    assert biezaca.mecz.gospodarz.nazwa == "Górnik Zabrze"
    assert biezaca.liczba_meczow_ligi == 6
    assert biezaca.ostatni_mecz_ligi == datetime(2025, 9, 15, 18)
    model = ModelSilyDruzyn(KatalogModeliPrognoz().definicja("team_strength_v1").konfiguracja)
    for mecz in sorted(
        (KwalifikacjaMeczuPolicy(WzorceNazwLig()).do_prognozy(m) for m in mecze_dwoch_sezonow()),
        key=lambda m: m.klucz_chronologii,
    ):
        model.aktualizuj(mecz, model.prognozuj(model.stan_przed_meczem(mecz)))
    assert biezaca.stan.gospodarz.rating == pytest.approx(model.rating(30))
    assert biezaca.stan.gosc.rating == pytest.approx(model.rating(10))
    assert biezaca.prognoza.typ is Typ1X2.REMIS


def test_prognoza_nierozegranego_meczu_z_zamiana_i_nowa_druzyna() -> None:
    mecze = [
        *mecze_dwoch_sezonow(),
        mecz_ligowy(205, datetime(2025, 10, 1, 18), 10, 99, None, None, zamiana=True),
    ]
    biezaca = prognozy_zapowiedzi(mecze).pobierz("team_strength_v1", 205).biezaca
    assert biezaca is not None
    assert biezaca.mecz.gospodarz.id_zespol == 99
    assert biezaca.stan.gospodarz.nowa_druzyna


@pytest.mark.parametrize(
    ("mecz", "powod"),
    [
        (
            mecz_ligowy(206, datetime(2025, 10, 1), 10, 20, None, None, walkower=True),
            PowodWykluczenia.WALKOWER,
        ),
        (
            mecz_ligowy(207, datetime(2025, 10, 1), 10, None, None, None),
            PowodWykluczenia.BRAK_GOSCIA,
        ),
        (
            mecz_ligowy(208, None, 10, 20, 30, 20),
            PowodWykluczenia.BRAK_DATY,
        ),
    ],
)
def test_brak_prognozy_ma_powod(mecz: MeczLigowy, powod: PowodWykluczenia) -> None:
    wynik = prognozy_zapowiedzi([*mecze_dwoch_sezonow(), mecz]).pobierz(
        "team_strength_v1", mecz.id_mecz
    )
    assert wynik.po_meczu is None and wynik.biezaca is None
    assert wynik.powod_braku is powod


def test_mecz_spoza_lig_modelu_nie_ma_prognozy() -> None:
    wynik = prognozy_zapowiedzi().pobierz("team_strength_v1", 999)
    assert wynik.powod_braku is PowodWykluczenia.NIEZNANA_LIGA


def test_kadra_bramkarze_na_gorze_potem_pozycje() -> None:
    kadra = KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy()).kadra(
        DruzynaZapowiedzi(10, "Wisła Płock"), KADRY[(10, 5)]
    )
    assert [(g.kolejnosc, [c.id_zawodnik for c in g.czlonkowie]) for g in kadra.grupy] == [
        (0, [1]),
        (1, [7]),
        (2, [9]),
        (5, [5]),
    ]
    assert kadra.grupy[0].czlonkowie[0].numery == (1, 12)
    assert all(c.poprzedni_sezon is None for g in kadra.grupy for c in g.czlonkowie)


def test_kadra_poprzedni_sezon_z_innych_klubow_i_lig() -> None:
    kadra = KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy()).kadra(
        DruzynaZapowiedzi(10, "Wisła Płock"),
        KADRY[(10, 5)],
        KADRY[(10, 4)],
        WYSTEPY_ZAWODNIKOW[4],
        "ORLEN Superliga",
    )
    czlonkowie = {c.id_zawodnik: c for g in kadra.grupy for c in g.czlonkowie}
    kowalski, nowak, lis, stary = (czlonkowie[i] for i in (7, 1, 9, 3))
    assert kowalski.poprzedni_sezon == PoprzedniSezonZawodnika(3, 20)
    assert nowak.poprzedni_sezon is not None
    assert nowak.poprzedni_sezon.inne_kluby == (KlubPoprzedniegoSezonu("Industria Kielce", 4, 1),)
    assert nowak.poprzedni_sezon.inne_ligi == ()
    assert lis.poprzedni_sezon == PoprzedniSezonZawodnika(
        6, 36, (KlubPoprzedniegoSezonu("KPR Legionowo", 6, 36),), ("I Liga Mężczyzn Grupa A",)
    )
    assert lis.poprzedni_sezon.srednia == 6.0
    assert stary.sezon is None and stary.pozycja == "Obrotowy"
    assert stary.poprzedni_sezon == PoprzedniSezonZawodnika(
        4, 6, (KlubPoprzedniegoSezonu("Górnik Zabrze", 2, 5),), (), tylko_druzyna=True
    )
    assert not kowalski.poprzedni_sezon.tylko_druzyna
    assert czlonkowie[5].poprzedni_sezon is None
    assert kowalski.srednia == 6.5 and stary.srednia is None
    assert 4 not in czlonkowie
    assert kadra.liczba_zawodnikow == 5


def test_serwis_pobiera_kadre_poprzedniego_sezonu_tylko_na_zyczenie() -> None:
    repo = ZapowiedzMeczuInMemoryRepository()
    zapowiedz = serwis(repo, PrognozyStale(), ZegarStaly(datetime(2030, 1, 1))).pobierz(
        204, "team_strength_v1"
    )
    assert {sezon for _, sezon, _ in repo.kadry} == {5}
    assert zapowiedz.gosc.kadra.liczba_zawodnikow == 4
    assert (tuple(sorted(repo.wystepy_zawodnikow[1][0])), repo.wystepy_zawodnikow[1][1]) == (
        (1, 5, 7, 9),
        4,
    )
    repo = ZapowiedzMeczuInMemoryRepository()
    zapowiedz = serwis(repo, PrognozyStale(), ZegarStaly(datetime(2030, 1, 1))).pobierz(
        204, "team_strength_v1", OpcjeZapowiedzi(kadra_z_poprzedniego_sezonu=True)
    )
    assert {sezon for _, sezon, _ in repo.kadry} == {5, 4}
    assert zapowiedz.sezon_poprzedni is not None and zapowiedz.sezon_poprzedni.nazwa == "2024/2025"
    assert zapowiedz.gosc.kadra.liczba_zawodnikow == 5


def test_bezposrednie_z_okresu_lat_bez_limitu_liczby() -> None:
    kalkulator = StatystykiZapowiedziCalculator()
    wystepy = tuple(
        wystep(100 + i, datetime(2010 + i, 3, 1, 18), 30, 10, "Wisła Płock", 25, 20 + i)
        for i in range(15)
    )
    od = kalkulator.poczatek_okresu(datetime(2025, 9, 22, 18), 10)
    assert od == datetime(2015, 9, 22, 18)
    h2h = kalkulator.bezposrednie(wystepy, 10, od)
    assert len(h2h.mecze) == 9 and h2h.bilans.mecze == 9 and h2h.od == od
    assert len(kalkulator.bezposrednie(wystepy, 10, None).mecze) == 15
    assert kalkulator.poczatek_okresu(datetime(2024, 2, 29), 1) == datetime(2023, 2, 28)
    assert kalkulator.poczatek_okresu(datetime(2024, 2, 29), None) is None


def test_opcje_zapowiedzi_odrzucaja_niedodatnie_lata() -> None:
    with pytest.raises(ValueError):
        OpcjeZapowiedzi(lata_bezposrednich=0)


def test_miejsca_strzelcow_piec_najlepszych_z_ex_aequo_bez_zer() -> None:
    kalkulator = KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy())
    zawodnicy = [
        ZawodnikKadry(i, None, f"Z{i}", (), "Rozgrywający", 3, bramki)
        for i, bramki in enumerate((20, 15, 15, 10, 9, 9, 8, 0), start=1)
    ]
    assert kalkulator.miejsca_strzelcow(zawodnicy) == {1: 1, 2: 2, 3: 2, 4: 4, 5: 5, 6: 5}
    assert kalkulator.miejsca_strzelcow([ZawodnikKadry(9, None, "Z", (), None, 1, 0)]) == {}


def test_zawodnik_zagral_wedlug_wyjsc_na_boisko() -> None:
    assert ZawodnikKadry(1, None, None, (), None, 2, 0, zagrane=1).zagral
    assert not ZawodnikKadry(1, None, None, (), None, 2, 0, zagrane=0).zagral
    assert ZawodnikKadry(1, None, None, (), None, 2, 0).zagral


def test_kadra_bez_protokolow_w_sezonie_ze_skladu_zgloszonego() -> None:
    repo = ZapowiedzMeczuInMemoryRepository(
        [mecz_zapowiedzi(999, gosp=(501, "Klub Spoza Ligi"), gosc=(502, "Inny Klub"))]
    )
    zapowiedz = serwis(repo, PrognozyStale(), ZegarStaly(datetime(2030, 1, 1))).pobierz(
        999, "team_strength_v1"
    )
    kadra = zapowiedz.gospodarz.kadra
    assert kadra.ze_skladu
    assert [[c.id_zawodnik for c in g.czlonkowie] for g in kadra.grupy] == [[62], [61], [63]]
    assert kadra.grupy[0].czlonkowie[0].numery == (16,)
    assert not zapowiedz.gosc.kadra.ze_skladu and zapowiedz.gosc.kadra.liczba_zawodnikow == 0
    assert repo.sklady == [(501, 5), (502, 5)]


def test_kadra_z_protokolow_nie_siega_do_skladu() -> None:
    repo = ZapowiedzMeczuInMemoryRepository()
    zapowiedz = serwis(repo, PrognozyStale(), ZegarStaly(datetime(2030, 1, 1))).pobierz(
        204, "team_strength_v1"
    )
    assert not zapowiedz.gosc.kadra.ze_skladu
    assert 64 not in {c.id_zawodnik for g in zapowiedz.gosc.kadra.grupy for c in g.czlonkowie}
    assert (10, 5) not in repo.sklady and SKLADY[(10, 5)]


def test_kadra_w_grupie_wedlug_numeru_potem_nazwiska_bez_numeru_na_koncu() -> None:
    zawodnicy = [
        ZawodnikKadry(1, "Adam", "Zet", (20,), "Rozgrywający", 9, 40),
        ZawodnikKadry(2, "Bartosz", "Bez", (), "Rozgrywający", 9, 40),
        ZawodnikKadry(3, "Cezary", "Ymir", (3, 33), "Rozgrywający", 1, 0),
        ZawodnikKadry(4, "Dawid", "Alfa", (20,), "Rozgrywający", 2, 1),
    ]
    kadra = KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy()).kadra(
        DruzynaZapowiedzi(10, "Wisła Płock"), zawodnicy
    )
    assert [c.id_zawodnik for c in kadra.grupy[0].czlonkowie] == [3, 4, 1, 2]
