# Komunikaty dla użytkownika

Status: etap 2 ukończony. Szablon `partials/messages.html` istnieje.

Docelowy szablon względem katalogu szablony: `partials/messages.html`.

## Przeznaczenie

Prezentacja komunikatów powodzenia, ostrzeżeń i błędów przekazanych przez aplikację (mechanizm Flask `flash()`).

## Dane wejściowe

`get_flashed_messages(with_categories=true)` — lista par `(kategoria, treść)` z sesji Flask. Kategoria trafia bezpośrednio do klasy CSS `notice-{{ kategoria }}` (np. `notice-error`, `notice-warning`, `notice-success`); Jinja2 automatycznie escapuje treść (autoescape włączony domyślnie we Flasku), więc nie renderuj tej treści przez `| safe`.

## Powiązania

Dołączany przez `base.html` przez `{% include %}`, wewnątrz `<main class="content">`; wygląd współdzielony przez wszystkie strony. Style `.komunikaty`, `.notice`, `.notice-error`, `.notice-warning`, `.notice-success` są w static/css/admin.css.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj układ i oznaczenia komunikatów. Decyzja o ich wyświetleniu (wywołanie `flash(tresc, kategoria)`) należy do widoku/serwisu; nie umieszczaj tu wyjątków sterownika ani sekretów.

## Sprawdzenie zmiany

Sprawdź brak komunikatów, wiele komunikatów, długi tekst i bezpieczne renderowanie treści.

## Stan implementacji

Wykonano: sprawdzenie w przeglądarce przy braku komunikatów (żaden widok jeszcze nie wywołuje `flash()`) — blok poprawnie się nie renderuje (`{% if komunikaty %}`). Nie sprawdzono jeszcze: wielu komunikatów naraz, długiego tekstu, wielu kategorii jednocześnie ani faktycznego bezpiecznego renderowania złośliwej treści — do zweryfikowania, gdy pierwszy widok zacznie używać `flash()`.

## Układ tekstowy i mapa zmian

Stan: istniejący fragment komunikatów wewnątrz `<main>`, przed treścią strony.

```text
[☰ Menu — jeżeli widoczny we wspólnym układzie]
(1) KOMUNIKATY — tylko gdy lista nie jest pusta
    [treść pierwszego komunikatu]   .notice.notice-{kategoria}
    [treść kolejnego komunikatu]    .notice.notice-{kategoria}
[treść konkretnej strony]
```

Komunikaty są wyświetlane jeden pod drugim, w kolejności otrzymanej z `get_flashed_messages(with_categories=true)`. Pusta lista nie tworzy nawet kontenera `.komunikaty`. Nie ma przycisku zamknięcia ani automatycznego znikania. Długi tekst może się zawijać. `error`, `warning` i `success` mają osobne style kolorystyczne; aktualne widoki nie wywołują jeszcze `flash()`.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Układ i znaczniki komunikatów | [messages.html](messages.html) | Warunek `{% if komunikaty %}`, pętla i `.notice.notice-{{ kategoria }}`. |
| Odstępy i kolory kategorii | [admin.css](../../static/css/admin.css) | `.komunikaty`, `.notice`, `.notice.notice-error`, `.notice.notice-warning`, `.notice.notice-success`. |
| Położenie względem treści | [base.html](../base.html) | Include `partials/messages.html` przed blokiem `tresc`. |
| Treść i moment powstania komunikatu | [match_views.py](../../admin/views/match_views.py) | W przyszłości wywołanie `flash()` należy umieścić w odpowiednim adapterze HTTP. Ten widok obecnie z niego nie korzysta; serwis domenowy nie powinien zależeć od Flask flash. |
