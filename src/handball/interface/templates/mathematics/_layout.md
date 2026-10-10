# Układ biblioteki matematycznej

Wspólny układ stron `/matematyka/…` (`_layout.html`). Rozszerza `base.html` (górny pasek, sidebar administracji, stopka) i dodaje własną nawigację działów oraz zasoby: KaTeX (lokalnie, `static/vendor/katex`, licencja MIT), `css/mathlib.css`, `js/mathlib.js`. ECharts ładowany leniwie z `data-echarts-url` tylko na stronach z wykresem `ml-plot`.

Dane: `dzialy` (`DzialMatematyki` z `BibliotekaMatematycznaService.dzialy()`), `rejestr` (`MathRegistry` — `rejestr.url(id)` buduje adresy z rejestru pojęć), opcjonalnie `aktywny_dzial` i `aktywny_artykul` ustawiane przez szablon potomny.

Blok potomny: `{% block matematyka %}`.

## Układ tekstowy i mapa zmian

```text
┌ base.html: header / nav (Matematyka aktywna) / sidebar ────────────────────────┐
│ ┌ nav.ml-sidenav ───────┐ ┌ div.ml-main ─────────────────────────────────────┐ │
│ │ ∑ Biblioteka …        │ │ {% block matematyka %}                           │ │
│ │ ▸ Podstawy statystyki │ │                                                  │ │
│ │   – Średnia …         │ │                                                  │ │
│ │ ▸ Rachunek prawd. …   │ │                                                  │ │
│ └───────────────────────┘ └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

| Element | Plik / selektor | Dane |
| --- | --- | --- |
| Kontener | `div.ml-shell[data-mathlib][data-echarts-url]` | adres ECharts |
| Nawigacja działów | `nav.ml-sidenav details/summary` | `dzialy`, `aktywny_dzial`, `aktywny_artykul` |
| Styl | `static/css/mathlib.css` (`.ml-*`) | — |
| Wzory, wykresy, spis treści | `static/js/mathlib.js` | KaTeX auto-render, numeracja `.ml-eq`, `.ml-plot` |
