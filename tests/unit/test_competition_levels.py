from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
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


def test_opcje_wedlug_poziomu_nazwy_i_identyfikatora() -> None:
    opcje = [
        OpcjaWyboru(3, "II Liga Kobiet"),
        OpcjaWyboru(9, "Superliga Mężczyzn"),
        OpcjaWyboru(2, "Superliga Mężczyzn"),
        OpcjaWyboru(5, "Liga Centralna Kobiet"),
    ]
    assert [o.wartosc for o in KolejnoscRozgrywekPolicy().uporzadkuj_opcje(opcje)] == [2, 9, 5, 3]
