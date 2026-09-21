# Rozgrywki

Status: zaimplementowany widok odczytowy `GET /administracja/rozgrywki`.

## Kontrakt

Lista pokazuje sezonowy rekord rozgrywek, nazwę, płeć oraz źródłową liczbę drużyn i rzeczywistą liczbę meczów. Filtry obejmują nazwę, sezon i płeć. Sortowanie działa w nagłówkach, a paginacja zachowuje parametry.

Akcja „Mecze” przekazuje identyfikator sezonu i nazwę rozgrywek do istniejącej listy meczów. Widok nie zapisuje danych.

## Układ tekstowy i mapa zmian

```text
+----------------------------------------------------------------+
| Rozgrywki                                                      |
| [Nazwa] [Sezon] [Płeć] [Filtruj] [Wyczyść]                     |
+----------------------------------------------------------------+
| ID | Sezon | Rozgrywki | Płeć | Drużyny | Mecze | Akcje        |
|                                                   [Mecze]       |
+----------------------------------------------------------------+
```

| Element | Odpowiedzialność |
| --- | --- |
| Filtry | `KatalogFilterForm`, `.catalog-filters` |
| Tabela | `#competitions-table`, `PozycjaRozgrywek` |
| Dane | `KatalogService`, `KatalogPodstawowySQLAlchemyRepository` |
| Nawigacja | `navigation.py`, klucz `rozgrywki` |
