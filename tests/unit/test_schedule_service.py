from datetime import date

import pytest
from tests.helpers.schedule import TerminarzInMemoryRepository

from handball.domain.options import OpcjaWyboru
from handball.domain.schedule import FiltryTerminarza, WyborTerminarza
from handball.services.schedule_service import NieznanySezonTerminarza, TerminarzService


class SezonyInMemory:
    def pobierz_wszystkie(self) -> list[OpcjaWyboru]:
        return [OpcjaWyboru(5, "2025/2026"), OpcjaWyboru(4, "2024/2025")]


def serwis(repo: TerminarzInMemoryRepository | None = None) -> TerminarzService:
    return TerminarzService(repo or TerminarzInMemoryRepository(), SezonyInMemory())


def test_bez_wyboru_domyslny_jest_najnowszy_sezon_i_brak_filtrow() -> None:
    opcje = serwis().pobierz_opcje(WyborTerminarza())
    assert opcje.wybor == WyborTerminarza(5)
    assert [o.etykieta for o in opcje.rozgrywki] == ["ORLEN Superliga", "II Liga Mężczyzn"]
    assert opcje.rundy == [] and opcje.kolejki == []
    assert opcje.filtry is None


def test_nieznany_sezon_to_blad_wejscia() -> None:
    with pytest.raises(NieznanySezonTerminarza):
        serwis().pobierz_opcje(WyborTerminarza(id_sezon=99))


def test_nieaktualne_zalezne_wybory_sa_pomijane() -> None:
    opcje = serwis().pobierz_opcje(WyborTerminarza(4, 501, 11, 111))
    assert opcje.wybor == WyborTerminarza(4)
    opcje = serwis().pobierz_opcje(WyborTerminarza(5, 501, 99, 121))
    assert opcje.wybor == WyborTerminarza(5, 501, None, 121)
    opcje = serwis().pobierz_opcje(WyborTerminarza(5, 501, 11, 121))
    assert opcje.wybor == WyborTerminarza(5, 501, 11, None)
    assert [o.wartosc for o in opcje.kolejki] == [111, 112]


def test_filtry_wymagaja_sezonu_i_rozgrywek() -> None:
    opcje = serwis().pobierz_opcje(WyborTerminarza(5, 501, 12))
    assert opcje.filtry == FiltryTerminarza(5, 501, 12, None)
    assert [o.etykieta for o in opcje.kolejki] == ["Seria 3"]


def test_terminarz_grupuje_rundy_kolejki_i_dni_w_kolejnosci() -> None:
    terminarz = serwis().pobierz_terminarz(FiltryTerminarza(5, 501))
    assert terminarz.liczba_meczow == 5
    assert [r.nazwa for r in terminarz.rundy] == ["I runda", "II runda"]
    pierwsza = terminarz.rundy[0]
    assert [k.nazwa for k in pierwsza.kolejki] == ["Seria 1", "Seria 2"]
    dni = pierwsza.kolejki[0].dni
    assert [d.dzien for d in dni] == [date(2025, 9, 1), date(2025, 9, 2)]
    assert [m.id_mecz for m in dni[0].mecze] == [201, 202]
    assert terminarz.rundy[1].kolejki[0].dni[0].dzien == date(2026, 2, 7)


def test_filtr_kolejki_trafia_do_repozytorium() -> None:
    repo = TerminarzInMemoryRepository()
    terminarz = serwis(repo).pobierz_terminarz(FiltryTerminarza(5, 501, 11, 112))
    assert repo.filtry == [FiltryTerminarza(5, 501, 11, 112)]
    assert terminarz.liczba_meczow == 1
