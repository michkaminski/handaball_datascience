from __future__ import annotations

from dataclasses import dataclass

from flask import Flask


@dataclass(frozen=True)
class PozycjaMenu:
    klucz: str
    etykieta: str
    punkt_koncowy: str | None
    ikona: str | None = None


GORNY_PASEK: list[PozycjaMenu] = [
    PozycjaMenu("start", "Start", "administracja.start"),
    PozycjaMenu("mecze", "Dane", "administracja.lista_meczow"),
    PozycjaMenu("raporty", "Raporty", "administracja.lista_raportow"),
    PozycjaMenu("import", "Import", "administracja.import_danych"),
    PozycjaMenu("kontrola", "Kontrola danych", None),
    PozycjaMenu("logi", "Logi", None),
]

SIDEBAR: list[tuple[str, list[PozycjaMenu]]] = [
    (
        "Dane",
        [
            PozycjaMenu("sezony", "Sezony", "administracja.lista_sezonow", "◫"),
            PozycjaMenu("rozgrywki", "Rozgrywki", "administracja.lista_rozgrywek", "⌘"),
            PozycjaMenu("druzyny", "Drużyny", "administracja.lista_druzyn", "▣"),
            PozycjaMenu("zawodnicy", "Zawodnicy", "administracja.lista_zawodnikow", "◎"),
            PozycjaMenu("sklady", "Składy", "administracja.lista_skladow", "☰"),
            PozycjaMenu("mecze", "Mecze", "administracja.lista_meczow", "◈"),
            PozycjaMenu("terminarz", "Terminarz", "administracja.terminarz", "☷"),
            PozycjaMenu("tabele", "Tabele", "administracja.lista_tabel", "▤"),
            PozycjaMenu("strzelcy", "Strzelcy", "administracja.lista_strzelcow", "★"),
            PozycjaMenu("hale", "Hale", "administracja.lista_hal", "⌂"),
            PozycjaMenu("sedziowie", "Sędziowie", "administracja.lista_sedziow", "⚑"),
        ],
    ),
    (
        "Raporty",
        [
            PozycjaMenu("raporty", "Katalog raportów", "administracja.lista_raportow", "▦"),
            PozycjaMenu("rozkłady", "Rozkłady", "administracja.lista_rozkladow", "▥"),
            PozycjaMenu("frekwencja", "Frekwencja", "administracja.raport_frekwencji", "◐"),
            PozycjaMenu("raporty_druzyn", "Raporty drużyn", "administracja.raporty_druzyn", "▤"),
            PozycjaMenu(
                "prognozy_meczow",
                "Prognozy meczów",
                "administracja.raport_prognoz_meczow",
                "↗",
            ),
            PozycjaMenu(
                "typowania_meczow",
                "Typowania meczów",
                "administracja.raport_typowan_meczow",
                "✎",
            ),
        ],
    ),
    (
        "Import / eksport",
        [
            PozycjaMenu("import", "Import danych", "administracja.import_danych", "⇪"),
            PozycjaMenu("historia_importow", "Historia importów", None, "⇄"),
            PozycjaMenu("eksport_danych", "Eksport danych", None, "⇩"),
        ],
    ),
    (
        "Narzędzia",
        [
            PozycjaMenu(
                "statystyki_bazy",
                "Statystyki tabel",
                "administracja.statystyki_tabel",
                "◫",
            ),
            PozycjaMenu("anomalie", "Anomalie danych", None, "!"),
            PozycjaMenu("walidacja", "Walidacja danych", None, "✓"),
            PozycjaMenu("logi_aplikacji", "Logi aplikacji", None, "≡"),
        ],
    ),
]


def zarejestruj_kontekst_nawigacji(aplikacja: Flask) -> None:
    @aplikacja.context_processor
    def wstrzyknij_menu() -> dict[str, object]:
        return {"gorny_pasek": GORNY_PASEK, "sidebar": SIDEBAR}
