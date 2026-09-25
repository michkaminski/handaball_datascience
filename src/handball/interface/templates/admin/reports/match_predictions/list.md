# Prognozy meczów — siła drużyn (raport)

Status: zaimplementowany szablon [list.html](list.html).

## Przeznaczenie i routing

`GET /administracja/raporty/prognozy-meczow` (endpoint `administracja.raport_prognoz_meczow`) pokazuje historyczny backtest modelu Dynamic Team Strength V1 dla Superligi, Ligi Centralnej i I Ligi mężczyzn i kobiet. Każda liga (poziom × płeć) ma osobny model. Główne pytanie raportu: jak dobrze da się przewidywać kolejne mecze wyłącznie na podstawie historycznej, dynamicznej siły drużyn.

Przepływ: `PrognozyMeczowListView` → `PrognozyMeczowFilterForm` → `RaportPrognozService` → `BacktestPrognozService` → `MeczeLigoweReadRepository` → `PrognozaMeczuPresenter` → szablon. Backtest jest liczony w pamięci przy każdym żądaniu (ok. 1,1 s dla trzech poziomów na bazie z 2026-09-25). Nie zapisuje niczego w bazie. Model i definicje miar: [ARCHITECTURE](../../../../../../../docs/ARCHITECTURE.md#raport-prognoz-meczów--2026-09-24) i [DATA](../../../../../../../docs/DATA.md#ligi-w-raportach-prognoz--2026-09-25).

Błędne parametry (nieznany poziom rozgrywek lub płeć, ocena, rozmiar, model, liczba sezonów raportu, sezon spoza zakresu raportu, `strona=0`) dają 400, a niedostępna baza 503.

## Dane i zachowanie

| Zmienna | Typ | Opis |
| --- | --- | --- |
| `raport` | `RaportPrognozViewModel` | Model, zakresy sezonów, wskaźniki, progi, strona tabeli, parametry i wykluczenia |
| `strona` | `StronaPrognozViewModel` | To samo co `raport.strona`; kontrakt partiala paginacji |
| `formularz` | `PrognozyMeczowFilterForm` | Model, rozgrywki (`poziom`: `superliga`, `liga_centralna`, `i_liga`), płeć (`plec`: `M`, `K`), sezon, liczba sezonów raportu (`sezony_raportu`: 3, 5, 10, 15, `wszystkie`; pole z `ZakresRaportuForm`), drużyna, Trafiony (TAK/NIE), liczba wierszy oraz checkboxy: Typ prognozy (`typ_prognozy`: poprawny/nieprzewidziany; oba albo żaden = wszystkie), Wynik 1X2 (`wynik_1x2`: H/X/A, wiele wartości), „Dokładny wynik”, „Poprawna różnica bramek”, oceny wyniku (`ocena_wyniku`, wiele wartości) i oceny score error (`ocena`, wiele wartości) |
| `filtry` | `FiltryPrognoz` | Zwalidowane filtry |
| `parametry` | `dict[str, list[str]]` | Bieżące parametry zapytania (`to_dict(flat=False)`, z powtórzeniami checkboxów). Trafiają do adresu szczegółów i jako `parametry_paginacji` do paginacji, więc zaznaczone checkboxy są zachowane |
| `sekcja_aktywna` / `sekcja_glowna` | `"prognozy_meczow"` / `"raporty"` | Aktywne pozycje sidebara i górnego paska |

- Tabela obejmuje tylko mecze z zakresu raportu, od najnowszych: ostatnie pełne sezony (liczba z filtra „Sezonów w raporcie”, domyślnie 10) i rozegrane mecze sezonu w toku. Starsze sezony są rozgrzewką; zawsze zostaje co najmniej jeden sezon rozgrzewki, więc „Wszystkie” oznacza wszystkie pełne sezony poza najstarszym. Wybór zmienia tylko zakres metryk i tabeli, a nie prognozy, bo model zawsze przechodzi całą historię. Sezon wybrany w filtrze „Sezon” musi mieścić się w zakresie, inaczej strona zwraca 400.
- **Ocena wyniku** porównuje zaokrągloną prognozę (kolumna Prognoza) z wynikiem (kolumna Wynik): Dokładny wynik, Dokładna różnica (np. 29:30 przy 30:31), Różnica ±1, ±2–3, ±4 i więcej. Liczy się różnica bramek wyniku prezentowanego, a nie `predicted_margin`. Progi są w `ProgiWyniku`. Dymek komórki pokazuje obie różnice.
- **Typ prognozy** to typ 1X2 odczytany z zaokrąglonego wyniku prognozy, porównany z wynikiem, np. „✕ H · Nieprzewidziany”. 38:20 przy wyniku 20:38 jest nieprzewidziany (`OcenaPrognozy.typ_prezentowany`, `poprawny_typ_prognozy`). Różni się od **Typu modelu** (dawniej „Typ”) i kolumny **Trafiony**, które stosują próg `DRAW_MARGIN_THRESHOLD` do dokładnej różnicy. Przy prognozie 29:28 z różnicą 0,6 typ modelu to X, a typ prognozy H. Na bazie jest 24 takich meczów z typem modelu trafionym, a typem prognozy nieprzewidzianym.
- Kolumna Liga pokazuje skrót poziomu i płeć: `SL`, `LC`, `1L` oraz `M`/`K`, np. „1L K”. Pełna nazwa ligi jest w nagłówku szczegółów.
- Filtr Wynik 1X2 zawęża do rzeczywistego wyniku H, X lub A.
- Checkboxy „Dokładny wynik” i „Poprawna różnica bramek” zawężają listę (dokładny wynik zawiera się w poprawnej różnicy). Zaznaczenia w jednej grupie ocen łączy OR, a różne filtry łączy AND. Brak zaznaczeń w grupie oznacza wszystkie.
- Podsumowanie zawiera też liczbę i odsetek dokładnych wyników, dokładnych różnic i różnic ±1 lub lepiej.
- Podsumowanie i progi `score_error ≤ 2/4/6` liczone są dla wszystkich meczów spełniających filtry, nie tylko dla bieżącej strony.
- Kolumny zawierają wartości z zapisanego stanu modelu sprzed meczu: ratingi, różnicę z home advantage, dokładne prognozy bramek, różnicy i sumy. Obok są wyniki rzeczywiste, błędy bezwzględne, typy 1X2, trafienie, score error i klasa trafności.
- Kliknięcie wiersza (`tr[data-href]`) otwiera stronę szczegółów prognozy. Ctrl+klik i środkowy przycisk otwierają nową kartę, a Enter działa na wierszu z fokusem. Link w kolumnie Gospodarz działa także bez JavaScriptu.
- Brak wyników pokazuje wiersz „Brak prognoz spełniających wybrane filtry”.
- Tabela ma ograniczoną wysokość (`.prediction-table-wrap`), dzięki czemu nagłówek pozostaje przyklejony przy przewijaniu. Wiersze mają ok. 30 px.

## Weryfikacja

`tests/interface/test_match_predictions.py`: tabela, podsumowanie, nawigacja, filtry, 400, 405 i 503. JavaScript: `tests/javascript/match_predictions.test.cjs`. Logika: `tests/unit/test_match_prediction_service.py` i `tests/unit/test_team_strength_model.py`. Wygląd sprawdzono 2026-09-24 w Edge (headless) na rzeczywistej bazie, w trybie tylko do odczytu.

## Układ tekstowy i mapa zmian

```text
[rama base.html: górny pasek „Raporty” aktywny, sidebar „Prognozy meczów” aktywny]
(1) Start › Raporty › Prognozy meczów
    PROGNOZY MECZÓW — SIŁA DRUŻYN
    opis backtestu · Model: Dynamic Team Strength V1 (team_strength_v1)
    [Zakres raportu: 2016/2017 – 2026/2027] [Rozgrzewka: ...] [Sezon w toku: ...]
(2) Filtry
    [Model] [Rozgrywki] [Płeć] [Sezon] [Sezonów w raporcie] [Drużyna] [Trafiony] [Wierszy] [Filtruj] [Wyczyść filtry]
    Typ prognozy: [ ] ✓ Poprawny [ ] ✕ Nieprzewidziany
    Wynik 1X2 (rzeczywisty): [ ] H — gospodarz [ ] X — remis [ ] A — gość
    Wynik prezentowany: [ ] Dokładny wynik  [ ] Poprawna różnica bramek
    Ocena wyniku:       [ ] Dokładny wynik [ ] Dokładna różnica [ ] ±1 [ ] ±2–3 [ ] ±4+
    Ocena score error:  [ ] Bardzo trafna [ ] Trafna [ ] Przeciętna [ ] Słaba [ ] Bardzo słaba
(3) Podsumowanie wybranego zakresu
    [Liczba prognoz][Trafione 1X2][Trafność 1X2][MAE gosp.][MAE gościa][MAE różnicy]
    [MAE sumy][Średni score_error][Mediana score_error]
    [Poprawny typ prognozy][Dokładny wynik][Dokładna różnica bramek][Różnica ±1 lub lepiej]
    [score_error ≤ 2][score_error ≤ 4][score_error ≤ 6]
(4) Historia prognoz (przewijana, nagłówek sticky; rysunek zawija szeroką tabelę)
    Data | Sezon | Liga | Kol. | Gospodarz (link) | Gość | Rating H | Rating A | Δ rating
    | Prognoza | Wynik | Ocena wyniku (pigułka) | Typ prognozy (✓/✕ H/X/A) | Prog. H | Real H | Błąd H | Prog. A | Real A | Błąd A
    | Prog. różn. | Real różn. | Błąd różn. | Prog. suma | Real suma | Błąd sumy
    | Typ modelu | Wynik 1X2 | Trafiony (✓/✕) | Score error | Ocena (kolorowa pigułka)
    [paginacja]
(5) Założenia i dane wejściowe
    Parametry modelu: symbol | wartość | znaczenie   ||   Mecze pominięte: powód | liczba
```

| Element | Plik | Blok / selektor / metoda |
| --- | --- | --- |
| 1. Opis i zakresy | [list.html](list.html), [match_prediction_presenter.py](../../../../presenters/match_prediction_presenter.py) | `.prediction-scope`, `_zakres()` |
| 2. Filtry i walidacja | [match_prediction_filters.py](../../../../admin/forms/match_prediction_filters.py) | `PrognozyMeczowFilterForm.do_filtrow()` |
| 2. Sezonów w raporcie | formularz, serwis | `ZakresRaportuForm.do_zakresu()`, `LICZBY_SEZONOW_RAPORTU`, `PodzialSezonowPolicy._liczba_sezonow_raportu()` |
| 2. Opcje list | [report_views.py](../../../../admin/views/report_views.py), presenter | `opcje_poziomow()`, `opcje_plci()`, `opcje_klas()`, `opcje_sezonow()` |
| 3. Wskaźniki | [match_prediction_service.py](../../../../../services/match_prediction_service.py), presenter | `PodsumowaniePrognozCalculator`, `_wskazniki()` |
| 3. Progi | [match_predictions.py](../../../../../domain/match_predictions.py) | `ProgiTrafnosci.progi_podsumowania` |
| 4. Wiersze tabeli | presenter | `_pozycja()`, `PozycjaPrognozyViewModel`, skrót ligi z `SKROTY_POZIOMOW` |
| 4. Filtrowanie i strony | serwis | `RaportPrognozService.pobierz_raport()`, `_pasuje()` |
| 4. Kliknięcie wiersza | [match_predictions.js](../../../../static/js/match_predictions.js) | `WierszePrognozController` |
| 4. Klasy trafności | domena, presenter | `ProgiTrafnosci.klasyfikuj()`, `ETYKIETY_KLAS`, `.ocena-*` |
| 4. Ocena wyniku | domena, presenter | `ProgiWyniku.klasyfikuj()`, `OcenaPrognozy.klasa_wyniku`, `ETYKIETY_KLAS_WYNIKU`, `.wynik-*` |
| 2. Checkboxy | [list.html](list.html), [admin.css](../../../../static/css/admin.css) | `fieldset.prediction-checks`, pola `dokladny_wynik`, `poprawna_roznica`, `ocena_wyniku`, `ocena` |
| Styl tabeli i kafelków | [admin.css](../../../../static/css/admin.css) | `.prediction-table`, `.prediction-table-wrap`, `.prediction-kpis`, `.prediction-hit`, `.prediction-grade` |
| 5. Parametry i wykluczenia | presenter | `SYMBOLE_PARAMETROW`, `ETYKIETY_WYKLUCZEN` |
| Paginacja | [pagination.html](../../../partials/pagination.html) | zmienna `strona` |
