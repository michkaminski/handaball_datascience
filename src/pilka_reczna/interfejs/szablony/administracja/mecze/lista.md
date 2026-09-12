# Lista meczów

Status: projekt szablonu. Plik `lista.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `administracja/mecze/lista.html`.

## Przeznaczenie

Tabela meczów i zwarte filtry na podstawie matches.html prototypu v6.

## Dane wejściowe

FiltryMeczow, StronaMeczow oraz opcje wyboru sezonu, rozgrywek, rundy i kolejki. Są to planowane obiekty; nazwy zmiennych Jinja2 uzupełnij podczas implementacji.

## Powiązania

WidokListyMeczow → SerwisMeczow → RepozytoriumOdczytuMeczow. Dziedziczy baza.html i dołącza elementy/paginacja.html.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj kolumny, etykiety i układ filtrów. Nowe dane dodawaj w obiekcie wyniku i odpowiednim przypadku użycia; filtrowanie i SQL pozostają poza szablonem.

## Sprawdzenie zmiany

Sprawdź brak drużyny lub wyniku, pustą listę, paginację, sortowanie, link do szczegółów i zgodność z prototypem.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.
