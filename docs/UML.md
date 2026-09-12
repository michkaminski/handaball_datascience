# UML — projekt obiektów i działania aplikacji

Status: projekt, nie dokumentacja istniejącego kodu. Diagramy zapisano w Mermaid, dzięki czemu pozostają edytowalną częścią MD. Pierwszy zakres to odczyt listy meczów i później szczegóły. [Projekt katalogów](DIRECTORY_STRUCTURE.md) przypisuje klasy do plików. [Relacje bazy](database/RELATIONSHIPS.md) opisują osobno istniejący model danych.

## 1. Diagram klas pierwszego zakresu

Strzałka z pustym trójkątem oznacza dziedziczenie, przerywana z trójkątem realizację kontraktu, a zwykła przerywana zależność. Protocol jest kontraktem strukturalnym: implementacja nie musi po nim dziedziczyć. Metody pokazują projekt odpowiedzialności; szczegóły typów parametrów dopracujemy w implementacji.

```mermaid
classDiagram
    class MethodView {
        <<framework>>
        +as_view()
    }
    class WidokListyMeczow {
        -SerwisMeczow serwis
        +get()
    }
    class WidokSzczegolowMeczu {
        -SerwisMeczow serwis
        +get(id_mecz)
    }
    class FormularzFiltrowMeczow {
        +waliduj()
        +do_filtrow() FiltryMeczow
    }
    class SerwisMeczow {
        -RepozytoriumOdczytuMeczow repozytorium
        +pobierz_liste(filtry) StronaMeczow
        +pobierz_szczegoly(id_mecz) SzczegolyMeczu
    }
    class RepozytoriumOdczytuMeczow {
        <<interface>>
        +pobierz_liste(filtry) StronaMeczow
        +pobierz_szczegoly(id_mecz) SzczegolyMeczu
    }
    class RepozytoriumMeczowSQLAlchemy {
        -Session sesja
        +pobierz_liste(filtry) StronaMeczow
        +pobierz_szczegoly(id_mecz) SzczegolyMeczu
    }
    class RepozytoriumMeczowPamieciowe {
        <<test>>
        +pobierz_liste(filtry) StronaMeczow
        +pobierz_szczegoly(id_mecz) SzczegolyMeczu
    }
    class FiltryMeczow {
        <<dataclass>>
        +id_sezon
        +id_rozgrywki
        +id_runda
        +id_kolejka
        +strona
        +rozmiar_strony
        +sortowanie
    }
    class StronaMeczow {
        <<dataclass>>
        +pozycje
        +liczba_wszystkich
        +strona
        +rozmiar_strony
    }
    class PozycjaListyMeczow {
        <<dataclass>>
        +id_mecz
        +termin
        +gospodarz
        +gosc
        +wynik
    }
    class SzczegolyMeczu {
        <<dataclass>>
        +id_mecz
        +wynik
        +sklad_gospodarzy
        +sklad_gosci
        +ostrzezenia
    }
    class Mecz {
        <<ORM>>
        +id
        +id_sezon
        +id_rozgrywki
        +id_zespol_gosp
        +id_zespol_gosc
    }
    MethodView <|-- WidokListyMeczow
    MethodView <|-- WidokSzczegolowMeczu
    WidokListyMeczow --> SerwisMeczow
    WidokSzczegolowMeczu --> SerwisMeczow
    WidokListyMeczow ..> FormularzFiltrowMeczow
    FormularzFiltrowMeczow ..> FiltryMeczow
    SerwisMeczow --> RepozytoriumOdczytuMeczow
    RepozytoriumMeczowSQLAlchemy ..|> RepozytoriumOdczytuMeczow
    RepozytoriumMeczowPamieciowe ..|> RepozytoriumOdczytuMeczow
    RepozytoriumMeczowSQLAlchemy ..> Mecz
    SerwisMeczow ..> FiltryMeczow
    SerwisMeczow ..> StronaMeczow
    SerwisMeczow ..> SzczegolyMeczu
    StronaMeczow *-- PozycjaListyMeczow
```

Metody szczegółów i WidokSzczegolowMeczu dochodzą w etapie 5. Jeśli różni odbiorcy potrzebują odrębnych kontraktów listy i szczegółów, rozdzielimy Protocol zgodnie z ISP; nie dodajemy operacji zapisu do kontraktu odczytu.

Filtry mają jawne reguły: identyfikatory są opcjonalne według funkcji, strona i rozmiar dodatnie, rozmiar ograniczony, sortowanie z listy dozwolonej. Kolejność wyników musi być stabilna, z id jako rozstrzygnięciem remisów sortowania. Brak meczu oznacza NieZnalezionoMeczu, brak wyników listy pustą StronaMeczow, a awaria zapytania BladOdczytuDanych. Implementacja pamięciowa zachowuje tę samą semantykę.

Pole wynik w obiekcie widoku jest planowaną prezentacją danych, nie nową kolumną bazy. Nazwy i kształt obiektów wyniku zostaną doprecyzowane po ustaleniu interpretacji zamiana, wariantów wyniku i braków. Modele ORM nie wychodzą z repozytorium do Jinja2.

## 2. Składanie aplikacji i zależności

```mermaid
classDiagram
    class Ustawienia {
        <<dataclass>>
        +waliduj()
    }
    class FabrykaAplikacji {
        +utworz() Flask
    }
    class RejestratorWidokow {
        +zarejestruj(aplikacja)
    }
    class FabrykaZaleznosciZadania {
        +utworz_serwis_meczow() SerwisMeczow
    }
    class KonfiguratorPolaczenia {
        +skonfiguruj_odczyt(aplikacja)
    }
    class SQLAlchemy {
        <<extension>>
        +init_app(aplikacja)
    }
    class SerwisMeczow
    class RepozytoriumMeczowSQLAlchemy
    class WidokListyMeczow
    FabrykaAplikacji --> Ustawienia
    FabrykaAplikacji ..> SQLAlchemy
    FabrykaAplikacji ..> KonfiguratorPolaczenia
    FabrykaAplikacji ..> RejestratorWidokow
    RejestratorWidokow --> FabrykaZaleznosciZadania
    WidokListyMeczow ..> FabrykaZaleznosciZadania : konstrukcja per zadanie
    FabrykaZaleznosciZadania ..> SQLAlchemy : sesja biezacego kontekstu
    FabrykaZaleznosciZadania ..> RepozytoriumMeczowSQLAlchemy : tworzy
    FabrykaZaleznosciZadania ..> SerwisMeczow : wstrzykuje repozytorium
```

create_app() deleguje do FabrykaAplikacji.utworz(). Fabryka ładuje Ustawienia, konfiguruje szablony i zasoby, inicjalizuje rozszerzenia i rejestruje Blueprints. Nie wykonuje importu, tworzenia tabel ani zapisu. Konfiguracja połączenia nie oznacza pobierania wszystkich danych przy starcie.

RejestratorWidokow przekazuje bezstanową FabrykaZaleznosciZadania jako argument as_view(). Flask tworzy instancję MethodView dla każdego żądania. Jej konstruktor prosi fabrykę o serwis. Fabryka pobiera sesję bieżącego kontekstu, przekazuje ją do nowej instancji repozytorium i przekazuje repozytorium do nowego serwisu. Widok zachowuje gotowy serwis. Logika nie pobiera zależności z current_app ani db.session.

FabrykaZaleznosciZadania jest miejscem składania obiektów, nie globalnym magazynem serwisów. Może istnieć przez czas życia aplikacji, ale nie przechowuje sesji ani obiektów żądania. Instancje repozytorium, serwisu i widoku są związane z jednym żądaniem. W testach można podać fabrykę zwracającą serwis z repozytorium pamięciowym.

## 3. Sekwencja wyświetlenia listy meczów

Projektowana trasa: GET /administracja/mecze, z parametrami id_sezon, id_rozgrywki, id_runda, id_kolejka, strona, rozmiar_strony i sortowanie. Szczegóły: GET /administracja/mecze/<id_mecz>. Są to planowane adresy, jeszcze niezarejestrowane.

```mermaid
sequenceDiagram
    actor U as Uzytkownik
    participant F as Flask
    participant Z as FabrykaZaleznosciZadania
    participant W as WidokListyMeczow
    participant S as SerwisMeczow
    participant R as RepozytoriumMeczowSQLAlchemy
    participant K as Sesja SQLAlchemy
    participant B as PostgreSQL
    participant J as Jinja2
    U->>F: GET /administracja/mecze z filtrami
    Note over F,W: Przed udostepnieniem panelu kontrola dostepu
    F->>W: Utworzenie instancji MethodView
    W->>Z: utworz_serwis_meczow()
    Z->>R: Nowe repozytorium z sesja biezacego kontekstu
    Z->>S: Nowy serwis z repozytorium
    Z-->>W: SerwisMeczow
    F->>W: get()
    W->>W: FormularzFiltrowMeczow i walidacja
    alt Bledne parametry
        W-->>F: Odpowiedz 400 z informacja o bledzie
    else Poprawne parametry
        W->>S: pobierz_liste(FiltryMeczow)
        S->>R: pobierz_liste(filtry)
        R->>B: Transakcja READ ONLY
        R->>B: SELECT z filtrami, sortowaniem i limitem
        R->>B: Liczba wszystkich pasujacych meczow
        alt Odczyt zakonczony
            B-->>R: Wiersze i liczba
            R-->>S: StronaMeczow bez obiektow ORM
            S-->>W: StronaMeczow
            W->>J: Renderowanie listy wedlug prototypu v6
            J-->>W: HTML
            W-->>F: Odpowiedz 200, takze dla pustej listy
        else Blad bazy
            B-->>R: Blad zapytania lub polaczenia
            R-->>S: BladOdczytuDanych
            S-->>W: BladOdczytuDanych
            W-->>F: Obsluga bledu HTTP 503
        end
    end
    F->>K: Sprzatanie przez Flask-SQLAlchemy przy zamknieciu kontekstu
    Note over K,B: ROLLBACK otwartej transakcji i zwrot polaczenia do puli
    F-->>U: Wynik zadania HTTP
```

Sesję sprząta integracja Flask-SQLAlchemy, a nie metoda repozytorium. Diagram pokazuje logiczny przepływ zapytań repozytorium do bazy; technicznie wykonuje je sesja SQLAlchemy przez sterownik. Przy błędzie walidacji transakcja nie musi zostać otwarta. Każde rzeczywiste użycie połączenia, również ponowne użycie z puli, musi zachować READ ONLY. Nie wykonujemy COMMIT ani zapisu przy odczycie.

Na etapie implementacji dobierz spójną migawkę dla zapytania strony i licznika, jeżeli mają przedstawiać dokładnie ten sam stan przy równoległych aktualizacjach danych. Zapytania mogą zostać połączone lub zoptymalizowane bez zmiany kontraktu wyniku. Diagram nie jest wymogiem wykonania dokładnie dwóch SELECT.

Dla szczegółów przebieg jest analogiczny: repozytorium przygotowuje dane meczu i powiązań bez mnożenia agregacji przez JOIN, a NieZnalezionoMeczu jest mapowane na 404. Renderowanie nie uruchamia lazy loading.

## 4. Etapy dostępu i późniejsza rozbudowa

Podczas lokalnej budowy wyglądu i odczytu nie udostępniamy panelu innym użytkownikom. Przed udostępnieniem etap logowania dodaje kontrolę sesji i uprawnień przed wykonaniem chronionego przypadku użycia. Nie projektujemy jeszcze tabel kont ani zapisu zmian administracyjnych.

Ekrany zespołów, zawodników i diagnostyki będą używały tego samego kierunku zależności, z kontraktami dopasowanymi do ich potrzeb. Eksporter będzie klientem serwisów, a nie kopią zapytań z widoków. Rozbudowa nie oznacza tworzenia pustych klas ani dodatkowych tabel.

## 5. Powiązanie z plikami i SOLID

| Obiekt | Planowany moduł w src/pilka_reczna/ | Odpowiedzialność |
| --- | --- | --- |
| FabrykaAplikacji | fabryka.py | Konfiguracja i złożenie aplikacji. |
| Ustawienia | ustawienia.py | Walidowana konfiguracja. |
| FabrykaZaleznosciZadania | fabryka_zaleznosci.py | Złożenie repozytorium i serwisu dla żądania. |
| KonfiguratorPolaczenia | infrastruktura/baza/polaczenie.py | Konfiguracja odczytu i integracji cyklu życia połączeń. |
| RejestratorWidokow | interfejs/rejestracja.py | Rejestracja adresów i klas widoków. |
| WidokListyMeczow, WidokSzczegolowMeczu | interfejs/administracja/widoki/mecze.py | Adaptacja HTTP. |
| FormularzFiltrowMeczow | interfejs/administracja/formularze/filtry_meczow.py | Walidacja parametrów i utworzenie FiltryMeczow. |
| SerwisMeczow | serwisy/mecze.py | Przypadki użycia niezależne od frameworka. |
| RepozytoriumOdczytuMeczow | kontrakty/mecze.py | Kontrakt odczytu bez metod zapisu. |
| RepozytoriumMeczowSQLAlchemy | infrastruktura/repozytoria/mecze.py | Zapytania i budowanie typowanego wyniku. |
| FiltryMeczow, StronaMeczow, PozycjaListyMeczow, SzczegolyMeczu | domena/mecze.py | Typowane dane wejścia i wyjścia. |
| NieZnalezionoMeczu, BladOdczytuDanych | domena/bledy.py | Błędy niezależne od HTTP i sterownika. |
| Mecz | infrastruktura/baza/modele/mecze.py | Mapowanie public.mecze. |

SRP oddziela HTTP, przypadek użycia i zapytania. DIP realizuje zależność serwisu od Protocol. ISP ogranicza kontrakt do odczytu. LSP wymaga tej samej semantyki błędów i wyników w obu repozytoriach. OCP pozwala dodać inną implementację repozytorium bez zmiany SerwisMeczow. Szczegółowe wymagania pozostają w [CODING_STANDARDS](CODING_STANDARDS.md).
