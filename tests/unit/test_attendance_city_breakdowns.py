from handball.domain.attendance_aggregate import AgregatFrekwencji, MiaryRozkladu
from handball.domain.attendance_cities import (
    DaneMiast,
    LimityRozbiciaMiast,
    MiastaFrekwencjiCalculator,
    MiastoFrekwencji,
    WkladMiasta,
)
from handball.domain.attendance_city_breakdowns import HalaMiasta, RozgrywkiMiasta, SezonMiasta
from handball.interface.presenters.attendance_cities_presenter import MiastaWykresPresenter

kalkulator = MiastaFrekwencjiCalculator()


def _agregat(znane: int, suma: int, rozegrane: int | None = None) -> AgregatFrekwencji:
    return AgregatFrekwencji(
        rozegrane=znane if rozegrane is None else rozegrane,
        znane=znane,
        suma=suma,
        maksimum=suma // znane if znane else None,
    )


def _miasto(
    nazwa: str,
    znane: int,
    suma: int,
    rozegrane: int | None = None,
    rozklad: MiaryRozkladu | None = None,
    klubow: int = 1,
    rozgrywek: int = 1,
) -> MiastoFrekwencji:
    agregat = _agregat(znane, suma, rozegrane)
    return MiastoFrekwencji(
        rozegrane=agregat.rozegrane,
        znane=agregat.znane,
        suma=agregat.suma,
        maksimum=agregat.maksimum,
        miasto=nazwa,
        liczba_klubow=klubow,
        liczba_rozgrywek=rozgrywek,
        rozklad=rozklad or MiaryRozkladu(),
    )


def _sezon(klucz: str, nazwa: str, rok: int | None, znane: int, suma: int) -> SezonMiasta:
    return SezonMiasta(
        klucz=klucz,
        sezon=nazwa,
        rok_poczatku=rok,
        agregat=_agregat(znane, suma),
        rozklad=MiaryRozkladu(mediana=suma / znane if znane else None, dominanta=None, minimum=1),
    )


def _rozgrywki(klucz: str, nazwa: str, znane: int, suma: int) -> RozgrywkiMiasta:
    return RozgrywkiMiasta(
        klucz=klucz, rozgrywki=nazwa, liczba_klubow=1, agregat=_agregat(znane, suma)
    )


def _hala(
    klucz: str, id_hala: int, nazwa: str, miasto_hali: str | None, znane: int, suma: int
) -> HalaMiasta:
    return HalaMiasta(
        klucz=klucz,
        id_hala=id_hala,
        hala=nazwa,
        miasto_hali=miasto_hali,
        agregat=_agregat(znane, suma),
    )


def test_pisownie_gdansk_i_gdansk_wielkimi_literami_sa_jednym_miastem() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(
                _miasto("GDAŃSK", 2, 5000, rozklad=MiaryRozkladu(minimum=1800)),
                _miasto("Gdańsk", 4, 8000, rozklad=MiaryRozkladu(2000, 2000, 1500)),
                _miasto("Kielce", 3, 6000),
            ),
            wklady=(),
            mecze_bez_miasta=0,
        )
    )

    assert [wiersz.miasto.miasto for wiersz in raport.ranking] == ["Gdańsk", "Kielce"]
    gdansk = raport.ranking[0].miasto
    assert gdansk.rozegrane == 6
    assert gdansk.znane == 6
    assert gdansk.suma == 13000
    assert gdansk.maksimum == 2500
    assert gdansk.srednia == 13000 / 6
    assert gdansk.rozklad.minimum == 1500
    assert gdansk.rozklad.mediana is None
    assert gdansk.rozklad.dominanta is None
    assert gdansk.klucz == "gdańsk"


def test_scalone_miasto_dostaje_etykiete_najczestszej_pisowni() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(
                _miasto("Gdańsk", 1, 1000),
                _miasto("GDAŃSK", 5, 9000),
                _miasto(" gdańsk ", 2, 3000),
            ),
            wklady=(),
            mecze_bez_miasta=0,
        )
    )

    assert len(raport.ranking) == 1
    assert raport.ranking[0].miasto.miasto == "GDAŃSK"


def test_pojedyncze_miasto_zachowuje_mediane_i_dominante() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Płock", 5, 15000, rozklad=MiaryRozkladu(2900.6, 3000, 2000)),),
            wklady=(),
            mecze_bez_miasta=0,
        )
    )

    rozklad = raport.ranking[0].miasto.rozklad
    assert rozklad.mediana == 2900.6
    assert rozklad.dominanta == 3000
    assert rozklad.minimum == 2000
    assert rozklad.mediana_etykieta == "2 901"
    assert rozklad.dominanta_etykieta == "3 000"
    assert rozklad.minimum_etykieta == "2 000"


def test_miary_rozkladu_bez_danych_maja_myslnik() -> None:
    rozklad = MiaryRozkladu()

    assert rozklad.mediana_etykieta == "—"
    assert rozklad.dominanta_etykieta == "—"
    assert rozklad.minimum_etykieta == "—"


def test_wiersze_rozbicia_trafiaja_do_scalonego_miasta_niezaleznie_od_pisowni() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Gdańsk", 4, 8000), _miasto("GDAŃSK", 2, 5000)),
            wklady=(
                WkladMiasta("GDAŃSK", 1, "Wybrzeże", "Superliga", _agregat(2, 5000)),
                WkladMiasta("Gdańsk", 1, "Wybrzeże", "Puchar", _agregat(4, 8000)),
            ),
            mecze_bez_miasta=0,
            sezony=(
                _sezon("gdańsk", "2024/2025", 2024, 3, 7000),
                _sezon("GDAŃSK", "2023/2024", 2023, 3, 6000),
            ),
            rozgrywki=(_rozgrywki("gdańsk", "Superliga", 6, 13000),),
            hale=(_hala("gdańsk", 1, "Hala Olivia", None, 6, 13000),),
        )
    )

    wiersz = raport.ranking[0]
    assert [wklad.rozgrywki for wklad in wiersz.wklady] == ["Puchar", "Superliga"]
    assert [sezon.sezon for sezon in wiersz.sezony] == ["2023/2024", "2024/2025"]
    assert [pozycja.rozgrywki for pozycja in wiersz.wg_rozgrywek] == ["Superliga"]
    assert [hala.hala for hala in wiersz.hale] == ["Hala Olivia"]


def test_sezony_sa_chronologiczne_a_sezon_bez_roku_jest_pierwszy() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Kielce", 9, 27000),),
            wklady=(),
            mecze_bez_miasta=0,
            sezony=(
                _sezon("kielce", "2024/2025", 2024, 3, 9000),
                _sezon("kielce", "bez roku", None, 3, 9000),
                _sezon("kielce", "2022/2023", 2022, 3, 9000),
                _sezon("kielce", "2023/2024", 2023, 0, 0),
            ),
        )
    )

    sezony = raport.ranking[0].sezony
    assert [sezon.sezon for sezon in sezony] == ["bez roku", "2022/2023", "2024/2025"]
    assert sezony[1].agregat.srednia == 3000
    assert sezony[1].rozklad.mediana == 3000
    assert raport.sezony == sezony


def test_rozgrywki_miasta_sa_sortowane_po_sumie_i_limitowane_na_miasto() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Kielce", 9, 27000), _miasto("Płock", 3, 6000)),
            wklady=(),
            mecze_bez_miasta=0,
            rozgrywki=(
                _rozgrywki("kielce", "Puchar", 2, 4000),
                _rozgrywki("kielce", "Superliga", 5, 15000),
                _rozgrywki("kielce", "Liga B", 2, 8000),
                _rozgrywki("płock", "Superliga", 3, 6000),
                _rozgrywki("lubin", "Superliga", 3, 1000),
            ),
        ),
        limity_rozbicia=LimityRozbiciaMiast(rozgrywki_na_miasto=2),
    )

    kielce, plock = raport.ranking
    assert [pozycja.rozgrywki for pozycja in kielce.wg_rozgrywek] == ["Superliga", "Liga B"]
    assert [pozycja.rozgrywki for pozycja in plock.wg_rozgrywek] == ["Superliga"]
    assert len(raport.wg_rozgrywek) == 3


def test_hale_miasta_sa_sortowane_po_sumie_i_pomijaja_nieznana_frekwencje() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Kielce", 9, 27000),),
            wklady=(),
            mecze_bez_miasta=0,
            hale=(
                _hala("kielce", 2, "Hala Legionów", "Kielce", 3, 6000),
                _hala("kielce", 1, "Hala Targowa", "Chęciny", 6, 21000),
                _hala("kielce", 3, "Hala Pusta", None, 0, 0),
            ),
        )
    )

    hale = raport.ranking[0].hale
    assert [hala.hala for hala in hale] == ["Hala Targowa", "Hala Legionów"]
    assert hale[0].miasto_hali_inne is True
    assert hale[0].miasto_hali_etykieta == "Chęciny"
    assert hale[0].etykieta == "Hala Targowa (Chęciny)"
    assert hale[1].miasto_hali_inne is False
    assert hale[1].miasto_hali_etykieta == "—"
    assert hale[1].etykieta == "Hala Legionów"


def test_miasto_hali_rozniace_sie_tylko_wielkoscia_liter_nie_jest_inne() -> None:
    hala = _hala("gdańsk", 1, "Hala Olivia", "GDAŃSK ", 3, 6000)

    assert hala.miasto_hali_inne is False
    assert hala.miasto_hali_etykieta == "—"
    assert _hala("gdańsk", 2, "Hala", "   ", 3, 6000).miasto_hali_inne is False
    assert _hala("gdańsk", 3, "Hala", None, 3, 6000).miasto_hali_inne is False


def test_limity_hal_ogolny_i_na_miasto() -> None:
    miasta = (_miasto("Kielce", 9, 27000), _miasto("Płock", 6, 12000))
    hale = (
        _hala("kielce", 1, "A", None, 3, 9000),
        _hala("kielce", 2, "B", None, 3, 8000),
        _hala("kielce", 3, "C", None, 3, 7000),
        _hala("płock", 4, "D", None, 3, 6000),
        _hala("płock", 5, "E", None, 3, 5000),
    )

    raport = kalkulator.zbuduj(
        DaneMiast(miasta=miasta, wklady=(), mecze_bez_miasta=0, hale=hale),
        limity_rozbicia=LimityRozbiciaMiast(hale=3, hale_na_miasto=2),
    )

    assert [[hala.hala for hala in wiersz.hale] for wiersz in raport.ranking] == [
        ["A", "B"],
        ["D"],
    ]


def test_rozbicie_pomija_miasta_spoza_rankingu() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(_miasto("Kielce", 3, 9000), _miasto("Lubin", 3, 3000)),
            wklady=(),
            mecze_bez_miasta=0,
            sezony=(_sezon("lubin", "2024/2025", 2024, 3, 3000),),
        ),
        limit_miast=1,
    )

    assert [wiersz.miasto.miasto for wiersz in raport.ranking] == ["Kielce"]
    assert raport.sezony == ()


def test_raport_bez_rozbicia_ma_puste_kolekcje() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(miasta=(_miasto("Kielce", 3, 9000),), wklady=(), mecze_bez_miasta=0)
    )

    assert raport.sezony == ()
    assert raport.wg_rozgrywek == ()
    assert raport.hale == ()


def test_presenter_zwraca_miary_i_szczegoly_dla_wykresow() -> None:
    raport = kalkulator.zbuduj(
        DaneMiast(
            miasta=(
                _miasto("Kielce", 6, 18000, rozklad=MiaryRozkladu(3000.0, 2800, 2000)),
                _miasto("Płock", 3, 6000),
            ),
            wklady=(),
            mecze_bez_miasta=0,
            sezony=(_sezon("kielce", "2024/2025", 2024, 6, 18000),),
            rozgrywki=(_rozgrywki("kielce", "Superliga", 6, 18000),),
            hale=(_hala("kielce", 1, "Hala Legionów", "Chęciny", 6, 18000),),
        )
    )

    dane = MiastaWykresPresenter().przygotuj(raport)

    assert [miasto["nazwa"] for miasto in dane["miasta"]] == ["Kielce", "Płock"]
    assert dane["miasta"][0]["mediana"] == 3000.0
    assert dane["miasta"][0]["dominanta"] == 2800
    assert dane["miasta"][0]["klucz"] == "kielce"
    kielce, plock = dane["miastaSzczegoly"]
    assert kielce["klucz"] == "kielce"
    assert kielce["sezony"][0]["sezon"] == "2024/2025"
    assert kielce["sezony"][0]["rozegrane"] == 6
    assert kielce["sezony"][0]["srednia"] == 3000
    assert kielce["rozgrywki"] == [
        {"nazwa": "Superliga", "suma": 18000, "srednia": 3000, "mediana": None, "znane": 6}
    ]
    assert kielce["hale"][0]["nazwa"] == "Hala Legionów (Chęciny)"
    assert plock["sezony"] == []
    assert plock["rozgrywki"] == []
    assert plock["hale"] == []
