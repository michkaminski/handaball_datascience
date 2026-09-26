# Typowania kolejki

Status: wdrożony 2026-09-26 na polecenie użytkownika („w terminarzu na kolejkę chcę mieć też okno modalne; po kliknięciu na kolejkę pokazuje się kolejka z typowaniami”). Szablon `tips.html` istnieje.

Docelowy szablon względem katalogu szablonów: `admin/schedule/tips.html`. Trasa `GET /administracja/terminarz/typowania?id_sezon=…&id_rozgrywki=…&id_kolejka=…` (opcjonalnie `model`), endpoint `administracja.typowania_kolejki`, widok `TypowaniaKolejkiView` ([schedule_views.py](../../../admin/views/schedule_views.py)).

## Przeznaczenie

Typowania wszystkich meczów jednej kolejki. Strona jest zwykłą stroną HTML (działa w nowej karcie i bez JavaScriptu), a [terminarz](list.md) wstawia jej sekcję `[data-schedule-tips]` do okna dialogowego po kliknięciu nazwy kolejki.

Na polecenie użytkownika każdy mecz pokazuje **tylko** nagłówek „Gospodarz — Gość” i sześć wartości: Prognoza wyniku, Typ modelu, Typ prognozy, Przewidywana różnica, Przewidywana suma, Δ rating (z HOME_ADVANTAGE). Nie ma wyniku, oceny, ratingów ani kroków obliczenia.

- Mecz nierozegrany: prognoza na teraz, czyli stan modelu po wszystkich wpisanych wynikach ligi (jak w [zapowiedzi](preview.md)).
- Mecz rozegrany: te same sześć wartości z prognozy sprzed meczu, jak w raporcie „Prognozy meczów”.
- Mecz, dla którego prognozy nie ma (liga spoza modelu, walkower, wycofanie): tekst „Prognoza niedostępna: …”.

## Dane wejściowe

- `typowania`: `TypowaniaKolejkiViewModel` z `TypowaniaPresenter.przygotuj_kolejke()`: `tytul` (nazwa kolejki albo „Kolejka N”) i `mecze` (`TypowanieKolejkiViewModel`: `id_mecz`, `naglowek`, `wskazniki` — sześć `WskaznikZapowiedziViewModel` albo pusto, `opis_braku`).
- `parametry_powrotu`: `id_sezon`, `id_rozgrywki`, `id_runda` do linku „Terminarz” w ścieżce.
- `sekcja_aktywna="terminarz"`, `sekcja_glowna="mecze"`.

Brak `id_sezon`, `id_rozgrywki` lub `id_kolejka` albo wartość nieliczbowa → 400 (`TypowaniaKolejkiForm`). Nieznany model → 400. Kolejka bez meczów → komunikat `[data-tips-empty]`.

## Powiązania

`TypowaniaKolejkiView` → `ZaleznosciZadaniaFactory.utworz_typowania_kolejki()` → `TypowaniaKolejkiService` ([match_tip_service.py](../../../../services/match_tip_service.py)). Mecze pochodzą z `TerminarzReadRepository.pobierz_mecze()` (te same filtry co terminarz), prognozy z `PrognozaZapowiedziService.pobierz_wiele()` ([match_prediction_service.py](../../../../services/match_prediction_service.py)): jeden przebieg modelu na żądanie dla wszystkich meczów kolejki. Domena: [match_tips.py](../../../../domain/match_tips.py). Prezentacja: [match_tip_presenter.py](../../../presenters/match_tip_presenter.py), sześć wartości daje `PrognozaMeczuPresenter.wskazniki_typowania()` (wspólne z zapowiedzią meczu).

## Sprawdzenie zmiany

`tests/unit/test_match_tip_service.py` (`test_typowania_kolejki`, zbiorcze prognozy), `tests/interface/test_schedule.py` (link kolejki i okno, tylko sześć wartości, kolejka zakończona i spoza modelu, 400) i `tests/javascript/schedule.test.cjs` (otwarcie okna, Ctrl+klik, błąd odczytu, zamknięcie). Na bazie (tylko odczyt) LOTTO Superliga 2026/2027: kolejka zakończona i przyszła po 6 meczów, odpowiedź około 1 s.

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `tips.html`. W oknie terminarza widoczna jest tylko sekcja `[data-schedule-tips]`; nagłówek strony `[data-tips-navigation]` pojawia się wyłącznie w samodzielnej karcie.

```text
Okno w terminarzu (dialog [data-tips-dialog], szer. do 760 px)
+----------------------------------------------------------------+
| (1) Typowania — Seria 3                                    [×] |
+----------------------------------------------------------------+
| (2) KGHM Chrobry Głogów — Piotrkowianin Piotrków Trybunalski   |
| (3) [Prognoza wyniku ][Typ modelu      ][Typ prognozy    ]     |
|     [ 32:26          ][ H — gospodarz  ][ H — gospodarz  ]     |
|     [Przewid. różnica][Przewid. suma   ][Δ rating (z H_A)]     |
|     [ +6.04          ][ 58.54          ][ +241.60        ]     |
|     ─────────────────────────────────────────────────────      |
| (2) Następny mecz … / „Prognoza niedostępna: …”                |
+----------------------------------------------------------------+
| (4)                        [Otwórz w nowej karcie] [Zamknij]   |
+----------------------------------------------------------------+
```

Wskaźniki tworzą siatkę 3 × 2, a do 520 px 2 × 3. Każdy wskaźnik ma lewy akcent, małą szarą etykietę i pogrubioną wartość.

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1, 4. Okno, tytuł, przyciski | [list.html](list.html), [schedule.js](../../../static/js/schedule.js) | `dialog[data-tips-dialog]`, `[data-tips-dialog-title]`, `[data-tips-open-tab]`, `[data-tips-close]`; `OknoTypowanController`. |
| 2. Nagłówek meczu | [match_tip_presenter.py](../../../presenters/match_tip_presenter.py) | `TypowaniaPresenter._druzyny()` (faktyczny gospodarz z modelu albo `MeczPolicy.para()`). |
| 3. Sześć wartości | [match_prediction_presenter.py](../../../presenters/match_prediction_presenter.py), [tips.html](tips.html) | `wskazniki_typowania()`; `dl.tips-kpis`. |
| Tekst braku prognozy | [match_prediction_presenter.py](../../../presenters/match_prediction_presenter.py) | `opis_braku()`. |
| Tryb prognozy | [match_prediction_service.py](../../../../services/match_prediction_service.py) | `PrognozaZapowiedziService.pobierz_wiele()`, `_rozstrzygnij()`. |
| Wygląd | [admin.css](../../../static/css/admin.css) | `.tips-dialog`, `.tips-match`, `.tips-kpis`. |
