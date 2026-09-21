# Karta hali

Status: zaimplementowana karta GET /administracja/hale/<id_hala> z zakładkami Dane, Mecze, Zawodnicy i Statystyki.

## Kontrakt

Nagłówek i Dane otrzymują SzczegolyHaliViewModel: pola hali, pierwszy i ostatni termin oraz liczby wszystkich meczów, rozegranych meczów, rozgrywek, sezonów, drużyn i zawodników.

Mecze korzystają z istniejących MeczService i MeczPresenter. Pokazują tylko mecze z oboma pełnymi wynikami, bez wycofania i walkoweru. Filtry obejmują sezon, rozgrywki i drużynę.

Zawodnicy pochodzą z wpisów mecze_zawodnicy rozegranych meczów hali. Występ oznacza obecność wpisu, nie minuty gry. Tabela zawiera pierwszy i ostatni termin, różne mecze, bramki, średnią oraz historyczne drużyny. Ma filtr, sortowanie i paginację.

Statystyki zawierają skróty nawigacyjne, trendy sezonowe, profil wyników, histogram sumy bramek, kalendarz sezon × miesiąc, rozkład dni tygodnia, frekwencję z kompletnością danych, porównanie ze średnią hal, rekordy meczowe oraz rankingi drużyn, rozgrywek i zawodników. Domyślny limit rankingów to 10, a linki Pokaż wszystkie rozszerzają konkretny ranking. Ranking średniej wymaga 3 występów.

Wszystkie analizy obejmują rozegrane mecze: oba pełne wyniki są dostępne, mecz nie jest wycofany i nie jest walkowerem. Suma bramek korzysta z pełnego wyniku, a różnica z wartości bezwzględnej. Porównanie obejmuje hale mające rozegrane mecze i nie jest rankingiem jakości. Frekwencja pokazuje średnią, medianę, maksimum i średnie wypełnienie tylko wtedy, gdy odpowiednie dane istnieją; zawsze podaje licznik kompletności. Występ zawodnika nadal oznacza obecność wpisu meczowego, nie czas gry.

Wykresy są renderowane jako dostępny HTML i CSS, bez zewnętrznej biblioteki. Wartości liczbowe pozostają widoczne obok pasków. Mecze i rekordy linkują do istniejącej karty meczu otwieranej w nowej karcie oraz stosują `zamiana` do kolejności stron.

## Przepływ

HalaSzczegolyView → SzczegolyHaliService → SzczegolyHaliReadRepository → SzczegolyHaliSQLAlchemyRepository. Mecze przechodzą przez MeczService i MeczPresenter. SzczegolyHaliPresenter formatuje dane widoku. Zapytania agregują w SQL, a drużyny strony zawodników pobiera jedno zapytanie zbiorcze.

Brak hali daje 404, błędne parametry 400, błąd odczytu 503. POST nie jest dostępny.

## Układ tekstowy i mapa zmian

~~~text
+------------------------------------------------------------------+
| Nazwa hali                                 [Powrót do listy]     |
| Miasto · adres · pojemność                                       |
| Mecze | Rozegrane | Drużyny | Zawodnicy | Sezony                |
+------------------------------------------------------------------+
| [Dane] [Mecze] [Zawodnicy] [Statystyki]                          |
| Dane: pola hali i podsumowanie                                   |
| Mecze: filtry, tabela, paginacja, link do meczu                  |
| Zawodnicy: filtr, tabela, paginacja, link do zawodnika           |
| Statystyki: [Trendy][Wyniki][Kalendarz][Frekwencja][Rekordy]     |
|   wykresy sezonowe | profil wyniku | heatmapa | porównanie       |
|   rekordy z linkami | TOP drużyny, rozgrywki i zawodnicy        |
+------------------------------------------------------------------+
~~~

| Element | Odpowiedzialność |
| --- | --- |
| Nagłówek | detail.html, .venue-head, SzczegolyHaliViewModel |
| Zakładki | detail.html, data-venue-tabs, venue_details.js |
| Mecze | .venue-matches-table, MeczService, MeczPresenter |
| Zawodnicy | .venue-players-table, FiltryZawodnikowHali |
| Rankingi | .venue-statistics, StatystykiHaliViewModel |
| Nawigacja analiz | .venue-analysis-nav, kotwice #venue-* |
| Wykresy paskowe | .venue-bars, PasekHaliViewModel |
| Heatmapa | .venue-heatmap, KomorkaKalendarzaHaliViewModel |
| Profil i frekwencja | .venue-metric-grid, ProfilWynikowHaliViewModel, FrekwencjaHaliViewModel |
| Rekordy | #venue-records, RekordMeczuHaliViewModel |
| Zapytania | infrastructure/repositories/venue_detail_repository.py |
| Responsywność | static/css/admin.css, selektory .venue-* |
