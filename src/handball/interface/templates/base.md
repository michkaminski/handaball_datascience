# Wspólny układ administracji

Status: etap 4 ukończony. Szablon `base.html` istnieje w katalogu szablony.

Docelowy szablon względem katalogu szablony: `base.html`.

## Przeznaczenie

Wspólna szerokość strony, nagłówek, obszar nawigacji, miejsce na komunikaty i blok treści. Punkt odniesienia: wspólny układ prototypu v6 (`index.html`, `assets/style.css`).

## Dane wejściowe

Bloki Jinja2 `tytul` (zawartość `<title>`) i `tresc` (treść `<main>`) dostarczane przez szablon potomny. Zmienna `sekcja_aktywna` (string, klucz pozycji menu, np. `"start"` lub `"mecze"`) musi być przekazana przez widok do `render_template` — określa, która pozycja górnego paska i sidebara jest podświetlona jako aktywna.

Struktura samego menu (`GORNY_PASEK`, `SIDEBAR` — pełny zestaw grup i pozycji 1:1 z prototypem v6, patrz `interface/navigation.py`) nie jest przekazywana przez widok: jest wstrzykiwana globalnie do wszystkich szablonów przez `zarejestruj_kontekst_nawigacji()` (context processor Flask, wywoływany w `AplikacjaFactory.utworz()`). Każda pozycja ma `klucz`, `etykieta`, `ikona` i `punkt_koncowy` (nazwa endpointu Flask albo `None`, jeśli widok jeszcze nie istnieje).

## Powiązania

Wszystkie pełne strony dziedziczą ten układ (`{% extends "base.html" %}`). Korzysta z `partials/navigation.html` (górny pasek) i `partials/messages.html` przez `{% include %}`. Sidebar (`aside.sidebar`) jest zapisany bezpośrednio w tym pliku (nie w osobnym szablonie): iteruje po grupach `sidebar` z kontekstu globalnego. Ładuje `static/css/admin.css` i `static/js/admin.js` przez `url_for('static', ...)`.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj znacznik `<aside class="sidebar">` i sposób renderowania pozycji. Samą **zawartość** menu (pozycje, grupy, ikony, docelowe endpointy) zmieniaj w `interface/navigation.py` (`GORNY_PASEK`, `SIDEBAR`), nie w tym szablonie. Kolory, odstępy i typografię zmieniaj w static/css/admin.css; danych tabel nie zmieniaj w tym szablonie.

Sidebar renderuje pełną strukturę prototypu v6 (grupy Dane/Import-eksport/Narzędzia, wszystkie pozycje z ikonami) — na wyraźne polecenie użytkownika, żeby wygląd jak najwierniej odpowiadał prototypowi. Pozycje bez zaimplementowanego widoku mają `punkt_koncowy=None` i renderują się jako `href="#"` (widoczne, ale nieaktywne) — dodaj prawdziwy endpoint w `interface/navigation.py`, gdy dany ekran faktycznie powstanie; nie podłączaj linku, zanim widok nie istnieje.

Nagłówek pomija selektor sezonu i wyszukiwarkę z prototypu — te elementy wymagają rzeczywistych danych i logiki; dodać je dopiero z działającą funkcją, nie jako dekorację.

Przycisk `.mobile-menu[data-mobile-menu]` pokazuje/chowa sidebar na wąskim ekranie (obsługa w static/js/admin.js, tylko to jedno zachowanie, bez filtrowania tabel ani modali — nieużywanych na tym etapie).

## Sprawdzenie zmiany

Sprawdź wszystkie strony potomne, szerokości ekranu, widoczność komunikatów, poprawne oznaczenie aktywnej pozycji (górny pasek i sidebar) i brak podwójnej nawigacji.

## Stan implementacji

Wykonano: render_template z `admin/start.html` i `admin/matches/list.html`, sprawdzenie w przeglądarce (Playwright, Chromium headless) przy szerokościach ~1400px i ~380px oraz porównanie zrzutu z prototypem v6 (`index.html`, `matches.html`) — układ (nagłówek, górny pasek, pełny sidebar, treść, stopka) spójny z prototypem, w tym z rzeczywistymi danymi z bazy `zprp`. Sprawdzono kliknięcie `☰ Menu` na wąskim ekranie — sidebar poprawnie się rozwija i chowa. `uv run pytest` sprawdza obecność `class="nav"` i tekstu marki w odpowiedzi HTTP. Nie sprawdzono jeszcze: wielu komunikatów naraz, długiego tekstu w komunikatach.
