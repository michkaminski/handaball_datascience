# Raport meczu — PDF A4

Status: wdrożony 2026-10-11 na polecenie użytkownika („wydruk do meczu … niech będzie wow, wykorzystaj analizy meczu i idź w Data Science … profesjonalnie, czytelnie”). Szablon [report_pdf.html](report_pdf.html) istnieje.

## Przeznaczenie i powiązania

Jednostronicowy raport rozegranego meczu (A4 w pionie) dla mediów, klubu i kibiców. Otwiera go przycisk „Raport meczu (PDF, A4)” na stronie szczegółów meczu ([detail.md](detail.md)), widoczny tylko dla meczu z wynikiem. Trasa: `GET /administracja/mecze/<id_mecz>/raport`, odpowiedź `application/pdf` (`raport-meczu-<id>.pdf`, inline). `?format=html` zwraca ten sam HTML bez generowania PDF, do podglądu i testów. Mecz bez wyniku lub nieistniejący: 404, błąd odczytu: 503, brak bibliotek Pango: 503.

Przepływ: `RaportMeczuPdfView` → `RaportMeczuService` → `StatystykiMeczuService` (szczegóły, składy, forma), `ZapowiedzMeczuReadRepository` (mecz, występy drużyn, kadra przed meczem), `PrognozyModeluService` (backtest `team_strength_v1`) → kalkulatory domenowe z [match_report.py](../../../../domain/match_report.py) → `RaportMeczuPresenter` → `RaportMeczuViewModel` → szablon → `PdfResponseBuilder` (WeasyPrint, arkusz [match_report_pdf.css](../../../static/css/match_report_pdf.css)). Nie ma nowych zapytań SQL: raport składa istniejące repozytoria.

## Wersja skrócona

Na prośbę użytkownika (2026-10-11) `?wariant=skrocony` daje skrót na jednej kartce: ten sam nagłówek (z dopiskiem „· skrót”), bez zdania przewodniego, wniosków i kafelków, a potem tylko ① Porównanie drużyn, ② Historia spotkań (obok porównania), Strzelcy (do 16 na drużynę) i Na tle sezonu. Bez modelu, wykresu ratingu i formy; serwis nie uruchamia backtestu (`RaportMeczuService.pobierz(..., z_modelem=False)`), więc skrót powstaje w ok. 1 s. Ten sam szablon i arkusz z flagą `skrocony` (klasa `body.skrocony` powiększa krój, odstępy i paski, żeby wypełnić kartkę). Plik: `raport-meczu-<id>-skrocony.pdf`. Gdy brak historii, porównanie zajmuje całą szerokość; gdy brak strzelców i tła sezonu obu drużyn, sekcji drużyn nie ma. Przycisk „Raport skrócony (PDF)” stoi obok pełnego raportu.

```text
┌─ ciemny pasek: RAPORT MECZOWY · SKRÓT, nagłówek jak w pełnej wersji ─┐
┌ ① Porównanie drużyn ─────────┐┌ ② Historia spotkań ─────────────────┐
│ paski jak w pełnej wersji     ││ [W 32:31 / data · dom / rozgrywki]×8│
└───────────────────────────────┘└─────────────────────────────────────┘
┌ ▌Gospodarz: Strzelcy, Na tle sezonu ┐┌ ▌Gość: Strzelcy, Na tle sezonu ┐
przypisy                                 Sportomatyka „Bawimy się danymi”
```

## Treść i metody

Wszystkie liczby powstają w Pythonie przed renderowaniem; szablon nie liczy i nie uruchamia skryptów.

- **Nagłówek** — rozgrywki, sezon, runda, kolejka, termin, wynik, połowy, dogrywka lub karne, hala, widzowie. Przy nazwie dłuższej niż 22 znaki nagłówek ma mniejszy krój (`.scoreline.long`).
- **Zdanie przewodnie** — z modelu: „Niespodzianka…” gdy zwycięzca miał przed meczem mniej niż 40% szans, „mecz otwarty” przy 40–50%, „wyżej / skromniej niż przewidywał model” przy odchyleniu różnicy o co najmniej 4 bramki, inaczej „zgodnie z prognozą”. Remis po 60 minutach z rozstrzygnięciem bierze pierwszy wniosek meczu.
- **Wnioski (do 4)** — wnioski z `WnioskiMeczuGenerator` oraz dwa rodzaje wniosków statystycznych: wyjątkowy występ zawodnika (rozkład Poissona ze średnią sezonu sprzed meczu, minimum 5 meczów i 3 bramki, prawdopodobieństwo poniżej 10%) i wyjątkowy wynik obrony/ataku drużyny (percentyl ≤ 10% straconych lub ≥ 90% zdobytych na tle meczów sezonu w tych samych rozgrywkach, minimum 5 meczów).
- **Kafelki KPI (do 5)** — szansa zwycięzcy przed meczem, indeks zaskoczenia (percentyl |reszty| wśród meczów ligi z backtestu, z = reszta/σ), zmiana ratingu, bramki w meczu z percentylem sezonu ligi, widzowie; bez modelu także najlepszy strzelec.
- **① Porównanie drużyn** — paski względem lepszej drużyny (karne według skuteczności); przewaga pogrubiona tylko tam, gdzie „więcej” znaczy „lepiej”.
- **Historia spotkań** — do 8 ostatnich meczów bezpośrednich sprzed meczu z perspektywy gospodarza (`StatystykiZapowiedziCalculator.bezposrednie`), z bilansem wszystkich; każdy mecz ma rozgrywki (bez wiodącego sponsora zapisanego wielkimi literami, np. „Superliga kobiet”, `_rozgrywki`).
- **② Model siły drużyn** (gdy mecz jest w backteście `team_strength_v1`) — szanse 1/X/2 z rozkładu normalnego różnicy bramek wokół prognozy (σ = odchylenie standardowe reszt ligi w sezonach raportu, minimum 30 meczów; remis = |różnica| < 0,5), prognoza vs wynik, reszta, klasa trafności, histogram reszt ligi z krzywą normalną (`HistogramResztBuilder`; pomarańczowe słupki = wyniki co najmniej tak zaskakujące), ratingi przed meczem, zmiana i ranking siły po meczu w sezonie (`AnalizaModeluCalculator`).
- **② Struktura ataku** (gdy modelu brak) — udział trzech najlepszych strzelców i pozostałych w bramkach każdej drużyny oraz efektywna liczba strzelców.
- **③ Siła drużyn w czasie** — rating po każdym z ostatnich 20 meczów ligowych drużyny (`WykresRatinguBuilder`); oś to kolejne terminy meczów obu drużyn, nie kalendarz, więc przerwy między sezonami nie tworzą pustych pól; linia drużyny jest przerywana na granicy sezonów, a sezony mają separatory i podpisy.
- **Kolumny drużyn** — strzelcy (do 9, reszta w linii „Pozostali”): bramki z paskiem na wspólnej skali obu drużyn, karne, kary 2 min, średnia sezonu sprzed meczu i Δ (zielone ≥ +1,5, czerwone ≤ −1,5), ★ wyjątkowy występ; efektywna liczba strzelców (Σb)²/Σb² i udział trzech najlepszych. „Na tle sezonu” (minimum 3 wcześniejsze mecze w rozgrywkach): wykres punktowy bramek zdobytych i straconych (`WykresSezonuBuilder`), duża kropka — ten mecz, kreska — średnia, z percentylem. Forma: 5 meczów sezonu do tego meczu włącznie.
- **Przypisy** — tylko te, których elementy są na stronie (★, Δ, kropki).
- **Podpis** — wyłącznie „Sportomatyka „Bawimy się danymi”” w prawym dolnym rogu (`@page @bottom-right`), bez stopki o źródle danych i modelu. Braki danych ukrywają sekcję zamiast notatki.

Nazwiska zapisane wielkimi literami są skracane do „I. Nazwisko” z zachowaniem członów wielowyrazowych i małych partykuł (`dos`, `de`).

## Układ tekstowy i mapa zmian

```text
┌──────────────────────────── ciemny pasek (.mast) ────────────────────────────┐
│ RAPORT MECZOWY      rozgrywki · sezon · runda · kolejka          dzień, data │
│ ▌Gospodarz               33:29                 Gość▐                         │
│              do przerwy 16:13 · druga połowa 17:16 · (dogrywka/karne)        │
│                       hala, miasto · widzowie                                │
└──────────────────────────────────────────────────────────────────────────────┘
▌Zdanie przewodnie z modelu
• wniosek 1                         • wniosek 3 (Poisson)
• wniosek 2                         • wniosek 4 (percentyl sezonu)
[Szansa zwycięzcy][Indeks zaskoczenia][Zmiana ratingu][Bramki w meczu][Widzowie]
┌ ① Porównanie drużyn ──────────┐┌ ② Model siły drużyn / ② Struktura ataku ─┐
│ 33 ████ Bramki ███ 29          ││ [38% | 8% | 54%] szanse                   │
│ …                              ││ Prognoza | Wynik | Ponad prognozę | Trafn.│
│ Historia spotkań               ││ histogram reszt + krzywa + znacznik       │
│ [W 32:31][R 30:30][P …][…]     ││ rating przed · zmiana · ranking           │
└────────────────────────────────┘└───────────────────────────────────────────┘
③ Siła drużyn w czasie: linie ratingu, separatory sezonów, kreska „ten mecz”
┌ ▌Gospodarz ────────────────────┐┌ ▌Gość ─────────────────────────────────────┐
│ Strzelcy: # Zawodnik Br.▬ K 2' ││ Strzelcy …                                 │
│   śr. sez. Δ (★)               ││                                            │
│ Na tle sezonu: kropki zdobyte/ ││ Na tle sezonu …                            │
│   stracone + opis z percentylem││                                            │
│ Forma [P][P][W] bilans          ││ Forma …                                    │
└────────────────────────────────┘└────────────────────────────────────────────┘
przypisy (★ · Δ · kropki)                     Sportomatyka „Bawimy się danymi”
```

| Element | Plik i miejsce |
| --- | --- |
| Nagłówek | [report_pdf.html](report_pdf.html): `header.mast`, `.mast-top`, `.scoreline(.long)`, `.mast-sub`, `.mast-meta`; dane `kontekst`, `termin`, `wynik`, `przebieg`, `dopisek`, `hala`, `widzowie`, `dlugie_nazwy` |
| Zdanie przewodnie, wnioski | `.headline`, `ul.insights`; [match_report_presenter.py](../../../presenters/match_report_presenter.py): `_naglowek`, `_wnioski`, `_wniosek_strzelca`, `_wniosek_sezonu` |
| Kafelki | `table.kpis`, `.kpi.hot`; `_kafelki`, `_kafelek_bramek`, `_najlepszy_strzelec` |
| Porównanie | `table.compare`, `.track`, `.fill`, `.better`; `_porownanie`, `_wiersz`, `_wiersz_karnych` |
| Historia spotkań | `table.h2h`, `.fm`; `_historia`; [match_report_service.py](../../../../services/match_report_service.py): `_bezposrednie` |
| Model | `table.prob`, `.prob-legend`, `table.xg`, `svg.hist`, `table.ratings`; `_model`; [match_report_charts.py](../../../match_report_charts.py): `HistogramResztBuilder`; domena: `AnalizaModeluCalculator`, `AnalizaModelu` |
| Struktura ataku | `table.struct-bar`, `table.struct-labels`, `.s1/.s2/.s3/.rest`; `_struktura` |
| Siła w czasie | `svg.rating`; `WykresRatinguBuilder`, `LiniaRatingu.odcinki`, `WykresRatingu.separatory` |
| Strzelcy | `table.scorers`, `tr.star`, `.up`, `.down`; `_atak`, `_strzelec`, `_wyjatkowosc`, `_zawodnik`; domena: `AtakDruzynyCalculator`, `StrzelecRaportu.prawdopodobienstwo_wystepu` |
| Na tle sezonu, forma | makro `wykres_sezonu`, `svg.strip`, `.season-line`, `.form-line`; `_tlo`; `WykresSezonuBuilder`; domena: `TloSezonuCalculator` |
| Przypisy, podpis | `.caption.legend`, `_przypisy`; CSS `@page @bottom-right` |
| Kontrakt danych | [match_report.py](../../../view_models/match_report.py): `RaportMeczuViewModel` i modele sekcji |
| Wersja skrócona | flaga `skrocony` w [report_pdf.html](report_pdf.html), makro `historia_spotkan`, `.cols.short`, CSS `.skrocony …`; `RaportMeczuPdfView.LIMIT_SKROCONY` |
| Widok i trasa | [match_views.py](../../../admin/views/match_views.py): `RaportMeczuPdfView`; [admin/__init__.py](../../../admin/__init__.py): `raport_meczu_pdf` |

## Weryfikacja

`tests/unit/test_match_report_analytics.py` (10 testów) sprawdza na syntetycznej lidze przeliczonej prawdziwym backtestem: prawdopodobieństwa sumujące się do 1, percentyl, ranking, ścieżkę ratingu z sezonami, tło ligi, koncentrację ataku i średnie sezonu, rozkład Poissona, filtr tła sezonu, histogram, podział wykresu ratingu na sezony, wykres punktowy i format liczb. `tests/interface/test_match_report.py` (9 testów, w tym wersja skrócona i jej przycisk) sprawdza PDF z arkuszem, wariant bez modelu (struktura ataku, historia, nazwiska), wariant z modelem, 404, przycisk na stronie meczu i nagłówek „Niespodzianka” z kafelkami. Wygląd sprawdzono w PDF wygenerowanym przez WeasyPrint i zamienionym na PNG na danych z bazy (odczyt): mecze 205624, 206511, 208133, 207606, 1783, 205606, 203883 — każdy na jednej stronie.
