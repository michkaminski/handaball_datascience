# Frekwencja — zakładka Atrakcyjność (MAF)

Fragment `maf_panel.html` dołączany na końcu `dashboard.html` (`{% include %}` wewnątrz `div[data-attendance]`). Zakładka `maf` w `ZAKLADKI_FREKWENCJI` ([attendance_tabs.py](../../../../presenters/attendance_tabs.py)); adres `GET /administracja/raporty/frekwencja?zakladka=maf`.

Panel nie liczy niczego przy wejściu na stronę. Kontekst szablonu to tylko `modele_maf` (`AtrakcyjnoscFrekwencyjnaService.modele()` — klucz, etykieta, czy wytrenowany, wersja, status diagnostyki). Wszystkie dane pobiera `static/js/attendance_appeal.js` z API JSON dopiero przy pierwszym pokazaniu zakładki:

| Endpoint | Trasa | Zwraca |
| --- | --- | --- |
| `administracja.maf_dane` | `/raporty/frekwencja/maf/dane?model=` | model, jakość danych, diagnostyka, współczynniki, KPI, kluby (bez histogramów), gospodarze, rozgrywki, hale, niespodzianki, rekordy, heatmapa, PPC, backtest, `links` |
| `administracja.maf_klub` | `/raporty/frekwencja/maf/klub/<id>` | pełny wpis klubu (histogram posterior IAF, ilustracja centralna, sezony) + metadane modelu do „Jak obliczono?” |
| `administracja.maf_gospodarz` | `/raporty/frekwencja/maf/gospodarz/<id>` | `HostOpponentAnalysis` — rywale zwiększający i zmniejszający zainteresowanie u gospodarza |
| `administracja.maf_porownanie` | `/raporty/frekwencja/maf/porownanie?a=&b=` | \(P(\mathrm{IAF}_a > \mathrm{IAF}_b)\), MCSE, różnica |
| `administracja.maf_prognoza` | `/raporty/frekwencja/maf/prognoza?gospodarz=&rywal=&rozgrywki=&sezon=&pojemnosc=&dzien=&godzina=&faza=&prog=` | `AttendanceSimulator` — rozkład predykcyjny |
| `administracja.maf_eksport` | `/raporty/frekwencja/maf/eksport.csv` | ranking IAF w CSV (UTF-8 z BOM, `;`) |

Brak artefaktu modelu → 404 JSON `{"blad": "… uv run python -m handball.maf_cli <klucz>"}`; błędne parametry → 400.

## Linkowanie matematyki

Elementy `span[data-maf-info="<klucz>"]` i wywołania `ikonaInfo('<klucz>')` w JS używają kluczy metryk z `POJECIA_MAF` ([attendance_appeal.py](../../../../domain/attendance_appeal.py)), które wskazują identyfikator pojęcia z rejestru `mathlib` i kotwicę. Payload `links` zawiera `pojecia` (nazwa, krótka definicja, URL i kotwice definicji, wzoru, wyprowadzenia, przykładu), `metryki` (klucz → pojęcie i URL) oraz `model` (strona naukowa MAF). Najechanie na ikonę „i” pokazuje definicję, kliknięcie przypina okno z odnośnikami. Testy `tests/unit/test_mathlib.py` sprawdzają, że każdy użyty klucz istnieje, a każda kotwica jest w artykule.

## Układ tekstowy i mapa zmian

```text
section#att-panel-maf [data-attendance-panel=maf]
┌ Model Atrakcyjności Frekwencyjnej (MAF)            [Model ▾] [Dokumentacja naukowa] ┐
│ uwaga: filtry raportu nie zawężają modelu                                            │
│ [status: ok / ostrzeżenie / niewiarygodny · wersja · trening · R-hat · ESS]          │
│ KPI ×8: łączna | średnia | mediana | wypełnienie | spotkania | rekord | efekt | IAF   │
│ Ranking · Forest · Trendy · Posterior · Gospodarz · Symulator · Odchylenia · …       │
│ #maf-ranking   szukaj | tylko wiarygodne | min. meczów | Porównaj (0/2) | CSV          │
│   # ☐ Klub Mecze Średnia Mediana Wypełnienie IAF Efekt P(>100) [==|==] Jak obliczono? │
│   └ szczegóły wiersza: jako rywal | jako gospodarz | IAF w sezonach                   │
│ #maf-forest    kluby × IAF, punkt = mediana, odcinek = 95%, linia IAF = 100           │
│ #maf-trendy    [klub ▾][Dodaj] chips; linie median + pasmo 80% w sezonach; tabela    │
│ #maf-posterior [klub ▾] histogram próbek, zielone słupki = IAF > 100                 │
│ #maf-gospodarz [gospodarz ▾] tabele: najbardziej / najsłabiej przyciągający rywale    │
│ #maf-symulator formularz (gospodarz, rywal, rozgrywki, sezon, hala, pojemność, dzień, │
│                godzina, faza, próg) → wyniki + wykres rozkładu predykcyjnego         │
│ #maf-odchylenia heatmapa reszt | niespodzianki + / − | rekordy sezonu/klubu/obiektu  │
│ #maf-diagnostyka MCMC | walidacja chronologiczna | współczynniki | hierarchia | PPC/PIT│
│ #maf-jakosc    liczniki kontroli jakości + przykładowe zgłoszenia                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
dialog[data-maf-dialog]  „Jak obliczono IAF — klub”: wzór (KaTeX), ilustracja na
                         wartościach centralnych vs faktyczna metoda z próbek posterior
```

| Element | Selektor | Dane / kod |
| --- | --- | --- |
| Korzeń i adresy API | `div[data-maf][data-url-*]` | `url_for('administracja.maf_*')` |
| Wybór modelu | `select[data-maf-model]` | `modele_maf` |
| Status | `[data-maf-status]` | `diagnostics`, `model` |
| KPI | `[data-maf-kpis]` | `kpi` |
| Ranking | `table[data-maf-ranking]`, `[data-maf-search]`, `[data-maf-reliable]`, `[data-maf-min]`, `[data-maf-compare]`, `[data-maf-export]` | `clubs[].away`, `clubs[].home` |
| Wykresy ECharts (SVG) | `[data-maf-chart="forest|trend|posterior|heatmap|ppc|pit|symulacja"]` | `rysuj()` w `attendance_appeal.js` |
| Gospodarz | `[data-maf-host-select]`, `[data-maf-host]` | `maf_gospodarz` |
| Symulator | `form[data-maf-sim]`, `[data-maf-sim-result]` | `maf_prognoza` |
| Odchylenia i rekordy | `[data-maf-surprises]`, `[data-maf-records]` | `surprises`, `records`, `heatmap` |
| Diagnostyka | `[data-maf-diagnostics]` | `diagnostics`, `backtest`, `coefficients`, `model.groups`, `ppc` |
| Jakość danych | `[data-maf-quality]` | `quality` |
| Ślad obliczenia | `dialog[data-maf-dialog]` | `maf_klub` |
| Ikony definicji | `span[data-maf-info]` → `button[data-maf-info-button]`, `div[data-maf-popover]` | `links` |
| Styl | `static/css/attendance_appeal.css` (`.maf-*`) | — |
