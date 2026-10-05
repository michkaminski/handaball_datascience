# Zapowiedź meczu

Status: wdrożona 2026-09-25 na polecenie użytkownika („zapowiedź meczu, czyli program meczowy przed meczem, ze statystykami sprzed meczu”, z prognozą jak w raporcie prognoz). Szablon `preview.html` istnieje.

Docelowy szablon: `admin/schedule/preview.html`. Trasa `GET /administracja/terminarz/<id_mecz>`, endpoint `administracja.zapowiedz_meczu`, widok `ZapowiedzMeczuView` ([schedule_views.py](../../../admin/views/schedule_views.py)). Parametr `model` wybiera wersję modelu prognoz (nieznana → 400); parametry filtrów terminarza są przekazywane do linku powrotu. Opcje (`ZapowiedzOpcjeForm`): `kadra_poprzedni=y` dołącza do kadry poprzedni sezon, `lata` = 5, 10 (domyślnie), 15, 20 albo `wszystkie` ustala okres meczów bezpośrednich; inna wartość → 400. Brak meczu → 404.

**Pobierz PDF** (polecenie użytkownika z 2026-09-27): przycisk w nagłówku strony (`[data-preview-pdf]`) wysyła formularz opcji `form#preview-options` (`formaction` = `administracja.zapowiedz_meczu_pdf`, `formtarget="_blank"`) i otwiera w nowej karcie całą zapowiedź jako PDF podzielony na strony A4, z bieżącymi opcjami kadry, uwag i okresu. Działa bez JavaScriptu. Układ stron: [preview_pdf.md](preview_pdf.md).

**Protokół do uzupełnienia** (polecenie użytkownika z 2026-09-27): drugi przycisk (`[data-preview-protocol]`) w ten sam sposób otwiera pusty protokół zawodów na jednej kartce A4 — drużyny, kadry pogrupowane według pozycji jak w sekcji Kadra, hala i obsada sędziowska, reszta do wypełnienia ręcznie. Obok przycisku lista „kolejność” (`kolejnosc_protokolu`, pole formularza `#preview-options`, `.preview-protocol-order`): „pozycja, numer” (grupy pozycji, w grupie numery koszulek) albo „według numerów”. Kontrakt: [protocol_pdf.md](protocol_pdf.md).

## Forma programu meczowego

Kolejność sekcji ustalił użytkownik 2026-09-26: 1 Kadra w sezonie, 2 Forma, 3 Porównanie drużyn, 4 Mecze bezpośrednie, 5 Prognoza modelu. Nad nimi są nagłówek meczu i spis treści.

- **Nagłówek meczu** — gospodarz i gość (linki do kart drużyn), wynik albo „vs”, status, termin z dniem tygodnia, hala z miastem, kontekst: rozgrywki · sezon · runda · kolejka. Uwzględnia `zamiana`.

1. **Kadra w sezonie** (zastępuje „Najlepszych strzelców sezonu”) — dla każdej drużyny wszyscy zawodnicy wpisani do protokołów jej meczów we wszystkich rozgrywkach sezonu meczu, rozegranych przed punktem odcięcia. Grupy według pozycji: bramkarze na górze, potem rozgrywający, skrzydłowi, obrotowi, inne pozycje i pozycja nieznana (`KolejnoscPozycjiPolicy`); w grupie według najniższego numeru koszulki rosnąco (bez numeru na końcu), potem nazwiska i imienia (zmienione przez użytkownika 2026-09-27; wcześniej według liczby meczów). Kolumny:
   - Nr — numer na koszulce z protokołów (kilka numerów rozdziela „/”);
   - Zawodnik (link do karty) z datą urodzenia w nawiasie małą szarą czcionką (`zawodnicy.data_urodzenia`, `.preview-birth`; bez daty — bez nawiasu), Pozycja (najczęstsza w protokołach);
   - Mecze, Bramki, Śr. — liczba protokołów, bramki i średnia bramek na mecz w sezonie;
   - kolumna poprzedniego sezonu (np. „2025/2026, br. / śr.”; widoczna, gdy poprzedni sezon istnieje): bramki / średnia na mecz zawodnika we **wszystkich klubach i rozgrywkach** tamtego sezonu, obok liczba meczów małą czcionką. U zawodników dodanych checkboxem (grali w drużynie w poprzednim sezonie, a w bieżącym nie) bramki, średnia i mecze dotyczą **tylko tej drużyny** (dopisek „w tej drużynie”, `PoprzedniSezonZawodnika.tylko_druzyna`, doprecyzowane przez użytkownika 2026-09-26). Pod spodem małą, pomarańczową czcionką: „inny klub: … — N bramek, M meczów” dla każdej drużyny innej niż obecna (inne `zespoly.id`, więc także druga drużyna tego samego klubu; `KlubPoprzedniegoSezonu`) oraz „inna liga: …” dla rozgrywek ligowych innego poziomu niż rozgrywki meczu (Superliga, Liga Centralna, I–IV Liga według `KolejnoscRozgrywekPolicy`; zmiana sponsora nazwy Superligi nie jest oznaczana, puchary i rozgrywki bez rozpoznanego poziomu się nie liczą). Komórka z uwagą ma jasne tło.

   **Najlepsi strzelcy** (polecenie użytkownika z 2026-09-26): pięciu zawodników drużyny z największą liczbą bramek w sezonie ma przy nazwisku znacznik „★ miejsce” (`.preview-scorer`), a komórka bramek jest czerwona (`.top-scorer`, jak na karcie meczu). Miejsca liczone są jak w tabelach: ex aequo dostają to samo miejsce (np. 1, 1, 3), zera nie są wyróżniane (`KadraZapowiedziCalculator.miejsca_strzelcow()`, `LICZBA_STRZELCOW = 5`).

   **Ukryj informacje o innym klubie i innej lidze** (polecenie użytkownika z 2026-09-26): checkbox w opcjach kadry (`bez_uwag=y`, pole formularza `#preview-options`, `ZapowiedzOpcjeForm.bez_uwag`) dodaje klasę `preview-hide-notes` do `div#kadra-druk`. Ukrywa ona uwagi „inny klub” i „inna liga” oraz ich tło (`.preview-hide-notes .preview-prev-note`, `.preview-prev-other`); wartości bramek, średniej i meczów zostają. `UwagiKadryController` w [match_preview.js](../../../static/js/match_preview.js) przełącza klasę od razu, bez przeładowania; stan trafia do adresu przy kolejnym przesłaniu opcji, a bez JavaScriptu — po „Pokaż”. To opcja prezentacji: nie zmienia danych ani `OpcjeZapowiedzi`.

   **Drukuj składy** (polecenie użytkownika z 2026-09-26): przycisk nad kadrą (`[data-print-section="#kadra-druk"]`) otwiera nową kartę z samymi składami obu drużyn (`div#kadra-druk`), w kolorach strony: dołącza arkusz [admin.css](../../../static/css/admin.css) (`data-print-styles`, adres bezwzględny) i wymusza druk kolorów (`print-color-adjust: exact`). Układ druku (ustalony z użytkownikiem 2026-09-26): jedna kartka A4 w pionie (`@page{size:A4 portrait;margin:10mm}`), składy drużyn jeden pod drugim, tabele na całą szerokość. Proporcje tabel i czcionek są takie jak na stronie (arkusz `admin.css`), a całość jest skalowana, żeby zmieściła się na jednej kartce: po załadowaniu karty `DopasowanieDoStrony` (skrypt wstawiany do karty druku) ustawia na `div[data-print-page]` szerokość obszaru druku (718 px) podzieloną przez skalę i `zoom = skala`, zmniejszając skalę o 0,01, aż wysokość treści zmieści się w 1030 px (277 mm). Najmniejsza skala to 0,3 — przy bardzo dużych kadrach treść może wtedy przejść na drugą stronę. Komórki się nie zawijają (`white-space:nowrap`), a w kolumnie poprzedniego sezonu liczba meczów i uwagi „inny klub” i „inna liga” idą jedna za drugą, rozdzielone „·”; zawijać się może tylko ta kolumna. Na meczu 206529 (15 i 16 zawodników) skala wynosi 0,72 i oba składy z legendą mieszczą się na jednej kartce. Przy ukrytych uwagach druk nie zawiera uwag (usuwane z kopii) i ustawia tabele **obok siebie** w dwóch kolumnach na kartce A4 **w poziomie** (klasa `print-landscape` na `div[data-print-page]`, strona nazwana `@page poziomo`); dopasowanie liczy wtedy obszar 1047 × 700 px i sprawdza także, czy każda tabela mieści się w szerokości swojej kolumny. Na meczu 206529 obie tabele mieszczą się obok siebie na jednej kartce w poziomie. Linki są zamieniane na zwykły tekst, a elementy z `data-print-exclude` pomijane. Tytuł: „Kadry w sezonie … : gospodarz — gość”, opis: kontekst meczu, termin, stan na. `DrukSekcjiController` i `WydrukSekcjiBuilder` w [print_table.js](../../../static/js/print_table.js) (obok druku czystej tabeli raportów). Kartę drukuje się poleceniem przeglądarki (Ctrl+P).

   **Skład zgłoszony na sezon** (polecenie użytkownika z 2026-09-27): gdy drużyna nie ma w sezonie meczu wpisanego do protokołów przed punktem odcięcia (np. pierwszy mecz sezonu), kadra pochodzi z `sklady` dla `zespoly_sezony` tej drużyny i sezonu (`ZapowiedzMeczuReadRepository.pobierz_sklad_sezonu()`). Numer i pozycja są wtedy ze składu, imię, nazwisko i data urodzenia z `zawodnicy` (w razie braku — ze składu), a mecze i bramki wynoszą 0. Pod nazwą drużyny pojawia się uwaga „Skład zgłoszony na sezon — drużyna nie ma jeszcze meczów w protokołach” (`KadraDruzyny.ze_skladu`, `.preview-squad-source`). Gdy jest choć jeden protokół, skład nie jest odczytywany. Bez składu kadra zostaje pusta. Opcja poprzedniego sezonu działa tak samo.

   Pole „Dodaj zawodników, którzy w sezonie … zagrali w tej drużynie co najmniej 1 mecz” (`kadra_poprzedni`, doprecyzowane przez użytkownika 2026-09-26) dołącza zawodników, którzy w poprzednim sezonie (sezon z największym `rok_rozpoczecia` mniejszym od bieżącego) mieli w tej drużynie co najmniej jeden mecz z `wyjscie = true` (`ZawodnikKadry.zagrane`, `zagral`), a w bieżącym jeszcze nie grali. Wpis w protokole bez wejścia na boisko nie wystarcza. Interpretacja `wyjscie` jako wejścia na boisko opiera się na danych: w sezonie 2025/2026 Superligi żaden z 687 wpisów z `wyjscie = false` nie ma bramki. Przy braku danych o wejściach (`zagrane = None`) liczy się wpis w protokole. mają „—” w kolumnach bieżącego sezonu oraz numer i pozycję z poprzedniego.
2. **Forma — ostatnie mecze** — 5 ostatnich rozegranych meczów każdej drużyny ze wszystkich rozgrywek: pasek W/R/P i tabela z miejscem (dom/wyjazd) i wynikiem z perspektywy drużyny.
3. **Porównanie drużyn** — tabela „tale of the tape” z meczów tych samych rozgrywek (`id_rozgrywki`) rozegranych przed terminem: mecze, bilans W-R-P, procent wygranych, bramki, różnica, średnie i mediany, bilans gospodarza u siebie i gościa na wyjeździe, forma z 5 ostatnich meczów, bieżąca seria. Pogrubienie wskazuje lepszą wartość (`WierszPorownaniaViewModel.przewaga`).
4. **Mecze bezpośrednie** — wszystkie spotkania drużyn z wybranego okresu przed punktem odcięcia (domyślnie ostatnie 10 lat; lista „Okres”: 5, 10, 15, 20 lat albo wszystkie) — bez limitu liczby meczów. Bilans (wygrane gospodarza, remisy, wygrane gościa, bramki) liczy te same mecze, które są w tabeli. Początek okresu: punkt odcięcia minus N lat (`StatystykiZapowiedziCalculator.poczatek_okresu()`, 29 lutego → 28 lutego).
5. **Prognoza modelu** (`team_strength_v1`) w trzech trybach (`data-preview-forecast`):
   - `biezaca` — mecz nierozegrany: „prognoza na teraz”. Model przelicza wszystkie rozegrane mecze ligi (jak backtest raportu), a następnie odczytuje stan przed tym meczem (z regresją sezonową, jeśli to nowy sezon). Pokazuje prognozę wyniku, typ modelu, typ z zaokrąglonego wyniku, przewidywaną różnicę i sumę, Δ rating oraz ratingi obu drużyn, a w rozwijanym bloku kroki 1–5 z raportu (wzór, podstawienie, wynik, interpretacja). Prognoza zmienia się po każdym nowym wyniku ligi.
   - `po_meczu` — mecz zakończony: ta sama prognoza co w raporcie „Prognozy meczów” (stan sprzed meczu), porównana z wynikiem: trafienie, ocena wyniku, typ prognozy, score_error i zmiana ratingów. Link „Pełne wyliczenie w raporcie prognoz” prowadzi do `administracja.szczegoly_prognozy_meczu`.
   - `brak` — rozgrywki poza modelem (np. II Liga, puchary), walkower, wycofanie, brak drużyny lub rozegrany mecz wykluczony z backtestu; komunikat podaje powód.

Opcje kadry i okresu należą do jednego ukrytego formularza `form#preview-options` (pola sekcji wskazują go atrybutem `form`); ukryte pola przenoszą parametry terminarza i `model`. Bez JavaScriptu działa przycisk „Pokaż” (`formaction` z kotwicą sekcji). `OpcjeZapowiedziController` w [match_preview.js](../../../static/js/match_preview.js) ukrywa przyciski i wysyła formularz po zmianie pola, wracając do jego sekcji.

Punkt odcięcia statystyk (`ZapowiedzMeczu.stan_na`) to `data_faktyczna` meczu, a przy jej braku bieżąca chwila (`ZegarWarszawa`). Liczone są wyłącznie mecze z pełnym wynikiem po 60 minutach, bez walkowerów i meczów wycofanych, wcześniejsze niż punkt odcięcia — także dla meczu zakończonego pokazywany jest stan sprzed meczu. Statystyki liczy domena (`StatystykiZapowiedziCalculator`, `Bilans`), nie szablon.

## Dane wejściowe

- `zapowiedz`: `ZapowiedzMeczuViewModel` z `ZapowiedzMeczuPresenter.przygotuj()`; prognoza to `PrognozaZapowiedziViewModel` z `PrognozaMeczuPresenter.przygotuj_zapowiedz()`.
- `parametry_powrotu`: `id_sezon`, `id_rozgrywki`, `id_runda`, `id_kolejka` z adresu; także ukryte pola formularza opcji.
- `formularz`: `ZapowiedzOpcjeForm` (lista okresów `lata.choices`); `model`: wartość parametru `model` albo `None`.
- W `zapowiedz`: `kadry` (`KadraDruzynyViewModel` → `GrupaKadryViewModel` → `ZawodnikKadryViewModel`), `sezon`, `sezon_poprzedni`, `kadra_z_poprzednim`, `lata_bezposrednich` (wartość wybrana w liście) i `bezposrednie.okres` (opis okresu).
- `sekcja_aktywna="terminarz"`, `sekcja_glowna="mecze"`.

## Powiązania

`ZapowiedzMeczuView` → `ZaleznosciZadaniaFactory.utworz_serwis_zapowiedzi_meczu()` → `ZapowiedzMeczuService` ([match_preview_service.py](../../../../services/match_preview_service.py)) → `ZapowiedzMeczuReadRepository` ([kontrakt](../../../../contracts/match_preview_repository.py), [SQLAlchemy](../../../../infrastructure/repositories/match_preview_repository.py): `pobierz_mecz`, `pobierz_wystepy`, `pobierz_kadre`, `pobierz_poprzedni_sezon`), `KadraZapowiedziCalculator` oraz `PrognozaZapowiedziService` ([match_prediction_service.py](../../../../services/match_prediction_service.py)), który korzysta z `BacktestPrognozService.przelicz()`. Domena: [match_preview.py](../../../../domain/match_preview.py), `MeczPrzyszly`, `PrognozaBiezaca` i `PrognozaZapowiedzi` w [match_predictions.py](../../../../domain/match_predictions.py).

Czas odpowiedzi na bazie z 2026-09-25: ok. 2–4 s, głównie backtest liczony w pamięci przy każdym żądaniu (zob. ARCHITECTURE).

## Sprawdzenie zmiany

Wspólny odczyt widoku strony i PDF: `ZapowiedzMeczuOdczyt` w [schedule_views.py](../../../admin/views/schedule_views.py).

`tests/unit/test_match_preview_service.py` (bilans, forma, seria, mecze bezpośrednie z okresu lat bez limitu, `zamiana`, punkt odcięcia, kadra od bramkarzy, poprzedni sezon z innych klubów i lig, średnie, pięć miejsc strzelców z ex aequo, prognoza bieżąca = stan modelu po wszystkich wynikach, prognoza po meczu = backtest, powody braku), `tests/interface/test_schedule.py` (kolejność sekcji i spisu treści, kadra z numerami i grupami, opcja poprzedniego sezonu, okres meczów bezpośrednich, trzy tryby prognozy, linki, 404/400) i `tests/javascript/match_preview.test.cjs`. Na bazie (tylko odczyt) mecz 206529 LOTTO Superligi: kadry 15 i 16 zawodników (26 i 22 z sezonem 2025/2026), mecze bezpośrednie: 22 z 10 lat, 11 z 5 lat; odpowiedź 1,4–1,6 s.

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `preview.html`.

```text
(1) Start › Dane › Terminarz › Zapowiedź meczu   [← Terminarz] [Szczegóły meczu] [Pobierz PDF] [Protokół do uzupełnienia] kolejność [pozycja, numer ▼]
    ZAPOWIEDŹ MECZU — rozgrywki · sezon · runda · kolejka
(2) +------------------------------------------------------------------+
    |   GOSPODARZ               28 : 27 / vs              GOŚĆ         |
    |   Nazwa (link)            [Zakończony]              Nazwa (link) |
    |        Termin: sob. 26.09.2026, godz. 18:00 · Hala: …, miasto     |
    +------------------------------------------------------------------+
(3) Spis treści: 1 Kadra · 2 Forma · 3 Porównanie · 4 Bezpośrednie · 5 Prognoza
(4) KADRA W SEZONIE 2026/2027
    [ ] Dodaj zawodników, którzy w sezonie 2025/2026 zagrali w tej drużynie co najmniej 1 mecz   ([Pokaż] tylko bez JS)
    Gospodarz (15 zawodników)                 | Gość (16 zawodników)
                                                          [Drukuj składy] → nowa karta
    Nr | Zawodnik (data ur.) | Pozycja | Mecze | Bramki | Śr. | 2025/2026 br. / śr.
    BRAMKARZE                                 | BRAMKARZE
    47 | Jakub MATLĘGA | Bramkarz | 3 | 0 | 0.00 | —
    11 | Marcin SZOPA [★ 1] | Skrzydłowy | 3 | [12] | 4.00 | 125 / 4.17 (30 meczów)
    42 | Dawid PETLAK [★ 2] | Rozgrywający | 3 | [11] | 3.67 | 94 / 4.95 (19 meczów)
                                                         inny klub: AKPR AZS AWF Biała Podlaska
                                                         inna liga: Liga Centralna Mężczyzn
    ROZGRYWAJĄCY / SKRZYDŁOWI / OBROTOWI / …
(5) FORMA — OSTATNIE MECZE
    Gospodarz [W][W][P]…              | Gość [W][R]…
    Data|Rozgrywki|Rywal|Miejsce|Wynik|• | Data|Rozgrywki|Rywal|Miejsce|Wynik|•
(6) PORÓWNANIE DRUŻYN
        wartość gospodarza | Statystyka | wartość gościa   (× 11 wierszy)
(7) MECZE BEZPOŚREDNIE
    Okres [10 lat ▼]  ([Pokaż] tylko bez JS)
    [Mecze][Wygrane H][Remisy][Wygrane A][Bramki]
    Okres: ostatnie 10 lat (od 26.09.2016). Wszystkie spotkania z tego okresu (22)…
    tabela spotkań z perspektywy gospodarza
(8) PROGNOZA MODELU — model, opis trybu
    [Prognoza wyniku][Typ modelu][Typ prognozy][Różnica][Suma][Δ rating] (+ ocena po meczu)
    Drużyna | Rating przed (| Zmiana | Rating po)
    ▸ Jak policzono prognozę — 5 kroków      / [Pełne wyliczenie w raporcie →]
```

Do 900 px sekcje dwukolumnowe (`.preview-grid`) układają się jedna pod drugą, a do 600 px nagłówek meczu staje się pionowy.

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1–2. Nagłówek i mecz | [preview.html](preview.html), [schedule_presenter.py](../../../presenters/schedule_presenter.py) | `.preview-head`, `.preview-hero`, makro `druzyna`; `ZapowiedzMeczuPresenter.przygotuj()`, `KalendarzFormat.termin()`. |
| 1. Pobierz PDF | [preview.html](preview.html), [preview_pdf.html](preview_pdf.html) | `[data-preview-pdf]` (`formaction`, `formtarget`); układ stron w [preview_pdf.md](preview_pdf.md). |
| 1. Protokół do uzupełnienia | [preview.html](preview.html), [protocol_pdf.html](protocol_pdf.html) | `[data-preview-protocol]`; układ w [protocol_pdf.md](protocol_pdf.md). |
| 2. Dane meczu | [match_preview_repository.py](../../../../infrastructure/repositories/match_preview_repository.py), [match_preview.py](../../../../domain/match_preview.py) | `pobierz_mecz()`, `MeczZapowiedzi` (właściwości ze `zamiana`). |
| 4. Kadra | [match_preview_repository.py](../../../../infrastructure/repositories/match_preview_repository.py), [match_preview.py](../../../../domain/match_preview.py), [schedule_presenter.py](../../../presenters/schedule_presenter.py), [preview.html](preview.html) | `pobierz_kadre()` (numery, najczęstsza pozycja, mecze, bramki), `pobierz_poprzedni_sezon()`, `pobierz_wystepy_zawodnikow()` (poprzedni sezon według zawodnika, drużyny i rozgrywek); `KadraZapowiedziCalculator`, `poprzednie_sezony()`, `PoprzedniSezonZawodnika`, `KolejnoscPozycjiPolicy`, `KolejnoscRozgrywekPolicy` ([competition_levels.py](../../../../domain/competition_levels.py)); `_kadra()`, `_zawodnik()`, `GRUPY_POZYCJI`; `section#kadra`, `.preview-squad`, `.preview-squad-group`. |
| 4. Najlepsi strzelcy | [match_preview.py](../../../../domain/match_preview.py), [preview.html](preview.html), [admin.css](../../../static/css/admin.css) | `miejsca_strzelcow()`, `LICZBA_STRZELCOW`, `CzlonekKadry.miejsce_strzelca`; `.preview-scorer-row`, `.preview-scorer`, `.preview-squad td.top-scorer`. |
| 4. Data urodzenia i druk składów | [match_preview_repository.py](../../../../infrastructure/repositories/match_preview_repository.py), [preview.html](preview.html), [print_table.js](../../../static/js/print_table.js) | `pobierz_kadre()` (`data_urodzenia`), `CzlonekKadry.data_urodzenia`, `.preview-birth`; `div#kadra-druk`, `[data-print-section]`, `data-print-styles`; `DrukSekcjiController`, `WydrukSekcjiBuilder.htmlSekcji()` (style karty druku), `DopasowanieDoStrony` (skalowanie do jednej kartki A4, poziomo przy ukrytych uwagach); checkbox uwag: `[data-preview-notes-toggle]`, `.preview-hide-notes`, `UwagiKadryController`. |
| 4. Poprzedni sezon i uwagi | [schedule_presenter.py](../../../presenters/schedule_presenter.py), [preview.html](preview.html), [admin.css](../../../static/css/admin.css) | `_zawodnik()` (`poprzedni`, `poprzedni_mecze`, `uwagi_poprzednie`), `_mecze()`, `_bramki_klubu()`; domena: `poprzednie_sezony()`, `_inne_kluby()`; `.preview-prev`, `.preview-prev-note`, `.preview-prev-other`. |
| 4, 7. Opcje | [schedule_filters.py](../../../admin/forms/schedule_filters.py), [preview.html](preview.html), [match_preview.js](../../../static/js/match_preview.js) | `ZapowiedzOpcjeForm`, `LATA_BEZPOSREDNICH`; `form#preview-options`, `[data-preview-auto]`, `[data-preview-apply]`, `.preview-options`; `OpcjeZapowiedziController`. |
| 5. Forma | [match_preview.py](../../../../domain/match_preview.py), [preview.html](preview.html) | `DLUGOSC_FORMY`, `seria()`; makro `tabela_wystepow`, `.form-mark`. |
| 6. Porównanie | [schedule_presenter.py](../../../presenters/schedule_presenter.py), [match_preview.py](../../../../domain/match_preview.py) | `_porownanie()`, `StatystykiZapowiedziCalculator.profil()`, `Bilans`. |
| 7. Mecze bezpośrednie | [match_preview.py](../../../../domain/match_preview.py), [schedule_presenter.py](../../../presenters/schedule_presenter.py) | `bezposrednie()`, `poczatek_okresu()`, `OpcjeZapowiedzi.lata_bezposrednich`; `_bezposrednie()` (opis okresu). |
| 8. Prognoza | [match_prediction_service.py](../../../../services/match_prediction_service.py), [match_prediction_presenter.py](../../../presenters/match_prediction_presenter.py) | `PrognozaZapowiedziService`, `przygotuj_zapowiedz()`, `_kroki_prognozy()` (kroki wspólne z raportem). |
| Punkt odcięcia | [match_preview_service.py](../../../../services/match_preview_service.py) | `ZapowiedzMeczuService.pobierz()`, `ZegarWarszawa`. |
| Wygląd | [admin.css](../../../static/css/admin.css) | `.preview-*`, `.form-*`; KPI i kroki z `.prediction-*`. |
