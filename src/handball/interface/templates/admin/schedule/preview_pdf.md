# Zapowiedź meczu — PDF A4

Status: wdrożony 2026-09-27 na polecenie użytkownika („przycisk zrzut do PDF-a … podziel estetycznie na strony, aby było bardzo ładnie czytelnie”). Szablon `preview_pdf.html` istnieje.

Samodzielny dokument HTML (nie rozszerza `base.html`, bez skryptów i linków) zamieniany na PDF przez WeasyPrint. Trasa `GET /administracja/terminarz/<id_mecz>/pdf`, endpoint `administracja.zapowiedz_meczu_pdf`, widok `ZapowiedzMeczuPdfView` ([schedule_views.py](../../../admin/views/schedule_views.py)). Parametry są takie same jak w [zapowiedzi](preview.md): `model`, `kadra_poprzedni`, `lata` i `bez_uwag`, z tymi samymi błędami 400/404. Gdy brakuje bibliotek Pango, widok zwraca 503 z instrukcją instalacji. Odpowiedź: `application/pdf`, `Content-Disposition: inline; filename="zapowiedz-meczu-<id>.pdf"`, więc przeglądarka otwiera PDF w karcie i pozwala go zapisać lub wydrukować.

Arkusz: [preview_pdf.css](../../../static/css/preview_pdf.css), przekazywany rendererowi jako plik (`ZapowiedzMeczuPdfView.ARKUSZ`). Nie korzysta z `admin.css`; kolory i klasy (forma W/R/P, ★ strzelców, czerwone pole bramek, tło uwag, KPI) odwzorowują stronę.

## Podział na strony

A4 w pionie, marginesy 17 / 13 / 15 mm. Od strony 2 nagłówek ma po lewej „Gospodarz — Gość” (`string-set` z `.running-match`), a po prawej „Zapowiedź meczu”. Stopka na każdej stronie: „Handball DataScience · stan na …” (`.running-date`) i „Strona X z Y”.

1. **Okładka** — etykieta, kontekst (rozgrywki · sezon · runda · kolejka), granatowy blok meczu (gospodarz, wynik albo „vs”, status, termin, hala), ewentualna uwaga o `zamiana`. Dalej „W skrócie”: forma W/R/P obu drużyn, bilans meczów bezpośrednich, kafelki prognozy (po 4 w rzędzie) albo powód jej braku, najlepsi strzelcy sezonu obu drużyn (`KadraDruzynyViewModel.najlepsi_strzelcy`: zawodnicy z `miejsce_strzelca`, według miejsca). Na końcu spis treści z numerami stron (`target-counter`) i opis zakresu statystyk.
2. **Kadra gospodarza** — sekcja 1, jedna drużyna na stronę; grupy pozycji z nagłówkami, grupa nie dzieli się między strony (`break-inside: avoid-page`), a przy bardzo dużej kadrze nagłówek tabeli powtarza się na następnej stronie. Pod tabelą legenda.
3. **Kadra gościa** — jak wyżej.
4. **Forma i porównanie** — sekcja 2 (dwie tabele 5 meczów z paskiem W/R/P) i sekcja 3 (tabela porównania, pogrubienie lepszej wartości) razem, jeśli się mieszczą; blok porównania się nie dzieli.
5. **Mecze bezpośrednie** — sekcja 4: kafelki bilansu i tabela wszystkich spotkań z okresu; długa tabela przechodzi na kolejne strony z powtarzanym nagłówkiem.
6. **Prognoza modelu** — sekcja 5: opis trybu, kafelki, ratingi, uwagi i przy prognozie na teraz kroki obliczenia; krok nie dzieli się między strony.

Przy `bez_uwag=y` uwagi „inny klub” i „inna liga” są pomijane już w HTML (`bez_uwag` w kontekście szablonu, klasa `bez-uwag` na `body`), a kolumna poprzedniego sezonu jest węższa. Każda sekcja rozpoczyna nową stronę (`.page`), a tytuł sekcji trafia do zakładek PDF (`bookmark-level`).

## Dane wejściowe

- `zapowiedz`: `ZapowiedzMeczuViewModel` z `ZapowiedzMeczuPresenter.przygotuj()`, ten sam co na stronie (wspólny `ZapowiedzMeczuOdczyt`).
- `bez_uwag`: `ZapowiedzOpcjeForm.bez_uwag` jako `bool`.

## Powiązania

`ZapowiedzMeczuPdfView` → `ZapowiedzMeczuOdczyt` (walidacja opcji, serwis i presenter zapowiedzi) → `render_template("admin/schedule/preview_pdf.html")` → `ZaleznosciZadaniaFactory.utworz_renderer_pdf()` → `DokumentPdfRenderer` ([kontrakt](../../../../contracts/pdf_renderer.py)) → `WeasyPrintPdfRenderer` ([pdf_renderer.py](../../../../infrastructure/pdf_renderer.py)). Przycisk „Pobierz PDF” na [preview.html](preview.html) wysyła formularz opcji `#preview-options` do tej trasy w nowej karcie, więc PDF ma bieżące opcje strony.

## Sprawdzenie zmiany

`tests/interface/test_schedule.py` (przycisk, kolejność stron i sekcji, nagłówek biegnący, brak linków i skryptów, okładka ze strzelcami, przeniesienie opcji i ukrycie uwag, 404/400/503) z testowym rendererem oraz `tests/unit/test_pdf_renderer.py` (brak Pango → `GeneratorPdfNiedostepny`; prawdziwy PDF, pomijany bez Pango). Na bazie (tylko odczyt) 2026-09-27: mecz rozegrany 206529 — 6 stron, ok. 5–6 s; mecz nierozegrany 206533 z poprzednim sezonem i ukrytymi uwagami — 8 stron (kadra 21 zawodników na jednej stronie, kroki prognozy na 2 stronach), ok. 5 s.

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `preview_pdf.html` (A4 pion).

```text
Strona 1 — okładka
 ZAPOWIEDŹ MECZU
 LOTTO Superliga · 2026/2027 · I runda · Seria 4
 +================================================================+
 |      GOSPODARZ                               GOŚĆ              |
 |  WKS Śląsk Wrocław        vs            COROTOP Gwardia Opole  |
 |                      [Zaplanowany]                              |
 |  ------------------------------------------------------------  |
 |        TERMIN niedz. 27.09.2026, 18:00   HALA Hala Orbita       |
 +================================================================+
 W skrócie
 +-- Forma --------------------+  +-- Mecze bezpośrednie --------+
 | Śląsk     [P][P][W][W][P]   |  |   0        0         3       |
 | Gwardia   [W][P][W][P][W]   |  | Śląsk   remisy   Gwardia     |
 +-----------------------------+  +------------------------------+
 +-- Prognoza modelu ---------------------------------------------+
 | [29:30] [X — remis] [A — gość] [−0.48]                         |
 | [58.87] [−19.06]                                               |
 +----------------------------------------------------------------+
 +-- Strzelcy — Śląsk ---------+  +-- Strzelcy — Gwardia --------+
 | 1. Marek MARCINIAK  11 br.  |  | 1. Dmytro ARTEMENKO 17 br.   |
 +-----------------------------+  +------------------------------+
 Spis treści
 1 Kadra w sezonie 2026/2027
     WKS Śląsk Wrocław ....................................... 2
     COROTOP Gwardia Opole ................................... 3
 2 Forma — ostatnie mecze .................................... 5
 …
 Handball DataScience · stan na …                    Strona 1 z 8

Strony 2–3 — kadry (jedna drużyna na stronę)
 Śląsk — Gwardia                                  Zapowiedź meczu
 (1) Kadra w sezonie 2026/2027
 WKS Śląsk Wrocław   gospodarz · 21 zawodników
 Nr | Zawodnik (data ur.) [★ n] | Pozycja | Mecze | Bramki | Śr. | 2025/2026 br. / śr.
 BRAMKARZE / ROZGRYWAJĄCY / SKRZYDŁOWI / OBROTOWI / …
 legenda

Strona 4 — (2) Forma: 2 × [pasek W/R/P + tabela 5 meczów]
          (3) Porównanie: gospodarz | statystyka | gość

Strona 5 — (4) Mecze bezpośrednie: [Mecze][Wygrane H][Remisy][Wygrane A][Bramki] + tabela

Strona 6+ — (5) Prognoza: opis, kafelki, ratingi, kroki 1–5 (Wzór | Podstawienie, Wynik)
```

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Rozmiar strony, marginesy, nagłówek i stopka | [preview_pdf.css](../../../static/css/preview_pdf.css), [preview_pdf.html](preview_pdf.html) | `@page`, `@page :first`, `.running-match`, `.running-date` (`string-set`). |
| Okładka i blok meczu | [preview_pdf.html](preview_pdf.html), [preview_pdf.css](../../../static/css/preview_pdf.css) | `section.cover`, `.hero`, `.hero-grid`, `.hero-meta`. |
| W skrócie | [preview_pdf.html](preview_pdf.html), [schedule.py](../../../view_models/schedule.py) | `.summary`, `.summary-box`, `.summary-h2h`, `.scorers`, makra `pasek_formy` i `kafelki_prognozy`; `KadraDruzynyViewModel.najlepsi_strzelcy`. |
| Spis treści | [preview_pdf.html](preview_pdf.html), [preview_pdf.css](../../../static/css/preview_pdf.css) | `ol.toc`, `.toc a::after` (`leader`, `target-counter`). |
| Podział na strony i tytuły sekcji | [preview_pdf.css](../../../static/css/preview_pdf.css) | `.page` (`break-before`), `.block`, `.step`, `.squad tbody` (`break-inside`), `.section-title`, makro `naglowek_sekcji`. |
| Kadra | [preview_pdf.html](preview_pdf.html), [preview_pdf.css](../../../static/css/preview_pdf.css) | `section.squad-page`, `table.squad`, `.group`, `.scorer`, `.top-scorer`, `.prev`, `.prev-note`, `.prev-other`, `.bez-uwag`. |
| Forma, porównanie, mecze bezpośrednie | [preview_pdf.html](preview_pdf.html), [preview_pdf.css](../../../static/css/preview_pdf.css) | makro `tabela_wystepow`, `.pdf-matches`, `.compare`, `.kpis`, `.kpi`. |
| Prognoza | [preview_pdf.html](preview_pdf.html), [preview_pdf.css](../../../static/css/preview_pdf.css) | `section#prognoza`, `.ratings`, `.step`, `.step-grid`, `.step-result`. |
| Generowanie i odpowiedź HTTP | [schedule_views.py](../../../admin/views/schedule_views.py), [pdf_renderer.py](../../../../infrastructure/pdf_renderer.py) | `ZapowiedzMeczuPdfView`, `ZapowiedzMeczuOdczyt`, `WeasyPrintPdfRenderer`. |
