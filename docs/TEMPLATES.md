# Dokumentacja każdego szablonu

Każdy plik szablonu ma własny plik MD obok siebie, z tą samą nazwą bazową: `lista.html` i `lista.md`. Zasada obejmuje strony, układy bazowe, fragmenty dołączane przez include oraz osobne pliki makr. Dla innych rozszerzeń zachowuj jednoznaczną parę, bez dwóch szablonów konkurujących o ten sam MD.

Przed zmianą szablonu przeczytaj jego MD. Aktualizuj dokument w tej samej zmianie, gdy zmieniają się przeznaczenie, dane wejściowe, bloki, powiązania, selektory lub sposób użycia. Przy przenoszeniu/zmianie nazwy przenieś również MD i popraw odnośniki; przy usunięciu szablonu usuń lub odpowiednio przenieś jego dokumentację.

MD opisuje aktualny kontrakt i miejsca zmian, a nie dziennik każdej korekty tekstu. Wspólne reguły pozostają w dokumentacji projektu; specyficzne instrukcje przy konkretnym szablonie.

## Zawartość dokumentu szablonu

- Przeznaczenie i źródło wyglądu w prototypie v6.
- Widok i serwis dostarczające dane; rzeczywiste nazwy, typy i opcjonalność zmiennych Jinja2 po implementacji.
- Dziedziczenie, include, makra, bloki oraz wpływ zmiany na inne szablony.
- Powiązane CSS, JS i selektory — gdzie zmienić układ, styl lub zachowanie.
- Wskazanie, które zmiany wymagają backendu, oraz stany błędu i braków danych.
- Sposób weryfikacji i powiązane testy; wyraźne odróżnienie planu od wykonanych kontroli.

## Obecne opisy

Utworzono dokumenty dla wszystkich 11 szablonów nazwanych w projekcie katalogów, łącznie z planowanym logowaniem. Powstały wyłącznie MD i ich katalogi; nie utworzono HTML ani kodu aplikacji.

| Planowany szablon | Dokument |
| --- | --- |
| `baza.html` | [baza.md](../src/pilka_reczna/interfejs/szablony/baza.md) |
| `elementy/nawigacja.html` | [elementy/nawigacja.md](../src/pilka_reczna/interfejs/szablony/elementy/nawigacja.md) |
| `elementy/komunikaty.html` | [elementy/komunikaty.md](../src/pilka_reczna/interfejs/szablony/elementy/komunikaty.md) |
| `elementy/paginacja.html` | [elementy/paginacja.md](../src/pilka_reczna/interfejs/szablony/elementy/paginacja.md) |
| `administracja/start.html` | [administracja/start.md](../src/pilka_reczna/interfejs/szablony/administracja/start.md) |
| `administracja/mecze/lista.html` | [administracja/mecze/lista.md](../src/pilka_reczna/interfejs/szablony/administracja/mecze/lista.md) |
| `administracja/mecze/szczegoly.html` | [administracja/mecze/szczegoly.md](../src/pilka_reczna/interfejs/szablony/administracja/mecze/szczegoly.md) |
| `administracja/logowanie.html` | [administracja/logowanie.md](../src/pilka_reczna/interfejs/szablony/administracja/logowanie.md) |
| `bledy/400.html` | [bledy/400.md](../src/pilka_reczna/interfejs/szablony/bledy/400.md) |
| `bledy/404.html` | [bledy/404.md](../src/pilka_reczna/interfejs/szablony/bledy/404.md) |
| `bledy/503.html` | [bledy/503.md](../src/pilka_reczna/interfejs/szablony/bledy/503.md) |

Przyszłe szablony zespołów, zawodników i diagnostyki otrzymają własne MD przy ich konkretnym zaprojektowaniu lub utworzeniu. MD nie są szablonami do renderowania ani zasobami publicznymi; nie wystawiaj ich przez routing i nie umieszczaj w publicznym eksporcie.
