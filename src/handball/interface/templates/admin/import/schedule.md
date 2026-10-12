# Pobieranie meczów

Status: wdrożony 2026-10-12. Szablon `schedule.html` istnieje.

Docelowy szablon względem katalogu szablonów: `admin/import/schedule.html`. Trasa `GET /administracja/import/mecze`, endpoint `administracja.pobieranie_meczow`, widok `PobieranieMeczowView` ([import_schedule_views.py](../../../admin/views/import_schedule_views.py)).

## Przeznaczenie

Lista meczów do pobrania z ZPRP, osobna od [Terminarza](../schedule/list.md). Zaznaczenie wysyła POST na import (`akcja=rozpocznij_mecze`, `mecze`). Zapis do bazy następuje dopiero po zatwierdzeniu podglądu w [panelu importu](panel.md). Dostęp jak przy imporcie: hasło `HDS_IMPORT_PASSWORD`, HTTP Basic `admin`, brak hasła → 503 (ekran panelu), złe logowanie → 401.

## Filtry

| Oznaczenie | Pole | Działanie |
| --- | --- | --- |
| F1 | Sezon `id_sezon` | Jak w terminarzu; bez parametru najnowszy sezon. |
| F2 | Rozgrywki `id_rozgrywki` | Opcja „Wszystkie”. Bez rozgrywek i bez filtra raportu strona prosi o wybór. |
| F3 | Runda `id_runda` | „Wszystkie”. |
| F4 | Kolejka `id_kolejka` | „Wszystkie”. |
| F5 | Tylko mecze bez wyników `bez_wynikow=y` | Mecz zaplanowany: brak obu wyników pełnych, nie jest wycofany ani walkowerem. |
| F6 | Wynik bez danych `wynik_bez_danych=y` | Mecz z oboma wynikami pełnymi, nie wycofany i nie walkower, któremu brakuje składu gospodarza albo gościa albo strona z bramkami nie ma zawodnika z bramkami. |
| F7 | Kolejki zakończone `kolejki_zakonczone=y` | Kolejka, w której żaden mecz nie jest zaplanowany. |
| F8 | Poziom `grupa` (wiele) | `superliga` (także Ekstraklasa i baraż o Superligę), `liga_centralna`, `i_liga`, `ii_liga`, `puchar_polski` (bez Superpucharu). Zaznaczone poziomy łączą się. |

Bez rozgrywek F5–F8 obejmują cały sezon; nazwa rozgrywek jest dopisywana do etykiety rundy. Z zakończonymi kolejkami najpierw odpadają niedokończone kolejki (liczone z meczów wybranego poziomu), potem zostają mecze pasujące do F5 albo F6. Kaskada pól jest w [schedule.js](../../../static/js/schedule.js) (`data-schedule-filters`).

## Zaznaczenie

`Zaznacz wszystko`, `Odznacz wszystko`, `Zaznacz kolejkę` i licznik są w [import_pobieranie.js](../../../static/js/import_pobieranie.js) (`[data-import-z-terminarza]`). Pusta lista i więcej niż `limit_meczow` (80) blokują wysłanie. Wiersz nie otwiera zapowiedzi; „Szczegóły” prowadzi do karty meczu.

## Dane wejściowe

- `opcje`: `OpcjeTerminarza`.
- `terminarz`: `TerminarzViewModel | None`. `None` — prośba o wybór (`data-schedule-prompt`). Puste rundy — `data-schedule-empty`.
- `bez_wynikow`, `wynik_bez_danych`, `kolejki_zakonczone`: stan checkboxów.
- `poziomy`, `wybrane_grupy`: etykiety poziomów i zaznaczone `GrupaRozgrywek`.
- `csrf_importu`, `limit_meczow`: tylko gdy lista ma mecze.
- `sekcja_aktywna="pobieranie_meczow"`, `sekcja_glowna="import"`.

## Powiązania

`PobieranieMeczowView` → `utworz_serwis_terminarza().pobierz_opcje()` oraz `utworz_serwis_pobierania_meczow().pobierz()` → `PobieranieMeczowService` ([import_schedule_service.py](../../../../services/import_schedule_service.py)) → `PobieranieMeczowReadRepository` i `TerminarzService.uloz()`. Zakres kolejek: `ZakresPobierania` w [schedule.py](../../../../domain/schedule.py). Formularz: `PobieranieMeczowFilterForm`.

## Sprawdzenie zmiany

Testy: `tests/unit/test_import_schedule_service.py`, `tests/interface/test_import_schedule.py`, `tests/javascript/import_pobieranie.test.cjs`. Publiczny terminarz nie zawiera `data-import-z-terminarza` (`tests/interface/test_schedule.py`).

## Układ tekstowy i mapa zmian

```text
Start › Import › Pobieranie meczów
H1 Pobieranie meczów
[Filtry]
  Sezon | Rozgrywki (Wszystkie) | Runda | Kolejka
  [ ] Tylko mecze bez wyników   [ ] Wynik bez danych   [ ] Kolejki zakończone
  Poziom: [ ] Superligi  [ ] Ligi centralne  [ ] I ligi  [ ] II ligi  [ ] Puchary Polski
  [Filtruj] [Wyczyść]
  notatka o znaczeniu filtrów
— albo prośba o wybór —
— albo „Brak meczów” —
— albo lista —
  Meczów na liście: N
  [Zaznacz wszystko] [Odznacz wszystko] [Pobierz zaznaczone]  Zaznaczono: 0
  Runda
    Kolejka
      [Zaznacz kolejkę]
      dzień
        [ ] godzina gospodarz wynik gość hala status [Szczegóły]
  [Pobierz zaznaczone]
```

| Element | Plik | Miejsce |
| --- | --- | --- |
| Filtry i raporty | [schedule.html](schedule.html), [import_schedule_filters.py](../../../admin/forms/import_schedule_filters.py) | `data-schedule-filters`, `bez_wynikow`, `wynik_bez_danych`, `kolejki_zakonczone`, `name="grupa"` |
| Kaskada sezon–kolejka | [schedule.js](../../../static/js/schedule.js) | `FiltryTerminarzaController` |
| Zaznaczenie | [import_pobieranie.js](../../../static/js/import_pobieranie.js) | `WyborMeczowDoPobrania`, `data-zaznacz`, `data-zaznacz-kolejke` |
| Lista i brak danych | [import_schedule_service.py](../../../../services/import_schedule_service.py), [import_schedule_repository.py](../../../../infrastructure/repositories/import_schedule_repository.py) | `pobierz()`, `_brak_danych_meczu()` |
| Kolejki zakończone | [schedule.py](../../../../domain/schedule.py) | `ZakresPobierania.zakonczone_kolejki()` |
| Wygląd paska | [admin.css](../../../static/css/admin.css) | `.schedule-import`, `.schedule-import-flags`, `.schedule-row-pick` |
