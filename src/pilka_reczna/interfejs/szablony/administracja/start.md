# Strona startowa administracji

Status: projekt szablonu. Plik `start.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `administracja/start.html`.

## Przeznaczenie

Start panelu oparty na index.html prototypu v6. Docelowo tabela meczów ma być jego główną częścią.

## Dane wejściowe

W etapie wyglądu jawnie oznaczony stan bez danych; po integracji wynik przypadku użycia listy meczów i ewentualne uzgodnione podsumowania.

## Powiązania

Dziedziczy baza.html. Planowany widok: WidokStartowy w interfejs/administracja/widoki/start.py.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj zawartość strony startowej. Wspólną prezentację tabeli wydziel do osobnego fragmentu z własnym MD, jeśli będzie użyta również na liście; nie duplikuj logiki danych.

## Sprawdzenie zmiany

Sprawdź stan przed integracją, pustą listę, brak części danych i zgodność hierarchii treści z prototypem.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.
