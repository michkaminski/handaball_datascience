# Dokumentacja każdego szablonu

Każdy plik szablonu ma własny plik MD obok siebie, z tą samą nazwą bazową: `list.html` i `list.md`. Nowe nazwy plików i katalogów są angielskie zgodnie z [CODING_STANDARDS](CODING_STANDARDS.md#język-i-nazewnictwo). Szablony i odpowiadające im MD przeniesiono razem do angielskich ścieżek; indeks poniżej wskazuje aktualne pliki. Zasada obejmuje strony, układy bazowe, fragmenty dołączane przez include oraz osobne pliki makr. Dla innych rozszerzeń zachowuj jednoznaczną parę, bez dwóch szablonów konkurujących o ten sam MD.

Przed zmianą szablonu przeczytaj jego MD. Aktualizuj dokument w tej samej zmianie, gdy zmieniają się przeznaczenie, dane wejściowe, bloki, powiązania, selektory lub sposób użycia. Przy przenoszeniu/zmianie nazwy przenieś również MD i popraw odnośniki; przy usunięciu szablonu usuń lub odpowiednio przenieś jego dokumentację.

MD opisuje aktualny kontrakt i miejsca zmian, a nie dziennik każdej korekty tekstu. Wspólne reguły pozostają w dokumentacji projektu; specyficzne instrukcje przy konkretnym szablonie.

## Zawartość dokumentu szablonu

- Przeznaczenie i źródło wyglądu w prototypie v6.
- Widok i serwis dostarczające dane; rzeczywiste nazwy, typy i opcjonalność zmiennych Jinja2 po implementacji.
- Dziedziczenie, include, makra, bloki oraz wpływ zmiany na inne szablony.
- Powiązane CSS, JS i selektory — gdzie zmienić układ, styl lub zachowanie.
- Wskazanie, które zmiany wymagają backendu, oraz stany błędu i braków danych.
- Sposób weryfikacji i powiązane testy; wyraźne odróżnienie planu od wykonanych kontroli.

## Obecne opisy

Utworzono dokumenty dla wszystkich 11 szablonów nazwanych w projekcie katalogów, łącznie z planowanym logowaniem. Po etapie 4 sześć z nich ma też rzeczywisty HTML (baza, nawigacja, komunikaty, paginacja, start, matches/list); pozostałe cztery to nadal wyłącznie MD i katalogi.

| Planowany szablon | Dokument | HTML |
| --- | --- | --- |
| `base.html` | [base.md](../src/handball/interface/templates/base.md) | istnieje |
| `partials/navigation.html` | [partials/navigation.md](../src/handball/interface/templates/partials/navigation.md) | istnieje |
| `partials/messages.html` | [partials/messages.md](../src/handball/interface/templates/partials/messages.md) | istnieje |
| `partials/pagination.html` | [partials/pagination.md](../src/handball/interface/templates/partials/pagination.md) | istnieje |
| `admin/start.html` | [admin/start.md](../src/handball/interface/templates/admin/start.md) | istnieje |
| `admin/matches/list.html` | [admin/matches/list.md](../src/handball/interface/templates/admin/matches/list.md) | istnieje |
| `admin/matches/detail.html` | [admin/matches/detail.md](../src/handball/interface/templates/admin/matches/detail.md) | planowany (etap 5) |
| `admin/login.html` | [admin/login.md](../src/handball/interface/templates/admin/login.md) | planowany (etap 6) |
| `errors/400.html` | [errors/400.md](../src/handball/interface/templates/errors/400.md) | planowany (błędy mapowane na HTTP przez interface/errors.py, ale własny wygląd stron błędów jeszcze nie istnieje — używane są domyślne strony Flaska) |
| `errors/404.html` | [errors/404.md](../src/handball/interface/templates/errors/404.md) | planowany (jw.) |
| `errors/503.html` | [errors/503.md](../src/handball/interface/templates/errors/503.md) | planowany (jw.) |

## Wczesne notatki planistyczne dla pozostałych pozycji sidebara

Na wyraźne polecenie użytkownika sidebar (patrz base.md) pokazuje pełne menu prototypu v6, łącznie z pozycjami bez jeszcze istniejącego widoku. Dla każdej z nich powstała wstępna notatka MD — krótsza niż dokumenty szablonów powyżej, bez ustalonego kontraktu danych, bo żaden kod jeszcze nie istnieje. Nie są to zobowiązania co do kształtu przyszłego HTML, tylko punkt startu przy planowaniu.

| Pozycja menu | Prototyp v6 | Notatka |
| --- | --- | --- |
| Sezony | seasons.html (placeholder) | [admin/seasons/list.md](../src/handball/interface/templates/admin/seasons/list.md) |
| Rozgrywki | competitions.html (placeholder) | [admin/competitions/list.md](../src/handball/interface/templates/admin/competitions/list.md) |
| Drużyny | teams.html (placeholder) | [admin/teams/list.md](../src/handball/interface/templates/admin/teams/list.md) |
| Zawodnicy | players.html (rzeczywista treść) | [admin/players/list.md](../src/handball/interface/templates/admin/players/list.md) |
| Składy | squads.html (placeholder) | [admin/rosters/list.md](../src/handball/interface/templates/admin/rosters/list.md) |
| Tabele | standings.html (placeholder) | [admin/standings/list.md](../src/handball/interface/templates/admin/standings/list.md) |
| Strzelcy | scorers.html (placeholder) | [admin/scorers/list.md](../src/handball/interface/templates/admin/scorers/list.md) |
| Hale | halls.html (placeholder) | [admin/venues/list.md](../src/handball/interface/templates/admin/venues/list.md) |
| Sędziowie | referees.html (placeholder) | [admin/referees/list.md](../src/handball/interface/templates/admin/referees/list.md) |
| Import danych, Historia importów, Eksport danych | imports.html (placeholder, 1 strona dla 3 linków) | [admin/import/panel.md](../src/handball/interface/templates/admin/import/panel.md) |
| Anomalie danych, Walidacja danych | quality.html (rzeczywista treść, 1 strona dla 2 linków) | [admin/quality/panel.md](../src/handball/interface/templates/admin/quality/panel.md) |
| Logi aplikacji | logs.html (placeholder) | [admin/logs/list.md](../src/handball/interface/templates/admin/logs/list.md) |

Prototyp v6 sam w sobie jest placeholderem ("Przykładowa strona administracyjna") dla większości tych ekranów — tylko `players.html` i `quality.html` mają rzeczywistą treść (filtry, kolumny, przykładowe dane) do adaptacji. Nazwy plików/katalogów w tabeli są robocze; potwierdź je przy faktycznym projektowaniu.

Przyszłe szablony zespołów, zawodników i diagnostyki otrzymają pełne MD (z ustalonym kontraktem) przy ich konkretnym zaprojektowaniu lub utworzeniu — powyższe notatki to punkt startu, nie gotowy kontrakt. MD nie są szablonami do renderowania ani zasobami publicznymi; nie wystawiaj ich przez routing i nie umieszczaj w publicznym eksporcie.
