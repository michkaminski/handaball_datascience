# Kolejne kroki realizacji

## Wzorzec wyglądu administracji

Decyzja użytkownika: wygląd strony administracyjnej ma opierać się na prototypie:

`C:\Michal\_ZPRP_PROD\Prototyp\Prototyp_administracja_v6`

Katalog jest dostępny. Sprawdzono listę plików i README; nie przeprowadzono jeszcze oceny wizualnej w przeglądarce. Zawiera m.in. index.html, matches.html, match_detail.html, match_edit.html, players.html, imports.html, quality.html, logs.html oraz assets/style.css i assets/app.js.

Według README prototypu v6 najważniejsza jest tabela meczów, nagłówki i filtry są zwarte, statystyki mają formę małych pigułek, a baner i górne menu mają szerokość reszty strony. Przy implementacji trzeba obejrzeć właściwe ekrany i zachować ich układ, proporcje, typografię, kolory, tabele, filtry i nawigację. Nie projektować administracji od nowa bez polecenia użytkownika.

Prototyp jest wzorcem wizualnym. Dane przykładowe i przyciski edycji nie definiują uprawnień ani nie oznaczają zgody na zapis w bazie. Kod backendu podlega standardom obiektowym, SOLID i polskiemu nazewnictwu tego projektu. Docelowa nazwa aplikacji pozostaje Handball DataScience.

Pliki źródłowego prototypu traktuj jako materiał do odczytu. Adaptowane szablony i zasoby umieszczaj w handball_datascience. Jeśli prototyp będzie niedostępny w innym środowisku, zgłoś brak źródła przed odtwarzaniem wyglądu z domysłów.

## Kolejność prac

Wszystkie poniższe etapy są planowane. Kryteria określają moment ukończenia etapu, nie stan już działającej aplikacji.

| Etap | Zakres | Kryterium ukończenia |
| --- | --- | --- |
| 1. Obiektowy szkielet Flaska | uv, pyproject.toml, uv.lock, FabrykaAplikacji, Ustawienia, Blueprints, Ruff, mypy i pytest | Aplikacja startuje lokalnie, konfiguracja jest walidowana, podstawowe kontrole przechodzą; start nie zmienia bazy. |
| 2. Układ administracji | Obejrzenie index.html i matches.html prototypu, adaptacja wspólnego szablonu Jinja2 i zasobów CSS/JS | Układ odpowiada v6, nawigacja i podstawowe stany działają, wygląd sprawdzono w przeglądarce także na wąskim ekranie. |
| 3. Odczyt przez SQLAlchemy | Modele potrzebne liście meczów, kontrakt repozytorium, implementacja SQLAlchemy, sesja READ ONLY | Pobranie danych działa z istniejącym schematem, a cykl życia sesji i ochrona przed zapisem są zweryfikowane bez modyfikowania bazy. |
| 4. Lista meczów | SerwisMeczow, widok MethodView, filtry sezonu/rozgrywek/etapu/kolejki, paginacja i sortowanie | Lista używa rzeczywistych danych, zachowuje filtry i rozróżnia brak danych, pusty wynik i błąd połączenia. |
| 5. Szczegóły meczu | Adaptacja match_detail.html, zespoły, wynik, skład i dostępne statystyki | Potwierdzono interpretację wariantów wyniku i zamiana; niepełne dane są widoczne, a agregacje nie mnożą wpisów przez JOIN. |
| 6. Dostęp administratora | Ustalenie źródła kont i ról, Flask-Login, kontrola dostępu | Chronione widoki wymagają właściwych uprawnień; sposób logowania jest przetestowany. Przygotować przed udostępnieniem panelu innym użytkownikom. |
| 7. Pozostałe widoki odczytu | Kolejno uzgodnione ekrany drużyn, zawodników, tabel oraz jakości/importów/logów, według prototypu | Każdy ekran ma potwierdzone mapowanie danych, testy zachowania i zgodny wygląd. |

Operacje edycji, importu i migracje nie są częścią domyślnej realizacji tych etapów. Wymagają wyraźnej prośby użytkownika o konkretną zmianę. Dotyczy to także ewentualnego utworzenia tabel kont lub bazy testowej. Publiczny eksport HTML/JSON/JavaScript pozostaje kolejnym, osobnym etapem projektu.

## Projekt katalogów i obiektów

[DIRECTORY_STRUCTURE](DIRECTORY_STRUCTURE.md) przypisuje katalogi i pliki do etapów, a [UML](UML.md) opisuje klasy, zależności i cykl żądania. Tworzymy tylko elementy potrzebne realizowanemu etapowi. Każdy szablon ma własny MD obok HTML; [TEMPLATES](TEMPLATES.md) zawiera indeks przygotowanych opisów. Ukończenie zmiany szablonu wymaga zgodności jego dokumentacji z implementacją.

## Punkt rozpoczęcia

Najbliższe zadanie implementacyjne: etap 1, następnie wspólny układ administracji z prototypu v6. Wymagania techniczne: [TECH_STACK](TECH_STACK.md), [CODING_STANDARDS](CODING_STANDARDS.md) i [ARCHITECTURE](ARCHITECTURE.md). Postęp zapisujemy w [STATUS](STATUS.md).
