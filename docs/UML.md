# UML rzeczywistych warstw aplikacji

Stan po refaktoryzacji 2026-09-19. Diagramy opisują istniejący kod. Planowane logowanie i pozostałe widoki odczytu nie są tu przedstawiane jako gotowe. Moduły i odpowiedzialności: [DIRECTORY_STRUCTURE](DIRECTORY_STRUCTURE.md).

## Zależności odczytu i prezentacji

```mermaid
classDiagram
    class MeczReadRepository {
        <<Protocol>>
        +pobierz_liste(filtry) StronaMeczow
        +pobierz_szczegoly(id_mecz) SzczegolyMeczu
    }
    class MeczSQLAlchemyRepository
    class MeczService
    class MeczListView
    class MeczSzczegolyView
    class MeczPresenter {
        +przygotuj_liste(strona) StronaMeczowViewModel
        +przygotuj_szczegoly(szczegoly) SzczegolyMeczuViewModel
    }
    class SkladMeczuPresenter
    class MeczFormat
    class MeczPolicy
    MeczListView --> MeczService
    MeczSzczegolyView --> MeczService
    MeczService --> MeczReadRepository
    MeczSQLAlchemyRepository ..|> MeczReadRepository
    MeczListView --> MeczPresenter
    MeczSzczegolyView --> MeczPresenter
    MeczPresenter --> MeczPolicy
    MeczPresenter --> MeczFormat
    MeczPresenter --> SkladMeczuPresenter
    SkladMeczuPresenter --> MeczPolicy
    SkladMeczuPresenter --> MeczFormat
```

Repozytorium mapuje ORM na dane domenowe i nie przygotowuje etykiet, dat w formacie tekstowym ani kolorów. Serwis deleguje odczyt do kontraktu. Presenter korzysta z reguł domenowych, ale domena i serwis nie znają presentera.

## Dane i modele widoku

```mermaid
classDiagram
    class DaneMeczu
    class ZawodnikMeczu
    class SzczegolyMeczu
    class PozycjaListyMeczow
    class StronaMeczow
    class ZawodnikMeczuViewModel
    class SzczegolyMeczuViewModel
    class PozycjaListyMeczowViewModel
    class StronaMeczowViewModel
    SzczegolyMeczu --> DaneMeczu
    SzczegolyMeczu --> ZawodnikMeczu
    PozycjaListyMeczow --> DaneMeczu
    StronaMeczow --> PozycjaListyMeczow
    SzczegolyMeczuViewModel --> ZawodnikMeczuViewModel
    StronaMeczowViewModel --> PozycjaListyMeczowViewModel
```

Liczby i daty pozostają typowane w domenie; `None` zachowuje brak informacji. Modele widoku w `interface/view_models/matches.py` zawierają gotowe teksty i pola wyróżnień. Są odrębnymi dataclass, nie dziedziczą po modelach ORM i nie wymagają aktywnej sesji.

## Składanie zależności

`create_app()` deleguje do `AplikacjaFactory`. Fabryka ustawia Flask, SQLAlchemy, konfigurację odczytu, nawigację oraz rejestratory. `WidokiRegistrar` przekazuje `ZaleznosciZadaniaFactory` do klas MethodView.

`ZaleznosciZadaniaFactory` tworzy repozytorium z sesją bieżącego żądania oraz serwis. Jej `utworz_presenter_meczow()` składa `MeczPolicy`, `MeczFormat`, `SkladMeczuPresenter` i `MeczPresenter`. Widoki nie tworzą tych zależności wewnątrz `get()`.

`ImportRegistrar` składa istniejącą ścieżkę importu osobno. Rejestracja widoku nie oznacza uruchomienia importu. Żadna z nowych klas prezentacji nie ma dostępu do sesji ORM.

## Żądanie szczegółów

```mermaid
sequenceDiagram
    actor U as Uzytkownik
    participant V as MeczSzczegolyView
    participant S as MeczService
    participant R as MeczSQLAlchemyRepository
    participant B as PostgreSQL
    participant P as MeczPresenter
    participant J as Jinja2
    U->>V: GET /administracja/mecze/id
    V->>S: pobierz_szczegoly(id)
    S->>R: pobierz_szczegoly(id)
    R->>B: SELECT meczu i skladow, READ ONLY
    B-->>R: wiersze
    R-->>S: SzczegolyMeczu z typowanymi danymi
    S-->>V: SzczegolyMeczu
    V->>P: przygotuj_szczegoly(dane)
    Note over P: MeczPolicy, MeczFormat, SkladMeczuPresenter
    P-->>V: SzczegolyMeczuViewModel
    V->>J: render_template(detail.html)
    J-->>U: HTML
```

Nieznany mecz daje 404; błąd repozytorium daje 503. Sesja odczytu jest sprzątana przez integrację Flask-SQLAlchemy z ROLLBACK, bez zatwierdzania zapisów.

Lista działa analogicznie z `MeczFilterForm`, słownikami, `FiltryMeczow`, `StronaMeczow` i `StronaMeczowViewModel`. Jej parametry to `id_sezon`, `rozgrywki`, `runda`, `kolejka`, `id_hala`, `druzyna`, `data_meczu`, `sortowanie`, `strona` i `rozmiar_strony`.

## Przeglądarka

`matches.js` obsługuje pamięć filtrów, widoczność kolumn, modal szczegółów i zakładki. Modal pobiera tę samą trasę szczegółów i wyciąga `[data-match-detail]`; pełna karta oraz podgląd korzystają z jednego presentera i szablonu. Szczegóły kontraktów: [list.md](../src/handball/interface/templates/admin/matches/list.md), [detail.md](../src/handball/interface/templates/admin/matches/detail.md).

## Lista zawodników — 2026-09-20

```mermaid
classDiagram
    class ZawodnikReadRepository {
        <<Protocol>>
        +pobierz_liste(filtry) StronaZawodnikow
        +pobierz_pozycje() list
    }
    ZawodnikListView --> ZawodnikFilterForm
    ZawodnikListView --> ZawodnikService
    ZawodnikListView --> SlownikiZawodnikowService
    ZawodnikListView --> ZawodnikPresenter
    ZawodnikService --> ZawodnikReadRepository
    ZawodnikSQLAlchemyRepository ..|> ZawodnikReadRepository
    ZawodnikSQLAlchemyRepository --> Zawodnik
    ZawodnikSQLAlchemyRepository --> MeczZawodnik
    ZawodnikPresenter --> StronaZawodnikowViewModel
    SlownikiZawodnikowService --> SezonReadRepository
    SlownikiZawodnikowService --> RozgrywkiReadRepository
```

Fabryka przekazuje repozytorium z sesją żądania. GET waliduje filtry, pobiera stronę domenową i prezentuje gotowe teksty. PostgreSQL wykonuje agregację po zawodniku z liczbą różnych meczów i kontrolą wielokrotnych stron. Repozytorium ogranicza paginację do ostatniej strony. Błędy danych wejściowych dają 400, odczytu 503; bez wyników widok zwraca 200.

## Karta hali

~~~mermaid
classDiagram
    HalaSzczegolyView --> SzczegolyHaliService
    SzczegolyHaliService --> SzczegolyHaliReadRepository
    SzczegolyHaliSQLAlchemyRepository ..|> SzczegolyHaliReadRepository
    SzczegolyHaliSQLAlchemyRepository --> Hala
    SzczegolyHaliSQLAlchemyRepository --> Mecz
    SzczegolyHaliSQLAlchemyRepository --> MeczZawodnik
    HalaSzczegolyView --> MeczService
    HalaSzczegolyView --> MeczPresenter
    HalaSzczegolyView --> SzczegolyHaliPresenter
~~~

Podsumowanie, zawodnicy i rankingi pochodzą z repozytorium szczegółów hali. Paginowane mecze przechodzą przez istniejący kontrakt meczów i presenter. Agregacje używają GROUP BY i COUNT DISTINCT, a nazwy drużyn strony zawodników pobiera jedno zapytanie zbiorcze.

## Podstawowe katalogi

```mermaid
classDiagram
    SezonListView --> KatalogService
    RozgrywkiListView --> KatalogService
    DruzynaListView --> KatalogService
    KatalogService --> KatalogPodstawowyReadRepository
    KatalogPodstawowySQLAlchemyRepository ..|> KatalogPodstawowyReadRepository
    KatalogPodstawowySQLAlchemyRepository --> Sezon
    KatalogPodstawowySQLAlchemyRepository --> Rozgrywki
    KatalogPodstawowySQLAlchemyRepository --> ZespolSezon
    KatalogPodstawowySQLAlchemyRepository --> Mecz
```

Wspólny formularz przekazuje tylko typowane filtry katalogowe. Zapytania agregują liczniki przed paginacją; widoki nie znają SQLAlchemy ani sesji.

## Karta zawodnika

```mermaid
classDiagram
    ZawodnikSzczegolyView --> SzczegolyZawodnikaService
    SzczegolyZawodnikaService --> SzczegolyZawodnikaReadRepository
    SzczegolyZawodnikaSQLAlchemyRepository ..|> SzczegolyZawodnikaReadRepository
    SzczegolyZawodnikaSQLAlchemyRepository --> SkladSezonowy
    SzczegolyZawodnikaSQLAlchemyRepository --> Zawodnik
    SzczegolyZawodnikaSQLAlchemyRepository --> Mecz
    ZawodnikSzczegolyView --> SzczegolyZawodnikaPresenter
    SzczegolyZawodnikaPresenter --> MeczPresenter
```

Repozytorium pobiera historię składów osobno od meczów, bez mnożenia wpisów. EXISTS wybiera różne mecze zawodnika; LIMIT/OFFSET dotyczy meczów, a dodatkowe zapytanie pobiera wszystkie jego wpisy z bieżącej strony. Modal pobiera ten sam HTML co pełna karta. Paginacja dostaje parametry z id_zawodnik i zakladka=mecze; JavaScript przechwytuje wyłącznie nawigację wewnątrz karty, pozostawiając linki do meczów.
