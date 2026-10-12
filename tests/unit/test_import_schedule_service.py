from tests.helpers.schedule import SezonyTerminarza, TerminarzInMemoryRepository, pozycje_terminarza

from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.schedule import FiltryPobierania, PozycjaTerminarza, WyborTerminarza
from handball.services.import_schedule_service import PobieranieMeczowService
from handball.services.schedule_service import TerminarzService


class MeczeDoPobrania:
    def __init__(self, wiersze: list[tuple[PozycjaTerminarza, bool]]) -> None:
        self.wiersze = wiersze
        self.filtry: list[FiltryPobierania] = []

    def pobierz(self, filtry: FiltryPobierania) -> list[tuple[PozycjaTerminarza, bool]]:
        self.filtry.append(filtry)
        return self.wiersze


def serwis(
    wiersze: list[tuple[PozycjaTerminarza, bool]],
) -> tuple[PobieranieMeczowService, MeczeDoPobrania]:
    terminarz = TerminarzService(
        TerminarzInMemoryRepository(), SezonyTerminarza(), KolejnoscRozgrywekPolicy()
    )
    mecze = MeczeDoPobrania(wiersze)
    return PobieranieMeczowService(terminarz, mecze), mecze


def identyfikatory(
    usluga: PobieranieMeczowService, wybor: WyborTerminarza, wynik: bool, kolejki: bool
) -> list[int]:
    terminarz = usluga.pobierz(wybor, wynik, kolejki)
    assert terminarz is not None
    return [
        mecz.id_mecz
        for runda in terminarz.rundy
        for kolejka in runda.kolejki
        for dzien in kolejka.dni
        for mecz in dzien.mecze
    ]


def test_bez_sezonu_albo_bez_rozgrywek_i_filtra_nie_ma_listy() -> None:
    usluga, mecze = serwis([])
    assert usluga.pobierz(WyborTerminarza(), False, False) is None
    assert usluga.pobierz(WyborTerminarza(5), False, False) is None
    assert mecze.filtry == []


def test_wynik_bez_danych_zostawia_mecze_oznaczone_do_aktualizacji() -> None:
    wiersze = [(pozycja, pozycja.id_mecz == 201) for pozycja in pozycje_terminarza()]
    usluga, mecze = serwis(wiersze)
    assert identyfikatory(usluga, WyborTerminarza(5, 501), True, False) == [201]
    assert mecze.filtry == [FiltryPobierania(5, 501)]


def test_kolejki_zakonczone_pomijaja_kolejke_z_meczem_zaplanowanym() -> None:
    wiersze = [(pozycja, False) for pozycja in pozycje_terminarza()]
    usluga, _mecze = serwis(wiersze)
    terminarz = usluga.pobierz(WyborTerminarza(5), False, True)
    assert terminarz is not None
    assert [kolejka.nazwa for runda in terminarz.rundy for kolejka in runda.kolejki] == ["Seria 1"]


def test_oba_filtry_zostawiaja_braki_tylko_w_zakonczonych_kolejkach() -> None:
    wiersze = [(pozycja, pozycja.id_mecz in {201, 204}) for pozycja in pozycje_terminarza()]
    usluga, _mecze = serwis(wiersze)
    assert identyfikatory(usluga, WyborTerminarza(5), True, True) == [201]
