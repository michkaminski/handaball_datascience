# Projekt struktury katalogów

Status: etap 1 ukończony. Obiektowy szkielet Flaska (FabrykaAplikacji, Ustawienia, RejestratorWidokow, Blueprint administracji z WidokStartowy) oraz konfiguracja uv/Ruff/mypy/pytest istnieją i są zweryfikowane. Szablony HTML i pozostałe warstwy (etapy 2 i dalej) jeszcze nie istnieją. Struktura odpowiada [planowi realizacji](IMPLEMENTATION_PLAN.md) i [diagramom UML](UML.md).

## Układ projektu

Głównym pakietem Pythona będzie `pilka_reczna`, umieszczony w `src`. Istniejący katalog projektu zachowuje nazwę `handball_datascience`. Własne nazwy katalogów i modułów są polskie bez znaków diakrytycznych. `src`, pliki narzędziowe i nazwy istniejącej dokumentacji zachowują przyjęte konwencje.

Legenda: E — już istnieje; 1–7 — etap pierwszego utworzenia. Zawartość pakietów rozwijamy wraz z funkcjami, bez tworzenia pustych modułów na zapas. Drzewo pokazuje plan do szczegółów meczu; rozszerzenia etapów 6–7 opisano osobno.

```text
handball_datascience/
|-- AGENTS.md                                      [E]
|-- README.md                                      [E]
|-- .agents/skills/                                [E]
|-- docs/                                          [E]
|   |-- DIRECTORY_STRUCTURE.md                     [E]
|   |-- UML.md                                     [E]
|   |-- IMPLEMENTATION_PLAN.md                     [E]
|   |-- database/                                  [E]
|   `-- ... pozostała istniejąca dokumentacja
|-- pyproject.toml                                 [E]
|-- uv.lock                                        [E]
|-- .python-version                                [E]
|-- .gitignore                                     [E]
|-- .env.example                                   [3; bez sekretów]
|-- src/                                           [E]
|   `-- pilka_reczna/
|       |-- __init__.py                            [E; adapter create_app]
|       |-- fabryka.py                             [E; FabrykaAplikacji]
|       |-- ustawienia.py                          [E; Ustawienia]
|       |-- fabryka_zaleznosci.py                   [3; składanie obiektów żądania]
|       |-- rozszerzenia.py                        [3; integracje Flaska]
|       |-- domena/                                [3]
|       |   |-- __init__.py
|       |   |-- mecze.py                           [3; filtry i obiekty wyniku]
|       |   `-- bledy.py                           [3; błędy kontraktów]
|       |-- kontrakty/                             [3]
|       |   |-- __init__.py
|       |   `-- mecze.py                           [3; Protocol odczytu]
|       |-- serwisy/                               [4]
|       |   |-- __init__.py
|       |   `-- mecze.py                           [4; SerwisMeczow]
|       |-- infrastruktura/                        [3]
|       |   |-- __init__.py
|       |   |-- baza/                              [3]
|       |   |   |-- __init__.py
|       |   |   |-- polaczenie.py                   [3; konfiguracja odczytu]
|       |   |   `-- modele/
|       |   |       |-- __init__.py
|       |   |       |-- baza.py                    [3; DeclarativeBase]
|       |   |       |-- rozgrywki.py               [3; sezon, rozgrywki, runda, kolejka]
|       |   |       |-- zespoly.py                 [3; zespół i migawka sezonowa]
|       |   |       |-- mecze.py                   [3; Mecz, rozszerzenie w etapie 5]
|       |   |       `-- zawodnicy.py               [5; skład i zawodnicy]
|       |   `-- repozytoria/
|       |       |-- __init__.py
|       |       `-- mecze.py                       [3; RepozytoriumMeczowSQLAlchemy]
|       `-- interfejs/                             [E]
|           |-- __init__.py
|           |-- rejestracja.py                     [E; RejestratorWidokow]
|           |-- bledy.py                           [4; mapowanie błędów na HTTP]
|           |-- administracja/
|           |   |-- __init__.py                    [E; Blueprint]
|           |   |-- widoki/
|           |   |   |-- __init__.py
|           |   |   |-- start.py                   [E; WidokStartowy]
|           |   |   `-- mecze.py                   [4; lista, 5; szczegóły]
|           |   `-- formularze/
|           |       |-- __init__.py
|           |       `-- filtry_meczow.py           [4]
|           |-- szablony/                          [E; HTML od etapu 2]
|           |   |-- baza.md [E; opis szablonu]
|           |   |-- baza.html
|           |   |-- elementy/
|           |   |   |-- nawigacja.md [E; opis szablonu]
|           |   |   |-- nawigacja.html
|           |   |   |-- komunikaty.md [E; opis szablonu]
|           |   |   |-- komunikaty.html
|           |   |   |-- paginacja.md [E; opis szablonu]
|           |   |   `-- paginacja.html             [4]
|           |   |-- administracja/
|           |   |   |-- start.md [E; opis szablonu]
|           |   |   |-- start.html
|           |   |   `-- mecze/
|           |   |       |-- lista.md [E; opis szablonu]
|           |   |       |-- lista.html             [4]
|           |   |       |-- szczegoly.md [E; opis szablonu]
|           |   |       `-- szczegoly.html         [5]
|           |   `-- bledy/                         [4]
|           |       |-- 400.md [E; opis szablonu]
|           |       |-- 400.html
|           |       |-- 404.md [E; opis szablonu]
|           |       |-- 404.html
|           |       |-- 503.md [E; opis szablonu]
|           |       `-- 503.html
|           `-- statyczne/                         [2]
|               |-- css/administracja.css
|               |-- js/administracja.js
|               `-- obrazy/                        [gdy potrzebne]
`-- testy/                                         [E]
    |-- conftest.py
    |-- jednostkowe/
    |   |-- test_fabryka.py                        [E]
    |   |-- test_ustawienia.py                     [E]
    |   `-- test_serwis_meczow.py                  [4]
    |-- interfejs/
    |   |-- test_start.py                          [E]
    |   `-- test_mecze.py                          [4]
    |-- integracyjne/
    |   `-- test_repozytorium_meczow.py            [3; wymagane środowisko testowe]
    `-- pomocnicze/
        `-- repozytorium_meczow.py                 [4; implementacja testowa kontraktu]
```

Numery przy plikach oznaczają pierwszy etap ich potrzeby. Etap 3 sprawdza modele i repozytorium; fabrykę zależności rozbudowujemy o SerwisMeczow dopiero w etapie 4. Dodajemy kolejne modele potrzebne zapytaniom i ich relacjom, nie mapujemy od razu wszystkich 65 tabel. Pakiety Pythona mają `__init__.py`; katalogi szablonów i zasobów go nie potrzebują.

## Opis przy każdym szablonie

Każdy HTML ma odpowiadający mu MD w tym samym katalogu. W drzewie MD są oznaczone E, a HTML pozostają planowane. Dokument logowanie.md z etapu 6 również już istnieje. Pełny indeks oraz zasady aktualizacji: [TEMPLATES](TEMPLATES.md).

## Odpowiedzialności i zależności

| Katalog lub moduł | Co zawiera | Granica odpowiedzialności |
| --- | --- | --- |
| domena | Typowane filtry, dane meczowe, wyniki i błędy | Bez importów Flask, SQLAlchemy i kodu infrastruktury. |
| kontrakty | Wąskie Protocol repozytoriów | Zależy od obiektów domeny; nie zawiera SQL ani operacji HTTP. |
| serwisy | Klasy przypadków użycia | Korzystają z kontraktów, nie znają sesji i modeli ORM. |
| infrastruktura | Klasy modeli, konfiguracja połączenia, repozytoria | Implementuje kontrakty, wykonuje zapytania i materializuje dane wyniku. |
| interfejs | MethodView, formularze, Jinja2, zasoby i błędy HTTP | Waliduje wejście HTTP, wywołuje serwis, renderuje odpowiedź. |
| fabryka.py / fabryka_zaleznosci.py | Kompozycja aplikacji i zależności żądania | Jedyny punkt łączący warstwy; nie zawiera logiki statystyk. |
| testy | Kontrole zachowania klas, HTTP i repozytoriów | Nie zmieniają bazy zprp; integracja wymaga odizolowanego, udostępnionego środowiska. |

Pakiet `domena` zawiera obiekty Pythona, a `infrastruktura/baza/modele` klasy mapujące tabele. Nie tworzymy dwóch identycznych modeli każdej tabeli: obiekty wyniku zawierają pola potrzebne widokowi, modele ORM odwzorowują wymagane fragmenty schematu.

## Administracja i prototyp v6

Wzorzec: `C:\Michal\_ZPRP_PROD\Prototyp\Prototyp_administracja_v6`. Katalog prototypu pozostaje źródłem do odczytu. Fragmenty adaptujemy do Jinja2 i polskich nazw własnych plików.

| Źródło prototypu | Planowany odpowiednik w interfejs/ |
| --- | --- |
| index.html | szablony/administracja/start.html oraz wspólny baza.html |
| matches.html | szablony/administracja/mecze/lista.html |
| match_detail.html | szablony/administracja/mecze/szczegoly.html |
| assets/style.css | statyczne/css/administracja.css |
| assets/app.js | statyczne/js/administracja.js, wyłącznie potrzebne zachowania |
| match_edit.html, player_edit.html | Poza bieżącym zakresem; obecność prototypu nie daje zgody na zapis. |

Nazwy `szablony` i `statyczne` będą jawnie skonfigurowane we Flasku wraz z dołączeniem plików do pakietu przy budowaniu. Nie polegamy na domyślnych nazwach templates/static. Mapowanie źródeł nie oznacza wiernego kopiowania przykładowych danych lub implementacji backendu prototypu.

## Rozbudowa po pierwszym widoku meczu

| Etap | Rozszerzenie | Warunek |
| --- | --- | --- |
| 6 | interfejs/administracja/widoki/logowanie.py, formularze/logowanie.py, szablony/administracja/logowanie.html (logowanie.md już istnieje); kontrakt i serwis dostępu | Ustalono źródło kont i role. Nie tworzymy automatycznie tabel użytkowników. |
| 7 | Moduły zespoly.py, zawodnicy.py, klasyfikacje.py w potrzebnych warstwach i odpowiadające szablony | Wdrażamy kolejno uzgodnione ekrany, bez pustych kopii warstw. |
| 7 | Modele schematu logs oraz repozytoria i widoki diagnostyki | Wyłącznie odczyt istniejących importów, anomalii i historii. |
| Później | Klasy eksportu i katalog wynikowych plików publicznych | Osobno ustalony format HTML/JSON/JavaScript i zakres publikacji. |

Nie planujemy teraz katalogu migracji, nowego importera ani CRUD dla wszystkich tabel. `.venv` i cache narzędzi będą lokalnymi plikami generowanymi, wyłączonymi z wersjonowania. `.env.example` pokazuje jedynie nazwy ustawień i niesekretne przykłady; nie oznacza automatycznego ładowania pliku .env.

## Minimum do utworzenia jako pierwsze

Etap 1 tworzy wyłącznie pliki oznaczone 1, wymagane pakiety nadrzędne i testy startu; ukończono go i oznaczono [E] w drzewie powyżej. Etap 2 dodaje wspólny wygląd na podstawie prototypu. Połączenie bazy oraz pozostałe warstwy dochodzą wraz z etapami 3–5. Pozwala to uruchomić i sprawdzić każdy przyrost bez pustej struktury całego przyszłego serwisu.
