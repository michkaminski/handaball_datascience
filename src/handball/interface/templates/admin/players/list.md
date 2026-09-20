# Lista zawodników

Status: zaimplementowana lista odczytu. Kontrakt: `GET /administracja/zawodnicy`, endpoint `administracja.lista_zawodnikow`. Zwarty układ oparty na `players.html` prototypu v6 oraz liście meczów. Widok tylko do odczytu, bez dodawania i edycji.

## Dane i reguły

Jeden wiersz odpowiada jednemu `zawodnicy.id`. Imię, nazwisko i rocznik pochodzą z `zawodnicy.imie`, `nazwisko`, `data_urodzenia`. Brak wartości pozostaje brakiem; pełna data urodzenia nie jest wyświetlana.

Pozycje i drużyny dotyczą wpisów `mecze_zawodnicy` w wybranym zakresie. Wzrost i waga pochodzą ze składów sezonowych `sklady`. Dla każdego pola osobno wybierany jest najnowszy niepusty zapis według roku rozpoczęcia sezonu, ID sezonu i ID migawki drużyny malejąco. Dlatego wzrost i waga mogą pochodzić z różnych rekordów historycznych. `—` oznacza brak znanej wartości.

Drużyny wynikają ze źródłowej strony gosp/gosc oraz odpowiedniego ID zespołu w meczu. Nazwa pochodzi z `zespoly_sezony` dobranego po `id_zespol` i `id_sezon`. Strona inne nie ma przypisanej drużyny. Zachowujemy parę skład–drużyna używaną przez szczegóły meczu; zamiana prezentowanych stron nie zmienia tej pary. To historyczne drużyny w wybranym zakresie, nie bieżący klub. Pokazujemy wszystkie różne nazwy i pozycje.

Bez filtrów kontekstu uwzględniamy również zawodników bez wpisów meczowych, pozycji, drużyn lub pomiarów. Sezon, rozgrywki, drużyna i pozycja ograniczają wpisy używane do pokazania pozycji i drużyn oraz wymagają dopasowania. Nie zawężają ostatnich znanych pomiarów. Drużynę wyszukujemy przez stały identyfikator dopasowany do historycznych nazw, jak na liście meczów. Rozgrywki mają unikalne nazwy. Rocznik i wyszukiwanie dotyczą słownika zawodników.

## Dane wejściowe i warstwy

- `filtry`: `FiltryZawodnikow`; opcjonalne id_sezon, rozgrywki, druzyna, pozycja, rocznik i szukaj; strona od 1, rozmiar_strony 1–100 (domyślnie 20), sortowanie domyślnie nazwisko.
- `formularz`: `ZawodnikFilterForm`, GET; listy wyboru sezonu, rozgrywek i pozycji oraz pola tekstowe/liczbowe. Puste pola oznaczają brak ograniczenia.
- `strona`: `StronaZawodnikowViewModel` z pozycje, liczba_wszystkich, strona, rozmiar_strony. Wiersze mają ID, teksty imienia, nazwiska, rocznika, pozycji i drużyn oraz ostatni dostępny wzrost i wagę.
- `sekcja_aktywna="zawodnicy"`: sidebar; górna sekcja „Dane”.

`ZawodnikListView` waliduje formularz, wywołuje `ZawodnikService` i `ZawodnikPresenter`. Fabryka zależności składa repozytorium i serwis. Kontrakt `ZawodnikReadRepository` oddziela serwis od SQLAlchemy. Repozytorium zwraca typowane dane domeny bez ORM i formatowania. Odczyt jak w meczach: READ ONLY, końcowy ROLLBACK.

## Zachowanie

Sortowanie przez nagłówki ID, Imię, Nazwisko, Rocznik, Wzrost i Waga; oba kierunki, ID rozstrzyga remisy, braki na końcu. Link zachowuje filtry i resetuje stronę do 1. Formularz zachowuje sortowanie i rozmiar strony. Paginacja używa wspólnego fragmentu; przekroczenie zakresu daje ostatnią stronę danych.

Błędne parametry: 400; błąd odczytu: 503; brak wyników: 200 z komunikatem. Stare linki z sortowaniem po `mecze` lub `bramki` pozostają obsługiwane i używają domyślnego sortowania po nazwisku. Jinja2 escapuje nazwy. Przycisk „Szczegóły” otwiera kartę zawodnika w nowej karcie przeglądarki. Dwuklik lub Enter na wierszu otwiera modal z tą samą treścią; Escape/×/Zamknij przywracają fokus na wiersz. Filtry i paginacja meczów działają wewnątrz modalu. Edycji nie ma. Kontrakt: [detail.md](detail.md). Pamięć filtrów zawodników jest niezależna od meczów.

## Powiązania i weryfikacja

Dziedziczy [base.html](../../base.html), używa [pagination.html](../../partials/pagination.html), [admin.css](../../../static/css/admin.css) i dedykowanego [players.js](../../../static/js/players.js). Kontrole obejmują walidację, filtry, sortowanie, paginację, niezależny wybór najnowszego wzrostu i wagi, braki oraz błędy bazy. Testy: `tests/interface/test_players.py`, `tests/unit/test_player_filters.py`, `tests/unit/test_player_repository.py` i `tests/javascript/player_filters.test.cjs`. Sprawdzenie zawijania: 12 długich nazw drużyn, viewport 1440 px — szerokość tabeli i jej kontenera 1172 px (bez poziomego przewijania). Przy 390 px dokument ma 390 px, a tabela pozostaje przewijana wewnątrz kontenera z powodu pozostałych kolumn.

Kontrola wizualna w lokalnym Edge na danych testowych: 1440 px oraz emulowane 390 px; przy 390 px szerokość dokumentu wynosi 390 px, tabela przewija się wewnątrz kontenera, menu mobilne działa. Porównano zrzut z prototypem v6. Po zmianie kolumn potwierdzono GET listy przez lokalną aplikację z rzeczywistymi danymi: wyszukiwanie zawodnika zwraca wzrost i wagę, bez nagłówków meczów oraz bramek. Pełna semantyka i wydajność archiwum nie były audytowane.

## Układ tekstowy i mapa zmian

Rzeczywisty układ list.html:

```text
[wspólna rama: nagłówek, Dane, sidebar Zawodnicy, stopka]
Start › Dane › Zawodnicy
ZAWODNICY
Zawodnicy i statystyki w wybranym zakresie.

FILTRY
[Sezon v] [Rozgrywki v] [Drużyna] [Pozycja v]
[Rocznik] [Szukaj] [Filtruj] [Wyczyść filtry]

ID ↕ | Imię ↕ | Nazwisko ↕ | Poz. | Drużyny | Rocznik ↕ |
Wzrost ↕ | Waga ↕ | Szczegóły
[wiersze albo komunikat o braku wyników]
Wzrost i waga: najnowsze dostępne wartości każdego pola. — Brak danych.
Wyniki od–do z wszystkich    [« Poprzednia] [Następna »]

[dwuklik/Enter: modal Szczegóły zawodnika / ×]
[Profil | Sezony i drużyny | Mecze]
[Otwórz w nowej karcie] [Zamknij]
```

Nazwy w kolumnie „Drużyny” zawijają się na spacji, a bardzo długie ciągi również wewnątrz słowa. Komórki mają klasę `.player-teams`, szerokość docelową 26% i maksimum 22rem; liczba drużyn zwiększa wysokość wiersza zamiast poszerzać tabelę. Na wąskim ekranie pozostałe kolumny mogą nadal wymagać przewijania tabeli.

Tabela ma jeden wiersz nagłówków; rysunek zawija go dla czytelności. Na wąskim ekranie filtry układa wspólna siatka CSS, tabela przewija się w .table-wrap, sidebar otwiera „☰ Menu”. Paginacja niewidoczna przy braku wyników.

### Mapa zmian

| Element | Plik | Odpowiedzialność |
| --- | --- | --- |
| Tytuł, filtry, tabela, legenda | [list.html](list.html) | Bloki tytul/tresc, .pagehead, .filters, #players-table. |
| Walidacja | [player_filters.py](../../../admin/forms/player_filters.py) | ZawodnikFilterForm.do_filtrow(). |
| HTTP | [player_views.py](../../../admin/views/player_views.py) | ZawodnikListView.get(). |
| Zapytania | [player_repository.py](../../../../infrastructure/repositories/player_repository.py) | ZawodnikSQLAlchemyRepository, `_ostatnie_pomiary()`. |
| Teksty i braki | [player_presenter.py](../../../presenters/player_presenter.py) | ZawodnikPresenter. |
| Karta zawodnika | [detail.md](detail.md), [player_details.js](../../../static/js/player_details.js) | data-player-href, #player-detail-dialog, SzczegolyZawodnikaController. |
| Pamięć filtrów | [players.js](../../../static/js/players.js) | data-player-filters, hds.zawodnicy.filtry.v1. |
| Paginacja | [pagination.html](../../partials/pagination.html) | Wspólny fragment, parametry GET. |
| Zawijanie drużyn | [list.html](list.html), [admin.css](../../../static/css/admin.css) | `#players-table .player-teams`: white-space, overflow-wrap, width, max-width. |
| Wygląd | [admin.css](../../../static/css/admin.css) | .filters, .pole-przycisku, .table-wrap, .note. |
| Menu | [navigation.py](../../../navigation.py) | SIDEBAR, endpoint zawodników. |
