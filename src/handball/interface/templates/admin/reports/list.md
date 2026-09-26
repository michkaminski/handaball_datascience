# Katalog raportów

Status: zaimplementowany szablon [list.html](list.html).

## Przeznaczenie i routing

`GET /administracja/raporty` (endpoint `administracja.lista_raportow`) to wejście do głównej zakładki „Raporty”: raportów analitycznych, modeli statystycznych i predykcyjnych. Widok `RaportyListView` nie czyta bazy. Wyświetla stałą listę `KATALOG_RAPORTOW` z [report_catalog.py](../../../report_catalog.py).

Nowy raport dodajemy jako kolejną `PozycjaRaportu` (klucz, tytuł, opis, kategoria, endpoint) oraz jego własne trasy i szablony w `admin/reports/<raport>/`. Tego szablonu nie trzeba wtedy zmieniać.

Prototyp v6 nie ma ekranu raportów. Wygląd korzysta ze wspólnych klas `pagehead`, `panel`, `table-wrap`, `badge` i `icon-link`.

## Dane

| Zmienna | Typ | Opis |
| --- | --- | --- |
| `raporty` | `tuple[PozycjaRaportu, ...]` | Pozycje katalogu, w kolejności wyświetlania |
| `sekcja_aktywna` | `"raporty"` | Aktywna pozycja sidebara „Katalog raportów” |
| `sekcja_glowna` | `"raporty"` | Aktywna pozycja górnego paska „Raporty” |

Pusty katalog pokazuje wiersz „Brak raportów”.

## Weryfikacja

`tests/interface/test_match_predictions.py::test_katalog_raportow_i_nawigacja`.

## Układ tekstowy i mapa zmian

```text
[rama base.html: nagłówek, górny pasek (Raporty aktywne), sidebar (Katalog raportów aktywny)]
(1) Start › Raporty
    RAPORTY
    Raporty analityczne, modele statystyczne i modele predykcyjne...
(2) Katalog raportów
    Raport (link) | Kategoria (badge) | Opis | Akcje [Otwórz]
    Prognozy meczów — siła drużyn | Model predykcyjny | Historyczny backtest... | [Otwórz]
    Typowania meczów              | Model predykcyjny | Prognozy meczów z okresu... | [Otwórz]
```

| Element | Plik | Blok / selektor / dane |
| --- | --- | --- |
| 1. Nagłówek | [list.html](list.html) | `section.pagehead` |
| 2. Wiersze katalogu | [report_catalog.py](../../../report_catalog.py) | `KATALOG_RAPORTOW`, `PozycjaRaportu` |
| 2. Znacznik tabeli | [list.html](list.html) | `table.report-catalog`, `td.report-description` |
| Styl opisu | [admin.css](../../../static/css/admin.css) | `.report-description` |
| Pozycje menu | [navigation.py](../../../navigation.py) | `GORNY_PASEK` „Raporty”, grupa sidebara „Raporty” |
| Trasa | [admin/\_\_init\_\_.py](../../../admin/__init__.py), [report_views.py](../../../admin/views/report_views.py) | `RaportyListView` |
