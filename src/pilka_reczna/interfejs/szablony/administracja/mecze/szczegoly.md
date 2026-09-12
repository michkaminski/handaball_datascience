# Szczegóły meczu

Status: projekt szablonu. Plik `szczegoly.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `administracja/mecze/szczegoly.html`.

## Przeznaczenie

Prezentacja meczu według match_detail.html prototypu v6: uczestnicy, wynik, składy i dostępne statystyki.

## Dane wejściowe

SzczegolyMeczu z przygotowanym wynikiem, składami i ostrzeżeniami. Braki danych pozostają jawne; nie trafiają tu modele ORM wymagające lazy loading.

## Powiązania

WidokSzczegolowMeczu → SerwisMeczow → RepozytoriumOdczytuMeczow. Dziedziczy baza.html; brak meczu obsługuje strona 404.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj sekcje i prezentację. Interpretację zamiana, wyniku, serii karnych i agregacji zmieniaj w klasach Pythona po potwierdzeniu danych.

## Sprawdzenie zmiany

Sprawdź niepełne składy, brak wyniku, ostrzeżenia, długie nazwy i bezpieczne odnośniki. Nie dodawaj edycji bez zlecenia.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.
