# Typowania meczów

Status: wdrożony 2026-09-26 na polecenie użytkownika („raport, gdzie wstawię daty od do (również przyszłe), rozgrywki (wielowybór), a on pokaże tabelkę taką jak Historia prognoz; domyślnie dzień dzisiejszy, wszystkie ligi, grupuj po lidze, rundzie, kolejce, czasie”). Szablon `list.html` istnieje.

Docelowy szablon względem katalogu szablonów: `admin/reports/match_tips/list.html`. Trasa `GET /administracja/raporty/typowania-meczow`, endpoint `administracja.raport_typowan_meczow`, widok `TypowaniaMeczowView` ([report_views.py](../../../../admin/views/report_views.py)). Pozycja w katalogu raportów ([report_catalog.py](../../../../report_catalog.py)) i w sidebarze Raporty › Typowania meczów.

## Przeznaczenie

Prosty raport z jedną tabelą: mecze Superligi, Ligi Centralnej i I Ligi (rozgrywki rozpoznane przez `WzorceNazwLig`, jak w modelu) z okresu od–do, także przyszłe.

- Mecz rozegrany i obecny w modelu: wiersz liczony dokładnie jak w „Historii prognoz” raportu [Prognozy meczów](../match_predictions/list.md) — prognoza sprzed meczu, wynik, błędy, ocena. Obejmuje też mecze sezonów rozgrzewki. Wiersz prowadzi do szczegółów prognozy.
- Mecz nierozegrany: prognoza na teraz (stan modelu po wszystkich wpisanych wynikach ligi); kolumny wyniku i błędów to „—”. Wiersz prowadzi do [zapowiedzi meczu](../../schedule/preview.md).
- Mecz bez prognozy (walkower, wycofanie, brak drużyny, rozegrany, ale pominięty przez model): powód w jednej komórce na miejscu kolumn prognozy.

Brak podsumowania i metryk — tylko tabela.

## Filtry

| Pole | Działanie |
| --- | --- |
| Data od / Data do (`data_od`, `data_do`, `RRRR-MM-DD`) | Termin meczu `coalesce(data_faktyczna, data_propozycji)` w dniach od–do włącznie. Bez parametru: dzisiaj (`ZegarWarszawa`). Podana jedna data uzupełnia drugą. Od > do albo nieprawidłowa data → 400. |
| Rozgrywki (`rozgrywki`, wielokrotny) | Nazwy rozgrywek (łączą rekordy sezonowe). Lista zawiera rozgrywki modelu z meczami w okresie oraz już wybrane. Brak wyboru = wszystkie ligi modelu. |
| Model (`model`) | Pole widoczne, gdy katalog ma więcej niż jeden model. Nieznany model → 400. |

„Dzisiaj, wszystkie ligi” przywraca domyślne filtry.

## Druk tabeli

Przycisk „Drukuj tabelę” nad tabelą (`[data-print-table]`, polecenie użytkownika z 2026-09-26) otwiera nową kartę z samą tabelą jako czystym tekstem: bez grafiki, kolorów, pigułek i linków, z cienkimi czarnymi ramkami. Nad tabelą jest tytuł (`data-print-title`) i opis (`data-print-subtitle`). Tabelę kopiuje `DrukTabeliController` w [print_table.js](../../../../static/js/print_table.js): bierze `textContent` każdej komórki i zachowuje `th`/`td` oraz `colspan`. Kartę drukuje się poleceniem przeglądarki (Ctrl+P). Wiersze nagłówków grup trafiają do wydruku jako scalone komórki. Opis podaje okres, rozgrywki, model i liczbę meczów.

## Grupowanie

Grupy są uporządkowane według poziomu rozgrywek (decyzja użytkownika z 2026-09-26): najpierw Superliga (także „Ekstraklasa”), potem Liga Centralna, I Liga, II Liga, III Liga, IV Liga, na końcu pozostałe (`KolejnoscRozgrywekPolicy` w [competition_levels.py](../../../../../domain/competition_levels.py)). W obrębie poziomu obowiązuje kolejność z repozytorium: nazwa rozgrywek, rekord rozgrywek (sezon), numer kolejki, termin. Lista rozgrywek w filtrze ma tę samą kolejność poziomów, a w poziomie — alfabetyczną. Każda para rozgrywki + runda + kolejka ma wiersz nagłówka grupy `tr.tips-group` („LOTTO Superliga · 2026/2027 · I runda · Seria 4”), a mecze w grupie są posortowane po czasie.

## Dane wejściowe

- `raport`: `RaportTypowanViewModel` z `TypowaniaPresenter.przygotuj_raport()`: model, `okres`, liczniki (`liczba_meczow`, `liczba_rozegranych`, `liczba_przyszlych`), opcje `rozgrywki` i `modele`, `grupy` (`GrupaTypowanViewModel`: `naglowek`, `wiersze`).
- Wiersz `WierszTypowaniaViewModel`: `tryb` (`po_meczu`, `biezaca`, `brak`), data, godzina („—” bez `data_faktyczna`), sezon, kolejka, drużyny, wynik oraz jedno z: `po_meczu` (`PozycjaPrognozyViewModel` — ten sam co w Historii prognoz), `przyszla` (`PrognozaPrzyszlaViewModel`), `opis_braku`.
- `filtry`: `FiltryTypowan` (daty, wybrane rozgrywki, model) do wypełnienia formularza.
- `sekcja_aktywna="typowania_meczow"`, `sekcja_glowna="raporty"`.

## Powiązania

`TypowaniaMeczowView` → `ZaleznosciZadaniaFactory.utworz_raport_typowan()` → `RaportTypowanService` ([match_tip_service.py](../../../../../services/match_tip_service.py)) → `TypowaniaReadRepository` ([kontrakt](../../../../../contracts/match_tip_repository.py), [SQLAlchemy](../../../../../infrastructure/repositories/match_tip_repository.py), zapytanie meczów wspólne z terminarzem: `ZapytanieMeczowTerminarza`) i `PrognozaZapowiedziService.pobierz_wiele()` — jeden przebieg modelu na żądanie. Klik wiersza: `WierszePrognozController` w [match_predictions.js](../../../../static/js/match_predictions.js) (`[data-tips-report] #tips-table`).

## Sprawdzenie zmiany

`tests/unit/test_match_tip_service.py` (domyślne i błędne filtry, grupowanie, sortowanie po czasie, przekazanie rozgrywek, zbiorcze prognozy) i `tests/interface/test_match_tips.py` (sidebar i katalog, domyślnie dzisiaj, trzy tryby wierszy, zaznaczone rozgrywki, przycisk druku, 400/405); druk: `tests/javascript/print_table.test.cjs`. Na bazie (tylko odczyt) 26.09.2026: dzisiaj 38 meczów w 10 grupach; 19.09–04.10.2026 — 136 meczów (50 rozegranych, 86 przyszłych), odpowiedź 1,3–1,9 s.

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `list.html`. Nagłówek, menu, sidebar i stopka pochodzą z `base.html`.

```text
(1) Start › Raporty › Typowania meczów
    TYPOWANIA MECZÓW — opis, model
    [Okres: sob. 19.09.2026 – niedz. 04.10.2026] [Meczów: 19] [Rozegrane: 6] [Przed meczem: 13]
(2) FILTRY
    Data od     Data do     Rozgrywki (brak wyboru — wszystkie)
    [19.09.2026][04.10.2026][I Liga Kobiet Grupa A ▲]  [Filtruj] [Dzisiaj, wszystkie ligi]
                            [LOTTO Superliga       ▼]
(3) TYPOWANIA                                                        [Drukuj tabelę] → nowa karta
    Data|Godz.|Sezon|Liga|Kol.|Gospodarz|Gość|Stan|Rating H|Rating A|Δ rating|Prognoza|Wynik|
    Ocena wyniku|Typ prognozy|Prog. H|Real H|Błąd H|…|Typ modelu|Wynik 1X2|Trafiony|Score error|Ocena
    ── LOTTO Superliga · 2026/2027 · I runda · Seria 3 ─────────────────────────────
    19.09.2026|15:00|…|SL M|3|KGHM …|Piotrkowianin …|[ROZEGRANY]|1524.59|…|32:26|41:21|…
    ── LOTTO Superliga · 2026/2027 · I runda · Seria 4 ─────────────────────────────
    26.09.2026|18:00|…|SL M|4|KGHM …|PGE …|[PRZED MECZEM]|1549.12|…|30:30| — | — |X|…
    …|Bez prognozy| Prognoza niedostępna: walkower.
```

Tabela używa stylów raportu prognoz (`.prediction-table`, przyklejony nagłówek, przewijanie w `.prediction-table-wrap`). Nagłówki grup to pełnoszerokie jasnoniebieskie wiersze. Stan to mały badge wersalikami: „Rozegrany” zielony, „Przed meczem” niebieski, „Bez prognozy” szary.

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Nagłówek i liczniki | [list.html](list.html), [match_tip_presenter.py](../../../../presenters/match_tip_presenter.py) | `.pagehead`, `.prediction-scope`; `przygotuj_raport()`, `_okres()`. |
| 2. Filtry | [list.html](list.html), [match_tip_filters.py](../../../../admin/forms/match_tip_filters.py), [match_tip_service.py](../../../../../services/match_tip_service.py) | `.tips-filters`; `TypowaniaFilterForm`; `RaportTypowanService.filtry()` (domyślne daty i walidacja). |
| 2. Lista rozgrywek | [match_tip_repository.py](../../../../../infrastructure/repositories/match_tip_repository.py) | `pobierz_rozgrywki()`. |
| 3. Mecze i kolejność | [match_tip_repository.py](../../../../../infrastructure/repositories/match_tip_repository.py) | `pobierz_mecze()`, `_w_okresie()`, `_ligi_modelu()`. |
| 3. Grupy | [match_tip_service.py](../../../../../services/match_tip_service.py), [match_tip_presenter.py](../../../../presenters/match_tip_presenter.py), [competition_levels.py](../../../../../domain/competition_levels.py) | `_grupuj()`, `_klucz_czasu()`; `_grupa()` (tekst nagłówka); `KolejnoscRozgrywekPolicy` (kolejność poziomów grup i opcji filtra). |
| 3. Wiersz rozegrany | [match_prediction_presenter.py](../../../../presenters/match_prediction_presenter.py) | `PrognozaMeczuPresenter.pozycja()` (wspólny z Historią prognoz). |
| 3. Wiersz przyszły | [match_prediction_presenter.py](../../../../presenters/match_prediction_presenter.py) | `prognoza_przyszla()`. |
| 3. Wiersz bez prognozy | [match_prediction_presenter.py](../../../../presenters/match_prediction_presenter.py) | `opis_braku()`. |
| 3. Druk tabeli | [list.html](list.html), [print_table.js](../../../../static/js/print_table.js) | `.print-actions`, `[data-print-table]`, `data-print-subtitle`; `WydrukTabeliBuilder`, `DrukTabeliController` |
| Klik wiersza | [match_predictions.js](../../../../static/js/match_predictions.js) | `WierszePrognozController`. |
| Wygląd | [admin.css](../../../../static/css/admin.css) | `.tips-filters`, `.tips-table .tips-group`, `.tips-state*`; reszta z `.prediction-*`. |
| Pozycja w sidebarze i katalogu | [navigation.py](../../../../navigation.py), [report_catalog.py](../../../../report_catalog.py) | klucz `typowania_meczow`. |
