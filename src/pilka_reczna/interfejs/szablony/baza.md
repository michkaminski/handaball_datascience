# Wspólny układ administracji

Status: etap 2 ukończony. Szablon `baza.html` istnieje w katalogu szablony.

Docelowy szablon względem katalogu szablony: `baza.html`.

## Przeznaczenie

Wspólna szerokość strony, nagłówek, obszar nawigacji, miejsce na komunikaty i blok treści. Punkt odniesienia: wspólny układ prototypu v6 (`index.html`, `assets/style.css`).

## Dane wejściowe

Bloki Jinja2 `tytul` (zawartość `<title>`) i `tresc` (treść `<main>`) dostarczane przez szablon potomny. Zmienna `pozycje_nawigacji` (lista słowników z kluczami `etykieta`, `adres`, `aktywna`) musi być przekazana przez widok do `render_template`, ponieważ `elementy/nawigacja.html` jest dołączany wewnątrz tego szablonu i korzysta z tej samej zmiennej kontekstu.

## Powiązania

Wszystkie pełne strony dziedziczą ten układ (`{% extends "baza.html" %}`). Korzysta z `elementy/nawigacja.html` i `elementy/komunikaty.html` przez `{% include %}`. Ładuje `statyczne/css/administracja.css` przez `url_for('static', ...)`.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj układ wspólny. Kolory, odstępy i typografię zmieniaj w statyczne/css/administracja.css; danych tabel nie zmieniaj w tym szablonie.

Sidebar prototypu v6 (`aside.sidebar` z sezonami, rozgrywkami, drużynami itd.) nie jest jeszcze zaimplementowany: większość jego pozycji nie ma odpowiadających widoków w obecnym zakresie projektu (patrz PROJECT.md i DIRECTORY_STRUCTURE.md). Layout używa klasy `.layout.jednokolumnowy` (dodanej w administracja.css) zamiast siatki dwukolumnowej z prototypu. Sidebar dodać dopiero, gdy powstanie kilka realnych sekcji do niego kwalifikujących się (np. przy etapie 7).

Nagłówek pomija selektor sezonu i wyszukiwarkę z prototypu — te elementy wymagają rzeczywistych danych i logiki (etap 4+); dodać je dopiero z działającą funkcją, nie jako dekorację.

## Sprawdzenie zmiany

Sprawdź wszystkie strony potomne, szerokości ekranu, widoczność komunikatów i brak podwójnej nawigacji.

## Stan implementacji

Wykonano: render_template z `administracja/start.html` (jedyna istniejąca strona potomna), sprawdzenie w przeglądarce (Playwright, Chromium headless) przy szerokościach ~1400px i ~380px — układ spójny z v6, responsywność działa (nagłówek i stopka składają się na wąskim ekranie), brak przewijania poziomego. `uv run pytest` sprawdza obecność `class="nav"` i tekstu marki w odpowiedzi HTTP. Nie sprawdzono jeszcze: wielu komunikatów naraz, długiego tekstu w komunikatach, zachowania z realnym sidebarem (nieistniejącym na tym etapie).
