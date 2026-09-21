# Drużyny

Status: zaimplementowany widok odczytowy `GET /administracja/druzyny`.

## Kontrakt

Każdy wiersz jest migawką `zespoly_sezony`, dlatego nazwa, miasto, płeć i status dotyczą wskazanego sezonu. Lista pokazuje także liczbę różnych meczów, w których drużyna wystąpiła jako gospodarz albo gość. Filtry obejmują nazwę, sezon, płeć, miasto i status wycofania.

Akcja „Mecze” przekazuje sezon i historyczną nazwę do istniejącej listy meczów. Widok nie zapisuje danych.

## Układ tekstowy i mapa zmian

```text
+---------------------------------------------------------------------+
| Drużyny                                                             |
| [Nazwa] [Sezon] [Płeć] [Miasto] [Status] [Filtruj] [Wyczyść]        |
+---------------------------------------------------------------------+
| ID | Sezon | Drużyna | Płeć | Miasto | Mecze | Status | Akcje       |
|                                                        [Mecze]      |
+---------------------------------------------------------------------+
```

| Element | Odpowiedzialność |
| --- | --- |
| Filtry | `KatalogFilterForm`, `.team-catalog-filters` |
| Tabela | `#teams-table`, `PozycjaDruzyny` |
| Dane | `KatalogService`, `KatalogPodstawowySQLAlchemyRepository` |
| Nawigacja | `navigation.py`, klucz `druzyny` |
