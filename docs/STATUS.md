# Stan projektu

Aktualizacja: 2026-09-22.

## Podsumowanie analityczne zawodnika — 2026-09-22

Karta zawodnika zachowuje istniejące zakładki Profil, Sezony i drużyny oraz Mecze i dodaje po nich Podsumowanie. Nowa zakładka ma filtry sezonu, rozgrywek i przeciwnika, KPI z liczbą meczów, bramkami, średnią, medianą, dominantami, kwartylami, karnymi, karami i pokryciem danych. Trend bramek i histogram renderuje lokalny Apache ECharts 6.1.0; wykresy mają animacje, punkty, wygaszenie kontekstu, ARIA, tabelę danych i tryb ograniczonego ruchu. Kliknięcie punktu trendu otwiera kartę meczu.

Zapytanie tylko do odczytu agreguje wpisy do poziomu mecz–zawodnik przed obliczeniami. Definicje statystyczne znajdują się w osobnym serwisie, a prezentacja w presenterze. Biblioteka wraz z LICENSE i NOTICE jest przechowywana lokalnie. Pozostałe zakładki projektu Data Science są nadal planem.

Weryfikacja: 248 testów Pythona bez integracyjnych testów bazy i 26 testów JavaScript przechodzi; Ruff dla zmienionego zakresu, formatowanie, mypy, składnia JavaScriptu i kontrola diffu przechodzą. Rzeczywista karta zawodnika i lokalny zasób ECharts zwracają `200`. Edge headless potwierdził dwa wykresy SVG z opisami ARIA na szerokościach 1440 i 390 px. Bazy nie zmieniano.

## Forma i regularność zawodnika — 2026-09-22

Karta zawodnika ma drugą dodatkową zakładkę, Forma i regularność, po Podsumowaniu. Pokazuje statystyki opisowe liczone wyłącznie z meczów ze znaną liczbą bramek w wybranym zakresie: średnią, medianę, wszystkie dominanty, minimum, maksimum, Q1–Q3, IQR, odchylenie standardowe (populacyjne), MAD, współczynnik zmienności (pomijany przy średniej poniżej 0,1 bramki na mecz), P10, P90, średnią uciętą 10% oraz udziały meczów z 0, 1–2, 3–5 i 6+ bramkami.

Wykres formy pokazuje bramki mecz po meczu kolorowane według sezonu, medianę i średnią kroczącą z 5 ostatnich meczów ze znaną liczbą bramek oraz, po osiągnięciu 10 takich meczów, dodatkową medianę kroczącą z 10. Okno liczone jest po kolejności meczów, nie po dniach; nieznana liczba bramek przerywa okno zamiast zamieniać się w zero. Poniżej progu 5 meczów pokazuje się jawne ostrzeżenie zamiast trendu. Drugi wykres to boxplot bramek według sezonu z wąsami ograniczonymi regułą Tukeya i osobno oznaczonymi wartościami odstającymi; sezon z mniej niż 5 znanymi meczami jest oznaczony jako mała próba. Oba wykresy mają tabelaryczny odpowiednik, opis ARIA i lokalny Apache ECharts 6.1.0. Zakładka korzysta z tego samego zapytania analitycznego co Podsumowanie, bez dodatkowego zapytania do bazy.

Przy okazji usunięto z karty cztery zakładki-placeholdery (Bramki i karne, Dyscyplina, Rekordy, Jakość danych), które były widoczne w interfejsie, lecz powielały dane Podsumowania bez własnej logiki ani stylów — niezgodnie z zasadą projektu, by nie przedstawiać planowanych funkcji jako gotowych. Wrócą jako osobno zaimplementowane zakładki w kolejnych etapach [PLAYER_DATA_SCIENCE](PLAYER_DATA_SCIENCE.md).

Na zgłoszenie użytkownika poprawiono czytelność wykresów liniowych (trend bramek w Podsumowaniu i wykres formy w Formie i regularności): przy wielu sezonach były nieczytelne w wąskiej połowie siatki obok drugiego wykresu. Oba wykresy w każdej z tych zakładek są teraz ułożone jeden pod drugim na pełną szerokość panelu (`.player-chart-grid.stacked` w `admin.css`) zamiast obok siebie.

Na kolejne zgłoszenie użytkownika te same wykresy pokazują od razu podział na mecze u siebie i na wyjeździe. Podsumowanie: trend bramek rozdzielono na dwa osobne wykresy (u siebie, na wyjeździe), każdy z własną medianą liczoną tylko z meczów tego miejsca; histogram rozkładu bramek pokazuje dwa słupki obok siebie na każdą liczbę bramek zamiast jednej sumy. Forma i regularność: wykres formy również rozdzielono na dwa, przy czym mediana i średnia krocząca (5, a od 10 meczów też mediana krocząca 10) są liczone niezależnie w obrębie każdego miejsca — piątka meczów u siebie pomija mecze wyjazdowe rozgrywane pomiędzy nimi, więc pokazuje rzeczywistą formę w danym miejscu, a nie ogólną formę przefiltrowaną wizualnie. Boxplot sezonów pozostaje jednym, wspólnym wykresem (podział nie był proszony).

Miejsce meczu jest liczone w `pobierz_analityke()` z `mecze_zawodnicy.strona` (`gosp`→u siebie, `gosc`→na wyjeździe) w tym samym zapytaniu agregującym, bez dodatkowego zapytania do bazy. Mecz z niejednoznaczną lub nieustaloną stroną (np. same wpisy `inne`, albo sprzeczne `gosp`/`gosc` w tym samym meczu przy kilku wpisach) ma miejsce nieustalone i jest pomijany w obu podziałach — zgodnie z zasadą projektu, by nie zgadywać jednej wartości dla niejednoznacznego agregatu, zamiast domyślnie przypisywać go do jednej ze stron.

Weryfikacja: 2 nowe testy repozytorium (jednoznaczne i niejednoznaczne miejsce meczu), 1 nowy test serwisu (niezależne okno kroczące per miejsce) oraz zaktualizowane testy interfejsu i oba testy JavaScript (formy i podsumowania) przechodzą. Pełny zestaw: 255 z 256 testów Pythona bez integracyjnych z bazą (jedyny nieprzechodzący jest środowiskowy, niezwiązany ze zmianą) i 27 testów JavaScript. Mypy i Ruff (check i format) bez błędów. Na rzeczywistej karcie zawodnika #1732 potwierdzono odpowiedzi 200 dla obu zakładek oraz poprawne dane JSON: pole `miejsce`/`miejsce_etykieta` w punktach Podsumowania, `mediana_dom`/`mediana_wyjazd`, słupki `dom`/`wyjazd` w rozkładzie i zagnieżdżone `dom`/`wyjazd` z osobnymi punktami formy w danych zakładki Forma i regularność. Bazy nie zmieniano.

Na dalsze doprecyzowanie użytkownika zakładka Podsumowanie pokazuje teraz trzy wykresy formy zamiast dwóch — „Forma mecz po meczu (wszystkie)” obok wariantów u siebie/na wyjeździe — a histogram „Rozkład bramek” ma trzy słupki na każdą liczbę bramek: Wszystkie, U siebie, Na wyjeździe. Mediana i liczniki wariantu „wszystkie” były już liczone wcześniej (KPI karty), więc zmiana dotyczyła tylko szablonu i `AnalitykaZawodnikaController` w JavaScripcie, bez zmian w repozytorium ani serwisie. Zakładka Forma i regularność pozostaje bez wariantu „wszystkie” — nie był proszony. Testy interfejsu i JavaScript zaktualizowano pod nowy układ; pełny zestaw testów pozostaje zielony poza tymi samymi dwoma wcześniej udokumentowanymi, nieistotnymi wyjątkami. Sprawdzono na rzeczywistej karcie #1732.

Weryfikacja: 5 nowych testów jednostkowych serwisu, 1 nowy test interfejsu i 1 nowy test JavaScript przechodzą. Pełny zestaw: 253 z 254 testów Pythona bez integracyjnych z bazą (jedyny nieprzechodzący jest środowiskowy, niezwiązany ze zmianą — zależy od lokalnej zmiennej `SECRET_KEY`) i 27 testów JavaScript. Mypy i Ruff (check i format) bez błędów dla zmienionego zakresu. Na rzeczywistej karcie zawodnika #1732 (231 meczów, sezony 2008/2009–2025/2026) potwierdzono odpowiedź 200, poprawne dane wykresów, oznaczenie sezonu jako małej próby i realny punkt odstający w rozstępie sezonowym. Bazy nie zmieniano.

## Grupowane tabele i składy — 2026-09-22

Listy `/administracja/tabele` i `/administracja/sklady` prezentują rekordy zbiorcze zamiast płaskich pozycji. Tabele są grupowane według sezonu, rozgrywek, tabeli i grupy. Składy są grupowane według sezonu i drużyny, a przypisane rozgrywki są pokazywane jako lista oddzielona przecinkami. Przycisk „Szczegóły” otwiera pełną kartę w nowej karcie, a dwuklik lub Enter na wierszu otwiera tę samą treść w modalu. Szczegóły tabeli pokazują wybraną grupę źródłowej klasyfikacji. Zawodnicy w szczegółach składu są uporządkowani według pozycji i oznaczeni paletą ze składów meczowych. Bazy nie zmieniano.

Weryfikacja: 15 testów interfejsu klasyfikacji przechodzi; Ruff, formatowanie i mypy przechodzą. Po poprawie kolejności argumentów `string_agg` rzeczywista lista zwróciła 3233 składy w transakcji READ ONLY zakończonej ROLLBACK. Kontrakty: [lista tabel](../src/handball/interface/templates/admin/standings/list.md), [szczegóły tabeli](../src/handball/interface/templates/admin/standings/detail.md), [lista składów](../src/handball/interface/templates/admin/rosters/list.md), [szczegóły składu](../src/handball/interface/templates/admin/rosters/detail.md).

## Szczegóły sędziego — 2026-09-21

Zaimplementowano `GET /administracja/sedziowie/<id_sedzia>` z zakładkami Dane, Mecze i Statystyki. Karta zawiera filtrowaną historię meczów, zbiorczo pobieranych partnerów, aktywność sezonową, rankingi rozgrywek i drużyn oraz kompaktowe wykresy HTML/CSS. Filtry sezonu i rozgrywek obejmują tabele i wykresy; filtr drużyny obsługuje stronę gospodarz/gość i zakres dat. Lista sędziów prowadzi do karty. Zapytania są tylko do odczytu i uwzględniają `mecze.zamiana`. Kontrakt: [detail.md](../src/handball/interface/templates/admin/referees/detail.md).

Weryfikacja: 14 testów szczegółów i katalogów przechodzi; Ruff, formatowanie, mypy i kontrola składni JavaScriptu dla zmienionego zakresu przechodzą. Rzeczywista lista i karta sędziego `#365` zwróciły `200` na PostgreSQL w konfiguracji READ ONLY; bazy nie zmieniano.
## Lista sędziów — 2026-09-21

Zaimplementowano GET /administracja/sedziowie: wyszukiwanie po nazwisku i mieście, filtr miasta, sortowanie w nagłówkach, paginację oraz liczbę różnych meczów powiązanych z osobą w obsadzie przez public.mecze_sedziowie. Pozycja „Sędziowie” w menu prowadzi do aktywnego widoku. Strona jest wyłącznie do odczytu; nie wykonano zmian w bazie. Kontrakt i mapa zmian: [list.md](../src/handball/interface/templates/admin/referees/list.md).

Weryfikacja: 11 testów interfejsu katalogów przechodzi; mypy oraz Ruff dla zmienionych plików przechodzą. Bazy nie odczytywano ani nie zmieniano.

## Sezony, Rozgrywki i Drużyny — 2026-09-21

Działają listy `/administracja/sezony`, `/administracja/rozgrywki` i `/administracja/druzyny`. Mają zwarte filtry, sortowanie w nagłówkach, paginację, aktywne pozycje menu oraz linki do listy meczów zachowujące sezon. Drużyny są prezentowane jako historyczne migawki sezonowe. Zapytania i liczniki zweryfikowano na istniejącej bazie w transakcji READ ONLY zakończonej ROLLBACK; bazy nie zmieniono. Pełna regresja bez integracji obejmuje 223 przechodzące testy.

## Lista hal — 2026-09-21

Zaimplementowano GET /administracja/hale: wyszukiwanie po nazwie i adresie, filtr miasta i minimalnej pojemności, sortowanie w nagłówkach, paginację oraz liczbę meczów powiązanych z halą. Pozycja „Hale” w menu prowadzi do aktywnego widoku. Strona jest wyłącznie do odczytu; nie wykonano zmian w bazie. Kontrakt i mapa zmian: [list.md](../src/handball/interface/templates/admin/venues/list.md).

Weryfikacja: 9 testów interfejsu hal przechodzi; mypy i Ruff dla kodu aplikacji oraz nowych testów przechodzą. Pełny zestaw 201 testów bez integracji z bazą przechodzi po odizolowaniu lokalnej zmiennej HDS_IMPORT_PASSWORD w procesie testowym. Bazy nie odczytywano ani nie zmieniano.

## Karta hali — 2026-09-21

Działa GET /administracja/hale/<id>: Dane, Mecze, Zawodnicy i Statystyki. Karta pokazuje pola hali, podsumowanie, filtrowane i paginowane rozegrane mecze, filtrowanych i sortowanych zawodników oraz rankingi TOP 10 drużyn, rozgrywek, najczęściej grających i najskuteczniejszych zawodników. Rankingi można rozszerzyć. Linki prowadzą do kart meczu i zawodnika. Kontrakt: [detail.md](../src/handball/interface/templates/admin/venues/detail.md).

Zakładka Statystyki zawiera również wygodną nawigację sekcji, trendy meczów i średniej bramek według sezonu, profil oraz histogram wyników, mecze wyrównane, heatmapę sezon × miesiąc, rozkład dni tygodnia, frekwencję z kompletnością, opisowe porównanie ze średnią hal i rekordy linkujące do kart meczów. Wykresy są lekkim, responsywnym HTML/CSS bez dodatkowej zależności.

Zapytania agregujące, w tym trendy, percentyle, frekwencję, porównania i rekordy, zweryfikowano na istniejącej bazie w transakcji READ ONLY zakończonej ROLLBACK; bazy nie zmieniono. Przechodzi 214 testów Pythona bez integracji i 25 testów JavaScript. Mypy, Ruff, kontrola formatowania i diffu przechodzą. Testy sprawdzają zakładki, filtry, walidację, linki, wykresy, rekordy, TOP 10 i rozszerzenie rankingów.

Poniższe opisy etapów zachowują wyniki wcześniejszych weryfikacji. Wynik migracji nazw z 2026-09-14 podano osobno; nie ponawiano historycznych kontroli na bazie użytkownika.

## Karta zawodnika — 2026-09-20

Działa `/administracja/zawodnicy/<id>`: Profil, Sezony i drużyny oraz Mecze. Profil pokazuje najnowszy dostępny wzrost i wagę. Historia zachowuje numer i pozycję rekordu sezon–drużyna oraz rozbija podsumowania na rozgrywki: bramki, karne i kary. Mecze mają filtry sezonu, rozgrywek i przeciwnika, sortowanie daty oraz paginację po 20 różnych meczów. Na liście działa „Szczegóły” w nowej karcie oraz dwuklik/Enter w modalu. Filtry i paginacja działają również w modalu. Kontrakt: [detail.md](../src/handball/interface/templates/admin/players/detail.md).

Weryfikacja po rozszerzeniu podsumowań sezonowych: 191 testów Pythona bez integracyjnych testów bazy; 25 testów JavaScript łącznie, w tym 7 nowych dla karty. Mypy oraz Ruff i formatowanie kodu oraz testów jednostkowych, interfejsu i helperów przechodzą. W Edge sprawdzono dwuklik, Enter, zamykanie Escape, fokus, zakładki, dane sezonowe, paginację, filtrowanie i czyszczenie w modalu oraz szerokości 1440 i 390 px. Odświeżono lokalny serwer bez automatycznego przeładowania; lista i karta zwracają 200. Przez GET rzeczywistej aplikacji potwierdzono również strony 1–20 i 21–40 zawodnika z 551 meczami. Nie uruchamiano zapisów do bazy ani pełnego audytu importu.

## Lista zawodników — 2026-09-20

Zaimplementowano `GET /administracja/zawodnicy` i aktywną pozycję menu. Lista na wzór meczów ma filtry sezonu, rozgrywek, drużyny, pozycji, rocznika i imienia/nazwiska; sortowanie w nagłówkach, paginację oraz niezależną pamięć filtrów. Zamiast liczby meczów i bramek pokazuje najnowszy dostępny wzrost oraz wagę, wybierane niezależnie z historii składów. Kontrakt i mapa zmian: [list.md](../src/handball/interface/templates/admin/players/list.md).

Weryfikacja po zmianie kolumn: 192 testy Pythona bez integracji z bazą i 24 testy JavaScript przechodzą. Mypy, formatowanie oraz Ruff dla kodu aplikacji i testów jednostkowych/widoków bez błędów. Pełny `ruff check .` wskazuje istniejący E501 w `tests/integration/test_import_repository.py:98`; tego pliku nie zmieniano. Regresję uruchomiono z pustym `HDS_IMPORT_PASSWORD` w procesie testowym, aby lokalna konfiguracja importu nie zmieniała klucza sesji testów.

Porównano z prototypem v6 w lokalnym Edge. Sprawdzono widok na danych testowych przy 1440 px i emulowanym viewport 390 px: dokument nie przewija się poziomo, tabela przewija się we własnym kontenerze, menu mobilne działa. Po odświeżeniu lokalnego serwera potwierdzono na rzeczywistym odczycie wyszukiwanie zawodnika, obecność wartości wzrostu i wagi oraz brak kolumn meczów i bramek. Bazy nie zmieniano.

## Warstwy danych i prezentacji — 2026-09-19

Wydzielono `interface/presenters/` oraz `interface/view_models/`. Repozytorium meczów zwraca liczby, flagi, daty i braki danych w typowanych obiektach domeny. Reguły stron, statusu i maksimum bramek są w `domain/match_rules.py`; etykiety, teksty wyniku, kolory i modele szablonów powstają w presenterach składanych przez fabrykę zależności. Usunięto poprzedni moduł `interface/match_presenter.py`. Zapytania i ścieżka importu pozostają bez zmian.

Weryfikacja: 130 testów Pythona bez integracji z bazą oraz 11 testów JavaScript przechodzi; mypy i Ruff dla kodu oraz testów jednostkowych/widoków bez błędów. Testy obejmują też typy i niezależność danych od ORM, brakujące wartości, zmianę stron i kierunek zależności warstw. Nie uruchamiano rzeczywistej bazy ani importu. Zaktualizowano [strukturę](DIRECTORY_STRUCTURE.md), [UML](UML.md) i [decyzję](ARCHITECTURE.md).

## Podgląd meczu i prezentacja składów — 2026-09-19

Istniejący widok szczegółów można otworzyć z listy w nowej karcie linkiem „Szczegóły” albo w modalu dwuklikiem lub klawiszem Enter na wierszu. Składy są grupowane według źródłowej pozycji i numeru koszulki, z pastelowymi kolorami pozycji i czerwonym wyróżnieniem komórek bramek liderów każdej drużyny osobno (również ex aequo). Szczegóły mają zakładki „Dane podstawowe”, „Wynik i statystyki” i „Składy”; legenda wyróżnień znajduje się pod tabelami składów. Aktualny kontrakt: [detail.md](../src/handball/interface/templates/admin/matches/detail.md). Sprawdzenie tej zmiany: 22 testy widoków i prezentacji, 11 testów JavaScript (modal, zakładki i pamięć filtrów), mypy oraz Ruff dla zmienionego Pythona przechodzą. Nie wykonano kontroli wizualnej w przeglądarce ani odczytu rzeczywistej bazy. Poniższe historyczne opisy etapów mogą poprzedzać istniejącą implementację szczegółów.

## Import i prezentacja meczów — 2026-09-19

Dodano tryb uzupełniający: wybiera z bazy mecze sezonu 2026/2027 sprzed dzisiejszego dnia z brakującym wynikiem lub składem jednej strony, pomija walkowery i wycofane spotkania, pobiera tylko szczegóły i uzupełnia brakujące wartości. Pełny import pozostaje dostępny do odkrywania spotkań i korekt. Opis ograniczeń, przepływu i zapisu: [IMPORTS](IMPORTS.md). Klient API zachowuje trzysekundowy odstęp między żądaniami w jednym procesie. Lista meczów uwzględnia `zamiana`, odwracając drużyny wraz z wynikiem. Zmiany nie obejmują uruchomienia rzeczywistego importu ani modyfikacji bazy przez AI. Weryfikacja: 85 testów bez integracji z bazą przechodzi, z wyłączonym hasłem importu w środowisku procesu testów; mypy oraz Ruff dla kodu i testów jednostkowych/widoków przechodzą. Zapytania wyboru kandydatów nie uruchamiano na rzeczywistym PostgreSQL.

## Runda i kolejka na liście meczów — 2026-09-19

Dodano filtry po nazwie rundy i kolejki oraz dwie opcjonalne kolumny włączane osobno w modalu „Widoczne kolumny”. Kolumny są domyślnie ukryte; wybór zapamiętuje przeglądarka. Filtry są stale dostępne. Kontrakt, zachowanie i aktualny spis elementów: [list.md](../src/handball/interface/templates/admin/matches/list.md).

## Gotowe

- Przyjęta nazwa Handball DataScience i katalog projektu.
- Instrukcje AGENTS.md, dokumentacja zakresu, architektury i danych.
- Opis ról AI oraz trzy projektowe skillsy.
- Użytkownik potwierdził wcześniejszy import bazy.
- Zweryfikowano połączenie `localhost:5432/zprp` jako `postgres` i rzeczywisty schemat PostgreSQL 15.1 w trybie tylko do odczytu.
- [Opisano bazę](database/README.md): 65 tabel, 2 widoki, kolumny, klucze, indeksy, triggery, funkcje i relacje. Liczby rekordów mają oznaczony czas odczytu.
- Zapisano zakaz samodzielnych zmian w bazie; konkretna zmiana wymaga wyraźnej prośby użytkownika.

- Przyjęto obiektowy Python, SOLID, role specjalisty Flask/SQLAlchemy i [standardy kodu](CODING_STANDARDS.md).
- [Wybrano technologie](TECH_STACK.md): Python 3.13, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, psycopg 3 oraz narzędzia jakości.

- Przyjęto [konwencję nazewnictwa z 2026-09-14](CODING_STANDARDS.md#język-i-nazewnictwo): angielskie pliki, katalogi, moduły i pakiety; polska domena, metody i zmienne bez znaków diakrytycznych; angielskie role klas, np. MeczService i MeczRepository. Udokumentowano niezależność domeny od języka przyszłej bazy. Konwencję wdrożono w istniejącym kodzie: pakiet `handball`, angielskie katalogi i pliki, klasy z rolami technicznymi, importy, konfiguracja narzędzi, `run.bat`, szablony i ich opisy. Odświeżono lokalną instalację pakietu. Weryfikacja migracji: 37 testów jednostkowych i widoków przechodzi, w tym kontrola CSS i JS; Ruff i mypy bez błędów. Wszystkie moduły i 6 szablonów HTML załadowano przy zablokowanym dostępie do bazy; sprawdzono 151 lokalnych odnośników. Testów bazy nie uruchamiano.

- Wskazano prototyp administracji v6 jako wzorzec wyglądu; potwierdzono dostępność katalogu i przeczytano jego README.
- Zapisano [kolejność realizacji](IMPLEMENTATION_PLAN.md) z kryteriami ukończenia etapów.

- Przygotowano [projekt katalogów](DIRECTORY_STRUCTURE.md) i [UML](UML.md): diagramy klas, kompozycji oraz sekwencji listy meczów.
- Utworzono 11 [opisów szablonów](TEMPLATES.md) w docelowym katalogu szablonów. Istnieją katalogi i pliki MD, bez HTML.

- Ukończono etap 1 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): obiektowy szkielet Flaska. Utworzono `pyproject.toml`, `uv.lock`, `.python-version` i `.gitignore`; `uv sync` instaluje Flask 3.1.3 zgodnie z TECH_STACK.
- Utworzono klasy `Ustawienia`, `AplikacjaFactory`, `WidokiRegistrar`, Blueprint `admin` z `StartView` oraz adapter `create_app()` w `src/handball/`.
- Skonfigurowano Ruff, mypy (strict) i pytest w `pyproject.toml`. Wykonano i potwierdzono: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` (bez błędów, 8 plików źródłowych) oraz `uv run pytest` (6 testów, wszystkie przechodzą).
- Zweryfikowano lokalne uruchomienie: `create_app()` rejestruje trasy `/administracja/` i `/static/...`, żądanie GET zwraca 200; start nie łączy się z bazą `zprp`.

- Ukończono etap 2 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): wspólny układ administracji na podstawie prototypu v6. Utworzono `base.html`, `partials/navigation.html`, `partials/messages.html`, `admin/start.html`, `static/css/admin.css` i `static/js/admin.js` (adaptacja `index.html`/`assets/style.css`/`assets/app.js` prototypu). Na wyraźne polecenie użytkownika strona startowa odwzorowuje pełną strukturę index.html (nagłówek, filtry, tabela z nagłówkami kolumn), nie tylko okrojony komunikat tekstowy — tabela ma jeden wiersz z jawną informacją o braku danych zamiast fikcyjnych wierszy z prototypu, a filtry nie są jeszcze podłączone do żadnej logiki.
- Układ zawiera sidebar (`aside.sidebar`, dwukolumnowa siatka jak w prototypie) z jedną realną pozycją "Start" — zamiast pełnego menu prototypu z pozycjami bez odpowiadających widoków. Rozwijanie sidebara na wąskim ekranie (przycisk "☰ Menu") obsługuje `static/js/admin.js`.
- `AplikacjaFactory` jawnie konfiguruje `template_folder`/`static_folder`/`static_url_path` (`templates`/`static`), zgodnie z ARCHITECTURE i DIRECTORY_STRUCTURE. `StartView` renderuje `admin/start.html` zamiast zwracać czysty tekst.
- Zaktualizowano MD czterech zaimplementowanych szablonów (baza, nawigacja, komunikaty, start) zgodnie z rzeczywistym kontraktem, blokami i selektorami.
- Sprawdzono wizualnie w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px, w tym bezpośrednie porównanie zrzutu z prototypem v6 i test kliknięcia "☰ Menu": układ zgodny z v6, responsywność działa, brak przewijania poziomego.

- Ukończono etap 3 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): warstwa danych do odczytu meczów. Dodano zależności SQLAlchemy 2.0.52, Flask-SQLAlchemy 3.1.1, psycopg 3.2.13 (`uv add`).
- Modele ORM (schemat `public`, bez `relationship()`, złączenia jawne w repozytorium): `Sezon`, `Rozgrywki`, `Runda`, `Kolejka` (infrastructure/database/models/competitions.py), `Zespol`, `ZespolSezon` (teams.py), `Mecz` (matches.py, pola potrzebne liście; rozszerzenie o wynik szczegółowy w etapie 5) — kolumny i klucze odwzorowane z [PUBLIC_SCHEMA](database/PUBLIC_SCHEMA.md).
- Obiekty domenowe `FiltryMeczow`, `PozycjaListyMeczow`, `StronaMeczow` (domain/matches.py, z walidacją strony/rozmiaru/sortowania) oraz błędy `NieZnalezionoMeczu`, `BladOdczytuDanych` (domain/errors.py).
- Kontrakt `MeczReadRepository` (contracts/match_repository.py) — na razie tylko `pobierz_liste`; `pobierz_szczegoly` dochodzi w etapie 5 zgodnie z UML.
- `MeczSQLAlchemyRepository.pobierz_liste` (infrastructure/repositories/match_repository.py): filtruje po sezonie/rozgrywkach/rundzie/kolejce, łączy `zespoly_sezony` (migawka sezonowa, nie `zespoly.nazwa` — zgodnie z DATA.md) osobnym aliasem dla gospodarza i gościa, LEFT JOIN dla nieustalonych uczestników, stabilne sortowanie po dacie i id, paginacja z limitem i osobnym zapytaniem o liczbę wszystkich, jawne rozróżnienie braku wyniku od 0:0.
- `PolaczenieConfigurator.skonfiguruj_odczyt` wymusza `execution_options={"postgresql_readonly": True}` na silniku SQLAlchemy (READ ONLY dla każdej transakcji, także po ponownym użyciu połączenia z puli). `extensions.py` inicjalizuje Flask-SQLAlchemy (`baza_danych`) powiązaną z `Baza(DeclarativeBase)`. `AplikacjaFactory` wpina oba elementy; start aplikacji nie łączy się z bazą (silnik SQLAlchemy jest leniwy).
- `Ustawienia` rozszerzone o `host_bazy`/`port_bazy`/`nazwa_bazy`/`uzytkownik_bazy`/`haslo_bazy` i właściwość `adres_bazy_danych`. Utworzono `.env.example` bez sekretów.
- Weryfikacja etapu 3: `ruff check`, `ruff format --check`, `mypy` — bez błędów.

- Ukończono etap 4 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): działająca lista meczów. `MeczService` (services/match_service.py, cienka delegacja do repozytorium — celowo, bez przedwczesnej logiki), `ZaleznosciZadaniaFactory` (request_dependencies.py, tworzy repozytorium+serwis per żądanie, wstrzykiwalna w testach), `MeczListView` i `MeczFilterForm` (WTForms, waliduje `id_sezon` jako wymagane, resztę jako opcjonalne).
- `interface/errors.py`: `obsluz_blad_domeny` mapuje `NieZnalezionoMeczu`→404, `BladOdczytuDanych`→503 (na razie domyślne strony Flaska; własny wygląd `errors/*.html` pozostaje do zrobienia). `MeczSQLAlchemyRepository` tłumaczy `SQLAlchemyError` na `BladOdczytuDanych`.
- Trasa `GET /administracja/mecze` (endpoint `administracja.lista_meczow`) zwraca 400 przy braku `id_sezon`, w przeciwnym razie renderuje `admin/matches/list.html` z filtrami (GET, bez CSRF) i paginacją (`partials/pagination.html`, zachowuje wszystkie parametry query przy zmianie strony).
- **Przeprojektowano nawigację na wyraźne polecenie użytkownika**: sidebar i górny pasek pokazują teraz **pełne** menu prototypu v6 (grupy Dane [10 pozycji]/Import-eksport [3]/Narzędzia [3], z ikonami), nie tylko pozycję "Start". Nowy moduł `interface/navigation.py` (`GORNY_PASEK`, `SIDEBAR`, poza pierwotnym planem DIRECTORY_STRUCTURE) wstrzykuje strukturę menu globalnie przez `context_processor`; widoki przekazują tylko `sekcja_aktywna` (string). Pozycje bez widoku mają `punkt_koncowy=None` → renderują się jako `href="#"`, widoczne ale nieaktywne (nie 404).
- `MeczInMemoryRepository` (tests/helpers/match_repository.py) — implementacja testowa kontraktu `MeczReadRepository`, używana w testach serwisu i widoku bez potrzeby bazy. `tests/` stało się pakietem (`__init__.py`), żeby te importy działały.
- **Zweryfikowano wobec prawdziwej bazy `zprp` w tej sesji** (hasło ustawione lokalnie przez użytkownika, nigdzie nie zapisane w dokumentacji ani w historii poleceń pokazywanej użytkownikowi): `uv run pytest tests/integration` — 3/3 przechodzi (lista dla sezonu 195/1817 meczów, pusta lista dla nieistniejącego sezonu, wymuszenie READ ONLY faktycznie blokuje zapis). Ręcznie w przeglądarce: pierwsza i druga strona listy z prawdziwymi meczami i wynikami, pusty wynik dla nieistniejącego sezonu, błąd 400 przy braku `id_sezon`, pełny sidebar z aktywną pozycją "Mecze"/"Dane". Kryterium etapu 3 i 4 "pobranie danych działa z istniejącym schematem" jest w pełni potwierdzone, nie tylko teoretycznie.
- **Uwaga bezpieczeństwa, nie do przeoczenia**: `src/handball/settings.py` ma teraz na dysku domyślną wartość `BAZA_HASLO` wpisaną wprost w kodzie (do wygodnych testów lokalnych). To narusza własną zasadę projektu (sekrety tylko ze środowiska, nigdy w kodzie) i **nie powinno trafić do commita** — użytkownik świadomie zdecydował zostawić to lokalnie, ale wyraźnie zastrzegł, żeby nie commitować tego pliku. Przy każdym `git add`/`git commit` obejmującym `settings.py` należy to przypomnieć.
- Weryfikacja etapu 4: `ruff check`, `ruff format --check`, `mypy` (32 pliki źródłowe) — bez błędów; `pytest`: 23/23 przechodzi (z `BAZA_HASLO` ustawionym lokalnie), 20 przechodzi / 3 pomijane bez niego.

- **Poprawka po zgłoszeniu użytkownika**: kliknięcie "Mecze"/"Dane" w menu dawało 400 (`id_sezon` wymagane), bo linki menu nie przekazują parametrów. Dodano `SezonReadRepository`/`SezonSQLAlchemyRepository` (contracts/season_repository.py, infrastructure/repositories/season_repository.py — poza pierwotnym planem DIRECTORY_STRUCTURE) i `ZaleznosciZadaniaFactory.utworz_repozytorium_sezonow()`. `MeczListView` bez `id_sezon` w query teraz przekierowuje (302) do najnowszego sezonu (`MAX(sezony.id)`) zamiast zwracać błąd; zweryfikowano ręcznie wobec żywej bazy (`id_sezon=195`) i testami (`test_lista_meczow_bez_id_sezon_przekierowuje_do_domyslnego`).
- **Dodano 12 wstępnych notatek MD** dla pozostałych pozycji sidebara bez widoku (Sezony, Rozgrywki, Drużyny, Zawodnicy, Składy, Tabele, Strzelcy, Hale, Sędziowie, Import/eksport [1 notatka dla 3 pozycji], Kontrola danych [1 notatka dla 2 pozycji], Logi) na wyraźne polecenie użytkownika — patrz [TEMPLATES](TEMPLATES.md), sekcja "Wczesne notatki planistyczne". To krótkie punkty startu (źródło w prototypie, przybliżone tabele bazy), nie ustalone kontrakty — większość stron prototypu v6 poza `players.html`/`quality.html` to same placeholdery ("Przykładowa strona administracyjna"), więc nie ma z czego wiernie skopiować układu.

- **Przebudowano filtry listy meczów na wyraźne polecenie użytkownika** (przycisk "Filtruj" był za duży, filtry pokazywały surowe ID zamiast nazw): sezon i rozgrywki to teraz rozwijane listy z nazwami (`OpcjaWyboru`, `SlownikiMeczowService`, contracts/repositories `seasons.py`/`competitions.py`/`venues.py` — wszystkie poza pierwotnym planem DIRECTORY_STRUCTURE); `id_sezon` jest teraz opcjonalny (pusty wybór = wszystkie sezony, usunięto wcześniejsze przekierowanie do najnowszego sezonu). Dodano model `Hala` (`infrastructure/database/models/venues.py`) i kolumnę "Hala" w tabeli i filtrach. Dodano wyszukiwanie po nazwie drużyny (`szukaj_druzyny`, ILIKE na gospodarzu lub gościu) oraz po dacie w formacie częściowym: rok (`2026`), rok-miesiąc (`2026-01`) albo pełna data (`2026-01-15`) — parsuje `zakres_z_czesciowej_daty()` w domain/matches.py, niepoprawny format zwraca czytelny błąd 400. Usunięto filtry `id_runda`/`id_kolejka` (nie były używane w interfejsie, użytkownik ich nie prosił). Poprawiono CSS (`.pole-przycisku`), żeby przycisk "Filtruj" nie rozciągał się na całą kolumnę siatki. Zweryfikowano ręcznie wobec żywej bazy `zprp`: filtr sezonu pokazuje "2026/2027" (nie ID), wyszukiwanie "Kielce" zwraca 169 trafień z poprawnymi nazwami hal, błędny format daty zwraca czytelny komunikat po polsku. `pytest`: 34 przechodzi, 3 integracyjne pomijane bez `BAZA_HASLO`.

- **Druga runda poprawek listy meczów, też na wyraźne polecenie użytkownika**: sortowanie przeniesione z pola w filtrach na klikalny nagłówek kolumny "Data" (rosnąco/malejąco, zachowuje pozostałe filtry, resetuje stronę) — **zapisano to jako trwałą konwencję projektu** w [CODING_STANDARDS](CODING_STANDARDS.md) ("Listy z filtrami") i w skillu `hds-flask-feature`, żeby dotyczyła też przyszłych list. Dodano kolumny Sezon i Rozgrywki (INNER JOIN, pola NOT NULL w `mecze`). Usunięto podpowiedź formatu z pola daty (użytkownik nie chciał podpowiedzi w samym polu). Wyszukiwanie drużyny przeprojektowane: zamiast dopasowania tekstu per wiersz, najpierw rozwiązuje nazwę do `id_zespol` (przez `zespoly_sezony`), potem filtruje mecze po tym stałym identyfikatorze — dzięki temu jedna historyczna nazwa (np. "Industria Kielce") znajduje też mecze z sezonów, gdy zespół nazywał się inaczej (np. "Vive Kielce"). Test integracyjny `test_szukaj_druzyny_znajduje_zespol_we_wszystkich_sezonach` to potwierdza wobec żywych danych — przy okazji ujawnił, że krótkie nazwy historyczne (np. "MKS Zagłębie Lubin") mogą dodatkowo dopasować niepowiązane zespoły (rezerwy/młodzieżowe o podobnej nazwie); test dobiera jednoznaczną nazwę, żeby nie być przypadkowo kruchy, a ograniczenie jest udokumentowane w list.md jako naturalna cecha wyszukiwania tekstowego, nie błąd. `pytest`: 39/39 (z `BAZA_HASLO`).

- **Trzecia runda poprawek: filtr Rozgrywki po nazwie, nie po ID sezonowym.** Użytkownik zauważył, że filtr "Rozgrywki" pokazywał tę samą nazwę (np. "I Liga Mężczyzn Grupa A") osobno dla każdego sezonu, bo w bazie każdy sezon ma własny wiersz `rozgrywki` z tą samą `nazwa`. `FiltryMeczow.id_rozgrywki` (int) zmieniono na `rozgrywki: str | None` (nazwa); `RozgrywkiSQLAlchemyRepository.pobierz_nazwy()` zwraca `DISTINCT` nazwy zamiast pary (id, nazwa); `MeczSQLAlchemyRepository` filtruje przez `Rozgrywki.nazwa == filtry.rozgrywki` na już istniejącym złączeniu (dokładne dopasowanie, bo nazwa pochodzi z zamkniętej listy, nie wolnego tekstu). Efekt: lista rozwijana "Rozgrywki" nie ma ani jednego duplikatu, a wybór nazwy pokazuje mecze ze wszystkich sezonów tej nazwy. Dodano testy integracyjne `test_pobierz_nazwy_rozgrywek_sa_unikalne` i `test_filtr_rozgrywki_po_nazwie_obejmuje_wiele_sezonow` — **zweryfikowane wobec żywej bazy**: "I Liga Kobiet" faktycznie obejmuje 6 sezonów i 750 meczów, dropdown potwierdzony bez duplikatów zliczeniem wystąpień w renderowanym HTML. `pytest`: 41/41 (z `BAZA_HASLO`).

## Jeszcze niewykonane

- Podgląd ostatnich meczów bezpośrednio na stronie startowej (obecnie: tylko przycisk do pełnej listy) — świadomie odłożone.
- Dostęp administratora i pozostałe widoki odczytu (etapy 6–7).
- Dodatkowe pozycje sidebara podłączone do realnych widoków (obecnie większość to `href="#"`) — razem z odpowiadającymi im widokami/etapami.
- Kaskadowe odświeżanie listy rozgrywek po zmianie sezonu bez przeładowania strony (obecnie: zwykły GET, bez JS) — możliwe usprawnienie później.
- Własny wygląd stron błędów (`errors/400.html`, `404.html`, `503.html`) — na razie domyślne strony Flaska.
- Pozostałe szablony (logowanie) — ma MD, brak HTML.
- Eksport i publiczny serwis.

## Następny krok

Odczyt listy i karty zawodnika potwierdzono przez lokalną aplikację. Do dalszej weryfikacji pozostają pełna kompletność i wydajność archiwum. Następnie dostęp administratora i kolejne uzgodnione widoki z [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md). Lista i szczegóły meczów oraz lista zawodników są zaimplementowane; warstwy opisują DIRECTORY_STRUCTURE i UML.

Nie używać `python ../run.py` jako komendy uruchomienia nowej aplikacji: dotyczy starszego serwisu i jego procesu importu.

## Składy, Strzelcy i Tabele — 2026-09-21

Zaimplementowano trzy zakładki administracyjne tylko do odczytu: filtry sezonu i rozgrywek, wyszukiwanie, sortowanie, paginację oraz aktywne pozycje menu. Składy opisują zgłoszenia sezonowe, a klasyfikacje zachowują wartości źródłowe bez przeliczania.
