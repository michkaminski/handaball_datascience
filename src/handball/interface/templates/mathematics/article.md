# Biblioteka matematyczna — artykuł

Trasa `GET /matematyka/<dzial>/<slug>/`, endpoint `matematyka.artykul`, widok `MatematykaArtykulView`. Treść pochodzi z `mathlib/content/articles/<dzial>/<slug>.html` i jest przetwarzana przez `mathlib.render.ArticleRenderer`: linki `data-concept` dostają `href` z rejestru, `li[data-bib]` i `cite[data-bib]` — opis z `bibliography.json`, sekcje `h2` — numer i kotwicę. Alias pojęcia (np. `z-score`) nie ma własnej strony, prowadzi do kotwicy artykułu docelowego.

Kotwice są kontraktem: każdy artykuł ma 13 sekcji o stałych `id` (`intuicja` … `bibliografia`), a główny wzór `id="eq-<slug>"`. Dashboard MAF linkuje do nich przez identyfikatory pojęć.

## Układ tekstowy i mapa zmian

```text
Matematyka › Rozkłady › Rozkład beta
Rozkład beta
[krótka definicja]  Używane przez: [MAF]
┌ Spis treści ─┐ ┌ article.ml-article ─────────────────────────────┐
│ 1. Intuicja  │ │ 1. Intuicyjne wprowadzenie                       │
│ 2. Definicja │ │ 2. Definicja formalna  [ramka ml-def]            │
│ …            │ │ 5. Wzory   \[ … \]                          (1)  │
│ 13. Bibliogr.│ │ 8. Przykład [wykres ml-plot + suwaki]            │
└──────────────┘ │ 13. Bibliografia                                 │
                 └──────────────────────────────────────────────────┘
[← poprzedni]                                   [następny →]
Powiązane pojęcia w rejestrze: …
```

| Element | Selektor | Dane / kod |
| --- | --- | --- |
| Spis treści | `aside.ml-toc a[data-ml-toc]` | `artykul.toc` (h2 + h3), podświetlanie w `mathlib.js` |
| Treść | `article[data-ml-article]` | `artykul.html` |
| Numery wzorów | `.ml-eq > .ml-eqnum` | `numerujWzory()`; odwołania `a.ml-eqref` |
| Wykresy | `.ml-plot[data-plot][data-params]` | typy w `TYPY` (`mathlib.js`), lista w `mathlib/AUTHORING.md` |
| Nawigacja | `nav.ml-pager` | `strona.poprzedni`, `strona.nastepny` |
| Powiązane | `ul.ml-related` | `strona.powiazane` (pole `related` rejestru) |
