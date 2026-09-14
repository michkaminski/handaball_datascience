# Sędziowie

Status: projekt szablonu. Katalog `referees/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `referees.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/referees/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Sędziowie" w sidebarze (grupa "Dane"). Docelowo słownik sędziów (`public.sedziowie`, 1158 wierszy) i ich udział w meczach (`public.mecze_sedziowie`) — patrz [PUBLIC_SCHEMA](../../../../../../docs/database/PUBLIC_SCHEMA.md).

## Dane wejściowe

Nieustalone. Prawdopodobnie lista sędziów z liczbą prowadzonych meczów.

## Powiązania

Dziedziczyłby `base.html`. Model `sedziowie`/`mecze_sedziowie` jeszcze nie istnieje w `infrastructure/database/models/`. Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `sedziowie`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Nie ma przypisanego etapu w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md).
