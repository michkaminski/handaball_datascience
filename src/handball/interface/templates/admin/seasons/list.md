# Sezony

Status: projekt szablonu. Katalog `seasons/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `seasons.html` — w prototypie to strona-placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`; nie ma jeszcze wzorca kolumn/filtrów do skopiowania.

Docelowy szablon względem katalogu szablony: `admin/seasons/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Sezony" w sidebarze (grupa "Dane", pierwsza pozycja). Docelowo przegląd sezonów z bazy `zprp` (`public.sezony`: 20 wierszy, patrz [database/README](../../../../../../docs/database/README.md)) — nazwa, rok rozpoczęcia, liczba rozgrywek, stan.

## Dane wejściowe

Nieustalone. Prawdopodobnie lista sezonów z `public.sezony`, bez filtrów (tabela ma tylko 20 wierszy). Ustalić przy implementacji, czy potrzebny jest osobny widok szczegółów sezonu, czy tylko lista.

## Powiązania

Dziedziczyłby `base.html`. Widok, serwis i repozytorium jeszcze nie istnieją. Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `sezony`) ma obecnie `punkt_koncowy=None`, renderuje się jako `href="#"`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Nie ma przypisanego etapu w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md); rozważyć przy planowaniu etapu 7 lub później, razem z Rozgrywkami.
