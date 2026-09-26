# Terminarz

Status: wdrożony 2026-09-25 na polecenie użytkownika („Po linku Mecze, link Terminarz”). Szablon `list.html` istnieje.

Docelowy szablon względem katalogu szablonów: `admin/schedule/list.html`. Trasa `GET /administracja/terminarz`, endpoint `administracja.terminarz`, widok `TerminarzView` ([schedule_views.py](../../../admin/views/schedule_views.py)).

## Przeznaczenie

Prosty terminarz jednych rozgrywek w jednym sezonie. Mecze są pogrupowane według rundy → kolejki → dnia i uporządkowane po numerze kolejki, terminie i ID. Zakończony mecz pokazuje wynik po 60 minutach (z dopiskiem dogrywki lub serii karnych), nierozegrany `– : –`. Każdy wiersz prowadzi do [zapowiedzi meczu](preview.md); link „Szczegóły” otwiera kartę meczu w nowej karcie. Nazwa kolejki (od 2026-09-26) otwiera okno dialogowe z [typowaniami kolejki](tips.md): dla każdego meczu sześć wartości prognozy modelu.

## Filtry

| Oznaczenie | Pole | Działanie |
| --- | --- | --- |
| F1 | Sezon `id_sezon` (wymagany) | Lista sezonów; bez parametru wybierany jest najnowszy (`SezonReadRepository.pobierz_wszystkie()` sortuje malejąco po ID). Nieznany sezon → 400. |
| F2 | Rozgrywki `id_rozgrywki` (wymagane) | Rozgrywki wybranego sezonu po ID (nazwy rozgrywek powtarzają się między sezonami, a nawet w sezonie). Bez wyboru strona pokazuje prośbę o wybór zamiast tabeli. |
| F3 | Runda `id_runda` | Rundy rozgrywek, w kolejności pierwszej kolejki. „Wszystkie” bez zawężenia. |
| F4 | Kolejka `id_kolejka` | Kolejki rozgrywek (albo wybranej rundy) po numerze. |

Wybór jest kaskadowy. `TerminarzService.pobierz_opcje()` odrzuca wartość zależną, która nie należy do wyższego poziomu (np. rozgrywki z innego sezonu), zamiast zwracać 400 — dzięki temu działa też przesłanie formularza bez JavaScriptu po zmianie sezonu. Wartość nieliczbowa → 400 (`TerminarzFilterForm`). `FiltryTerminarzaController` w [schedule.js](../../../static/js/schedule.js) po zmianie pola czyści i wyłącza pola niższych poziomów (`data-schedule-level`) i wysyła formularz; wyłączone pola nie trafiają do adresu.

## Dane wejściowe

- `opcje`: `OpcjeTerminarza` (sezony, rozgrywki, rundy, kolejki jako `OpcjaWyboru` oraz oczyszczony `wybor`); `opcje.filtry` jest `None`, dopóki nie wybrano sezonu i rozgrywek.
- `terminarz`: `TerminarzViewModel | None` z `TerminarzPresenter` — rundy (`RundaTerminarzaViewModel`) → kolejki (`KolejkaTerminarzaViewModel`: nazwa, zakres dat, liczba meczów i zakończonych) → dni (`DzienTerminarzaViewModel`: „sob. 26.09.2026”) → mecze (`MeczTerminarzaViewModel`).
- `opcje.wybor.id_sezon`, `opcje.wybor.id_rozgrywki` i `KolejkaTerminarzaViewModel.id_kolejka`: adres typowań kolejki (`administracja.typowania_kolejki`); kolejka bez ID nie ma linku.
- `parametry`: bieżące parametry adresu; dopinane do linku zapowiedzi, żeby „← Terminarz” wracał do tych samych filtrów.
- `sekcja_aktywna="terminarz"`, `sekcja_glowna="mecze"` — w sidebarze świeci „Terminarz”, w górnym pasku „Dane”.

Termin to `data_faktyczna`, a przy jej braku `data_propozycji`; wtedy godzina to „—” z dopiskiem „prop.”. Gospodarz, gość i wynik uwzględniają `zamiana` przez `MeczPolicy.para()`. Status (Zakończony, Zaplanowany, Walkower, Wycofany) daje `MeczPolicy.status()`.

## Powiązania

`TerminarzView` → `ZaleznosciZadaniaFactory.utworz_serwis_terminarza()` → `TerminarzService` ([schedule_service.py](../../../../services/schedule_service.py)) → `TerminarzReadRepository` ([kontrakt](../../../../contracts/schedule_repository.py), [SQLAlchemy](../../../../infrastructure/repositories/schedule_repository.py)) i `SezonReadRepository`. Domena: [schedule.py](../../../../domain/schedule.py). Prezentacja: `TerminarzPresenter` w [schedule_presenter.py](../../../presenters/schedule_presenter.py), modele w [view_models/schedule.py](../../../view_models/schedule.py).

## Sprawdzenie zmiany

`tests/unit/test_schedule_service.py` (domyślny sezon, nieznany sezon, odrzucanie nieaktualnych wyborów, grupowanie), `tests/interface/test_schedule.py` (link w sidebarze, prośba o wybór, grupowanie i wyniki, filtr kolejki, puste rozgrywki, 400/405) i `tests/javascript/schedule.test.cjs` (kaskada filtrów, klikalne wiersze, okno typowań kolejki). Testy okna typowań opisuje [tips.md](tips.md). Na bazie (tylko odczyt) LOTTO Superliga 2026/2027: 132 mecze, 22 kolejki w dwóch rundach.

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `list.html`. Nagłówek, menu, sidebar i stopka pochodzą z `base.html`.

```text
+-------------------+----------------------------------------------------------------+
| Dane              | (1) Start › Dane › Terminarz                                   |
|  Mecze            |     TERMINARZ — opis                                           |
|  Terminarz [akt.] | (2) FILTRY (osobny jasny panel, jedna linia na desktopie)      |
|  ...              | Sezon*   Rozgrywki*          Runda       Kolejka               |
|                   | [2026/27][LOTTO Superliga  ][Wszystkie ][Wszystkie ][Filtruj][Wyczyść]|
|                   | (3) albo: „Wybierz sezon i rozgrywki…” / „Brak meczów…”         |
|                   | (4)                                   Meczów w terminarzu: 132 |
|                   | (5) I RUNDA                                                    |
|                   |     ────────────────────────────────────────────────────────── |
|                   | (6) KOLEJKA 1  ← link: okno „Typowania — Kolejka 1” (tips.md)   |
|                   |     04.09–06.09.2026 · zakończone 6/6                          |
|                   | (7) PT. 04.09.2026                                             |
|                   | (8) 18:00      Gospodarz  19 : 46  Gość   hala  [✓ ZAKOŃCZONY] Zapowiedź Szczegóły |
|                   |     ────────────────────────────────────────────────────────── |
|                   | (7) SOB. 05.09.2026                                            |
|                   | (8) 15:00      …                                               |
|                   |     ─ ─ ─ cienki separator kolejek ─ ─ ─                        |
|                   | (6) KOLEJKA 2 …                                                |
|                   | (5) II RUNDA …                                                 |
+-------------------+----------------------------------------------------------------+
```

Styl (decyzja użytkownika z 2026-09-25): klasyczna tekstowa lista wyników sportowych na białym tle, bez tabeli `<table>`, kart, cieni, kolorowych bloków i dużych nagłówków. Terminarz to `section.schedule` (białe tło, tylko cienka górna i dolna linia, bez zaokrągleń), nie `.panel`. Runda (`h2.schedule-round`) to mały napis wersalikami z cienką dolną linią. Kolejka (`h3.schedule-matchday-title`) jest pogrubiona, wersalikami, z zakresem dat i licznikiem zakończonych w drugiej, szarej linii (`p.schedule-matchday-meta`); kolejne kolejki dzieli cienki separator. Dzień (`h4.schedule-day`) to mały szary napis.

Mecze dnia to lista `ul.schedule-list`; każdy mecz to jeden poziomy wiersz `li.schedule-row` z siatką CSS o stałych kolumnach (godzina 56 px, gospodarz, wynik 76 px, gość, hala, status 100 px, akcje 128 px), więc kolumny są wyrównane w całym terminarzu. Najmocniejsze są nazwy drużyn (półgrube) i wynik (bardzo gruby, liczby tabelaryczne); nierozegrany `– : –` jest szary. Hala jest mniejsza i szara. Status to mały badge wersalikami z cienką ramką („✓ Zakończony”, „Zaplanowany”, walkower i wycofanie w odcieniu ostrzeżenia). „Zapowiedź” to mały link tekstowy, „Szczegóły” jest szary. Między meczami są cienkie jasnoszare linie, a pionowe odstępy są małe. Za długie nazwy kończą się wielokropkiem, pełna nazwa jest w `title`.

Nazwa kolejki jest linkiem w kolorze tekstu z kropkowanym podkreśleniem (niebieskim po najechaniu). Zwykły klik otwiera okno `dialog[data-tips-dialog]` na dole szablonu, Ctrl/Shift/środkowy przycisk — zwykłą stronę typowań.

Do 900 px wiersz ma kolumny: godzina, gospodarz, wynik, gość, „Zapowiedź”; hala, status i „Szczegóły” są ukryte.

Filtry to kontener flex (`.schedule-filters`) w osobnym jasnym panelu: na desktopie jedna linia, pola i przyciski mają wysokość 30 px, etykiety są w jednej linii nad polami, rozgrywki są szersze (240–320 px). Przy braku miejsca elementy przechodzą do kolejnego wiersza; do 600 px pola zajmują po pół szerokości, do 430 px całą.

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Ścieżka, tytuł, opis | [list.html](list.html) | `.pagehead`, blok `tytul`. |
| 2. Filtry i kaskada | [list.html](list.html), [schedule_filters.py](../../../admin/forms/schedule_filters.py), [schedule.js](../../../static/js/schedule.js), [schedule_service.py](../../../../services/schedule_service.py) | `[data-schedule-filters]`, `data-schedule-level`, `TerminarzFilterForm`, `TerminarzService.pobierz_opcje()`. |
| 2. Opcje list | [schedule_repository.py](../../../../infrastructure/repositories/schedule_repository.py) | `pobierz_rozgrywki()`, `pobierz_rundy()`, `pobierz_kolejki()`. |
| 3. Prośba o wybór / pusty wynik | [list.html](list.html) | `[data-schedule-prompt]`, `[data-schedule-empty]`. |
| 5–7. Grupowanie | [schedule_service.py](../../../../services/schedule_service.py), [schedule_presenter.py](../../../presenters/schedule_presenter.py) | `TerminarzService._grupuj()`; nazwy, zakres dat i dni tygodnia w `TerminarzPresenter` i `KalendarzFormat`. |
| Wiersz meczu | [list.html](list.html), [schedule_presenter.py](../../../presenters/schedule_presenter.py) | `li.schedule-row` i jego `span`-y, `TerminarzPresenter._mecz()` (godzina, wynik, dopisek, status). |
| Dane meczów | [schedule_repository.py](../../../../infrastructure/repositories/schedule_repository.py) | `pobierz_mecze()` i jego sortowanie. |
| Klik wiersza | [schedule.js](../../../static/js/schedule.js) | `WierszeTerminarzaController`. |
| 6. Link kolejki i okno typowań | [list.html](list.html), [schedule.js](../../../static/js/schedule.js), [tips.md](tips.md) | `a[data-tips-link]` w `h3.schedule-matchday-title`, `dialog[data-tips-dialog]`; `OknoTypowanController`; `id_kolejka` w `TerminarzPresenter._kolejka()`. |
| Wygląd | [admin.css](../../../static/css/admin.css) | `.schedule-filters`, `.schedule-field`, `.schedule-filter-actions`, `.schedule`, `.schedule-total`, `.schedule-round`, `.schedule-matchday-*` (także `.schedule-matchday-title a`), `.schedule-day`, `.schedule-list`, `.schedule-row` (siatka kolumn), `.schedule-badge` oraz reguły `@media` 900/600/430 px. |
| Pozycja w sidebarze | [navigation.py](../../../navigation.py) | `SIDEBAR`, grupa „Dane”, klucz `terminarz`. |
