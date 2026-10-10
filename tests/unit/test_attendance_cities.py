from handball.domain.attendance_aggregate import AgregatFrekwencji
from handball.domain.attendance_cities import (
    UWAGA_O_ZRODLE_MIASTA,
    DaneMiast,
    MiastaFrekwencjiCalculator,
    MiastoFrekwencji,
    WkladMiasta,
)

kalkulator = MiastaFrekwencjiCalculator()


def _miasto(
    nazwa: str,
    rozegrane: int,
    znane: int,
    suma: int,
    klubow: int = 1,
    rozgrywek: int = 1,
) -> MiastoFrekwencji:
    return MiastoFrekwencji(
        rozegrane=rozegrane,
        znane=znane,
        suma=suma,
        maksimum=suma // znane if znane else None,
        miasto=nazwa,
        liczba_klubow=klubow,
        liczba_rozgrywek=rozgrywek,
    )


def _wklad(
    miasto: str, id_zespol: int, klub: str, rozgrywki: str, znane: int, suma: int
) -> WkladMiasta:
    return WkladMiasta(
        miasto=miasto,
        id_zespol=id_zespol,
        klub=klub,
        rozgrywki=rozgrywki,
        agregat=AgregatFrekwencji(
            rozegrane=znane, znane=znane, suma=suma, maksimum=suma // znane if znane else None
        ),
    )


def test_ranking_miast_sortuje_po_sumie_potem_sredniej_i_pomija_brak_miasta() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(
                _miasto("Kielce", 10, 10, 30000),
                _miasto("Płock", 5, 5, 30000),
                _miasto("Lubin", 4, 4, 8000),
                _miasto("", 3, 3, 90000),
                _miasto("   ", 2, 2, 50000),
                _miasto("Gdańsk", 6, 0, 0),
            ),
            wklady=(),
            mecze_bez_miasta=7,
        )
    )

    assert [wiersz.miasto.miasto for wiersz in raport.ranking] == ["Płock", "Kielce", "Lubin"]
    assert [wiersz.pozycja for wiersz in raport.ranking] == [1, 2, 3]
    assert raport.ranking[0].miasto.srednia == 6000
    assert raport.mecze_bez_miasta == 7 + 3 + 2
    assert raport.uwaga == UWAGA_O_ZRODLE_MIASTA
    assert raport.uwaga_o_brakach is not None


def test_wklady_sa_przypisane_do_miast_z_rankingu_i_pomijaja_nieznana_frekwencje() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Kielce", 6, 6, 12000, 2, 2), _miasto("Płock", 3, 3, 4500)),
            wklady=(
                _wklad("Kielce", 1, "Industria", "Superliga", 3, 6000),
                _wklad("Kielce", 2, "Vive", "Puchar", 3, 6000),
                _wklad("Kielce", 1, "Industria", "Liga B", 0, 0),
                _wklad("Płock", 3, "Wisła", "Superliga", 3, 4500),
                _wklad("Lubin", 4, "Zagłębie", "Superliga", 3, 3000),
            ),
            mecze_bez_miasta=0,
        )
    )

    kielce, plock = raport.ranking
    assert [wklad.klub for wklad in kielce.wklady] == ["Industria", "Vive"]
    assert [wklad.klub for wklad in plock.wklady] == ["Wisła"]
    assert len(raport.wklady) == 3
    assert raport.rozgrywki == ("Puchar", "Superliga")
    assert raport.uwaga_o_brakach is None


def test_limity_miast_i_wkladow() -> None:
    miasta = tuple(_miasto(f"Miasto {i}", 1, 1, 1000 * i) for i in range(1, 6))
    wklady = tuple(
        _wklad(f"Miasto {i}", i, f"Klub {i}{j}", "Superliga", 1, 100 * j)
        for i in range(1, 6)
        for j in range(1, 4)
    )

    raport = kalkulator.zbuduj(
        DaneMiast(miasta=miasta, wklady=wklady, mecze_bez_miasta=0),
        limit_miast=3,
        limit_wkladow=4,
    )

    assert [wiersz.miasto.miasto for wiersz in raport.ranking] == [
        "Miasto 5",
        "Miasto 4",
        "Miasto 3",
    ]
    assert [len(wiersz.wklady) for wiersz in raport.ranking] == [3, 1, 0]
    assert len(raport.wklady) == 4


def test_pusty_raport_miast_nie_ma_danych() -> None:
    raport = kalkulator.zbuduj(DaneMiast(miasta=(), wklady=(), mecze_bez_miasta=0))

    assert not raport.ma_dane
    assert raport.ranking == ()
    assert raport.wklady == ()
    assert raport.mecze_bez_miasta == 0
