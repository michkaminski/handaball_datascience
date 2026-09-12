# Nawigacja administracji

Status: etap 2 ukończony. Szablon `elementy/nawigacja.html` istnieje.

Docelowy szablon względem katalogu szablony: `elementy/nawigacja.html`.

## Przeznaczenie

Menu sekcji i oznaczenie bieżącego ekranu, zgodne z prototypem v6 (`.nav`/`.nav-inner` z index.html).

## Dane wejściowe

Zmienna kontekstu `pozycje_nawigacji`: lista słowników `{"etykieta": str, "adres": str, "aktywna": bool}`, budowana przez widok (np. `WidokStartowy`) i przekazywana do `render_template`. Szablon tylko renderuje, nie decyduje o uprawnieniach ani dostępności pozycji.

## Powiązania

Dołączany przez `baza.html` przez `{% include %}`. Nowa pozycja wymaga istniejącego widoku, poprawnego adresu (najlepiej `url_for(...)` z widoku) i dopisania jej do listy `pozycje_nawigacji` w tym widoku.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj znacznik HTML pozycji menu (klasa `active`, struktura `<a>`). Etykiety, kolejność i zestaw pozycji zmieniaj w widokach, które budują `pozycje_nawigacji` — nie hardkoduj ich w tym szablonie. Ukrycie odnośnika nie zastępuje kontroli uprawnień w backendzie.

Obecnie lista zawiera tylko pozycję "Start" (jedyny zaimplementowany widok). Prototyp v6 ma też górne menu Dane/Import/Kontrola danych/Logi — te pozycje dodać dopiero razem z odpowiadającymi im widokami (patrz IMPLEMENTATION_PLAN.md), nie jako martwe odnośniki.

## Sprawdzenie zmiany

Sprawdź adresy, aktywną sekcję, obsługę klawiatury i zachowanie na wąskim ekranie.

## Stan implementacji

Wykonano: sprawdzenie w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px — pozycja "Start" widoczna i oznaczona jako aktywna (klasa `active`), pasek nie zawija się nieprawidłowo. `uv run pytest` sprawdza obecność `class="nav"` w odpowiedzi. Nie sprawdzono: zachowania z więcej niż jedną pozycją, nawigacji klawiaturą (Tab/Enter) — do zweryfikowania przy dodaniu kolejnych widoków.
