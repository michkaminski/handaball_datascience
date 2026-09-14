# Strzelcy

Status: projekt szablonu. Katalog `scorers/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `scorers.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/scorers/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Strzelcy" w sidebarze (grupa "Dane"). Docelowo klasyfikacja strzelców z `public.strzelcy` — patrz [database/README](../../../../../../docs/database/README.md).

## Dane wejściowe

Nieustalone. Prawdopodobnie ranking zawodników po liczbie bramek w wybranym sezonie/rozgrywkach. Podobna uwaga jak przy Zawodnikach: rozróżnić kompletność danych źródłowych od realnej liczby bramek (patrz [DATA.md](../../../../../../docs/DATA.md)).

## Powiązania

Dziedziczyłby `base.html`. Naturalnie powiązane z ekranem Zawodnicy (`admin/players/list.md`) — może współdzielić część logiki agregacji bramek. Model `strzelcy` jeszcze nie istnieje w `infrastructure/database/models/`. Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `strzelcy`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Nie ma przypisanego etapu w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md); rozważyć razem z Zawodnicy (etap 7).
