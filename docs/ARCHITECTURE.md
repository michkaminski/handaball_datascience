# Architektura i decyzje

## Ustalone

Flask będzie obsługiwał stronę i administrację. Nowa aplikacja powstaje w `handball_datascience`. Starszy serwis w katalogu nadrzędnym nie jest szkieletem nowej aplikacji.

Inspekcja 2026-09-12 potwierdziła PostgreSQL 15.1, bazę `zprp` na `localhost:5432`, użytkownika `postgres` oraz schematy `public` i `logs`. [Dokumentacja rzeczywistej bazy](database/README.md) jest punktem odniesienia dla zapytań. [Archiwalny plik schema_postgres.sql](database/schema_postgres_archive.sql) (kopia wcześniejszego projektu bazy z katalogu nadrzędnego, stan 2026-09-10) jest wcześniejszym projektem i różni się od bazy. Nie wykonuj go w celu nawiązania połączenia.

Decyzja użytkownika z 2026-09-12: AI nie zmienia bazy samodzielnie. Jakikolwiek zapis, zmiana struktury lub administracja bazą wymagają wyraźnej prośby o daną zmianę. Sama implementacja Flaska nie upoważnia do migracji ani zapisu. Do inspekcji używamy transakcji tylko do odczytu, bez zmiany globalnej konfiguracji PostgreSQL.

## Przyjęty podział obiektowy

Decyzja z 2026-09-12: cały nowy kod aplikacyjny powstaje obiektowo i zgodnie z SOLID. Aktualizacja nazewnictwa z 2026-09-14: pliki, katalogi, moduły i pakiety są angielskie; domena, metody i zmienne polskie bez znaków diakrytycznych, a role techniczne klas angielskie, np. MeczService i MeczRepository. Zachowujemy oryginalne API bibliotek i jawne mapowanie rzeczywistych nazw bazy. Przyjęty stos oraz uzasadnienie: [TECH_STACK](TECH_STACK.md). Wymagania implementacji: [CODING_STANDARDS](CODING_STANDARDS.md).

- AplikacjaFactory i Ustawienia składają aplikację oraz konfigurację. Cienki adapter create_app() obsługuje integrację z narzędziami Flaska.
- Klasy MethodView w Blueprints obsługują HTTP; szablony Jinja2 odpowiadają za prezentację.
- Klasy serwisów realizują przypadki użycia i logikę meczową.
- Kontrakty Protocol oddzielają serwisy od klas repozytoriów SQLAlchemy. Zależności przekazujemy przez konstruktor.
- Typowane modele SQLAlchemy 2.0 mapują istniejące tabele, a obiekty dataclass przenoszą filtry i wyniki.
- Flask-SQLAlchemy zarządza integracją silnika i sesji; sterownikiem PostgreSQL jest psycopg 3.
- Późniejszy eksporter będzie klasą korzystającą z tej samej logiki przypadków użycia.

Przepływ zależności:

```mermaid
flowchart LR
    V[MethodView] --> S[Serwis przypadku użycia]
    S --> P[Protocol repozytorium]
    R[Repozytorium SQLAlchemy] -. implementuje .-> P
    R --> DB[(Istniejący PostgreSQL)]
    F[AplikacjaFactory] -. składa obiekty .-> V
    F -. wstrzykuje implementację .-> S
```

Warstwy dla listy meczów są zaimplementowane; kolejne funkcje rozwijają ten podział. Twórz klasy potrzebne konkretnej funkcji, bez pustych warstw i ogólnych repozytoriów CRUD na zapas.

Projekt modułów: [DIRECTORY_STRUCTURE](DIRECTORY_STRUCTURE.md). Diagramy klas, składania zależności i obsługi żądania: [UML](UML.md). Istniejący pakiet aplikacji to `src/handball/`; przemianowanie kodu i odwołań wykonano 2026-09-14.

## Niezależność od języka bazy i interfejsu

Decyzja z 2026-09-14: język nazw domenowych nie wynika z języka tabel i kolumn. ORM mapuje fizyczny schemat, a repozytoria realizują kontrakty serwisów i zwracają obiekty domenowe. Przyszła baza z angielskimi nazwami może wymagać nowego mapowania i zapytań, przy zachowaniu polskiej domeny. Zmiany znaczenia danych wymagają osobnej analizy i testów; nie zakładamy automatycznej wymienności baz.

Nowy interfejs WWW może być kolejnym adapterem tych samych serwisów. Logika nadal nie zależy od Flask request, current_app ani sesji ORM. Nie tworzymy teraz dodatkowych adapterów ani migracji na zapas.

Nazwy klas i ścieżek w dokumentacji odpowiadają migracji z 2026-09-14. Pakiet dystrybucyjny i importowany to `handball`, testy są w `tests`, a skrypt startowy to `run.bat`. Flask jawnie wskazuje `interface/templates` i `interface/static`. Zachowano adresy `/administracja/`, `/administracja/mecze` i prefiks zasobów `/statyczne`; pliki zasobów nazywają się `admin.css` i `admin.js`.

## Decyzje otwarte

| Temat | Kiedy rozstrzygnąć |
| --- | --- |
| Dokładne wersje poprawek i konfiguracja narzędzi | Przy szkielecie: rozwiązanie zależności uv na Pythonie 3.13, zapis uv.lock i wspólne sprawdzenie |
| Integracja połączenia z Flaskiem | Parametry i schemat są rozpoznane; do przygotowania konfiguracja aplikacji bez sekretów w MD |
| Źródło kont, role i operacje administracyjne | Przed implementacją panelu; biblioteką sesji użytkownika będzie Flask-Login |
| Własne tabele aplikacji i migracje | Gdy pojawi się potrzeba trwałego zapisu |
| Format eksportu i hosting | Przy rozpoczęciu etapu publicznego serwisu |

## Warunki implementacji

Start aplikacji nie może importować danych, tworzyć tabel ani uruchamiać migracji w istniejącej bazie. Repozytoria odczytu korzystają z transakcji READ ONLY; sesji nie współdzielimy między żądaniami. Parametry zapytań muszą być przekazywane przez mechanizm sterownika/ORM; sortowanie wybierane z dopuszczonych pól. Zapytania listujące powinny mieć limit i stabilny porządek.

Przed udostępnieniem administracji wymagane są uwierzytelnienie, kontrola uprawnień oraz ochrona formularzy zmieniających stan. Pola pochodzące ze źródeł danych wymagają bezpiecznego renderowania. Eksport publiczny powinien mieć jawny zestaw pól, zamiast kopiować całe rekordy bazy.

Istotną rozstrzygniętą decyzję zapisuj tutaj z datą, powodem i skutkami. Osobny ADR dodawaj dopiero, gdy uzasadnienie jest zbyt obszerne dla tego dokumentu.
