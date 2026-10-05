# Zestawienia sezonu — PDF A4 w poziomie

Status: wdrożony 2026-10-05 na polecenie użytkownika (wzór: wydruk „Season sheets” z projektu EHF, dostosowany do danych ZPRP — bez obron bramkarzy, z rzutami karnymi i karami U/D).

Dwie kartki A4 w poziomie: zestawienie wybranego sezonu i sezonu poprzedniego (`pobierz_poprzedni_sezon`). Gdy drużyna nie ma wpisu w poprzednim sezonie, jego strona zawiera tylko komunikat; gdy w bazie nie ma wcześniejszego sezonu, drukuje się jedna strona. Trasa `GET /administracja/druzyny/<id_zespol>/zestawienia?id_sezon=<id>`, endpoint `administracja.zestawienia_druzyny_pdf`, widok `ZestawieniaDruzynyPdfView` ([team_report_views.py](../../../admin/views/team_report_views.py)), formularz `RaportDruzynyForm`. Błędy jak w [report_pdf.md](report_pdf.md) (400/404/503). Plik `zestawienia-druzyny-<id>-<id_sezon>.pdf`. Arkusz: [team_report_pdf.css](../../../static/css/team_report_pdf.css) — strony `.sheet-page` mają nazwaną stronę `@page poziomo`.

## Zawartość strony

- Nagłówek: drużyna, „Zestawienie sezonu”, sezon i data „stan na” (na pierwszej stronie); pod nim rozgrywki, liczba meczów, W–R–P i bramki sezonu.
- Tabela jak zakładka Zestawienie sezonu karty drużyny (`ZestawienieDruzynyService`): zawodnicy w wierszach (grupy pozycji, w grupie według bramek), mecze w kolumnach. Kolumny zawodnika: numer, nazwisko i imię, rocznik (z kadry sezonu, a dla brakujących ze składu zgłoszonego), pozycja B/R/S/O.
- Nagłówek meczu: przeciwnik i data pionowo (`transform: rotate`, bo WeasyPrint nie obsługuje `writing-mode`), D/W, wynik w dwóch liniach — bramki drużyny nad bramkami rywala; podkreślenie oznacza wygraną.
- Komórka: bramki, kary w indeksie górnym (′ za każde 2 min, U, D), pod spodem rzuty karne trafione/wszystkie; najlepszy strzelec drużyny w meczu w ramce; brak w protokole — szare pole.
- Podsumowanie wiersza: M, Br, karne z %, kary. Wyróżnione (pogrubienie na szarym tle): 3 najlepszych strzelców i 3 najskuteczniejszych z rzutów karnych (min. 5 prób). Wiersz „Drużyna” z bramkami i karnymi w meczach.

## Dopasowanie do kartki

`UkladZestawieniaPolicy` dzieli 116 mm na wiersze zawodników i wiersz drużyny (3,3–6,0 mm) oraz 178 mm na kolumny meczów (najwyżej 13 mm na mecz); czcionka zależy od obu wymiarów (najwyżej 8 pt). Wartości trafiają do `<style>` osobno dla każdej strony (`#sheet-<n>`). Sprawdzono na bazie (tylko odczyt): ORLEN Wisła Płock 2025/2026 (34 mecze, 26 zawodników) i 2024/2025 (36 meczów, 28 zawodników) — po jednej stronie z legendą.

## Dane wejściowe

`zestawienia`: `ZestawieniaDruzynyViewModel` (`druzyna`, `stan_na`, `strony`) z `RaportDruzynyPresenter.przygotuj_zestawienia()`; strona `StronaZestawienViewModel`: `sezon`, `opis`, `brak`, `mecze` (`KolumnaZestawieniaRaportuViewModel`), `wiersze` (`WierszZestawieniaRaportuViewModel` z `KomorkaZestawieniaRaportuViewModel` i `SumaZestawieniaRaportuViewModel`), `sumy_meczow`, `suma`, `uklad`.

## Powiązania

`ZestawieniaDruzynyPdfView` → `RaportDruzynyService.pobierz_zestawienia()` → `ZestawienieDruzynyService.pobierz_zestawienie()` dla obu sezonów, `KadraRaportuReadRepository.pobierz_kadre()` / `pobierz_sklad_sezonu()` (roczniki), `BilansDruzynyCalculator` (opis strony). Wejścia: przycisk „Zestawienia sezonu (PDF)” na karcie drużyny i lista [../reports/teams.md](../reports/teams.md).

## Sprawdzenie zmiany

`tests/interface/test_team_reports.py` (dwie strony, rocznik, wyróżnienie, karne, komunikat dla sezonu bez wpisu) i `tests/unit/test_team_report_service.py` (sezony, roczniki); `UkladZestawieniaPolicy` w `tests/unit/test_team_report_presenter.py`.

## Układ tekstowy i mapa zmian

```text
ORLEN Wisła Płock               ZESTAWIENIE SEZONU               2025/2026 · stan na …
Zestawienie sezonu 2025/2026  rozgrywki · 34 meczów · 30–2–2 · bramki 1170:824
                        │rywal│rywal│ … (pionowo z datą)  │
Zawodnik      Ur.  Poz. │ D   │ W   │                      │ M │ Br │ Karne    │ Kary
                        │ 37  │ 32  │  wynik: drużyna /     │   │    │          │
                        │ 27  │ 21  │  rywal                │   │    │          │
 22 RICHARDSON M. 1997 R│ [9] │ 5′  │ …                     │31 │146 │84/99 85% │5×2′ 1U
                        │ 6/7 │ 1/1 │  karne pod bramkami   │   │    │          │
 … grupy: B / R / S / O, linia między grupami
Drużyna                 │ 26  │ 37  │                      │34 │1170│122/156   │134×2′ …
legenda
(druga strona: poprzedni sezon)
```

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Strona pozioma, marginesy | [team_report_pdf.css](../../../static/css/team_report_pdf.css) | `@page poziomo`, `.sheet-page`. |
| Nagłówek strony i opis sezonu | [season_sheets_pdf.html](season_sheets_pdf.html), [team_report_presenter.py](../../../presenters/team_report_presenter.py) | `.running`, `.section`; `_opis_strony()`. |
| Nagłówki meczów | [season_sheets_pdf.html](season_sheets_pdf.html), [team_report_pdf.css](../../../static/css/team_report_pdf.css) | `.vertical-box`, `.vertical`, `.sheet-score`, `.lost`. |
| Komórki i najlepszy strzelec meczu | [team_report_presenter.py](../../../presenters/team_report_presenter.py), [team_report_pdf.css](../../../static/css/team_report_pdf.css) | `_komorka()`, `_kary()`, `najlepsi_meczu` w `_strona()`; `.cell`, `.cell.best`, `.pk`, `.empty`. |
| Podsumowanie i wyróżnienia | [team_report_presenter.py](../../../presenters/team_report_presenter.py) | `_suma()`, `NAJLEPSZYCH_STRZELCOW`, `NAJLEPSZYCH_KARNYCH`, `NAJMNIEJ_KARNYCH`; `.sum.hl`. |
| Rocznik | [team_report_service.py](../../../../services/team_report_service.py) | `_strona_zestawien()` (kadra sezonu, potem skład zgłoszony). |
| Wymiary wierszy i kolumn | [team_report_presenter.py](../../../presenters/team_report_presenter.py), [season_sheets_pdf.html](season_sheets_pdf.html) | `UkladZestawieniaPolicy`; `<style>` z `#sheet-<n>`. |
