# Logi aplikacji

Status: projekt szablonu. Katalog `logs/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `logs.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/logs/list.html` (nazwa robocza).

## Przeznaczenie

Obsługuje pozycję "Logi aplikacji" w sidebarze (grupa "Narzędzia") oraz pozycję "Logi" w górnym pasku. Docelowo przegląd historii zmian ze schematu `logs` (tabele `*_log`, patrz [LOGS_SCHEMA](../../../../../../docs/database/LOGS_SCHEMA.md)) — kto/co/kiedy zmienił dany rekord.

## Dane wejściowe

Nieustalone. Historia `*_log` zawiera wiele obrazów tego samego rekordu (`log_id` jest kluczem wpisu historii, `log_klucz` opisuje klucz obiektu źródłowego — patrz [RELATIONSHIPS](../../../../../../docs/database/RELATIONSHIPS.md)). Obsługa `logs` wymaga jawnego kwalifikowania nazw schematu w zapytaniach (search_path sesji go nie zawiera).

## Powiązania

Dziedziczyłby `base.html`. Modele schematu `logs` jeszcze nie istnieją w `infrastructure/database/models/`. Pozycje menu w `interface/navigation.py` (`GORNY_PASEK` klucz `logs`; `SIDEBAR` grupa "Narzędzia", klucz `logi_aplikacji`) mają obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Zbliżone do etapu 7 z [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md) ("Modele schematu logs oraz repozytoria i widoki diagnostyki — wyłącznie odczyt istniejących importów, anomalii i historii").

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Logi aplikacji
| [miejsce na przegląd logów]
| [źródło / filtry / kolumny: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Najpierw należy ustalić, jakie logi i dane są przeznaczone do pokazania użytkownikowi.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
