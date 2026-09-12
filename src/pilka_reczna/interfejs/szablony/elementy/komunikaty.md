# Komunikaty dla użytkownika

Status: etap 2 ukończony. Szablon `elementy/komunikaty.html` istnieje.

Docelowy szablon względem katalogu szablony: `elementy/komunikaty.html`.

## Przeznaczenie

Prezentacja komunikatów powodzenia, ostrzeżeń i błędów przekazanych przez aplikację (mechanizm Flask `flash()`).

## Dane wejściowe

`get_flashed_messages(with_categories=true)` — lista par `(kategoria, treść)` z sesji Flask. Kategoria trafia bezpośrednio do klasy CSS `notice-{{ kategoria }}` (np. `notice-error`, `notice-warning`, `notice-success`); Jinja2 automatycznie escapuje treść (autoescape włączony domyślnie we Flasku), więc nie renderuj tej treści przez `| safe`.

## Powiązania

Dołączany przez `baza.html` przez `{% include %}`, wewnątrz `<main class="content">`; wygląd współdzielony przez wszystkie strony. Style `.komunikaty`, `.notice`, `.notice-error`, `.notice-warning`, `.notice-success` są w statyczne/css/administracja.css.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj układ i oznaczenia komunikatów. Decyzja o ich wyświetleniu (wywołanie `flash(tresc, kategoria)`) należy do widoku/serwisu; nie umieszczaj tu wyjątków sterownika ani sekretów.

## Sprawdzenie zmiany

Sprawdź brak komunikatów, wiele komunikatów, długi tekst i bezpieczne renderowanie treści.

## Stan implementacji

Wykonano: sprawdzenie w przeglądarce przy braku komunikatów (żaden widok jeszcze nie wywołuje `flash()`) — blok poprawnie się nie renderuje (`{% if komunikaty %}`). Nie sprawdzono jeszcze: wielu komunikatów naraz, długiego tekstu, wielu kategorii jednocześnie ani faktycznego bezpiecznego renderowania złośliwej treści — do zweryfikowania, gdy pierwszy widok zacznie używać `flash()`.
