# Szczegóły meczu

Status: projekt szablonu. Plik `detail.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `admin/matches/detail.html`.

## Przeznaczenie

Prezentacja meczu według match_detail.html prototypu v6: uczestnicy, wynik, składy i dostępne statystyki.

## Dane wejściowe

SzczegolyMeczu z przygotowanym wynikiem, składami i ostrzeżeniami. Braki danych pozostają jawne; nie trafiają tu modele ORM wymagające lazy loading.

## Powiązania

MeczDetailView → MeczService → MeczReadRepository. Dziedziczy base.html; brak meczu obsługuje strona 404.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj sekcje i prezentację. Interpretację zamiana, wyniku, serii karnych i agregacji zmieniaj w klasach Pythona po potwierdzeniu danych.

## Sprawdzenie zmiany

Sprawdź niepełne składy, brak wyniku, ostrzeżenia, długie nazwy i bezpieczne odnośniki. Nie dodawaj edycji bez zlecenia.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Szczegóły meczu
| [uczestnicy i wynik]
| [metadane spotkania]
| [składy i dostępne statystyki]
| [braki danych / ostrzeżenia]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Kolejność, szczegółowe pola i selektory wymagają potwierdzenia przy adaptacji prototypu `match_detail.html`. Własny HTML, widok szczegółów i kontrakt wyniku nie istnieją.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [detail.md](detail.md) | Najpierw uzupełnij ten opis; planowany plik `detail.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
