# Szczegóły prognozy meczu

Status: zaimplementowany szablon [detail.html](detail.html).

## Przeznaczenie i routing

`GET /administracja/raporty/prognozy-meczow/<id_mecz>` (endpoint `administracja.szczegoly_prognozy_meczu`, opcjonalny parametr `model`, domyślnie `team_strength_v1`) jest pełną stroną analityczną z własnym adresem, nie modalem. Odpowiada na dwa pytania: jak działa algorytm i jak dokładnie policzył ten konkretny mecz. Łączy dokumentację matematyczną, wyjaśnienie modelu i audyt pojedynczej prognozy.

Przepływ: `PrognozaMeczuSzczegolyView` → `SzczegolyPrognozyService` → `BacktestPrognozService` → `PrognozaMeczuPresenter.przygotuj_szczegoly()` → szablon. Mecz spoza backtestu (inna liga, wycofany, walkower, bez wyniku lub daty) daje 404, nieznany model 400, a niedostępna baza 503. Strona działa też dla meczów z okresu rozgrzewki i wtedy oznacza, że nie wchodzą one do metryk.

## Zasada wartości historycznych

Wszystkie liczby pochodzą z `PrognozaMeczu`, czyli ze snapshotu stanu modelu utworzonego w chwili prognozy tego meczu. Snapshot obejmuje ratingi przed meczem, informację o nowej drużynie lub regresji, EWMA przed meczem i jej ostatnie aktualizacje, prognozę, ocenę, aktualizację ratingów i zamrożone parametry `KonfiguracjaSilyDruzyn` z `model_version`. Presenter nie liczy ich na nowo z dzisiejszego stanu. Wyjątkiem jest wartość `tanh(...)` pokazana w podstawieniu kroku 8, dopisana jako pośredni wynik tego samego wzoru. Backtest jest chronologiczny, więc późniejsze mecze nie zmieniają snapshotu wcześniejszego meczu (test `test_backtest_sortuje_chronologicznie_i_nie_przecieka_z_przyszlosci`). Ograniczenie: snapshot nie jest trwale zapisany w bazie. Zmiana historycznych danych źródłowych przez import zmieni wynik backtestu. Zmiana parametrów wymaga nowej `wersja_modelu`.

## Dane

`szczegoly: SzczegolyPrognozyViewModel`: nagłówek, kontekst (pełna nazwa ligi, np. „I Liga kobiet”, sezon, kolejka, data), opcjonalna informacja o `zamiana`, okres (raport/rozgrzewka), `wynik_prognozy`, `bledy`, `dane_wejsciowe`, `uwagi_ratingow` (nowa drużyna, regresja sezonowa), `ostatnie_ewma`, osiem `kroki` (`KrokObliczeniaViewModel`: kotwica, tytuł, definicja, wzór, podstawienie, wynik, interpretacja), `znaczenie_aktualizacji`, `ratingi`, `historia` (10 poprzednich meczów każdej drużyny, od najnowszego), `parametry` (JSON snapshotu) i `definicje`. Dodatkowo `parametry_powrotu` — parametry zapytania przekazane z raportu, używane przez przycisk „Powrót do raportu” — oraz `sezony_raportu` (wartość z `ZakresRaportuForm`, domyślnie `10`), która decyduje, czy mecz jest w zakresie raportu czy w rozgrzewce, i jest przekazywana w linkach historii. Błędna wartość daje 400.

## Weryfikacja

`tests/interface/test_match_predictions.py::test_szczegoly_prognozy_pokazuja_kroki_wzory_i_podstawienia` i `test_szczegoly_meczu_z_rozgrzewki_i_bledy`. Wygląd sprawdzono 2026-09-24 w Edge (headless) na meczu #206654. Na szerokości telefonu kroki układają się w jednej kolumnie; zrzut headless nie odwzorował wiernie szerokości poniżej ok. 500 px.

## Układ tekstowy i mapa zmian

```text
[rama base.html: „Raporty” aktywne w górnym pasku, „Prognozy meczów” w sidebarze]
(1) Start › Raporty › Prognozy meczów › Szczegóły prognozy meczu
    SZCZEGÓŁY PROGNOZY MECZU           [← Powrót do raportu] [Szczegóły meczu]
    Gospodarz — Gość · Superliga kobiet · 2026/2027 · kolejka 3 · data
(2) Wynik prognozy
    Gospodarz — Gość
    [Prognoza 30:26][Rzeczywisty wynik][Typ modelu][Rzeczywisty typ][Trafiony][Ocena wyniku][Typ prognozy]
    [score_error][margin_error][total_error][Ocena]
    okres raportu/rozgrzewki · (notice o zamiana = true)
(3) Spis treści (13 kotwic)
(4) Dane wejściowe przed meczem: parametr → wartość; uwagi o nowej drużynie/regresji
(5) Krok 1…8 (każdy panel):
    Definicja.
    [Wzór]                    [Podstawienie wartości]
    WYNIK OBLICZENIA  rating_diff = +133.39
    Interpretacja.
    (krok 3: lista ostatnich aktualizacji EWMA)
(6) Co oznacza aktualizacja? — 4 zdania
(7) Stan ratingów przed i po: Drużyna | Rating przed | Zmiana | Rating po
(8) Historia ratingu: [tabela gospodarza] [tabela gościa]
    Data | Rywal (link do prognozy) | Miejsce | Wynik | Przed | Zmiana | Po
(9) Parametry modelu użyte w obliczeniu (JSON)
(10) Definicje modelu: pojęcie → opis
```

| Element | Plik | Blok / selektor / metoda |
| --- | --- | --- |
| 1. Nagłówek, kontekst, powrót | [detail.html](detail.html), [match_prediction_presenter.py](../../../../presenters/match_prediction_presenter.py) | `.prediction-head`, `przygotuj_szczegoly()` |
| 2. Wynik i błędy | presenter | `wynik_prognozy`, `bledy`, `.prediction-outcome`, `.kpi-hit`, `.kpi-miss` |
| 3. Spis treści | [detail.html](detail.html) | `nav.prediction-toc`, `krok.kotwica` |
| 4. Dane wejściowe | presenter | `_dane_wejsciowe()`, `_uwaga_ratingu()`, `.prediction-inputs` |
| 5. Treść kroków | presenter | `_kroki()` — wzory, podstawienia, interpretacje |
| 5. Obliczenia modelu | [team_strength_model.py](../../../../../domain/team_strength_model.py) | `RownaniaSilyDruzyn`, `ModelSilyDruzyn` |
| 5. Błędy i klasa | [match_predictions.py](../../../../../domain/match_predictions.py) | `OcenaPrognozyPolicy`, `ProgiTrafnosci`, `ProgiWyniku` (krok 7 pokazuje też różnicę wyniku prezentowanego i ocenę wyniku) |
| 5. Wygląd kroków | [admin.css](../../../../static/css/admin.css) | `.prediction-step-grid`, `.prediction-result`, `.prediction-interpretation`, wspólne `.defense-formula` |
| 6. Znaczenie aktualizacji | presenter | `_znaczenie()` |
| 7. Tabela ratingów | presenter | `_wiersz_ratingu()`, `.zmiana-plus`, `.zmiana-minus` |
| 8. Historia | serwis, presenter | `SzczegolyPrognozyService._historia()`, `DLUGOSC_HISTORII`, `_historia()` |
| 9. Parametry | domena | `KonfiguracjaSilyDruzyn.jako_slownik()` |
| 10. Definicje | presenter | `DEFINICJE_MODELU` |
