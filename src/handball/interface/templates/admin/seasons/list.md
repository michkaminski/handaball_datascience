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

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Sezony
| [miejsce na przegląd sezonów]
| [filtry / kolumny / akcje: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Nie ma jeszcze własnego ekranu sezonów; istniejący odczyt opcji sezonów dla listy meczów nie jest implementacją tego ekranu.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
