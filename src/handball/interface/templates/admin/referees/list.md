# Sędziowie

Status: zaimplementowany szablon listy `admin/referees/list.html`.

## Przeznaczenie

Widok administracyjny `GET /administracja/sedziowie` pokazuje słownik sędziów i delegatów z `public.sedziowie` oraz liczbę różnych meczów powiązanych przez `public.mecze_sedziowie`.

## Dane wejściowe

Szablon dziedziczy `base.html` i otrzymuje:

- `sekcja_aktywna="sedziowie"`.
- `formularz`: `KatalogFilterForm` z polami `szukaj`, `miasto`, `sortowanie`, `strona`, `rozmiar_strony`.
- `filtry`: `FiltryKatalogu`.
- `strona`: `StronaKatalogu[PozycjaSedziego]`, gdzie pozycja ma `id`, `nazwisko`, `miasto`, `liczba_meczow`.

## Zachowanie

Filtr `szukaj` działa po nazwisku albo mieście. Filtr `miasto` zawęża po mieście. Sortowanie odbywa się przez nagłówki `ID`, `Nazwisko`, `Miasto` i `Mecze`, zgodnie ze wspólną konwencją list. Paginacja korzysta z `partials/pagination.html` i zachowuje parametry GET.

## Powiązania

- Trasa listy: `administracja.lista_sedziow`, `/administracja/sedziowie`.
- Szczegóły: `administracja.szczegoly_sedziego`, `/administracja/sedziowie/<id_sedzia>`; kontrakt: [detail.md](detail.md).
- Widok: `SedziaListView` w `interface/admin/views/catalog_views.py`.
- Serwis: `KatalogService.pobierz_sedziow()`.
- Repozytorium: `KatalogPodstawowySQLAlchemyRepository.pobierz_sedziow()`.
- Modele: `Sedzia` i `MeczSedzia` w `infrastructure/database/models/officials.py`.
- Nawigacja: `PozycjaMenu("sedziowie", "Sędziowie", "administracja.lista_sedziow", "⚑")` w `interface/navigation.py`.

## Gdzie wprowadzać zmiany

| Zmiana | Plik |
| --- | --- |
| Układ listy, kolumny i teksty | `list.html` oraz ten `list.md` |
| Filtry HTTP i walidacja | `interface/admin/forms/catalog_filters.py` |
| Logika pobierania listy i agregacji meczów | `infrastructure/repositories/core_catalog_repository.py` |
| Rejestracja trasy albo aktywne menu | `interface/admin/__init__.py`, `interface/navigation.py` |

## Sprawdzenie zmiany

Sprawdź widok testem klienta Flaska z repozytorium in-memory oraz jakość kodu poleceniami właściwymi dla zmiany. Widok jest tylko do odczytu i nie wykonuje zmian w bazie.

## Układ tekstowy i mapa zmian

```text
[base.html]
+------------------------------------------------------------+
| Start › Dane › Sędziowie                                   |
| Sędziowie                                                  |
| Lista sędziów i delegatów z obsady meczów.                 |
+------------------------------------------------------------+
| Filtry                                                     |
| [Szukaj: nazwisko lub miasto...] [Miasto...] [Filtruj]     |
| [Wyczyść filtry]                                           |
+------------------------------------------------------------+
| ID ↕ | Nazwisko ↕ | Miasto ↕ | Mecze ↕ | Akcje             |
| 11   | Kowalski Jan | Płock | 34      | [Szczegóły]       |
| ...                                                        |
| Liczba meczów obejmuje różne mecze powiązane z osobą...    |
| [paginacja]                                                |
+------------------------------------------------------------+
[stopka base.html]
```

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Nagłówek i opis strony | `list.html`, bloki `tytul` i `tresc` | Teksty `Sędziowie`, breadcrumb i opis |
| Panel filtrów | `list.html`, `KatalogFilterForm` | Pola `szukaj`, `miasto`, ukryte `sortowanie`, `rozmiar_strony` |
| Tabela | `list.html`, pętla po `strona.pozycje` | Kolumny `id`, `nazwisko`, `miasto`, `liczba_meczow` i link do szczegółów |
| Sortowanie | `list.html`, linki nagłówków; `SedziaListView.sortowanie` | Dozwolone pola i kierunek sortowania |
| Dane i liczniki | `KatalogPodstawowySQLAlchemyRepository.pobierz_sedziow` | JOIN do `mecze_sedziowie`, `count(distinct id_mecz)` |
| Nawigacja | `interface/navigation.py` | Aktywna pozycja `sedziowie` i endpoint `administracja.lista_sedziow` |
