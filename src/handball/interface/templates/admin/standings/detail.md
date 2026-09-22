# Szczegóły tabeli

## Przeznaczenie

Widok `GET /administracja/tabele/<id_tabela_grupa>` pokazuje źródłowe pozycje jednej grupy tabeli. Jest pełną stroną oraz fragmentem pobieranym do modalu listy. Nie przelicza kolejności ani punktów.

`TabelaSzczegolyView` pobiera `SzczegolyTabeli` przez `KlasyfikacjaService` po `tabele_grupy.id`. Brak grupy zwraca 404, a błąd odczytu 503. `[data-classification-detail]` wyznacza fragment modalu; `[data-detail-navigation]` jest w nim usuwany.

## Układ tekstowy i mapa zmian

```text
[base.html: nawigacja; w modalu pominięta]
Start › Dane › Tabele › Szczegóły
[nazwa tabeli]
[sezon · rozgrywki · grupa]
[Powrót do listy; usuwany w modalu]
+------------------------------------------------------------------------+
| Grupa | M. | Drużyna | M | Pkt | Z | R | RW | RP | P | Bramki | ... |
+------------------------------------------------------------------------+
[informacja o danych źródłowych]
```

| Element | Plik / dane |
| --- | --- |
| Nagłówek i tabela | `detail.html`, `szczegoly.tabela`, `szczegoly.pozycje` |
| Dane | `TabelaSzczegolyView` → `pobierz_szczegoly_tabeli` |
| Modal | [list.md](list.md), `classification_details.js`, `[data-classification-detail]` |
