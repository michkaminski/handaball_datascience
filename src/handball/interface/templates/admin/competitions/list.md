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

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Rozgrywki
| [miejsce na przegląd rozgrywek w kontekście sezonu]
| [filtry / kolumny / akcje: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Odczyt nazw do filtra meczów istnieje, ale ten ekran nie jest podłączony do widoku.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
