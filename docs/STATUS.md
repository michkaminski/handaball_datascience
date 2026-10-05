# Stan projektu

Aktualizacja: 2026-09-27.

## Kolejność rozgrywek w filtrach — 2026-09-27

Na zlecenie użytkownika wszystkie listy rozgrywek w filtrach mają kolejność według poziomu: Superligi (także Ekstraklasa i baraże o Superligę), Ligi Centralne, I Liga, II Liga, potem pozostałe (III i IV Liga, puchary, turnieje i inne). W obrębie poziomu baraże są za zwykłymi rozgrywkami, a reszta według nazwy (`KolejnoscRozgrywekPolicy.klucz()`, `uporzadkuj_nazwy()`, `uporzadkuj_opcje()`). Dotyczy to listy meczów, listy i karty zawodnika, defensywy rywali, karty sędziego, karty hali, karty drużyny, składów i tabel oraz terminarza; raport typowań stosował tę regułę już wcześniej. Lista rozgrywek w panelu importu zostaje bez zmian, bo nie jest filtrem. Na bazie (tylko odczyt): lista meczów zaczyna się od Ekstraklasy i Superlig, terminarz 2026/2027 od LOTTO Superligi, Lig Centralnych i I Lig. Weryfikacja: 2 nowe testy reguły; pełny zestaw 546 testów Pythona (poza błędem `SECRET_KEY`), mypy bez błędów. Bazy nie zmieniano.

## Zapowiedź meczu: kolejność kadry — 2026-09-27

Na zlecenie użytkownika kadra w zapowiedzi (strona, PDF, protokół) ma w grupie pozycji kolejność według numeru koszulki, potem nazwiska; zawodnicy bez numeru są na końcu grupy (`KadraZapowiedziCalculator._klucz()`). Wcześniej grupa była sortowana według liczby meczów.

## Zapowiedź meczu: kadra ze składu zgłoszonego przed pierwszym meczem — 2026-09-27

Na zlecenie użytkownika drużyna, która nie ma jeszcze w sezonie meczu w protokołach, dostaje w zapowiedzi, jej PDF i protokole do uzupełnienia kadrę ze składu zgłoszonego na sezon (`sklady`). Numer i pozycja pochodzą ze składu, mecze i bramki są zerowe, a źródło jest opisane przy drużynie. Na bazie z 2026-09-27 składy na 2026/2027 ma 153 drużyny (3059 wpisów); mecz 207100 — gospodarz 22 zawodniczki ze składu, gość z protokołów. Kontrakt: [schedule/preview.md](../src/handball/interface/templates/admin/schedule/preview.md). Weryfikacja: 2 testy serwisu i 1 test interfejsu; pełny zestaw 539 testów Pythona (poza błędem `SECRET_KEY`), mypy bez błędów. Bazy nie zmieniano.

## Zapowiedź meczu: protokół zawodów do uzupełnienia — 2026-09-27

Na zlecenie użytkownika (wzór: protokół ZPRP meczu 206534) zapowiedź ma przycisk **Protokół do uzupełnienia**. Otwiera on w nowej karcie pusty protokół na jednej kartce A4, bez logo i stopki ZPRP.

Z bazy uzupełnione są: numer meczu (np. SM/23), drużyny, rozgrywki, data i godzina, hala z adresem i pojemnością oraz obsada sędziowska (sędziowie, sekretarz, mierzący czas, delegat). Kadry obu drużyn mają kolejność jak w zapowiedzi (grupy pozycji, a w grupie numery koszulek) albo, do wyboru obok przycisku, według samych numerów; przy nazwisku są pozycja, rocznik, mecze, bramki i średnia w sezonie, a bramki 4 najlepszych strzelców drużyny są pogrubione; opcja „Dodaj zawodników z poprzedniego sezonu” działa także tu.

Puste do wypełnienia ręcznie: kary, osoby towarzyszące, wynik, przebieg zawodów (34 wiersze na połowę), rzuty karne, uwagi i podpisy. Wysokość wierszy dopasowuje się do liczby zawodników, więc całość zawsze mieści się na jednej stronie. Kontrakt: [schedule/protocol_pdf.md](../src/handball/interface/templates/admin/schedule/protocol_pdf.md).

Weryfikacja: 4 nowe testy interfejsu i 3 testy presentera. Pełny zestaw: 536 testów Pythona (poza istniejącym błędem `SECRET_KEY`) i 66 testów JavaScript; mypy bez błędów, Ruff bez nowych uwag. Na bazie (tylko odczyt) mecz 206533: 34 zawodników i 51 z poprzednim sezonem — po jednej stronie; odpowiedź ok. 2,3 s. Bazy nie zmieniano.

## Zapowiedź meczu: PDF na kartki A4 — 2026-09-27

Na zlecenie użytkownika zapowiedź ma przycisk **Pobierz PDF**. Otwiera on w nowej karcie całą zapowiedź jako PDF A4 w pionie, z bieżącymi opcjami kadry, uwag i okresu. Generuje go WeasyPrint (nowa zależność, decyzja w [ARCHITECTURE](ARCHITECTURE.md#dokumenty-pdf--2026-09-27)).

Podział stron:
- okładka z blokiem meczu, „W skrócie” (forma, bilans bezpośredni, prognoza, pięciu strzelców drużyn) i spisem treści z numerami stron;
- każda kadra na osobnej stronie;
- forma razem z porównaniem;
- mecze bezpośrednie;
- prognoza z krokami.

Każda strona ma nagłówek „Gospodarz — Gość”, a stopka „stan na …” i „Strona X z Y”. Kontrakt: [schedule/preview_pdf.md](../src/handball/interface/templates/admin/schedule/preview_pdf.md).

Wymaganie środowiska: biblioteki Pango (MSYS2). Instalacja jednorazowa opisana w [README](../README.md); `run.bat` sam wskazuje `C:\msys64\mingw64\bin`. Bez nich trasa PDF zwraca 503, a reszta aplikacji działa.

Weryfikacja: 5 nowych testów interfejsu i 2 testy renderera. Pełny zestaw: 530 testów Pythona (poza istniejącym błędem `SECRET_KEY`) i 66 testów JavaScript; mypy bez błędów, Ruff bez nowych uwag. Na bazie (tylko odczyt) wygenerowano PDF meczu 206529 (6 stron) i 206533 (8 stron) i obejrzano strony. Bazy nie zmieniano.

## Karta zawodnika: drużyny spoza składów sezonowych — 2026-09-26

Zakładka „Sezony i drużyny” pokazuje też drużyny, w których zawodnik ma wpisy meczowe, ale nie ma rekordu w `sklady` (zgłoszenie użytkownika: zawodnik 62101 w 2025/2026 grał w AZS UW Warszawa i ENERGA GWARDIA Koszalin, a skład sezonowy ma tylko AZS UW). Numer i pozycja takiego wiersza pochodzą z protokołów. Zakładka „Mecze” już wcześniej pokazywała obie drużyny. Kontrakt: [players/detail.md](../src/handball/interface/templates/admin/players/detail.md).

## Zapowiedź meczu: kadra, nowa kolejność sekcji — 2026-09-26

Na zlecenie użytkownika zapowiedź ma sekcje w kolejności: 1 Kadra w sezonie, 2 Forma, 3 Porównanie drużyn, 4 Mecze bezpośrednie, 5 Prognoza modelu. „Najlepszych strzelców sezonu” zastąpiła **Kadra w sezonie**: wszyscy zawodnicy z protokołów meczów drużyny w sezonie przed meczem, pogrupowani od bramkarzy, z numerem na koszulce, pozycją, liczbą meczów i bramkami. Kadra ma średnią bramek na mecz oraz kolumnę poprzedniego sezonu: bramki / średnia zawodnika we wszystkich klubach i rozgrywkach, z małą adnotacją „inny klub — bramki, mecze” i „inna liga” (inny poziom ligi niż mecz); u zawodników dodanych z poprzedniego sezonu wartości dotyczą tylko tej drużyny. Opcja dołącza zawodników, którzy w poprzednim sezonie zagrali w tej drużynie co najmniej 1 mecz (wejście na boisko, `wyjscie = true`). Przy nazwisku jest data urodzenia, a przycisk „Drukuj składy” otwiera nową kartę z kolorowymi składami obu drużyn jeden pod drugim na jednej kartce A4 (proporcje jak na stronie, całość skalowana do kartki, uwagi w jednej linii). Checkbox „Ukryj informacje o innym klubie i innej lidze” chowa te uwagi na stronie i w druku; wtedy druk ma tabele obok siebie na kartce A4 w poziomie. Pięciu najlepszych strzelców drużyny w sezonie jest oznaczonych „★ miejsce” i czerwonym polem bramek (ex aequo to samo miejsce). **Mecze bezpośrednie** pokazują wszystkie spotkania z wybranego okresu (domyślnie 10 lat; 5/15/20/wszystkie) bez limitu liczby. Kontrakt: [schedule/preview.md](../src/handball/interface/templates/admin/schedule/preview.md).

Weryfikacja: 523 testy Pythona (poza istniejącym błędem `SECRET_KEY`) i 66 testów JavaScript; mypy bez błędów, Ruff bez nowych uwag. Na bazie (tylko odczyt) mecz 206529 (ok. 1,7 s): kadry 15 i 16 zawodników (26 i 22 z poprzednim sezonem), mecze bezpośrednie 22 z 10 lat. Wygląd sprawdzony w Edge headless. Bazy nie zmieniano.

## Typowania: okno kolejki w terminarzu i raport — 2026-09-26

Na zlecenie użytkownika nazwa kolejki w **Terminarzu** otwiera okno dialogowe z typowaniami wszystkich meczów kolejki (`/administracja/terminarz/typowania`). Każdy mecz pokazuje tylko nagłówek i sześć wartości: prognoza wyniku, typ modelu, typ prognozy, przewidywana różnica, przewidywana suma i Δ rating (z HOME_ADVANTAGE). Mecz nierozegrany dostaje prognozę na teraz, a rozegrany prognozę sprzed meczu. Kontrakt: [schedule/tips.md](../src/handball/interface/templates/admin/schedule/tips.md).

Nowy raport **Typowania meczów** (Raporty › Typowania meczów, `/administracja/raporty/typowania-meczow`) ma filtry daty od–do (także przyszłe) i wielowybór rozgrywek. Domyślnie pokazuje dzisiejsze mecze wszystkich lig modelu. Wynikiem jest jedna tabela z kolumnami „Historii prognoz”, pogrupowana według ligi, rundy i kolejki, a w grupie według czasu. Ligi idą według poziomu: Superliga, Liga Centralna, I Liga, II Liga itd. Mecz rozegrany jest liczony jak w Historii prognoz, nierozegrany ma prognozę na teraz. Kontrakt: [reports/match_tips/list.md](../src/handball/interface/templates/admin/reports/match_tips/list.md).

Obie tabele raportów (Typowania meczów i Historia prognoz) mają przycisk „Drukuj tabelę”. Otwiera on nową kartę z samą tabelą jako czystym tekstem, bez grafiki i linków ([print_table.js](../src/handball/interface/static/js/print_table.js)). Historia prognoz drukuje bieżącą stronę.

Oba widoki liczą model raz na żądanie dla wszystkich meczów (`PrognozaZapowiedziService.pobierz_wiele()`). Zapytanie meczów terminarza jest wspólne (`ZapytanieMeczowTerminarza`).

Weryfikacja: 8 nowych testów jednostkowych, 9 testów interfejsu i 3 testy JavaScript. Pełny zestaw: 506 testów Pythona (poza istniejącym błędem `SECRET_KEY`) i 58 testów JavaScript; mypy bez błędów, Ruff bez nowych uwag. Na bazie (tryb tylko do odczytu) 26.09.2026: dzisiaj 38 meczów w 10 grupach; 19.09–04.10.2026 — 136 meczów (50 rozegranych, 86 przyszłych). Raport odpowiada w 1,3–1,9 s, okno kolejki w ok. 1 s. Wygląd sprawdzony w Edge headless. Bazy nie zmieniano.

## Terminarz i zapowiedź meczu — 2026-09-25

Na zlecenie użytkownika w sidebarze Dane, zaraz po „Mecze”, jest **Terminarz** (`/administracja/terminarz`). Sezon i rozgrywki są wymagane (domyślnie najnowszy sezon), runda i kolejka opcjonalne; filtry są kaskadowe. Terminarz grupuje mecze według rundy, kolejki i dnia, z godziną, halą, statusem i wynikiem zakończonych meczów. Kontrakt: [schedule/list.md](../src/handball/interface/templates/admin/schedule/list.md).

Każdy mecz ma **zapowiedź** (`/administracja/terminarz/<id_mecz>`), czyli program meczowy: nagłówek meczu, prognoza modelu `team_strength_v1`, porównanie drużyn w rozgrywkach, forma z 5 ostatnich meczów, mecze bezpośrednie i najlepsi strzelcy sezonu. Wszystkie statystyki pochodzą sprzed terminu meczu. Prognoza nierozegranego meczu to „prognoza na teraz” ze stanu modelu po wszystkich wpisanych wynikach ligi. Dla meczu zakończonego pokazujemy prognozę z raportu „Prognozy meczów” z oceną i linkiem do pełnego wyliczenia. Kontrakt: [schedule/preview.md](../src/handball/interface/templates/admin/schedule/preview.md).

Weryfikacja: 20 testów jednostkowych (serwis terminarza, statystyki zapowiedzi, prognoza bieżąca i po meczu), 8 testów interfejsu i 3 testy JavaScript. Pełny zestaw: 485 testów Pythona (poza istniejącym błędem `SECRET_KEY`) i 53 testy JavaScript; mypy bez błędów, Ruff bez nowych uwag. Na bazie (tryb tylko do odczytu): LOTTO Superliga 2026/2027 ma 132 mecze w 22 kolejkach; zapowiedzi meczów nierozegranych, zakończonych i z `zamiana` zwracają 200, brak meczu 404. Wygląd sprawdzony w Edge headless. Zapowiedź ładuje się 2–4 s, bo backtest jest liczony przy każdym żądaniu. Bazy nie zmieniano.

Następny krok (propozycja): cache wyniku backtestu na czas żądania/procesu, jeśli czas zapowiedzi będzie przeszkadzał, oraz tabela ligowa „przed meczem” w zapowiedzi (wymaga ustalenia reguł punktacji).

## Szczegóły meczu: okno drużyny — 2026-09-25

Na zlecenie użytkownika nazwy gospodarza i gościa w nagłówku szczegółów meczu otwierają kartę drużyny: kliknięcie w oknie modalnym, dwuklik w nowej karcie. Działa na pełnej stronie i w modalu listy meczów. Identyfikatory drużyn (`mecze.id_zespol_gosp`/`id_zespol_gosc`) przechodzą przez `DaneMeczu` do modelu widoku i są zamieniane razem z nazwami przy `zamiana=true`. Mechanikę okna przejęto bez zmian z tabel ligowych (`classification_details.js`). Kontrakt: [matches/detail.md](../src/handball/interface/templates/admin/matches/detail.md#okno-drużyny).

Weryfikacja: 2 nowe testy interfejsu (linki z zamianą, brak linku bez identyfikatora, kolejność skryptów) i 2 testy JavaScript (klik, dwuklik). Pełny zestaw: 457 testów Pythona (poza istniejącym błędem `SECRET_KEY`) i 50 testów JavaScript; mypy bez błędów, Ruff bez nowych uwag (istniejące E501 w `tests/integration/test_import_repository.py`). Nie sprawdzano w przeglądarce. Bazy nie zmieniano.

## Raporty: Prognozy meczów — siła drużyn — 2026-09-24

Na zlecenie użytkownika dodano główną zakładkę **Raporty** (górny pasek i grupa sidebara) z katalogiem raportów oraz pierwszy raport: historyczny backtest modelu **Dynamic Team Strength V1** (`team_strength_v1`) dla Superligi mężczyzn i kobiet, a od 2026-09-25 także Ligi Centralnej i I Ligi.

- `/administracja/raporty` — katalog raportów; kolejne raporty dodaje się bez przebudowy sekcji.
- `/administracja/raporty/prognozy-meczow` — gęsta tabela z 28 kolumnami: ratingi przed meczem, Δ rating, prognoza i wynik, błędy H/A/różnicy/sumy, typ 1X2, trafienie, score error i klasa. Nad nią podsumowanie: trafność 1X2, MAE, średni i medianowy score error oraz progi ≤ 2/4/6. Filtry: model, rozgrywki (Superliga, Liga Centralna, I Liga), płeć, sezon, liczba sezonów raportu (3/5/10/15/wszystkie, domyślnie 10), drużyna, trafność i ocena. Na końcu parametry modelu i liczby pominiętych meczów.
- `/administracja/raporty/prognozy-meczow/<id_mecz>` — pełna strona szczegółów. Zawiera wynik prognozy, dane wejściowe i 8 kroków (definicja, wzór, podstawienie, wynik, interpretacja). Dalej: znaczenie aktualizacji, ratingi przed i po, historia 10 meczów obu drużyn, snapshot parametrów i definicje.
- Poziom rozpoznajemy po nazwie: „Superliga”/„Superligę”/„Ekstraklasa”, „Liga Centralna” oraz „I Liga” jako osobne słowa (bez II i III Ligi); płeć po `rozgrywki.plec`. Każda liga ma osobny model. Na bazie z 2026-09-25: 12 156 prognoz w raporcie, backtest ok. 1,1 s na żądanie. Reguły danych: [DATA](DATA.md#ligi-w-raportach-prognoz--2026-09-25), decyzje: [ARCHITECTURE](ARCHITECTURE.md#raport-prognoz-meczów--2026-09-24).

Wynik na bazie z 2026-09-24: 3453 prognozy z sezonów 2016/2017–2026/2027, rozgrzewka 2007/2008–2015/2016. Trafność 1X2 wynosi 68,0%. MAE gospodarza 3,65, gościa 3,50, różnicy 4,11, sumy 5,86. Średni score error to 7,16, mediana 6,44. Parametry to wartości startowe ze specyfikacji, bez strojenia. Model punktowy prawie nigdy nie typuje remisu.

Ograniczenia: snapshoty są liczone w pamięci przy każdym żądaniu, a nie zapisywane w bazie (zob. ARCHITECTURE). Zamiast wykresu historii ratingu jest tabela.

Weryfikacja: 32 testy modelu, 16 testów serwisów, 9 testów interfejsu i 5 testów JavaScript. Pełny zestaw: 428 testów Pythona (poza istniejącym błędem `SECRET_KEY`) i 48 testów JavaScript; mypy i Ruff bez błędów. Na bazie (tryb tylko do odczytu) sprawdzono odpowiedzi 200/400/404 oraz wygląd w Edge headless: listę i szczegóły meczu #206654. Bazy nie zmieniano.

Uzupełnienie tego samego dnia (na prośbę użytkownika): kolumna **Ocena wyniku** porównuje zaokrągloną prognozę z wynikiem. Klasy: Dokładny wynik, Dokładna różnica (np. 29:30 przy 30:31), Różnica ±1, ±2–3, ±4+. Filtry mają checkboxy „Dokładny wynik”, „Poprawna różnica bramek”, a obie oceny wybiera się checkboxami z wieloma wartościami. Na bazie: dokładny wynik 24 (0,7%), dokładna różnica 275 (8,0%), różnica ±1 lub lepiej 851 (24,6%) z 3453 prognoz. Kolejne uzupełnienie: kolumna **Typ prognozy** (typ 1X2 z zaokrąglonego wyniku prognozy i czy się sprawdził; 38:20 przy 20:38 to „Nieprzewidziany”) z filtrem checkboxowym; dawna kolumna „Typ” nazywa się teraz „Typ modelu”, filtr **Wynik 1X2** (H/X/A) i filtr „Trafiony” (TAK/NIE). Na bazie poprawny typ prognozy ma 2415 z 3453 prognoz (69,9%).

Następny krok (propozycja): strojenie parametrów na okresie rozgrzewki i porównanie z prostymi punktami odniesienia (zawsze gospodarz, średnia ligi), a potem probabilistyczny typ 1X2.

## Karta drużyny: Zestawienie sezonu, „Tylko zakończone”, okno zawodnika — 2026-09-23

Na zlecenia użytkownika:

- **Zestawienie sezonu** (nowa zakładka karty drużyny): sezon wymagany (domyślnie najnowszy), filtry rozgrywek i przeciwnika. Zawodnicy są w wierszach, uporządkowani według pozycji (bramkarze na górze), a mecze w kolumnach z pionowym nagłówkiem (data, przeciwnik, D/W, wynik). W komórce: bramki, kary i karne wykorzystane/wszystkie. Na końcu „Podsumowanie sezonu” (Mecze, Bramki, Kary, Karne), w stopce sumy drużyny. Bez przewijania pionowego tabeli.
- **Mecze w karcie drużyny:** checkbox „Tylko zakończone”, domyślnie zaznaczony, z tym samym warunkiem co lista meczów (wspólny `WarunkiMeczuSql`).
- **Okno zawodnika:** w składach szczegółów meczu, w Zestawieniu sezonu i w zakładce Zawodnicy kliknięcie nazwiska otwiera kartę zawodnika w oknie modalnym, a dwuklik — w nowej karcie. Mechanikę wydzielono z modalu listy zawodników do wspólnych `OknoZawodnikaController` i `LinkiZawodnikowController` (`player_details.js`).

Kontrakty: [teams/detail.md](../src/handball/interface/templates/admin/teams/detail.md), [matches/detail.md](../src/handball/interface/templates/admin/matches/detail.md).

Weryfikacja: nowe testy interfejsu (zestawienie, sezon wymagany i 400 dla obcego sezonu, podsumowanie, kolejność pozycji, checkbox, linki okna), testy reguły pozycji i 4 testy JavaScript linków (klik, dwuklik, Enter, Ctrl+klik, brak okna). Pełny zestaw: 367 testów Pythona (poza błędem `SECRET_KEY`) i 40 testów JavaScript; mypy i Ruff bez błędów. Na bazie (tryb tylko do odczytu, tymczasowy serwer) sprawdzono w Edge: Zestawienie Wisły Płock 2025/2026 (25 meczów), okno zawodnika otwierane z zestawienia i ze składu meczu #189180 oraz filtr „Tylko zakończone” (2026/2027: 4 z 23 meczów). Bazy nie zmieniano.

## Poprawka: zawodnicy po złych stronach przy zmianie gospodarza — 2026-09-23

Na zgłoszenie użytkownika poprawiono przypisanie zawodników przy `zamiana=true`. `mecze_zawodnicy.strona` ma już stronę po zamianie (potwierdzone na składach sezonowych we wszystkich sezonach), a aplikacja odwracała ją drugi raz. Szczegóły meczu nie zamieniają już składów. Wszystkie repozytoria łączą stronę wpisu z drużyną przez nową, wspólną regułę `StronyMeczuSql`: karta zawodnika (drużyna i przeciwnik w meczach, drużyny sezonów, filtr przeciwnika), lista zawodników, defensywa rywali, karta hali, aktualności i zakładka Zawodnicy karty drużyny. Przykład: mecz #189180 pokazuje teraz zawodniczki Galiczanki pod Galiczanką. Lista zawodników Wisły Płock spadła z 329 do 178 osób, bo 152 osoby były zawodnikami rywali z 21 meczów z zamianą. Opis: [DATA](DATA.md#strona-wpisów-zawodników-przy-zamiana--2026-09-23).

Weryfikacja: nowy test reguły na SQLite w pamięci (cztery kombinacje strony i zamiany oraz `inne`) i nowy test defensywy rywali przy zamianie. Pięć istniejących testów utrwalało błędne założenie lub dawny kształt wiersza i zostało poprawionych. Pełny zestaw: 354 testy Pythona (poza błędem `SECRET_KEY`) i 36 testów JavaScript; mypy i Ruff bez błędów. Na bazie (tryb tylko do odczytu) sprawdzono mecz #189180 i odpowiedzi 200 kart zawodnika, drużyny, hali, listy zawodników i strony Start. Bazy nie zmieniano.

## Frekwencja: lista meczów i karta drużyny — 2026-09-23

Na zlecenie użytkownika lista meczów ma kolumnę **Widzowie** (`mecze.widzowie`, separator tysięcy, „—” przy braku danych), umieszczoną przed Halą. Karta drużyny pokazuje frekwencję w trzech pierwszych zakładkach:

- **Dane podstawowe:** sekcja „Frekwencja w całej historii” (średnia, mediana, suma, rekord z linkiem do meczu i pokrycie, osobno u siebie i na wyjeździe) oraz średnia widzów w tabeli hal.
- **Sezony:** kolumny ze średnią widzów u siebie i na wyjeździe oraz sumą u siebie, dla sezonów i rozgrywek.
- **Mecze:** te same kafelki dla zakresu filtrów i kolumna Widzowie.

Liczone są tylko mecze rozegrane. 0 (mecz bez publiczności) wchodzi do średniej, brak danych nie. Frekwencja jest częścią `BilansDruzyny` (`FrekwencjaDruzynyCalculator`). Dane o widzach są w bazie od 2011/2012; w 2020/2021 większość meczów ma 0.

Weryfikacja: 2 nowe testy kalkulatora, 2 testy interfejsu karty i 1 test listy meczów. Pełny zestaw: 352 testy Pythona (poza błędem `SECRET_KEY`) i 36 testów JavaScript; mypy i Ruff bez błędów. Na bazie (tryb tylko do odczytu) wartości #272 zgadzają się z bezpośrednim zapytaniem SQL, a lista meczów i zakładki karty renderują się w Edge headless przy 1440 px. Bazy nie zmieniano.

## Karta drużyny — 2026-09-23

Na zlecenie użytkownika dodano `GET /administracja/druzyny/<id_zespol>` z zakładkami Dane podstawowe, Sezony, Mecze, Zawodnicy, Podsumowanie, Forma i regularność. Lista drużyn ma przycisk „▣ Szczegóły” (nowa karta).

- Sezony pokazują bilans Z/R/P, bramki i średnie dla każdego sezonu i rozgrywek.
- Mecze pokazują wynik z perspektywy drużyny, z filtrami i paginacją.
- Zawodnicy to historia z protokołów (mecze, bramki, średnia, karne, kary, sezony), z filtrami, sortowaniem i osobną paginacją.
- Podsumowanie i Forma są analogiczne do karty zawodnika i opisują zdobyte bramki drużyny. Podsumowanie ma dodatkowo wykres Z/R/P według sezonu i rekordy meczów.

Z/R/P wynika z pełnego wyniku, a rozstrzygnięcia remisów po dogrywce lub karnych są pokazane osobno. Zasady: [DATA](DATA.md#karta-drużyny--2026-09-23), kontrakt: [teams/detail.md](../src/handball/interface/templates/admin/teams/detail.md).

Na kolejne prośby Podsumowanie oraz Forma i regularność pokazują **bramki zdobyte i stracone razem** na tych samych wykresach, bez przełącznika serii. Podsumowanie:

- tabela miar zdobyte / stracone / różnica;
- wspólny wykres średniej, mediany i dominanty według sezonu;
- sumy sezonu w dwóch stosach rozgrywek;
- rozkład z przełącznikiem miejsca.

Forma i regularność:

- statystyki opisowe w trzech kolumnach;
- mecz po meczu z medianami obu serii;
- bilans bramek ze średnią kroczącą różnicy;
- forma krocząca obu serii;
- boxploty sezonów parami.

Dane łączy presenter; obie serie i różnicę liczy ten sam kalkulator. Średnie z kalkulatora są zawsze liczbą zmiennoprzecinkową (wcześniej całkowita średnia wyświetlała się bez miejsca po przecinku, także na karcie zawodnika). Weryfikacja: 347 testów Pythona (poza błędem `SECRET_KEY`) i 36 testów JavaScript; mypy i Ruff bez błędów. Na #272 Podsumowanie i Forma zwracają 200 i poprawnie renderują się w Edge headless przy 1440 px.

Obliczenia, formatowanie i wykresy statystyk bramek wydzielono z karty zawodnika do wspólnych modułów (`goal_statistics`, `goal_charts.js`), zob. [ARCHITECTURE](ARCHITECTURE.md#wspólna-analityka-bramek--2026-09-23). Poprawiono mapowanie `Zespol`: nieistniejącą kolumnę `miasto` zastąpiono `nr_klubu`. Fragment paginacji przyjmuje opcjonalne `parametr_strony`.

Weryfikacja: 7 nowych testów serwisu, 8 testów interfejsu i 3 testy JavaScript. Pełny zestaw: 345 testów Pythona (poza znanym błędem `SECRET_KEY`) i 34 testy JavaScript; Ruff i mypy dla `src` bez błędów. Na bazie (tryb tylko do odczytu) drużyna #272 zwraca 200 we wszystkich zakładkach w 0,4–0,8 s, nieistniejąca drużyna 404, a niepoprawne sortowanie 400. Wszystkie zakładki sprawdzono w Edge headless przy 1440 px. Nie zrobiono modalu na liście drużyn ani linków do karty z innych ekranów (np. szczegółów meczu). Bazy nie zmieniano.

## Mecze: filtr „Tylko zakończone” — 2026-09-23

Lista meczów ma checkbox „Tylko zakończone”, domyślnie zaznaczony: pokazuje mecze z terminem przed dzisiejszym dniem (Europe/Warsaw) albo z wpisanym wynikiem. Stan jest zachowywany w sortowaniu, paginacji i pamięci filtrów dzięki parze checkbox + ukryte `zakonczone=0`; brak parametru oznacza stan domyślny. Nowy test interfejsu (domyślne zaznaczenie, odznaczenie, zachowanie w linkach); pełny zestaw 330 testów Pythona (poza błędem `SECRET_KEY`) i 31 testów JavaScript, Ruff i mypy bez błędów. Na bazie w sezonie 2026/2027 filtr zwraca 125 z 1945 meczów (123 z wynikiem i 2 po terminie bez wyniku). Kontrakt: [list.md](../src/handball/interface/templates/admin/matches/list.md).

## Import tabel wybranego sezonu — 2026-09-23

Na zlecenie użytkownika panel importu (`/administracja/import`) ma nową sekcję „Import tabel”: wybór sezonu z bazy (domyślnie bieżący) i rozgrywek tego sezonu, pobranie z ZPRP wyłącznie tabel (`pokaz_tabele_spis.php`, `pokaz_tabela.php`, wszystkie grupy) i zwykły podgląd z zatwierdzeniem. Dotychczasowe tryby (pełny i uzupełniający dla 2026/2027) pozostały bez zmian. Importer obsługuje teraz tabele `tabele`, `tabele_grupy` i `tabele_wiersze` z łańcuchem kluczy rozwiązywanym od rodzica; drużyny z tabel są tylko dopisywane lub uzupełniane; wierszy nie usuwa. Sezon przebiegu zastąpił stałą 195 w blokadzie, historii i kontekście audytu (stare przebiegi mają domyślnie 195). Opis: [IMPORTS.md](IMPORTS.md#import-tabel-wybranego-sezonu), [panel.md](../src/handball/interface/templates/admin/import/panel.md).

Weryfikacja: 15 nowych przypadków testowych (mapper spisu i tabeli, serwis i walidacja sezonu/rozgrywek, rekurencyjne rozwiązywanie kluczy, odczyt list tylko do odczytu, panel i POST); pełny zestaw 329 testów Pythona (poza tym samym błędem `SECRET_KEY`) i 31 testów JavaScript, Ruff i mypy bez błędów. Na prawdziwym API ZPRP i bazie wykonano przebieg tylko do podglądu (2026/2027, Superliga M i Liga Centralna M): istniejące tabele i grupy rozpoznane, 14 nowych i 12 zmienionych wierszy. Zapisu do bazy nie wykonano; stan roboczy tego sprawdzenia był w katalogu tymczasowym, poza historią panelu.

## Start: Aktualności — 2026-09-23

Na zlecenie użytkownika strona Start (`GET /administracja/`) zamiast makiety listy meczów pokazuje aktualności bieżącego sezonu w stylu klasycznego portalu sportowego: ostatnie mecze w osobnych ramkach dla Superligi M i K oraz Lig Centralnych M i K, tabelę najnowszych wyników pozostałych rozgrywek, ciekawostki sezonu (sezon w liczbach, najwięcej bramek w meczu, najwyższe zwycięstwo, najlepszy występ indywidualny, najbardziej bramkostrzelna liga) i najlepszych strzelców lig priorytetowych. Ligi rozpoznawane są po nazwie i płci rozgrywek bieżącego sezonu, a nie po utrwalonych ID. Oficjalna tabela `public.strzelcy` jest dla bieżącego sezonu nieaktualna (stan po 1. kolejce, bez Lig Centralnych), więc strzelcy są liczeni z protokołów `mecze_zawodnicy`, co strona opisuje wprost. Nowe warstwy: `domain/news.py`, `contracts/news_repository.py`, `AktualnosciSQLAlchemyRepository`, `AktualnosciService` z `KategoriaRozgrywekPolicy`, `AktualnosciPresenter`; `StartView` dostaje zależności z `ZaleznosciZadaniaFactory`. Kontrakt: [start.md](../src/handball/interface/templates/admin/start.md).

Weryfikacja: 22 nowe przypadki testowe (serwis, presenter, repozytorium, interfejs; testy strony Start nie łączą się już z bazą, tylko używają repozytorium w pamięci); pełny zestaw 314 testów Pythona (poza tym samym błędem `SECRET_KEY`) i 31 testów JavaScript, Ruff i mypy bez błędów. Na rzeczywistej bazie (sezon 2026/2027, 123 rozegrane mecze, ostatni wynik 20.09.2026) strona zwraca 200 i renderuje się poprawnie w Edge przy 1440 px i w ramce 390 px. Inspekcję bazy wykonano w transakcjach READ ONLY zakończonych ROLLBACK; bazy nie zmieniano.

## Wykresy karty zawodnika w zakładce Forma i regularność — 2026-09-23

Na prośbę użytkownika wszystkie wykresy analityczne karty zawodnika zebrano w zakładce Forma i regularność. W Podsumowaniu został tylko histogram „Rozkład bramek: wszystkie, u siebie i na wyjeździe” (z nową tabelą danych). Do Formy i regularności przeniesiono trzy wykresy „Forma mecz po meczu” (wszystkie, u siebie, na wyjeździe) oraz skrót „Bramki zawodnika a poziom defensywy rywali” z przyciskiem „Pokaż szczegóły”; zakładka Statystyki, która po przeniesieniu byłaby pusta, została usunięta (`zakladka=statystyki` nie jest już akceptowana). Forma i regularność ma spis treści z pięcioma sekcjami: Statystyki opisowe, Bramki mecz po meczu, Forma krocząca, Regularność według sezonu, Defensywa rywali. Sekcja defensywy nadal obejmuje całą karierę i nie reaguje na filtry zakładki — opisuje to notatka. Zmiana dotyczy tylko szablonu, JavaScriptu i CSS; obliczenia, zapytania i serwisy są bez zmian. Kontrakt: [detail.md](../src/handball/interface/templates/admin/players/detail.md).

Weryfikacja: zaktualizowane testy interfejsu (podział wykresów między panele, kotwice spisu treści, brak zakładki Statystyki, sekcja defensywy) i JavaScript (histogram w Podsumowaniu, sześć wykresów Formy, przewijanie spisu treści z `prefers-reduced-motion`) przechodzą. Pełny zestaw: 287 z 288 testów Pythona bez integracyjnych (ten sam środowiskowy błąd `SECRET_KEY`) i 29 testów JavaScript; Ruff i mypy bez błędów. Na rzeczywistej karcie #1732, na tymczasowej instancji aplikacji, potwierdzono odpowiedź 200, poprawne dane JSON wszystkich sekcji i renderowanie w Edge headless (1440 px). Działający serwer na porcie 5057 wymaga restartu, aby pokazać zmiany. Bazy nie zmieniano.

Na kolejną prośbę użytkownika dopracowano wygląd zakładki w stylu strony: spis treści jako kafelki z numerem, opisem i liczbą wykresów, każda sekcja jako karta z nagłówkiem i przyciskiem „↑ Spis treści”, akcenty z palety strony oraz statystyki opisowe w czterech grupach (Poziom, Zakres, Rozrzut, Udziały meczów). Sprawdzono w Edge headless przy 1440 px i w ramce 390 px; testy interfejsu i JavaScript zaktualizowano i przechodzą.

Forma krocząca ma teraz jako pierwszy wykres wariant „wszystkie mecze” (`FormaIRegularnoscZawodnika.wszystkie`), z oknem 5/10 meczów liczonym ze wszystkich meczów zakresu, także tych o nieustalonym miejscu; warianty u siebie i na wyjeździe są bez zmian. Nowy test serwisu sprawdza okno kroczące niezależne od miejsca; na karcie #1732 wariant ma 231 punktów (114 u siebie + 117 na wyjeździe). Pełny zestaw: 288 testów Pythona (poza tym samym błędem `SECRET_KEY`) i 29 testów JavaScript.

Sekcja „Bramki zawodnika a poziom defensywy rywali” reaguje teraz na filtry zakładki (sezon, rozgrywki, przeciwnik). Przeciwnik jest rozwiązywany w repozytorium po dowolnej historycznej nazwie zespołu (`pobierz_zespoly_o_nazwie()`), tak jak w pozostałych sekcjach karty. Filtry zawężają wyłącznie mecze zawodnika; kontekst ligowy i Defense Factor pozostają liczone z pełnych danych sprzed meczu. „Pokaż szczegóły” przenosi filtry, strona szczegółowa ma pole przeciwnika, a jej link powrotu, który po usunięciu zakładki Statystyki zwracał 400, prowadzi teraz do sekcji defensywy w Formie i regularności. Zgłoszone znikanie formy kroczącej po filtrowaniu wynikało z nieaktualnego serwera na porcie 5057 (stary szablon w pamięci przy nowym JS z dysku); na aktualnym kodzie filtr działa. Weryfikacja: nowy test serwisu (filtr przeciwnika bez zmiany Defense Factor), dwa nowe testy interfejsu; 291 testów Pythona (poza błędem `SECRET_KEY`) i 29 testów JavaScript, Ruff i mypy bez błędów; na karcie #1732 filtry sezonu i przeciwnika zmieniają liczebność klas, a strona szczegółowa z filtrami zwraca 200. Bazy nie zmieniano.

W Podsumowaniu nad histogramem dodano wykres „Średnia, mediana i dominanta bramek na mecz według sezonu”; na prośbę użytkownika oś pokazuje sezony (wszystkie rozgrywki razem), a podział na rozgrywki jest w okienku po najechaniu i w tabeli danych. Statystyki sezonu i każdych rozgrywek w sezonie (mecze, suma, średnia, mediana, dominanty, Q1–Q3, min–maks) liczy serwis w Pythonie. Sezony z mniej niż 5 meczami są oznaczone jako mała próba, a obydwa wykresy Podsumowania mają jednozdaniowy opis. Weryfikacja: nowy test serwisu (grupowanie, dominanty wielokrotne, braki), rozszerzony test interfejsu i nowy test JavaScript (serie, romby dominant, escapowanie tooltipa); 292 testy Pythona (poza błędem `SECRET_KEY`) i 30 testów JavaScript, Ruff i mypy bez błędów; na karcie #1732 wykres ma 9 sezonów, a okienko dla 2012/2013 pokazuje podsumowanie sezonu i podział na I Ligę i Puchar Polski (sprawdzone w Edge headless przez `showTip`).

Na kolejną prośbę wykres miar dostał przełącznik „Linie / Słupki” (domyślnie linie, płynne przejście z poszanowaniem `prefers-reduced-motion`), a obok niego pojawił się wykres słupkowy „Liczba bramek w sezonie”: suma sezonu i obok słupki poszczególnych rozgrywek, z okienkiem pokazującym podział. Zmiana dotyczy tylko szablonu, JavaScriptu i CSS — dane pochodzą z tych samych statystyk sezonów liczonych w Pythonie. Nowy test JavaScript sprawdza serie wykresu bramek, escapowanie okienka i przełączanie widoków; 31 testów JavaScript i 292 testy Pythona (poza błędem `SECRET_KEY`) przechodzą, a oba widoki i okienko sprawdzono na danych #1732 w Edge headless. Następnie, na zgłoszenie zbyt cienkich słupków, liczba słupków w sezonie zależy od największej liczby rozgrywek w jednym sezonie (dla #1732: 3 + suma), a nie od liczby wszystkich rozgrywek w karierze; kolor i wzór zostają przypisane do nazwy rozgrywek, a ukrycie rozgrywek w legendzie poszerza pozostałe słupki. Bazy nie zmieniano.

## Bramki zawodnika a poziom defensywy rywali — 2026-09-22

Na wyraźne, szczegółowe zlecenie użytkownika zaimplementowano nową analizę, spoza pierwotnego planu [PLAYER_DATA_SCIENCE](PLAYER_DATA_SCIENCE.md): „Bramki zawodnika a poziom defensywy rywali”. Karta zawodnika dostała szóstą zakładkę „Statystyki” z kompaktowym wykresem (średnia bramek w pięciu klasach jakości defensywy rywala, z n przy każdej klasie) i przyciskiem „Pokaż szczegóły”, który otwiera pełny raport data-science na osobnej stronie (`GET /administracja/zawodnicy/<id>/defensywa-rywali`), w nowej karcie przeglądarki — nie w modalu. Karta pozostaje prosta: bez wzorów, regresji, Pearsona, Spearmana, R² ani metodologii; wszystko to jest wyłącznie na stronie szczegółowej. Pełny opis metody, sekcji strony i mapy zmian: [defensywa_rywali.md](../src/handball/interface/templates/admin/players/defensywa_rywali.md); zmiany w karcie zawodnika opisano też w [detail.md](../src/handball/interface/templates/admin/players/detail.md).

Jakość defensywy rywala liczona jest wyłącznie ze stanu **przed** analizowanym meczem (bez data leakage), względem średniej ligowej tych samych rozgrywek (`GA_league`), z shrinkage przy małej liczbie wcześniejszych meczów rywala (`GA_smoothed = (n×GA_team + k×GA_league)/(n+k)`, `k` konfigurowalne, domyślnie 5) i opcjonalnym, domyślnie wyłączonym priorem z poprzedniego sezonu (dopasowanym po nazwie rozgrywek, bez automatycznego wykrywania awansu/spadku). Pięć klas Defense Factor ma konfigurowalne granice. Dla każdej klasy liczone są: n, suma, średnia, mediana, min/maks, Q1/Q3, wariancja próbki, odchylenie standardowe, udziały progowe (1+/3+/5+/8+/10+, konfigurowalne) oraz whiskery i wartości odstające regułą Tukeya do boxplota. Cała matematyka (w tym Pearson, Spearman na rangach z uśrednionymi remisami, regresja liniowa z β0/β1/R² i przybliżonym 95% przedziałem ufności) jest liczona w czystym, testowalnym module Pythona (`services/opponent_defense_service.py`), bez zależności od Flaska, ORM ani nowych bibliotek numerycznych (projekt nie używa numpy/scipy — zgodnie z [TECH_STACK](TECH_STACK.md)).

Strona szczegółowa ma 14 sekcji ze spisem treści (wynik analizy, główny wykres, sortowalna tabela źródłowa, wyjaśnienie GA_team/shrinkage/Defense Factor/klas ze wzorami i przykładami liczbowymi, statystyki opisowe z boxplotem, wykres prawdopodobieństw progowych, korelacja ze scatterplotem, regresja z interpretacją Δbramki dla +0,10 Defense Factor, wybieralny krok-po-kroku przykład jednego meczu, końcowa interpretacja matematyczna łącząca wszystkie miary i sekcja ograniczeń). Automatyczny komentarz na karcie i stronie wynika z rzeczywistej różnicy średnich między klasami, nie jest zawsze efektownym wnioskiem. Filtry: sezon, rozgrywki, miejsce (u siebie/na wyjeździe), ostatnie N sezonów, przełącznik „wszystkie mecze” (domyślnie tylko mecze z pełnymi danymi).

Weryfikacja: 20 nowych testów jednostkowych serwisu (shrinkage, n=0/1/2, klasyfikacja, korelacje, regresja, filtry, poprzedni sezon, brak wycieku danych z przyszłości), 6 testów repozytorium (rozwiązywanie strony z surowych kolumn bez stosowania `zamiana`, niejednoznaczność, unpivot meczów ligowych, dopasowanie poprzednich rozgrywek), 6 testów interfejsu i 2 testy JavaScript (cztery wykresy strony szczegółowej: słupki, boxplot, prawdopodobieństwa, scatter; wykres skrótu na karcie) przechodzą. Pełny zestaw: 287 z 288 testów Pythona bez integracyjnych z bazą (jedyny nieprzechodzący jest środowiskowy, niezwiązany ze zmianą) i 29 testów JavaScript. Mypy i Ruff (check i format) bez błędów. Na rzeczywistej karcie zawodnika #1732 (229 meczów) potwierdzono odpowiedzi 200 obu stron, poprawne dane JSON wszystkich czterech wykresów, działający filtr miejsca (229 → 114 dla „u siebie”) oraz przykład krok po kroku dla rzeczywistego meczu z 2017 roku. Bazy nie zmieniano.

## Podsumowanie analityczne zawodnika — 2026-09-22

Karta zawodnika zachowuje istniejące zakładki Profil, Sezony i drużyny oraz Mecze i dodaje po nich Podsumowanie. Nowa zakładka ma filtry sezonu, rozgrywek i przeciwnika, KPI z liczbą meczów, bramkami, średnią, medianą, dominantami, kwartylami, karnymi, karami i pokryciem danych. Trend bramek i histogram renderuje lokalny Apache ECharts 6.1.0; wykresy mają animacje, punkty, wygaszenie kontekstu, ARIA, tabelę danych i tryb ograniczonego ruchu. Kliknięcie punktu trendu otwiera kartę meczu.

Zapytanie tylko do odczytu agreguje wpisy do poziomu mecz–zawodnik przed obliczeniami. Definicje statystyczne znajdują się w osobnym serwisie, a prezentacja w presenterze. Biblioteka wraz z LICENSE i NOTICE jest przechowywana lokalnie. Pozostałe zakładki projektu Data Science są nadal planem.

Weryfikacja: 248 testów Pythona bez integracyjnych testów bazy i 26 testów JavaScript przechodzi; Ruff dla zmienionego zakresu, formatowanie, mypy, składnia JavaScriptu i kontrola diffu przechodzą. Rzeczywista karta zawodnika i lokalny zasób ECharts zwracają `200`. Edge headless potwierdził dwa wykresy SVG z opisami ARIA na szerokościach 1440 i 390 px. Bazy nie zmieniano.

## Forma i regularność zawodnika — 2026-09-22

Karta zawodnika ma drugą dodatkową zakładkę, Forma i regularność, po Podsumowaniu. Pokazuje statystyki opisowe liczone wyłącznie z meczów ze znaną liczbą bramek w wybranym zakresie: średnią, medianę, wszystkie dominanty, minimum, maksimum, Q1–Q3, IQR, odchylenie standardowe (populacyjne), MAD, współczynnik zmienności (pomijany przy średniej poniżej 0,1 bramki na mecz), P10, P90, średnią uciętą 10% oraz udziały meczów z 0, 1–2, 3–5 i 6+ bramkami.

Wykres formy pokazuje bramki mecz po meczu kolorowane według sezonu, medianę i średnią kroczącą z 5 ostatnich meczów ze znaną liczbą bramek oraz, po osiągnięciu 10 takich meczów, dodatkową medianę kroczącą z 10. Okno liczone jest po kolejności meczów, nie po dniach; nieznana liczba bramek przerywa okno zamiast zamieniać się w zero. Poniżej progu 5 meczów pokazuje się jawne ostrzeżenie zamiast trendu. Drugi wykres to boxplot bramek według sezonu z wąsami ograniczonymi regułą Tukeya i osobno oznaczonymi wartościami odstającymi; sezon z mniej niż 5 znanymi meczami jest oznaczony jako mała próba. Oba wykresy mają tabelaryczny odpowiednik, opis ARIA i lokalny Apache ECharts 6.1.0. Zakładka korzysta z tego samego zapytania analitycznego co Podsumowanie, bez dodatkowego zapytania do bazy.

Przy okazji usunięto z karty cztery zakładki-placeholdery (Bramki i karne, Dyscyplina, Rekordy, Jakość danych), które były widoczne w interfejsie, lecz powielały dane Podsumowania bez własnej logiki ani stylów — niezgodnie z zasadą projektu, by nie przedstawiać planowanych funkcji jako gotowych. Wrócą jako osobno zaimplementowane zakładki w kolejnych etapach [PLAYER_DATA_SCIENCE](PLAYER_DATA_SCIENCE.md).

Na zgłoszenie użytkownika poprawiono czytelność wykresów liniowych (trend bramek w Podsumowaniu i wykres formy w Formie i regularności): przy wielu sezonach były nieczytelne w wąskiej połowie siatki obok drugiego wykresu. Oba wykresy w każdej z tych zakładek są teraz ułożone jeden pod drugim na pełną szerokość panelu (`.player-chart-grid.stacked` w `admin.css`) zamiast obok siebie.

Na kolejne zgłoszenie użytkownika te same wykresy pokazują od razu podział na mecze u siebie i na wyjeździe. Podsumowanie: trend bramek rozdzielono na dwa osobne wykresy (u siebie, na wyjeździe), każdy z własną medianą liczoną tylko z meczów tego miejsca; histogram rozkładu bramek pokazuje dwa słupki obok siebie na każdą liczbę bramek zamiast jednej sumy. Forma i regularność: wykres formy również rozdzielono na dwa, przy czym mediana i średnia krocząca (5, a od 10 meczów też mediana krocząca 10) są liczone niezależnie w obrębie każdego miejsca — piątka meczów u siebie pomija mecze wyjazdowe rozgrywane pomiędzy nimi, więc pokazuje rzeczywistą formę w danym miejscu, a nie ogólną formę przefiltrowaną wizualnie. Boxplot sezonów pozostaje jednym, wspólnym wykresem (podział nie był proszony).

Miejsce meczu jest liczone w `pobierz_analityke()` z `mecze_zawodnicy.strona` (`gosp`→u siebie, `gosc`→na wyjeździe) w tym samym zapytaniu agregującym, bez dodatkowego zapytania do bazy. Mecz z niejednoznaczną lub nieustaloną stroną (np. same wpisy `inne`, albo sprzeczne `gosp`/`gosc` w tym samym meczu przy kilku wpisach) ma miejsce nieustalone i jest pomijany w obu podziałach — zgodnie z zasadą projektu, by nie zgadywać jednej wartości dla niejednoznacznego agregatu, zamiast domyślnie przypisywać go do jednej ze stron.

Weryfikacja: 2 nowe testy repozytorium (jednoznaczne i niejednoznaczne miejsce meczu), 1 nowy test serwisu (niezależne okno kroczące per miejsce) oraz zaktualizowane testy interfejsu i oba testy JavaScript (formy i podsumowania) przechodzą. Pełny zestaw: 255 z 256 testów Pythona bez integracyjnych z bazą (jedyny nieprzechodzący jest środowiskowy, niezwiązany ze zmianą) i 27 testów JavaScript. Mypy i Ruff (check i format) bez błędów. Na rzeczywistej karcie zawodnika #1732 potwierdzono odpowiedzi 200 dla obu zakładek oraz poprawne dane JSON: pole `miejsce`/`miejsce_etykieta` w punktach Podsumowania, `mediana_dom`/`mediana_wyjazd`, słupki `dom`/`wyjazd` w rozkładzie i zagnieżdżone `dom`/`wyjazd` z osobnymi punktami formy w danych zakładki Forma i regularność. Bazy nie zmieniano.

Na dalsze doprecyzowanie użytkownika zakładka Podsumowanie pokazuje teraz trzy wykresy formy zamiast dwóch — „Forma mecz po meczu (wszystkie)” obok wariantów u siebie/na wyjeździe — a histogram „Rozkład bramek” ma trzy słupki na każdą liczbę bramek: Wszystkie, U siebie, Na wyjeździe. Mediana i liczniki wariantu „wszystkie” były już liczone wcześniej (KPI karty), więc zmiana dotyczyła tylko szablonu i `AnalitykaZawodnikaController` w JavaScripcie, bez zmian w repozytorium ani serwisie. Zakładka Forma i regularność pozostaje bez wariantu „wszystkie” — nie był proszony. Testy interfejsu i JavaScript zaktualizowano pod nowy układ; pełny zestaw testów pozostaje zielony poza tymi samymi dwoma wcześniej udokumentowanymi, nieistotnymi wyjątkami. Sprawdzono na rzeczywistej karcie #1732.

Weryfikacja: 5 nowych testów jednostkowych serwisu, 1 nowy test interfejsu i 1 nowy test JavaScript przechodzą. Pełny zestaw: 253 z 254 testów Pythona bez integracyjnych z bazą (jedyny nieprzechodzący jest środowiskowy, niezwiązany ze zmianą — zależy od lokalnej zmiennej `SECRET_KEY`) i 27 testów JavaScript. Mypy i Ruff (check i format) bez błędów dla zmienionego zakresu. Na rzeczywistej karcie zawodnika #1732 (231 meczów, sezony 2008/2009–2025/2026) potwierdzono odpowiedź 200, poprawne dane wykresów, oznaczenie sezonu jako małej próby i realny punkt odstający w rozstępie sezonowym. Bazy nie zmieniano.

## Grupowane tabele i składy — 2026-09-22

Listy `/administracja/tabele` i `/administracja/sklady` prezentują rekordy zbiorcze zamiast płaskich pozycji. Tabele są grupowane według sezonu, rozgrywek, tabeli i grupy. Składy są grupowane według sezonu i drużyny, a przypisane rozgrywki są pokazywane jako lista oddzielona przecinkami. Przycisk „Szczegóły” otwiera pełną kartę w nowej karcie, a dwuklik lub Enter na wierszu otwiera tę samą treść w modalu. Szczegóły tabeli pokazują wybraną grupę źródłowej klasyfikacji. Zawodnicy w szczegółach składu są uporządkowani według pozycji i oznaczeni paletą ze składów meczowych. Bazy nie zmieniano.

Weryfikacja: 15 testów interfejsu klasyfikacji przechodzi; Ruff, formatowanie i mypy przechodzą. Po poprawie kolejności argumentów `string_agg` rzeczywista lista zwróciła 3233 składy w transakcji READ ONLY zakończonej ROLLBACK. Kontrakty: [lista tabel](../src/handball/interface/templates/admin/standings/list.md), [szczegóły tabeli](../src/handball/interface/templates/admin/standings/detail.md), [lista składów](../src/handball/interface/templates/admin/rosters/list.md), [szczegóły składu](../src/handball/interface/templates/admin/rosters/detail.md).

## Szczegóły sędziego — 2026-09-21

Zaimplementowano `GET /administracja/sedziowie/<id_sedzia>` z zakładkami Dane, Mecze i Statystyki. Karta zawiera filtrowaną historię meczów, zbiorczo pobieranych partnerów, aktywność sezonową, rankingi rozgrywek i drużyn oraz kompaktowe wykresy HTML/CSS. Filtry sezonu i rozgrywek obejmują tabele i wykresy; filtr drużyny obsługuje stronę gospodarz/gość i zakres dat. Lista sędziów prowadzi do karty. Zapytania są tylko do odczytu i uwzględniają `mecze.zamiana`. Kontrakt: [detail.md](../src/handball/interface/templates/admin/referees/detail.md).

Weryfikacja: 14 testów szczegółów i katalogów przechodzi; Ruff, formatowanie, mypy i kontrola składni JavaScriptu dla zmienionego zakresu przechodzą. Rzeczywista lista i karta sędziego `#365` zwróciły `200` na PostgreSQL w konfiguracji READ ONLY; bazy nie zmieniano.
## Lista sędziów — 2026-09-21

Zaimplementowano GET /administracja/sedziowie: wyszukiwanie po nazwisku i mieście, filtr miasta, sortowanie w nagłówkach, paginację oraz liczbę różnych meczów powiązanych z osobą w obsadzie przez public.mecze_sedziowie. Pozycja „Sędziowie” w menu prowadzi do aktywnego widoku. Strona jest wyłącznie do odczytu; nie wykonano zmian w bazie. Kontrakt i mapa zmian: [list.md](../src/handball/interface/templates/admin/referees/list.md).

Weryfikacja: 11 testów interfejsu katalogów przechodzi; mypy oraz Ruff dla zmienionych plików przechodzą. Bazy nie odczytywano ani nie zmieniano.

## Sezony, Rozgrywki i Drużyny — 2026-09-21

Działają listy `/administracja/sezony`, `/administracja/rozgrywki` i `/administracja/druzyny`. Mają zwarte filtry, sortowanie w nagłówkach, paginację, aktywne pozycje menu oraz linki do listy meczów zachowujące sezon. Drużyny są prezentowane jako historyczne migawki sezonowe. Zapytania i liczniki zweryfikowano na istniejącej bazie w transakcji READ ONLY zakończonej ROLLBACK; bazy nie zmieniono. Pełna regresja bez integracji obejmuje 223 przechodzące testy.

## Lista hal — 2026-09-21

Zaimplementowano GET /administracja/hale: wyszukiwanie po nazwie i adresie, filtr miasta i minimalnej pojemności, sortowanie w nagłówkach, paginację oraz liczbę meczów powiązanych z halą. Pozycja „Hale” w menu prowadzi do aktywnego widoku. Strona jest wyłącznie do odczytu; nie wykonano zmian w bazie. Kontrakt i mapa zmian: [list.md](../src/handball/interface/templates/admin/venues/list.md).

Weryfikacja: 9 testów interfejsu hal przechodzi; mypy i Ruff dla kodu aplikacji oraz nowych testów przechodzą. Pełny zestaw 201 testów bez integracji z bazą przechodzi po odizolowaniu lokalnej zmiennej HDS_IMPORT_PASSWORD w procesie testowym. Bazy nie odczytywano ani nie zmieniano.

## Karta hali — 2026-09-21

Działa GET /administracja/hale/<id>: Dane, Mecze, Zawodnicy i Statystyki. Karta pokazuje pola hali, podsumowanie, filtrowane i paginowane rozegrane mecze, filtrowanych i sortowanych zawodników oraz rankingi TOP 10 drużyn, rozgrywek, najczęściej grających i najskuteczniejszych zawodników. Rankingi można rozszerzyć. Linki prowadzą do kart meczu i zawodnika. Kontrakt: [detail.md](../src/handball/interface/templates/admin/venues/detail.md).

Zakładka Statystyki zawiera również wygodną nawigację sekcji, trendy meczów i średniej bramek według sezonu, profil oraz histogram wyników, mecze wyrównane, heatmapę sezon × miesiąc, rozkład dni tygodnia, frekwencję z kompletnością, opisowe porównanie ze średnią hal i rekordy linkujące do kart meczów. Wykresy są lekkim, responsywnym HTML/CSS bez dodatkowej zależności.

Zapytania agregujące, w tym trendy, percentyle, frekwencję, porównania i rekordy, zweryfikowano na istniejącej bazie w transakcji READ ONLY zakończonej ROLLBACK; bazy nie zmieniono. Przechodzi 214 testów Pythona bez integracji i 25 testów JavaScript. Mypy, Ruff, kontrola formatowania i diffu przechodzą. Testy sprawdzają zakładki, filtry, walidację, linki, wykresy, rekordy, TOP 10 i rozszerzenie rankingów.

Poniższe opisy etapów zachowują wyniki wcześniejszych weryfikacji. Wynik migracji nazw z 2026-09-14 podano osobno; nie ponawiano historycznych kontroli na bazie użytkownika.

## Karta zawodnika — 2026-09-20

Działa `/administracja/zawodnicy/<id>`: Profil, Sezony i drużyny oraz Mecze. Profil pokazuje najnowszy dostępny wzrost i wagę. Historia zachowuje numer i pozycję rekordu sezon–drużyna oraz rozbija podsumowania na rozgrywki: bramki, karne i kary. Mecze mają filtry sezonu, rozgrywek i przeciwnika, sortowanie daty oraz paginację po 20 różnych meczów. Na liście działa „Szczegóły” w nowej karcie oraz dwuklik/Enter w modalu. Filtry i paginacja działają również w modalu. Kontrakt: [detail.md](../src/handball/interface/templates/admin/players/detail.md).

Weryfikacja po rozszerzeniu podsumowań sezonowych: 191 testów Pythona bez integracyjnych testów bazy; 25 testów JavaScript łącznie, w tym 7 nowych dla karty. Mypy oraz Ruff i formatowanie kodu oraz testów jednostkowych, interfejsu i helperów przechodzą. W Edge sprawdzono dwuklik, Enter, zamykanie Escape, fokus, zakładki, dane sezonowe, paginację, filtrowanie i czyszczenie w modalu oraz szerokości 1440 i 390 px. Odświeżono lokalny serwer bez automatycznego przeładowania; lista i karta zwracają 200. Przez GET rzeczywistej aplikacji potwierdzono również strony 1–20 i 21–40 zawodnika z 551 meczami. Nie uruchamiano zapisów do bazy ani pełnego audytu importu.

## Lista zawodników — 2026-09-20

Zaimplementowano `GET /administracja/zawodnicy` i aktywną pozycję menu. Lista na wzór meczów ma filtry sezonu, rozgrywek, drużyny, pozycji, rocznika i imienia/nazwiska; sortowanie w nagłówkach, paginację oraz niezależną pamięć filtrów. Zamiast liczby meczów i bramek pokazuje najnowszy dostępny wzrost oraz wagę, wybierane niezależnie z historii składów. Kontrakt i mapa zmian: [list.md](../src/handball/interface/templates/admin/players/list.md).

Weryfikacja po zmianie kolumn: 192 testy Pythona bez integracji z bazą i 24 testy JavaScript przechodzą. Mypy, formatowanie oraz Ruff dla kodu aplikacji i testów jednostkowych/widoków bez błędów. Pełny `ruff check .` wskazuje istniejący E501 w `tests/integration/test_import_repository.py:98`; tego pliku nie zmieniano. Regresję uruchomiono z pustym `HDS_IMPORT_PASSWORD` w procesie testowym, aby lokalna konfiguracja importu nie zmieniała klucza sesji testów.

Porównano z prototypem v6 w lokalnym Edge. Sprawdzono widok na danych testowych przy 1440 px i emulowanym viewport 390 px: dokument nie przewija się poziomo, tabela przewija się we własnym kontenerze, menu mobilne działa. Po odświeżeniu lokalnego serwera potwierdzono na rzeczywistym odczycie wyszukiwanie zawodnika, obecność wartości wzrostu i wagi oraz brak kolumn meczów i bramek. Bazy nie zmieniano.

## Warstwy danych i prezentacji — 2026-09-19

Wydzielono `interface/presenters/` oraz `interface/view_models/`. Repozytorium meczów zwraca liczby, flagi, daty i braki danych w typowanych obiektach domeny. Reguły stron, statusu i maksimum bramek są w `domain/match_rules.py`; etykiety, teksty wyniku, kolory i modele szablonów powstają w presenterach składanych przez fabrykę zależności. Usunięto poprzedni moduł `interface/match_presenter.py`. Zapytania i ścieżka importu pozostają bez zmian.

Weryfikacja: 130 testów Pythona bez integracji z bazą oraz 11 testów JavaScript przechodzi; mypy i Ruff dla kodu oraz testów jednostkowych/widoków bez błędów. Testy obejmują też typy i niezależność danych od ORM, brakujące wartości, zmianę stron i kierunek zależności warstw. Nie uruchamiano rzeczywistej bazy ani importu. Zaktualizowano [strukturę](DIRECTORY_STRUCTURE.md), [UML](UML.md) i [decyzję](ARCHITECTURE.md).

## Podgląd meczu i prezentacja składów — 2026-09-19

Istniejący widok szczegółów można otworzyć z listy w nowej karcie linkiem „Szczegóły” albo w modalu dwuklikiem lub klawiszem Enter na wierszu. Składy są grupowane według źródłowej pozycji i numeru koszulki, z pastelowymi kolorami pozycji i czerwonym wyróżnieniem komórek bramek liderów każdej drużyny osobno (również ex aequo). Szczegóły mają zakładki „Dane podstawowe”, „Wynik i statystyki” i „Składy”; legenda wyróżnień znajduje się pod tabelami składów. Aktualny kontrakt: [detail.md](../src/handball/interface/templates/admin/matches/detail.md). Sprawdzenie tej zmiany: 22 testy widoków i prezentacji, 11 testów JavaScript (modal, zakładki i pamięć filtrów), mypy oraz Ruff dla zmienionego Pythona przechodzą. Nie wykonano kontroli wizualnej w przeglądarce ani odczytu rzeczywistej bazy. Poniższe historyczne opisy etapów mogą poprzedzać istniejącą implementację szczegółów.

## Import i prezentacja meczów — 2026-09-19

Dodano tryb uzupełniający: wybiera z bazy mecze sezonu 2026/2027 sprzed dzisiejszego dnia z brakującym wynikiem lub składem jednej strony, pomija walkowery i wycofane spotkania, pobiera tylko szczegóły i uzupełnia brakujące wartości. Pełny import pozostaje dostępny do odkrywania spotkań i korekt. Opis ograniczeń, przepływu i zapisu: [IMPORTS](IMPORTS.md). Klient API zachowuje trzysekundowy odstęp między żądaniami w jednym procesie. Lista meczów uwzględnia `zamiana`, odwracając drużyny wraz z wynikiem. Zmiany nie obejmują uruchomienia rzeczywistego importu ani modyfikacji bazy przez AI. Weryfikacja: 85 testów bez integracji z bazą przechodzi, z wyłączonym hasłem importu w środowisku procesu testów; mypy oraz Ruff dla kodu i testów jednostkowych/widoków przechodzą. Zapytania wyboru kandydatów nie uruchamiano na rzeczywistym PostgreSQL.

## Runda i kolejka na liście meczów — 2026-09-19

Dodano filtry po nazwie rundy i kolejki oraz dwie opcjonalne kolumny włączane osobno w modalu „Widoczne kolumny”. Kolumny są domyślnie ukryte; wybór zapamiętuje przeglądarka. Filtry są stale dostępne. Kontrakt, zachowanie i aktualny spis elementów: [list.md](../src/handball/interface/templates/admin/matches/list.md).

## Gotowe

- Przyjęta nazwa Handball DataScience i katalog projektu.
- Instrukcje AGENTS.md, dokumentacja zakresu, architektury i danych.
- Opis ról AI oraz trzy projektowe skillsy.
- Użytkownik potwierdził wcześniejszy import bazy.
- Zweryfikowano połączenie `localhost:5432/zprp` jako `postgres` i rzeczywisty schemat PostgreSQL 15.1 w trybie tylko do odczytu.
- [Opisano bazę](database/README.md): 65 tabel, 2 widoki, kolumny, klucze, indeksy, triggery, funkcje i relacje. Liczby rekordów mają oznaczony czas odczytu.
- Zapisano zakaz samodzielnych zmian w bazie; konkretna zmiana wymaga wyraźnej prośby użytkownika.

- Przyjęto obiektowy Python, SOLID, role specjalisty Flask/SQLAlchemy i [standardy kodu](CODING_STANDARDS.md).
- [Wybrano technologie](TECH_STACK.md): Python 3.13, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, psycopg 3 oraz narzędzia jakości.

- Przyjęto [konwencję nazewnictwa z 2026-09-14](CODING_STANDARDS.md#język-i-nazewnictwo): angielskie pliki, katalogi, moduły i pakiety; polska domena, metody i zmienne bez znaków diakrytycznych; angielskie role klas, np. MeczService i MeczRepository. Udokumentowano niezależność domeny od języka przyszłej bazy. Konwencję wdrożono w istniejącym kodzie: pakiet `handball`, angielskie katalogi i pliki, klasy z rolami technicznymi, importy, konfiguracja narzędzi, `run.bat`, szablony i ich opisy. Odświeżono lokalną instalację pakietu. Weryfikacja migracji: 37 testów jednostkowych i widoków przechodzi, w tym kontrola CSS i JS; Ruff i mypy bez błędów. Wszystkie moduły i 6 szablonów HTML załadowano przy zablokowanym dostępie do bazy; sprawdzono 151 lokalnych odnośników. Testów bazy nie uruchamiano.

- Wskazano prototyp administracji v6 jako wzorzec wyglądu; potwierdzono dostępność katalogu i przeczytano jego README.
- Zapisano [kolejność realizacji](IMPLEMENTATION_PLAN.md) z kryteriami ukończenia etapów.

- Przygotowano [projekt katalogów](DIRECTORY_STRUCTURE.md) i [UML](UML.md): diagramy klas, kompozycji oraz sekwencji listy meczów.
- Utworzono 11 [opisów szablonów](TEMPLATES.md) w docelowym katalogu szablonów. Istnieją katalogi i pliki MD, bez HTML.

- Ukończono etap 1 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): obiektowy szkielet Flaska. Utworzono `pyproject.toml`, `uv.lock`, `.python-version` i `.gitignore`; `uv sync` instaluje Flask 3.1.3 zgodnie z TECH_STACK.
- Utworzono klasy `Ustawienia`, `AplikacjaFactory`, `WidokiRegistrar`, Blueprint `admin` z `StartView` oraz adapter `create_app()` w `src/handball/`.
- Skonfigurowano Ruff, mypy (strict) i pytest w `pyproject.toml`. Wykonano i potwierdzono: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` (bez błędów, 8 plików źródłowych) oraz `uv run pytest` (6 testów, wszystkie przechodzą).
- Zweryfikowano lokalne uruchomienie: `create_app()` rejestruje trasy `/administracja/` i `/static/...`, żądanie GET zwraca 200; start nie łączy się z bazą `zprp`.

- Ukończono etap 2 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): wspólny układ administracji na podstawie prototypu v6. Utworzono `base.html`, `partials/navigation.html`, `partials/messages.html`, `admin/start.html`, `static/css/admin.css` i `static/js/admin.js` (adaptacja `index.html`/`assets/style.css`/`assets/app.js` prototypu). Na wyraźne polecenie użytkownika strona startowa odwzorowuje pełną strukturę index.html (nagłówek, filtry, tabela z nagłówkami kolumn), nie tylko okrojony komunikat tekstowy — tabela ma jeden wiersz z jawną informacją o braku danych zamiast fikcyjnych wierszy z prototypu, a filtry nie są jeszcze podłączone do żadnej logiki.
- Układ zawiera sidebar (`aside.sidebar`, dwukolumnowa siatka jak w prototypie) z jedną realną pozycją "Start" — zamiast pełnego menu prototypu z pozycjami bez odpowiadających widoków. Rozwijanie sidebara na wąskim ekranie (przycisk "☰ Menu") obsługuje `static/js/admin.js`.
- `AplikacjaFactory` jawnie konfiguruje `template_folder`/`static_folder`/`static_url_path` (`templates`/`static`), zgodnie z ARCHITECTURE i DIRECTORY_STRUCTURE. `StartView` renderuje `admin/start.html` zamiast zwracać czysty tekst.
- Zaktualizowano MD czterech zaimplementowanych szablonów (baza, nawigacja, komunikaty, start) zgodnie z rzeczywistym kontraktem, blokami i selektorami.
- Sprawdzono wizualnie w przeglądarce (Playwright, Chromium headless) na ~1400px i ~380px, w tym bezpośrednie porównanie zrzutu z prototypem v6 i test kliknięcia "☰ Menu": układ zgodny z v6, responsywność działa, brak przewijania poziomego.

- Ukończono etap 3 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): warstwa danych do odczytu meczów. Dodano zależności SQLAlchemy 2.0.52, Flask-SQLAlchemy 3.1.1, psycopg 3.2.13 (`uv add`).
- Modele ORM (schemat `public`, bez `relationship()`, złączenia jawne w repozytorium): `Sezon`, `Rozgrywki`, `Runda`, `Kolejka` (infrastructure/database/models/competitions.py), `Zespol`, `ZespolSezon` (teams.py), `Mecz` (matches.py, pola potrzebne liście; rozszerzenie o wynik szczegółowy w etapie 5) — kolumny i klucze odwzorowane z [PUBLIC_SCHEMA](database/PUBLIC_SCHEMA.md).
- Obiekty domenowe `FiltryMeczow`, `PozycjaListyMeczow`, `StronaMeczow` (domain/matches.py, z walidacją strony/rozmiaru/sortowania) oraz błędy `NieZnalezionoMeczu`, `BladOdczytuDanych` (domain/errors.py).
- Kontrakt `MeczReadRepository` (contracts/match_repository.py) — na razie tylko `pobierz_liste`; `pobierz_szczegoly` dochodzi w etapie 5 zgodnie z UML.
- `MeczSQLAlchemyRepository.pobierz_liste` (infrastructure/repositories/match_repository.py): filtruje po sezonie/rozgrywkach/rundzie/kolejce, łączy `zespoly_sezony` (migawka sezonowa, nie `zespoly.nazwa` — zgodnie z DATA.md) osobnym aliasem dla gospodarza i gościa, LEFT JOIN dla nieustalonych uczestników, stabilne sortowanie po dacie i id, paginacja z limitem i osobnym zapytaniem o liczbę wszystkich, jawne rozróżnienie braku wyniku od 0:0.
- `PolaczenieConfigurator.skonfiguruj_odczyt` wymusza `execution_options={"postgresql_readonly": True}` na silniku SQLAlchemy (READ ONLY dla każdej transakcji, także po ponownym użyciu połączenia z puli). `extensions.py` inicjalizuje Flask-SQLAlchemy (`baza_danych`) powiązaną z `Baza(DeclarativeBase)`. `AplikacjaFactory` wpina oba elementy; start aplikacji nie łączy się z bazą (silnik SQLAlchemy jest leniwy).
- `Ustawienia` rozszerzone o `host_bazy`/`port_bazy`/`nazwa_bazy`/`uzytkownik_bazy`/`haslo_bazy` i właściwość `adres_bazy_danych`. Utworzono `.env.example` bez sekretów.
- Weryfikacja etapu 3: `ruff check`, `ruff format --check`, `mypy` — bez błędów.

- Ukończono etap 4 [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): działająca lista meczów. `MeczService` (services/match_service.py, cienka delegacja do repozytorium — celowo, bez przedwczesnej logiki), `ZaleznosciZadaniaFactory` (request_dependencies.py, tworzy repozytorium+serwis per żądanie, wstrzykiwalna w testach), `MeczListView` i `MeczFilterForm` (WTForms, waliduje `id_sezon` jako wymagane, resztę jako opcjonalne).
- `interface/errors.py`: `obsluz_blad_domeny` mapuje `NieZnalezionoMeczu`→404, `BladOdczytuDanych`→503 (na razie domyślne strony Flaska; własny wygląd `errors/*.html` pozostaje do zrobienia). `MeczSQLAlchemyRepository` tłumaczy `SQLAlchemyError` na `BladOdczytuDanych`.
- Trasa `GET /administracja/mecze` (endpoint `administracja.lista_meczow`) zwraca 400 przy braku `id_sezon`, w przeciwnym razie renderuje `admin/matches/list.html` z filtrami (GET, bez CSRF) i paginacją (`partials/pagination.html`, zachowuje wszystkie parametry query przy zmianie strony).
- **Przeprojektowano nawigację na wyraźne polecenie użytkownika**: sidebar i górny pasek pokazują teraz **pełne** menu prototypu v6 (grupy Dane [10 pozycji]/Import-eksport [3]/Narzędzia [3], z ikonami), nie tylko pozycję "Start". Nowy moduł `interface/navigation.py` (`GORNY_PASEK`, `SIDEBAR`, poza pierwotnym planem DIRECTORY_STRUCTURE) wstrzykuje strukturę menu globalnie przez `context_processor`; widoki przekazują tylko `sekcja_aktywna` (string). Pozycje bez widoku mają `punkt_koncowy=None` → renderują się jako `href="#"`, widoczne ale nieaktywne (nie 404).
- `MeczInMemoryRepository` (tests/helpers/match_repository.py) — implementacja testowa kontraktu `MeczReadRepository`, używana w testach serwisu i widoku bez potrzeby bazy. `tests/` stało się pakietem (`__init__.py`), żeby te importy działały.
- **Zweryfikowano wobec prawdziwej bazy `zprp` w tej sesji** (hasło ustawione lokalnie przez użytkownika, nigdzie nie zapisane w dokumentacji ani w historii poleceń pokazywanej użytkownikowi): `uv run pytest tests/integration` — 3/3 przechodzi (lista dla sezonu 195/1817 meczów, pusta lista dla nieistniejącego sezonu, wymuszenie READ ONLY faktycznie blokuje zapis). Ręcznie w przeglądarce: pierwsza i druga strona listy z prawdziwymi meczami i wynikami, pusty wynik dla nieistniejącego sezonu, błąd 400 przy braku `id_sezon`, pełny sidebar z aktywną pozycją "Mecze"/"Dane". Kryterium etapu 3 i 4 "pobranie danych działa z istniejącym schematem" jest w pełni potwierdzone, nie tylko teoretycznie.
- **Uwaga bezpieczeństwa, nie do przeoczenia**: `src/handball/settings.py` ma teraz na dysku domyślną wartość `BAZA_HASLO` wpisaną wprost w kodzie (do wygodnych testów lokalnych). To narusza własną zasadę projektu (sekrety tylko ze środowiska, nigdy w kodzie) i **nie powinno trafić do commita** — użytkownik świadomie zdecydował zostawić to lokalnie, ale wyraźnie zastrzegł, żeby nie commitować tego pliku. Przy każdym `git add`/`git commit` obejmującym `settings.py` należy to przypomnieć.
- Weryfikacja etapu 4: `ruff check`, `ruff format --check`, `mypy` (32 pliki źródłowe) — bez błędów; `pytest`: 23/23 przechodzi (z `BAZA_HASLO` ustawionym lokalnie), 20 przechodzi / 3 pomijane bez niego.

- **Poprawka po zgłoszeniu użytkownika**: kliknięcie "Mecze"/"Dane" w menu dawało 400 (`id_sezon` wymagane), bo linki menu nie przekazują parametrów. Dodano `SezonReadRepository`/`SezonSQLAlchemyRepository` (contracts/season_repository.py, infrastructure/repositories/season_repository.py — poza pierwotnym planem DIRECTORY_STRUCTURE) i `ZaleznosciZadaniaFactory.utworz_repozytorium_sezonow()`. `MeczListView` bez `id_sezon` w query teraz przekierowuje (302) do najnowszego sezonu (`MAX(sezony.id)`) zamiast zwracać błąd; zweryfikowano ręcznie wobec żywej bazy (`id_sezon=195`) i testami (`test_lista_meczow_bez_id_sezon_przekierowuje_do_domyslnego`).
- **Dodano 12 wstępnych notatek MD** dla pozostałych pozycji sidebara bez widoku (Sezony, Rozgrywki, Drużyny, Zawodnicy, Składy, Tabele, Strzelcy, Hale, Sędziowie, Import/eksport [1 notatka dla 3 pozycji], Kontrola danych [1 notatka dla 2 pozycji], Logi) na wyraźne polecenie użytkownika — patrz [TEMPLATES](TEMPLATES.md), sekcja "Wczesne notatki planistyczne". To krótkie punkty startu (źródło w prototypie, przybliżone tabele bazy), nie ustalone kontrakty — większość stron prototypu v6 poza `players.html`/`quality.html` to same placeholdery ("Przykładowa strona administracyjna"), więc nie ma z czego wiernie skopiować układu.

- **Przebudowano filtry listy meczów na wyraźne polecenie użytkownika** (przycisk "Filtruj" był za duży, filtry pokazywały surowe ID zamiast nazw): sezon i rozgrywki to teraz rozwijane listy z nazwami (`OpcjaWyboru`, `SlownikiMeczowService`, contracts/repositories `seasons.py`/`competitions.py`/`venues.py` — wszystkie poza pierwotnym planem DIRECTORY_STRUCTURE); `id_sezon` jest teraz opcjonalny (pusty wybór = wszystkie sezony, usunięto wcześniejsze przekierowanie do najnowszego sezonu). Dodano model `Hala` (`infrastructure/database/models/venues.py`) i kolumnę "Hala" w tabeli i filtrach. Dodano wyszukiwanie po nazwie drużyny (`szukaj_druzyny`, ILIKE na gospodarzu lub gościu) oraz po dacie w formacie częściowym: rok (`2026`), rok-miesiąc (`2026-01`) albo pełna data (`2026-01-15`) — parsuje `zakres_z_czesciowej_daty()` w domain/matches.py, niepoprawny format zwraca czytelny błąd 400. Usunięto filtry `id_runda`/`id_kolejka` (nie były używane w interfejsie, użytkownik ich nie prosił). Poprawiono CSS (`.pole-przycisku`), żeby przycisk "Filtruj" nie rozciągał się na całą kolumnę siatki. Zweryfikowano ręcznie wobec żywej bazy `zprp`: filtr sezonu pokazuje "2026/2027" (nie ID), wyszukiwanie "Kielce" zwraca 169 trafień z poprawnymi nazwami hal, błędny format daty zwraca czytelny komunikat po polsku. `pytest`: 34 przechodzi, 3 integracyjne pomijane bez `BAZA_HASLO`.

- **Druga runda poprawek listy meczów, też na wyraźne polecenie użytkownika**: sortowanie przeniesione z pola w filtrach na klikalny nagłówek kolumny "Data" (rosnąco/malejąco, zachowuje pozostałe filtry, resetuje stronę) — **zapisano to jako trwałą konwencję projektu** w [CODING_STANDARDS](CODING_STANDARDS.md) ("Listy z filtrami") i w skillu `hds-flask-feature`, żeby dotyczyła też przyszłych list. Dodano kolumny Sezon i Rozgrywki (INNER JOIN, pola NOT NULL w `mecze`). Usunięto podpowiedź formatu z pola daty (użytkownik nie chciał podpowiedzi w samym polu). Wyszukiwanie drużyny przeprojektowane: zamiast dopasowania tekstu per wiersz, najpierw rozwiązuje nazwę do `id_zespol` (przez `zespoly_sezony`), potem filtruje mecze po tym stałym identyfikatorze — dzięki temu jedna historyczna nazwa (np. "Industria Kielce") znajduje też mecze z sezonów, gdy zespół nazywał się inaczej (np. "Vive Kielce"). Test integracyjny `test_szukaj_druzyny_znajduje_zespol_we_wszystkich_sezonach` to potwierdza wobec żywych danych — przy okazji ujawnił, że krótkie nazwy historyczne (np. "MKS Zagłębie Lubin") mogą dodatkowo dopasować niepowiązane zespoły (rezerwy/młodzieżowe o podobnej nazwie); test dobiera jednoznaczną nazwę, żeby nie być przypadkowo kruchy, a ograniczenie jest udokumentowane w list.md jako naturalna cecha wyszukiwania tekstowego, nie błąd. `pytest`: 39/39 (z `BAZA_HASLO`).

- **Trzecia runda poprawek: filtr Rozgrywki po nazwie, nie po ID sezonowym.** Użytkownik zauważył, że filtr "Rozgrywki" pokazywał tę samą nazwę (np. "I Liga Mężczyzn Grupa A") osobno dla każdego sezonu, bo w bazie każdy sezon ma własny wiersz `rozgrywki` z tą samą `nazwa`. `FiltryMeczow.id_rozgrywki` (int) zmieniono na `rozgrywki: str | None` (nazwa); `RozgrywkiSQLAlchemyRepository.pobierz_nazwy()` zwraca `DISTINCT` nazwy zamiast pary (id, nazwa); `MeczSQLAlchemyRepository` filtruje przez `Rozgrywki.nazwa == filtry.rozgrywki` na już istniejącym złączeniu (dokładne dopasowanie, bo nazwa pochodzi z zamkniętej listy, nie wolnego tekstu). Efekt: lista rozwijana "Rozgrywki" nie ma ani jednego duplikatu, a wybór nazwy pokazuje mecze ze wszystkich sezonów tej nazwy. Dodano testy integracyjne `test_pobierz_nazwy_rozgrywek_sa_unikalne` i `test_filtr_rozgrywki_po_nazwie_obejmuje_wiele_sezonow` — **zweryfikowane wobec żywej bazy**: "I Liga Kobiet" faktycznie obejmuje 6 sezonów i 750 meczów, dropdown potwierdzony bez duplikatów zliczeniem wystąpień w renderowanym HTML. `pytest`: 41/41 (z `BAZA_HASLO`).

## Jeszcze niewykonane

- Podgląd ostatnich meczów bezpośrednio na stronie startowej (obecnie: tylko przycisk do pełnej listy) — świadomie odłożone.
- Dostęp administratora i pozostałe widoki odczytu (etapy 6–7).
- Dodatkowe pozycje sidebara podłączone do realnych widoków (obecnie większość to `href="#"`) — razem z odpowiadającymi im widokami/etapami.
- Kaskadowe odświeżanie listy rozgrywek po zmianie sezonu bez przeładowania strony (obecnie: zwykły GET, bez JS) — możliwe usprawnienie później.
- Własny wygląd stron błędów (`errors/400.html`, `404.html`, `503.html`) — na razie domyślne strony Flaska.
- Pozostałe szablony (logowanie) — ma MD, brak HTML.
- Eksport i publiczny serwis.

## Następny krok

Odczyt listy i karty zawodnika potwierdzono przez lokalną aplikację. Do dalszej weryfikacji pozostają pełna kompletność i wydajność archiwum. Następnie dostęp administratora i kolejne uzgodnione widoki z [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md). Lista i szczegóły meczów oraz lista zawodników są zaimplementowane; warstwy opisują DIRECTORY_STRUCTURE i UML.

Nie używać `python ../run.py` jako komendy uruchomienia nowej aplikacji: dotyczy starszego serwisu i jego procesu importu.

## Składy, Strzelcy i Tabele — 2026-09-21

Zaimplementowano trzy zakładki administracyjne tylko do odczytu: filtry sezonu i rozgrywek, wyszukiwanie, sortowanie, paginację oraz aktywne pozycje menu. Składy opisują zgłoszenia sezonowe, a klasyfikacje zachowują wartości źródłowe bez przeliczania.
