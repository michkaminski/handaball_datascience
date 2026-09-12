# Strona startowa administracji

Status: etap 2 ukończony (wygląd bez danych). Szablon `administracja/start.html` istnieje.

Docelowy szablon względem katalogu szablony: `administracja/start.html`.

## Przeznaczenie

Start panelu oparty na index.html prototypu v6. Docelowo tabela meczów ma być jego główną częścią; na tym etapie panel "Mecze" pokazuje jawny stan bez danych zamiast przykładowych wierszy z prototypu.

## Dane wejściowe

`pozycje_nawigacji`: lista pozycji menu przekazana przez `WidokStartowy` (patrz elementy/nawigacja.md). Na tym etapie brak danych meczowych — panel wyświetla tekst informujący, że integracja z bazą jeszcze nie istnieje. Po etapach 3–4 doda dane rzeczywistej listy meczów (wynik przypadku użycia `SerwisMeczow.pobierz_liste`).

## Powiązania

Dziedziczy `baza.html` (`{% extends %}`). Widok: `WidokStartowy` w `interfejs/administracja/widoki/start.py`, zarejestrowany pod `/administracja/` w Blueprint `administracja`.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj zawartość strony startowej. Wspólną prezentację tabeli wydziel do osobnego fragmentu z własnym MD, jeśli będzie użyta również na liście; nie duplikuj logiki danych.

## Sprawdzenie zmiany

Sprawdź stan przed integracją, pustą listę, brak części danych i zgodność hierarchii treści z prototypem.

## Stan implementacji

Wykonano: `testy/interfejs/test_start.py` sprawdza status 200 i obecność marki/nawigacji w odpowiedzi; sprawdzenie wizualne w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px potwierdza układ zgodny z prototypem v6 (pagehead + panel) i poprawną responsywność. Nie sprawdzono: rzeczywistej tabeli meczów (nie istnieje jeszcze — planowana etap 3–4), zachowania przy błędzie bazy.
