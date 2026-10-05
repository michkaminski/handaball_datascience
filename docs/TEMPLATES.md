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

## Układ tekstowy na końcu każdego MD

Każdy opis szablonu kończy się sekcją `## Układ tekstowy i mapa zmian`. Dotyczy to stron, układów bazowych, fragmentów, makr oraz notatek dla planowanych HTML.

- W bloku `text` rozrysuj stronę lub fragment w kolejności widocznej dla użytkownika: nagłówek, nawigację, treść, filtry, przyciski, kolumny, komunikaty i paginację — wyłącznie elementy występujące w danym szablonie lub wyraźnie oznaczone jako odziedziczona rama.
- Oznacz obszary numerami lub nazwami. Pod rysunkiem dodaj tabelę „Mapa zmian”: element → rzeczywisty plik → konkretny blok Jinja2, selektor, pole lub metoda. Używaj względnych, działających odnośników.
- Rozróżniaj zmianę etykiety/układu w HTML, wyglądu w CSS, interakcji w JS oraz danych i walidacji w Pythonie. Wskaż wspólne fragmenty, zamiast sugerować zmianę ich kopii w każdym ekranie.
- Dopisz warunki widoczności, pusty wynik i istotne różnice na wąskim ekranie. Jeżeli rysunek zawija szeroką tabelę dla czytelności, zaznacz to, aby nie sugerować innego układu HTML.
- Dla planowanego HTML napisz „plan — brak odpowiadającego HTML”; pokaż wyłącznie ustalony zakres, a nieznane pola, kolumny i akcje oznacz jako nieustalone. Nie linkuj do nieistniejących plików.
- Przy zmianie HTML aktualizuj rysunek i mapę w tej samej zmianie. Ta sekcja pozostaje ostatnią sekcją opisu.

## Obecne opisy

Utworzono dokumenty dla wszystkich 11 szablonów nazwanych w projekcie katalogów, łącznie z planowanym logowaniem. Po etapie 4 sześć z nich ma też rzeczywisty HTML (baza, nawigacja, komunikaty, paginacja, start, matches/list); pozostałe pięć to nadal wyłącznie MD i katalogi. Łącznie z 12 wczesnymi notatkami poniżej są 23 opisy; każdy ma na końcu tekstowy układ i mapę zmian.

| Planowany szablon | Dokument | HTML |
| --- | --- | --- |
| `base.html` | [base.md](../src/handball/interface/templates/base.md) | istnieje |
| `partials/navigation.html` | [partials/navigation.md](../src/handball/interface/templates/partials/navigation.md) | istnieje |
| `partials/messages.html` | [partials/messages.md](../src/handball/interface/templates/partials/messages.md) | istnieje |
| `partials/pagination.html` | [partials/pagination.md](../src/handball/interface/templates/partials/pagination.md) | istnieje |
| `admin/start.html` | [admin/start.md](../src/handball/interface/templates/admin/start.md) | istnieje: Aktualności — ostatnie mecze, ciekawostki, najlepsi strzelcy |
| `admin/matches/list.html` | [admin/matches/list.md](../src/handball/interface/templates/admin/matches/list.md) | istnieje |
| `admin/matches/detail.html` | [admin/matches/detail.md](../src/handball/interface/templates/admin/matches/detail.md) | planowany (etap 5) |
| `admin/teams/detail.html` | [admin/teams/detail.md](../src/handball/interface/templates/admin/teams/detail.md) | istnieje: Dane podstawowe, Sezony, Mecze, Zawodnicy, Podsumowanie, Forma i regularność |
| `admin/players/detail.html` | [admin/players/detail.md](../src/handball/interface/templates/admin/players/detail.md) | istnieje: Profil, Sezony i drużyny, Mecze, Podsumowanie, Forma i regularność (ze spisem treści i sekcją defensywy rywali) |
| `admin/players/defensywa_rywali.html` | [admin/players/defensywa_rywali.md](../src/handball/interface/templates/admin/players/defensywa_rywali.md) | istnieje: szczegółowy raport „Bramki zawodnika a poziom defensywy rywali” |
| `admin/reports/list.html` | [admin/reports/list.md](../src/handball/interface/templates/admin/reports/list.md) | istnieje: katalog raportów (zakładka Raporty) |
| `admin/reports/match_predictions/list.html` | [admin/reports/match_predictions/list.md](../src/handball/interface/templates/admin/reports/match_predictions/list.md) | istnieje: raport „Prognozy meczów — siła drużyn” (backtest, podsumowanie, tabela) |
| `admin/reports/match_tips/list.html` | [admin/reports/match_tips/list.md](../src/handball/interface/templates/admin/reports/match_tips/list.md) | istnieje: raport „Typowania meczów” — okres od–do, rozgrywki, jedna tabela prognoz także przyszłych meczów |
| `admin/reports/match_predictions/detail.html` | [admin/reports/match_predictions/detail.md](../src/handball/interface/templates/admin/reports/match_predictions/detail.md) | istnieje: szczegóły prognozy meczu — kroki obliczenia, ratingi, historia, definicje |
| `admin/schedule/list.html` | [admin/schedule/list.md](../src/handball/interface/templates/admin/schedule/list.md) | istnieje: terminarz rozgrywek (runda → kolejka → dzień), sidebar Dane › Terminarz |
| `admin/schedule/tips.html` | [admin/schedule/tips.md](../src/handball/interface/templates/admin/schedule/tips.md) | istnieje: typowania kolejki — treść okna dialogowego terminarza |
| `admin/schedule/preview.html` | [admin/schedule/preview.md](../src/handball/interface/templates/admin/schedule/preview.md) | istnieje: zapowiedź meczu — kadra w sezonie, forma, porównanie, mecze bezpośrednie, prognoza modelu |
| `admin/schedule/preview_pdf.html` | [admin/schedule/preview_pdf.md](../src/handball/interface/templates/admin/schedule/preview_pdf.md) | istnieje: zapowiedź meczu jako PDF A4 (WeasyPrint) — okładka „W skrócie”, kadry na osobnych stronach, numeracja stron |
| `admin/schedule/protocol_pdf.html` | [admin/schedule/protocol_pdf.md](../src/handball/interface/templates/admin/schedule/protocol_pdf.md) | istnieje: pusty protokół zawodów A4 do wypełniania podczas meczu — drużyny, kadry, hala, obsada sędziowska |
| `admin/login.html` | [admin/login.md](../src/handball/interface/templates/admin/login.md) | planowany (etap 6) |
| `errors/400.html` | [errors/400.md](../src/handball/interface/templates/errors/400.md) | planowany (błędy mapowane na HTTP przez interface/errors.py, ale własny wygląd stron błędów jeszcze nie istnieje — używane są domyślne strony Flaska) |
| `errors/404.html` | [errors/404.md](../src/handball/interface/templates/errors/404.md) | planowany (jw.) |
| `errors/503.html` | [errors/503.md](../src/handball/interface/templates/errors/503.md) | planowany (jw.) |

## Szablony pozycji sidebara

Sidebar pokazuje pełne menu prototypu v6. Tabela rozróżnia działające widoki od nadal planowanych ekranów.

| Pozycja menu | Prototyp v6 | Notatka |
| --- | --- | --- |
| Sezony — wdrożona lista odczytu | seasons.html (placeholder) | [admin/seasons/list.md](../src/handball/interface/templates/admin/seasons/list.md) |
| Rozgrywki — wdrożona lista odczytu | competitions.html (placeholder) | [admin/competitions/list.md](../src/handball/interface/templates/admin/competitions/list.md) |
| Drużyny — wdrożona lista odczytu i karta drużyny | teams.html (placeholder) | [admin/teams/list.md](../src/handball/interface/templates/admin/teams/list.md), [admin/teams/detail.md](../src/handball/interface/templates/admin/teams/detail.md) |
| Zawodnicy — wdrożona lista odczytu | players.html (rzeczywista treść) | [admin/players/list.md](../src/handball/interface/templates/admin/players/list.md) |
| Składy — wdrożona lista odczytu | squads.html (placeholder) | [admin/rosters/list.md](../src/handball/interface/templates/admin/rosters/list.md) |
| Tabele — wdrożona lista odczytu | standings.html (placeholder) | [admin/standings/list.md](../src/handball/interface/templates/admin/standings/list.md) |
| Strzelcy — wdrożona lista odczytu | scorers.html (placeholder) | [admin/scorers/list.md](../src/handball/interface/templates/admin/scorers/list.md) |
| Hale | halls.html (placeholder, rozwinięty w aplikacji) | [lista](../src/handball/interface/templates/admin/venues/list.md), [karta](../src/handball/interface/templates/admin/venues/detail.md) |
| Sędziowie | referees.html (placeholder) | [lista](../src/handball/interface/templates/admin/referees/list.md), [szczegóły](../src/handball/interface/templates/admin/referees/detail.md) |
| Terminarz — wdrożony terminarz i zapowiedź meczu (poza prototypem, 2026-09-25) | brak | [terminarz](../src/handball/interface/templates/admin/schedule/list.md), [zapowiedź](../src/handball/interface/templates/admin/schedule/preview.md), [zapowiedź PDF](../src/handball/interface/templates/admin/schedule/preview_pdf.md), [protokół do uzupełnienia](../src/handball/interface/templates/admin/schedule/protocol_pdf.md), [typowania kolejki](../src/handball/interface/templates/admin/schedule/tips.md) |
| Raporty — Katalog raportów, Prognozy meczów (poza prototypem, 2026-09-24) | brak | [katalog](../src/handball/interface/templates/admin/reports/list.md), [raport](../src/handball/interface/templates/admin/reports/match_predictions/list.md), [szczegóły](../src/handball/interface/templates/admin/reports/match_predictions/detail.md), [typowania](../src/handball/interface/templates/admin/reports/match_tips/list.md) |
| Import danych, Historia importów, Eksport danych | imports.html (placeholder, 1 strona dla 3 linków) | [admin/import/panel.md](../src/handball/interface/templates/admin/import/panel.md) |
| Anomalie danych, Walidacja danych | quality.html (rzeczywista treść, 1 strona dla 2 linków) | [admin/quality/panel.md](../src/handball/interface/templates/admin/quality/panel.md) |
| Logi aplikacji | logs.html (placeholder) | [admin/logs/list.md](../src/handball/interface/templates/admin/logs/list.md) |

Prototyp v6 sam w sobie jest placeholderem ("Przykładowa strona administracyjna") dla większości tych ekranów — tylko `players.html` i `quality.html` mają rzeczywistą treść (filtry, kolumny, przykładowe dane) do adaptacji. Nazwy plików/katalogów w tabeli są robocze; potwierdź je przy faktycznym projektowaniu.

Lista zawodników ma już HTML i pełny kontrakt MD (2026-09-20). Przyszłe szablony zespołów i diagnostyki otrzymają pełne MD (z ustalonym kontraktem) przy ich konkretnym zaprojektowaniu lub utworzeniu — powyższe notatki to punkt startu, nie gotowy kontrakt. MD nie są szablonami do renderowania ani zasobami publicznymi; nie wystawiaj ich przez routing i nie umieszczaj w publicznym eksporcie.
