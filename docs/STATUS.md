# Stan projektu

Aktualizacja: 2026-09-14.

Poniższe opisy etapów zachowują wyniki wcześniejszych weryfikacji. Wynik migracji nazw z 2026-09-14 podano osobno; nie ponawiano historycznych kontroli na bazie użytkownika.

## Import i prezentacja meczów — 2026-09-19

Dodano tryb uzupełniający: wybiera z bazy mecze sezonu 2026/2027 sprzed dzisiejszego dnia z brakującym wynikiem lub składem jednej strony, pomija walkowery i wycofane spotkania, pobiera tylko szczegóły i uzupełnia brakujące wartości. Pełny import pozostaje dostępny do odkrywania spotkań i korekt. Opis ograniczeń, przepływu i zapisu: [IMPORTS](IMPORTS.md). Klient API zachowuje trzysekundowy odstęp między żądaniami w jednym procesie. Lista meczów uwzględnia `zamiana`, odwracając drużyny wraz z wynikiem. Zmiany nie obejmują uruchomienia rzeczywistego importu ani modyfikacji bazy przez AI. Weryfikacja: 85 testów bez integracji z bazą przechodzi, z wyłączonym hasłem importu w środowisku procesu testów; mypy oraz Ruff dla kodu i testów jednostkowych/widoków przechodzą. Zapytania wyboru kandydatów nie uruchamiano na rzeczywistym PostgreSQL.

## Runda i kolejka na liście meczów — 2026-09-19

Dodano filtry po nazwie rundy i kolejki oraz dwie opcjonalne kolumny włączane osobno w modalu „Widoczne kolumny”. Kolumny są domyślnie ukryte; wybór zapamiętuje przeglądarka. Filtry są stale dostępne. Kontrakt, zachowanie i aktualny spis elementów: [list.md](../src/handball/interface/templates/admin/matches/list.md).

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

- Przyjęto [konwencję nazewnictwa z 2026-09-14](CODING_STANDARDS.md#język-i-nazewnictwo): angielskie pliki, katalogi, moduły i pakiety; polska domena, metody i zmienne bez znaków diakrytycznych; angielskie role klas, np. MeczService i MeczRepository. Udokumentowano niezależność domeny od języka przyszłej bazy. Konwencję wdrożono w istniejącym kodzie: pakiet `handball`, angielskie katalogi i pliki, klasy z rolami technicznymi, importy, konfiguracja narzędzi, `run.bat`, szablony i ich opisy. Odświeżono lokalną instalację pakietu. Weryfikacja migracji: 37 testów jednostkowych i widoków przechodzi, w tym kontrola CSS i JS; Ruff i mypy bez błędów. Wszystkie moduły i 6 szablonów HTML załadowano przy zablokowanym dostępie do bazy; sprawdzono 151 lokalnych odnośników. Testów bazy nie uruchamiano.

- Wskazano prototyp administracji v6 jako wzorzec wyglądu; potwierdzono dostępność katalogu i przeczytano jego README.
- Zapisano [kolejność realizacji](IMPLEMENTATION_PLAN.md) z kryteriami ukończenia etapów.

- Przygotowano [projekt katalogów](DIRECTORY_STRUCTURE.md) i [UML](UML.md): diagramy klas, kompozycji oraz sekwencji listy meczów.
- Utworzono 11 [opisów szablonów](TEMPLATES.md) w docelowym katalogu szablonów. Istnieją katalogi i pliki MD, bez HTML.

- Ukończono etap 1 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): obiektowy szkielet Flaska. Utworzono `pyproject.toml`, `uv.lock`, `.python-version` i `.gitignore`; `uv sync` instaluje Flask 3.1.3 zgodnie z TECH_STACK.
- Utworzono klasy `Ustawienia`, `AplikacjaFactory`, `WidokiRegistrar`, Blueprint `admin` z `StartView` oraz adapter `create_app()` w `src/handball/`.
- Skonfigurowano Ruff, mypy (strict) i pytest w `pyproject.toml`. Wykonano i potwierdzono: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` (bez błędów, 8 plików źródłowych) oraz `uv run pytest` (6 testów, wszystkie przechodzą).
- Zweryfikowano lokalne uruchomienie: `create_app()` rejestruje trasy `/administracja/` i `/static/...`, żądanie GET zwraca 200; start nie łączy się z bazą `zprp`.

- Ukończono etap 2 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): wspólny układ administracji na podstawie prototypu v6. Utworzono `base.html`, `partials/navigation.html`, `partials/messages.html`, `admin/start.html`, `static/css/admin.css` i `static/js/admin.js` (adaptacja `index.html`/`assets/style.css`/`assets/app.js` prototypu). Na wyraźne polecenie użytkownika strona startowa odwzorowuje pełną strukturę index.html (nagłówek, filtry, tabela z nagłówkami kolumn), nie tylko okrojony komunikat tekstowy — tabela ma jeden wiersz z jawną informacją o braku danych zamiast fikcyjnych wierszy z prototypu, a filtry nie są jeszcze podłączone do żadnej logiki.
- Układ zawiera sidebar (`aside.sidebar`, dwukolumnowa siatka jak w prototypie) z jedną realną pozycją "Start" — zamiast pełnego menu prototypu z pozycjami bez odpowiadających widoków. Rozwijanie sidebara na wąskim ekranie (przycisk "☰ Menu") obsługuje `static/js/admin.js`.
- `AplikacjaFactory` jawnie konfiguruje `template_folder`/`static_folder`/`static_url_path` (`templates`/`static`), zgodnie z ARCHITECTURE i DIRECTORY_STRUCTURE. `StartView` renderuje `admin/start.html` zamiast zwracać czysty tekst.
- Zaktualizowano MD czterech zaimplementowanych szablonów (baza, nawigacja, komunikaty, start) zgodnie z rzeczywistym kontraktem, blokami i selektorami.
- Sprawdzono wizualnie w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px, w tym bezpośrednie porównanie zrzutu z prototypem v6 i test kliknięcia "☰ Menu": układ zgodny z v6, responsywność działa, brak przewijania poziomego.

- Ukończono etap 3 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): warstwa danych do odczytu meczów. Dodano zależności SQLAlchemy 2.0.52, Flask-SQLAlchemy 3.1.1, psycopg 3.2.13 (`uv add`).
- Modele ORM (schemat `public`, bez `relationship()`, złączenia jawne w repozytorium): `Sezon`, `Rozgrywki`, `Runda`, `Kolejka` (infrastructure/database/models/competitions.py), `Zespol`, `ZespolSezon` (teams.py), `Mecz` (matches.py, pola potrzebne liście; rozszerzenie o wynik szczegółowy w etapie 5) — kolumny i klucze odwzorowane z [PUBLIC_SCHEMA](database/PUBLIC_SCHEMA.md).
- Obiekty domenowe `FiltryMeczow`, `PozycjaListyMeczow`, `StronaMeczow` (domain/matches.py, z walidacją strony/rozmiaru/sortowania) oraz błędy `NieZnalezionoMeczu`, `BladOdczytuDanych` (domain/errors.py).
- Kontrakt `MeczReadRepository` (contracts/match_repository.py) — na razie tylko `pobierz_liste`; `pobierz_szczegoly` dochodzi w etapie 5 zgodnie z UML.
- `MeczSQLAlchemyRepository.pobierz_liste` (infrastructure/repositories/match_repository.py): filtruje po sezonie/rozgrywkach/rundzie/kolejce, łączy `zespoly_sezony` (migawka sezonowa, nie `zespoly.nazwa` — zgodnie z DATA.md) osobnym aliasem dla gospodarza i gościa, LEFT JOIN dla nieustalonych uczestników, stabilne sortowanie po dacie i id, paginacja z limitem i osobnym zapytaniem o liczbę wszystkich, jawne rozróżnienie braku wyniku od 0:0.
- `PolaczenieConfigurator.skonfiguruj_odczyt` wymusza `execution_options={"postgresql_readonly": True}` na silniku SQLAlchemy (READ ONLY dla każdej transakcji, także po ponownym użyciu połączenia z puli). `extensions.py` inicjalizuje Flask-SQLAlchemy (`baza_danych`) powiązaną z `Baza(DeclarativeBase)`. `AplikacjaFactory` wpina oba elementy; start aplikacji nie łączy się z bazą (silnik SQLAlchemy jest leniwy).
- `Ustawienia` rozszerzone o `host_bazy`/`port_bazy`/`nazwa_bazy`/`uzytkownik_bazy`/`haslo_bazy` i właściwość `adres_bazy_danych`. Utworzono `.env.example` bez sekretów.
- Weryfikacja etapu 3: `ruff check`, `ruff format --check`, `mypy` — bez błędów.

- Ukończono etap 4 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): działająca lista meczów. `MeczService` (services/match_service.py, cienka delegacja do repozytorium — celowo, bez przedwczesnej logiki), `ZaleznosciZadaniaFactory` (request_dependencies.py, tworzy repozytorium+serwis per żądanie, wstrzykiwalna w testach), `MeczListView` i `MeczFilterForm` (WTForms, waliduje `id_sezon` jako wymagane, resztę jako opcjonalne).
- `interface/errors.py`: `obsluz_blad_domeny` mapuje `NieZnalezionoMeczu`→404, `BladOdczytuDanych`→503 (na razie domyślne strony Flaska; własny wygląd `errors/*.html` pozostaje do zrobienia). `MeczSQLAlchemyRepository` tłumaczy `SQLAlchemyError` na `BladOdczytuDanych`.
- Trasa `GET /administracja/mecze` (endpoint `administracja.lista_meczow`) zwraca 400 przy braku `id_sezon`, w przeciwnym razie renderuje `admin/matches/list.html` z filtrami (GET, bez CSRF) i paginacją (`partials/pagination.html`, zachowuje wszystkie parametry query przy zmianie strony).
- **Przeprojektowano nawigację na wyraźne polecenie użytkownika**: sidebar i górny pasek pokazują teraz **pełne** menu prototypu v6 (grupy Dane [10 pozycji]/Import-eksport [3]/Narzędzia [3], z ikonami), nie tylko pozycję "Start". Nowy moduł `interface/navigation.py` (`GORNY_PASEK`, `SIDEBAR`, poza pierwotnym planem DIRECTORY_STRUCTURE) wstrzykuje strukturę menu globalnie przez `context_processor`; widoki przekazują tylko `sekcja_aktywna` (string). Pozycje bez widoku mają `punkt_koncowy=None` → renderują się jako `href="#"`, widoczne ale nieaktywne (nie 404).
- `MeczInMemoryRepository` (tests/helpers/match_repository.py) — implementacja testowa kontraktu `MeczReadRepository`, używana w testach serwisu i widoku bez potrzeby bazy. `tests/` stało się pakietem (`__init__.py`), żeby te importy działały.
- **Zweryfikowano wobec prawdziwej bazy `zprp` w tej sesji** (hasło ustawione lokalnie przez użytkownika, nigdzie nie zapisane w dokumentacji ani w historii poleceń pokazywanej użytkownikowi): `uv run pytest tests/integration` — 3/3 przechodzi (lista dla sezonu 195/1817 meczów, pusta lista dla nieistniejącego sezonu, wymuszenie READ ONLY faktycznie blokuje zapis). Ręcznie w przeglądarce: pierwsza i druga strona listy z prawdziwymi meczami i wynikami, pusty wynik dla nieistniejącego sezonu, błąd 400 przy braku `id_sezon`, pełny sidebar z aktywną pozycją "Mecze"/"Dane". Kryterium etapu 3 i 4 "pobranie danych działa z istniejącym schematem" jest w pełni potwierdzone, nie tylko teoretycznie.
- **Uwaga bezpieczeństwa, nie do przeoczenia**: `src/handball/settings.py` ma teraz na dysku domyślną wartość `BAZA_HASLO` wpisaną wprost w kodzie (do wygodnych testów lokalnych). To narusza własną zasadę projektu (sekrety tylko ze środowiska, nigdy w kodzie) i **nie powinno trafić do commita** — użytkownik świadomie zdecydował zostawić to lokalnie, ale wyraźnie zastrzegł, żeby nie commitować tego pliku. Przy każdym `git add`/`git commit` obejmującym `settings.py` należy to przypomnieć.
- Weryfikacja etapu 4: `ruff check`, `ruff format --check`, `mypy` (32 pliki źródłowe) — bez błędów; `pytest`: 23/23 przechodzi (z `BAZA_HASLO` ustawionym lokalnie), 20 przechodzi / 3 pomijane bez niego.

- **Poprawka po zgłoszeniu użytkownika**: kliknięcie "Mecze"/"Dane" w menu dawało 400 (`id_sezon` wymagane), bo linki menu nie przekazują parametrów. Dodano `SezonReadRepository`/`SezonSQLAlchemyRepository` (contracts/season_repository.py, infrastructure/repositories/season_repository.py — poza pierwotnym planem DIRECTORY_STRUCTURE) i `ZaleznosciZadaniaFactory.utworz_repozytorium_sezonow()`. `MeczListView` bez `id_sezon` w query teraz przekierowuje (302) do najnowszego sezonu (`MAX(sezony.id)`) zamiast zwracać błąd; zweryfikowano ręcznie wobec żywej bazy (`id_sezon=195`) i testami (`test_lista_meczow_bez_id_sezon_przekierowuje_do_domyslnego`).
- **Dodano 12 wstępnych notatek MD** dla pozostałych pozycji sidebara bez widoku (Sezony, Rozgrywki, Drużyny, Zawodnicy, Składy, Tabele, Strzelcy, Hale, Sędziowie, Import/eksport [1 notatka dla 3 pozycji], Kontrola danych [1 notatka dla 2 pozycji], Logi) na wyraźne polecenie użytkownika — patrz [TEMPLATES](TEMPLATES.md), sekcja "Wczesne notatki planistyczne". To krótkie punkty startu (źródło w prototypie, przybliżone tabele bazy), nie ustalone kontrakty — większość stron prototypu v6 poza `players.html`/`quality.html` to same placeholdery ("Przykładowa strona administracyjna"), więc nie ma z czego wiernie skopiować układu.

- **Przebudowano filtry listy meczów na wyraźne polecenie użytkownika** (przycisk "Filtruj" był za duży, filtry pokazywały surowe ID zamiast nazw): sezon i rozgrywki to teraz rozwijane listy z nazwami (`OpcjaWyboru`, `SlownikiMeczowService`, contracts/repositories `seasons.py`/`competitions.py`/`venues.py` — wszystkie poza pierwotnym planem DIRECTORY_STRUCTURE); `id_sezon` jest teraz opcjonalny (pusty wybór = wszystkie sezony, usunięto wcześniejsze przekierowanie do najnowszego sezonu). Dodano model `Hala` (`infrastructure/database/models/venues.py`) i kolumnę "Hala" w tabeli i filtrach. Dodano wyszukiwanie po nazwie drużyny (`szukaj_druzyny`, ILIKE na gospodarzu lub gościu) oraz po dacie w formacie częściowym: rok (`2026`), rok-miesiąc (`2026-01`) albo pełna data (`2026-01-15`) — parsuje `zakres_z_czesciowej_daty()` w domain/matches.py, niepoprawny format zwraca czytelny błąd 400. Usunięto filtry `id_runda`/`id_kolejka` (nie były używane w interfejsie, użytkownik ich nie prosił). Poprawiono CSS (`.pole-przycisku`), żeby przycisk "Filtruj" nie rozciągał się na całą kolumnę siatki. Zweryfikowano ręcznie wobec żywej bazy `zprp`: filtr sezonu pokazuje "2026/2027" (nie ID), wyszukiwanie "Kielce" zwraca 169 trafień z poprawnymi nazwami hal, błędny format daty zwraca czytelny komunikat po polsku. `pytest`: 34 przechodzi, 3 integracyjne pomijane bez `BAZA_HASLO`.

- **Druga runda poprawek listy meczów, też na wyraźne polecenie użytkownika**: sortowanie przeniesione z pola w filtrach na klikalny nagłówek kolumny "Data" (rosnąco/malejąco, zachowuje pozostałe filtry, resetuje stronę) — **zapisano to jako trwałą konwencję projektu** w [CODING_STANDARDS](CODING_STANDARDS.md) ("Listy z filtrami") i w skillu `hds-flask-feature`, żeby dotyczyła też przyszłych list. Dodano kolumny Sezon i Rozgrywki (INNER JOIN, pola NOT NULL w `mecze`). Usunięto podpowiedź formatu z pola daty (użytkownik nie chciał podpowiedzi w samym polu). Wyszukiwanie drużyny przeprojektowane: zamiast dopasowania tekstu per wiersz, najpierw rozwiązuje nazwę do `id_zespol` (przez `zespoly_sezony`), potem filtruje mecze po tym stałym identyfikatorze — dzięki temu jedna historyczna nazwa (np. "Industria Kielce") znajduje też mecze z sezonów, gdy zespół nazywał się inaczej (np. "Vive Kielce"). Test integracyjny `test_szukaj_druzyny_znajduje_zespol_we_wszystkich_sezonach` to potwierdza wobec żywych danych — przy okazji ujawnił, że krótkie nazwy historyczne (np. "MKS Zagłębie Lubin") mogą dodatkowo dopasować niepowiązane zespoły (rezerwy/młodzieżowe o podobnej nazwie); test dobiera jednoznaczną nazwę, żeby nie być przypadkowo kruchy, a ograniczenie jest udokumentowane w list.md jako naturalna cecha wyszukiwania tekstowego, nie błąd. `pytest`: 39/39 (z `BAZA_HASLO`).

- **Trzecia runda poprawek: filtr Rozgrywki po nazwie, nie po ID sezonowym.** Użytkownik zauważył, że filtr "Rozgrywki" pokazywał tę samą nazwę (np. "I Liga Mężczyzn Grupa A") osobno dla każdego sezonu, bo w bazie każdy sezon ma własny wiersz `rozgrywki` z tą samą `nazwa`. `FiltryMeczow.id_rozgrywki` (int) zmieniono na `rozgrywki: str | None` (nazwa); `RozgrywkiSQLAlchemyRepository.pobierz_nazwy()` zwraca `DISTINCT` nazwy zamiast pary (id, nazwa); `MeczSQLAlchemyRepository` filtruje przez `Rozgrywki.nazwa == filtry.rozgrywki` na już istniejącym złączeniu (dokładne dopasowanie, bo nazwa pochodzi z zamkniętej listy, nie wolnego tekstu). Efekt: lista rozwijana "Rozgrywki" nie ma ani jednego duplikatu, a wybór nazwy pokazuje mecze ze wszystkich sezonów tej nazwy. Dodano testy integracyjne `test_pobierz_nazwy_rozgrywek_sa_unikalne` i `test_filtr_rozgrywki_po_nazwie_obejmuje_wiele_sezonow` — **zweryfikowane wobec żywej bazy**: "I Liga Kobiet" faktycznie obejmuje 6 sezonów i 750 meczów, dropdown potwierdzony bez duplikatów zliczeniem wystąpień w renderowanym HTML. `pytest`: 41/41 (z `BAZA_HASLO`).

## Jeszcze niewykonane

- Szczegóły meczu (`MeczDetailView`, `matches/detail.html`, model `players.py`, rozszerzenie `Mecz`) — etap 5.
- Podgląd ostatnich meczów bezpośrednio na stronie startowej (obecnie: tylko przycisk do pełnej listy) — świadomie odłożone.
- Dostęp administratora i pozostałe widoki odczytu (etapy 6–7).
- Dodatkowe pozycje sidebara podłączone do realnych widoków (obecnie większość to `href="#"`) — razem z odpowiadającymi im widokami/etapami.
- Kaskadowe odświeżanie listy rozgrywek po zmianie sezonu bez przeładowania strony (obecnie: zwykły GET, bez JS) — możliwe usprawnienie później.
- Własny wygląd stron błędów (`errors/400.html`, `404.html`, `503.html`) — na razie domyślne strony Flaska.
- Pozostałe szablony (logowanie) — ma MD, brak HTML.
- Eksport i publiczny serwis.

## Następny krok

Etap 5 z [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): szczegóły meczu — rozszerzenie modelu `Mecz`, model `players.py`/`sklady`, `pobierz_szczegoly` w kontrakcie i repozytorium, `MeczDetailView`, adaptacja `match_detail.html` prototypu. Przed tym warto ustalić interpretację wariantów wyniku i `zamiana` (patrz DATA.md) — obecnie nie są jeszcze rozstrzygnięte.

Nie używać `python ../run.py` jako komendy uruchomienia nowej aplikacji: dotyczy starszego serwisu i jego procesu importu.
