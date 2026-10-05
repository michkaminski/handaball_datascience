# Protokół zawodów do uzupełnienia — PDF A4

Status: wdrożony 2026-09-27 na polecenie użytkownika. Wzorem był protokół ZPRP meczu 206534 („nie chcę logo ZPRP, chcę tylko uzupełnioną tabelkę o dane, jakie mam … abym mógł sobie uzupełniać podczas meczu przebieg zawodów … te same sortowania”). Szablon `protocol_pdf.html` istnieje.

Jedna kartka A4 w pionie do ręcznego wypełniania podczas meczu. Samodzielny dokument HTML bez skryptów i linków, zamieniany na PDF przez WeasyPrint. Trasa `GET /administracja/terminarz/<id_mecz>/protokol`, endpoint `administracja.protokol_meczu_pdf`, widok `ProtokolMeczuPdfView` ([schedule_views.py](../../../admin/views/schedule_views.py)). Parametry opcji są takie jak w [zapowiedzi](preview.md) (`ZapowiedzOpcjeForm`): działa `kadra_poprzedni=y` oraz `kolejnosc_protokolu` = `pozycje` (domyślnie) albo `numery` (polecenie użytkownika z 2026-09-27); pozostałe pola są walidowane (np. `lata=7`, `kolejnosc_protokolu=x` → 400). Brak meczu → 404, brak Pango → 503. Plik: `protokol-meczu-<id>.pdf` (inline). Arkusz: [protocol_pdf.css](../../../static/css/protocol_pdf.css).

## Co jest uzupełnione, a co puste

- **Uzupełnione z bazy:**
  - drużyny A (gospodarz) i B (gość), z uwzględnieniem `zamiana`;
  - rozgrywki, sezon, runda i kolejka, data i godzina (godzina tylko przy `data_faktyczna`);
  - hala z adresem (`hale.nazwa`, `ulica`, `numer`, `miasto`) i pojemność;
  - obsada z `mecze_sedziowie`: dwaj sędziowie główni (`pierwszy`, `drugi`), `sekretarz`, `czas` (m. czas) i `delegat`, każdy z miejscowością. Brakujące role zostają pustymi wierszami.
- **Zawodnicy:** numer i „NAZWISKO Imię”, a za nazwiskiem (polecenie użytkownika z 2026-09-27) pięć wąskich kolumn na szarym tle: **P** — pozycja jedną literą (B bramkarz, R rozgrywający, S skrzydłowy, O obrotowy; inna lub nieznana — puste, `SKROTY_POZYCJI`), **Ur.** — rocznik dwiema cyframi, **M**, **Br**, **Śr** — mecze, bramki i średnia na mecz (jedno miejsce po przecinku) w sezonie meczu. Zawodnik dodany z poprzedniego sezonu, który w bieżącym nie grał, ma „–” w M, Br i Śr; zawodnik ze składu zgłoszonego — 0, 0 i „–”. Bramki czterech najlepszych strzelców drużyny w sezonie są pogrubione na ciemniejszym tle (`wyroznij_bramki`, `.stat-top`; `LICZBA_WYROZNIONYCH_STRZELCOW = 4`). Miejsca pochodzą z `KadraZapowiedziCalculator.miejsca_strzelcow()`, więc ex aequo dostaje to samo miejsce (np. 1, 1, 1, 4 — cztery osoby, 1, 2, 2, 4, 4 — pięć), a zera nie są wyróżniane. Legenda skrótów jest w stopce. Kolejność wybiera lista „kolejność” obok przycisku (`KolejnoscZawodnikowProtokoluPolicy` w [match_protocol.py](../../../../domain/match_protocol.py)):
  - `pozycje` („pozycja, numer”, domyślna) — grupy pozycji jak w kadrze zapowiedzi (bramkarze, rozgrywający, skrzydłowi, obrotowi, inne, nieznana), a w grupie według numeru koszulki rosnąco, potem nazwiska (bez numeru na końcu) — ta sama kolejność co w kadrze zapowiedzi; granicę grup zaznacza grubsza linia;
  - `numery` — według najniższego numeru koszulki rosnąco, bez granic grup; zawodnicy bez numeru na końcu, remisy według nazwiska.

   Lista obejmuje całą kadrę sezonu sprzed meczu, więc może mieć więcej niż 16 osób — niegrających skreśla się ręcznie. Drużyna bez protokołów w sezonie dostaje skład zgłoszony na sezon z `sklady` (zob. [preview.md](preview.md)); przy nazwie drużyny jest wtedy dopisek „(skład zgłoszony na sezon)” (`DruzynaProtokoluViewModel.ze_skladu`, `.source-note`), a stopka wspomina o tym źródle.
- **Puste pola:**
  - W, B, U, trzy 2', D i Kd;
  - osoby towarzyszące A–E i U;
  - wynik końcowy, do przerwy i na korzyść;
  - przebieg zawodów: time outy, 34 wiersze T / Zaw. A / wynik / Zaw. B dla każdej połowy;
  - rzuty karne, uwagi sędziów, liczba widzów, rejestracja, raport, podpisy, opieka medyczna i weryfikacja wyniku.
- **Pominięte** względem oryginału: wiersz tytułu „PROTOKÓŁ ZAWODÓW” z numerem meczu (usunięty na polecenie użytkownika 2026-09-27), logo i nazwa ZPRP w nagłówku, stopka Departamentu Rozgrywek, „Wygenerowano przez…” i identyfikator dokumentu. Checkboxy rodzaju zawodów zastępuje nazwa rozgrywek. Sztabu (`mecze_sztab`) nie wpisujemy, bo przed meczem jest pusty.

## Dopasowanie do jednej kartki

Kolumna drużyn zajmuje 63% szerokości (przebieg zawodów 37%); kolumny kar mają po 5,4 mm, statystyk 3,6–6,2 mm. `UkladProtokoluPolicy` ([match_protocol_presenter.py](../../../presenters/match_protocol_presenter.py)) dzieli 173 mm na wszystkich zawodników obu drużyn, odejmuje 0,2 mm na obramowanie i ogranicza wynik do przedziału 3,0–5,2 mm. Czcionka nazwisk to 1,6 × wysokość w pt, maksymalnie 8,5 pt. Wartości trafiają do `<style>` w nagłówku szablonu. Przebieg zawodów ma stałe 34 wiersze po 5,05 mm. Sprawdzono: 34 zawodników (mecz 206533) — wiersze 4,65 mm; 51 zawodników z poprzednim sezonem — 3,0 mm; w obu przypadkach jedna strona.

## Dane wejściowe

- `protokol`: `ProtokolMeczuViewModel` ([match_protocol.py](../../../view_models/match_protocol.py)) z `ProtokolMeczuPresenter.przygotuj()`: `gospodarz`, `gosc`, `rozgrywki`, `sezon`, `etap`, `data`, `godzina`, `hala`, `adres`, `pojemnosc`, `stan_na`, `druzyny` (`DruzynaProtokoluViewModel` → `ZawodnikProtokoluViewModel`: `numer`, `nazwa`, `nowa_grupa`, `pozycja`, `rocznik`, `mecze`, `bramki`, `srednia`, `wyroznij_bramki`), `sedziowie` (`SedziaProtokoluViewModel`: `funkcja`, `nazwisko`, `miasto`), `uklad`.

## Powiązania

`ProtokolMeczuPdfView` → `ZaleznosciZadaniaFactory.utworz_serwis_protokolu_meczu()` → `ProtokolMeczuService` ([match_protocol_service.py](../../../../services/match_protocol_service.py)). Serwis korzysta z `ZapowiedzMeczuReadRepository` (mecz, poprzedni sezon, kadry), z `KadraMeczuBuilder` — tej samej klasy co zapowiedź, więc sortowanie jest identyczne — oraz z `ProtokolMeczuReadRepository` ([kontrakt](../../../../contracts/match_protocol_repository.py), [SQLAlchemy](../../../../infrastructure/repositories/match_protocol_repository.py): `pobierz_dane_protokolu`). Nie liczy prognozy, więc odpowiada w ok. 2–2,5 s. Domena: [match_protocol.py](../../../../domain/match_protocol.py). PDF tworzy `PdfResponseBuilder` → `DokumentPdfRenderer` (zob. [preview_pdf.md](preview_pdf.md)). Przycisk „Protokół do uzupełnienia” (`[data-preview-protocol]`) na [preview.html](preview.html) wysyła formularz opcji do tej trasy w nowej karcie.

## Sprawdzenie zmiany

- `tests/interface/test_schedule.py`: przycisk; nagłówek z numerem, halą i pojemnością; kolejność zawodników (grupy pozycji, w grupie numery) i granice grup; kolumny P, Ur., M, Br, Śr i pogrubienie strzelców; brak kadry; kolejność i puste role obsady; brak ZPRP i skryptów; opcja `kadra_poprzedni`; 404/400/503.
- `tests/unit/test_match_protocol_presenter.py`: format nazw, granice grup, adres i obsada, granice układu.
- Na bazie (tylko odczyt) 2026-09-27: mecz 206533, obejrzany wydruk; mecz 207100 (I Liga Kobiet, pierwszy mecz gospodarza w sezonie) — gospodarz 22 zawodniczki ze składu zgłoszonego, gość 15 z protokołów, jedna strona.

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `protocol_pdf.html` (A4 pion, jedna strona).

```text
+----------------------+------------------+-----------------------------------+
| A Drużyna Gospodarzy:| Zawody:          | Miejsce rozgrywania zawodów:      |
|   WKS Śląsk Wrocław  | LOTTO Superliga  | Hala Orbita, Wejherowska 34, Wr.  |
| B Drużyna Gości:     | 2026/2027 · I r. | [  ]:[  ]  [  ]:[  ]  [      ]    |
|   COROTOP Gwardia    | data … godz. …   | wynik końc. do przerwy na korzyść |
+----------------------+------------------+-----------------------------------+
| A (nazwa) Śląsk                | Kary   | Przebieg zawodów                   |
| Nr | Nazwisko i imię | P Ur. M Br Śr | W B U 2' 2' 2' D Kd | [ ] I połowa [ ] | [ ] II połowa [ ] |
| 21 | MAŁECKI Patryk  | B 92 3 0 0.0 |  (puste)        | [ ] time out [ ] | [ ] time out  [ ] |
| …  (grupy pozycji, gruba linia)       | T|Zaw.A|wynik|Zaw.B | T|Zaw.A|wynik|Zaw.B |
| A osoba odp. | B | C | D | E | U      |  … 34 puste wiersze × 2 połowy …   |
| B (nazwa) Gwardia              | Kary   |                                     |
| … jak wyżej …                         | Rzuty karne: A liczba/bramki, B …   |
+---------------------------------------+-------------------------------------+
| Sędziowie: funkcja | nazwisko | miejscowość | … | podpis | Uwagi, widzowie, | Wynik końcowy [ ]:[ ] |
| sędzia główny ×2, sekretarz, m. czas, delegat ZPRP     | pojemność, rejestr.| Do przerwy, Na korzyść |
|                                                          |                    | Opieka medyczna        |
+----------------------------------------------------------------------------+
                                  Handball DataScience · zawody #… · kadry z …
```

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Rozmiar strony, marginesy, czcionka | [protocol_pdf.css](../../../static/css/protocol_pdf.css) | `@page`, `html`. |
| Nagłówek (drużyny, zawody, miejsce, wynik) | [protocol_pdf.html](protocol_pdf.html), [protocol_pdf.css](../../../static/css/protocol_pdf.css) | `table.head`, `.teams`, `.event`, `.place`, `table.score`. |
| Dane nagłówka i obsady | [match_protocol_repository.py](../../../../infrastructure/repositories/match_protocol_repository.py), [match_protocol_presenter.py](../../../presenters/match_protocol_presenter.py) | `pobierz_dane_protokolu()`; `_adres()`, `_sedziowie()`, `OBSADA_PROTOKOLU`. |
| Kolumny P, Ur., M, Br, Śr | [protocol_pdf.html](protocol_pdf.html), [protocol_pdf.css](../../../static/css/protocol_pdf.css), [match_protocol_presenter.py](../../../presenters/match_protocol_presenter.py) | `.stat`, `.stat-last`, `.stat-top`, `.c-pos`…`.c-avg`; `_zawodnik()`, `_pozycja()`, `SKROTY_POZYCJI`, `LICZBA_WYROZNIONYCH_STRZELCOW`; legenda w `.source`. |
| Tabele drużyn i kolejność zawodników | [protocol_pdf.html](protocol_pdf.html), [match_protocol_presenter.py](../../../presenters/match_protocol_presenter.py), [match_protocol.py](../../../../domain/match_protocol.py), [match_preview_service.py](../../../../services/match_preview_service.py), [schedule_filters.py](../../../admin/forms/schedule_filters.py) | `table.team-table`, `.player`, `.new-group`, `kary`; `_druzyna()`, `_zawodnik()`; `KolejnoscProtokolu`, `KolejnoscZawodnikowProtokoluPolicy`; `KadraMeczuBuilder`, `KadraZapowiedziCalculator`; `ZapowiedzOpcjeForm.kolejnosc_protokolu`. |
| Wysokość wierszy zawodników | [match_protocol_presenter.py](../../../presenters/match_protocol_presenter.py), [protocol_pdf.html](protocol_pdf.html) | `UkladProtokoluPolicy` (`MIEJSCE_ZAWODNIKOW_MM`, granice, `OBRAMOWANIE_WIERSZA_MM`); `<style>` w `head`. |
| Osoby towarzyszące | [protocol_pdf.html](protocol_pdf.html), [protocol_pdf.css](../../../static/css/protocol_pdf.css) | `.officials-grid`. |
| Przebieg zawodów i rzuty karne | [protocol_pdf.html](protocol_pdf.html), [protocol_pdf.css](../../../static/css/protocol_pdf.css), [match_protocol_presenter.py](../../../presenters/match_protocol_presenter.py) | `table.flow`, `.flow-row`, `.flow-score`, `table.penalty-shots`; `WIERSZE_PRZEBIEGU`. |
| Stopka (sędziowie, informacje, weryfikacja) | [protocol_pdf.html](protocol_pdf.html), [protocol_pdf.css](../../../static/css/protocol_pdf.css) | `table.foot`, `.referees` (`colgroup`), `.info`, `.verify`, `.medical`, `.source`. |
