# Sezony

Status: zaimplementowany widok odczytowy `GET /administracja/sezony`.

## Kontrakt

Lista pokazuje identyfikator, nazwę i rok rozpoczęcia sezonu, stan oraz liczby różnych rozgrywek i meczów. Wyszukiwanie obejmuje nazwę, a filtr stanu używa wartości źródłowej. Sortowanie działa w nagłówkach, paginacja zachowuje parametry.

Akcje prowadzą do rozgrywek danego sezonu i do przefiltrowanej listy meczów. Widok nie zapisuje danych.

## Układ tekstowy i mapa zmian

```text
+--------------------------------------------------------------+
| Sezony                                                       |
| [Nazwa sezonu] [Stan] [Filtruj] [Wyczyść]                    |
+--------------------------------------------------------------+
| ID | Sezon | Rok | Rozgrywki | Mecze | Stan | Akcje          |
|                                        [Rozgrywki] [Mecze]    |
+--------------------------------------------------------------+
```

| Element | Odpowiedzialność |
| --- | --- |
| Filtry | `KatalogFilterForm`, `.catalog-filters.compact` |
| Tabela | `#seasons-table`, `PozycjaSezonu` |
| Dane | `KatalogService`, `KatalogPodstawowySQLAlchemyRepository` |
| Nawigacja | `navigation.py`, klucz `sezony` |
