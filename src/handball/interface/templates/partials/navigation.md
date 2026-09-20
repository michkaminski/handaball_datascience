# Nawigacja administracji

Status: etap 4 ukończony. Szablon `partials/navigation.html` istnieje.

Docelowy szablon względem katalogu szablony: `partials/navigation.html`.

## Przeznaczenie

Górne menu sekcji i oznaczenie bieżącego ekranu, zgodne z prototypem v6 (`.nav`/`.nav-inner` z index.html): Start, Dane, Import, Kontrola danych, Logi.

## Dane wejściowe

Stała `GORNY_PASEK` z `interface/navigation.py` (lista `PozycjaMenu`: `klucz`, `etykieta`, `punkt_koncowy` — nazwa endpointu Flask albo `None`), wstrzykiwana globalnie do wszystkich szablonów przez `zarejestruj_kontekst_nawigacji()`. Zmienna `sekcja_aktywna` (string) przekazywana przez widok określa, która pozycja ma klasę `active`. Dla `sekcja_aktywna="zawodnicy"` aktywna jest górna pozycja „Dane”; sidebar wyróżnia „Zawodnicy”. Szablon tylko renderuje, nie decyduje o uprawnieniach ani dostępności pozycji.

## Powiązania

Dołączany przez `base.html` przez `{% include %}`. Ta sama stała `GORNY_PASEK` jest też częściowo odzwierciedlona w sidebarze wewnątrz `base.html` (grupa "Dane" zawiera m.in. "Mecze" wskazujące ten sam endpoint co "Dane" w górnym pasku) — patrz base.md.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj znacznik HTML pozycji menu (klasa `active`, struktura `<a>`). Etykiety, kolejność, zestaw pozycji i ich docelowe endpointy zmieniaj w `interface/navigation.py` — nie hardkoduj ich w tym szablonie. Ukrycie odnośnika nie zastępuje kontroli uprawnień w backendzie.

Pozycje "Kontrola danych" i "Logi" mają `punkt_koncowy=None` (renderują się jako `href="#"`, widoczne zgodnie z pełnym menu prototypu, ale nieaktywne) — nie mają jeszcze odpowiadających widoków. Podłącz prawdziwy endpoint w `interface/navigation.py` dopiero, gdy dany ekran faktycznie powstanie.

## Sprawdzenie zmiany

Sprawdź adresy, aktywną sekcję, obsługę klawiatury i zachowanie na wąskim ekranie.

## Stan implementacji

Wykonano: sprawdzenie w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px — pozycje "Start" i "Dane" widoczne, poprawnie oznaczane jako aktywne na odpowiednich stronach, pasek nie zawija się nieprawidłowo. `uv run pytest` sprawdza obecność `class="nav"` w odpowiedzi. Nie sprawdzono: nawigacji klawiaturą (Tab/Enter).

## Układ tekstowy i mapa zmian

Stan: fragment istniejącego menu, dołączany pod nagłówkiem w `base.html`.

```text
<nav class="nav">
  (1) [Start] [Dane] [Import] [Kontrola danych] [Logi]
         ^       ^
         |       aktywne dla sekcja_aktywna="mecze" lub "zawodnicy"
         aktywne dla sekcja_aktywna="start"
</nav>
```

Kolejność wynika z `GORNY_PASEK`. „Start”, „Dane” i „Import” mają realne adresy; dwie pozostałe pozycje mają `href="#"`. Klasa `.active` wyróżnia bieżącą sekcję. Na wąskim ekranie `.nav-inner` przewija się poziomo i nie zawija pozycji. Fragment nie zawiera sidebara ani przycisku „☰ Menu”.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Etykiety, kolejność i adresy | [navigation.py](../../navigation.py) | Lista `GORNY_PASEK`; `punkt_koncowy` określa cel, a `klucz` porównanie z aktywną sekcją. |
| Znacznik pojedynczej pozycji | [navigation.html](navigation.html) | Pętla po `gorny_pasek`, `<a>` i warunek `class="active"`. |
| Kolory, odstępy i poziome przewijanie | [admin.css](../../static/css/admin.css) | `.nav`, `.nav-inner`, `.nav a`, `.nav a.active`. |
| Miejsce menu na stronie | [base.html](../base.html) | Include `partials/navigation.html`, pomiędzy nagłówkiem a `.layout`. |
