# Tabele

Status: projekt szablonu. Katalog `standings/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `standings.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/standings/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Tabele" w sidebarze (grupa "Dane"). Docelowo tabela klasyfikacji rozgrywek z `public.tabele`, `public.tabele_grupy`, `public.tabele_wiersze` — patrz [database/README](../../../../../../docs/database/README.md).

## Dane wejściowe

Nieustalone. Prawdopodobnie klasyfikacja dla wybranego sezonu/rozgrywek/grupy, z pozycją, punktami, bilansem bramek. Zasady punktacji do potwierdzenia w danych, nie do zgadnięcia z nazw rozgrywek (patrz [DATA.md](../../../../../../docs/DATA.md)).

## Powiązania

Dziedziczyłby `base.html`. Wspomniane pośrednio w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md) (etap 7: "standings.py"). Model `tabele` jeszcze nie istnieje w `infrastructure/database/models/`. Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `tabele`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Planowane na etap 7 (jako `standings.py`).

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Tabele
| [miejsce na klasyfikację rozgrywek]
| [wybór kontekstu / kolumny / punktacja: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Punktacji nie należy wyprowadzać z samej nazwy rozgrywek. Układ i interpretacja danych wymagają potwierdzenia.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
