from datetime import datetime

import pytest
from tests.helpers.news import (
    I_LIGA,
    LIGA_CENTRALNA_K,
    LIGA_CENTRALNA_M,
    SUPERLIGA_K,
    SUPERLIGA_M,
    SUPERPUCHAR_K,
    AktualnosciInMemoryRepository,
    mecz,
)

from handball.domain.news import (
    KategoriaRozgrywek,
    RozgrywkiAktualnosci,
    StrzelecAktualnosci,
    WystepAktualnosci,
)
from handball.services.news_service import (
    LICZBA_MECZOW_W_SEKCJI,
    AktualnosciService,
    KategoriaRozgrywekPolicy,
)


@pytest.mark.parametrize(
    ("rozgrywki", "kategoria"),
    [
        (SUPERLIGA_M, KategoriaRozgrywek.SUPERLIGA_M),
        (SUPERLIGA_K, KategoriaRozgrywek.SUPERLIGA_K),
        (LIGA_CENTRALNA_M, KategoriaRozgrywek.LIGA_CENTRALNA_M),
        (LIGA_CENTRALNA_K, KategoriaRozgrywek.LIGA_CENTRALNA_K),
        (SUPERPUCHAR_K, KategoriaRozgrywek.POZOSTALE),
        (I_LIGA, KategoriaRozgrywek.POZOSTALE),
        (RozgrywkiAktualnosci(9, "PGNiG Superliga Kobiet", None), KategoriaRozgrywek.SUPERLIGA_K),
    ],
)
def test_kategoria_rozgrywek_rozpoznaje_ligi_priorytetowe_po_nazwie_i_plci(
    rozgrywki: RozgrywkiAktualnosci, kategoria: KategoriaRozgrywek
) -> None:
    assert KategoriaRozgrywekPolicy().kategoria(rozgrywki) is kategoria


def test_brak_sezonu_daje_puste_aktualnosci() -> None:
    wynik = AktualnosciService(AktualnosciInMemoryRepository(sezon=None)).pobierz_aktualnosci()
    assert wynik.sezon is None and wynik.sekcje == () and wynik.liczba_rozegranych == 0


def test_sekcje_priorytetowe_sa_uporzadkowane_i_zawieraja_najnowsze_mecze() -> None:
    mecze = tuple(mecz(100 + d, SUPERLIGA_M.id_rozgrywki, d, (30, 20 + d)) for d in range(1, 9))
    mecze += (
        mecz(200, LIGA_CENTRALNA_K.id_rozgrywki, 5, (25, 25)),
        mecz(300, I_LIGA.id_rozgrywki, 7, (40, 10)),
        mecz(301, SUPERPUCHAR_K.id_rozgrywki, 2, (22, 21)),
    )
    wynik = AktualnosciService(AktualnosciInMemoryRepository(mecze=mecze)).pobierz_aktualnosci()
    assert [s.kategoria for s in wynik.sekcje] == [
        KategoriaRozgrywek.SUPERLIGA_M,
        KategoriaRozgrywek.SUPERLIGA_K,
        KategoriaRozgrywek.LIGA_CENTRALNA_M,
        KategoriaRozgrywek.LIGA_CENTRALNA_K,
    ]
    superliga = wynik.sekcje[0]
    assert superliga.liczba_rozegranych == 8
    assert len(superliga.ostatnie_mecze) == LICZBA_MECZOW_W_SEKCJI
    assert superliga.ostatnie_mecze[0].id_mecz == 108
    assert superliga.srednia_bramek == pytest.approx(sum(50 + d for d in range(1, 9)) / 8)
    assert wynik.sekcje[1].liczba_rozegranych == 0 and wynik.sekcje[1].srednia_bramek is None
    assert [p.mecz.id_mecz for p in wynik.pozostale_mecze] == [300, 301]
    assert wynik.liczba_rozegranych == 11


def test_ciekawostki_licza_rekordy_i_najbardziej_bramkostrzelna_lige() -> None:
    mecze = (
        mecz(1, SUPERLIGA_M.id_rozgrywki, 1, (35, 34)),
        mecz(2, SUPERLIGA_K.id_rozgrywki, 2, (30, 20)),
        mecz(3, I_LIGA.id_rozgrywki, 3, (45, 12)),
    )
    wystep = WystepAktualnosci(
        I_LIGA.id_rozgrywki, 3, datetime(2026, 9, 3), 77, "Jan Nowak", "KS", 14
    )
    wynik = AktualnosciService(
        AktualnosciInMemoryRepository(mecze=mecze, wystepy=(wystep,))
    ).pobierz_aktualnosci()
    assert wynik.najwiecej_bramek is not None and wynik.najwiecej_bramek.mecz.id_mecz == 1
    assert wynik.najwiecej_bramek.wartosc == 69
    assert wynik.najwyzsze_zwyciestwo is not None and wynik.najwyzsze_zwyciestwo.wartosc == 33
    assert wynik.najwyzsze_zwyciestwo.rozgrywki == I_LIGA
    assert wynik.najlepsze_wystepy[0].wystep.bramki == 14
    assert wynik.najlepsze_wystepy[0].rozgrywki == I_LIGA
    assert wynik.najbardziej_bramkostrzelna is not None
    assert wynik.najbardziej_bramkostrzelna.kategoria is KategoriaRozgrywek.SUPERLIGA_M
    assert wynik.suma_bramek == 69 + 50 + 57


def test_strzelcy_trafiaja_do_sekcji_swoich_rozgrywek() -> None:
    strzelcy = (
        StrzelecAktualnosci(SUPERLIGA_K.id_rozgrywki, 5, "Anna Kowalska", "MKS", 3, 21),
        StrzelecAktualnosci(I_LIGA.id_rozgrywki, 6, "Piotr Zieliński", "KS", 3, 30),
    )
    wynik = AktualnosciService(
        AktualnosciInMemoryRepository(strzelcy=strzelcy)
    ).pobierz_aktualnosci()
    assert [s.zawodnik for s in wynik.sekcje[1].strzelcy] == ["Anna Kowalska"]
    assert all(
        not s.strzelcy for s in wynik.sekcje if s.kategoria is not KategoriaRozgrywek.SUPERLIGA_K
    )
