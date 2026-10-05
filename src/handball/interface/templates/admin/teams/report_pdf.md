# Raport drużyny — PDF A4

Status: wdrożony 2026-10-05 na polecenie użytkownika („zrób dwa takie same wydruki w handball_datascience … tam nie masz skuteczności bramkarzy, dostosuj pod tamte dane”). Wzorem był raport drużyny z projektu EHF; tu bez narodowości i statystyk bramkarzy, których protokoły ZPRP nie zawierają, za to z rzutami karnymi i karami zawodników.

Jedna kartka A4 w pionie. Samodzielny dokument HTML bez skryptów, zamieniany na PDF przez WeasyPrint. Trasa `GET /administracja/druzyny/<id_zespol>/raport?id_sezon=<id>&mecze=<5–30>`, endpoint `administracja.raport_druzyny_pdf`, widok `RaportDruzynyPdfView` ([team_report_views.py](../../../admin/views/team_report_views.py)), formularz `RaportDruzynyForm` ([team_report_filters.py](../../../admin/forms/team_report_filters.py)). Brak `id_sezon`, sezon bez wpisu drużyny w `zespoly_sezony` albo `mecze` poza 5–30 → 400; nieznana drużyna → 404; brak Pango → 503. Plik `raport-druzyny-<id>-<id_sezon>.pdf` (inline). Arkusz: [team_report_pdf.css](../../../static/css/team_report_pdf.css) (wspólny z [season_sheets_pdf.md](season_sheets_pdf.md)).

## Zawartość

- **Nagłówek:** nazwa drużyny w sezonie, płeć, kategoria, miasto, rozgrywki sezonu, sezon i data „stan na”.
- **Pasek liczb:** mecze rozegrane, W–R–P, bramki z różnicą, średnie zdobytych i straconych, najlepszy strzelec sezonu, wyniki 5 ostatnich meczów.
- **1 Sezony:** do 5 sezonów do wybranego włącznie (`LICZBA_SEZONOW`), bilans jak na karcie drużyny (`SzczegolyDruzynyPresenter.przygotuj_sezony`). Wiersze rozgrywek tylko dla wybranego sezonu; wybrany sezon zacieniowany.
- **2 Kadra:** grupy pozycji (bramkarze, rozgrywający, skrzydłowi, obrotowi, inne, nieznana), w grupie według najniższego numeru, potem nazwiska (`KolejnoscZawodnikowRaportuPolicy`). Kolumny: Nr, zawodnik, rocznik, pozycja (B/R/S/O), w sezonie M, Br, Śr, karne trafione/wszystkie i %, 2′, U, D; w poprzednim sezonie M, Br, Śr oraz klub i rozgrywki: „ten sam klub”, „ten sam klub · <inne rozgrywki>”, „<klub> · <rozgrywki>” (kursywa, gdy zawodnik nie grał w tym klubie) albo „brak meczów”. Drużyna bez protokołów w sezonie dostaje skład zgłoszony (`sklady`) z dopiskiem w nagłówku sekcji.
- **3 Ostatnie mecze:** domyślnie 15 (`DOMYSLNA_LICZBA_MECZOW`) rozegranych meczów i walkowerów do wybranego sezonu włącznie, od najnowszego: data, rozgrywki, D/W, przeciwnik, wynik drużyny (z oznaczeniem remisu rozstrzygniętego dogrywką `d` lub karnymi `k`), W/R/P, rzuty karne drużyny, kary 2 min drużyny, widzowie, trzej najlepsi strzelcy. Wiersze w odcieniach szarości: wygrana szara, remis jasnoszara, porażka biała; linia oddziela sezony.

Wyróżnienia (pogrubienie na jasnoszarym tle, czytelne w druku czarno-białym; `MiejscaPolicy`, miejsca ex aequo): 3 najlepszych strzelców sezonu, 3 najskuteczniejszych z rzutów karnych (min. 5 prób) i 3 najlepszych strzelców poprzedniego sezonu.

## Dopasowanie do jednej kartki

`UkladRaportuPolicy` ([team_report_presenter.py](../../../presenters/team_report_presenter.py)) dzieli 205 mm na wszystkie wiersze (sezony, zawodnicy, nagłówki grup, mecze), odejmuje 0,7 mm na obramowanie i marginesy komórki i ogranicza wynik do 2,6–4,4 mm; czcionka to 1,8 × wysokość w pt, najwyżej 7,4 pt. Wartości trafiają do `<style>` w nagłówku szablonu. Sprawdzono na bazie (tylko odczyt): ORLEN Wisła Płock 2025/2026 — 8 wierszy sezonów, 24 zawodników, 15 meczów, jedna strona z zapasem ok. 3,5 mm.

## Dane wejściowe

`raport`: `RaportDruzynyViewModel` ([team_report.py](../../../view_models/team_report.py)) z `RaportDruzynyPresenter.przygotuj_raport()`: `druzyna`, `opis`, `sezon`, `poprzedni_sezon`, `rozgrywki`, `stan_na`, `liczby` (`LiczbaRaportuViewModel`), `sezony` (`WierszSezonuDruzynyViewModel`), `zawodnicy` (`ZawodnikRaportuViewModel` z `PoprzedniSezonViewModel`), `ze_skladu`, `mecze` (`MeczRaportuViewModel`), `uklad` (`UkladRaportuViewModel`).

## Powiązania

`RaportDruzynyPdfView` → `ZaleznosciZadaniaFactory.utworz_serwis_raportu_druzyny()` → `RaportDruzynyService.pobierz_raport()` ([team_report_service.py](../../../../services/team_report_service.py)). Serwis czyta `SzczegolyDruzynyReadRepository` (szczegóły, wszystkie mecze, zawodnicy sezonu ze statystykami karnych i kar, wpisy zestawień do strzelców meczów) i wąski kontrakt `KadraRaportuReadRepository` ([team_report_repository.py](../../../../contracts/team_report_repository.py)), który spełnia istniejący `ZapowiedzMeczuSQLAlchemyRepository` (numery, pozycja, data urodzenia, skład zgłoszony, poprzedni sezon i występy w innych klubach). Bilanse liczy `BilansDruzynyCalculator`, wyniki `WystepDruzynyPolicy`. Domena: [team_report.py](../../../../domain/team_report.py). PDF: `PdfResponseBuilder` → `DokumentPdfRenderer`.

Wejścia: przycisk „Raport drużyny (PDF)” w pasku karty drużyny ([detail.md](detail.md)) dla sezonu z zakładki Zestawienie sezonu oraz lista Raporty › Raporty drużyn ([../reports/teams.md](../reports/teams.md)).

## Sprawdzenie zmiany

- `tests/interface/test_team_reports.py`: PDF, nazwa pliku, arkusz, brak skryptów, kadra z rocznikiem i grupami, poprzedni sezon (ten sam klub, inny klub), ostatnie mecze ze strzelcami, 400/404/503.
- `tests/unit/test_team_report_service.py`: łączenie kadry ze statystykami, skład zgłoszony, sezony do wybranego, limit i kolejność meczów, błędny sezon.
- `tests/unit/test_team_report_presenter.py`: miejsca ex aequo, kolejność zawodników, granice układu, skróty pozycji.

## Układ tekstowy i mapa zmian

```text
RAPORT DRUŻYNY                                                         2025/2026
ORLEN Wisła Płock                                     protokoły ZPRP · stan na …
Mężczyźni · Senior · Płock · rozgrywki
────────────────────────────────────────────────────────────────────────────────
MECZE | W – R – P | BRAMKI ±różn. | ŚREDNIO | NAJLEPSZY STRZELEC | OSTATNIE 5
(1) Sezony   Sezon | Rozgrywki | M W R P %zw. | Bramki Różn. Śr Śr | Remisy rozstrz. | Widzowie
(2) Kadra            ┌──────── 2025/2026 ────────┐   ┌──── 2024/2025 ────┐
    Nr | Zawodnik | Ur. | Poz. | M Br Śr Karne % 2′ U D ‖ M Br Śr | Klub · rozgrywki
    BRAMKARZE / ROZGRYWAJĄCY / SKRZYDŁOWI / OBROTOWI (wiersze grup)
(3) Ostatnie mecze (15)
    Data | Rozgrywki | D/W | Przeciwnik | Wynik | (W)(R)(P) | Karne | 2′ | Widzowie | Najlepsi strzelcy
    wiersze: szare = wygrana, jasnoszare = remis, białe = porażka
legendy pod sekcjami 2 i 3
```

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Rozmiar strony, marginesy, czcionka | [team_report_pdf.css](../../../static/css/team_report_pdf.css) | `@page`, `html`. |
| Nagłówek i pasek liczb | [report_pdf.html](report_pdf.html), [team_report_pdf.css](../../../static/css/team_report_pdf.css), [team_report_presenter.py](../../../presenters/team_report_presenter.py) | `.masthead`, `table.kpis`; `_liczby()`. |
| Sezony | [report_pdf.html](report_pdf.html), [team_report_service.py](../../../../services/team_report_service.py) | `table.seasons`; `LICZBA_SEZONOW`; filtr wierszy w `przygotuj_raport()`. |
| Kadra i poprzedni sezon | [report_pdf.html](report_pdf.html), [team_report_presenter.py](../../../presenters/team_report_presenter.py), [team_report.py](../../../../domain/team_report.py) | `table.players`, `.group`, `.where.moved`; `_zawodnicy()`, `_zawodnik()`, `_poprzedni()`, `GRUPY_POZYCJI`; `KolejnoscZawodnikowRaportuPolicy`. |
| Wyróżnienia | [team_report_presenter.py](../../../presenters/team_report_presenter.py), [team_report_pdf.css](../../../static/css/team_report_pdf.css) | `NAJLEPSZYCH_STRZELCOW`, `NAJLEPSZYCH_KARNYCH`, `NAJMNIEJ_KARNYCH`, `MiejscaPolicy`; `.hl`. |
| Ostatnie mecze | [report_pdf.html](report_pdf.html), [team_report_service.py](../../../../services/team_report_service.py), [team_report_presenter.py](../../../presenters/team_report_presenter.py) | `table.matches`, `.res-row-*`, `.res`; `_ostatnie_mecze()`, `_mecz()`, `STRZELCOW_MECZU`; `_mecze()`. |
| Wysokość wierszy | [team_report_presenter.py](../../../presenters/team_report_presenter.py), [report_pdf.html](report_pdf.html) | `UkladRaportuPolicy`; `<style>` w `head`. |
