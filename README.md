# Handball DataScience

Serwis do przeglądania danych meczów polskich seniorskich lig piłki ręcznej, ze szczególnym uwzględnieniem Superligi M i K oraz Lig Centralnych.

Obecny etap: działająca aplikacja Flask z administracją oraz listami meczów i zawodników. Działają szczegóły meczu, modal, zakładki i panel importu; odczyt domenowy jest oddzielony od presenterów i modeli widoku. Pakiet `handball` oraz nazwy plików, katalogów i klas technicznych stosują uzgodnioną konwencję.

## Uruchomienie i sprawdzenia

W katalogu projektu uruchom `run.bat` albo:

```powershell
uv sync
uv run python app.py
```

Port domyślny: `5057` (`HDS_PORT`). Na Linuxie (Ubuntu Server) uruchom `./run.sh`: tworzy `.venv`, gdy go brak, i doinstalowuje zależności tylko po ich zmianie (przez `uv`, a bez niego przez `pip` i Python 3.13). PDF wymaga `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`; z `.env` usuń `WEASYPRINT_DLL_DIRECTORIES`.

PDF zapowiedzi meczu (przycisk „Pobierz PDF”) generuje WeasyPrint, który na Windows potrzebuje bibliotek Pango. Instalacja jednorazowa:

1. Zainstaluj [MSYS2](https://www.msys2.org/) w domyślnym katalogu `C:\msys64` (instalator ze strony albo `winget install --id MSYS2.MSYS2 -e`).
2. Otwórz z menu Start „MSYS2 MSYS” i wykonaj `pacman -Syu` (jeśli konsola się zamknie, otwórz ją ponownie i powtórz polecenie), a potem `pacman -S mingw-w64-x86_64-pango`.
3. Sprawdź, że istnieje plik `C:\msys64\mingw64\bin\libpango-1.0-0.dll`.
4. Uruchom ponownie serwer przez `run.bat` — sam ustawi `WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin`. Przy innej ścieżce ustaw tę zmienną ręcznie. Skrypt dopisuje ten katalog także na początek `PATH`, bo biblioteki szukane są najpierw w `PATH`, a inne programy (np. Meld) mają tam starsze wersje GTK/Pango, których mieszanie kończy się błędem `cannot load library … error 0x7f`. Bez Pango reszta aplikacji działa, a trasa PDF zwraca 503 z tą instrukcją.

Panel: `http://127.0.0.1:5057/administracja/`. Lista zawodników: `/administracja/zawodnicy` — filtry, sortowanie i paginacja. Nazwy zmiennych konfiguracji połączenia opisuje `.env.example`.

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --ignore=tests/integration
```

Model Atrakcyjności Frekwencyjnej (zakładka Raporty › Frekwencja › Atrakcyjność) wymaga jednorazowego treningu, który nie zmienia bazy: `uv run python -m handball.maf_cli` — szczegóły w [docs/MAF.md](docs/MAF.md). Biblioteka matematyczna: `/matematyka/`.

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
| [PLAYER_DATA_SCIENCE](docs/PLAYER_DATA_SCIENCE.md) | Projekt profesjonalnej analityki i wizualizacji karty zawodnika |
| [Baza danych](docs/database/README.md) | Zweryfikowane połączenie, rzeczywisty schemat, relacje i historia zmian |
| [AI_WORKFLOW](docs/AI_WORKFLOW.md) | Role agentów i dobór skillsów |
| [DIRECTORY_STRUCTURE](docs/DIRECTORY_STRUCTURE.md) | Projekt katalogów, plików i odpowiedzialności warstw |
| [TEMPLATES](docs/TEMPLATES.md) | Indeks opisów poszczególnych szablonów i zasady ich aktualizacji |
| [UML](docs/UML.md) | Diagramy klas, składania zależności i obsługi żądania |
| [IMPLEMENTATION_PLAN](docs/IMPLEMENTATION_PLAN.md) | Wzorzec wyglądu administracji i kolejne etapy realizacji |
| [MAF](docs/MAF.md) | Model Atrakcyjności Frekwencyjnej i biblioteka Matematyka |
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
