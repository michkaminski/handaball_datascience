# Handball DataScience

Serwis do przeglądania danych meczów polskich seniorskich lig piłki ręcznej, ze szczególnym uwzględnieniem Superligi M i K oraz Lig Centralnych.

Obecny etap: działająca aplikacja Flask z administracją i listą meczów. Działają szczegóły meczu, modal, zakładki i panel importu; odczyt domenowy jest oddzielony od presenterów i modeli widoku. Pakiet `handball` oraz nazwy plików, katalogów i klas technicznych stosują uzgodnioną konwencję.

## Uruchomienie i sprawdzenia

W katalogu projektu uruchom `run.bat` albo:

```powershell
uv sync
uv run flask --app handball run
```

Panel: `http://127.0.0.1:5000/administracja/`. Nazwy zmiennych konfiguracji połączenia opisuje `.env.example`.

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --ignore=tests/integration
```

Ostatnia komenda sprawdza logikę i widoki bez bazy. Testy w `tests/integration` wymagają osobnego, świadomego uruchomienia zgodnie z zasadami bazy w AGENTS.md.

## Dokumentacja

| Plik | Przeznaczenie |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Główne instrukcje pracy AI w tym katalogu |
| [PROJECT](docs/PROJECT.md) | Zakres produktu i kryteria pierwszego etapu |
| [MOJA_ARCHITECTURE — MD](docs/MOJA_ARCHITECTURE.md) / [HTML](docs/MOJA_ARCHITECTURE.html) | Przewodnik po kodzie krok po kroku, z interaktywnym UML |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Ustalenia techniczne i otwarte decyzje |
| [TECH_STACK](docs/TECH_STACK.md) | Wybrane technologie i etapy ich wdrażania |
| [CODING_STANDARDS](docs/CODING_STANDARDS.md) | Obiektowy Python, SOLID, typowanie i kryteria review |
| [IMPORTS](docs/IMPORTS.md) | Aktualizacja ZPRP krok po kroku, tekstowy UML, statusy i zapis danych |
| [DATA](docs/DATA.md) | Źródła i pułapki interpretacji danych |
| [Baza danych](docs/database/README.md) | Zweryfikowane połączenie, rzeczywisty schemat, relacje i historia zmian |
| [AI_WORKFLOW](docs/AI_WORKFLOW.md) | Role agentów i dobór skillsów |
| [DIRECTORY_STRUCTURE](docs/DIRECTORY_STRUCTURE.md) | Projekt katalogów, plików i odpowiedzialności warstw |
| [TEMPLATES](docs/TEMPLATES.md) | Indeks opisów poszczególnych szablonów i zasady ich aktualizacji |
| [UML](docs/UML.md) | Diagramy klas, składania zależności i obsługi żądania |
| [IMPLEMENTATION_PLAN](docs/IMPLEMENTATION_PLAN.md) | Wzorzec wyglądu administracji i kolejne etapy realizacji |
| [STATUS](docs/STATUS.md) | Stan projektu i następny krok |

## Praca z AI

Cały nowy kod aplikacyjny piszemy obiektowo i zgodnie z SOLID. Przyjęty rdzeń: Python 3.13, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1 i psycopg 3. Obowiązuje standard specjalisty Flask i obiektowego Pythona opisany w CODING_STANDARDS. [Konwencja nazewnictwa](docs/CODING_STANDARDS.md#język-i-nazewnictwo): angielskie pliki i katalogi, polska domena oraz angielskie role klas, np. MeczService i MeczRepository. Konwencja została wdrożona w istniejącym kodzie.

AI może badać bazę tylko do odczytu. Zmiany w bazie wykonuje dopiero na wyraźną prośbę użytkownika o konkretną zmianę. Hasło nie jest przechowywane w dokumentacji.

Otwórz `handball_datascience` jako katalog projektu. Projektowe skillsy znajdują się w `.agents/skills/`. Jeśli bieżąca sesja nie pokazuje nowych skillsów, rozpocznij sesję w tym katalogu; można również wskazać AI konkretny plik `SKILL.md` do przeczytania.

Przykładowe zadania:

- „Użyj $hds-data-contract i przygotuj mapowanie danych potrzebnych do listy meczów”.
- „Użyj $hds-flask-feature i zbuduj pierwszy widok zgodnie z zakresem projektu”.
- „Użyj $hds-review i sprawdź zmiany w widoku meczu”.

Role w AI_WORKFLOW są instrukcjami organizacji pracy, a nie zainstalowanymi procesami ani konfiguracją automatycznie uruchamianych subagentów.

Konwencje instrukcji i skillsów: [oficjalna dokumentacja AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) oraz [skillsów](https://learn.chatgpt.com/docs/build-skills).
