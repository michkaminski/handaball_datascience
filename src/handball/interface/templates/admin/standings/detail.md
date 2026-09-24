# Szczegóły tabeli

## Przeznaczenie

Widok `GET /administracja/tabele/<id_tabela_grupa>` pokazuje źródłowe pozycje jednej grupy tabeli. Jest pełną stroną oraz fragmentem pobieranym do modalu listy. Nie przelicza kolejności ani punktów.

`TabelaSzczegolyView` pobiera `SzczegolyTabeli` przez `KlasyfikacjaService` po `tabele_grupy.id`. Brak grupy zwraca 404, a błąd odczytu 503. `[data-classification-detail]` wyznacza fragment modalu; `[data-detail-navigation]` jest w nim usuwany.

Kolumny: grupa, miejsce, drużyna, mecze, punkty, Z, R, RW, RP, P, bramki i bonus. Kolumna „Bonus” jest renderowana tylko wtedy, gdy `SzczegolyTabeli.ma_punkty_bonusowe` jest prawdą, czyli choć jedna pozycja ma `punkty_bonusowe` różne od `NULL`; wartość `0` jest daną i pokazuje kolumnę. Kolumna „Kryteria” nie jest pokazywana, a `PozycjaTabeli` nie przenosi już tego pola.

Nazwa drużyny jest linkiem `[data-team-modal-link]` do `administracja.szczegoly_druzyny` po `tabele_wiersze.id_zespol`. Pojedyncze kliknięcie otwiera kartę drużyny w oknie `[data-team-modal-dialog]` (po 250 ms, aby odróżnić je od dwukliku), dwuklik otwiera kartę w nowej karcie, a kliknięcie z modyfikatorem lub środkowym przyciskiem pozostaje obsługą przeglądarki. Okno pobiera `[data-team-detail]`, usuwa `[data-team-navigation]`, uruchamia zakładki drużyny i okno zawodnika. Filtry, sortowanie i paginacja karty drużyny wczytują się w tym samym oknie. Okno drużyny znajduje się wewnątrz `[data-classification-detail]`, więc działa zarówno na pełnej stronie, jak i w modalu listy tabel.

## Układ tekstowy i mapa zmian

```text
[base.html: nawigacja; w modalu pominięta]
Start › Dane › Tabele › Szczegóły
[nazwa tabeli]
[sezon · rozgrywki · grupa]
[Powrót do listy; usuwany w modalu]
+------------------------------------------------------------------------+
| Grupa | M. | Drużyna* | M | Pkt | Z | R | RW | RP | P | Bramki | [Bonus]|
+------------------------------------------------------------------------+
[informacja o danych źródłowych]
* klik: modal Karta drużyny / × · dwuklik: nowa karta
[Bonus] tylko gdy któraś pozycja ma punkty bonusowe
```

| Element | Plik / dane |
| --- | --- |
| Nagłówek i tabela | `detail.html`, `szczegoly.tabela`, `szczegoly.pozycje` |
| Dane | `TabelaSzczegolyView` → `pobierz_szczegoly_tabeli` |
| Modal | [list.md](list.md), `classification_details.js`, `[data-classification-detail]` |
| Kolumna Bonus | `szczegoly.ma_punkty_bonusowe`, `SzczegolyTabeli` w `domain/classifications.py` |
| Link i okno drużyny | `[data-team-modal-link]`, `[data-team-modal-dialog]`, `[data-team-content]`, `[data-team-open-tab]`; `LinkiDruzynController`, `OknoDruzynyController` w `classification_details.js` |
| Karta drużyny w oknie | [../teams/detail.md](../teams/detail.md), `HandballDruzyna.ZakladkiDruzynyController` w `team_details.js`; skrypty `goal_charts.js`, `player_details.js`, `team_details.js` |
