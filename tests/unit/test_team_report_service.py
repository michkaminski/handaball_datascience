import pytest
from tests.helpers.schedule import ZegarTestowy
from tests.helpers.team_details import SzczegolyDruzynyInMemoryRepository
from tests.helpers.team_reports import KadraRaportuInMemoryRepository

from handball.domain.match_rules import MeczPolicy
from handball.domain.team_details import (
    FiltryZawodnikowDruzyny,
    KolejnoscPozycjiPolicy,
    StronaZawodnikowDruzyny,
    WystepDruzynyPolicy,
)
from handball.domain.team_report import KolejnoscZawodnikowRaportuPolicy
from handball.services.team_detail_service import (
    BilansDruzynyCalculator,
    FrekwencjaDruzynyCalculator,
    ZestawienieDruzynyService,
)
from handball.services.team_report_service import RaportDruzynyService


class DruzynaBezProtokolow(SzczegolyDruzynyInMemoryRepository):
    def pobierz_zawodnikow(
        self, id_zespol: int, filtry: FiltryZawodnikowDruzyny
    ) -> StronaZawodnikowDruzyny:
        return StronaZawodnikowDruzyny([], 0, 1, 20)


def serwis(
    druzyny: SzczegolyDruzynyInMemoryRepository | None = None,
    kadry: KadraRaportuInMemoryRepository | None = None,
) -> RaportDruzynyService:
    repozytorium = druzyny or SzczegolyDruzynyInMemoryRepository()
    reguly = WystepDruzynyPolicy(MeczPolicy())
    return RaportDruzynyService(
        repozytorium,
        kadry or KadraRaportuInMemoryRepository(),
        ZestawienieDruzynyService(repozytorium, reguly, KolejnoscPozycjiPolicy()),
        BilansDruzynyCalculator(FrekwencjaDruzynyCalculator()),
        reguly,
        KolejnoscZawodnikowRaportuPolicy(KolejnoscPozycjiPolicy()),
        ZegarTestowy(),
    )


def test_raport_laczy_kadre_ze_statystykami_i_poprzednim_sezonem() -> None:
    raport = serwis().pobierz_raport(272, 195)
    assert [z.id_zawodnik for z in raport.zawodnicy] == [8, 7]
    jan = raport.zawodnicy[1]
    assert jan.numery == (9,) and jan.sezon is not None and jan.sezon.karne_liczba == 3
    assert jan.poprzedni.mecze == 12 and jan.poprzedni.bramki == 34
    assert raport.poprzedni_sezon == "2025/2026"
    assert not raport.ze_skladu


def test_raport_bez_protokolow_bierze_sklad_zgloszony() -> None:
    kadry = KadraRaportuInMemoryRepository(kadry={})
    raport = serwis(DruzynaBezProtokolow(), kadry).pobierz_raport(272, 193)
    assert raport.ze_skladu
    assert [z.nazwisko for z in raport.zawodnicy] == ["Zgłoszony"]
    assert kadry.sklady == [(272, 193)]


def test_raport_pomija_sezony_pozniejsze_niz_wybrany() -> None:
    raport = serwis().pobierz_raport(272, 194)
    assert [b.sezon for b in raport.sezony] == ["2025/2026", "2024/2025"]
    assert all(m.wystep.sezon != "2026/2027" for m in raport.mecze)


def test_ostatnie_mecze_od_najnowszego_z_limitem_i_strzelcami() -> None:
    raport = serwis().pobierz_raport(272, 195, liczba_meczow=2)
    assert [m.wystep.id_mecz for m in raport.mecze] == [3, 2]
    assert raport.mecze[0].strzelcy[0].nazwisko == "J. Testowy"
    assert raport.mecze[0].karne_liczba == 1


def test_sezon_spoza_druzyny_to_blad() -> None:
    with pytest.raises(ValueError):
        serwis().pobierz_raport(272, 7)


def test_zestawienia_maja_sezon_i_poprzedni_z_rocznikami() -> None:
    zestawienia = serwis().pobierz_zestawienia(272, 195)
    assert [s.sezon for s in zestawienia.strony] == ["2026/2027", "2025/2026"]
    assert zestawienia.strony[0].roczniki[7].year == 1999
    assert zestawienia.strony[0].zestawienie is not None
