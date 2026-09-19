# Paginacja list

Status: etap 4 ukończony. Szablon `partials/pagination.html` istnieje.

Docelowy szablon względem katalogu szablony: `partials/pagination.html`.

## Przeznaczenie

Przejście między stronami wyników z zachowaniem filtrów i sortowania.

## Dane wejściowe

`strona`: `StronaMeczow` (liczba_wszystkich, strona, rozmiar_strony) z kontekstu widoku. Odnośniki budowane przez `url_for(request.endpoint, **dict(request.args, strona=...))`, więc automatycznie zachowują wszystkie bieżące parametry zapytania (filtry, sortowanie) — zmienia się tylko `strona`. Puste wyniki (`liczba_wszystkich == 0`) nie renderują żadnego odnośnika.

## Powiązania

Używany przez `admin/matches/list.html`; przyszłe listy (np. zawodnicy, drużyny) mogą dołączać ten sam fragment, jeśli będą zwracać obiekt z tymi samymi czterema polami.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj wygląd przycisków i opis zakresu. Limity, walidację numeru strony i obliczanie wyników zmieniaj w `FiltryMeczow`/`MeczSQLAlchemyRepository`, nie w tym szablonie.

## Sprawdzenie zmiany

Sprawdź pierwszą i ostatnią stronę, pustą listę, pojedynczą stronę i zachowanie parametrów filtrów.

## Stan implementacji

Wykonano: sprawdzono ręcznie wobec rzeczywistej bazy `zprp` (sezon 195, 1817 meczów, rozmiar strony 20 → 91 stron) — pierwsza strona pokazuje tylko "Następna »", strona 2 pokazuje też "« Poprzednia" z zachowanym `id_sezon` w adresie, pusty wynik nie pokazuje żadnego odnośnika. Nie sprawdzono: zachowania na ostatniej stronie zbioru (tylko "« Poprzednia").

## Układ tekstowy i mapa zmian

Stan: istniejący fragment pod tabelą meczów. Liczby w rysunku są wyłącznie przykładem prezentacji.

```text
[koniec tabeli]
(1) Wyniki 21–40 z 100                 (2) [« Poprzednia] [Następna »]
```

- Cały fragment istnieje tylko, gdy `strona.liczba_wszystkich > 0`.
- „« Poprzednia” pojawia się przy `strona.strona > 1`.
- „Następna »” pojawia się, gdy `strona.strona * strona.rozmiar_strony < strona.liczba_wszystkich`.
- Na jednej stronie wyników pozostaje licznik bez przycisków. Nie ma numerowanych przycisków stron ani pola „przejdź do strony”.
- Linki zachowują parametry bieżącego adresu i zmieniają numer strony. Na wąskim ekranie `.toolbar` i `.right` mogą zawijać elementy.
- Fragment wylicza zakres bez normalizowania zbyt dużego numeru strony. Przy ręcznym podaniu strony poza końcem danych licznik może pokazać początek większy od końca; rysunek opisuje zwykły, poprawny zakres.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Napis i obliczenia zakresu | [pagination.html](pagination.html) | `span.note`, pola `strona`, `rozmiar_strony`, `liczba_wszystkich`. |
| 2. Etykiety, warunki i linki | [pagination.html](pagination.html) | Warunki Jinja2 oraz `url_for(request.endpoint, **dict(request.args, strona=...))`. |
| Ułożenie i rozmiar przycisków | [admin.css](../../static/css/admin.css) | `.toolbar`, `.toolbar .right`, `.note`, `.btn.secondary.small`; klasa `.paginacja` oznacza fragment, ale nie ma osobnej reguły CSS. |
| Miejsce pod tabelą | [list.html](../admin/matches/list.html) | Include po `.table-wrap`. |
| Limity i pobieranie strony | [matches.py](../../../domain/matches.py) | `FiltryMeczow` waliduje rozmiar i numer; repozytorium meczów stosuje LIMIT/OFFSET. |
