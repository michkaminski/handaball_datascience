# Wybrane technologie

Decyzja projektowa: 2026-09-12. Technologie wybrano dla obiektowej aplikacji Flask korzystającej z istniejącej bazy PostgreSQL. To wybór do implementacji; zależności nie zostały jeszcze zainstalowane ani wspólnie przetestowane.

## Rdzeń aplikacji

| Obszar | Wybór | Zastosowanie i powód |
| --- | --- | --- |
| Python | 3.13.x | Linia bazowa projektu; lokalnie potwierdzono 3.13.15. Typowany kod obiektowy. |
| Framework | Flask 3.1.x | Strona i administracja, podział na Blueprints, widoki klasowe MethodView. [Dokumentacja](https://flask.palletsprojects.com/en/stable/views/). |
| ORM | SQLAlchemy 2.0.x | Jawne klasy modeli, Mapped i mapped_column, zapytania w stylu select(). [Dokumentacja integracji](https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/). |
| Integracja ORM | Flask-SQLAlchemy 3.1.x | Konfiguracja silnika i sesja związana z kontekstem aplikacji Flask. Warstwy logiki nie importują rozszerzenia. [Dokumentacja](https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/). |
| Sterownik | psycopg 3, pakiet psycopg[binary] dla lokalnego Windows | Synchroniczne połączenie z PostgreSQL przez dialekt postgresql+psycopg. [Dokumentacja dialektu](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg). |
| Baza | Istniejący PostgreSQL 15.1 | localhost:5432/zprp, schematy public i logs. Wybór stosu nie obejmuje aktualizacji serwera ani zmiany bazy. |
| Renderowanie | Jinja2 dostarczane z Flaskiem, HTML5 i CSS | Widoki renderowane po stronie serwera; obliczenia domenowe pozostają w klasach Pythona. |
| Konfiguracja | Klasa Ustawienia oparta na dataclass i zmiennych środowiska | Typowane, walidowane ustawienia bez sekretów w repozytorium. |
| Obiekty wejścia i wyniku | dataclass, w razie potrzeby frozen=True | Filtry i wyniki przypadków użycia jako jawne obiekty, niezależne od Flask request i modeli ORM. |

Wybieramy synchroniczne Flask i SQLAlchemy. Model sesji oraz obsługi żądań będzie jednolity w całym backendzie.

## Formularze i administracja

| Obszar | Wybór | Kiedy dodać |
| --- | --- | --- |
| Formularze | Flask-WTF / WTForms | Przy pierwszym formularzu; klasy formularzy, walidacja i ochrona CSRF. [Dokumentacja](https://flask-wtf.readthedocs.io/en/1.2.x/). |
| Sesja zalogowanego użytkownika | Flask-Login | Przy implementacji logowania administratora. Biblioteka nie zastępuje polityki ról i uprawnień. [Dokumentacja](https://flask-login.readthedocs.io/en/latest/). |
| Panel administracyjny | Własne klasy MethodView i szablony Jinja2 | Widoki dopasowane do meczów, źródeł i anomalii. Operacje zapisu dopiero po wyraźnym zleceniu użytkownika. |

Sposób przechowywania kont, role i lista operacji pozostają do rozstrzygnięcia przed logowaniem. Wybór Flask-Login nie upoważnia do tworzenia tabel kont. Nie dodajemy teraz automatycznego panelu CRUD nad wszystkimi tabelami.

## Narzędzia pracy

| Obszar | Wybór | Rola |
| --- | --- | --- |
| Środowisko i zależności | uv, pyproject.toml, uv.lock | Osobne środowisko projektu i powtarzalny zestaw zależności. [Dokumentacja](https://docs.astral.sh/uv/). |
| Formatowanie i lint | Ruff | Jedno narzędzie do formatowania i kontroli kodu. [Dokumentacja](https://docs.astral.sh/ruff/). |
| Typowanie | mypy w trybie strict dla nowego pakietu | Sprawdzanie kontraktów klas; ewentualne wyjątki ograniczone do konkretnej integracji. [Dokumentacja](https://mypy.readthedocs.io/en/stable/). |
| Testy | pytest i klient testowy Flaska | Testy klas logiki, kontraktów repozytoriów i zachowania HTTP. [Dokumentacja pytest](https://docs.pytest.org/en/stable/). |
| Serwer WSGI | Waitress | Wybrany dla uruchomienia na Windows; konfiguracja przy przygotowaniu uruchamiania. [Dokumentacja](https://docs.pylonsproject.org/projects/waitress/en/stable/). |

Linie wersji rdzenia wyznaczają wybór architektoniczny. Przy szkielecie rozwiąż zależności na Pythonie 3.13, zapisz konkretne wersje poprawek i narzędzi w uv.lock oraz sprawdź je razem. Nie traktuj podanych linii jako obietnicy przetestowanej zgodności ani jako polecenia instalowania wszystkiego teraz.

## SQLAlchemy a istniejąca baza

Modele mają odwzorowywać rzeczywisty schemat opisany w [dokumentacji bazy](database/README.md). W tym projekcie nazwy klas i atrybutów Pythona pisz po polsku, bez znaków diakrytycznych. Atrybuty modeli odpowiadają nazwom istniejących kolumn, np. id_sezon i id_zespol_gosp. Klasy nazywaj w liczbie pojedynczej, np. Mecz dla tabeli mecze i ZespolSezon dla zespoly_sezony. Zachowaj jawne przypisanie modelu do rzeczywistej tabeli; nie tłumacz nazw bazy ani nie zmieniaj jej struktury. Każdy model określa schemat public lub logs. Twórz mapowania tabel potrzebnych bieżącej funkcji, z pełnym uwzględnieniem ich rzeczywistych kluczy.

W szczególności uwzględniaj złożony PK mecze_zawodnicy, bigint zespoly_sezony.id, osobne id_api, dopuszczalne NULL uczestników oraz dwa FK drużyn w mecze. Przy relacjach gospodarza i gościa jawnie rozstrzygaj foreign_keys. Dane sezonowe dobieraj z właściwego sezonu.

Definicja klas ORM nie daje zgody na create_all(), drop_all(), migracje, flush() ani commit() do istniejącej bazy. Połączenia odczytowe mają wymuszać READ ONLY dla każdej transakcji, także po ponownym użyciu połączenia z puli. Wyłączenie autoflush może ograniczać przypadkowe zapisy, ale nie zastępuje tego zabezpieczenia. Transakcje odczytu kończ rollback; sesję sprząta integracja Flask-SQLAlchemy przy zamknięciu kontekstu.

Alembic/Flask-Migrate nie wchodzą do bieżącego etapu. Narzędzie migracyjne dobierz, gdy użytkownik wyraźnie zleci zmianę schematu; najpierw zaplanuj zgodność z istniejącymi obiektami i historią logs.

## Późniejszy serwis publiczny

Utrzymujemy ustalony kierunek HTML + JSON + JavaScript. Format eksportu, biblioteki interfejsu i hosting wybierzemy przy tym etapie. Obecny wybór nie dodaje frameworka SPA, kolejki zadań, cache ani bibliotek uczenia maszynowego.
