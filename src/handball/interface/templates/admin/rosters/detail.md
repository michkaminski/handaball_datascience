# Szczegóły składu

## Przeznaczenie

Widok `GET /administracja/sklady/<id_zespol_sezon>` pokazuje zawodników zgłoszonych do jednej drużyny w sezonie. Jest pełną stroną oraz fragmentem pobieranym do modalu listy. Zgłoszenie nie jest interpretowane jako występ w meczu.

`SkladSzczegolyView` pobiera `SzczegolySkladu` przez `KlasyfikacjaService`, a `SkladPresenter` sortuje zawodników według pozycji, numeru i nazwiska oraz przypisuje pozycjom tę samą pastelową paletę co w składach meczowych. Brak składu zwraca 404, a błąd odczytu 503. Każdy zawodnik ma link do istniejącej karty zawodnika.

## Układ tekstowy i mapa zmian

```text
[base.html: nawigacja; w modalu pominięta]
Start › Dane › Składy › Szczegóły
[drużyna]
[sezon · rozgrywki po przecinku]
[Powrót do listy; usuwany w modalu]
+----------------------------------------------------------------+
| Pozycja [kolor] | Nr | Zawodnik | Wzrost | Waga | Szczegóły zawodnika |
+----------------------------------------------------------------+
[informacja: zgłoszenie sezonowe, nie występy]
```

| Element | Plik / dane |
| --- | --- |
| Nagłówek i tabela | `detail.html`, `szczegoly.sklad`, `szczegoly.zawodnicy` |
| Dane | `SkladSzczegolyView` → `pobierz_szczegoly_skladu` |
| Sortowanie i kolory | `SkladPresenter`, `.roster-player`, `--position-hue` |
| Karta zawodnika | `administracja.szczegoly_zawodnika` |
| Modal | [list.md](list.md), `classification_details.js`, `[data-classification-detail]` |
