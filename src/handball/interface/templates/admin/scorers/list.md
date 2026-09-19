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

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Strzelcy
| [miejsce na klasyfikację strzelców]
| [filtry / kolumny / zakres danych: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Przy projektowaniu trzeba odróżnić brak danych od zerowej liczby bramek.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
