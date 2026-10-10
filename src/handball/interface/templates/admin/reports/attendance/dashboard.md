# Frekwencja

Dashboard analityki frekwencji kibiców. Trasa `GET /administracja/raporty/frekwencja`, endpoint `administracja.raport_frekwencji`, widok `FrekwencjaView` ([attendance_analytics_views.py](../../../admin/views/attendance_analytics_views.py)). Pozycja w katalogu raportów i sidebarze Raporty › Frekwencja.

Źródło: `mecze.widzowie` z rozegranych meczów (pełny wynik, bez wycofania i walkoweru). `NULL` nie jest zerem i nie wchodzi do średniej, mediany ani sumy. `0` to mecz bez publiczności i liczy się jako znana wartość, chyba że włączono filtr „Pomiń zera”. Ranking klubów i przeciwników obejmuje wyłącznie mecze u siebie (miejsce po `zamiana`). Wypełnienie obiektu tylko gdy znana `hale.pojemnosc > 0`.

## Etapy

- **Etap 1:** KPI, trendy sezonowe, ranking klubów, TOP 50 rekordów.
- **Etap 2:** Przeciwnicy, Kalendarz, Rozszerzone rekordy.
- **Etap 3:** Data Science (rozkład, rozrzut, anomalie IQR, efekty dnia tygodnia i przeciwnika, korelacje, prognoza OLS).

Termin meczu to `COALESCE(mecze.data_faktyczna, mecze.data_propozycji)`. Kolumny `mecze.godzina` nie ma; dzień tygodnia, miesiąc i godzina pochodzą z tego znacznika czasu (`timestamp without time zone`, traktowany jako czas lokalny Europe/Warsaw, bez konwersji). Godzina 00:00 oznacza brak godziny i nie wchodzi do rozkładu godzin ani mapy cieplnej. Runda/faza to `rundy.nazwa` przez `kolejki.id_runda`; finały są dopasowywane przybliżenie po `rundy.nazwa`, `kolejki.nazwa` lub `rozgrywki.nazwa` zawierającym „fina”.

Całość strony (poza filtrami) jest opakowana w `div[data-attendance]` z adresem ECharts (`data-echarts-url`), aktywną zakładką (`data-active-tab`) i jednym blokiem JSON `#attendance-chart-data` przygotowanym przez `FrekwencjaWykresPresenter`: `sezony`, `heatmapa`, `histogram`, `kluby` (top 15: nazwa, średnia, znane), `miesiace` / `dni` / `godziny` (etykieta, średnia, znane, rozegrane), `miasta` (top 30 miast według sumy: klucz, nazwa, suma, średnia, mediana, dominanta, znane, kluby), `miastaSzczegoly` (te same miasta: klucz, nazwa oraz listy `sezony` — sezon, rozegrane, suma, średnia, mediana, znane; `rozgrywki` i `hale` — nazwa, suma, średnia, mediana, znane), `przeciwnicy` (do 20 wierszy: nazwa, średnia, różnica; pusta lista bez filtra Gospodarz), `pokrycie` (sezon, znane, rozegrane, pokrycie w procentach 0–100), `efektDnia` (etykieta, średnia, n).

## Zakładki

Pasek `.match-tabs.att-tabs[role=tablist][data-attendance-tabs]` (ukryty do uruchomienia JS; bez JS wszystkie panele są widoczne) z przyciskami `data-tab` i panelami `section.panel[data-attendance-panel][id=att-panel-*]`. Filtry zostają nad zakładkami; ukryte pole `data-attendance-tab-field` przenosi aktywną zakładkę przy filtrowaniu.

| Klucz | Etykieta | Panel | Zawartość |
|---|---|---|---|
| `overview` | Podsumowanie | `#att-panel-overview` | KPI, uwagi, wykres pokrycia (`coverage`) |
| `trends` | Trendy | `#att-panel-trends` | wykres `trend`, tabela sezonów |
| `clubs` | Kluby | `#att-panel-clubs` | wykres `clubs`, szukaj, tabela rankingu |
| `cities` | Miasta | `#att-panel-cities` | uwaga o źródle, KPI braków miasta, wykresy `cities` / `citiesMean` / `citiesMedian` (top 30 obok siebie; każdy sortowany malejąco po swojej metryce), ranking miast (mediana, dominanta, min, max), wykresy wybranego miasta (`citySeasons`, `cityCompetitions`, `cityHalls`), tabele sezonów, rozgrywek i hal miast, „Skąd pochodzi frekwencja” |
| `records` | Rekordy | `#att-panel-records` | TOP 50 |
| `opponents` | Przeciwnicy | `#att-panel-opponents` | wykres `opponents`, tabela |
| `calendar` | Kalendarz | `#att-panel-calendar` | wykresy `months`, `weekdays`, `hours`, tabele, `heatmap` |
| `extended` | Rekordy+ | `#att-panel-extended` | rekordy sezonów, klubów, hal, finałów, par |
| `science` | Data Science | `#att-panel-science` | `histogram`, `weekdayEffect`, rozrzut, anomalie, korelacje, prognoza |
| `maf` | Atrakcyjność (MAF) | `#att-panel-maf` | fragment [maf_panel.html](maf_panel.md): bayesowski Model Atrakcyjności Frekwencyjnej, dane z API JSON i zapisanego artefaktu modelu |

Wybór zakładki: `?zakladka=` lub `?tab=` (nieznany klucz → `overview`), logika w [attendance_tabs.py](../../../presenters/attendance_tabs.py) (`WyborZakladkiFrekwencji`, `ZAKLADKI_FREKWENCJI`). Kliknięcie zmienia `?zakladka=` przez `history.replaceState`; kotwica (np. `#kalendarz`) otwiera swoją zakładkę. Wykresy są inicjowane przy pierwszym pokazaniu panelu (`MenedzerWykresow`), a przy kolejnych pokazaniach i zmianie okna wywoływane jest `resize()`.

## Układ tekstowy i mapa zmian

```text
Start › Raporty › Frekwencja
Frekwencja
Widzowie na rozegranych meczach...

[ Filtry: Sezon | Rozgrywki | Płeć | Gospodarz | Hala | Pomiń zera ]

┌ div[data-attendance] ───────────────────────────────────────────────┐
[ Podsumowanie | Trendy | Kluby | Miasta | Rekordy | Przeciwnicy | Kalendarz | Rekordy+ | Data Science | Atrakcyjność (MAF) ]  ← tablist

▸ Podsumowanie
[ KPI: suma | znane | rozegrane | pokrycie | średnia | mediana | rekord | YoY | wypełnienie? ]
[ uwagi o kompletności ]
[ wykres: mecze znane (słupki) + pokrycie % (linia) według sezonów ]

▸ Trendy
[ Trendy sezonowe ]
  [ wykres ECharts średnia / mediana / śr. 3 sezony ]
  [ tabela sezonów: rozegrane, znane, suma, średnia, mediana, Q1, Q3, YoY, śr. 3 ]

▸ Kluby
[ Frekwencja gospodarzy według klubu ]
  [ szukaj ]  Top N… YoY…
  [ wykres poziomy: średnia top 15 klubów ]
  [ tabela: # | klub | mecze | znane | suma | średnia | mediana | min | max | YoY ]

▸ Miasta
[ Frekwencja według miasta klubu gospodarza ]
  [ uwaga: miasto z zespoly_sezony.miasto gospodarza, nie z hali ]
  [ KPI: mecze bez miasta klubu | miasta w rankingu | wiersze wkładu ]
  [ wykresy obok siebie: suma / średnia / mediana, top 30; każdy malejąco po swojej metryce ]
  [ Ranking miast: szukaj miasta; # | miasto | mecze | znane | suma | średnia | mediana | dominanta | min | max | kluby | rozgrywki ]
  [ Wybrane miasto: select (domyślnie pierwsze z rankingu) + 3 wykresy: sezony (średnia słupki + mediana linia) | rozgrywki (suma) | hale (suma) ]
  [ Sezony w miastach: szukaj + filtr miasta; miasto | sezon | mecze | znane | suma | średnia | mediana | dominanta | min | max ]
  [ Rozgrywki w miastach: szukaj + filtr miasta; miasto | rozgrywki | kluby | mecze … max ]
  [ Hale w miastach: uwaga, szukaj + filtr miasta; miasto klubu | hala | miasto hali (gdy inne) | mecze … max ]
  [ Skąd pochodzi frekwencja: szukaj + filtr miasta + filtr rozgrywek; miasto | klub | rozgrywki | mecze | znane | suma | średnia | max ]

▸ Rekordy
[ Rekordy frekwencji ]
  [ TOP 50: data, sezon, rozgrywki, drużyny, wynik, hala, widzowie, szczegóły ]

▸ Rekordy+
[ Rozszerzone rekordy ]
  [ Rekordy sezonów ]   tabela rekordów (jak wyżej)
  [ Rekordy klubów ]    top 30, mecz u siebie
  [ Rekordy hal ]       top 30
  [ Finały ]            top 30, dopasowanie po „fina”
  [ Pary drużyn ]       top 30, niezależnie od gospodarza

▸ Przeciwnicy
[ Przeciwnicy ]
  bez klubu: uwaga „wybierz Gospodarza”
  z klubem:  [ wykres poziomy: średnia według rywala (zielony ≥ średnia gospodarza, czerwony poniżej) ]
             [ tabela: # | przeciwnik | mecze | znane | średnia | max | różnica vs średnia gospodarza | pokrycie ]

▸ Kalendarz
[ Kalendarz ]
  uwaga o terminach
  [ wykresy słupkowe: miesiące | dni tygodnia | godziny ]
  [ Miesiąc ][ Dzień tygodnia ]   tabele: etykieta | rozegrane | znane | średnia
  [ Godzina  ][ Weekend/roboczy ]
  [ Runda / faza ]
  [ Mapa cieplna dzień × godzina: wykres ECharts + <details> tabela średnia (n) ]

▸ Data Science
[ Data Science ]
  [ Rozkład: histogram ECharts + percentyle p10 p25 p50 p75 p90 p95 + <details> tabela ]
  [ Rozrzut: n | średnia | odchylenie | CV + ostrzeżenie n<5 ]
  [ Anomalie IQR: granice, tabela wysokie | tabela niskie ]
  [ Efekt dnia tygodnia: wykres słupkowy + tabela z n i różnicą ]
  [ Efekt przeciwnika: tabela (tylko z filtrem Gospodarz) ]
  [ Korelacja Pearsona: różnica bramek, suma bramek + ostrzeżenie „nie przyczyna” ]
  [ Prognoza OLS: n uczące/testowe, MAE, RMSE, punkty odniesienia, współczynniki | powód pominięcia ]
└─────────────────────────────────────────────────────────────────────┘
```

| Element | Plik | Bloki / dane |
|---|---|---|
| Widok i trasa | [attendance_analytics_views.py](../../../admin/views/attendance_analytics_views.py), [admin/__init__.py](../../../admin/__init__.py) | `FrekwencjaView`, `/raporty/frekwencja` |
| Menu i katalog | [navigation.py](../../../navigation.py), [report_catalog.py](../../../report_catalog.py) | klucz `frekwencja` |
| Filtry | [attendance_analytics_filters.py](../../../admin/forms/attendance_analytics_filters.py) | `FrekwencjaFilterForm` |
| Serwis | [attendance_analytics_service.py](../../../../services/attendance_analytics_service.py) | `FrekwencjaService.pobierz_raport()` składa `RaportFrekwencji` |
| Domena (raport, ranking, trend) | [attendance_analytics.py](../../../../domain/attendance_analytics.py) | `FrekwencjaCalculator`, `RaportFrekwencji` (`rekordy_rozszerzone`, `przeciwnicy`, `kalendarz`, `data_science`) |
| Domena (Etap 2) | [attendance_opponents.py](../../../../domain/attendance_opponents.py), [attendance_calendar.py](../../../../domain/attendance_calendar.py), [attendance_records.py](../../../../domain/attendance_records.py) | `PrzeciwnicyFrekwencjiCalculator`, `KalendarzFrekwencjiCalculator`, `RekordyRozszerzoneFrekwencji` |
| Domena (Etap 3) | [attendance_data_science.py](../../../../domain/attendance_data_science.py), [attendance_forecast.py](../../../../domain/attendance_forecast.py), [attendance_sample.py](../../../../domain/attendance_sample.py) | `FrekwencjaDataScienceCalculator`, `PrognozaFrekwencjiCalculator`, `RegresjaOLS`, `MeczProbki` |
| Domena (miasta) | [attendance_cities.py](../../../../domain/attendance_cities.py) | `MiastoFrekwencji` (z `MiaryRozkladu`), `WkladMiasta`, `DaneMiast`, `WierszMiasta`, `RaportMiast`, `MiastaMerger`, `MiastaFrekwencjiCalculator`; limity 100 miast i 300 wierszy wkładu |
| Domena (rozbicia miast) | [attendance_city_breakdowns.py](../../../../domain/attendance_city_breakdowns.py), [attendance_city_names.py](../../../../domain/attendance_city_names.py) | `SezonMiasta`, `RozgrywkiMiasta`, `HalaMiasta`, `przydziel_do_miast`; `klucz_miasta`, `najczestsza_pisownia` |
| SQL miast | [attendance_cities_queries.py](../../../../infrastructure/repositories/attendance_cities_queries.py), [attendance_city_rows.py](../../../../infrastructure/repositories/attendance_city_rows.py), [attendance_rows.py](../../../../infrastructure/repositories/attendance_rows.py) | `ZESTAWY_MIAST`: agregat po kluczu miasta, wkład miasto × klub × rozgrywki, sezony, rozgrywki, hale, licznik meczów bez miasta; mappery wierszy |
| Wspólne | [attendance_aggregate.py](../../../../domain/attendance_aggregate.py), [attendance_formatting.py](../../../../domain/attendance_formatting.py) | `AgregatFrekwencji`, formatery, `percentyl` |
| Kontrakt repo | [attendance_analytics_repository.py](../../../../contracts/attendance_analytics_repository.py) | `FrekwencjaReadRepository` (m.in. `pobierz_przeciwnikow`, `pobierz_kalendarz`, `pobierz_rekordy_rozszerzone`, `pobierz_probke`) |
| Repo | [attendance_analytics_repository.py](../../../../infrastructure/repositories/attendance_analytics_repository.py), [attendance_extended_queries.py](../../../../infrastructure/repositories/attendance_extended_queries.py), [attendance_sql.py](../../../../infrastructure/repositories/attendance_sql.py) | agregacje SQL, próbka do 8000 meczów |
| Wykresy miast | [attendance_cities_presenter.py](../../../presenters/attendance_cities_presenter.py) | `MiastaWykresPresenter` (`miasta`, `miastaSzczegoly`, top 30); hosty `citySeasons`, `cityCompetitions`, `cityHalls` w `div[data-city-charts]` z `select[data-city-select]`; JS: `WyborMiasta`, `MenedzerWykresow.odswiez` |
| Wykresy | [attendance_analytics_presenter.py](../../../presenters/attendance_analytics_presenter.py), [attendance_analytics.js](../../../static/js/attendance_analytics.js), [goal_charts.js](../../../static/js/goal_charts.js) | `FrekwencjaWykresPresenter`; hosty `[data-chart="trend|coverage|clubs|cities|heatmap|months|weekdays|hours|opponents|histogram|weekdayEffect"]` (dodatkowo `data-attendance-chart`, `-heatmap`, `-histogram`, `-chart-coverage`, `-chart-clubs`, `-chart-cities`, `-chart-months`, `-chart-weekdays`, `-chart-hours`, `-chart-opponents`, `-chart-weekday-effect`); ECharts SVG, rejestr `WYKRESY`, `MenedzerWykresow`, `ZakladkiFrekwencji` |
| Zakładki | [attendance_tabs.py](../../../presenters/attendance_tabs.py) | `ZAKLADKI_FREKWENCJI`, `WyborZakladkiFrekwencji` |
| Makra szablonu | dashboard.html | `zmiana`, `naglowki_miar`, `komorki_miar`, `pasek_miast`, `tabela_rekordow`, `tabela_kalendarza`, `tabela_efektu`, `tabela_anomalii` |
| Styl | [admin.css](../../../static/css/admin.css) | `.att-*` (m.in. `.att-subpanel`, `.att-cal-grid`, `.att-chart-grid`, `.att-chart-sm`, `.att-tabs`, `.att-warning`, `.att-heatmap`, `.att-details`), `.match-tabs`, `[data-attendance-panel][hidden]` |

Kotwice sekcji (na `.panel-body` w panelu zakładki): `#trendy`, `#kluby`, `#miasta` (`#miasta-sezony`, `#miasta-rozgrywki`, `#miasta-hale`), `#rekordy`, `#rekordy-rozszerzone`, `#przeciwnicy`, `#kalendarz`, `#data-science` (`#ds-rozklad`, `#ds-rozrzut`, `#ds-anomalie`, `#ds-dni`, `#ds-przeciwnik`, `#ds-korelacje`, `#ds-prognoza`).

## Zasady zakładki Miasta

- Miasto pochodzi wyłącznie z sezonowej karty klubu gospodarza: `NULLIF(btrim(zg.miasto), '')`, gdzie `zg` to `zespoly_sezony` dla gospodarza po `zamiana` w sezonie meczu. Miasto hali nie jest używane jako zastępstwo.
- Puste lub `NULL` miasto wyklucza mecz z rankingu; takie rozegrane mecze są zliczane w KPI „Mecze bez miasta klubu” i w uwadze o brakach (liczą się też mecze bez gospodarza).
- Reguły frekwencji bez zmian: `NULL` ≠ 0, tylko rozegrane mecze (`WARUNKI_MECZU`), filtr „Pomiń zera” zmienia predykat znanej frekwencji. Miasta i wiersze bez żadnego meczu ze znaną frekwencją są pomijane.
- Ranking: suma widzów malejąco, potem średnia, potem nazwa; limit 100 miast. Wkład klubów (miasto × klub × rozgrywki) jest dołączany pod miastami rankingu w jego kolejności, w obrębie miasta według sumy; limit 300 wierszy łącznie. Nazwa klubu to najnowsza nazwa z karty sezonowej w danej grupie.
- Wykresy `cities`, `citiesMean` i `citiesMedian` obok siebie: te same top 30 miast, ale każdy sortowany malejąco po swojej metryce (suma / średnia / mediana); tabela „Skąd pochodzi frekwencja” ma wyszukiwarkę oraz filtry miasta i rozgrywek (`data-attendance-filter`, `FiltrTabeli` w JS; ten sam mechanizm obsługuje wyszukiwarkę klubów).
- Tożsamość miasta: klucz = obcięcie, zwinięcie białych znaków i `casefold` (w SQL `lower(btrim(regexp_replace(zg.miasto, '\s+', ' ', 'g')))`); „Gdańsk” i „GDAŃSK” to jedno miasto, polskie znaki zostają. Etykieta w ekranie to najczęstsza pisownia (SQL `mode() WITHIN GROUP`, przy remisie pierwsza w porządku alfabetycznym). `MiastaMerger` łączy w Pythonie wiersze o tym samym kluczu (np. gdy baza ma lokalizację `C` i `lower()` nie obsługuje polskich liter): sumuje liczniki, bierze maksimum i minimum, a medianę i dominantę ustawia na „—”, bo nie da się ich złożyć z agregatów. Wiersze sezonów, rozgrywek, hal i wkładu są przypisywane do miasta po tym samym kluczu.
- Miary rozkładu miasta liczy SQL na meczach ze znaną frekwencją (z filtrem „Pomiń zera”): `percentile_cont(0.5)` (mediana), `mode() WITHIN GROUP` (dominanta, przy remisie najmniejsza wartość), `MIN`, `MAX`. Dominanta bywa mało informatywna przy rozproszonych wynikach.
- Sezony miasta: wszystkie sezony miast z rankingu, rosnąco po `sezony.rok_rozpoczecia` (sezon bez roku na początku); łącznie do 600 wierszy w kolejności rankingu miast.
- Rozgrywki miasta: zestawienie miasto × rozgrywki bez podziału na kluby (z liczbą klubów), po sumie malejąco; do 15 pozycji na miasto i 400 łącznie.
- Hale miasta: hale, w których rozegrano mecze u siebie klubów z miasta (`mecze.id_hala` → `hale`), grupowane po `hale.id`; mecze bez hali są pomijane w tej tabeli. Przypisanie do miasta nadal wynika z klubu gospodarza; „Miasto hali” jest pokazane tylko, gdy po normalizacji różni się od miasta klubu. Do 10 hal na miasto i 300 łącznie.
- Wykresy wybranego miasta pokazują miasto z `select[data-city-select]` (domyślnie pierwsze z rankingu, lista = top 30 z wykresu `cities`); zmiana wyboru przerysowuje tylko te trzy wykresy bez przeładowania strony. Każda tabela ma wyszukiwarkę i filtr miasta (`FiltrTabeli`).
- Zapytania są tylko do odczytu (SELECT).

## Zasady Etapu 3

- Próbka to najnowsze mecze ze znaną frekwencją w zakresie filtrów, maksymalnie 8000; przycięcie jest opisane w uwadze.
- Percentyle p10, p25, p50, p75, p90, p95; odchylenie standardowe próbkowe (n−1); CV = odchylenie / średnia; ostrzeżenie przy n&lt;5.
- Anomalie: poza `[Q1 − 1,5·IQR, Q3 + 1,5·IQR]`, tabele pokazują do 15 najbardziej odstających.
- Korelacja Pearsona frekwencji z różnicą (gospodarz − gość) i sumą bramek; to współwystępowanie, nie przyczyna, bo wynik jest znany po meczu.
- Prognoza OLS używa tylko cech znanych przed meczem (weekend, godzina, miesiąc jako sin/cos, średnia ostatnich 5 meczów gospodarza z wcześniejszych terminów w próbce); uczenie na wcześniejszych 80% meczów, test na ostatnich 20%; pomijana przy n&lt;40; MAE i RMSE podane obok punktów odniesienia.
