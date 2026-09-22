# Strzelcy

Status: zaimplementowano.

## Przeznaczenie

Widok `GET /administracja/strzelcy` pokazuje źródłową klasyfikację strzelców z `public.strzelcy`. Brak danych pozostaje odróżniony od wartości zero.

## Dane i zachowanie

`StrzelecListView` korzysta z `KlasyfikacjaService` i `KlasyfikacjaReadRepository`. Dostępne są wyszukiwanie po zawodniku, drużynie lub rozgrywkach, filtry sezonu i rozgrywek, sortowanie oraz paginacja. Widok prezentuje miejsce, mecze, bramki, średnią, rzuty karne i kary dwuminutowe. Nazwisko prowadzi do szczegółów zawodnika.

## Sprawdzenie zmiany

Testy interfejsu są w `tests/interface/test_classifications.py`. Kontrole jakości obejmują Ruff, mypy i testy tras.

## Układ tekstowy i mapa zmian

```text
[base.html: nawigacja]
Strzelcy
[szukaj] [sezon] [rozgrywki] [Filtruj] [Wyczyść]
+----------------------------------------------------------------+
| M. | Zawodnik | Drużyna | Sezon | Rozgrywki | Mecze | Bramki |
| Śr./mecz | Karne | 2 min                                      |
+----------------------------------------------------------------+
[uwaga o brakach danych] [paginacja]
```

| Element | Plik / dane |
| --- | --- |
| Nagłówek, filtry i tabela | `list.html`, `KlasyfikacjaFilterForm` |
| Dane | `StrzelecListView` → `KlasyfikacjaService` → `KlasyfikacjaSQLAlchemyRepository.pobierz_strzelcow` |
| Menu | `interface/navigation.py`, klucz `strzelcy` |
| Paginacja | `partials/pagination.html`, `StronaKlasyfikacji` |
