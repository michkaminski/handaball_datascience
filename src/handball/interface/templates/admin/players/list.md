# Zawodnicy

Status: projekt szablonu. Katalog `players/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `players.html` — jedna z niewielu podstron prototypu z rzeczywistą treścią (nie placeholder): filtry (sezon, rozgrywki, klub, pozycja, rocznik, szukaj, bramek min.) i tabela z kolumnami ID, Imię, Nazwisko, Poz., Klub, Rocznik, Mecze, Bramki, Akcje. Prototyp wprost zaznacza: "Brak pola narodowość — źródło ZPRP go nie dostarcza."

Docelowy szablon względem katalogu szablony: `admin/players/list.html` (nazwa robocza).

## Przeznaczenie

Pozycja "Zawodnicy" w sidebarze (grupa "Dane"). Docelowo przegląd zawodników z `public.zawodnicy` (19 850 wierszy) z liczbą meczów/bramek wyliczoną z `public.mecze_zawodnicy` (1 113 018 wierszy — wymaga agregacji, nie liczby wierszy 1:1, patrz [DATA.md](../../../../../../docs/DATA.md) o `mecze_zawodnicy`).

## Dane wejściowe

Nieustalone. Prototyp sugeruje kolumny ID/Imię/Nazwisko/Poz./Klub/Rocznik/Mecze/Bramki — "Klub" wymaga przejścia przez migawkę sezonową drużyny (`zespoly_sezony`), "Mecze"/"Bramki" wymagają agregacji `mecze_zawodnicy` z uwzględnieniem kompletności danych (nie każdy zawodnik–mecz oznacza potwierdzony występ, patrz DATA.md). Kolumna "Akcje" (Szczegóły/Edytuj) w prototypie prowadzi do `player_detail.html`/`player_edit.html` — edycja jest poza obecnym zakresem projektu (patrz [PROJECT.md](../../../../../../docs/PROJECT.md)).

## Powiązania

Dziedziczyłby `base.html`. Wspomniane w [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md) (etap 7: "Moduły... players.py..."). Model `zawodnicy` w `infrastructure/database/models/` jeszcze nie istnieje (etap 3 zmapował tylko modele potrzebne liście meczów). Pozycja menu w `interface/navigation.py` (`SIDEBAR`, grupa "Dane", klucz `zawodnicy`) ma obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Planowane na etap 7. Agregacja bramek/meczów wymaga wcześniejszego ustalenia zasad z DATA.md (kompletność `mecze_zawodnicy`, rozróżnienie obecności w składzie od występu).

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Zawodnicy
| [miejsce na przegląd zawodników]
| [filtry / kolumny / akcje: do adaptacji i ustalenia]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Prototyp `players.html` zawiera treść, ale nie jest to jeszcze zaadaptowany HTML aplikacji. Rysunek nie utrwala jego pól jako gotowego kontraktu.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [list.md](list.md) | Najpierw uzupełnij ten opis; planowany plik `list.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
