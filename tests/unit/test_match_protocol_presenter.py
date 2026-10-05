from dataclasses import replace
from datetime import date, datetime

from tests.helpers.schedule import mecz_zapowiedzi

from handball.domain.match_preview import (
    CzlonekKadry,
    DruzynaZapowiedzi,
    GrupaKadry,
    KadraDruzyny,
)
from handball.domain.match_protocol import (
    DaneProtokolu,
    HalaProtokolu,
    KolejnoscProtokolu,
    KolejnoscZawodnikowProtokoluPolicy,
    ProtokolMeczu,
    SedziaProtokolu,
)
from handball.interface.presenters.match_protocol_presenter import (
    ProtokolMeczuPresenter,
    UkladProtokoluPolicy,
)


def czlonek(id_zawodnik: int, nazwisko: str, numery: tuple[int, ...]) -> CzlonekKadry:
    return CzlonekKadry(id_zawodnik, "Jan", nazwisko, numery, None, None)


def presenter() -> ProtokolMeczuPresenter:
    return ProtokolMeczuPresenter(UkladProtokoluPolicy(), KolejnoscZawodnikowProtokoluPolicy())


def protokol(
    liczba: int = 2, kolejnosc: KolejnoscProtokolu = KolejnoscProtokolu.POZYCJE
) -> ProtokolMeczu:
    gospodarz = KadraDruzyny(
        DruzynaZapowiedzi(30, " Górnik Zabrze "),
        (
            GrupaKadry(0, (czlonek(1, "BRAMKARZ", (1, 12)),)),
            GrupaKadry(1, tuple(czlonek(i, f"GRACZ{i}", (i,)) for i in range(2, liczba + 1))),
            GrupaKadry(5, (czlonek(99, "BEZNUMERU", ()), czlonek(98, "ALFA", (5,)))),
        ),
    )
    return ProtokolMeczu(
        mecz=mecz_zapowiedzi(data=datetime(2025, 9, 22, 18, 30)),
        stan_na=datetime(2025, 9, 22, 18, 30),
        gospodarz=gospodarz,
        gosc=KadraDruzyny(DruzynaZapowiedzi(10, "Wisła Płock"), ()),
        dane=DaneProtokolu(
            HalaProtokolu("Hala Pogoń", "Zabrze", "Olimpijska", "7", None),
            (SedziaProtokolu("czas", "ZEGAR Ola", None),),
        ),
        kolejnosc=kolejnosc,
    )


def test_protokol_ma_zawodnikow_w_kolejnosci_kadry_i_granice_grup() -> None:
    wynik = presenter().przygotuj(protokol(3))
    gospodarz = wynik.druzyny[0]
    assert (gospodarz.litera, gospodarz.druzyna) == ("A", "Górnik Zabrze")
    assert [(z.numer, z.nazwa, z.nowa_grupa) for z in gospodarz.zawodnicy] == [
        ("1/12", "BRAMKARZ Jan", False),
        ("2", "GRACZ2 Jan", True),
        ("3", "GRACZ3 Jan", False),
        ("5", "ALFA Jan", True),
        ("", "BEZNUMERU Jan", False),
    ]
    assert wynik.druzyny[1].zawodnicy == ()
    assert (wynik.data, wynik.godzina) == ("22.09.2025", "18:30")
    assert (wynik.hala, wynik.adres, wynik.pojemnosc) == (
        "Hala Pogoń",
        "Olimpijska 7, Zabrze",
        "",
    )
    assert [(s.funkcja, s.nazwisko) for s in wynik.sedziowie] == [
        ("sędzia główny", ""),
        ("sędzia główny", ""),
        ("sekretarz", ""),
        ("m. czas", "ZEGAR Ola"),
        ("delegat ZPRP", ""),
    ]


def test_uklad_zmniejsza_wiersze_przy_duzej_kadrze_w_granicach() -> None:
    uklad = UkladProtokoluPolicy()
    assert uklad.uklad(10).wysokosc_zawodnika_mm == UkladProtokoluPolicy.NAJWYZSZY_WIERSZ_MM
    assert uklad.uklad(34).wysokosc_zawodnika_mm == round(173 / 34 - 0.2, 2)
    assert uklad.uklad(90).wysokosc_zawodnika_mm == UkladProtokoluPolicy.NAJNIZSZY_WIERSZ_MM
    assert uklad.uklad(0).wiersze_przebiegu == 34


def test_protokol_wedlug_numerow_bez_granic_grup_i_bez_numeru_na_koncu() -> None:
    wynik = presenter().przygotuj(protokol(3, KolejnoscProtokolu.NUMERY))
    assert [(z.numer, z.nowa_grupa) for z in wynik.druzyny[0].zawodnicy] == [
        ("1/12", False),
        ("2", False),
        ("3", False),
        ("5", False),
        ("", False),
    ]


def test_zawodnik_bez_sezonu_ma_kreski_a_rocznik_dwie_cyfry() -> None:
    dawny = replace(czlonek(7, "DAWNY", (7,)), pozycja="Obrotowy", data_urodzenia=date(2005, 3, 1))
    kadra = KadraDruzyny(DruzynaZapowiedzi(30, "Górnik"), (GrupaKadry(3, (dawny,)),))
    wynik = presenter().przygotuj(replace(protokol(), gospodarz=kadra))
    z = wynik.druzyny[0].zawodnicy[0]
    assert (z.pozycja, z.rocznik, z.mecze, z.bramki, z.srednia) == ("O", "05", "–", "–", "–")


def test_pogrubia_bramki_czterech_najlepszych_strzelcow_z_ex_aequo() -> None:
    czlonkowie = tuple(
        replace(czlonek(i, f"G{i}", (i,)), miejsce_strzelca=miejsce)
        for i, miejsce in enumerate((1, 2, 2, 4, 4, 6, None), start=1)
    )
    kadra = KadraDruzyny(DruzynaZapowiedzi(30, "Górnik"), (GrupaKadry(1, czlonkowie),))
    wynik = presenter().przygotuj(replace(protokol(), gospodarz=kadra))
    assert [z.wyroznij_bramki for z in wynik.druzyny[0].zawodnicy] == [
        True,
        True,
        True,
        True,
        True,
        False,
        False,
    ]


def test_w_grupie_pozycji_wedlug_numerow() -> None:
    grupa = GrupaKadry(1, (czlonek(1, "C", (20,)), czlonek(2, "A", (3,)), czlonek(3, "B", (11,))))
    kadra = KadraDruzyny(DruzynaZapowiedzi(30, "Górnik"), (grupa,))
    wynik = presenter().przygotuj(replace(protokol(), gospodarz=kadra))
    assert [z.numer for z in wynik.druzyny[0].zawodnicy] == ["3", "11", "20"]
