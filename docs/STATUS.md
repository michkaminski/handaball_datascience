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

## Jeszcze niewykonane

- Wspólny układ administracji na podstawie prototypu v6 (etap 2): szablony Jinja2, CSS i JS.
- Odczyt przez SQLAlchemy, lista i szczegóły meczu (etapy 3–5).
- Dostęp administratora i pozostałe widoki odczytu (etapy 6–7).
- Eksport i publiczny serwis.

## Następny krok

Etap 2 z [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): obejrzeć index.html i matches.html prototypu administracji v6, a następnie zaadaptować wspólny układ Jinja2 (`baza.html`) i zasoby CSS/JS zgodnie z istniejącymi opisami w `interfejs/szablony/`. Szczegółowe uprawnienia administracji i interpretacja wyników pozostają do ustalenia przed ich implementacją.

Nie używać `python ../run.py` jako komendy uruchomienia nowej aplikacji: dotyczy starszego serwisu i jego procesu importu.
