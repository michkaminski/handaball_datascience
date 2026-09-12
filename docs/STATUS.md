# Stan projektu

Aktualizacja: 2026-09-12.

## Gotowe

- Przyjęta nazwa Handball DataScience i katalog projektu.
- Instrukcje AGENTS.md, dokumentacja zakresu, architektury i danych.
- Opis ról AI oraz trzy projektowe skillsy.
- Użytkownik potwierdził wcześniejszy import bazy.
- Zweryfikowano połączenie `localhost:5432/zprp` jako `postgres` i rzeczywisty schemat PostgreSQL 15.1 w trybie tylko do odczytu.
- [Opisano bazę](database/README.md): 65 tabel, 2 widoki, kolumny, klucze, indeksy, triggery, funkcje i relacje. Liczby rekordów mają oznaczony czas odczytu.
- Zapisano zakaz samodzielnych zmian w bazie; konkretna zmiana wymaga wyraźnej prośby użytkownika.

- Przyjęto obiektowy Python, SOLID, role specjalisty Flask/SQLAlchemy i [standardy kodu](CODING_STANDARDS.md).
- [Wybrano technologie](TECH_STACK.md): Python 3.13, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, psycopg 3 oraz narzędzia jakości.

- Ujednolicono nazewnictwo: własne identyfikatory po polsku bez znaków diakrytycznych, z zachowaniem oryginalnego API bibliotek i nazw bazy.

- Wskazano prototyp administracji v6 jako wzorzec wyglądu; potwierdzono dostępność katalogu i przeczytano jego README.
- Zapisano [kolejność realizacji](IMPLEMENTATION_PLAN.md) z kryteriami ukończenia etapów.

- Przygotowano [projekt katalogów](DIRECTORY_STRUCTURE.md) i [UML](UML.md): diagramy klas, kompozycji oraz sekwencji listy meczów.
- Utworzono 11 [opisów szablonów](TEMPLATES.md) w docelowym katalogu szablonów. Istnieją katalogi i pliki MD, bez HTML.

- Ukończono etap 1 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): obiektowy szkielet Flaska. Utworzono `pyproject.toml`, `uv.lock`, `.python-version` i `.gitignore`; `uv sync` instaluje Flask 3.1.3 zgodnie z TECH_STACK.
- Utworzono klasy `Ustawienia`, `FabrykaAplikacji`, `RejestratorWidokow`, Blueprint `administracja` z `WidokStartowy` oraz adapter `create_app()` w `src/pilka_reczna/`.
- Skonfigurowano Ruff, mypy (strict) i pytest w `pyproject.toml`. Wykonano i potwierdzono: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` (bez błędów, 8 plików źródłowych) oraz `uv run pytest` (6 testów, wszystkie przechodzą).
- Zweryfikowano lokalne uruchomienie: `create_app()` rejestruje trasy `/administracja/` i `/static/...`, żądanie GET zwraca 200; start nie łączy się z bazą `zprp`.

- Ukończono etap 2 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): wspólny układ administracji na podstawie prototypu v6. Utworzono `baza.html`, `elementy/nawigacja.html`, `elementy/komunikaty.html`, `administracja/start.html` oraz `statyczne/css/administracja.css` (adaptacja `index.html`/`assets/style.css` prototypu, bez sidebara i bez fikcyjnych danych meczowych — `start.html` pokazuje jawny stan "brak danych" zamiast przykładowych wierszy z prototypu).
- `FabrykaAplikacji` jawnie konfiguruje `template_folder`/`static_folder`/`static_url_path` (`szablony`/`statyczne`), zgodnie z ARCHITECTURE i DIRECTORY_STRUCTURE. `WidokStartowy` renderuje `administracja/start.html` zamiast zwracać czysty tekst.
- Zaktualizowano MD czterech zaimplementowanych szablonów (baza, nawigacja, komunikaty, start) zgodnie z rzeczywistym kontraktem, blokami i selektorami.
- Sprawdzono wizualnie w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px: układ zgodny z v6, responsywność działa, brak przewijania poziomego. `uv run pytest` (7/7), `ruff check`, `ruff format --check` i `mypy` przechodzą bez błędów.
- `js/administracja.js` świadomie nie utworzono — obecny układ (bez sidebara, bez filtrów) nie używa jeszcze żadnego zachowania z prototypowego `app.js`; doda się go razem z pierwszą potrzebną interakcją.

## Jeszcze niewykonane

- Odczyt przez SQLAlchemy, lista i szczegóły meczu (etapy 3–5).
- Dostęp administratora i pozostałe widoki odczytu (etapy 6–7).
- Sidebar administracji (odłożony do etapu z realnymi sekcjami, np. etap 7) i pozostałe szablony (paginacja, mecze/lista, mecze/szczegoly, logowanie, bledy) — mają MD, brak HTML.
- Eksport i publiczny serwis.

## Następny krok

Etap 3 z [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): modele SQLAlchemy potrzebne liście meczów, kontrakt repozytorium (`RepozytoriumOdczytuMeczow`), implementacja SQLAlchemy z sesją READ ONLY. Wymaga połączenia z bazą `zprp` — konfiguracja przez zmienne środowiska, bez zapisu i bez tworzenia tabel.

Nie używać `python ../run.py` jako komendy uruchomienia nowej aplikacji: dotyczy starszego serwisu i jego procesu importu.
