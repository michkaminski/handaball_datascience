# Profesjonalna analityka Data Science karty zawodnika

## Cel dokumentu

Dokument projektuje rozbudowę karty `GET /administracja/zawodnicy/<id>` z perspektywy statystyka, analityka danych i analityka piłki ręcznej. Kolejność nowych zakładek i funkcji wynika z wartości decyzyjnej, jakości dostępnych danych i kosztu poprawnej implementacji.

Nie jest to opis funkcji już wdrożonych. Poniższy zakres jest planem rozwoju opartym na rzeczywistym schemacie bazy.

### Zakres nienaruszalny

Obecna karta i jej trzy zakładki pozostają w dotychczasowej postaci:

1. `Profil`;
2. `Sezony i drużyny`;
3. `Mecze`.

Nie należy zmieniać ich nazw, zawartości, filtrów, paginacji ani dotychczasowych zachowań. Nie należy przenosić istniejących informacji do nowych widoków. Wszystkie opisane dalej statystyki i wykresy są dodatkowymi zakładkami umieszczonymi po obecnych trzech. Nowa analityka może prowadzić do istniejących zakładek lub szczegółów meczu, lecz nie zastępuje ich.

### Stan wdrożenia

Zaimplementowano dwie dodatkowe zakładki. `Podsumowanie`: KPI opisowe, pokrycie danych, filtry sezonu, rozgrywek i przeciwnika, trend bramek z medianą i rekordem oraz histogram bramek. `Forma i regularność`: pełne statystyki opisowe (średnia, mediana, dominanty, min/maks, Q1–Q3, IQR, odchylenie standardowe, MAD, współczynnik zmienności, P10/P90, średnia ucięta 10%, udziały bramkowe), wykres formy z medianą i średnią kroczącą (5, a od 10 meczów też mediana krocząca 10) oraz boxplot bramek według sezonu z wykrywaniem wartości odstających regułą Tukeya. Wykresy korzystają z lokalnego Apache ECharts 6.1.0. Na prośbę użytkownika (2026-09-23) wszystkie wykresy karty poza histogramem rozkładu bramek zebrano w zakładce Forma i regularność, która ma spis treści sekcji; trzy wykresy „Forma mecz po meczu” przeniesiono z Podsumowania, a skrót analizy defensywy rywali z usuniętej zakładki Statystyki. Pozostałe zakładki (Bramki i karne, Porównania, Dyscyplina, Rekordy i kamienie milowe, Jakość danych) są nadal planem i nie są pokazywane jako nieczynne elementy interfejsu.

## Najważniejsza zasada

Efektowna wizualizacja nie może udawać wiedzy, której nie ma w danych. Obecna baza pozwala profesjonalnie analizować:

- bramki w poszczególnych meczach;
- rzuty karne: trafienia i próby;
- kary dwuminutowe jako liczbę zapisanych kar, nie liczbę minut;
- upomnienia i dyskwalifikacje;
- sezony, rozgrywki, drużyny, pozycję i numer zawodnika;
- przeciwnika, stronę gospodarz/gość, termin, wynik i kontekst meczu;
- regularność, rozkład wyników, trendy, rekordy i pozycję na tle porównywalnej grupy;
- kompletność oraz pochodzenie części danych.

Obecna baza nie pozwala wiarygodnie obliczyć minut gry, asyst, strat, przechwytów, bloków, obron bramkarza, wszystkich rzutów z gry, stref rzutów, posiadań, tempa, plus/minus, xG ani wpływu przyczynowego zawodnika na wynik.

## Stan danych potwierdzony na 2026-09-22

Kontrola została wykonana zbiorczo w transakcji `READ ONLY`, zakończonej `ROLLBACK`. Nie odczytywano ani nie zapisano danych kontaktowych.

| Miara | Wartość |
| --- | ---: |
| Wpisy zawodnik–mecz w `mecze_zawodnicy` | 1 116 242 |
| Różni zawodnicy | 18 412 |
| Różne mecze | 31 330 |
| Wpisy z bramkami | 1 116 221 |
| Wpisy z karami dwuminutowymi | 1 116 221 |
| Wpisy z upomnieniem, dyskwalifikacją, `wyjscie` i `kd` | po 1 116 221 |
| Wpisy z trafieniami i próbami karnych | 643 151 |
| Wpisy z karnymi w serii | 643 151 |

Wysoka kompletność techniczna nie dowodzi jeszcze jednakowej semantyki we wszystkich sezonach. Wartość `0` może oznaczać rzeczywiste zero albo wartość uzupełnioną przez źródło. Przed publikacją rankingów należy wykonać audyt rozkładów według sezonu, rozgrywek i źródła.

## Globalny kontekst nowych analiz

W obrębie nowych zakładek analitycznych powinien znajdować się jeden pasek kontekstu. Nie zmienia on działania zakładek `Profil`, `Sezony i drużyny` ani `Mecze`. Każda nowa statystyka, wykres i tabela musi respektować ten sam wybór:

| Filtr | Zachowanie |
| --- | --- |
| Sezon | Jeden, wiele albo cała kariera |
| Rozgrywki | Dokładna nazwa rozgrywek; opcjonalnie wszystkie |
| Drużyna | Historyczna drużyna zawodnika w danym sezonie |
| Przeciwnik | Stała tożsamość zespołu rozpoznana po historycznych nazwach |
| Miejsce | Wszystkie, dom, wyjazd |
| Zakres dat | Od–do |
| Rodzaj meczu | Wszystkie albo tylko mecze z pełnym wynikiem |

Pasek pokazuje aktywny zakres, liczbę meczów, liczbę wpisów zawodnika i wskaźnik kompletności. Zmiana filtra ma aktualizować wszystkie nowe zakładki analityczne bez zmiany definicji miar.

## Docelowa kolejność zakładek

| Kolejność | Zakładka | Status i główne pytanie |
| ---: | --- | --- |
| 1 | Profil | Istniejąca, bez zmian |
| 2 | Sezony i drużyny | Istniejąca, bez zmian |
| 3 | Mecze | Istniejąca, bez zmian |
| 4 | Podsumowanie | Nowa: co najważniejszego wynika z wybranego zakresu? |
| 5 | Forma i regularność | Nowa: jak zmienia się produkcja oraz jak stabilne są wyniki? |
| 6 | Bramki i karne | Nowa: skąd bierze się produkcja bramkowa i jaka jest skuteczność karnych? |
| 7 | Porównania | Nowa: jak zawodnik wypada na tle właściwej grupy odniesienia? |
| 8 | Dyscyplina | Nowa: jaki jest profil kar i jego zmienność? |
| 9 | Rekordy i kamienie milowe | Nowa: jakie są rekordowe serie, mecze i progi kariery? |
| 10 | Jakość danych | Nowa: na ile można ufać każdej mierze i z jakich źródeł pochodzi? |

## 1. Podsumowanie

Najważniejsza zakładka. Ma umożliwić ocenę zawodnika w kilkanaście sekund, bez przewijania ściany wskaźników.

### Karty KPI

| KPI | Definicja | Uwagi |
| --- | --- | --- |
| Mecze w danych | liczba różnych `id_mecz` z wpisem zawodnika | Nazywać „mecze z wpisem”, nie występy ani rozegrane mecze |
| Bramki | suma znanych `bramki` | Obok pokazać pokrycie danych |
| Średnia bramek | suma bramek / liczba meczów ze znaną liczbą bramek | Nie dzielić przez wpisy z brakiem |
| Mediana bramek | mediana bramek na mecz | Odporniejsza od średniej na mecze rekordowe |
| Dominanta bramek | najczęstsza liczba bramek | Przy remisie pokazać wszystkie dominanty albo „brak jednej dominanty” |
| Q1–Q3 | kwartyle bramek na mecz | Pokazują typowy zakres środkowych 50% meczów |
| Mecze z bramką | odsetek meczów z `bramki > 0` | Czytelniejszy niż sama średnia |
| Rekord bramek | maksimum oraz link do meczu | Przy remisie wszystkie rekordowe mecze |
| Karne | trafione / próby oraz skuteczność ważona | Tylko gdy mianownik jest dodatni |
| Kary | 2 min, upomnienia, dyskwalifikacje | „2 min” to liczba kar, nie suma minut |

### Wykres główny

Szereg czasowy bramek na mecz:

- punkty dla pojedynczych meczów;
- linia mediany kroczącej z 5 ostatnich meczów;
- linia średniej kroczącej z 5 meczów jako mniej odporne uzupełnienie;
- pas Q1–Q3 z wybranego okresu;
- pionowe separatory sezonów;
- kolor punktu według drużyny lub rozgrywek;
- podpowiedź: data, przeciwnik, wynik, bramki, karne i kary;
- kliknięcie punktu otwiera szczegóły meczu.

To powinien być pierwszy „efekt wow”, ale nadal czytelny i analitycznie poprawny.

### Miniwnioski automatyczne

Maksymalnie trzy zdania oparte na jawnych regułach, np.:

- „Mediana z ostatnich 5 meczów jest wyższa od mediany sezonu”.
- „Zmienność bramek jest wysoka: środkowe 50% wyników mieści się między Q1 a Q3”.
- „Skuteczność karnych opiera się na małej próbie: 7 rzutów”.

Bez języka przyczynowego: nie pisać, że zawodnik „zapewnił zwycięstwo” albo „jest w formie” wyłącznie na podstawie korelacji.

## 2. Forma i regularność

### Statystyki opisowe

| Miara | Zastosowanie |
| --- | --- |
| Średnia arytmetyczna | Ogólny poziom produkcji, wrażliwy na rekordowe mecze |
| Mediana | Typowy mecz zawodnika |
| Dominanta | Najczęstszy wynik bramkowy |
| Minimum i maksimum | Pełny zakres |
| Q1, Q3 i IQR | Typowy zakres oraz odporna zmienność |
| Odchylenie standardowe | Zmienność wokół średniej |
| MAD | Mediana bezwzględnych odchyleń, odporna regularność |
| Współczynnik zmienności | Tylko przy sensownie dodatniej średniej; nie dla średniej bliskiej zeru |
| P10, P50, P90 | Czytelny profil słabszego, typowego i bardzo dobrego meczu |
| Średnia ucięta 10% | Stabilna wartość pomocnicza przy długiej historii |
| Udział 0, 1–2, 3–5, 6+ bramek | Profil rozkładu bez nadmiaru cyfr |

### Wykresy

1. **Linia formy 5/10 meczów** – mediana i średnia krocząca.
2. **Boxplot sezonów** – mediana, kwartyle, wartości odstające i liczba meczów.
3. **Beeswarm meczów** – każdy mecz jako punkt na osi bramek; pokazuje skupienia ukryte przez boxplot.
4. **Histogram dyskretny** – częstość 0, 1, 2… bramek z wyróżnioną dominantą i medianą.
5. **Karta regularności** – MAD i IQR, nie arbitralny „rating stabilności”.
6. **Karta kontrolna** – mediana krocząca oraz granice oparte na MAD; tylko jako detektor nietypowych meczów, nie proces przemysłowy.

### Zasady interpretacji

- Okno kroczące ma być liczone po kolejności meczów, nie dniach.
- Dla mniej niż 5 meczów nie pokazywać trendu pięciomeczowego.
- Dla sezonów z małą próbą wykres powinien pokazywać `n` i ostrzeżenie.
- Braki danych nie mogą automatycznie stawać się zerami.

## 3. Bramki i karne

### Produkcja bramkowa

- suma, średnia, mediana i dominanta bramek;
- bramki według sezonu, rozgrywek, drużyny, przeciwnika oraz dom/wyjazd;
- udział zawodnika w bramkach jego drużyny w meczu: `bramki_zawodnika / bramki_druzyny`;
- mediana udziału w bramkach drużyny;
- liczba i udział meczów z co najmniej 1, 3, 5, 8 i 10 bramkami;
- rekordy oraz serie kolejnych meczów z bramką;
- produkcja w zwycięstwach, remisach i porażkach wyłącznie opisowo.

Udział w bramkach drużyny nie jest udziałem w ataku, ponieważ baza nie ma asyst, zasłon, wywalczonych karnych ani posiadań.

### Karne

| Miara | Wzór |
| --- | --- |
| Skuteczność ważona | `SUM(karne_bramki) / SUM(karne_liczba)` |
| Średnia prób na mecz | `SUM(karne_liczba) / mecze ze znanym polem` |
| Mediana prób | mediana `karne_liczba` na mecz |
| Udział bramek z karnych | `SUM(karne_bramki) / SUM(bramki)` |
| Mecze bez pudła | mecze z próbą i `trafione = próby` |
| Mecze z karnym | udział meczów z `karne_liczba > 0` |

Nie wolno uśredniać procentów meczowych bez pokazania wyniku ważonego. Mecz 1/1 nie może mieć takiej samej wagi jak 8/10.

### Wykresy

1. **Waffle 100 pól** dla skuteczności karnych, dopiero przy odpowiedniej próbie.
2. **Funnel liczebności**: mecze → mecze ze znanymi karnymi → mecze z próbą → próby → trafienia.
3. **Forest plot skuteczności sezonów** z przedziałem ufności Wilsona i liczbą prób.
4. **Scatter próby–skuteczność** dla sezonów lub rozgrywek; rozmiar punktu = liczba meczów.
5. **Trend kroczący** trafień i prób z oknem co najmniej 20 prób, nie arbitralnie 5 meczów.
6. **Skumulowany bilans karnych**: trafienia i próby narastająco w karierze.

### Czego nie nazywać skutecznością rzutową

`bramki / mecze` to średnia bramek, nie skuteczność. Baza nie zawiera liczby wszystkich rzutów z gry, więc nie wolno pokazywać ogólnej skuteczności rzutowej zawodnika.

## Istniejące zakładki jako punkt odniesienia

Zakładki `Sezony i drużyny` oraz `Mecze` pozostają bez zmian. Nowe analizy korzystają z tego samego zakresu danych, ale prezentują wyniki wyłącznie we własnych zakładkach.

Wizualizacje kariery, takie jak small multiples sezonów, slopegraph, ridgeline, streamgraph i oś kariery, należy umieścić w nowych zakładkach `Forma i regularność`, `Porównania` albo `Rekordy i kamienie milowe`, zależnie od pytania analitycznego. Nie rozszerzają one istniejącej tabeli `Sezony i drużyny`.

Obecna tabela `Mecze` pozostaje podstawą audytowalności. Każdy agregat powinien prowadzić linkiem do właściwego meczu lub otwierać istniejącą zakładkę `Mecze` z obsługiwanym już kontekstem. Nowy plan nie dodaje do tej tabeli kolumn, filtrów, oznaczeń ani eksportu.

## Profesjonalna definicja wyniku

Zwycięstwo/remis/porażkę wyznaczać z pełnego wyniku po zastosowaniu istniejącej reguły `zamiana`. Serię karnych i dogrywkę prezentować osobno. Walkower, wycofanie i brak pełnego wyniku oznaczać jawnie i domyślnie wyłączać z analiz zależnych od wyniku.

## 4. Porównania

Najbardziej wartościowa analitycznie zakładka po ustabilizowaniu podstawowych miar.

### Poprawna grupa odniesienia

Domyślnie porównywać zawodnika tylko z osobami:

- w tym samym sezonie;
- w tych samych rozgrywkach;
- na tej samej znormalizowanej pozycji;
- z minimalną liczbą meczów z wpisem, np. 10;
- z wystarczającym pokryciem analizowanej cechy.

Użytkownik może rozszerzyć grupę do wszystkich pozycji, ale interfejs musi wyświetlić ostrzeżenie. Bramkarza nie należy porównywać bramkami z zawodnikami pola bez jawnego wyboru.

### Miary porównawcze

- percentyl bramek na mecz;
- percentyl mediany bramek;
- percentyl regularności według IQR lub MAD;
- percentyl udziału meczów z bramką;
- percentyl prób karnych na mecz;
- percentyl skuteczności karnych przy minimalnej liczbie prób;
- percentyl kar dwuminutowych na mecz;
- pozycja w klasyfikacji `strzelcy`, jeżeli rekord jednoznacznie odpowiada zakresowi;
- różnica względem mediany grupy wraz z `n` zawodnika i grupy.

### Wykresy

1. **Percentile bars** – poziome paski percentyli; czytelniejsze niż radar.
2. **Radar percentylowy** – maksymalnie 5–6 cech, wszystkie na tej samej skali percentylowej. To „fajerwerk”, nie główna tabela.
3. **Beeswarm ligowy** – pozycja zawodnika w rozkładzie grupy.
4. **Scatter produkcja–regularność** – średnia bramek kontra IQR/MAD, rozmiar = liczba meczów.
5. **Quadrant chart** – wysoka/niska produkcja i wysoka/niska regularność względem median grupy, bez etykiet wartościujących typu „zły”.

### Niepewność

Percentyl nie może być pokazywany bez liczebności grupy. Dla karnych stosować minimalny próg prób i przedział ufności. Ranking przy małej próbie oznaczać jako niestabilny.

## 5. Dyscyplina

### Statystyki

- suma i średnia kar dwuminutowych na mecz z wpisem;
- mediana i dominanta kar dwuminutowych;
- mecze bez kary oraz z 1, 2, 3+ karami;
- upomnienia i dyskwalifikacje: liczba i udział meczów;
- kary według sezonu, rozgrywek, przeciwnika oraz dom/wyjazd;
- współwystępowanie wysokiej liczby bramek i kar wyłącznie opisowo;
- seria meczów bez kary;
- percentyl dyscypliny na tle tej samej pozycji.

### Wykresy

1. **Kalendarzowa heatmapa meczów** – kolor według kar, symbol dyskwalifikacji.
2. **Stacked bars sezonów** – 2 min, upomnienia i dyskwalifikacje jako osobne miary, nie jedna suma „kar”.
3. **Macierz przeciwnik × sezon** – średnia lub suma kar z liczbą meczów w komórce.
4. **Scatter bramki–kary** – eksploracyjny, bez wniosku o przyczynowości.

`dwie_minuty = 2` oznacza najprawdopodobniej dwie kary dwuminutowe, a nie dwie minuty. Etykieta musi brzmieć „liczba kar 2 min”.

## 6. Rekordy i kamienie milowe

### Rekordy

- najwięcej bramek w meczu;
- najwyższa mediana i średnia w sezonie przy minimalnym `n`;
- najwięcej trafionych karnych i prób w meczu;
- najwyższa skuteczność karnych w sezonie przy progu prób;
- najdłuższa seria meczów z bramką;
- najdłuższa seria meczów z 3+, 5+ bramkami;
- najdłuższa seria bez kary;
- najwięcej meczów i bramek przeciw jednemu przeciwnikowi;
- rekordowa produkcja dom/wyjazd;
- kamienie milowe: 50, 100, 250, 500 meczów z wpisem oraz 100, 250, 500, 1000 bramek.

### Wizualizacje „fajerwerkowe”

1. **Oś kamieni milowych** z linkami do meczów.
2. **Kalendarz kariery** – każdy mecz jako komórka, intensywność = bramki.
3. **Constellation chart** – sezony jako węzły, drużyny i rozgrywki jako połączenia; tylko przy złożonej karierze.
4. **Animated race sezonów** – wyłącznie jako opcjonalna prezentacja, nie narzędzie analityczne.
5. **Personal best cards** z kontekstem próby i datą, bez konfetti zasłaniającego dane.

## 7. Jakość danych

Ta zakładka jest obowiązkowa w narzędziu administracyjnym i odróżnia profesjonalną analitykę od dekoracyjnego dashboardu.

### Elementy

- pokrycie każdego pola: znane / wszystkie wpisy;
- pokrycie według sezonu i rozgrywek;
- liczba meczów z wieloma wpisami stron dla zawodnika;
- rozbieżność `sklady.pozycja_nazwa` i `mecze_zawodnicy.pozycja`;
- zmiany wzrostu, wagi, numeru i pozycji oraz podejrzane skoki;
- wpisy z karnymi większymi od wszystkich bramek;
- trafione karne większe od prób;
- ujemne wartości i niemożliwe zakresy;
- mecze z wpisem zawodnika, ale bez pełnego wyniku;
- źródło i wersja składu, jeżeli relacja jest jednoznaczna;
- data ostatniego importu właściwego źródła;
- etykieta wiarygodności każdej sekcji: wysoka, średnia, niska wraz z przyczyną.

### Macierz kompletności

Najlepszy wykres tej zakładki to heatmapa sezon × pole. Kolor oznacza procent znanych wartości, a liczba w komórce pokazuje licznik/mianownik. Nie używać jednej ogólnej „jakości 87%”, która ukrywa problem konkretnego pola.

## Definicje statystyczne

### Jednostka analizy

Podstawową jednostką jest różny mecz `id_mecz` z co najmniej jednym wpisem zawodnika. Jeśli zawodnik ma kilka wpisów w tym samym meczu, należy:

1. zachować wpisy osobno w audycie;
2. nie sumować ich automatycznie;
3. wybrać jawnie rekord źródłowy albo oznaczyć mecz jako niejednoznaczny;
4. wyłączyć niejednoznaczny mecz z agregatu wymagającego jednej wartości, dopóki reguła nie zostanie zatwierdzona.

### Braki danych

- `NULL` nie jest zerem;
- średnia, mediana, kwartyle i dominanta korzystają tylko ze znanych wartości;
- każda miara pokazuje `n` oraz pokrycie;
- zero w źródle pozostaje zerem, ale audyt jakości sprawdza podejrzanie jednolite okresy;
- brak mianownika uniemożliwia obliczenie procentu;
- wartość 0/0 dla karnych nie jest skutecznością 0%, tylko brakiem próby.

### Mediana

Dla parzystej liczby obserwacji mediana jest średnią dwóch środkowych wartości. W PostgreSQL można użyć `percentile_cont(0.5) WITHIN GROUP (ORDER BY wartosc)`.

### Dominanta

Dominanta to wszystkie wartości o najwyższej częstości. Przy kilku wartościach ex aequo interfejs pokazuje „wielomodalny: 2, 3”, a nie arbitralnie pierwszą wartość.

### Kwartyle i wartości odstające

- Q1 = 25. percentyl;
- Q3 = 75. percentyl;
- IQR = Q3 − Q1;
- obserwacja poniżej `Q1 − 1,5 × IQR` lub powyżej `Q3 + 1,5 × IQR` jest punktem odstającym na boxplocie, nie automatycznie błędem danych.

### Regularność

Nie tworzyć jednego nieprzejrzystego „AI consistency score”. Pokazać IQR, MAD i odchylenie standardowe. Jeżeli produkt potrzebuje jednej etykiety, musi wynikać z jawnej, udokumentowanej reguły percentylowej w grupie porównawczej.

### Przedziały ufności

Dla skuteczności karnych stosować przedział Wilsona. Nie pokazywać samego procentu 100% bez liczby prób i przedziału. Dla średniej bramek można użyć bootstrapowego przedziału ufności, ale mediana i surowy rozkład powinny pozostać widoczne.

## Analizy specyficzne dla piłki ręcznej

### Zawodnik pola

Najbardziej użyteczne są produkcja bramkowa, regularność, udział w bramkach drużyny, karne, profil dom/wyjazd, przeciwnicy, trendy sezonowe i dyscyplina.

### Bramkarz

Obecna baza nie ma obron ani rzutów przeciwnika, dlatego nie wolno tworzyć procentu obron. Karta bramkarza może pokazywać historię drużyn, mecze z wpisem, kary i incydentalne bramki. Docelowa profesjonalna analityka bramkarza wymaga co najmniej liczby rzutów w światło bramki i obron, najlepiej z lokalizacją oraz sytuacją gry.

### Różne pozycje w historii

Porównania pozycyjne powinny korzystać z pozycji zapisanej w danym meczu, a nie jednej „aktualnej” pozycji. Nazwy pozycji wymagają normalizacji wariantów pisowni. Zmiana pozycji jest informacją na osi kariery, nie błędem.

## Wykresy od najbardziej potrzebnych do najmniej potrzebnych

| Priorytet | Wykres | Wartość | Warunek |
| ---: | --- | --- | --- |
| 1 | Szereg bramek + mediana krocząca | Forma i kontekst pojedynczych meczów | co najmniej 5 meczów |
| 2 | Boxplot sezonów | Poziom i zmienność | `n` na każdy sezon |
| 3 | Histogram bramek z dominantą | Rzeczywisty rozkład | co najmniej 10 meczów |
| 4 | Percentile bars | Porównanie z właściwą grupą | poprawna pozycja i próg meczów |
| 5 | Forest plot karnych | Skuteczność i niepewność | dodatnia liczba prób |
| 6 | Beeswarm meczów | Szczegół rozkładu | do kilkuset punktów lub agregacja |
| 7 | Heatmapa sezon × pole | Jakość danych | zawsze |
| 8 | Kalendarz bramki/kary | Wzorce czasowe | rzeczywiste daty |
| 9 | Scatter średnia–regularność | Profil na tle grupy | wystarczająca grupa |
| 10 | Radar percentylowy | Szybki profil wielowymiarowy | 5–6 porównywalnych cech |
| 11 | Ridgeline sezonów | Ewolucja rozkładów | wiele sezonów i duże `n` |
| 12 | Sankey/streamgraph kariery | Historia drużyn i rozgrywek | złożona kariera |
| 13 | Animowany race | Prezentacja | opcjonalny dodatek, nigdy rdzeń |

## Proponowany układ interfejsu

```text
ZAWODNIK — IMIĘ I NAZWISKO

[Profil] [Sezony i drużyny] [Mecze]
[Podsumowanie] [Forma] [Bramki i karne] [Porównania]
[Dyscyplina] [Rekordy] [Jakość danych]

Podsumowanie:
[Sezon] [Rozgrywki] [Drużyna] [Przeciwnik] [Dom/wyjazd] [Data od–do]
[zakres danych] [pokrycie]
[Mecze z wpisem] [Bramki] [Średnia] [Mediana] [Dominanta]
[Q1–Q3] [Karne trafione/próby] [Skuteczność] [Kary 2 min]

[szereg czasowy bramek + mediana krocząca + pas Q1–Q3]
[3 automatyczne, ostrożne wnioski]
[rekordowy mecz] [ostatnie 5] [porównanie z medianą sezonu]
```

Na telefonie KPI układają się w dwie kolumny, potem jedną. Wykresy zachowują stałą wysokość i mają przewijalną lub redukowaną oś, a tabele przewijają się we własnym kontenerze. Tooltip nie może być jedynym nośnikiem danych; wykres musi mieć dostępny opis tekstowy.

## Architektura obliczeń

### Warstwy

- `SzczegolyZawodnikaAnalyticsRepository` – wyłącznie odczyt i agregacje SQLAlchemy;
- `SzczegolyZawodnikaAnalyticsService` – definicje zakresów, mianowników i reguł kompletności;
- `SzczegolyZawodnikaAnalyticsPresenter` – formatowanie, etykiety, kolory i modele wykresów;
- typowane obiekty domenowe dla podsumowania, rozkładu, trendu, porównania i jakości;
- osobne formularze filtrów analitycznych bez zależności logiki od `request`;
- jedna definicja każdej miary używana przez KPI, wykres i eksport.

### Strategia zapytań

1. Najpierw wybrać różne mecze spełniające kontekst.
2. Osobno pobrać wpisy zawodnika, wynik i drużyny.
3. Nie łączyć bezpośrednio historii `sklady` z `mecze_zawodnicy` przed agregacją.
4. Agregować do poziomu mecz–zawodnik przed statystykami sezonowymi.
5. Porównania ligowe liczyć w osobnym zapytaniu na tym samym kontrakcie kompletności.
6. Dla kosztownych percentyli rozważyć cache aplikacyjny dopiero po pomiarze planu zapytania.

## Etapy wdrożenia

### Etap A — fundament, najwyższy priorytet

- testy regresji potwierdzające niezmienione działanie zakładek Profil, Sezony i drużyny oraz Mecze;
- nowa zakładka Podsumowanie i wspólny pasek filtrów nowych analiz;
- Podsumowanie z `n`, pokryciem, sumą, średnią, medianą, dominantą i kwartylami;
- szereg bramek z medianą kroczącą;
- rozkład bramek;
- odsyłacze z agregatów do istniejących szczegółów meczu lub zakładki Mecze;
- audyt braków i wielokrotnych wpisów;
- testy definicji mianowników i `NULL`.

### Etap B — analityka sportowa

- Forma i regularność;
- Bramki i karne wraz z Wilsonem;
- udział w bramkach drużyny;
- dyscyplina;
- rekordy i serie;
- linkowanie każdego ekstremum do meczu.

### Etap C — benchmarking

- normalizacja pozycji;
- grupy odniesienia;
- percentyle i beeswarm;
- radar percentylowy;
- progi minimalnej próby i ostrzeżenia stabilności.

### Etap D — „fajerwerki” i jakość

- ridgeline, kalendarze i oś kariery;
- heatmapa kompletności;
- automatyczne wnioski regułowe;
- opcjonalne animacje;
- pomiar wydajności i cache tylko tam, gdzie jest potrzebny.

## Kryteria ukończenia

- Istniejące zakładki `Profil`, `Sezony i drużyny` i `Mecze` zachowują zawartość oraz dotychczasowe zachowanie.
- Nowe filtry nie zmieniają stanu ani kontraktu istniejących zakładek.
- Każda miara ma nazwę, wzór, jednostkę, mianownik i regułę braków.
- Każdy procent pokazuje licznik i mianownik.
- Każdy ranking pokazuje grupę odniesienia, `n` i próg kwalifikacji.
- Średnia nigdy nie zastępuje mediany; obie są widoczne tam, gdzie rozkład może być skośny.
- Dominanta obsługuje remisy częstości.
- `NULL` nigdy nie jest automatycznie zerem.
- Agregacja nie mnoży wartości przez relacje składów ani rozgrywek.
- Wynik meczu uwzględnia `zamiana`, walkower, wycofanie, dogrywkę i karne.
- Bramkarz nie otrzymuje fikcyjnego procentu obron.
- Ogólna skuteczność rzutowa nie jest pokazywana bez liczby rzutów.
- Wartości odstające są oznaczane, nie usuwane bez reguły jakości.
- Każdy wykres ma tabelaryczny lub tekstowy odpowiednik dostępnościowy.
- Karta działa dla braku historii, jednego meczu, małej próby i wielu sezonów.
- Testy używają izolowanych danych; rzeczywista baza jest sprawdzana wyłącznie w `READ ONLY` z `ROLLBACK`.

## Dane potrzebne do analiz obecnie niemożliwych

| Przyszła analiza | Minimalne nowe dane |
| --- | --- |
| Ogólna skuteczność rzutowa | rzuty i bramki z gry według zawodnika |
| Mapa rzutów | współrzędne lub strefa, wynik rzutu, sytuacja gry |
| xG | lokalizacja, typ akcji, obrona, faza, wynik rzutu |
| Asysty i kreacja | asysta, kluczowe podanie, wywalczony karny |
| Straty i przechwyty | zdarzenia z zawodnikiem i czasem |
| Plus/minus | zmiany, czas przebywania na boisku i wynik w czasie |
| Obciążenie | minuty i sekwencje zmian |
| Bramkarz | rzuty w światło, obrony, strefa, typ rzutu |
| Tempo i per-possession | posiadania albo pełny strumień zdarzeń |
| Analiza clutch | czas zdarzenia, stan wyniku i waga sytuacji |

Do czasu pozyskania tych danych interfejs może pokazywać miejsce na przyszły kontrakt wyłącznie w dokumentacji, nie jako pustą lub oszacowaną zakładkę produktu.

## Rekomendacja końcowa

Zachować obecną kartę i najpierw dołożyć po niej zakładki Podsumowanie, Forma, Bramki i karne oraz Jakość danych. To daje największą wartość sportową przy najmniejszym ryzyku błędnej interpretacji i regresji istniejących funkcji. Porównania pozycyjne powinny wejść dopiero po normalizacji pozycji i ustaleniu progów próby. Ridgeline, radar, kalendarz i animacje są wartościowym dodatkiem, ale muszą bazować na tych samych jawnych definicjach co proste KPI i tabele.
