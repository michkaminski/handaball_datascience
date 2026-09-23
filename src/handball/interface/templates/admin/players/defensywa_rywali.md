# Bramki zawodnika a poziom defensywy rywali — szczegóły

Osobna strona raportu (nie zakładka karty zawodnika, nie modal). Trasa `GET /administracja/zawodnicy/<id_zawodnik>/defensywa-rywali`, endpoint `administracja.defensywa_rywala_zawodnika`. Widok odczytu bez edycji, otwierany z sekcji „Defensywa rywali” w zakładce Forma i regularność karty zawodnika linkiem „Pokaż szczegóły” w nowej karcie przeglądarki (`target="_blank"`), zgodnie z zasadą, by pełnej analizy nie otwierać w małym modalu.

## Cel analizy

Odpowiada na pytanie: jak zawodnik historycznie zdobywał bramki przeciw rywalom o różnym poziomie defensywy? Jakość defensywy nie jest nazwą klubu ani miejscem w tabeli — wynika z liczby bramek traconych przez rywala względem średniej ligowej, liczonej wyłącznie ze stanu **przed** analizowanym meczem (bez data leakage). Analiza jest historyczna i opisowa; nie jest prognozą przyszłego meczu.

## Dane wejściowe i miejsce meczu

Dla każdego meczu zawodnika (wyłącznie strony `gosp`/`gosc`, bez `inne`) repozytorium rozwiązuje drużynę zawodnika i przeciwnika z surowych kolumn `mecze.id_zespol_gosp`/`id_zespol_gosc` i `wynik_gosp_full`/`wynik_gosc_full`, dopasowanych do strony zapisanej w `mecze_zawodnicy.strona` — **bez** stosowania `mecze.zamiana`, ponieważ `id_zespol_gosp` zawsze odpowiada `wynik_gosp_full`, niezależnie od zamiany (którą stosuje wyłącznie warstwa prezentacji istniejącej karty meczu, dla etykiety dom/wyjazd, nie dla przypisania bramek drużynie). Mecz z więcej niż jedną stroną zawodnika w tym samym meczu (`liczba_stron != 1`) albo z brakującym `id_zespol_gosp`/`id_zespol_gosc` jest pomijany — drużyna byłaby niejednoznaczna.

## Obliczenia (warstwa serwisu, niezależna od Flaska)

`DefensywaRywalaService` (`services/opponent_defense_service.py`) liczy dla każdego meczu, na podstawie samych wcześniejszych (`termin <` meczu analizowanego) meczów przeciwnika i całych rozgrywek:

- `GA_team` — średnia bramek traconych przez przeciwnika przed meczem, w tych samych rozgrywkach (`id_rozgrywki`, który już jednoznacznie wyznacza sezon).
- `GA_league` — średnia bramek traconych przez dowolną drużynę w tych rozgrywkach przed meczem (repozytorium rozbija każdy wcześniejszy mecz rozgrywek na dwa wpisy zespół–data–bramki\_stracone przez `pobierz_mecze_ligowe()`).
- `GA_smoothed` — wygładzona przez shrinkage: `(n×GA_team + k×GA_league) / (n+k)`; przy `n=0` równa `GA_league` (Defense Factor neutralny 1,00). `k` konfigurowalne (`KonfiguracjaDefensywyRywala.k_shrinkage`, domyślnie 5).
- Opcjonalnie `GA_previous` (średnia przeciwnika w odpowiadających rozgrywkach poprzedniego sezonu, dopasowanych po identycznej nazwie rozgrywek i `Sezon.rok_rozpoczecia - 1`) jako dodatkowy prior, tylko gdy `KonfiguracjaDefensywyRywala.uzyj_poprzedniego_sezonu=True` i dopasowanie jednoznaczne; domyślnie wyłączone.
- `DefenseFactor = GA_smoothed / GA_league`, klasyfikowany na 5 klas z konfigurowalnymi granicami (`klasyfikuj_defense_factor()`).
- Statystyki opisowe klasy (n, suma, średnia, mediana, min/maks, Q1/Q3, wariancja próbki, odchylenie standardowe, udziały progowe 1+/3+/5+/8+/10+, whiskery i wartości odstające regułą Tukeya) oraz Pearson, Spearman (na rangach z remisami uśrednionymi) i regresja liniowa (β0, β1, R², przybliżony 95% przedział ufności dla β1 oparty na przybliżeniu normalnym, nie dokładnym rozkładem t) liczone w czystych funkcjach modułu `opponent_defense_service.py`, bez zależności od Flaska ani ORM — w pełni testowalne jednostkowo.

## Filtry

Sezon, rozgrywki (listy z tych samych słowników co karta zawodnika), miejsce (wszystkie/u siebie/na wyjeździe), ostatnie N sezonów oraz checkbox „Wszystkie mecze” (odwrócona semantyka: zaznaczenie wyłącza domyślny filtr `tylko_pelne_dane`, żeby stan `tylko_pelne_dane=True` był domyślny mimo że niezaznaczony checkbox w GET nie wysyła wartości). Zmiana filtra przelicza statystyki, wykresy, klasy, prawdopodobieństwa, korelacje, regresję i interpretację — jedna ścieżka obliczeń w serwisie.

Filtr przeciwnika (tekst) działa jak na karcie zawodnika: `DefensywaRywalaReadRepository.pobierz_zespoly_o_nazwie()` zwraca identyfikatory zespołów, których dowolna historyczna nazwa w `zespoly_sezony` zawiera frazę, a serwis zostawia tylko mecze zawodnika przeciw tym zespołom. Wszystkie filtry zawężają wyłącznie analizowane mecze zawodnika; jakość defensywy rywala (GA_team, GA_league, shrinkage, Defense Factor) jest zawsze liczona z pełnych danych ligowych sprzed meczu, więc filtr nie zmienia klasy pojedynczego meczu. Link „Pokaż szczegóły” z karty przenosi sezon, rozgrywki i przeciwnika, a „← Powrót do karty zawodnika” prowadzi do sekcji `#player-forma-defensywa` w zakładce Forma i regularność.

## Sekcje strony (spis treści, 14 pozycji)

Wynik analizy (automatyczny komentarz wynikający z różnicy średnich skrajnych klas, nie zawsze efektowny wniosek) → główny wykres → dane źródłowe (sortowalna tabela, sortowanie po kliknięciu nagłówka, JS klienta, bez przeładowania) → jak liczona jest defensywa → shrinkage → Defense Factor → klasy defensywy (tabela granic) → statystyki opisowe (tabela + boxplot) → prawdopodobieństwa (wykres liniowy P(próg+) na klasę + tabela) → korelacja (Pearson, Spearman, scatter) → regresja (β0, β1, R², ΔBramki dla +0,10 Defense Factor, CI) → przykład jednego meczu krok po kroku (wybór meczu przez zwykły GET `id_mecz_przykladu`, bez JS) → interpretacja matematyczna (jedna spójna sekcja łącząca wszystkie miary) → ograniczenia analizy.

Mała próba (`liczba_z_defense_factor < prog_malej_proby`, domyślnie 10) pokazuje jawne ostrzeżenie w sekcji 1; każda klasa z `n` poniżej progu jest oznaczona „(mała próba)” w tabeli statystyk opisowych.

## Kontrakt i powiązania

- `analiza`: `DefensywaRywalaSzczegolyViewModel` (`interface/view_models/opponent_defense.py`) — wszystkie sformatowane dane strony, w tym `mecze` (tabela źródłowa), `wykres_klas`, `boxplot_klas`, `wykres_prawdopodobienstw`, `punkty_scatter` jako gotowe do `tojson` listy/słowniki liczb (nie stringi), oraz `przyklad`/`opcje_przykladu` dla kroku po kroku.
- `formularz`: `DefensywaRywalaFilterForm` (`interface/admin/forms/opponent_defense_filters.py`).
- `DefensywaRywalaZawodnikaView` (`interface/admin/views/opponent_defense_views.py`) składa `SzczegolyZawodnikaService` (nazwa i istnienie zawodnika, 404 przy braku), `DefensywaRywalaService` i `DefensywaRywalaPresenter`; zależności z `ZaleznosciZadaniaFactory`.
- Repozytorium `DefensywaRywalaSQLAlchemyRepository` (`infrastructure/repositories/opponent_defense_repository.py`) ma trzy metody: `pobierz_wystapienia`, `pobierz_mecze_ligowe` (rozbija mecz na dwa wpisy zespół–bramki\_stracone), `pobierz_poprzednie_rozgrywki`. ORM nie opuszcza repozytorium.
- Wykresy: `static/js/opponent_defense.js` (ECharts 6.1.0 lokalnie, SVG, ARIA, ładowane leniwie jak w karcie zawodnika) — bar (klasy), boxplot (klasy z odstającymi), line (prawdopodobieństwa progowe na klasę), scatter (Defense Factor vs bramki, klik otwiera mecz w nowej karcie).

Brak zawodnika daje 404, błąd odczytu 503, błędne filtry 400 (np. niepoprawne `miejsce`). Brak meczów z wyznaczonym Defense Factor pokazuje komunikat zamiast błędu i pomija sekcję przykładu.

## Ograniczenia (świadomie nieautomatyzowane)

Dopasowanie poprzedniego sezonu opiera się na identycznej nazwie rozgrywek i różnicy roku sezonu o 1; nie wykrywa awansu, spadku ani zmiany poziomu ligi — użytkownik musi to ocenić sam, stąd domyślnie wyłączone. Przedział ufności dla β1 jest przybliżeniem z rozkładu normalnego (bez zależności numpy/scipy — projekt ich nie używa, zgodnie z `docs/TECH_STACK.md`), nie dokładnym rozkładem t-Studenta. Model nie uwzględnia minut gry, rzutów, kontuzji, składu, tempa ani siły ofensywnej drużyny zawodnika — tych danych nie ma w bazie.

## Weryfikacja

Testy: `tests/unit/test_opponent_defense_service.py` (20 przypadków: shrinkage, n=0, klasyfikacja, korelacje, regresja, filtry, poprzedni sezon, brak danych leakage), `tests/unit/test_opponent_defense_repository.py` (rozwiązywanie strony, niejednoznaczność, unpivot, dopasowanie poprzednich rozgrywek), `tests/interface/test_opponent_defense.py` (strona, 404, 400, brak danych, przykład wybierany parametrem, zakładka karty) i `tests/javascript/opponent_defense.test.cjs` (cztery wykresy). Pełny zestaw i mypy/Ruff opisane w [STATUS](../../../../../docs/STATUS.md).

Na rzeczywistej karcie zawodnika #1732 (229 meczów) potwierdzono odpowiedź 200 karty i strony szczegółowej, poprawne dane JSON wykresów, działający filtr miejsca (229 → 114 dla „u siebie”) oraz przykład krok po kroku dla rzeczywistego meczu z 2017 roku. Bazy nie zmieniano.

## Układ tekstowy i mapa zmian

```text
Start › Dane › Zawodnicy › Szczegóły › Bramki a defensywa rywali
Bramki zawodnika a poziom defensywy rywali — szczegóły analizy
IMIĘ NAZWISKO · N meczów · sezony: ... · rozgrywki: ... · filtry: ...
[← Powrót do karty zawodnika]

[Sezon v] [Rozgrywki v] [Miejsce v] [Przeciwnik] [Ostatnie N sezonów] [ ] Wszystkie mecze [Filtruj] [Wyczyść filtry]

Spis treści (2 kolumny, 14 pozycji z odnośnikami #kotwica)

1. Wynik analizy
   [ostrzeżenie małej próby, jeśli n < próg]
   [automatyczny komentarz wynikający z danych]
2. Główny wykres
   [pełna szerokość: średnia bramek według 5 klas defensywy, etykiety n]
3. Dane źródłowe
   [tabela sortowalna klikiem nagłówka: Data|Sezon|Rozgrywki|Drużyna|
    Przeciwnik|Wynik|Gole|GA_team|GA_smoothed|GA_league|DefenseFactor|
    Klasa|n rywala]
4. Jak liczona jest defensywa — wzór GA_team + przykład
5. Shrinkage — wzór + przykład liczbowy + status poprzedniego sezonu
6. Defense Factor — wzór + interpretacja znaku
7. Klasy defensywy — tabela granic (konfigurowalne)
8. Statystyki opisowe
   [tabela: n|suma|średnia|mediana|min|Q25|Q75|maks|wariancja|odch.std]
   [boxplot pełna szerokość, z odstającymi]
9. Prawdopodobieństwa
   [wykres liniowy P(próg+) na klasę] [tabela tych samych wartości]
10. Korelacja — wzór Pearsona, r, rho, interpretacja siły, scatter
11. Regresja — wzór, β0, β1, R², CI, ΔBramki dla +0,10
12. Przykład jednego meczu
    [select meczu, GET onchange] [lista kroków opis→wartość]
13. Interpretacja matematyczna — jeden akapit łączący wszystkie miary
14. Ograniczenia analizy
```

Na wąskim ekranie spis treści zwija się do jednej kolumny, filtry i tabela źródłowa przewijają się w swoich kontenerach. Bez JavaScript wykresy nie renderują się (widoczny komunikat po nieudanym ładowaniu), ale wszystkie tabele, wzory i formularz filtrów/przykładu (`<noscript>` z przyciskiem) działają jako zwykłe GET.

### Mapa zmian

| Element | Plik | Blok / selektor / dane |
| --- | --- | --- |
| Domena i wzory statystyczne | [opponent_defense.py](../../../../domain/opponent_defense.py), [opponent_defense_service.py](../../../../services/opponent_defense_service.py) | `KonfiguracjaDefensywyRywala`, `pearson()`, `spearman()`, `regresja_liniowa()`, `klasyfikuj_defense_factor()`, `DefensywaRywalaService.pobierz_analize()`. |
| Dostęp do danych | [opponent_defense_repository.py](../../../../infrastructure/repositories/opponent_defense_repository.py) | `pobierz_wystapienia()`, `pobierz_mecze_ligowe()`, `pobierz_poprzednie_rozgrywki()`. |
| Formatowanie i interpretacje | [opponent_defense_presenter.py](../../../presenters/opponent_defense_presenter.py), [view_models/opponent_defense.py](../../../view_models/opponent_defense.py) | `DefensywaRywalaPresenter.przygotuj_szczegoly()`/`przygotuj_karte()`. |
| Filtry i walidacja | [opponent_defense_filters.py](../../../admin/forms/opponent_defense_filters.py) | `DefensywaRywalaFilterForm`, pole `przeciwnik`, odwrócony checkbox `wszystkie_mecze`; `pobierz_zespoly_o_nazwie()` w repozytorium. |
| Trasa i widok | [opponent_defense_views.py](../../../admin/views/opponent_defense_views.py), [__init__.py](../../../__init__.py) | `DefensywaRywalaZawodnikaView.get()`, `administracja.defensywa_rywala_zawodnika`. |
| Wykresy strony szczegółowej | [opponent_defense.js](../../../static/js/opponent_defense.js) | `rysujKlasy`, `rysujBoxplot`, `rysujPrawdopodobienstwa`, `rysujScatter`, `podepnijSortowanieTabeli`, `data-defense-*`. |
| Skrót na karcie zawodnika | [detail.html](detail.html), [detail.md](detail.md) | sekcja `#player-forma-defensywa` w zakładce `forma`, `data-defense-summary`, `DefensywaSkrotZawodnikaController` w [player_details.js](../../../static/js/player_details.js). |
| Style | [admin.css](../../../static/css/admin.css) | `.defense-filters`, `.defense-toc`, `.defense-formula`, `.defense-table`, `.defense-kroki`, `.player-chart-single`. |
