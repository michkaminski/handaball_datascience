# Strona startowa administracji

Status: etap 4 ukończony. Szablon `admin/start.html` odwzorowuje pełną strukturę `index.html` prototypu v6 (nagłówek strony, filtry, tabela meczów) na wyraźne polecenie użytkownika ("weź prototyp i pod niego będzie wszystko budowane") — bez okrojonej wersji z samym komunikatem tekstowym.

Docelowy szablon względem katalogu szablony: `admin/start.html`.

## Przeznaczenie

Start panelu oparty na index.html prototypu v6. Docelowo tabela meczów ma pokazywać podgląd ostatnich meczów; pełna, filtrowana lista jest już dostępna pod osobnym adresem (`admin/matches/list.html`). Na tym etapie sekcja filtrów i tabela mają pełną strukturę prototypu (nagłówki kolumn, pola filtrów), ale bez fikcyjnych wierszy — tabela ma jeden wiersz `colspan` z jawną informacją, filtry nie są jeszcze podłączone do żadnej logiki (brak `action`/JS). Przycisk "Pełna lista meczów" prowadzi do prawdziwego, działającego widoku (`administracja.lista_meczow`).

## Dane wejściowe

`sekcja_aktywna="start"` przekazywana przez `StartView` (patrz partials/navigation.md i base.md — sam zestaw pozycji menu jest teraz globalny, nie budowany przez ten widok). Na tym etapie brak danych meczowych na samej stronie startowej — tabela wyświetla tekst informujący, gdzie znaleźć rzeczywiste dane. Podgląd ostatnich meczów bezpośrednio na stronie startowej jest świadomie odłożony (patrz "Stan implementacji").

## Powiązania

Dziedziczy `base.html` (`{% extends %}`). Widok: `StartView` w `interface/admin/views/start.py`, zarejestrowany pod `/administracja/` w Blueprint `admin`.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj zawartość strony startowej. Wspólną prezentację tabeli wydziel do osobnego fragmentu z własnym MD, jeśli będzie użyta również na liście; nie duplikuj logiki danych.

## Sprawdzenie zmiany

Sprawdź stan przed integracją, pustą listę, brak części danych i zgodność hierarchii treści z prototypem.

## Stan implementacji

Wykonano: `tests/interface/test_start.py` sprawdza status 200 i obecność marki/nawigacji w odpowiedzi; sprawdzenie wizualne w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px oraz bezpośrednie porównanie zrzutu z prototypem (`index.html`) potwierdza zgodność struktury (nagłówek, filtry, tabela, pełny sidebar). Przycisk "Pełna lista meczów" sprawdzony ręcznie — prowadzi do działającego widoku z rzeczywistymi danymi z bazy `zprp`. Nie sprawdzono/nie zrobiono: podglądu ostatnich meczów bezpośrednio na tej stronie (zamiast wiersza informacyjnego) — to świadomie odłożona decyzja projektowa, nie błąd; samego formularza filtrów na tej stronie (nie jest jeszcze podłączony do żadnej logiki, w przeciwieństwie do filtrów na `matches/list.html`).

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `start.html`. Rama strony pochodzi z `base.html`. Pola filtrów na tej stronie są makietą bez obsługi danych.

```text
[wspólny nagłówek] -> [górne menu: Start aktywne]
+------------------+-------------------------------------------------------+
| wspólny sidebar  | [☰ Menu na wąskim ekranie] [komunikaty, jeżeli są]      |
|                  | (1) Start › Mecze                                    |
|                  |     OSTATNIE MECZE I ZARZĄDZANIE DANYMI               |
|                  |     Najważniejsza część panelu: lista meczów...       |
|                  |                                                       |
|                  | (2) FILTRY — jeszcze nie działają                    |
|                  | [Sezon v] [Rozgrywki v] [Kolejka v]                   |
|                  | [Drużyna v] [Status v] [Szukaj: tekst]                |
|                  |                                                       |
|                  | (3) [Pełna lista meczów]   Podgląd ... w kolejnym etapie|
|                  |                                                       |
|                  | (4) ID | Data | Godz. | Rozgrywki | Kol. |            |
|                  |     Gospodarz | Wynik | Gość | Status                |
|                  |     Podgląd ostatnich meczów ... nie został wdrożony |
+------------------+-------------------------------------------------------+
[wspólna stopka]
```

Rysunek zawija długi wiersz filtrów i nagłówki tabeli. W HTML kolejność elementów jest taka jak powyżej. Nie ma przycisku wysłania filtrów ani formularza GET. Działa odnośnik „Pełna lista meczów”, prowadzący do `/administracja/mecze`. Jedyny wiersz tabeli jest komunikatem, nie prawdziwym meczem.

Siatka filtrów zmienia liczbę kolumn przy 1100, 700 i 430 px, tak samo jak na liście meczów. Wspólny sidebar i przycisk mobilnego menu opisuje `base.md`.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Nagłówek strony | [start.html](start.html) | `.pagehead`, `.crumb`, `<h1>`, opis i blok `tytul`. |
| 2. Makieta filtrów | [start.html](start.html) | `.panel-body.filters`; podłączenie filtrów wymaga dodatkowo danych i logiki widoku, nie tylko zmiany etykiet. |
| 3. Odnośnik i notatka | [start.html](start.html) | `.toolbar .left` i `.toolbar .right`; cel linku to `administracja.lista_meczow`. |
| 4. Tabela i komunikat | [start.html](start.html) | `<thead>` oraz jedyny wiersz `<tbody>` z `colspan="9"`. |
| Dostarczenie prawdziwego podglądu | [start.py](../../admin/views/start.py) | `StartView.get()` obecnie tylko renderuje szablon. Nie dostarcza listy meczów. |
| Rozmiary i zawijanie | [admin.css](../../static/css/admin.css) | `.filters`, `.toolbar`, `.table-wrap`, `.note` i zapytania `@media`. |
