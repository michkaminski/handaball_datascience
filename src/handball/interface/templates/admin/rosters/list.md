# Składy

Status: projekt szablonu. Katalog `rosters/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `squads.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/rosters/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Składy" w sidebarze (grupa "Dane"). Docelowo przegląd znormalizowanych składów zespołu (`public.sklady`, 74 731 wierszy) i ich wersji (`public.sklady_wersje`, `public.sklady_wersje_zawodnicy`) — patrz [database/README](../../../../../../docs/database/README.md).

## Dane wejściowe

Nieustalone. `public.sklady` to skład zespołu w sezonie z pozycją i migawką zawodnika — "nie jest to lista występów meczowych" (patrz PUBLIC_SCHEMA.md, opis tabeli). Rozróżnienie od `mecze_zawodnicy` (występy meczowe) trzeba jasno pokazać w interfejsie, żeby nie sugerować czegoś innego niż dane zawierają.

## Powiązania

Dziedziczyłby `base.html`. Model `sklady`/`sklady_wersje` jeszcze nie istnieje w `infrastructure/database/models/`. Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `sklady`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Nie ma przypisanego etapu w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md); prawdopodobnie razem z Zawodnicy (etap 7) ze względu na wspólne tabele źródłowe.
