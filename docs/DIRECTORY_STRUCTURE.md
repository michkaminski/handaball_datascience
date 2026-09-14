# Projekt struktury katalogów

Status: etapy 1–4 ukończone. Obiektowy szkielet Flaska, wspólny układ Jinja2 na bazie prototypu v6 (łącznie z pełnym sidebarem 1:1 z prototypem), warstwa danych do odczytu oraz działająca lista meczów (`MeczService`, `ZaleznosciZadaniaFactory`, `MeczListView`, `MeczFilterForm`) istnieją i są zweryfikowane — łącznie z rzeczywistym uruchomieniem wobec bazy `zprp` (sezon 195, 1817 meczów, paginacja, filtry, stan pusty i błąd 400 sprawdzone ręcznie). Szczegóły meczu, dostęp administratora i pozostałe widoki odczytu (etap 5 i dalej) jeszcze nie istnieją. Struktura odpowiada [planowi realizacji](IMPLEMENTATION_PLAN.md) i [diagramom UML](UML.md).

## Układ projektu

Istniejący pakiet Pythona to `src/handball/`, a katalog projektu to `handball_datascience`. Od 2026-09-14 nowe pliki, katalogi, moduły i pakiety nazywamy po angielsku zgodnie z [CODING_STANDARDS](CODING_STANDARDS.md#język-i-nazewnictwo).

Poniższy wykaz pokazuje rzeczywiste pliki po migracji z 2026-09-14. Tabele opisują ich odpowiedzialności oraz osobno planowane rozszerzenia. Plik MD bez HTML opisuje planowany szablon.

```text
src/handball/__init__.py
src/handball/app_factory.py
src/handball/contracts/__init__.py
src/handball/contracts/competition_repository.py
src/handball/contracts/match_repository.py
src/handball/contracts/season_repository.py
src/handball/contracts/venue_repository.py
src/handball/domain/__init__.py
src/handball/domain/errors.py
src/handball/domain/matches.py
src/handball/domain/options.py
src/handball/extensions.py
src/handball/infrastructure/__init__.py
src/handball/infrastructure/database/__init__.py
src/handball/infrastructure/database/connection.py
src/handball/infrastructure/database/models/__init__.py
src/handball/infrastructure/database/models/base.py
src/handball/infrastructure/database/models/competitions.py
src/handball/infrastructure/database/models/matches.py
src/handball/infrastructure/database/models/teams.py
src/handball/infrastructure/database/models/venues.py
src/handball/infrastructure/repositories/__init__.py
src/handball/infrastructure/repositories/competition_repository.py
src/handball/infrastructure/repositories/match_repository.py
src/handball/infrastructure/repositories/season_repository.py
src/handball/infrastructure/repositories/venue_repository.py
src/handball/interface/__init__.py
src/handball/interface/admin/__init__.py
src/handball/interface/admin/forms/__init__.py
src/handball/interface/admin/forms/match_filters.py
src/handball/interface/admin/views/__init__.py
src/handball/interface/admin/views/match_views.py
src/handball/interface/admin/views/start.py
src/handball/interface/errors.py
src/handball/interface/navigation.py
src/handball/interface/registration.py
src/handball/interface/static/css/admin.css
src/handball/interface/static/js/admin.js
src/handball/interface/templates/admin/competitions/list.md
src/handball/interface/templates/admin/import/panel.md
src/handball/interface/templates/admin/login.md
src/handball/interface/templates/admin/logs/list.md
src/handball/interface/templates/admin/matches/detail.md
src/handball/interface/templates/admin/matches/list.html
src/handball/interface/templates/admin/matches/list.md
src/handball/interface/templates/admin/players/list.md
src/handball/interface/templates/admin/quality/panel.md
src/handball/interface/templates/admin/referees/list.md
src/handball/interface/templates/admin/rosters/list.md
src/handball/interface/templates/admin/scorers/list.md
src/handball/interface/templates/admin/seasons/list.md
src/handball/interface/templates/admin/standings/list.md
src/handball/interface/templates/admin/start.html
src/handball/interface/templates/admin/start.md
src/handball/interface/templates/admin/teams/list.md
src/handball/interface/templates/admin/venues/list.md
src/handball/interface/templates/base.html
src/handball/interface/templates/base.md
src/handball/interface/templates/errors/400.md
src/handball/interface/templates/errors/404.md
src/handball/interface/templates/errors/503.md
src/handball/interface/templates/partials/messages.html
src/handball/interface/templates/partials/messages.md
src/handball/interface/templates/partials/navigation.html
src/handball/interface/templates/partials/navigation.md
src/handball/interface/templates/partials/pagination.html
src/handball/interface/templates/partials/pagination.md
src/handball/request_dependencies.py
src/handball/services/__init__.py
src/handball/services/match_dictionary_service.py
src/handball/services/match_service.py
src/handball/settings.py
tests/__init__.py
tests/conftest.py
tests/helpers/__init__.py
tests/helpers/competition_repository.py
tests/helpers/match_repository.py
tests/helpers/season_repository.py
tests/helpers/venue_repository.py
tests/integration/__init__.py
tests/integration/test_match_repository.py
tests/interface/test_matches.py
tests/interface/test_start.py
tests/unit/test_app_factory.py
tests/unit/test_match_filters.py
tests/unit/test_match_service.py
tests/unit/test_settings.py
```

Wykaz zawiera istniejące pliki; plik MD bez HTML opisuje planowany szablon. Dodajemy kolejne modele potrzebne zapytaniom i ich relacjom, nie mapujemy od razu wszystkich 65 tabel. Pakiety Pythona mają `__init__.py`; katalogi szablonów i zasobów go nie potrzebują.

Katalogi `seasons/`, `competitions/`, `teams/`, `players/`, `rosters/`, `standings/`, `scorers/`, `venues/`, `referees/`, `import/`, `quality/`, `logs/` pod `templates/admin/` nie były pierwotnie w tym drzewie — dodano je na wyraźne polecenie użytkownika razem z pełnym sidebarem (patrz base.md), żeby każda widoczna, jeszcze niezaimplementowana pozycja menu miała choć wstępną notatkę planistyczną zamiast być całkowicie nieudokumentowana. Zawierają wyłącznie MD (patrz [TEMPLATES](TEMPLATES.md), sekcja "Wczesne notatki planistyczne") — bez HTML, bez modeli, bez widoków. `import/panel.md` i `quality/panel.md` opisują po kilka pozycji menu naraz, bo w prototypie v6 prowadzą do tej samej strony.

`interface/navigation.py` nie był pierwotnie przewidziany w tym drzewie — dodano go w etapie 4 na wyraźne polecenie użytkownika, żeby sidebar i górny pasek odzwierciedlały pełne menu prototypu v6 (wszystkie grupy i pozycje, także te bez jeszcze istniejącego widoku — renderowane jako `href="#"`), zamiast tylko pozycji z realnymi widokami.

`tests/integration/test_match_repository.py` wymaga zmiennej środowiskowej `BAZA_HASLO` wskazującej na rzeczywiste, tylko-do-odczytu połączenie z bazą `zprp`; bez niej testy są pomijane (`pytest.mark.skipif`), nie fałszywie zielone. Historyczne sprawdzenia wobec `zprp` opisuje STATUS. Przy migracji nazw testów bazy nie uruchamiano.

## Opis przy każdym szablonie

Każdy HTML ma odpowiadający mu MD w tym samym katalogu. Wykaz pokazuje istniejące pliki HTML i MD; opisy bez odpowiadającego HTML dotyczą planowanych ekranów. Dokument login.md z etapu 6 również już istnieje. Pełny indeks oraz zasady aktualizacji: [TEMPLATES](TEMPLATES.md).

## Odpowiedzialności i zależności

| Katalog lub moduł | Co zawiera | Granica odpowiedzialności |
| --- | --- | --- |
| domain | Typowane filtry, dane meczowe, wyniki i błędy | Bez importów Flask, SQLAlchemy i kodu infrastruktury. |
| contracts | Wąskie Protocol repozytoriów | Zależy od obiektów domeny; nie zawiera SQL ani operacji HTTP. |
| services | Klasy przypadków użycia | Korzystają z kontraktów, nie znają sesji i modeli ORM. |
| infrastructure | Klasy modeli, konfiguracja połączenia, repozytoria | Implementuje kontrakty, wykonuje zapytania i materializuje dane wyniku. |
| interface | MethodView, formularze, Jinja2, zasoby i błędy HTTP | Waliduje wejście HTTP, wywołuje serwis, renderuje odpowiedź. |
| app_factory.py / request_dependencies.py | Kompozycja aplikacji i zależności żądania | Jedyny punkt łączący warstwy; nie zawiera logiki statystyk. |
| tests | Kontrole zachowania klas, HTTP i repozytoriów | Nie zmieniają bazy zprp; integracja wymaga odizolowanego, udostępnionego środowiska. |

Pakiet `domain` zawiera obiekty Pythona, a `infrastructure/database/models` klasy mapujące tabele. Nie tworzymy dwóch identycznych modeli każdej tabeli: obiekty wyniku zawierają pola potrzebne widokowi, modele ORM odwzorowują wymagane fragmenty schematu.

## Administracja i prototyp v6

Wzorzec: `C:\Michal\_ZPRP_PROD\Prototyp\Prototyp_administracja_v6`. Katalog prototypu pozostaje źródłem do odczytu. Nowe fragmenty adaptujemy do Jinja2 i angielskich nazw plików. Poniższe ścieżki uwzględniają migrację nazw.

| Źródło prototypu | Planowany odpowiednik w interface/ |
| --- | --- |
| index.html | templates/admin/start.html oraz wspólny base.html |
| matches.html | templates/admin/matches/list.html |
| match_detail.html | templates/admin/matches/detail.html |
| assets/style.css | static/css/admin.css |
| assets/app.js | static/js/admin.js, wyłącznie potrzebne zachowania |
| match_edit.html, player_edit.html | Poza bieżącym zakresem; obecność prototypu nie daje zgody na zapis. |

Flask jawnie wskazuje `interface/templates` i `interface/static`; zasoby są dołączane do budowanego pakietu. Prefiks HTTP zasobów pozostaje `/statyczne`. Mapowanie źródeł nie oznacza wiernego kopiowania przykładowych danych lub implementacji backendu prototypu.

## Rozbudowa po pierwszym widoku meczu

| Etap | Rozszerzenie | Warunek |
| --- | --- | --- |
| 6 | interface/admin/views/login.py, forms/login.py, templates/admin/login.html (login.md już istnieje); kontrakt i serwis dostępu | Ustalono źródło kont i role. Nie tworzymy automatycznie tabel użytkowników. |
| 7 | Moduły teams.py, players.py, standings.py w potrzebnych warstwach i odpowiadające szablony | Wdrażamy kolejno uzgodnione ekrany, bez pustych kopii warstw. |
| 7 | Modele schematu logs oraz repozytoria i widoki diagnostyki | Wyłącznie odczyt istniejących importów, anomalii i historii. |
| Później | Klasy eksportu i katalog wynikowych plików publicznych | Osobno ustalony format HTML/JSON/JavaScript i zakres publikacji. |

Nie planujemy teraz katalogu migracji, nowego importera ani CRUD dla wszystkich tabel. `.venv` i cache narzędzi będą lokalnymi plikami generowanymi, wyłączonymi z wersjonowania. `.env.example` pokazuje jedynie nazwy ustawień i niesekretne przykłady; nie oznacza automatycznego ładowania pliku .env.

## Minimum do utworzenia jako pierwsze

Etapy 1–4 są ukończone, a wykaz powyżej pokazuje aktualne pliki po migracji nazw. Szczegóły meczu i dalsze funkcje powstają według [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md), bez pustych warstw na zapas.
