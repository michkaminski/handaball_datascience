# Wspólny układ administracji

Status: etap 4 ukończony. Szablon `base.html` istnieje w katalogu szablony.

Docelowy szablon względem katalogu szablony: `base.html`.

## Przeznaczenie

Wspólna szerokość strony, nagłówek, obszar nawigacji, miejsce na komunikaty i blok treści. Punkt odniesienia: wspólny układ prototypu v6 (`index.html`, `assets/style.css`).

## Dane wejściowe

Bloki Jinja2 `tytul` (zawartość `<title>`) i `tresc` (treść `<main>`) dostarczane przez szablon potomny. Zmienna `sekcja_aktywna` (string, klucz pozycji menu, np. `"start"`, `"mecze"` lub `"zawodnicy"`) musi być przekazana przez widok do `render_template` — określa, która pozycja górnego paska i sidebara jest podświetlona jako aktywna.

Dla listy zawodników sidebar wyróżnia „Zawodnicy”, a górny pasek „Dane”. Strony raportów przekazują dodatkowo `sekcja_glowna="raporty"` dla górnego paska (zob. [navigation.md](partials/navigation.md)); grupa sidebara „Raporty” zawiera „Katalog raportów”, „Prognozy meczów” i „Typowania meczów”. Pozycja zawodników prowadzi do `administracja.lista_zawodnikow`. W grupie „Dane” po „Mecze” jest „Terminarz” (`administracja.terminarz`); terminarz i zapowiedź meczu przekazują `sekcja_aktywna="terminarz"` i `sekcja_glowna="mecze"`, więc w górnym pasku świeci „Dane”.

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

## Układ tekstowy i mapa zmian

Stan: rzeczywisty układ `base.html`, współdzielony przez stronę startową i listę meczów. Miejsce (5) wypełniają szablony potomne.

```text
(1) [HD] Handball DataScience
         Administracja danych
(2) [Start | Dane | Import | Kontrola danych | Logi]
+--------------------------------+-------------------------------------------+
| (3) ADMINISTRACJA              | (4) [☰ Menu] na wąskim ekranie             |
| Dane                          |     [komunikaty, jeżeli istnieją]          |
|  Sezony / Rozgrywki / Drużyny  |                                           |
|  Zawodnicy / Składy / Mecze    | (5) BLOK tresc                            |
|  Tabele / Strzelcy / Hale      |     nagłówek konkretnej strony            |
|  Sędziowie                    |     filtry / tabela / pozostała treść     |
| Raporty                       |                                           |
|  Katalog raportów             |                                           |
|  Prognozy meczów              |                                           |
|  Typowania meczów             |                                           |
| Import / eksport              |                                           |
|  Import danych                |                                           |
|  Historia importów            |                                           |
|  Eksport danych               |                                           |
| Narzędzia                     |                                           |
|  Anomalie danych              |                                           |
|  Walidacja danych             |                                           |
|  Logi aplikacji               |                                           |
+--------------------------------+-------------------------------------------+
(6) Handball DataScience                               Flask + PostgreSQL
```

Pozycje w grupach sidebara są osobnymi wierszami z ikonami; ukośniki powyżej skracają rysunek. Obecnie działa tylko „Mecze” w sidebarze oraz „Start” i „Dane” w menu górnym. Pozostałe pozycje mają `href="#"`. Zmienna `sekcja_aktywna` steruje wyróżnieniem.

**Wąski ekran:** do 920 px `.layout` ma jedną kolumnę, a `.sidebar` jest początkowo ukryty. „☰ Menu” przełącza jego widoczność. Pokazany sidebar znajduje się przed `<main>`, nie jest wysuwanym panelem nakładanym na treść. Górne menu może przewijać się poziomo. Do 700 px stopka ma układ blokowy.

Blok `tytul` określa tytuł karty przeglądarki, nie widoczny nagłówek strony. CSS jest podłączony w `<head>`, a JS na końcu `<body>`.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Marka i podpis | [base.html](base.html) | `.header`, `.header-inner`, `.brand` i `.brand-badge`. |
| 2. Górne menu | [navigation.md](partials/navigation.md) | Fragment `partials/navigation.html`; lista pozycji pochodzi z `GORNY_PASEK`. |
| 3. Etykiety, ikony i kolejność menu | [navigation.py](../navigation.py) | `SIDEBAR`, `GORNY_PASEK`, `PozycjaMenu` i docelowe endpointy. |
| 3. Znaczniki grup i pozycji | [base.html](base.html) | `aside.sidebar`, `.sidegroup` oraz pętle po `sidebar`. |
| 4. Komunikaty | [messages.md](partials/messages.md) | Fragment znajduje się przed blokiem treści i nie powstaje przy pustej liście komunikatów. |
| 4. Przełączanie menu | [admin.js](../static/js/admin.js) | `[data-mobile-menu]` i `.sidebar`; JS ustawia styl `display`. |
| 5. Zawartość konkretnej strony | [base.html](base.html) | Punkt rozszerzenia `{% block tresc %}`; samą zawartość zmieniaj w szablonie potomnym. |
| 6. Stopka i podłączenie zasobów | [base.html](base.html) | `.footer`, odwołania `url_for("static", ...)` do CSS/JS. |
| Kolumny, kolory, szerokości, progi ekranu | [admin.css](../static/css/admin.css) | `.layout`, `.sidebar`, `.content`, `.mobile-menu`, `.header`, `.footer` i `@media`. |
