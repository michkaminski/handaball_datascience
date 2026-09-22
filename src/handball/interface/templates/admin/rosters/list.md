# Składy

Status: zaimplementowano.

## Przeznaczenie i zachowanie

Widok `GET /administracja/sklady` pokazuje po jednym wierszu dla drużyny w sezonie (`public.zespoly_sezony`) posiadającej skład. Kolumny to sezon, drużyna, alfabetyczna lista unikalnych rozgrywek oddzielona przecinkami oraz akcja. Paginacja dotyczy składów sezonowych, nie zawodników.

Filtry sezonu i rozgrywek ograniczają listę drużyn. Wyszukiwanie obejmuje nazwę drużyny oraz zawodnika lub pozycję w jej składzie. Nagłówki sezonu, drużyny i rozgrywek sterują sortowaniem; domyślnie najnowszy sezon jest pierwszy.

Przycisk „Szczegóły” otwiera `GET /administracja/sklady/<id_zespol_sezon>` w nowej karcie. Dwuklik lub Enter na wierszu pobiera tę samą kartę do modalu. Kliknięcie przycisku nie uruchamia modalu.

## Dane i powiązania

`SkladListView` korzysta z `KlasyfikacjaService` i `KlasyfikacjaReadRepository`. Rozgrywki są pobierane przez `zespoly_rozgrywki` w kontekście tego samego zespołu i sezonu. Zawodnicy są pobierani dopiero w szczegółach, bez interpretowania zgłoszenia jako występu meczowego.

## Sprawdzenie zmiany

Testy tras, listy rozgrywek i szczegółów są w `tests/interface/test_classifications.py`. Interakcję zapewnia `static/js/classification_details.js`.

## Układ tekstowy i mapa zmian

```text
[base.html: nawigacja]
Składy
[szukaj] [sezon] [rozgrywki] [Filtruj] [Wyczyść]
+----------------------------------------------------------------+
| Sezon ↕ | Drużyna ↕ | Rozgrywki: A, B, C ↕ | Szczegóły       |
+----------------------------------------------------------------+
[paginacja]
[dwuklik/Enter: modal Szczegóły składu / ×]
```

| Element | Plik / dane |
| --- | --- |
| Nagłówek, filtry, tabela i modal | `list.html`, `KlasyfikacjaFilterForm`, `[data-detail-*]` |
| Dane listy | `SkladListView` → `KlasyfikacjaService` → `pobierz_sklady` |
| Lista rozgrywek | `zespoly_rozgrywki` + `rozgrywki`, pole `Sklad.rozgrywki` |
| Szczegóły | [detail.md](detail.md), `administracja.szczegoly_skladu` |
| Dwuklik i Enter | `static/js/classification_details.js`, `SzczegolyKlasyfikacjiController` |
| Paginacja | `partials/pagination.html`, `StronaKlasyfikacji` |
