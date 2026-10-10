# Biblioteka matematyczna — strona główna

Trasa `GET /matematyka/`, endpoint `matematyka.indeks`, widok `MatematykaIndeksView` ([views.py](../../mathematics/views.py)). Pozycja w górnym pasku „Matematyka” i w sidebarze grupa „Matematyka”.

Pokazuje wszystkie działy z rejestru (`content/registry.json` pakietu `mathlib`), artykuły z krótką definicją, wyszukiwarkę po stronie klienta i listę planowanych modeli sportowych (bez linków — nie są zaimplementowane).

## Układ tekstowy i mapa zmian

```text
Start › Matematyka
Biblioteka matematyczna
[opis]
┌ Szukaj pojęcia [_______________] ┐
┌ 1. Podstawy statystyki ┐ ┌ 2. Rachunek prawd. ┐ ┌ 3. Rozkłady … ┐
│ Średnia arytmetyczna   │ │ …                  │ │ …             │
│   krótka definicja     │ │                    │ │               │
└────────────────────────┘ └────────────────────┘ └───────────────┘
… 10. Modele sportowe: MAF + „Planowane modele”
Rejestr pojęć w wersji … · N pojęć · M źródeł
```

| Element | Selektor | Dane |
| --- | --- | --- |
| Wyszukiwarka | `input[data-ml-search]` | filtruje `[data-ml-item]` i ukrywa puste `[data-ml-category]` (`mathlib.js`) |
| Karta działu | `section.ml-card[data-ml-category]` | `pozycja.dzial`, `pozycja.artykuly` |
| Planowane modele | `ul.ml-planned` | `planowane` (`registry.planned_models`) |
