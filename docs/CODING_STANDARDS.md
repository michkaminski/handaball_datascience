# Standard obiektowego Pythona i SOLID

## Wymaganie użytkownika

Cały nowy kod aplikacyjny tego projektu ma powstawać obiektowo i zgodnie z SOLID. AI pracujące nad implementacją ma przyjmować odpowiedzialność doświadczonego specjalisty Flask, SQLAlchemy i obiektowego Pythona: projektować kontrakty, rozumieć cykl życia obiektów oraz weryfikować zachowanie kodu. Jest to wymaganie jakości pracy, nie deklaracja kwalifikacji autora.

Standard dotyczy nowych modeli, widoków, logiki, repozytoriów, konfiguracji, formularzy i przyszłych eksporterów. Nie upoważnia do przepisywania starszego serwisu poza katalogiem projektu. Wybrane biblioteki są w [TECH_STACK](TECH_STACK.md).

## Język i nazewnictwo

Decyzja użytkownika: wyjątkowo w tym projekcie własne identyfikatory piszemy po polsku, spójnie z istniejącą bazą. Nie używamy znaków diakrytycznych w identyfikatorach; dokumentację i teksty interfejsu piszemy z poprawnymi polskimi znakami.

- Klasy: PascalCase, np. Mecz, ZespolSezon, SerwisMeczow, RepozytoriumMeczowSQLAlchemy i FabrykaAplikacji.
- Atrybuty, metody, zmienne oraz własne moduły i pakiety: snake_case, np. id_sezon, pobierz_mecz, filtry_meczow i repozytoria.
- Stałe: UPPER_SNAKE_CASE, np. DOMYSLNY_ROZMIAR_STRONY.
- Atrybuty ORM zachowują nazwy istniejących kolumn; model jawnie wskazuje nazwę tabeli oraz schemat public lub logs.
- Oryginalne API bibliotek i konwencje integracji pozostają bez tłumaczenia: MethodView, mapped_column, __tablename__, get(), post(), create_app(), zmienne konfiguracyjne wymagane przez biblioteki oraz prefiks test_ wymagany do wykrywania testów. Własna część nazwy testu jest polska, np. test_pobiera_mecz.

Zasada obejmuje nowy kod tego projektu; nie wymaga zmiany nazw istniejących tabel, katalogu handball_datascience ani dotychczasowych dokumentów i skillsów. Nie rozszerza zakresu na starszy serwis.

## Organizacja kodu

- Widoki HTTP implementuj jako klasy MethodView. Widok odczytuje i waliduje wejście, wywołuje przypadek użycia oraz buduje odpowiedź.
- Przypadki użycia i obliczenia implementuj w klasach serwisów. Logika wyników meczu nie trafia do szablonu, widoku ani zapytania przypadkowo powielonego w kilku miejscach.
- Dostęp do danych zamykaj w klasach repozytoriów dopasowanych do funkcji, np. RepozytoriumMeczowSQLAlchemy. Używaj wąskich kontraktów Protocol na granicy logiki i infrastruktury.
- Parametry zapytań, filtry i dane widoku przekazuj jako typowane obiekty, np. FiltryMeczow i SzczegolyMeczu. Serwis nie przyjmuje Flask request ani nie zwraca odpowiedzi HTTP.
- Modele ORM odpowiadają za mapowanie bazy. Serwis i szablon nie uruchamiają przez przypadek dodatkowych zapytań przy odczycie relacji; repozytorium przygotowuje potrzebny wynik przed zamknięciem sesji.
- Konfigurację i składanie aplikacji obsługują klasy Ustawienia i FabrykaAplikacji. Fabryka składa zależności i rejestruje moduły, bez logiki meczowej.
- Stosuj kompozycję i jawne przekazywanie zależności przez konstruktor. Dziedziczenie wykorzystuj tam, gdzie rzeczywiście zachodzi wspólny kontrakt, w tym klasy bazowe Flask i SQLAlchemy.

Minimalne funkcje wymagane przez integrację z frameworkiem, np. create_app(), adapter callbacka lub fixture pytest, mogą delegować do obiektów. Nie umieszczaj w nich logiki aplikacyjnej. HTML, CSS, JSON i deklaracje SQL zachowują format właściwy danej technologii; zachowanie aplikacji pozostaje w klasach.

Nie twórz klas będących tylko zbiorem staticmethod ani jednego obiektu zarządzającego całym projektem. Nie mnoż abstrakcji bez konkretnej odpowiedzialności. Prosty przypadek użycia może mieć małą klasę z jedną publiczną metodą.

## SOLID w tym projekcie

| Zasada | Wymaganie | Przykład kontroli podczas review |
| --- | --- | --- |
| S — Single Responsibility | Klasa ma jedną spójną odpowiedzialność i powód zmiany. | Widok nie zawiera SQL, a repozytorium nie renderuje HTML. |
| O — Open/Closed | Zachowanie zmienne wydzielaj w osobne implementacje kontraktu. | Różną interpretację wyniku można dodać jako strategię, gdy pojawi się rzeczywista potrzeba; nie rozbudowuj jednego przełącznika w wielu warstwach. |
| L — Liskov Substitution | Implementacje przestrzegają tych samych warunków wejścia, wyniku i błędów. | Repozytorium testowe i SQLAlchemy tak samo obsługują brak meczu, filtry i porządek wyników. |
| I — Interface Segregation | Kontrakty zawierają tylko operacje potrzebne odbiorcy. | Przeglądanie meczów zależy od kontraktu odczytu, bez obowiązkowych metod zapisu i usuwania. |
| D — Dependency Inversion | Logika zależy od kontraktu, a integracja dostarcza implementację. | SerwisMeczow dostaje RepozytoriumOdczytuMeczow przez konstruktor; nie pobiera db.session ani current_app. |

Protocol stosuj na granicach odpowiedzialności, a nie automatycznie dla każdej klasy. Nie buduj ogólnego CRUD repozytorium z dziesiątkami metod tylko dla przyszłych możliwości.

## Typy, stan i błędy

Nowe publiczne metody i konstruktory mają adnotacje typów. Wartości opcjonalne odwzorowują rzeczywiste braki danych. Nie ukrywaj nieznanego wyniku pod zerem ani nie rozprzestrzeniaj Any. Obiekty danych powinny być niezmienne, jeśli nie potrzebują zmiany stanu.

Każde żądanie ma własny zakres pracy z sesją. Nie przechowuj sesji, danych użytkownika ani filtrów żądania w globalnych singletonach. Instancje MethodView pozostają tworzone per żądanie; zmianę init_every_request należy uzasadnić brakiem współdzielonego stanu żądań.

Rozróżniaj błędne wejście, brak obiektu i niedostępność bazy. Repozytorium tłumaczy błędy infrastruktury na zdefiniowany kontrakt, a warstwa HTTP na odpowiedź. Nie zwracaj pustej listy po każdym wyjątku.

## SQLAlchemy i granice transakcji

Używaj stylu SQLAlchemy 2.0: DeclarativeBase, Mapped, mapped_column i select(). Integruj silnik oraz sesję przez Flask-SQLAlchemy. Wstrzykuj sesję do implementacji repozytorium; logika zależy od kontraktu repozytorium, nie od rozszerzenia Flaska.

Repozytorium odczytu nie zatwierdza transakcji i nie zmienia modeli. Wyjście z repozytorium powinno mieć dane potrzebne odbiorcy, bez zależności od późniejszego lazy loading. Dobieraj projekcję lub ładowanie relacji do konkretnego widoku; sprawdzaj ryzyko N+1 i zwielokrotnienia agregacji przez JOIN.

Obsługę zapisu i jego transakcji projektuj dopiero po wyraźnym zleceniu użytkownika. Wtedy granica transakcji powinna obejmować przypadek użycia, a nie ukryty commit w każdej metodzie repozytorium. Szczegóły istniejącego audytu logs trzeba uwzględnić przed pierwszym zapisem.

## Dokumentacja szablonów

Każdy szablon HTML/Jinja2, również układ, fragment i plik makr, ma własny MD w tym samym katalogu. Dokument opisuje kontrakt danych, zależności i miejsca wprowadzania zmian. Przeczytaj go przed edycją i utrzymuj zgodność z implementacją. Szczegóły i istniejące opisy: [TEMPLATES](TEMPLATES.md).

## Weryfikacja profesjonalnej implementacji

- Testy logiki organizuj wokół klas i zachowania przypadków użycia. Testy nie potrzebują Flaska ani rzeczywistej bazy, jeśli dotyczą tylko logiki.
- Repozytoria sprawdzaj kontraktowo na odizolowanym PostgreSQL, gdy implementacja tego wymaga. SQLite nie zastępuje weryfikacji PostgreSQL JSONB, złożonych FK i jego reguł unikalności. Przygotowanie bazy testowej także wymaga wyraźnego zlecenia; nie twórz jej samodzielnie.
- Widoki sprawdzaj klientem testowym Flaska z podmienionymi zależnościami i odpowiednimi testami integracji.
- Po implementacji uruchamiaj skonfigurowane Ruff, mypy i testy właściwe zmianie. Dokumentuj rzeczywiście wykonane sprawdzenia; nie deklaruj gotowych kontroli przed przygotowaniem konfiguracji.
- Podczas review oceniaj SOLID, typowanie, zakres sesji, izolację warstw i poprawność danych, a nie samą liczbę klas.

Zachowujemy preferencję użytkownika: bez nowych komentarzy w kodzie i testach; wyjaśnienia w dokumentacji. Zakaz samodzielnych zmian w bazie z AGENTS.md ma zastosowanie także do inicjalizacji ORM, testów i narzędzi administracyjnych.
