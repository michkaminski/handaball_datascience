from __future__ import annotations

from datetime import datetime

import pytest
from tests.helpers.match_repository import MeczInMemoryRepository

from handball.domain.errors import NieZnalezionoMeczu
from handball.domain.matches import DaneMeczu, FiltryMeczow, PozycjaListyMeczow, SzczegolyMeczu
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
            mecz=DaneMeczu(id=1, wynik_gosp_full=32, wynik_gosc_full=28),
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


def test_pobierz_szczegoly_deleguje_do_repozytorium() -> None:
    szczegoly = SzczegolyMeczu(mecz=DaneMeczu(id=1))
    serwis = MeczService(MeczInMemoryRepository(szczegoly={1: szczegoly}))

    assert serwis.pobierz_szczegoly(1) == szczegoly


def test_pobierz_szczegoly_nieznanego_meczu_zglasza_wyjatek() -> None:
    serwis = MeczService(MeczInMemoryRepository())

    with pytest.raises(NieZnalezionoMeczu):
        serwis.pobierz_szczegoly(1)
