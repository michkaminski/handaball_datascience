# Karta zawodnika

Status: zaimplementowane Profil, Sezony i drużyny, Mecze oraz dodatkowe Podsumowanie i Forma i regularność. Pierwsze trzy zakładki zachowują wcześniejszą zawartość i zachowanie. Trasa `GET /administracja/zawodnicy/<id_zawodnik>`, endpoint `administracja.szczegoly_zawodnika`. Widok odczytu bez edycji.

## Otwieranie

Przycisk „Szczegóły” na liście otwiera pełną kartę w nowej karcie przeglądarki. Dwuklik lub Enter na wierszu otwiera natywny modal. Kliknięcie linku w wierszu nie otwiera dodatkowo modalu. Modal pobiera ten sam endpoint, wycina `[data-player-detail]` i usuwa przycisk powrotu do listy. Escape, × i „Zamknij” zamykają okno oraz przywracają fokus na wiersz.

Filtry, czyszczenie, sortowanie i paginacja działają także w modalu: pobierają nowy fragment bez opuszczania listy. „Otwórz w nowej karcie” zachowuje aktualne filtry, stronę i zakładkę. Nowsze żądanie anuluje poprzednie; zamknięcie modalu anuluje oczekujące pobranie. Błąd pobrania daje komunikat i pozostawia link do pełnej karty.

## Zakładki i dane

### Profil

Imię i nazwisko, ID, data urodzenia, wzrost, waga i opcjonalne zdjęcie ze słownika `zawodnicy`. Brak zdjęcia lub błąd jego wczytania jest obsłużony tekstem. Akceptowane są wyłącznie adresy HTTP/HTTPS; obraz nie wysyła nagłówka Referer. Brak daty oznacza „—”. Wzrost i waga pochodzą osobno z najnowszego, według porządku historii, niepustego zapisu `sklady`. Nie wyznaczamy bieżącego numeru, pozycji ani klubu.

### Sezony i drużyny

Tabela: Sezon, Drużyna, Rozgrywki, Numer, Pozycja, Bramki, Karne i Kary. Jeden rekord składu jest rozwijany do osobnego wiersza dla każdych rozgrywek, w których zawodnik ma przypisane statystyki meczowe dla tej drużyny. Skład bez takich wpisów pozostaje jednym wierszem z „—”. Nazwa i sezon pochodzą z `zespoly_sezony` oraz `sezony`. Pozycja pochodzi z `sklady.pozycja_nazwa`, a przy jej braku z `pozycje.nazwa`. Numer 0, jeśli zapisany, pozostaje zerem. Od 2026-09-26 (zgłoszenie użytkownika: zawodnik 62101 grał w 2025/2026 w dwóch drużynach, a skład sezonowy ma tylko jedną) historia obejmuje też drużyny, w których zawodnik ma wpisy meczowe, ale nie ma rekordu w `sklady`. Taki wiersz ma nazwę drużyny z `zespoly_sezony` (albo `zespoly`), numer i pozycję — najczęstsze w protokołach tej drużyny w sezonie (`mode()`), bez wzrostu i wagi, a `id_zespol_sezon = None`. Wpisy ze stroną `inne` nie tworzą wierszy.

Podsumowanie powstaje z `mecze_zawodnicy` połączonych z `mecze` i `rozgrywki`, grupowanych według sezonu, drużyny wynikającej ze strony `gosp`/`gosc` oraz nazwy rozgrywek. Bramki to suma znanych `bramki`; karne pokazują sumę `karne_bramki/karne_liczba`; kary pokazują sumy `dwie_minuty`, upomnień i dyskwalifikacji. `NULL` pozostaje „—”, jeżeli w grupie nie ma żadnej znanej wartości danego pola. Wpisy strony `inne` nie mają jednoznacznej drużyny i nie trafiają do tego zestawienia.

Sortowanie historii: rok rozpoczęcia sezonu malejąco, ID sezonu malejąco, nazwa i identyfikator migawki drużyny. Historia pokazuje wszystkie istniejące rekordy składów sezonowych zawodnika oraz drużyny znane tylko z protokołów; wiersze obu rodzajów są sortowane razem (rok sezonu, ID sezonu, nazwa drużyny). Filtry meczów jej nie zawężają. To nie jest historia wszystkich wersji JSON ani rejestr dat transferów.

### Mecze

Proste filtry: sezon (lista nazw), rozgrywki (unikalne nazwy), przeciwnik (tekst). Przeciwnik rozwiązywany jest przez historyczne nazwy do ID zespołu; następnie dobierany według strony wpisu zawodnika. `inne` nie przypisuje przeciwnika. Puste filtry oznaczają cały dostępny zakres.

Paginacja domyślnie po 20 różnych meczów, rozmiar strony 1–100. Sortowanie daty przez nagłówek, domyślnie najnowsze; ID rozstrzyga remisy, brak terminu na końcu. Termin to data faktyczna lub, przy jej braku, propozycja. Filtrowanie i sortowanie resetują stronę do 1, paginacja zachowuje filtry i zakładkę Mecze. Numer ponad zakres jest ograniczany do ostatniej strony.

Kolumny: Data, Sezon / rozgrywki, Drużyna (z numerem i pozycją z meczu), Przeciwnik, Wynik, Bramki, Karne, Kary, Akcje. Wynik w kolejności gospodarz–gość, zgodnie z presenterem meczu i regułą zamiany stron. Nazwy obu drużyn przy wyniku wyjaśniają kolejność; drużyna zawodnika i przeciwnik zachowują źródłową parę skład–zespół.

Karne pokazują trafione/próby, serie osobno. Nieznana część ułamka pozostaje „—”, np. `0/—`. Kary pokazują zapisane `dwie_minuty` pod etykietą „2 min”, upomnienie i dyskwalifikację; nie przeliczamy pola na minuty. Wpis w składzie nie dowodzi występu na boisku.

### Podsumowanie

Dodatkowa zakładka ma niezależny kontekst sezonu, rozgrywek i przeciwnika. Pokazuje liczbę różnych meczów z wpisem, sumę, średnią, medianę, wszystkie dominanty, Q1–Q3, udział meczów z bramką, karne, skuteczność karnych, kary i pokrycie danych. Braki nie są zerami. Wielokrotne wpisy zawodnika są agregowane do poziomu mecz–zawodnik przed obliczeniem statystyk.

Miejsce meczu (u siebie / na wyjeździe) jest wyznaczane w tym samym zapytaniu z `mecze_zawodnicy.strona`: `gosp` → u siebie, `gosc` → na wyjeździe. Strona wskazuje stronę po zamianie gospodarza, więc drużyna i przeciwnik wpisu biorą nazwy wyświetlane po `zamiana`, a drużyna sezonu i filtr przeciwnika korzystają z `StronyMeczuSql` ([DATA](../../../../../../docs/DATA.md#strona-wpisów-zawodników-przy-zamiana--2026-09-23)). Jeżeli wszystkie wpisy zawodnika w danym meczu zgadzają się co do strony, miejsce jest jednoznaczne; jeżeli mecz ma tylko wpisy `inne` albo sprzeczne strony (np. `gosp` i `gosc` w tym samym meczu), miejsce pozostaje nieustalone i mecz jest pomijany w podziale na u siebie/na wyjeździe — zgodnie z regułą projektu, by nie zgadywać jednej wartości dla niejednoznacznego agregatu.

Nad histogramem jest wykres „Średnia, mediana i dominanta bramek na mecz według sezonu”. Na osi są sezony; każdy punkt liczony jest ze wszystkich meczów sezonu w wybranym zakresie, niezależnie od rozgrywek. Serwis grupuje mecze po sezonie (kolejność pierwszego meczu), a w sezonie po rozgrywkach, i dla obu poziomów liczy w Pythonie tę samą `StatystykiBramekGrupy`: liczbę meczów, liczbę meczów ze znaną liczbą bramek, sumę, średnią, medianę, wszystkie dominanty, Q1, Q3, minimum i maksimum (`PodsumowanieAnalityczneZawodnika.statystyki_sezonow` → `StatystykiSezonuZawodnika.rozgrywki` → `StatystykiRozgrywekSezonuZawodnika`). Średnia i mediana są liniami z punktami, dominanta rombami (przy kilku dominantach kilka rombów w sezonie). Sezon z mniej niż 5 meczami ze znaną liczbą bramek ma pusty punkt i znacznik „mała próba”. Okienko po najechaniu (HTML, nazwy z bazy escapowane) pokazuje sezon, podsumowanie całego sezonu (mecze, suma, średnia, mediana, dominanta, Q1–Q3, min–maks) i tabelkę „Podział na rozgrywki” z liczbą meczów, średnią, medianą i dominantą każdych rozgrywek. Tabela „Dane statystyk według sezonu i rozgrywek” ma wiersz sezonu i — gdy sezon obejmuje więcej niż jedne rozgrywki — wcięte wiersze rozgrywek. Suwak przybliżania pojawia się dopiero przy ponad 20 sezonach.

Wykres ma przełącznik „Linie / Słupki” w nagłówku (`[data-player-season-toggle]`, przyciski z `aria-pressed`, ukryty bez JavaScript). Domyślny widok to linie; widok słupkowy pokazuje średnią, medianę i dominantę jako słupki obok siebie, przy kilku dominantach słupek ma wartość najmniejszej, a etykieta nad nim wszystkie (np. „1/4”). Sezon z małą próbą ma słupek półprzezroczysty z przerywaną ramką. Serie mają stałe `id`, więc zmiana widoku jest płynnym przejściem (`universalTransition`), wyłączonym przy `prefers-reduced-motion`. Obie wersje budują `opcjeSezonow(sezony, tryb)`.

Obok (na ekranach węższych niż 1200 px pod spodem, `.player-chart-grid.pair`) jest wykres słupkowy „Liczba bramek w sezonie: suma i podział na rozgrywki” (`[data-player-season-goals]`, `rysujBramkiSezonow()`), korzystający z tych samych danych `statystyki_sezonow`. W każdym sezonie pierwszy, ciemny słupek to suma bramek, a kolejne to bramki w poszczególnych rozgrywkach. Żeby słupki nie były zbyt wąskie, serie nie odpowiadają nazwom rozgrywek, tylko pozycjom w sezonie (`slotyRozgrywek()`, `id` `rozgrywki-0`, `rozgrywki-1`…): liczba słupków w grupie to suma plus największa liczba rozgrywek w jednym sezonie, a nie liczba wszystkich rozgrywek w karierze. Kolor i wzór (`itemStyle.decal`) nadawane są każdemu słupkowi według nazwy rozgrywek, więc te same rozgrywki wyglądają tak samo w każdym sezonie. Legendę budują puste serie liniowe z nazwami rozgrywek (niezajmujące miejsca na słupki); kliknięcie nazwy ukrywa rozgrywki, a zdarzenie `legendselectchanged` przelicza pozycje, więc po ukryciu słupki się poszerzają. Legenda jest przewijana i skraca długie nazwy. Okienko po najechaniu pokazuje sumę sezonu i tabelkę rozgrywek z liczbą meczów i bramek. Tabela „Dane statystyk według sezonu i rozgrywek” jest tekstowym odpowiednikiem obu wykresów.

Histogram „Rozkład bramek: wszystkie, u siebie i na wyjeździe” ma jednozdaniowy opis pod tytułem — liczba meczów dla każdej liczby bramek jako trzy słupki obok siebie, na pełną szerokość panelu, z tabelą „Dane rozkładu bramek” jako odpowiednikiem tekstowym. Dane histogramu trafiają do `data-player-distribution-data`. Pozostałe wykresy analityczne karty, w tym trzy wykresy „Forma mecz po meczu” przeniesione stąd na prośbę użytkownika, są w zakładce Forma i regularność. Wykres używa lokalnego Apache ECharts 6.1.0 w SVG, ma ARIA i respektuje `prefers-reduced-motion`.

Zapytanie wybiera mecze przez EXISTS, zlicza je i paginuje przed pobraniem wpisów. Wpisy zawodnika są pobierane jednym dodatkowym zapytaniem dla bieżącej strony, bez N+1. Kilka stron jednego meczu pozostaje jednym meczem w paginacji; źródłowe statystyki pokazane są osobno z komunikatem o kilku stronach. Nie są sumowane. „Szczegóły meczu” prowadzą do istniejącej karty meczu w nowej karcie przeglądarki.

### Forma i regularność

Dodatkowa zakładka z niezależnym kontekstem sezonu, rozgrywek i przeciwnika (ten sam formularz filtrów co Podsumowanie). Korzysta z tego samego zapytania `pobierz_analityke()` co Podsumowanie — bez dodatkowego zapytania do bazy.

Zakładka gromadzi wszystkie wykresy analityczne karty poza histogramem rozkładu bramek, który pozostaje w Podsumowaniu. Pod filtrami jest spis treści (`nav.player-toc[data-player-toc]`) z kotwicami do pięciu sekcji `section.player-section`: Statystyki opisowe (`#player-forma-statystyki`), Bramki mecz po meczu (`#player-forma-mecze`), Forma krocząca (`#player-forma-kroczaca`), Regularność według sezonu (`#player-forma-sezony`) i Defensywa rywali (`#player-forma-defensywa`). Bez JavaScript linki działają jak zwykłe kotwice; z JavaScript `ZakladkiZawodnikaController.podlaczSpisTresci()` przewija do sekcji (płynnie, a przy `prefers-reduced-motion` natychmiast), przenosi na nią fokus i nie zmienia adresu strony, co ma znaczenie także w modalu listy zawodników. Sekcja bez danych pokazuje komunikat, więc spis treści zawsze prowadzi do istniejącego celu.

Wygląd: lista sekcji jest zdefiniowana raz w szablonie (`sekcje_formy`: klucz kotwicy, tytuł, podtytuł, liczba wykresów lub miar) i zasila zarówno spis treści, jak i nagłówki sekcji (lokalne makro `naglowek_sekcji(nr)` w `detail.html`). Spis treści to siatka kafelków: numer w kolorowym kwadracie, tytuł, jednozdaniowy opis i znacznik liczby wykresów; kafelek unosi się lekko po najechaniu (bez ruchu przy `prefers-reduced-motion`), a na telefonie opis jest ukryty, żeby spis był zwarty. Każda sekcja jest osobną kartą z nagłówkiem (numer, tytuł, podtytuł, przycisk „↑ Spis treści”) i akcentem kolorystycznym z palety strony (`--acc`, `--good`, `--warn`, `--n3`, `--danger`) w tej samej kolejności co kafelki. Linki spisu i powrotu mają `data-player-scroll`. Statystyki opisowe są pogrupowane w cztery bloki: Poziom (średnia, mediana, dominanta, średnia ucięta), Zakres (min, maks, Q1–Q3, P10, P90), Rozrzut (IQR, odchylenie standardowe, MAD, współczynnik zmienności) i Udziały meczów (0, 1–2, 3–5, 6+) — na desktopie po dwa bloki w rzędzie, każdy z kafelkami w jednym wierszu, na węższych ekranach jeden pod drugim.

Sekcja Bramki mecz po meczu zawiera trzy wykresy przeniesione z Podsumowania: wszystkie mecze, tylko u siebie i tylko na wyjeździe, każdy z własną medianą (linia przerywana) — wariant „wszystkie” liczy medianę z całego zakresu, warianty miejsca tylko z meczów danego miejsca. Mecz z niejednoznaczną lub nieustaloną stroną (np. wpis `inne`) nie trafia do wariantu u siebie ani na wyjeździe, ale pozostaje w wariancie wszystkie; kliknięcie punktu otwiera mecz, a najwyższy wynik jest wyróżniony. Dane pochodzą z `podsumowanie.punkty` i median Podsumowania (`data-player-trend-data`), a tabela „Dane wykresów mecz po meczu” jest ich odpowiednikiem tekstowym.

KPI: średnia, mediana, wszystkie dominanty, minimum, maksimum, Q1–Q3, IQR, odchylenie standardowe (populacyjne), MAD (mediana bezwzględnych odchyleń od mediany), współczynnik zmienności, P10, P90, średnia ucięta 10% oraz udział meczów z 0, 1–2, 3–5 i 6+ bramkami. Wszystkie miary liczone są tylko z meczów ze znaną liczbą bramek w wybranym zakresie; braki nie stają się zerami. Współczynnik zmienności jest pomijany („—”), gdy średnia jest mniejsza niż 0,1 bramki na mecz.

Sekcja Forma krocząca ma trzy wykresy. Pierwszy, „Przebieg formy (wszystkie mecze)”, liczy okno kroczące ze wszystkich meczów zakresu w kolejności rozgrywania, łącznie z meczami o nieustalonym miejscu (`forma.wszystkie`, liczone w `_forma_meczow()` tą samą metodą co warianty miejsca). Pod nim są dwa wykresy według miejsca — u siebie i na wyjeździe — z niezależnie liczonym oknem kroczącym: każdy pokazuje punkty meczów tego miejsca (kolor według sezonu), medianę kroczącą i średnią kroczącą z 5 ostatnich takich meczów ze znaną liczbą bramek oraz — po osiągnięciu 10 — dodatkową medianę kroczącą z 10. Rozdzielenie okna kroczącego (a nie tylko podział wykresu) ma znaczenie: krocząca piątka meczów u siebie pomija mecze wyjazdowe rozgrywane między nimi, więc pokazuje rzeczywistą formę w danym miejscu, nie formę ogólną przefiltrowaną wizualnie. Kolejność w każdym z wykresów jest ustalana po kolejności meczów danego miejsca (termin, potem ID), nie po dniach kalendarzowych; nieznana liczba bramek przerywa okno kroczące zamiast zamieniać się w zero. Mecz z niejednoznacznym lub nieustalonym miejscem (np. wpis `inne`) nie trafia do żadnego z dwóch wykresów. Poniżej 5 takich meczów zamiast trendu pokazuje się osobne, jawne ostrzeżenie dla danego wariantu (wszystkie, u siebie, na wyjeździe); przy zerze meczów wykres pokazuje krótki komunikat zamiast pustego obszaru. Kliknięcie punktu otwiera szczegóły meczu w nowej karcie. Pionowe linie oznaczają granice sezonów w obrębie danego miejsca.

Wykres regularności to jeden, wspólny (nie rozdzielony na miejsca) boxplot bramek na mecz według sezonu: mediana, Q1, Q3 oraz wąsy ograniczone regułą Tukeya (`Q1 − 1,5×IQR` … `Q3 + 1,5×IQR`); wartości poza tym zakresem są oznaczone osobno jako punkty odstające, nie ukrywane. Sezon z mniej niż 5 znanymi meczami jest oznaczony jako mała próba w tabeli danych i na osi kategorii (etykieta `n=`).

Wszystkie wykresy zakładki są ułożone jeden pod drugim na pełną szerokość panelu (`.player-chart-grid.stacked`), żeby pozostawały czytelne przy wielu sezonach i setkach meczów. Każda sekcja ma tabelaryczny odpowiednik w rozwijanych blokach pod wykresami, wykresy mają opis ARIA i respektują `prefers-reduced-motion`.

#### Defensywa rywali (sekcja Formy i regularności)

Ostatnia sekcja zakładki, przeniesiona z usuniętej zakładki Statystyki na prośbę użytkownika, aby wszystkie wykresy były w jednym miejscu. Zawiera nagłówek „Bramki zawodnika a poziom defensywy rywali”, opis, jeden wykres słupkowy (średnia bramek zawodnika w pięciu klasach jakości defensywy rywala, z liczbą meczów n przy każdym słupku), tabelę „Dane wykresu defensywy rywali” (klasa, średnia, n) i przycisk „Pokaż szczegóły” otwierający pełny raport w nowej karcie (`target="_blank"`, nie modal). Bez wzorów, regresji, Pearsona, Spearmana, R², shrinkage ani tabel matematycznych — te trafiają wyłącznie na osobną stronę [defensywa_rywali.md](defensywa_rywali.md), pod trasą `GET /administracja/zawodnicy/<id_zawodnik>/defensywa-rywali` (endpoint `administracja.defensywa_rywala_zawodnika`). Jakość defensywy rywala jest liczona ze stanu **przed** każdym analizowanym meczem (bez data leakage), względem średniej ligowej tych samych rozgrywek, z shrinkage przy małej liczbie wcześniejszych meczów rywala — pełny opis metody jest w dokumencie strony szczegółowej. Przy braku meczów z wyznaczoną jakością defensywy pokazuje się jawny komunikat zamiast pustego wykresu. Sekcja uwzględnia filtry zakładki: widok przekazuje sezon, rozgrywki i przeciwnika do `FiltryDefensywyRywala`, a link „Pokaż szczegóły” przenosi je na stronę szczegółową. Filtry zawężają tylko analizowane mecze zawodnika; jakość defensywy rywala jest zawsze liczona z pełnych danych ligowych sprzed meczu. Tak jak na stronie szczegółowej domyślnie liczone są tylko mecze z pełnymi danymi, co opisuje notatka w sekcji. Parametr `zakladka=statystyki` nie jest już akceptowany.

## Kontrakt i powiązania

- `szczegoly`: `SzczegolyZawodnikaViewModel`: id_zawodnik, nazwa, data_urodzenia, foto_url, najnowszy dostępny wzrost i wagę oraz sezony z podsumowaniami rozgrywek.
- `strona`: `StronaMeczowZawodnikaViewModel`: pozycje, liczba_wszystkich, strona i rozmiar_strony. Każda pozycja zawiera model meczu, termin, wpisy i flagę wiele_stron.
- `formularz`: `MeczeZawodnikaFilterForm`; `filtry`: `FiltryMeczowZawodnika`.
- `aktywna_zakladka`: profil / sezony / mecze / podsumowanie / forma. Bez parametrów profil; przy parametrach bez jawnej zakładki — mecze.
- `defensywa_rywali`: `DefensywaRywalaKartaViewModel` (sekcja Defensywa rywali w Formie i regularności): klasy z n i średnią, `wykres` gotowy do `tojson`, flaga wystarczającej liczby danych.
- `podsumowanie`: `PodsumowanieAnalityczneZawodnikaViewModel`; KPI, punkty trendu z miejscem meczu, rozkład bramek podzielony na wszystkie/u siebie/na wyjeździe i mediana każdego wariantu.
- `forma`: `FormaIRegularnoscViewModel` (wspólny z kartą drużyny, [goal_statistics.py](../../../view_models/goal_statistics.py)); statystyki opisowe (całościowe), zagnieżdżone `wszystkie`/`dom`/`wyjazd` (`FormaWedlugMiejscaViewModel`: własne punkty formy z medianą/średnią kroczącą i próg trendu) oraz wspólne rozstępy sezonów do boxplota.
- `parametry_paginacji`: bieżące parametry GET z nadpisanym prawidłowym id_zawodnik i zakladka=mecze, używane przez wspólną paginację.
- `sekcja_aktywna="zawodnicy"`: sidebar Zawodnicy i górna sekcja Dane.

`ZawodnikSzczegolyView` korzysta z `SzczegolyZawodnikaService` i `SzczegolyZawodnikaAnalyticsService`. Repozytorium agreguje analitykę do poziomu meczu, serwis oblicza miary opisowe, a `SzczegolyZawodnikaPresenter` formatuje KPI i wykresy. Zależności składa `ZaleznosciZadaniaFactory`; ORM nie opuszcza repozytorium.

Brak zawodnika daje 404, błąd odczytu 503, błędne filtry 400. Brak historii lub pasujących meczów daje osobny komunikat i nie usuwa profilu. Nazwy są escapowane przez Jinja2. Bez JavaScript wszystkie trzy sekcje są widoczne i formularz/paginacja działają jako zwykły GET.

## Weryfikacja

Testy: `tests/interface/test_player_details.py`, `tests/unit/test_player_detail_repository.py` i `tests/javascript/player_details.test.cjs`. Sprawdzają historię i braki, błędy, walidację, stronę 2, parametry linków, zamianę stron meczu, oddzielne wpisy i brak zamiany NULL karnych na zero.

W Edge na izolowanych danych sprawdzono przycisk, dwuklik, Enter, Escape, przywrócenie fokusu, zakładki, historię, stronę 2 w modalu, filtrowanie i czyszczenie bez opuszczania listy oraz pełną kartę. Kontrola 1440 px i 390 px: bez poziomego przewijania dokumentu; tabela na telefonie przewija się we własnym kontenerze.

Po odświeżeniu lokalnego serwera potwierdzono GET listy i karty z rzeczywistymi danymi (200), w tym pierwszą i drugą stronę zawodnika z 551 meczami: 1–20 i 21–40. To sprawdzenie działania odczytu, nie pełny audyt historycznego importu ani pomiar kompletności wszystkich pól. Bazy nie zmieniano.

Po dodaniu Podsumowania potwierdzono na rzeczywistej karcie odpowiedź 200, dwa wykresy SVG, lokalny zasób ECharts, opisy ARIA oraz renderowanie przy szerokości 1440 i 390 px. Testy obejmują obliczenia statystyczne, SQL agregujący do meczu, widok i inicjalizację wykresów. Bazy nie zmieniano.

Po dodaniu Formy i regularności: 5 nowych testów jednostkowych serwisu (okno kroczące, próg 5/10 meczów, statystyki opisowe, współczynnik zmienności, grupowanie sezonów i wartości odstające), 1 nowy test interfejsu i 1 nowy test JavaScript (dwa wykresy SVG, granica sezonu w markLine, boxplot z punktem odstającym) przechodzą. Pełny zestaw poza tą zmianą: 253 z 254 testów Pythona bez integracyjnych z bazą (jedyny nieprzechodzący, `test_utworz_zwraca_skonfigurowana_aplikacje`, jest środowiskowy — zależy od lokalnej zmiennej `SECRET_KEY` i nie dotyczy tej zmiany; 8 testów integracyjnych pominiętych bez `BAZA_HASLO`) oraz 27 testów JavaScript. Mypy i Ruff (check i format) bez błędów dla zmienionego zakresu; poza zakresem pozostaje znany, wcześniej udokumentowany E501 w `tests/integration/test_import_repository.py`. Na rzeczywistej karcie zawodnika #1732 (231 meczów, sezony 2008/2009–2025/2026) potwierdzono odpowiedź 200, poprawne dane JSON wykresów, oznaczenie sezonu jako małej próby i realny punkt odstający w rozstępie sezonowym. Bazy nie zmieniano.

Na wyraźne polecenie użytkownika dodano podział wykresów formy (Podsumowanie i Forma i regularność) oraz histogramu (Podsumowanie) na u siebie/na wyjeździe, z niezależnym oknem kroczącym per miejsce w Formie i regularności. Zmiana objęła repozytorium (nowa kolumna `miejsce` w `pobierz_analityke()`, z regułą wykluczania niejednoznacznych stron), domenę, serwis, presenter, widok, szablon i JavaScript. Weryfikacja: 2 nowe testy repozytorium (jednoznaczne i niejednoznaczne miejsce), 1 nowy test serwisu (niezależne okno kroczące per miejsce), zaktualizowane testy interfejsu i oba testy JavaScript formy/podsumowania przechodzą; pełny zestaw 255/256 testów Pythona (ten sam nieistotny błąd `SECRET_KEY`) i 27 testów JavaScript. Mypy i Ruff bez błędów. Na rzeczywistej karcie zawodnika #1732 potwierdzono odpowiedzi 200 dla obu zakładek oraz poprawne dane JSON z polami `miejsce`, `miejsce_etykieta`, `mediana_dom`/`mediana_wyjazd` i zagnieżdżonymi `dom`/`wyjazd` w danych formy. Bazy nie zmieniano.

Na dalsze doprecyzowanie użytkownika w zakładce Podsumowanie przywrócono wykres „Forma mecz po meczu (wszystkie)” obok wariantów u siebie/na wyjeździe (trzy wykresy formy zamiast dwóch) i rozszerzono histogram „Rozkład bramek” do trzech słupków na każdą liczbę bramek: Wszystkie, U siebie, Na wyjeździe. Dane do wariantu „wszystkie” (mediana całościowa, łączna liczba meczów na słupek) były już liczone wcześniej na potrzeby KPI i pozostałych wariantów, więc zmiana dotyczyła tylko szablonu i JavaScriptu (`AnalitykaZawodnikaController`), bez zmian w repozytorium ani serwisie. Zakładka Forma i regularność nie zmieniła się — użytkownik nie prosił tam o wariant „wszystkie”. Testy interfejsu i JavaScript zaktualizowano pod nowy układ (4 wykresy zamiast 3, histogram z 3 seriami); pełny zestaw testów pozostaje zielony poza tymi samymi dwoma nieistotnymi, wcześniej udokumentowanymi wyjątkami. Sprawdzono na rzeczywistej karcie #1732: cztery wykresy i trzy podpisane serie histogramu renderują się poprawnie.

Dodano zakładkę Statystyki (kompaktowy wykres „Bramki zawodnika a poziom defensywy rywali” + przycisk „Pokaż szczegóły”) i osobną stronę raportu pod tym przyciskiem — pełny opis w [defensywa_rywali.md](defensywa_rywali.md). Nowa analiza dostała własną warstwę domeny/serwisu/repozytorium/presentera, niezależną od istniejącej analityki Podsumowania i Formy; jedyna zmiana w tym pliku i widoku karty to dodanie szóstej zakładki i wywołanie nowego serwisu z domyślnymi filtrami (cała kariera) na potrzeby kompaktowego wykresu. Weryfikacja: 20 nowych testów jednostkowych serwisu, 6 testów repozytorium, 6 testów interfejsu (strona szczegółowa, 404, 400, brak danych, przykład wybierany parametrem, zakładka karty) i 2 testy JavaScript (cztery wykresy strony szczegółowej, wykres skrótu na karcie) przechodzą. Pełny zestaw: 287 z 288 testów Pythona bez integracyjnych z bazą (ten sam nieistotny błąd `SECRET_KEY`, niezwiązany ze zmianą) i 29 testów JavaScript. Mypy i Ruff (check i format) bez błędów. Na rzeczywistej karcie zawodnika #1732 (229 meczów) potwierdzono odpowiedź 200 karty i strony szczegółowej, poprawne dane JSON wszystkich czterech wykresów, działający filtr miejsca (229 → 114 dla „u siebie”) i przykład krok po kroku dla rzeczywistego meczu z 2017 roku. Bazy nie zmieniano.

## Dalszy plan

Istniejące zakładki Profil, Sezony i drużyny oraz Mecze pozostają bez zmian. Podsumowanie oraz Forma i regularność (z sekcją defensywy rywali) są zaimplementowanymi dodatkowymi zakładkami. Bramki i karne, Porównania, Dyscyplina, Rekordy i Jakość danych (z [PLAYER_DATA_SCIENCE](../../../../../../docs/PLAYER_DATA_SCIENCE.md)) pozostają planem bez nieczynnych elementów w interfejsie — nie są renderowane jako zakładki, dopóki nie zostaną zaimplementowane. Analiza defensywy rywali (ten dokument i [defensywa_rywali.md](defensywa_rywali.md)) jest osobną, dodatkową analizą spoza pierwotnego planu PLAYER_DATA_SCIENCE, zleconą wprost przez użytkownika.

## Układ tekstowy i mapa zmian

Rzeczywisty układ `detail.html`, wspólny dla pełnej karty i modalu:

```text
[pełna karta: rama base.html; modal: nagłówek Szczegóły zawodnika / ×]
Start › Dane › Zawodnicy › Szczegóły
IMIĘ NAZWISKO
Karta zawodnika #ID
[Powrót do listy] — tylko w pełnej karcie

[Profil] [Sezony i drużyny] [Mecze] [Podsumowanie] [Forma i regularność]

Profil:
  [zdjęcie / brak]  ID / Imię i nazwisko / Data urodzenia / Wzrost / Waga
Sezony i drużyny:
  Sezon | Drużyna | Rozgrywki | Numer | Pozycja | Bramki | Karne | Kary
  [rekordy składów i drużyny tylko z protokołów, rozwinięte według rozgrywek / brak danych]
Mecze:
  [Sezon v] [Rozgrywki v] [Przeciwnik] [Filtruj] [Wyczyść filtry]
  Data ↕ | Sezon/rozgrywki | Drużyna | Przeciwnik | Wynik |
  Bramki | Karne | Kary | Szczegóły meczu
  [mecze bieżącej strony / pusty wynik]
  Wyniki od–do z wszystkich   [« Poprzednia] [Następna »]
Podsumowanie:
  [Sezon v] [Rozgrywki v] [Przeciwnik] [Filtruj analizy] [Wyczyść filtry]
  [KPI: mecze | bramki | średnia | mediana | dominanta | Q1–Q3 | karne | kary]
  [Pokrycie danych o bramkach]
  [średnia / mediana / dominanta według sezonu  [Linie|Słupki]] [liczba bramek w sezonie: suma | rozgrywki...]
    (obok siebie od 1200 px, niżej jeden pod drugim)
    okienko miar: sezon · podsumowanie sezonu · Podział na rozgrywki (mecze | śr. | med. | dom.)
    okienko bramek: sezon · suma sezonu · Podział na rozgrywki (mecze | bramki)
  [tabela danych: wiersz sezonu + wcięte wiersze rozgrywek]
  [rozkład bramek: słupki wszystkie, u siebie i na wyjeździe — pełna szerokość]
  [tabela danych rozkładu bramek]
  Wykresy formy, regularności i defensywy rywali są w zakładce Forma i regularność.
Forma i regularność:
  [Sezon v] [Rozgrywki v] [Przeciwnik] [Filtruj analizy] [Wyczyść filtry]
  +- Spis treści ------------------------------ 5 sekcji · kliknij, aby przejść -+
  | [1] Statystyki | [2] Bramki mecz | [3] Forma     | [4] Regularność | [5] Defensywa |
  |  opisowe       |  po meczu       |  krocząca     |  według sezonu  |  rywali       |
  |  opis          |  opis           |  opis         |  opis           |  opis         |
  |  (17 miar)     |  (3 wykresy)    |  (3 wykresy)  |  (1 wykres)     |  (1 wykres)   |
  +-----------------------------------------------------------------------------+
  każda sekcja poniżej: [n] Tytuł / podtytuł ................ [↑ Spis treści]
  1. Statystyki opisowe
    [POZIOM: średnia | mediana | dominanta | śr. ucięta]  [ZAKRES: min | maks | Q1–Q3 | P10 | P90]
    [ROZRZUT: IQR | odch. std. | MAD | wsp. zmienności]  [UDZIAŁY: 0 | 1–2 | 3–5 | 6+]
  2. Bramki mecz po meczu
    [trend bramek (wszystkie) + mediana — pełna szerokość]
    [trend bramek u siebie + mediana — pełna szerokość]
    [trend bramek na wyjeździe + mediana — pełna szerokość]
    [tabela danych wykresów mecz po meczu, z kolumną Miejsce]
  3. Forma krocząca
    [ostrzeżenie o zbyt małej liczbie meczów: wszystkie / u siebie / na wyjeździe, jeśli n < 5]
    [forma — wszystkie mecze: bramki + mediana/średnia krocząca 5 (+ mediana krocząca 10)]
    [forma u siebie: bramki + mediana/średnia krocząca 5 (+ mediana krocząca 10)]
    [forma na wyjeździe: bramki + mediana/średnia krocząca 5 (+ mediana krocząca 10)]
    [tabela danych formy: wszystkie mecze] [u siebie] [na wyjeździe]
  4. Regularność według sezonu
    [boxplot sezonów (wspólny) — pełna szerokość] [tabela danych rozstępu sezonów]
  5. Bramki zawodnika a poziom defensywy rywali
    [notatka: filtry sezonu, rozgrywek i przeciwnika; tylko mecze z pełnymi danymi]
    [wykres słupkowy: 5 klas defensywy, średnia + n / komunikat o zbyt małej próbie]
    [tabela danych wykresu defensywy rywali]
    [Pokaż szczegóły] → nowa karta: defensywa_rywali.html (osobny raport, nie modal)

[modal: Otwórz w nowej karcie / Zamknij]
```

Z JavaScript widoczna jest jedna zakładka. Na wąskim ekranie filtry układają się pionowo, tabele przewijają w swoich kontenerach, a modal ma przewijaną treść i osobną stopkę. Zawinięcie tabeli meczów w rysunku służy czytelności.

### Mapa zmian

| Element | Plik | Blok / selektor / dane |
| --- | --- | --- |
| Nagłówek i profil | [detail.html](detail.html) | tytul, tresc, .pagehead, .player-profile, szczegoly. |
| Dane sezonowe | [detail.html](detail.html), [repozytorium](../../../../infrastructure/repositories/player_detail_repository.py) | .player-season-table, pobierz_szczegoly(), _pobierz_statystyki_sezonowe(), modele SkladSezonowy/Pozycja/MeczZawodnik. |
| Filtry i walidacja | [player_match_filters.py](../../../admin/forms/player_match_filters.py) | MeczeZawodnikaFilterForm; do_filtrow(). |
| Tabela meczów | [detail.html](detail.html), [repozytorium](../../../../infrastructure/repositories/player_detail_repository.py) | .player-matches-table, pobierz_mecze(), _zapytanie_meczow(). |
| HTTP i parametry | [player_detail_views.py](../../../admin/views/player_detail_views.py) | ZawodnikSzczegolyView.get(), parametry_paginacji. |
| Formatowanie | [player_detail_presenter.py](../../../presenters/player_detail_presenter.py) | SzczegolyZawodnikaPresenter i modele w interface/view_models/player_details.py. |
| Zakładki i modal | [player_details.js](../../../static/js/player_details.js) | ZakladkiZawodnikaController, SzczegolyZawodnikaController, data-player-*; `OPCJE_WYKRESOW = {prefiks: 'player', podmiot: 'zawodnika'}` dla wspólnych wykresów. Szablony ładują najpierw [goal_charts.js](../../../static/js/goal_charts.js). |
| Spis treści Formy i regularności | [detail.html](detail.html), [player_details.js](../../../static/js/player_details.js), [admin.css](../../../static/css/admin.css) | sekcje_formy, makro naglowek_sekcji(), nav.player-toc#player-forma-spis[data-player-toc], .player-toc-list, section.player-section#player-forma-*, .player-section-head, .player-kpi-groups, a[data-player-scroll], podlaczSpisTresci(). |
| Podsumowanie analityczne | [detail.html](detail.html), [repozytorium](../../../../infrastructure/repositories/player_detail_repository.py), [serwis](../../../../services/player_detail_service.py) | .player-kpi-grid, pobierz_analityke(), SzczegolyZawodnikaAnalyticsService. |
| Wykresy ECharts (Podsumowanie) | [goal_charts.js](../../../static/js/goal_charts.js), [ECharts](../../../static/vendor/echarts/echarts.min.js), [kalkulator](../../../../services/goal_statistics.py), [presenter](../../../presenters/goal_statistics_presenter.py) | AnalitykaBramekController.uruchomSezony() (data-player-season-stats, data-player-season-stats-data, opisSezonu(), opcjeSezonow(), slupekSezonu(), data-player-season-toggle, .player-chart-toggle, rysujBramkiSezonow(), opisBramekSezonu(), data-player-season-goals, .player-chart-grid.pair, .player-tooltip, .player-tooltip-breakdown, .player-season-stats-table, .player-chart-opis), StatystykiBramekCalculator.statystyki_sezonow(), statystyki_grupy(), StatystykiBramekPresenter.statystyki_sezonow(), rozklad(); uruchomRozklad(): data-player-distribution, data-player-distribution-data. |
| Forma i regularność | [detail.html](detail.html), [domena](../../../../domain/player_details.py), [serwis](../../../../services/player_detail_service.py), [presenter](../../../presenters/player_detail_presenter.py) | pobierz_forme() → StatystykiBramekCalculator.forma(); typy FormaIRegularnosc, FormaWedlugMiejsca, PunktFormy, RozstepSezonu w [domain/goal_statistics.py](../../../../domain/goal_statistics.py); FormaIRegularnoscViewModel. |
| Wykresy Formy i regularności | [goal_charts.js](../../../static/js/goal_charts.js) | FormaBramekController.uruchomTrendy() (data-player-trend-wszystkie/-dom/-wyjazd, data-player-trend-data), uruchomForme(): data-player-form-wszystkie, data-player-form-dom, data-player-form-wyjazd, data-player-boxplot, data-player-forma-data. |
| Podział u siebie/na wyjeździe | [repozytorium](../../../../infrastructure/repositories/player_detail_repository.py), [domena](../../../../domain/player_details.py) | AnalitykaMeczuZawodnika.miejsce, kolumna `miejsce` liczona z `mecze_zawodnicy.strona` z wykluczeniem niejednoznacznych meczów. |
| Defensywa rywali (sekcja Formy) | [detail.html](detail.html), [detail_views.py](../../../admin/views/player_detail_views.py) | #player-forma-defensywa, data-defense-summary, DefensywaSkrotZawodnikaController, DefensywaRywalaService.pobierz_analize(), DefensywaRywalaPresenter.przygotuj_karte(). |
| Bramki a defensywa rywali (szczegóły) | [defensywa_rywali.html](defensywa_rywali.html), [defensywa_rywali.md](defensywa_rywali.md) | Pełny opis modelu, tras, plików i mapy zmian w osobnym dokumencie. |
| Przycisk i dwuklik | [list.html](list.html), [list.md](list.md) | data-player-href, #player-detail-dialog, link Szczegóły. |
| Paginacja | [pagination.html](../../partials/pagination.html) | parametry_paginacji, strona. |
| Style i responsywność | [admin.css](../../../static/css/admin.css) | .match-detail-dialog, .match-tabs, .player-*, data-player-panel. |
