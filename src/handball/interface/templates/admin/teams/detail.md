# Karta drużyny

Status: zaimplementowany szablon [detail.html](detail.html), trasa `GET /administracja/druzyny/<id_zespol>`. Lista drużyn ([list.html](list.html)) ma przy każdym wierszu przycisk „▣ Szczegóły”, otwierający kartę w nowej karcie przeglądarki. Modal na liście, taki jak przy meczach i zawodnikach, nie jest jeszcze zrobiony.

## Przeznaczenie i powiązania

Karta opisuje drużynę jako `zespoly.id`, czyli tożsamość przez wszystkie sezony. Historyczne nazwy, miasta i statusy pochodzą z migawek `zespoly_sezony`. Zakładki, w kolejności: Dane podstawowe, Sezony, Mecze, Zawodnicy, Zestawienie sezonu, Podsumowanie, Forma i regularność. Domyślna jest pierwsza. Parametry filtrów meczów (`id_sezon`, `rozgrywki`, `przeciwnik`, `strona`, `sortowanie`) bez parametru `zakladka` otwierają Mecze. Parametry zawodników (`zawodnik`, `strona_zawodnikow`, `sortowanie_zawodnikow`) otwierają Zawodników, a parametry zestawienia (`sezon_zestawienia`, `rozgrywki_zestawienia`, `przeciwnik_zestawienia`) — Zestawienie sezonu. Parametr `zakonczone` też otwiera Mecze.

Przepływ: `DruzynaSzczegolyView` → `SzczegolyDruzynyService` i `AnalitykaDruzynyService` → `SzczegolyDruzynySQLAlchemyRepository`, następnie `SzczegolyDruzynyPresenter` → modele widoku → szablon. Zależności składa `ZaleznosciZadaniaFactory` (`utworz_serwis_szczegolow_druzyny()`, `utworz_analityke_druzyny()`, `utworz_presenter_szczegolow_druzyny()`). Brak drużyny daje 404, błąd odczytu 503, a niepoprawny parametr filtru 400. Strona dziedziczy `base.html` i podświetla sekcję `druzyny`.

## Zasady danych

- **Strona drużyny w meczu:** kolumna `mecze.id_zespol_gosp` albo `id_zespol_gosc` równa `id_zespol`. Wynik tej kolumny (`wynik_gosp_full`/`wynik_gosc_full`) to bramki drużyny; `zamiana` przestawia razem nazwy i wyniki, więc nie zmienia tego powiązania.
- **Miejsce (u siebie / na wyjeździe):** kolumna gospodarza bez `zamiana` albo kolumna gościa z `zamiana=true` oznacza mecz u siebie. W pozostałych przypadkach drużyna gra na wyjeździe. Reguła jest w `WystepDruzynyPolicy`.
- **Rozegrany mecz:** `MeczPolicy.status()` = rozegrany, czyli oba pełne wyniki, bez wycofania i walkowera. Tylko takie mecze mają bramki i rezultat. Walkowery, wycofane i mecze bez wyniku są liczone osobno („Pozostałe mecze”).
- **Zwycięstwo, remis, porażka** wynikają z pełnego wyniku, zgodnie z [PLAYER_DATA_SCIENCE](../../../../../../docs/PLAYER_DATA_SCIENCE.md). Remis z pełnego wyniku ma osobne rozstrzygnięcie: najpierw dogrywka (`dogrywka_2_full_*`, a bez niej `dogrywka_1_full_*`), potem seria karnych (`dogrywka_karne_*`). Rozstrzygnięcia nie zmieniają liczby remisów.
- **Bramki w analizach:** pełny wynik drużyny, bez dogrywki i serii karnych. Kolumna `zwyciezca` nie jest używana. Na bazie jest zgodna z wynikiem, ale jej semantyka nie jest udokumentowana.
- **Zawodnicy:** wpisy `mecze_zawodnicy`, których strona wskazuje tę drużynę po uwzględnieniu `zamiana` (`StronyMeczuSql.zespol(strona) == id_zespol`; przy zamianie `gosp` to kolumna gościa), agregowane po `id_zawodnik`. Mecze to różne `id_mecz`. Bramki i kary to sumy znanych wartości. Średnia = bramki / mecze ze znaną liczbą bramek. Imię i nazwisko pochodzą z `zawodnicy`, a przy braku z wpisu meczowego.
- **Hale:** najczęstsze hale meczów, w których drużyna jest gospodarzem po `zamiana` (maks. 5), ze średnią `mecze.widzowie` z meczów w tej hali ze znaną frekwencją.
- **Frekwencja:** `mecze.widzowie` z rozegranych meczów, osobno u siebie (miejsce po `zamiana`) i na wyjeździe. 0 to mecz bez publiczności i wchodzi do średniej; `NULL` to brak danych i nie wchodzi. Liczone są średnia, mediana, suma, rekord (mecz z największą liczbą widzów) i pokrycie (mecze ze znaną frekwencją / rozegrane). Reguły są w `FrekwencjaDruzynyCalculator`; wynik jest częścią każdego `BilansDruzyny`. Dane o widzach są w bazie od sezonu 2011/2012, a w 2020/2021 większość meczów ma 0 (mecze bez publiczności).
- **Miasto** w danych podstawowych to najnowsza niepusta wartość `zespoly_sezony.miasto`. Tabela `zespoly` nie ma kolumny miasta; wcześniejsze mapowanie ORM `Zespol.miasto` było błędne i zostało zastąpione rzeczywistą kolumną `nr_klubu`.

## Dane wejściowe szablonu

- `szczegoly: SzczegolyDruzynyViewModel`: nazwa, numer klubu, płeć, kategoria, miasto, status, liczba i zakres sezonów, liczba meczów, `nazwy` (kolejne okresy tej samej nazwy), `sezony` (z `id_zespol_sezon` do linku składu), `hale`.
- `frekwencja: FrekwencjaDruzynyViewModel`: frekwencja z całej historii (Dane podstawowe), z `HistoriaDruzyny.bilans`. `frekwencja_meczow`: to samo dla zakresu filtrów Meczów (sezon, rozgrywki, przeciwnik), z bilansu analityki. Oba mają `dom`/`wyjazd` (`FrekwencjaMiejscaViewModel`: średnia, mediana, suma, pokrycie, rekord z id meczu i opisem) oraz `ma_dane`.
- `sezony: list[WierszSezonuDruzynyViewModel]`: wiersz sezonu (`podsumowanie_sezonu=True`), a przy kilku rozgrywkach również ich wiersze. Każdy ma `BilansViewModel`.
- `strona: StronaMeczowDruzynyViewModel`: mecze z modelem listy meczów, miejscem, przeciwnikiem, wynikiem drużyny, rezultatem, klasą odznaki i rozstrzygnięciem.
- `zawodnicy: StronaZawodnikowDruzynyViewModel`: nazwa, mecze, bramki, średnia, karne, kary, zakres sezonów i ostatni mecz.
- `podsumowanie: PodsumowanieDruzynyViewModel`: bilans, serie zwycięstw, cztery `rekordy` (najwyższe zwycięstwo, najwyższa porażka, najwięcej zdobytych, najwięcej straconych) i `bilanse_sezonow` (Z/R/P, sumy oraz średnie zdobytych/straconych i różnica na mecz).
- `bramki: AnalizaBramekDruzynyViewModel`: bramki zdobyte i stracone razem. `miary` i `grupy` (Poziom, Zakres, Rozrzut) to wiersze `MiaraBramekDruzynyViewModel` z kolumnami zdobyte, stracone i różnica. `sezony` łączy dla każdego sezonu i rozgrywek statystyki obu serii. `rozklad` podaje liczbę meczów z daną liczbą zdobytych i straconych bramek, w podziale na wszystkie, u siebie i na wyjeździe. `mecze` ma klucze `wszystkie`/`dom`/`wyjazd` z punktami (wynik, obie serie, różnica, okna kroczące), medianami i progami trendu. `rozstepy` to pary pudełek sezonów.
- `filtry`, `filtry_zawodnikow`, `formularz: DruzynaFilterForm`, `aktywna_zakladka`, `parametry_meczow`, `parametry_zawodnikow`.

Opcje sezonów ograniczają się do sezonów drużyny, a opcje rozgrywek do rozgrywek jej meczów (`pobierz_opcje_filtrow()`). Sezon i rozgrywki są wspólne dla zakładek. Przeciwnik działa w Meczach, Podsumowaniu i Formie; wyszukiwanie zawodnika tylko w Zawodnikach. Przeciwnik jest dopasowywany do dowolnej historycznej nazwy w `zespoly_sezony`.

## Zakładki

- **Dane podstawowe:** kafelki (sezony, zakres, mecze, liczba nazw), sekcja „Frekwencja w całej historii” (10 kafelków: średnia, mediana, suma, rekord z linkiem do meczu i pokrycie, u siebie i na wyjeździe), siatka pól drużyny, historia nazw, najczęstsze hale (link do karty hali, średnia widzów), wpisy sezonowe z linkiem do szczegółów składu.
- **Sezony:** bez filtrów, pełna historia w kolejności sezonów karty (od najnowszego). Kolumny: M, Z, R, P, % zwycięstw, bramki, różnica, średnie, remisy rozstrzygnięte, pozostałe mecze, średnia widzów u siebie i na wyjeździe oraz suma widzów u siebie. Nagłówki są skrócone (np. „Śr. zdob.”, „Remisy rozstrz.”, „Inne mecze”, „Widzowie dom śr.”), pełna nazwa jest w podpowiedzi `title`, a nagłówki, rozgrywki, nazwy i kolumny notatek zawijają się (`.team-season-table thead th`, `.team-note-cell`), żeby tabela mieściła się bez przewijania przy 1440 px.
- **Mecze:** filtry z checkboxem „Tylko zakończone” (domyślnie zaznaczony, para checkbox + ukryte `zakonczone=0`, jak na liście meczów; warunek `WarunkiMeczuSql.zakonczony()`: termin przed dzisiejszym dniem w Europe/Warsaw albo wpisany wynik; dotyczy tylko listy meczów, nie frekwencji ani analiz), sekcja „Frekwencja w wybranym zakresie” (te same kafelki co w Danych podstawowych, liczone z meczów spełniających filtry), sortowanie po dacie, paginacja `strona`, kolumna Widzowie. Wynik drużyny zdobyte:stracone, odznaka rezultatu (`.badge.ok`, `.plan`, `.loss`, `.warn`), wynik meczu gospodarz–gość.
- **Zawodnicy:** filtry sezonu, rozgrywek, zawodnika i sortowania. Nagłówki Zawodnik, Mecze, Bramki, Średnia i Ostatni mecz sortują. Paginacja przez `strona_zawodnikow`, niezależna od paginacji meczów. Kliknięcie imienia i nazwiska otwiera szczegóły zawodnika w oknie modalnym, a dwuklik — kartę w nowej karcie.
- **Zestawienie sezonu:** filtr sezonu jest wymagany: lista ma tylko sezony drużyny, bez „Wszystkie”, a domyślnie wybrany jest najnowszy. Pozostałe filtry to rozgrywki i przeciwnik. Tabela ma zawodników w wierszach i mecze w kolumnach, chronologicznie. Pomijane są mecze bez żadnego wpisu drużyny w protokole.
  - Nagłówek meczu: data i przeciwnik pionowo, pod nimi D/W (u siebie / wyjazd) i wynik drużyny z kolorem rezultatu; kliknięcie otwiera mecz.
  - Komórka: bramki (pogrubione), kary (`n×2′`, `U`, `D`) i karne wykorzystane/wszystkie (`karne_bramki`/`karne_liczba`). Brak wpisu to pole kreskowane, „—” to wpis bez liczby bramek.
  - Na końcu grupa „Podsumowanie sezonu”: Mecze, Bramki, Kary, Karne (wyk./wsz.). W stopce „Suma drużyny” dla każdego meczu i całego sezonu.
  - Zawodnik: link do okna ze szczegółami (klik) i nowej karty (dwuklik), numery koszulek, pozycje po przecinku (najczęstsza pierwsza), zawijane.
  - Kolejność wierszy: najczęstsza pozycja według `KolejnoscPozycjiPolicy` (Bramkarz, Rozgrywający, Skrzydłowy, Obrotowy, inne, brak), potem bramki malejąco i nazwisko.
  - Tabela nie ma własnego przewijania pionowego, tylko poziome; kolumna zawodnika jest przyklejona do lewej krawędzi.
- **Podsumowanie:** 12 kafelków bilansu, cztery rekordy z linkiem do meczu i wykres skumulowany Z/R/P według sezonu. Pod nimi sekcja „Bramki zdobyte i stracone”:
  - tabela miar (zdobyte, stracone, różnica): średnia na mecz, mediana, dominanta, Q1–Q3, min–maks i mediany u siebie i na wyjeździe;
  - jeden wykres średniej, mediany i dominanty obu serii według sezonu (niebieskie zdobyte, czerwone stracone; linie, przerywane mediany, romby i trójkąty dominant; przełącznik Linie/Słupki; w okienku różnica średnich i podział na rozgrywki);
  - suma w sezonie: dwa stosy przy każdym sezonie (zdobyte i stracone z ukośnym wzorem), segmenty w kolorach rozgrywek, etykiety „Z …”/„S …” (przy co najwyżej 14 sezonach); ukrycie rozgrywek w legendzie przelicza sumy;
  - rozkład: dwa słupki na każdą liczbę bramek i przełącznik Wszystkie/U siebie/Na wyjeździe.
- **Forma i regularność:** spis treści z czterema sekcjami, każda dla obu serii naraz:
  1. Statystyki opisowe: trzy tabele (Poziom, Zakres, Rozrzut) z kolumnami zdobyte, stracone i różnica. Współczynnik zmienności różnicy nie jest liczony.
  2. Mecz po meczu: wykres zdobytych (ciągła linia z kółkami) i straconych (przerywana z kwadratami) z medianami oraz wykres bilansu (słupki różnicy, ujemne czerwone z wzorem, remis bursztynowy) ze średnią kroczącą różnicy z 5 meczów. Oba mają przełącznik miejsca, a kliknięcie otwiera mecz. Tabele danych są osobne dla wszystkich meczów, u siebie i na wyjeździe.
  3. Forma krocząca: średnia z 5 i mediana z 10 dla obu serii na tle wyników meczów, z liniami początku sezonów i przełącznikiem miejsca.
  4. Regularność według sezonu: dwa boxploty przy każdym sezonie (stracone przerywane) i punkty odstające. Punkty odstające są rysowane na środku kategorii sezonu, a nie dokładnie nad własnym pudełkiem.

  Grupa „Udziały meczów” z karty zawodnika jest pominięta, bo jej progi 0/1–2/3–5/6+ nie opisują wyników drużyn. Sekcji defensywy rywali nie ma, bo dotyczy zawodników.

Obie serie liczy ten sam `StatystykiBramekCalculator` na obiektach `BramkiMeczuDruzyny` (występ i wybrana wartość: zdobyte, stracone albo różnica), więc miary obu serii mają identyczne definicje. Okna kroczące każdej serii i miejsca są liczone niezależnie, a punkty serii są łączone po kolejności tych samych meczów. Przy #272 strona ma ok. 0,86 MB HTML.

## Wspólny kod z kartą zawodnika

Obliczenia statystyk bramek (`StatystykiBramekCalculator` w `services/goal_statistics.py`), typy (`domain/goal_statistics.py`), formatowanie (`StatystykiBramekPresenter`) są wspólne dla obu kart. Wykresy drużyny są własne (`team_details.js`), bo zestawiają dwie serie naraz. Z `goal_charts.js` biorą tylko ładowanie ECharts, escapowanie i formatowanie liczb. Karta korzysta ze stylów analitycznych `.player-kpi-grid`, `.player-chart*`, `.player-toc*` i `.player-section*`. Nowe style mają prefiks `.team-`. `team_details.js` udostępnia `globalThis.HandballDruzyna.ZakladkiDruzynyController`, którego używa okno karty drużyny w szczegółach tabeli ([../standings/detail.md](../standings/detail.md)); w oknie usuwany jest `[data-team-navigation]`.

## Weryfikacja

`tests/unit/test_team_detail_service.py`: strona i miejsce przy `zamiana`, remis rozstrzygnięty karnymi i dogrywką, walkower i brak wyniku, bilans, kolejność sezonów, podsumowanie tylko z rozegranych meczów, serie zdobytych, straconych i różnicy (miary, mediany według miejsca, forma, sezony), filtr rozgrywek. `tests/interface/test_team_details.py`: sześć zakładek, 404/400, bilans sezonów, mecze z perspektywy drużyny z escapowaniem, osobna paginacja i sortowanie zawodników, atrybuty wykresów, przełączenie na Mecze po filtrze, link z listy. Test interfejsu sprawdza też tabele miar zdobyte/stracone/różnica z wartościami, atrybuty wszystkich wykresów, brak współczynnika zmienności różnicy i tabele danych według miejsca. `node --test tests/javascript/team_details.test.cjs`: zakładki z klawiaturą; miary sezonów obu serii (sześć serii, mała próba, dominanty, tooltip z różnicą i escapowaniem, tryb Słupki); sumy sezonów (dwa stosy, wzór straconych, etykiety Z/S, przeliczenie po ukryciu rozgrywek); rozkład z przełącznikiem miejsca; wykresy Formy (mecze z medianami i otwieraniem meczu, pusty zakres miejsca, bilans, forma krocząca z granicami sezonów, boxplot z odstającymi). Dane testowe są pamięciowe. Frekwencję sprawdzają testy kalkulatora (u siebie/na wyjeździe, 0 kontra brak danych, rekord, tylko rozegrane) i interfejsu (kafelki z separatorem tysięcy, rekord z linkiem, pokrycie, średnia hali, kolumny sezonów, zależność od filtrów). Wartości frekwencji #272 zgadzają się z bezpośrednim zapytaniem SQL (średnio 2120 u siebie, mediana 1850, suma 527 955, 249/266 meczów, rekord 8313). Na bazie `zprp` (READ ONLY) sprawdzono drużynę #272 we wszystkich zakładkach i w Edge headless przy 1440 px.

## Wydruki PDF

Pasek `[data-team-navigation]` ma przyciski „Raport drużyny (PDF)” i „Zestawienia sezonu (PDF)” (`[data-team-report]`, `[data-team-sheets]`), otwierane w nowej karcie dla sezonu z zakładki Zestawienie sezonu (`sezon_zestawienia`, domyślnie najnowszy). Opisy: [report_pdf.md](report_pdf.md), [season_sheets_pdf.md](season_sheets_pdf.md). Przyciski nie pokazują się, gdy drużyna nie ma żadnego sezonu.

## Układ tekstowy i mapa zmian

```text
[Start › Dane › Drużyny › Szczegóły]
[Nazwa drużyny]  Karta drużyny #ID · płeć · sezony A–B
[← Powrót do listy drużyn] [▤ Raport drużyny (PDF)] [☷ Zestawienia sezonu (PDF)]
[Dane podstawowe | Sezony | Mecze | Zawodnicy | Podsumowanie | Forma i regularność]

Dane podstawowe:
[Sezony][Zakres][Mecze][Nazwy]
Frekwencja w całej historii:
[Śr. u siebie][Mediana][Suma][Rekord →mecz][Pokrycie]
[Śr. na wyjeździe][Mediana][Suma][Rekord →mecz][Pokrycie]
[ID | Nr klubu | Nazwa | Płeć | Kategoria | Miasto | Status]
[Historia nazw            ] [Najczęstsze hale jako gospodarz + śr. widzów]
[Wpisy sezonowe: Sezon | Nazwa | Miasto | Kategoria | Status | ☰ Skład]

Sezony:
[Sezon | Rozgrywki | Nazwa | M Z R P | % | Bramki | Różnica | Śr. | Śr. | Rozstrz. | Inne | Widz. dom śr. | Widz. wyj. śr. | Widz. dom suma]
[2025/2026  Wszystkie rozgrywki (3) ...]            ← wiersz sezonu
[           ↳ Superliga ...]                       ← wiersz rozgrywek

Mecze:
[Sezon][Rozgrywki][Przeciwnik][Filtruj][Wyczyść]
Frekwencja w wybranym zakresie: [10 kafelków jak w Danych podstawowych]
[Data ▼ | Sezon/rozgrywki | Miejsce | Przeciwnik | Wynik drużyny | Rezultat | Wynik meczu | Widzowie | ◈]
[Wyniki 1–20 z N                                   « Poprzednia  Następna »]

Zawodnicy:
[Sezon][Rozgrywki][Zawodnik][Sortowanie][Filtruj][Wyczyść]
[# | Zawodnik▲▼ | Mecze▲▼ | Bramki▲▼ | Średnia▲▼ | Karne | Kary | Sezony | Ostatni mecz▲▼]
[paginacja strona_zawodnikow]

Zestawienie sezonu:
[Sezon (wymagany)][Rozgrywki][Przeciwnik][Pokaż][Wyczyść]
[Zawodnik | Pozycja | 30.08 Rywal (pionowo) D 26:26 | … | Podsumowanie sezonu: Mecze Bramki Kary Karne]
[Bramkarz …   | Bramkarz | 0            | … |  29  1  1×2′  —  ]
[Rozgrywający …| Rozgr.   | 9 / 1×2′ / 6/7 | … |  31 146 5×2′ U 84/99]
[Suma drużyny |          | 26 / 4×2′ U / 6/7 | … | sumy sezonu ]

Podsumowanie:
[filtry]  [12 kafelków bilansu]
[Najwyższe zwycięstwo][Najwyższa porażka][Najwięcej zdobytych][Najwięcej straconych]
[Z/R/P według sezonu — słupki skumulowane]
Bramki zdobyte i stracone:
[Miara | Zdobyte | Stracone | Różnica]
[Średnia/mediana/dominanta: zdobyte ■ i stracone ■ na jednym wykresie (Linie|Słupki)]
[Suma w sezonie: słupek Z | słupek S (wzór), segmenty = rozgrywki]
[Rozkład: zdobyte ■ / stracone ▨   (Wszystkie|U siebie|Na wyjeździe)]

Forma i regularność:
[filtry] [Spis treści: 1 2 3 4]
[1 Poziom | Zakres | Rozrzut — kolumny Zdobyte | Stracone | Różnica]
[2 Mecz po meczu: zdobyte — / stracone - - (miejsce)] [Bilans: słupki różnicy + śr. krocząca 5]
[3 Forma krocząca: śr. 5 i med. 10 obu serii (miejsce)]
[4 Boxploty sezonów: zdobyte ▭ stracone ┄]
```

| Element | Plik | Blok / selektor / dane |
| --- | --- | --- |
| Trasa i widok | [team_detail_views.py](../../../admin/views/team_detail_views.py), [admin/__init__.py](../../../admin/__init__.py) | `DruzynaSzczegolyView.get()`, `szczegoly_druzyny`, wybór zakładki z parametrów. |
| Filtry | [team_filters.py](../../../admin/forms/team_filters.py) | `DruzynaFilterForm`, `do_filtrow()`, `do_filtrow_zawodnikow()`, `ZAKLADKI_DRUZYNY`, `SORTOWANIA_ZAWODNIKOW`. |
| Domena i reguły | [team_details.py](../../../../domain/team_details.py) | `FiltryDruzyny`, `FiltryZawodnikowDruzyny`, `WystepDruzynyPolicy`, `RezultatMeczu`, `RozstrzygniecieRemisu`, `RodzajBramek`, `FrekwencjaMiejsca`, `FrekwencjaDruzyny`, `BilansDruzyny` (pole `frekwencja`), `WystepDruzyny.widzowie`, `HalaDruzyny.srednia_widzow`, `PodsumowanieDruzyny`, `BramkiMeczuDruzyny`, `SeriaBramekDruzyny`. |
| Zapytania | [team_detail_repository.py](../../../../infrastructure/repositories/team_detail_repository.py), [kontrakt](../../../../contracts/team_detail_repository.py) | `pobierz_szczegoly()`, `pobierz_opcje_filtrow()`, `pobierz_mecze()`, `pobierz_wszystkie_mecze()`, `pobierz_zawodnikow()`, `_zapytanie_meczow()`, `_zapytanie_zawodnikow()`. |
| Obliczenia | [team_detail_service.py](../../../../services/team_detail_service.py), [goal_statistics.py](../../../../services/goal_statistics.py) | `BilansDruzynyCalculator`, `AnalitykaDruzynyService.pobierz_historie()` → `HistoriaDruzyny(bilans, sezony)`, `FrekwencjaDruzynyCalculator`, `pobierz_analityke()` → `AnalitykaDruzyny(podsumowanie, zdobyte, stracone, roznica)`, `_seria()`, `_wartosc()`, `StatystykiBramekCalculator`. |
| Formatowanie | [team_detail_presenter.py](../../../presenters/team_detail_presenter.py), [view_models/team_details.py](../../../view_models/team_details.py) | `SzczegolyDruzynyPresenter`, `przygotuj_bilans()` (pola `widzowie_*`), `przygotuj_frekwencje()`, `przygotuj_podsumowanie()`, `przygotuj_analize_bramek()` (`_sezony_bramek()`, `_rozklad_bramek()`, `_mecze_bramek()`, `_rozstepy_bramek()`), `GRUPY_MIAR_FORMY`, `REZULTATY`, `ROZSTRZYGNIECIA`, `PLCIE`. |
| Dane podstawowe | [detail.html](detail.html) | `#team-panel-dane`, `.team-kpi-basic`, makro `kafelki_frekwencji()`, `.team-attendance`, `dl.team-fields`, `.team-basic-grid`, `.team-subpanel`, `.team-seasons-list`. |
| Sezony | [detail.html](detail.html) | `#team-panel-sezony`, `.team-season-table`, `.team-season-row`, `.team-competition-row`, makro `wiersz_bilansu`, `naglowek_bilansu`. |
| Mecze | [detail.html](detail.html) | `#team-panel-mecze`, `kafelki_frekwencji(frekwencja_meczow)`, `.team-matches-table` (kolumna Widzowie), `.badge.loss`, include paginacji z `parametry_meczow`. |
| Zestawienie sezonu | [detail.html](detail.html), [team_detail_service.py](../../../../services/team_detail_service.py), [team_details.py](../../../../domain/team_details.py) | `#team-panel-zestawienie`, `.team-sheet-filters`, `.team-sheet-table`, `.team-sheet-match`, `.team-sheet-vertical`, `.team-sheet-cell`, `.team-sheet-empty`, `.team-sheet-sum*`, makra `komorka_zestawienia()` i `suma_zestawienia()`; `DruzynaFilterForm.sezon_zestawienia`, `do_filtrow_zestawienia()`; `pobierz_zestawienie()` (repozytorium i `ZestawienieDruzynyService`), `FiltryZestawieniaDruzyny`, `WpisZestawienia`, `StatystykiZestawienia` (`karne_wszystkie`), `WierszZestawienia`, `KolejnoscPozycjiPolicy`; `przygotuj_zestawienie()`, `ZestawienieSezonuDruzynyViewModel`. |
| Okno zawodnika | [detail.html](detail.html), [player_details.js](../../../static/js/player_details.js) | `dialog[data-player-modal-dialog]`, `a[data-player-modal-link]` (Zawodnicy i Zestawienie), `LinkiZawodnikowController`, `OknoZawodnikaController`; skrypt `player_details.js` ładowany przed `team_details.js`. |
| Zawodnicy | [detail.html](detail.html), [pagination.html](../../partials/pagination.html) | `#team-panel-zawodnicy`, `.team-player-filters`, makro `sortowalny`, `.team-players-table`, `parametr_strony='strona_zawodnikow'`. |
| Podsumowanie | [detail.html](detail.html) | `#team-panel-podsumowanie`, makra `filtry_analizy`, `tabela_miar()`, `przelacznik_miejsca()`, `.team-records`, `.team-goals-block`, `.team-measures`, `data-team-results`, `data-team-season-means`, `data-team-means-toggle`, `data-team-season-sums`, `data-team-distribution`, `data-team-place-toggle="distribution"`, skrypty `data-team-results-data`, `data-team-seasons-data`, `data-team-distribution-data`. |
| Forma i regularność | [detail.html](detail.html) | `#team-panel-forma`, `sekcje_formy`, `naglowek_sekcji()`, `nav#team-forma-spis[data-team-toc]`, `.team-stat-groups`, `data-team-matches`, `data-team-balance`, `data-team-rolling`, `data-team-boxplot`, `data-team-place-toggle` (`matches`, `balance`, `rolling`), skrypty `data-team-matches-data`, `data-team-spread-data`. |
| Zakładki i wykresy drużyny | [team_details.js](../../../static/js/team_details.js) | `ZakladkiDruzynyController`, `WykresyBramekDruzynyController` (`narysuj()`, `przelacznik()`, `miejsce()`), `PodsumowanieDruzynyController` (`rysujBilans()`, `opcjeMiar()`, `rysujSumy()`, `serieSum()`, `opcjeRozkladu()`), `FormaDruzynyController` (`opcjeMeczow()`, `opcjeBilansu()`, `opcjeKroczacej()`, `rysujRozstep()`), `KOLOR_ZDOBYTE`, `KOLOR_STRACONE`, `WZOR_KRESKI`. |
| Wspólne narzędzia | [goal_charts.js](../../../static/js/goal_charts.js) | `HandballWykresyBramek.zaladujECharts`, `escapujHtml`, `formatujLiczbe`. |
| Style | [admin.css](../../../static/css/admin.css) | `.team-*`, `.badge.loss` oraz wspólne `.player-kpi-grid`, `.player-chart*`, `.player-toc*`, `.player-section*`, `.match-tabs`. |
| Link z listy | [list.html](list.html), [list.md](list.md) | przycisk „▣ Szczegóły” w kolumnie Akcje. |
