# Raporty drużyn

Status: wdrożona 2026-10-05 na polecenie użytkownika — wejście do wydruków drużyn w sekcji Raporty.

Lista drużyn w sezonach z odnośnikami do wydruków PDF. Trasa `GET /administracja/raporty/druzyny`, endpoint `administracja.raporty_druzyn`, widok `RaportyDruzynListView` ([team_report_views.py](../../../admin/views/team_report_views.py)) — podklasa `DruzynaListView`, więc filtry, sortowanie, stronicowanie i dane (`KatalogService.pobierz_druzyny()`) są takie jak na liście Drużyny ([../teams/list.md](../teams/list.md)). `sekcja_aktywna="raporty_druzyn"`, `sekcja_glowna="raporty"` (podświetla zakładkę Raporty i pozycję „Raporty drużyn” w sidebarze). Wpis w katalogu raportów: `KATALOG_RAPORTOW` ([report_catalog.py](../../../report_catalog.py)).

Każdy wiersz to drużyna w sezonie, z odnośnikami otwieranymi w nowej karcie:
- „Raport drużyny” → `administracja.raport_druzyny_pdf` z `id_sezon` wiersza ([../teams/report_pdf.md](../teams/report_pdf.md));
- „Zestawienia sezonu” → `administracja.zestawienia_druzyny_pdf` ([../teams/season_sheets_pdf.md](../teams/season_sheets_pdf.md));
- „Karta” → karta drużyny.

Sprawdzenie: `tests/interface/test_team_reports.py::test_lista_raportow_druzyn_ma_linki_do_wydrukow` oraz wpis w katalogu raportów.

## Układ tekstowy i mapa zmian

```text
Start › Raporty › Raporty drużyn
Raporty drużyn — opis wydruków
[Filtry] Szukaj | Sezon | Płeć | Miasto | Status | [Filtruj] [Wyczyść]
Sezon | Drużyna | Płeć | Miasto | Mecze | Wydruki PDF
2025/2026 | Wisła … | M | Płock | 34 | [▤ Raport drużyny] [☷ Zestawienia sezonu] [▣ Karta]
notka o zawartości wydruków · stronicowanie
```

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Filtry i sortowanie | [teams.html](teams.html), [catalog_views.py](../../../admin/views/catalog_views.py) | formularz `KatalogFilterForm`; `DruzynaListView.sortowanie`. |
| Odnośniki do wydruków | [teams.html](teams.html) | `[data-team-report]`, `[data-team-sheets]`. |
| Pozycja w menu i katalogu | [navigation.py](../../../navigation.py), [report_catalog.py](../../../report_catalog.py) | `PozycjaMenu("raporty_druzyn", …)`, `PozycjaRaportu("raporty_druzyn", …)`. |
