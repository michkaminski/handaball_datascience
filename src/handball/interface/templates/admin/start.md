# Strona startowa administracji — Aktualności

Status: zaimplementowane (2026-09-23). Szablon `admin/start.html`, trasa `GET /administracja/`, endpoint `administracja.start`. Widok tylko do odczytu. Na wyraźne zlecenie użytkownika Start zastąpił dotychczasową makietę listy meczów z prototypu (niepodłączone filtry i pustą tabelę) stroną aktualności w stylu klasycznego portalu sportowego: ostatnie mecze, ciekawostki i najlepsi strzelcy bieżącego sezonu, z naciskiem na Superligę M i K oraz Ligi Centralne.

## Przeznaczenie i dane

Bieżący sezon to sezon z najwyższym `sezony.rok_rozpoczecia`, w którym jest choć jeden rozegrany mecz (oba wyniki `*_full`, bez wycofania i walkowera). Jeżeli takiego sezonu nie ma, strona pokazuje tylko nagłówek z komunikatem „Brak rozegranych meczów w bazie.”.

Ligi priorytetowe rozpoznaje `KategoriaRozgrywekPolicy` po nazwie i płci rozgrywek bieżącego sezonu, a nie po zakodowanych identyfikatorach (zgodnie z [dokumentacją bazy](../../../../../docs/database/README.md), która ostrzega przed utrwalaniem ID): nazwa zawierająca „superliga” (ale nie „superpuchar”) to Superliga, „liga centralna” to Liga Centralna; płeć pochodzi z `rozgrywki.plec`, a przy jej braku z nazwy („kobiet”). Kolejność sekcji: Superliga mężczyzn, Superliga kobiet, Liga Centralna mężczyzn, Liga Centralna kobiet. Pozostałe rozgrywki sezonu trafiają do wspólnej tabeli.

- **Ostatnie mecze** — w każdej sekcji priorytetowej 6 najnowszych rozegranych meczów, liczba rozegranych i średnia bramek na mecz; w „Pozostałych rozgrywkach” 12 najnowszych wyników z nazwą rozgrywek. Strony i wynik uwzględniają `mecze.zamiana` przez `MeczPolicy`, jak lista meczów. Zwycięzca jest pogrubiony, wynik prowadzi do karty meczu, a „wszystkie mecze »” do listy meczów przefiltrowanej po sezonie (i rozgrywkach).
- **Ciekawostki sezonu** — liczone w `AktualnosciService` z rozegranych meczów i protokołów: sezon w liczbach (bramki, mecze, średnia), mecz z największą liczbą bramek, najwyższe zwycięstwo (różnica), najlepszy występ indywidualny (najwięcej bramek zawodnika w jednym meczu) oraz najbardziej bramkostrzelna liga priorytetowa. Odmiana „bramka/bramki/bramek” jest poprawna gramatycznie.
- **Najlepsi strzelcy** — 5 najlepszych w każdej lidze priorytetowej. Tabela `public.strzelcy` (oficjalna klasyfikacja ze źródła) jest dla bieżącego sezonu nieaktualna (stan po pierwszej kolejce) i nie obejmuje Lig Centralnych, dlatego strzelcy są sumą bramek z `mecze_zawodnicy` w danych rozgrywkach (M = liczba meczów z wpisaną liczbą bramek, Śr. = bramki / M). Drużyna to drużyna z najnowszego meczu zawodnika w tych rozgrywkach. Strona mówi o tym wprost pod tabelami.

Strona wykonuje pięć zapytań tylko do odczytu (bieżący sezon, rozgrywki, rozegrane mecze, strzelcy z funkcją okna `row_number`, najlepsze występy); wszystkie statystyki i wybory rekordów liczy Python.

## Kontrakt i powiązania

- `aktualnosci`: `AktualnosciViewModel` — `sezon`, `id_sezon`, `stan_danych` (data ostatniego wyniku), `liczba_rozegranych`, `suma_bramek`, `srednia_bramek`, `sekcje` (`SekcjaAktualnosciViewModel`: `klucz` kategorii, `etykieta`, `rozgrywki`, `liczba_rozegranych`, `srednia_bramek`, `mecze`, `strzelcy`), `pozostale_mecze`, `ciekawostki` (`CiekawostkaViewModel`: `tytul`, `wartosc`, `opis`, opcjonalnie `id_mecz`, `id_zawodnik`).
- `sekcja_aktywna="start"`.
- Warstwy: `StartView` → `AktualnosciService` (+ `KategoriaRozgrywekPolicy`) → kontrakt `AktualnosciReadRepository` → `AktualnosciSQLAlchemyRepository`; formatowanie w `AktualnosciPresenter`. Zależności składa `ZaleznosciZadaniaFactory` (`fabryka_aktualnosci`, `utworz_serwis_aktualnosci()`, `utworz_presenter_aktualnosci()`).
- Błąd odczytu bazy daje 503 (`obsluz_blad_domeny`). Nazwy z bazy są escapowane przez Jinja2, a nadmiarowe spacje w nazwach drużyn i zawodników są usuwane w presenterze.

Tabele mają ukryty dla oka nagłówek i podpis (`.sr-only`), więc czytniki ekranu dostają kolumny Data / Gospodarz / Wynik / Gość. Szerokości kolumn ustala `<colgroup>` (`table-layout: fixed`); w ramkach lig nazwy drużyn zawijają się do dwóch linii, w tabeli pozostałych rozgrywek są skracane wielokropkiem z pełną nazwą w `title`.

## Weryfikacja

Testy: `tests/unit/test_news_service.py` (klasyfikacja lig, kolejność sekcji, limity, średnie, rekordy, strzelcy w sekcjach, brak sezonu), `tests/unit/test_news_presenter.py` (zamiana stron, zwycięzca, remis, odmiana, linki, puste pola), `tests/unit/test_news_repository.py` (mapowanie wierszy, błąd bazy) i `tests/interface/test_start.py` (render, linki, escapowanie, brak danych, 503, zasoby statyczne). Na rzeczywistej bazie (sezon 2026/2027, 123 rozegrane mecze) sprawdzono stronę w Edge przy 1440 px i w ramce 390 px.

## Układ tekstowy i mapa zmian

```text
[wspólny nagłówek] -> [górne menu: Start aktywne]
+------------------+----------------------------------------------------------------+
| wspólny sidebar  | (1) Start › Aktualności                                        |
|                  |     AKTUALNOŚCI (szeryfowy tytuł)                              |
|                  |     Sezon 2026/2027 · ostatni wynik · rozegrane mecze · bramki |
|                  | +-------------------------------------+ +--------------------+ |
|                  | | (2) Ostatnie mecze (podwójna linia) | | (5) CIEKAWOSTKI    | |
|                  | | +-----------------+ +--------------+ | |  Sezon w liczbach  | |
|                  | | |SUPERLIGA MĘŻCZ. | |SUPERLIGA KOB.| | |  Najwięcej bramek  | |
|                  | | |20.09 A [37:24] B| |16.09 C [28:29]| | |  Najwyższe zwycięs.| |
|                  | | |... 6 wyników    | |...           | | |  Najlepszy występ  | |
|                  | | |Rozegrane · śr.  | |wszystkie »   | | |  Najbardziej bramk.| |
|                  | | +-----------------+ +--------------+ | +--------------------+ |
|                  | | |LIGA CENTR. M.   | |LIGA CENTR. K.| | | (6) NAJLEPSI       | |
|                  | | +-----------------+ +--------------+ | |     STRZELCY       | |
|                  | | (3) POZOSTAŁE ROZGRYWKI             | |  Superliga M: 1-5  | |
|                  | |  data | rozgrywki | A [wynik] B      | |  Superliga K: 1-5  | |
|                  | |  ... 12 wyników · wszystkie mecze » | |  LC M, LC K: 1-5   | |
|                  | +-------------------------------------+ |  (4) źródło danych | |
|                  |                                         +--------------------+ |
+------------------+----------------------------------------------------------------+
[wspólna stopka]
```

Poniżej 1100 px kolumna boczna przechodzi pod główną, a poniżej 760 px ramki lig układają się jedna pod drugą i znika kolumna rozgrywek w tabeli pozostałych meczów. Ramki kobiece mają bordowy pasek nagłówka, męskie granatowy; Ligi Centralne mają jaśniejsze podkreślenie paska.

### Mapa zmian

| Element | Plik | Blok / selektor / dane |
| --- | --- | --- |
| 1. Nagłówek i linia stanu | [start.html](start.html) | `.news-head`, `.news-dateline`, `aktualnosci.sezon`, `stan_danych`, `liczba_rozegranych`, `suma_bramek`. |
| 2. Ramki lig priorytetowych | [start.html](start.html), [admin.css](../../static/css/admin.css) | makro `wiersz_meczu`, `.news-boxes`, `.news-box.news-{klucz}`, `.news-results`, `.news-col-*`, `aktualnosci.sekcje`. |
| 3. Pozostałe rozgrywki | [start.html](start.html) | `.news-other`, `wiersz_meczu(mecz, true)`, `aktualnosci.pozostale_mecze`. |
| 4. Źródło strzelców | [start.html](start.html) | `.news-source`; zmiana źródła wymaga zmiany `pobierz_strzelcow()`. |
| 5. Ciekawostki | [news_presenter.py](../../presenters/news_presenter.py), [news_service.py](../../../services/news_service.py) | `_ciekawostki()`, `_rekord()`, `_wystep()`; rekordy i średnie liczy serwis. |
| 6. Najlepsi strzelcy | [news_repository.py](../../../infrastructure/repositories/news_repository.py) | `pobierz_strzelcow()` (agregacja `mecze_zawodnicy`, `row_number` w rozgrywkach), `.news-scorer-table`. |
| Rozpoznawanie lig | [news_service.py](../../../services/news_service.py) | `KategoriaRozgrywekPolicy.kategoria()`, `KategoriaRozgrywek` w [domain/news.py](../../../domain/news.py). |
| Liczby w sekcjach | [news_service.py](../../../services/news_service.py) | `LICZBA_MECZOW_W_SEKCJI`, `LICZBA_STRZELCOW_W_SEKCJI`, `LICZBA_POZOSTALYCH_MECZOW`, `LICZBA_NAJLEPSZYCH_WYSTEPOW`. |
| Widok i zależności | [start.py](../../admin/views/start.py), [request_dependencies.py](../../../request_dependencies.py) | `StartView.get()`, `fabryka_aktualnosci`. |
| Styl „klasycznego portalu” | [admin.css](../../static/css/admin.css) | `.news-*`, `.sr-only`, zapytania `@media` 1100 i 760 px. |
