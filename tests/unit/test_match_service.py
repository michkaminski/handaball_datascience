from __future__ import annotations

from datetime import datetime

from tests.helpers.match_repository import MeczInMemoryRepository

from handball.domain.matches import FiltryMeczow, PozycjaListyMeczow
from handball.services.match_service import MeczService


def test_pobierz_liste_deleguje_do_repozytorium() -> None:
    pozycje = [
        PozycjaListyMeczow(
            id_mecz=1,
            termin=datetime(2026, 9, 12, 18, 0),
            sezon="2026/2027",
            rozgrywki="ORLEN Superliga",
            gospodarz="Industria Kielce",
            gosc="Orlen Wisła Płock",
            wynik="32 : 28",
            hala="Hala Legionów",
        ),
    ]
    repozytorium = MeczInMemoryRepository(pozycje)
    serwis = MeczService(repozytorium)

    strona = serwis.pobierz_liste(FiltryMeczow(id_sezon=195))

    assert strona.liczba_wszystkich == 1
    assert strona.pozycje == pozycje


def test_pobierz_liste_dla_pustego_repozytorium() -> None:
    serwis = MeczService(MeczInMemoryRepository())

    strona = serwis.pobierz_liste(FiltryMeczow(id_sezon=195))

    assert strona.liczba_wszystkich == 0
    assert strona.pozycje == []
