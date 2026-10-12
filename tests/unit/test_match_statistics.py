from datetime import datetime
from typing import Any
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from tests.helpers.match_repository import MeczInMemoryRepository
from tests.helpers.match_statistics_repository import FormaMeczuInMemoryRepository

from handball.domain.errors import BladOdczytuDanych
from handball.domain.match_rules import MeczPolicy
from handball.domain.match_statistics import (
    FormaDruzyny,
    MeczFormy,
    RezultatFormy,
    StatystykiMeczuCalculator,
)
from handball.domain.matches import DaneMeczu, SzczegolyMeczu, ZawodnikMeczu
from handball.infrastructure.repositories.match_statistics_repository import (
    FormaMeczuSQLAlchemyRepository,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.presenters.match_statistics_presenter import StatystykiMeczuPresenter
from handball.services.match_statistics_service import StatystykiMeczuService


def mecz_formy(id_mecz: int, zdobyte: int, stracone: int, **pola: Any) -> MeczFormy:
    return MeczFormy(
        id_mecz=id_mecz,
        data=datetime(2026, 9, id_mecz, 18, 0),
        rywal=f"Rywal {id_mecz}",
        u_siebie=id_mecz % 2 == 1,
        bramki_zdobyte=zdobyte,
        bramki_stracone=stracone,
        **pola,
    )


def szczegoly(**pola: Any) -> SzczegolyMeczu:
    dane: dict[str, Any] = {
        "id": 10,
        "wynik_gosp_full": 30,
        "wynik_gosc_full": 27,
        "wynik_gosp_pol": 12,
        "wynik_gosc_pol": 15,
        "karne_bramki_gosp": 3,
        "karne_ile_gosp": 4,
        "karne_bramki_gosc": 2,
        "karne_ile_gosc": 2,
        "timeout1_gosp": "00:25:10",
        "id_zespol_gosp": 1,
        "id_zespol_gosc": 2,
    }
    dane.update(pola)
    return SzczegolyMeczu(
        mecz=DaneMeczu(**dane),
        nazwa_gospodarz="Gospodarze ",
        nazwa_gosc="Goście",
        sklad_gospodarz=[
            ZawodnikMeczu(zawodnik="Nowak", bramki=9, karne_bramki=3, dwie_minuty=1),
            ZawodnikMeczu(zawodnik="Lis", bramki=4, dwie_minuty=0),
        ],
        sklad_gosc=[
            ZawodnikMeczu(zawodnik="Wróbel", bramki=6, dwie_minuty=2),
            ZawodnikMeczu(zawodnik="Sowa", bramki=0, dwie_minuty=2),
        ],
    )


def serwis(
    repozytorium_formy: FormaMeczuInMemoryRepository, dane: SzczegolyMeczu
) -> StatystykiMeczuService:
    return StatystykiMeczuService(
        MeczInMemoryRepository(szczegoly={10: dane}),
        repozytorium_formy,
        StatystykiMeczuCalculator(MeczPolicy()),
        MeczPolicy(),
    )


def test_rozstrzygniecie_remisu_dogrywka_przed_seria() -> None:
    mecz = mecz_formy(1, 28, 28, dogrywka_zdobyte=33, dogrywka_stracone=31)
    assert mecz.rezultat is RezultatFormy.REMIS
    assert mecz.rozstrzygniecie is RezultatFormy.WYGRANA
    seria = mecz_formy(2, 28, 28, seria_zdobyte=3, seria_stracone=4)
    assert seria.rozstrzygniecie is RezultatFormy.PORAZKA
    assert mecz_formy(3, 30, 28).rozstrzygniecie is None


def test_forma_ostatnie_i_bilans() -> None:
    forma = FormaDruzyny(
        1, tuple(mecz_formy(i, 30, 30 - (i % 3 - 1)) for i in range(1, 8)), id_analizowany=7
    )
    assert [m.id_mecz for m in forma.ostatnie(5)] == [3, 4, 5, 6, 7]
    assert forma.bilans(5) == {
        RezultatFormy.WYGRANA: 1,
        RezultatFormy.REMIS: 2,
        RezultatFormy.PORAZKA: 2,
    }
    assert forma.ostatnie(0) == ()


def test_serwis_pobiera_forme_obu_druzyn_po_zamianie() -> None:
    repozytorium_formy = FormaMeczuInMemoryRepository({1: [mecz_formy(10, 27, 30)]})
    wynik = serwis(repozytorium_formy, szczegoly(zamiana=True)).pobierz(10)
    assert repozytorium_formy.zapytania == [(10, 2), (10, 1)]
    assert wynik.forma_gospodarza is not None and wynik.forma_gospodarza.id_zespol == 2
    assert wynik.forma_goscia is not None and len(wynik.forma_goscia.mecze) == 1
    assert wynik.gospodarz.nazwa == "Goście"


def test_serwis_bez_identyfikatora_druzyny_nie_pyta_o_forme() -> None:
    repozytorium_formy = FormaMeczuInMemoryRepository()
    wynik = serwis(repozytorium_formy, szczegoly(id_zespol_gosc=None)).pobierz(10)
    assert repozytorium_formy.zapytania == [(10, 1)]
    assert wynik.forma_goscia is None


def test_presenter_porownanie_strzelcy_i_forma() -> None:
    forma = FormaDruzyny(
        1,
        (
            mecz_formy(8, 25, 25, seria_zdobyte=4, seria_stracone=3),
            mecz_formy(9, 20, 22),
            mecz_formy(10, 30, 27),
        ),
        id_analizowany=10,
    )
    statystyki = StatystykiMeczuCalculator(MeczPolicy()).oblicz(szczegoly(), forma, None)
    widok = StatystykiMeczuPresenter(MeczFormat()).przygotuj(statystyki)

    wiersze = {w.etykieta: w for w in widok.porownanie}
    assert (wiersze["Bramki"].gospodarz, wiersze["Bramki"].gosc) == ("30", "27")
    assert wiersze["Bramki"].przewaga == "home"
    assert wiersze["Bramki"].udzial_gospodarza == 53
    assert wiersze["Druga połowa"].gospodarz == "18"
    assert wiersze["Druga połowa"].przewaga == "home"
    assert wiersze["Do przerwy"].przewaga == "away"
    assert (wiersze["Rzuty karne"].gospodarz, wiersze["Rzuty karne"].gosc) == ("3/4", "2/2")
    assert wiersze["Skuteczność karnych"].przewaga == "away"
    assert wiersze["Czasy drużyny"].gospodarz == "1 (25:10)"
    assert wiersze["Czasy drużyny"].gosc == "0"
    assert wiersze["Kary 2 min"].przewaga is None
    assert [s.zawodnik for s in widok.strzelcy_gospodarz] == ["Nowak", "Lis"]
    assert widok.strzelcy_gospodarz[0].karne == "3 z karnych"
    assert [s.zawodnik for s in widok.strzelcy_gosc] == ["Wróbel"]
    assert widok.wnioski and "odrobiła" in widok.wnioski[0]
    assert statystyki.gospodarz.nazwa == "Gospodarze"

    assert widok.forma_gospodarz is not None and widok.forma_gosc is None
    assert widok.forma_gospodarz.bilans == "1W 1R 1P"
    assert widok.forma_gospodarz.bramki == "75:74"
    assert [m.analizowany for m in widok.forma_gospodarz.mecze] == [False, False, True]
    assert widok.forma_gospodarz.mecze[0].dopisek == "k. 4:3"
    assert widok.forma_gospodarz.mecze[1].klasa == "loss"


def test_presenter_meczu_bez_wyniku_nie_ma_porownania() -> None:
    statystyki = StatystykiMeczuCalculator(MeczPolicy()).oblicz(
        szczegoly(wynik_gosp_full=None, wynik_gosc_full=None)
    )
    widok = StatystykiMeczuPresenter(MeczFormat()).przygotuj(statystyki)
    assert not widok.rozegrany
    assert widok.porownanie == [] and widok.wnioski == []


def test_repozytorium_formy_liczy_z_perspektywy_druzyny() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.return_value.all.return_value = [
        (5, datetime(2026, 9, 1), 7, False, 30, 25, None, None, None, None, None, None, "L", "A"),
        (6, datetime(2026, 9, 8), 9, True, 28, 28, 4, 5, 31, 30, 35, 36, "L", "B"),
    ]
    mecze = FormaMeczuSQLAlchemyRepository(sesja).pobierz_forme(6, 7)
    assert mecze[0].u_siebie
    assert (mecze[0].bramki_zdobyte, mecze[0].bramki_stracone) == (30, 25)
    drugi = mecze[1]
    assert drugi.u_siebie
    assert (drugi.seria_zdobyte, drugi.seria_stracone) == (5, 4)
    assert (drugi.dogrywka_zdobyte, drugi.dogrywka_stracone) == (36, 35)
    assert drugi.rywal == "B" and drugi.rozgrywki == "L"


def test_repozytorium_formy_zamienia_blad_bazy() -> None:
    sesja = Mock(spec=Session)
    sesja.execute.side_effect = SQLAlchemyError("x")
    with pytest.raises(BladOdczytuDanych):
        FormaMeczuSQLAlchemyRepository(sesja).pobierz_forme(1, 1)
