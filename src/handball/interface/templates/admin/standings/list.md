# Tabele

Status: zaimplementowano.

## Przeznaczenie i zachowanie

Widok `GET /administracja/tabele` pokazuje po jednym wierszu dla rekordu `public.tabele_grupy`, pogrupowanego przez sezon, rozgrywki, tabelę i grupę. Filtry sezonu i rozgrywek oraz wyszukiwanie działają przed paginacją. Nagłówki czterech kolumn sterują sortowaniem, domyślnie od najnowszego sezonu.

Przycisk „Szczegóły” otwiera `GET /administracja/tabele/<id_tabela_grupa>` w nowej karcie. Dwuklik lub Enter na wierszu pobiera tę samą kartę do modalu. Szczegóły obejmują wyłącznie wybraną grupę. Kliknięcie przycisku nie otwiera dodatkowo modalu. Brak wyników jest osobnym wierszem tabeli.

## Dane i powiązania

`TabelaListView` korzysta z `KlasyfikacjaService` i `KlasyfikacjaReadRepository`. Lista odczytuje `tabele_grupy`, `tabele`, `rozgrywki` i `sezony`; pozycje drużyn są pobierane dopiero przez szczegóły. Paginacja dotyczy grup tabel, nie wierszy klasyfikacji.

Obsługę modalu zapewnia `static/js/classification_details.js`. Po wczytaniu szczegółów podłącza w nich linki drużyn (klik: okno karty drużyny nad modalem tabeli, dwuklik: nowa karta); dlatego lista ładuje też `goal_charts.js`, `player_details.js` i `team_details.js`. Wygląd tabeli, dialogu i klikalnego wiersza pochodzi z `static/css/admin.css`.

## Sprawdzenie zmiany

Testy tras, grupowania kontraktu i szczegółów są w `tests/interface/test_classifications.py`. Interakcja ma zachowanie zgodne z listami meczów i zawodników: dwuklik, Enter, Escape, przywrócenie fokusu oraz zapasowy link nowej karty.

## Układ tekstowy i mapa zmian

```text
[base.html: nawigacja]
Tabele
[szukaj] [sezon] [rozgrywki] [Filtruj] [Wyczyść]
+-----------------------------------------------------------+
| Sezon ↕ | Rozgrywki ↕ | Tabela ↕ | Grupa ↕ | Szczegóły |
+-----------------------------------------------------------+
[paginacja]
[dwuklik/Enter: modal Szczegóły tabeli / ×]
  [w modalu klik drużyny: modal Karta drużyny / × · dwuklik: nowa karta]
```

| Element | Plik / dane |
| --- | --- |
| Nagłówek, filtry, tabela i modal | `list.html`, `KlasyfikacjaFilterForm`, `[data-detail-*]` |
| Dane listy | `TabelaListView` → `KlasyfikacjaService` → `pobierz_tabele` |
| Szczegóły | [detail.md](detail.md), `administracja.szczegoly_tabeli` |
| Dwuklik i Enter | `static/js/classification_details.js`, `SzczegolyKlasyfikacjiController` |
| Paginacja | `partials/pagination.html`, `StronaKlasyfikacji` |
