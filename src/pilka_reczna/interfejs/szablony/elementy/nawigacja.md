# Nawigacja administracji

Status: projekt szablonu. Plik `nawigacja.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `elementy/nawigacja.html`.

## Przeznaczenie

Menu sekcji i oznaczenie bieżącego ekranu, zgodne z prototypem v6.

## Dane wejściowe

Aktywna sekcja, dostępne adresy i uprawnienia przekazane przez warstwę HTTP; bez zapytań do bazy.

## Powiązania

Dołączany przez baza.html. Nowa pozycja wymaga istniejącego widoku i poprawnego adresu.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj etykiety, kolejność i aktywne pozycje menu. Ukrycie odnośnika nie zastępuje kontroli uprawnień w backendzie.

## Sprawdzenie zmiany

Sprawdź adresy, aktywną sekcję, obsługę klawiatury i zachowanie na wąskim ekranie.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.
