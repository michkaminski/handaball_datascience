from handball.domain.competition_levels import (
    DopasowanieGrupRozgrywek,
    GrupaRozgrywek,
    KolejnoscRozgrywekPolicy,
)
from handball.domain.options import OpcjaWyboru


def test_nazwy_superliga_liga_centralna_i_liga_ii_liga_potem_pozostale() -> None:
    nazwy = [
        "Puchar Polski Mężczyzn",
        "II Liga Mężczyzn gr. 2",
        "III Liga Kobiet",
        "I Liga Kobiet Grupa A",
        "Liga Centralna Mężczyzn",
        "ORLEN Superliga Kobiet",
        "Baraż o I Ligę",
        "LOTTO Superliga",
        "Liga Centralna Kobiet",
        "I Liga Mężczyzn Grupa B",
        "Baraż o ORLEN Superligę Kobiet",
        "Ekstraklasa Kobiet",
    ]
    assert KolejnoscRozgrywekPolicy().uporzadkuj_nazwy(nazwy) == [
        "Ekstraklasa Kobiet",
        "LOTTO Superliga",
        "ORLEN Superliga Kobiet",
        "Baraż o ORLEN Superligę Kobiet",
        "Liga Centralna Kobiet",
        "Liga Centralna Mężczyzn",
        "I Liga Kobiet Grupa A",
        "I Liga Mężczyzn Grupa B",
        "II Liga Mężczyzn gr. 2",
        "III Liga Kobiet",
        "Puchar Polski Mężczyzn",
        "Baraż o I Ligę",
    ]


def test_grupa_rozgrywek_rozpoznaje_poziom_i_puchar() -> None:
    dopasowanie = DopasowanieGrupRozgrywek()
    assert dopasowanie.grupa("LOTTO Superliga") is GrupaRozgrywek.SUPERLIGA
    assert dopasowanie.grupa("Ekstraklasa Kobiet") is GrupaRozgrywek.SUPERLIGA
    assert dopasowanie.grupa("Baraż o ORLEN Superligę Kobiet") is GrupaRozgrywek.SUPERLIGA
    assert dopasowanie.grupa("Liga Centralna Mężczyzn") is GrupaRozgrywek.LIGA_CENTRALNA
    assert dopasowanie.grupa("I Liga Kobiet Grupa A") is GrupaRozgrywek.I_LIGA
    assert dopasowanie.grupa("II Liga Mężczyzn gr. 2") is GrupaRozgrywek.II_LIGA
    assert dopasowanie.grupa("III Liga Kobiet") is None
    assert dopasowanie.grupa("Puchar Polski Mężczyzn") is GrupaRozgrywek.PUCHAR_POLSKI
    assert dopasowanie.grupa("Superpuchar Polski") is None


def test_opcje_wedlug_poziomu_nazwy_i_identyfikatora() -> None:
    opcje = [
        OpcjaWyboru(3, "II Liga Kobiet"),
        OpcjaWyboru(9, "Superliga Mężczyzn"),
        OpcjaWyboru(2, "Superliga Mężczyzn"),
        OpcjaWyboru(5, "Liga Centralna Kobiet"),
    ]
    assert [o.wartosc for o in KolejnoscRozgrywekPolicy().uporzadkuj_opcje(opcje)] == [2, 9, 5, 3]
