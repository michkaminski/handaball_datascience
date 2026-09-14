# Standard obiektowego Pythona i SOLID

## Wymaganie użytkownika

Cały nowy kod aplikacyjny tego projektu ma powstawać obiektowo i zgodnie z SOLID. AI pracujące nad implementacją ma przyjmować odpowiedzialność doświadczonego specjalisty Flask, SQLAlchemy i obiektowego Pythona: projektować kontrakty, rozumieć cykl życia obiektów oraz weryfikować zachowanie kodu. Jest to wymaganie jakości pracy, nie deklaracja kwalifikacji autora.

Standard dotyczy nowych modeli, widoków, logiki, repozytoriów, konfiguracji, formularzy i przyszłych eksporterów. Nie upoważnia do przepisywania starszego serwisu poza katalogiem projektu. Wybrane biblioteki są w [TECH_STACK](TECH_STACK.md).

## Język i nazewnictwo

Decyzja użytkownika z 2026-09-14 zastępuje wcześniejszą zasadę polskich nazw wszystkich własnych identyfikatorów. Pliki, katalogi, moduły i pakiety nazywamy po angielsku; pojęcia domenowe w kodzie pozostają polskie. Identyfikatory nie zawierają znaków diakrytycznych. Dokumentację i teksty interfejsu piszemy po polsku z poprawnymi polskimi znakami.

| Element | Konwencja | Przykład |
| --- | --- | --- |
| Katalogi i pakiety | Angielski, snake_case | `services/`, `repositories/`, `views/`, `templates/`, `static/`, `tests/` |
| Moduły | Angielski, snake_case | `match_service.py`, `match_repository.py`, `match_views.py` |
| Szablony i ich opisy | Angielski, wspólna nazwa bazowa | `matches/list.html` i `matches/list.md` |
| Modele i obiekty domenowe | Polski, PascalCase | `Mecz`, `ZespolSezon`, `FiltryMeczow`, `StronaMeczow` |
| Klasy z rolą techniczną | Polska nazwa domenowa, potem angielska rola | `MeczService`, `MeczRepository`, `MeczListView`, `MeczFilterForm` |
| Metody, atrybuty i zmienne | Polski, snake_case | `pobierz_mecz()`, `pobierz_mecze_sezonu()`, `mecz`, `identyfikator_sezonu` |
| Stałe | Polski, UPPER_SNAKE_CASE | `DOMYSLNY_ROZMIAR_STRONY` |
| Pliki testów / funkcje testowe | Angielska nazwa pliku / polski opis zachowania | `test_match_service.py` / `test_pobiera_mecz()` |

Rolę umieszczamy po nazwie domenowej: `MeczService`, nie `ServiceMeczow` ani `SerwisMeczow`. Kontrakt odczytu może nazywać się `MeczReadRepository`, a implementacje `MeczSQLAlchemyRepository` i `MeczInMemoryRepository`. Dla klas technicznych stosujemy analogicznie np. `AplikacjaFactory` i `ZaleznosciZadaniaFactory`; obiekty bez takiej roli mogą zachować nazwę `Ustawienia`. Nie tłumaczymy domeny na `Match` w klasach tylko dlatego, że plik nazywa się `match_service.py`.

Oryginalne API bibliotek i wymagane punkty integracji pozostają bez tłumaczenia: `MethodView`, `mapped_column`, `__tablename__`, `get()`, `post()`, `create_app()`, `__init__.py`, `conftest.py` oraz wymagane nazwy konfiguracji. Konwencja nie zmienia automatycznie adresów URL, endpointów, parametrów HTTP ani nazw istniejącej bazy.

### Nazwy w bazie a domena

Modele jawnie mapują rzeczywiste tabele, kolumny i schematy. Dla obecnej bazy zachowujemy istniejące nazwy atrybutów ORM odpowiadających kolumnom, np. `id_sezon`. Nazewnictwo domeny nie jest jednak uzależnione od języka przyszłej bazy: przy bazie angielskiej polski atrybut może zostać jawnie przypisany do angielskiej kolumny. Repozytorium przekłada wynik na polskie obiekty domenowe zgodne z kontraktem serwisu.

Inny interfejs WWW może korzystać z tych samych serwisów przez nowy adapter. Zmiana bazy wymaga dopasowania mapowania i zapytań oraz weryfikacji semantyki danych i testów kontraktowych; sama konwencja nazw nie zapewnia automatycznej zgodności. Nie jest to zgoda na migrację ani jakąkolwiek zmianę bazy.

### Istniejący kod i dokumentacja

Konwencję wdrożono 2026-09-14 w istniejącym kodzie: pakiet aplikacji to `src/handball/`, testy znajdują się w `tests/`, a klasy techniczne obejmują m.in. `MeczService`, `MeczReadRepository`, `MeczSQLAlchemyRepository`, `MeczListView` i `AplikacjaFactory`. Importy, konfiguracja pakietu, szablony i ich MD oraz dokumentacja używają nowych nazw. Metody, zmienne, obiekty domenowe, adresy stron i nazwy bazy zachowują dotychczasową konwencję.

Przemianowanie istniejącego fragmentu wykonuj jako spójną zmianę obejmującą importy, konfigurację narzędzi, odwołania do szablonów i zasobów, testy oraz dokumentację. Szablon i jego MD przenoś razem. Nie rozszerzaj takiej zmiany na starszy serwis ani bazę danych.

## Organizacja kodu

- Widoki HTTP implementuj jako klasy MethodView. Widok odczytuje i waliduje wejście, wywołuje przypadek użycia oraz buduje odpowiedź.
- Przypadki użycia i obliczenia implementuj w klasach serwisów. Logika wyników meczu nie trafia do szablonu, widoku ani zapytania przypadkowo powielonego w kilku miejscach.
- Dostęp do danych zamykaj w klasach repozytoriów dopasowanych do funkcji, np. MeczSQLAlchemyRepository. Używaj wąskich kontraktów Protocol na granicy logiki i infrastruktury.
- Parametry zapytań, filtry i dane widoku przekazuj jako typowane obiekty, np. FiltryMeczow i SzczegolyMeczu. Serwis nie przyjmuje Flask request ani nie zwraca odpowiedzi HTTP.
- Modele ORM odpowiadają za mapowanie bazy. Serwis i szablon nie uruchamiają przez przypadek dodatkowych zapytań przy odczycie relacji; repozytorium przygotowuje potrzebny wynik przed zamknięciem sesji.
- Konfigurację i składanie aplikacji obsługują klasy Ustawienia i AplikacjaFactory. Fabryka składa zależności i rejestruje moduły, bez logiki meczowej.
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
| D — Dependency Inversion | Logika zależy od kontraktu, a integracja dostarcza implementację. | MeczService dostaje MeczReadRepository przez konstruktor; nie pobiera db.session ani current_app. |

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

## Listy z filtrami

Decyzja użytkownika z 2026-09-12: na każdej liście z panelem filtrów sortowanie realizuje się przez kliknięcie nagłówka kolumny (link przełączający rosnąco/malejąco, z zachowaniem pozostałych parametrów filtrów i resetem strony do 1), a nie przez osobne pole/listę rozwijaną "Sortowanie" w panelu filtrów. Wzorzec wdrożony w `admin/matches/list.html` (patrz [list.md](../src/handball/interface/templates/admin/matches/list.md)): nagłówek kolumny to `<a href="{{ url_for(request.endpoint, **dict(request.args, sortowanie=..., strona=1)) }}">Etykieta {{ strzałka }}</a>`, gdzie strzałka pokazuje aktualny kierunek. Pole `sortowanie` w `FiltryMeczow`/formularzu nadal istnieje i jest walidowane — nie jest już renderowane jako widoczny element panelu filtrów. Stosuj ten sam wzorzec przy każdej kolejnej liście z sortowaniem (Zawodnicy, Drużyny, Tabele itd.), zamiast wymyślać nowy za każdym razem.

## Weryfikacja profesjonalnej implementacji

- Testy logiki organizuj wokół klas i zachowania przypadków użycia. Testy nie potrzebują Flaska ani rzeczywistej bazy, jeśli dotyczą tylko logiki.
- Repozytoria sprawdzaj kontraktowo na odizolowanym PostgreSQL, gdy implementacja tego wymaga. SQLite nie zastępuje weryfikacji PostgreSQL JSONB, złożonych FK i jego reguł unikalności. Przygotowanie bazy testowej także wymaga wyraźnego zlecenia; nie twórz jej samodzielnie.
- Widoki sprawdzaj klientem testowym Flaska z podmienionymi zależnościami i odpowiednimi testami integracji.
- Po implementacji uruchamiaj skonfigurowane Ruff, mypy i testy właściwe zmianie. Dokumentuj rzeczywiście wykonane sprawdzenia; nie deklaruj gotowych kontroli przed przygotowaniem konfiguracji.
- Podczas review oceniaj SOLID, typowanie, zakres sesji, izolację warstw i poprawność danych, a nie samą liczbę klas.

Zachowujemy preferencję użytkownika: bez nowych komentarzy w kodzie i testach; wyjaśnienia w dokumentacji. Zakaz samodzielnych zmian w bazie z AGENTS.md ma zastosowanie także do inicjalizacji ORM, testów i narzędzi administracyjnych.
