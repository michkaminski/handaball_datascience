# Wspólny układ administracji

Status: projekt szablonu. Plik `baza.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `baza.html`.

## Przeznaczenie

Wspólna szerokość strony, nagłówek, obszar nawigacji, miejsce na komunikaty i blok treści. Punkt odniesienia: wspólny układ prototypu v6.

## Dane wejściowe

Tytuł strony, aktywna sekcja i treść bloków dostarczanych przez szablon potomny. Dokładne nazwy bloków ustali implementacja.

## Powiązania

Wszystkie pełne strony dziedziczą ten układ. Korzysta z elementy/nawigacja.html i elementy/komunikaty.html.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj układ wspólny. Kolory, odstępy i typografię zmieniaj w statyczne/css/administracja.css; danych tabel nie zmieniaj w tym szablonie.

## Sprawdzenie zmiany

Sprawdź wszystkie strony potomne, szerokości ekranu, widoczność komunikatów i brak podwójnej nawigacji.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.
