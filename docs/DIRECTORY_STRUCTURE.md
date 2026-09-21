# Struktura katalogów

Stan rzeczywistego kodu po uporządkowaniu warstw 2026-09-19. Działają lista i szczegóły meczów, podgląd modalny, zakładki, filtry oraz panel importu. Ogólne logowanie administratora i pozostałe ekrany odczytu pozostają kolejnymi etapami. Plan prac: [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md); bieżący stan: [STATUS](STATUS.md).

## Podział odpowiedzialności

| Miejsce | Odpowiedzialność |
| --- | --- |
| `domain/` | Typowane dane i reguły meczowe, bez Flaska, SQLAlchemy, kolorów i etykiet widoku. |
| `contracts/` | Wąskie kontrakty Protocol repozytoriów, klienta API i magazynu importu. |
| `services/` | Przypadki użycia listy, szczegółów, słowników i importu; zależności od kontraktów. |
| `infrastructure/database/models/` | Mapowanie istniejącej bazy przez ORM. |
| `infrastructure/repositories/` | Zapytania oraz materializacja danych do obiektów niezależnych od sesji; osobny zapis importu. |
| `infrastructure/zprp_client.py`, `import_store.py` | Adapter HTTP ZPRP i lokalny magazyn przebiegów importu. |
| `interface/admin/views/` | MethodView: wejście HTTP, walidacja, wywołanie serwisu i presentera, odpowiedź. |
| `interface/admin/forms/` | Formularze i walidacja parametrów listy. |
| `interface/presenters/` | Przygotowanie tekstów, kolejności składów, kolorów i wyróżnień dla szablonów. |
| `interface/view_models/` | Dataclass z gotowymi polami widoku; nie są modelami ORM ani kontraktami repozytorium. |
| `interface/templates/`, `static/` | Jinja2, opisy MD, CSS i kontrolery JavaScript. |
| Fabryki w katalogu pakietu | Składanie zależności i integracja aplikacji. |

## Katalogi i główne pliki

```text
src/handball/
├── __init__.py                 create_app deleguje do fabryki
├── app_factory.py              AplikacjaFactory
├── request_dependencies.py     ZaleznosciZadaniaFactory: serwisy i presenter meczów
├── import_factory.py           ImportRegistrar: składanie i rejestracja importu
├── settings.py                 Ustawienia
├── extensions.py               integracja Flask-SQLAlchemy
├── domain/
│   ├── matches.py              DaneMeczu, SzczegolyMeczu, ZawodnikMeczu, filtry i lista
│   ├── match_rules.py          MeczPolicy, StatusMeczu
│   ├── imports.py              przebiegi i rekordy importu
│   ├── options.py
│   └── errors.py
├── contracts/
│   ├── match_repository.py
│   ├── season_repository.py
│   ├── competition_repository.py
│   ├── venue_repository.py
│   ├── match_stage_repository.py
│   ├── import_repository.py
│   └── import_storage.py
├── services/
│   ├── match_service.py
│   ├── match_dictionary_service.py
│   ├── import_service.py
│   └── import_mapping.py
├── infrastructure/
│   ├── database/
│   │   ├── connection.py
│   │   └── models/             base, matches, competitions, teams, venues
│   ├── repositories/           implementacje kontraktów odczytu i importu
│   ├── zprp_client.py
│   └── import_store.py
└── interface/
    ├── registration.py
    ├── navigation.py
    ├── errors.py
    ├── admin/
    │   ├── forms/match_filters.py
    │   └── views/              start.py, match_views.py, import_views.py
    ├── presenters/
    │   └── match_presenter.py   MeczPresenter, SkladMeczuPresenter, MeczFormat
    ├── view_models/
    │   └── matches.py          modele listy, szczegółów i zawodnika
    ├── templates/              base, partials, admin oraz planowane errors
    └── static/
        ├── css/admin.css
        └── js/                 admin.js, matches.js, import.js
```

Pakiety Pythona zawierają `__init__.py`; w drzewie pominięto powtarzające się pliki inicjalizacji.

## Kontrakt listy i szczegółów

Repozytorium przekazuje `DaneMeczu` z wartościami liczbowymi, flagami, datami i `None`, a `ZawodnikMeczu` zachowuje m.in. numer koszulki i bramki jako `int | None`. `SzczegolyMeczu` łączy te dane z nazwami i źródłowymi składami. `PozycjaListyMeczow` zawiera źródłowe nazwy obu stron i dane meczu. Obiekty ORM nie opuszczają repozytorium.

`MeczPolicy` określa kolejność stron według `zamiana`, status, obecność dogrywki/serii karnych i maksimum bramek w składzie. Nie formatuje HTML ani etykiet.

`MeczPresenter` korzysta z tych reguł i zwraca `StronaMeczowViewModel` albo `SzczegolyMeczuViewModel`. `SkladMeczuPresenter` tworzy `ZawodnikMeczuViewModel` z tekstami, kolorem pozycji i flagą najlepszego strzelca. `MeczFormat` odpowiada za tekst braków, dat, flag, ułamków i dopisków wyniku. Wszystkie zależności presentera składa `ZaleznosciZadaniaFactory` i przekazuje widokom.

Serwisy i kontrakty nie importują presenterów ani modeli widoku. Nowy odbiorca danych może wykorzystać domenę bez kolorów i formatów interfejsu.

## Import

Istniejąca ścieżka importu pozostaje odrębna: `ImportRegistrar` składa `ImportService`, `ZprpClient`, `ImportFileStore` i `ImportSQLAlchemyRepository`. `services/import_mapping.py` jest obecnie mapowaniem specyficznym dla importu ZPRP; nie przeniesiono go w tej refaktoryzacji. Szczegóły działania i ograniczeń: [IMPORTS](IMPORTS.md). Refaktoryzacja odczytu nie uruchamia importu ani zapisu w bazie.

## Szablony i prototyp

Wzorzec wizualny pozostaje w `C:\Michal\_ZPRP_PROD\Prototyp\Prototyp_administracja_v6`. Źródłowego prototypu nie modyfikujemy. Istnieją m.in. `admin/start.html`, `admin/matches/list.html`, `admin/matches/detail.html`, `admin/import/panel.html`, `base.html` i fragmenty nawigacji, komunikatów i paginacji. Każdy HTML ma MD obok siebie.

Pozostałe katalogi szablonów zawierające tylko MD są planami, nie działającymi ekranami. Indeks i reguły opisów: [TEMPLATES](TEMPLATES.md). Nie tworzymy dodatkowych katalogów infrastruktury ani pustych warstw na zapas.

## Testy

- `tests/unit/`: logika i kontrakty, mapowanie repozytorium z atrapą sesji, kontrola kierunku importów.
- `tests/interface/`: klient Flaska, presentery, formatowanie, składy i import na atrapach zależności.
- `tests/javascript/`: filtry, modal i zakładki z atrapami DOM.
- `tests/helpers/`: repozytoria pamięciowe i dane testowe.
- `tests/integration/`: osobno uruchamiane testy bazowe; nie należą do bezpiecznej regresji bez bazy.

Komendy: [README](../README.md). Refaktoryzację weryfikuje zestaw `pytest --ignore=tests/integration`; integracji z rzeczywistą bazą nie uruchamiano.

## Lista zawodników — 2026-09-20

Działa trasa `/administracja/zawodnicy` z pozycją w sidebarze. `domain/players.py` zawiera filtry, pozycję i stronę danych; `contracts/player_repository.py` kontrakt odczytu. `infrastructure/database/models/players.py` mapuje słownik zawodników, a `infrastructure/repositories/player_repository.py` agreguje wpisy meczowe. `services/player_service.py` obsługuje odczyt listy/pozycji, `player_dictionary_service.py` zbiera istniejące słowniki sezonów i rozgrywek.

Interfejs obejmuje `admin/forms/player_filters.py`, `admin/views/player_views.py`, `presenters/player_presenter.py`, `view_models/players.py`, parę `templates/admin/players/list.html`/`list.md` oraz `static/js/players.js`. Zależności składa istniejąca fabryka. Szczegóły i edycja zawodnika pozostają poza implementacją tej listy.

## Karta hali

Warstwy domain/venue_details.py, contracts/venue_detail_repository.py, services/venue_detail_service.py i infrastructure/repositories/venue_detail_repository.py obsługują podsumowanie, zawodników i rankingi. Mecze korzystają z istniejącego kontraktu i presentera meczów. Interfejs obejmuje venue_detail_views.py, venue_detail_filters.py, venue_detail_presenter.py, view_models/venue_details.py, parę venues/detail.html i detail.md oraz venue_details.js.

## Podstawowe katalogi

Listy Sezonów, Rozgrywek i Drużyn korzystają ze wspólnych `domain/catalogs.py`, `contracts/core_catalog_repository.py`, `services/catalog_service.py` i `infrastructure/repositories/core_catalog_repository.py`. Adapter HTTP obejmuje `admin/forms/catalog_filters.py`, `admin/views/catalog_views.py` oraz pary `seasons/list`, `competitions/list` i `teams/list`. Drużyny są migawkami sezonowymi, nie bieżącymi nazwami z `zespoly`.

## Szczegóły zawodnika

`domain/player_details.py`, `contracts/player_detail_repository.py`, `services/player_detail_service.py` oraz `infrastructure/repositories/player_detail_repository.py` obsługują profil, historię i paginowane mecze. `models/rosters.py` mapuje istniejące `sklady` i `pozycje`; model zawodnika zawiera też foto_url. Interfejs: `admin/views/player_detail_views.py`, `admin/forms/player_match_filters.py`, `presenters/player_detail_presenter.py`, `view_models/player_details.py`, para `templates/admin/players/detail.html`/`detail.md` i `static/js/player_details.js`. Fabryka składa osobny kontrakt szczegółów, nie poszerzając kontraktu listy.
