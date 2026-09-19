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

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Sędziowie
| [miejsce na przegląd sędziów]
| [filtry / kolumny / akcje: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Nie ma ustalonego kontraktu danych ani gotowego HTML tej strony.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
