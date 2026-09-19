# Hale

Status: projekt szablonu. Katalog `venues/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `halls.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/venues/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Hale" w sidebarze (grupa "Dane"). Docelowo słownik hal sportowych (`public.hale`) i ich wykorzystanie w meczach (`mecze.id_hala`) — patrz [PUBLIC_SCHEMA](../../../../../../docs/database/PUBLIC_SCHEMA.md).

## Dane wejściowe

Nieustalone. Prawdopodobnie prosta lista hal, ewentualnie z liczbą rozegranych w nich meczów.

## Powiązania

Dziedziczyłby `base.html`. Model `hale` jeszcze nie istnieje w `infrastructure/database/models/`; `Mecz.id_hala` też nie jest jeszcze zmapowany (dodano tylko pola potrzebne liście meczów w etapie 3). Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `hale`) ma obecnie `punkt_koncowy=None`.

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
| Hale
| [miejsce na słownik hal i ich wykorzystanie]
| [filtry / kolumny / akcje: nieustalone]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Model Hala i odczyt opcji hal dla listy meczów istnieją; osobnego ekranu hal jeszcze nie ma.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
