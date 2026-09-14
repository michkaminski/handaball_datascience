# Rozgrywki

Status: projekt szablonu. Katalog `competitions/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `competitions.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/competitions/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Rozgrywki" w sidebarze (grupa "Dane"). Docelowo przegląd rozgrywek z `public.rozgrywki` (506 wierszy) w danym sezonie — nazwa, kategoria, płeć, liczba drużyn.

## Dane wejściowe

Nieustalone. Prawdopodobnie lista rozgrywek filtrowana po sezonie (podobnie jak filtr `id_rozgrywki` na liście meczów — patrz `admin/matches/list.md`), z linkiem do listy meczów danych rozgrywek.

## Powiązania

Dziedziczyłby `base.html`. Widok, serwis i repozytorium jeszcze nie istnieją. Naturalnie powiązane z listą meczów (`admin/matches/list.html`) — filtr `id_rozgrywki` już tam istnieje. Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `rozgrywki`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Nie ma przypisanego etapu w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md); rozważyć razem z Sezonami.
