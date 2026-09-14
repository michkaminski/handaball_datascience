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
