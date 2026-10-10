# Biblioteka matematyczna — dział

Trasa `GET /matematyka/<dzial>/`, endpoint `matematyka.dzial`, widok `MatematykaDzialView`. Nieznany dział → 404. Dział bez artykułów (np. „Wnioskowanie statystyczne”) pokazuje informację o przygotowaniu i odsyłacze.

## Układ tekstowy i mapa zmian

```text
Matematyka › Statystyka bayesowska
Statystyka bayesowska
[opis działu]
┌ Twierdzenie Bayesa w estymacji ┐ ┌ Priory ┐ ┌ … ┐   (karty-linki)
│ krótka definicja   [MAF]       │
[Planowane modele]  (tylko Modele sportowe)
```

| Element | Selektor | Dane |
| --- | --- | --- |
| Karta artykułu | `a.ml-card-link` | `wynik.artykuly`, `rejestr.url(id)`, `models` |
| Pusty dział | `.ml-empty` | — |
| Planowane | `ul.ml-planned` | `planowane` |
