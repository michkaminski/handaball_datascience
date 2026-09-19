# Drużyny

Status: projekt szablonu. Katalog `teams/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `teams.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/teams/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Drużyny" w sidebarze (grupa "Dane"). Docelowo przegląd drużyn (`public.zespoly`, 909 wierszy) i ich migawek sezonowych (`public.zespoly_sezony`, 3584 wiersze) — patrz [DATA.md](../../../../../../docs/DATA.md), rozróżnienie klubu/drużyny/migawki sezonowej.

## Dane wejściowe

Nieustalone. Prawdopodobnie lista drużyn filtrowana po sezonie, z nazwą z migawki sezonowej (`zespoly_sezony.nazwa`, nie `zespoly.nazwa` — ta sama zasada co w `MeczSQLAlchemyRepository.pobierz_liste`).

## Powiązania

Dziedziczyłby `base.html`. Model `Zespol`/`ZespolSezon` już istnieje (`infrastructure/database/models/teams.py`, etap 3), ale bez własnego widoku/serwisu/repozytorium dla tego ekranu. Wspomniane w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md) (etap 7: "Moduły teams.py... w potrzebnych warstwach"). Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `zespoly`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Planowane na etap 7.

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Drużyny
| [miejsce na przegląd drużyn i nazw sezonowych]
| [filtry / kolumny / akcje: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Przy ustalaniu kolumn trzeba rozróżnić zespół i jego nazwę w danym sezonie.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
