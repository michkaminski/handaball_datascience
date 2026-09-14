# Paginacja list

Status: etap 4 ukończony. Szablon `partials/pagination.html` istnieje.

Docelowy szablon względem katalogu szablony: `partials/pagination.html`.

## Przeznaczenie

Przejście między stronami wyników z zachowaniem filtrów i sortowania.

## Dane wejściowe

`strona`: `StronaMeczow` (liczba_wszystkich, strona, rozmiar_strony) z kontekstu widoku. Odnośniki budowane przez `url_for(request.endpoint, **dict(request.args, strona=...))`, więc automatycznie zachowują wszystkie bieżące parametry zapytania (filtry, sortowanie) — zmienia się tylko `strona`. Puste wyniki (`liczba_wszystkich == 0`) nie renderują żadnego odnośnika.

## Powiązania

Używany przez `admin/matches/list.html`; przyszłe listy (np. zawodnicy, drużyny) mogą dołączać ten sam fragment, jeśli będą zwracać obiekt z tymi samymi czterema polami.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj wygląd przycisków i opis zakresu. Limity, walidację numeru strony i obliczanie wyników zmieniaj w `FiltryMeczow`/`MeczSQLAlchemyRepository`, nie w tym szablonie.

## Sprawdzenie zmiany

Sprawdź pierwszą i ostatnią stronę, pustą listę, pojedynczą stronę i zachowanie parametrów filtrów.

## Stan implementacji

Wykonano: sprawdzono ręcznie wobec rzeczywistej bazy `zprp` (sezon 195, 1817 meczów, rozmiar strony 20 → 91 stron) — pierwsza strona pokazuje tylko "Następna »", strona 2 pokazuje też "« Poprzednia" z zachowanym `id_sezon` w adresie, pusty wynik nie pokazuje żadnego odnośnika. Nie sprawdzono: zachowania na ostatniej stronie zbioru (tylko "« Poprzednia").
