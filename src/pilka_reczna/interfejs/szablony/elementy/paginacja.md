# Paginacja list

Status: projekt szablonu. Plik `paginacja.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `elementy/paginacja.html`.

## Przeznaczenie

Przejście między stronami wyników z zachowaniem filtrów i sortowania.

## Dane wejściowe

Numer strony, rozmiar, liczba wyników oraz adresy przygotowane przez warstwę HTTP. Puste wyniki nie tworzą odnośnika do strony 0.

## Powiązania

Początkowo używany przez administracja/mecze/lista.html; przyszłe listy korzystają z tego samego kontraktu.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj wygląd przycisków i opis zakresu. Limity, walidację numeru i obliczanie wyników zmieniaj w odpowiednich klasach Pythona.

## Sprawdzenie zmiany

Sprawdź pierwszą i ostatnią stronę, pustą listę, pojedynczą stronę i zachowanie parametrów filtrów.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.
