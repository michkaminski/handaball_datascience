# Zakres produktu

## Ustalone z użytkownikiem

- Nazwa: Handball DataScience; katalog: `handball_datascience`.
- Dane: mecze polskich seniorskich lig piłki ręcznej obu płci.
- Priorytet rozgrywek: Superliga M, Superliga K oraz Ligi Centralne.
- Baza danych została już zaimportowana.
- Połączenie: `localhost:5432`, baza `zprp`, użytkownik `postgres`. AI nie wykonuje zmian w bazie bez wyraźnej prośby użytkownika o konkretną zmianę.
- Flask obsługuje stronę oraz administrację.
- Wygląd administracji opieramy na `C:\Michal\_ZPRP_PROD\Prototyp\Prototyp_administracja_v6`. Szczegóły wzorca i kolejność prac: [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md).
- Cały nowy kod aplikacyjny powstaje obiektowo, zgodnie z SOLID, na poziomie doświadczonego specjalisty Flask i obiektowego Pythona.
- Pliki, katalogi, moduły i pakiety nazywamy po angielsku. Pojęcia domenowe, metody i zmienne pozostają polskie bez znaków diakrytycznych, a klasy otrzymują angielską rolę po nazwie domenowej, np. MeczService i MeczRepository. API bibliotek i rzeczywiste nazwy bazy pozostają oryginalne. Szczegóły: [CODING_STANDARDS](CODING_STANDARDS.md#język-i-nazewnictwo).
- Przyjęto SQLAlchemy 2.0 jako ORM. Pełny wybór technologii: [TECH_STACK](TECH_STACK.md).
- Docelowa publikacja zewnętrzna wykorzysta pliki HTML, JSON i JavaScript.
- Aktualna praca dotyczy przygotowania projektu do pracy z AI; implementacja Flaska jest kolejnym etapem.

## Proponowany pierwszy zakres Flaska

Poniższy zakres jest punktem wyjścia do implementacji, nie deklaracją gotowych funkcji:

1. Konfiguracja aplikacji i połączenie z istniejącą bazą bez modyfikacji danych.
2. Lista meczów z filtrami sezonu, rozgrywek i etapu/kolejki oraz paginacją.
3. Szczegóły meczu: zespoły, termin, status, wynik i dostępne statystyki.
4. Administracja: dokładne operacje i uprawnienia do ustalenia przed jej wdrożeniem.

Widoki powinny rozróżniać brak danych od zera, nieodbyty mecz od wyniku 0:0 oraz błąd połączenia od pustej listy wyników. Filtry muszą zachowywać identyfikatory sezonu i rozgrywek, również przy powtarzających się nazwach.

## Poza bieżącym etapem

Publiczny eksport, wdrożenie, automatyczne pobieranie danych, nowe importy, modele predykcyjne i uczenie maszynowe. Nazwa DataScience nie oznacza automatycznego dodania tych funkcji.
