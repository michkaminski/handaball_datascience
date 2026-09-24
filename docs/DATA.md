# Dane i ich interpretacja

## Materiały odniesienia

- [Rzeczywista baza — przegląd](database/README.md), [schemat public](database/PUBLIC_SCHEMA.md), [schemat logs](database/LOGS_SCHEMA.md) i [relacje oraz różnice](database/RELATIONSHIPS.md): inspekcja `localhost:5432/zprp` z 2026-09-12. Pierwszy punkt odniesienia dla nowej aplikacji.
- [Archiwalny schemat PostgreSQL](database/schema_postgres_archive.sql) (kopia wcześniejszego projektu bazy z katalogu nadrzędnego, stan 2026-09-10): encje i relacje zaprojektowane dla archiwum ZPRP.
- README starszego serwisu poza katalogiem tego projektu (`_ZPRP_API/README.md` w katalogu nadrzędnym): opis źródeł i zaobserwowanej normalizacji.
- Normalizacja starszego serwisu poza katalogiem tego projektu (`_ZPRP_API/handball/normalize.py` w katalogu nadrzędnym): przykład istniejącej interpretacji danych, wymagający weryfikacji przed ponownym użyciem.
- Testy starszego serwisu poza katalogiem tego projektu (`_ZPRP_API/tests/test_import.py` w katalogu nadrzędnym): przypadki regresyjne istniejącego importu.

Ścieżki dotyczą obecnego układu katalogów na dysku, poza katalogiem tego projektu. Nie kopiuj całego archiwum ani schematu do kontekstu AI. Czytaj pola i próbki potrzebne w zadaniu.

## Skrócona mapa danych

| Obszar | Tabele |
| --- | --- |
| Sezon i rozgrywki | `sezony`, `rozgrywki`, `rundy`, `kolejki` |
| Kluby i drużyny | `kluby`, `zespoly`, `zespoly_sezony`, `zespoly_rozgrywki` |
| Mecze i występy | `mecze`, `mecze_zawodnicy`, `zawodnicy`, `sklady` |
| Klasyfikacje | `tabele`, `tabele_grupy`, `tabele_wiersze`, `strzelcy` |
| Wersje składów | `sklady_wersje`, `sklady_wersje_zawodnicy` |
| Pochodzenie danych | `pliki_zrodlowe`, `rekordy_zrodla` |
| Import, anomalie i historia | Schemat `logs`: rejestry, widoki i tabele `*_log` |

Tabele domenowe są w `public`. Stan rzeczywisty obejmuje 30 tabel `public`, 35 tabel `logs` i 2 widoki `logs`. Pełne kolumny, klucze i indeksy znajdują się w dokumentacji bazy. Przy późniejszej zmianie schematu odśwież odpowiedni fragment dokumentacji tylko do odczytu.

## Zasady domenowe

- Rozróżniaj klub, drużynę i jej migawkę sezonową. Historyczna nazwa nie musi być nazwą aktualną.
- Łącz rekordy po identyfikatorach i odpowiednim kontekście sezonu/rozgrywek, nie po samej nazwie.
- Brak wartości nie oznacza zera. Nie licz pełnych sum i skuteczności bez określenia kompletności danych i mianownika.
- Nie sumuj zamiennie wyniku końcowego, wyników tymczasowych, dogrywek i serii karnych. Najpierw ustal semantykę wyświetlanego pola.
- Starszy README opisuje specjalną obsługę `zamiana`: część metadanych i wyników jest odwracana, a składy już mają docelową stronę. Przed zastosowaniem tej logiki sprawdź, czy import do bazy już ją wykonał. Podwójna zamiana zepsuje wynik.
- Nie wliczaj kar sztabu do kar zawodników. Nie utożsamiaj obecności w składzie z występem.
- Identyfikatory lig, kody płci, statusy i zasady punktacji potwierdzaj w danych lub odpowiedniej dokumentacji; nie zgaduj ich z nazw rozgrywek.
- Dane kontaktowe, licencyjne i pola badań dostępne w bazie nie są domyślnie polami widoku meczu ani publicznego eksportu.

## Braki do ustalenia podczas integracji

Schemat oraz obecność 20 sezonów od 2007/2008 do 2026/2027 potwierdzono. Do ustalenia pozostają sposób normalizacji podczas importu oraz mapowanie statusów i wariantów wyniku na prezentację. Ostatni zapisany przebieg importu ma status `CZESCIOWY`; liczby rekordów nie dowodzą kompletności archiwum.

Nie naprawiaj danych ani nie uruchamiaj ponownie importu na podstawie tych obserwacji. Zmiany w bazie są dozwolone dopiero na wyraźną prośbę użytkownika.


## Prezentacja zmiany gospodarza — 2026-09-19

Na polecenie użytkownika lista meczów uwzględnia `mecze.zamiana=True`: odwraca nazwy obu drużyn oraz części wyniku `wynik_gosp_full` / `wynik_gosc_full`. Dla `False` lub `NULL` pozostawia kolejność. Po refaktoryzacji 2026-09-19 reguła jest stosowana raz przez `MeczPresenter` z użyciem `MeczPolicy`, bez zmiany danych źródłowych. Składów nie odwraca: `strona` wpisów zawodników ma już docelową stronę (zob. [Strona wpisów zawodników przy `zamiana`](#strona-wpisów-zawodników-przy-zamiana--2026-09-23)).

## Kontrakt odczytu po refaktoryzacji — 2026-09-19

Repozytorium zwraca źródłową kolejność stron, liczby, daty i `None`; `ZawodnikMeczu` nie zawiera pól koloru ani tekstowych ułamków. Presenter stosuje regułę stron dla listy oraz szczegółów (nazwy, wyniki i składy) i przygotowuje modele szablonów. Zachowano istniejące zachowanie; refaktoryzacja nie jest nową weryfikacją semantyki importu ani zgody na zmianę bazy. Maksimum bramek jest wyznaczane osobno w każdym składzie przez regułę domenową; braki pozostają brakami w domenie.

## Podsumowanie sezonów zawodnika — 2026-09-20

Karta zawodnika łączy historię `sklady` z osobną agregacją `mecze_zawodnicy`. Agregacja grupuje wpisy według `mecze.id_sezon`, drużyny wynikającej ze strony `gosp` lub `gosc` oraz `rozgrywki.nazwa`. Dzięki oddzielnemu zapytaniu relacja składów nie mnoży sum. Strona `inne` nie ma jednoznacznej drużyny i nie trafia do podsumowania drużynowego.

Bramki, trafione i wykonywane karne oraz liczba kar dwuminutowych są sumami znanych wartości. Upomnienia i dyskwalifikacje są sumą wartości prawdziwych. Gdy wszystkie wartości danego pola w grupie są `NULL`, wynik pozostaje nieznany. Te statystyki oznaczają dostępne wpisy zawodnik–strona–mecz, a nie potwierdzone minuty lub wejście na boisko. Wzrost i waga w Profilu to najnowsza niepusta wartość każdego pola według kolejności historii składów; mogą pochodzić z różnych zapisów.

## Lista zawodników — 2026-09-20

Lista grupuje po `zawodnicy.id`. Pokazuje najnowszy niepusty wzrost i najnowszą niepustą wagę z `sklady`, wybierane niezależnie według roku rozpoczęcia sezonu, ID sezonu i ID migawki drużyny malejąco. Pomiary mogą pochodzić z różnych rekordów. Brak wartości pozostaje brakiem.

Sezon, nazwa rozgrywek, historyczna tożsamość drużyny i pozycja ograniczają wpisy przed agregacją. Nazwy drużyn pochodzą z unikalnej migawki zespołu i sezonu. Strona `inne` pozostaje bez przypisania drużyny. Wiele historycznych drużyn i pozycji pokazujemy razem; nie wyznaczamy „aktualnego klubu”. Bez filtrów kontekstu pozostają też zawodnicy bez wpisów meczowych.

Mapowanie opiera się na udokumentowanym schemacie i obecnym powiązaniu stron w szczegółach meczu/importerze. Nie jest nową weryfikacją semantyki historycznego importu. Rzeczywiste zapytania agregacji i wydajność wymagają sprawdzenia przy dostępnym połączeniu READ ONLY; w tej sesji brak hasła w środowisku. Pełny kontrakt: [lista zawodników](../src/handball/interface/templates/admin/players/list.md).

## Karta hali — 2026-09-21

Hala łączy się z meczem przez mecze.id_hala. Za rozegrany uznajemy mecz z oboma pełnymi wynikami, bez wycofania i walkoweru. Ten sam zakres zasila mecze, zawodników i rankingi karty; wszystkie zapisane mecze pozostają osobną liczbą podsumowania.

Występ zawodnika oznacza różny mecz z wpisem mecze_zawodnicy, nie minuty gry. Bramki są sumą znanych wartości, a średnia dzieli tę sumę przez liczbę różnych meczów. Ranking średniej wymaga 3 występów. Historyczne nazwy drużyn pochodzą z zespoly_sezony połączonych po zespole i sezonie.

Ranking drużyn grupuje po zespoly.id. Nie wyznaczamy właściciela hali. Rozgrywki grupujemy po nazwie, łącząc rekordy sezonowe. Zapytania sprawdzono w transakcji READ ONLY zakończonej ROLLBACK.
## Analizy hali

Analizy hali obejmują tylko rozegrane mecze z oboma polami `wynik_gosp_full` i `wynik_gosc_full`, bez `wycofany = true` i bez `id_zespol_walkower`. Suma i różnica bramek korzystają z pełnego wyniku. Rekordy oraz prezentacja drużyn stosują `zamiana`; agregaty symetryczne, takie jak suma i bezwzględna różnica, nie wymagają odwracania stron.

Frekwencja pochodzi z `mecze.widzowie`. Brak wartości nie jest zerem i nie wchodzi do średniej ani mediany. Widok zawsze pokazuje liczbę meczów z frekwencją względem wszystkich rozegranych meczów hali. Średnie wypełnienie to średnia frekwencja podzielona przez `hale.pojemnosc`; przy braku lub zerowej pojemności pozostaje nieznane.

Porównanie hali ze średnią innych hal ma charakter opisowy. Obejmuje hale z co najmniej jednym rozegranym meczem i nie służy do wskazywania najlepszej hali. Liczba meczów na sezon ma mianownik równy liczbie różnych sezonów danej hali.

## Karta drużyny — 2026-09-23

Drużyna to `zespoly.id`. Nazwy, miasta i statusy w sezonach pochodzą z `zespoly_sezony` (jedna migawka na zespół i sezon). Tabela `zespoly` nie ma kolumny `miasto`; model ORM mapuje teraz rzeczywistą kolumnę `nr_klubu`.

Bramki drużyny to pełny wynik jej kolumny (`id_zespol_gosp` ↔ `wynik_gosp_full`, `id_zespol_gosc` ↔ `wynik_gosc_full`). `zamiana` przestawia nazwy i wyniki razem, więc nie zmienia tego powiązania, a jedynie miejsce meczu. Kolumna gospodarza bez `zamiana` albo kolumna gościa z `zamiana=true` oznacza mecz u siebie. Kolumna `zwyciezca` (1 = kolumna gospodarza, 2 = kolumna gościa, 0 = remis) jest w rozegranych meczach zgodna z tą regułą, ale nie jest używana.

Na bazie (READ ONLY, 2026-09-23) `wynik_*_full` to zwykle wynik po czasie regulaminowym. Z 1141 meczów z serią karnych 1134 mają remis w pełnym wyniku, a dogrywka jest w osobnych polach. W 9 z 21 meczów z dogrywką pełny wynik równa się jednak wynikowi dogrywki. Dlatego Z/R/P liczymy z pełnego wyniku, a rozstrzygnięcie remisu (dogrywka, potem seria karnych) pokazujemy osobno. W sezonach 2007/2008–2016/2017 jest ok. 750 meczów z remisem bez karnych i dogrywki (`zwyciezca=0`).

Zawodnicy drużyny to wpisy `mecze_zawodnicy` ze stroną zgodną z kolumną drużyny w meczu. Opis zakładek i mapa zmian: [teams/detail.md](../src/handball/interface/templates/admin/teams/detail.md).

Frekwencja drużyny i listy meczów pochodzi z `mecze.widzowie`. Na bazie (READ ONLY, 2026-09-23) 25 880 z 32 216 rozegranych meczów ma liczbę widzów; sezony do 2010/2011 nie mają jej wcale. 1527 meczów ma 0, z czego 1450 w sezonie 2020/2021 (mecze bez publiczności). Zero traktujemy jako znaną wartość, a brak jako brak danych. Frekwencję drużyny liczymy tylko z rozegranych meczów, osobno u siebie (miejsce po `zamiana`) i na wyjeździe.

## Strona wpisów zawodników przy `zamiana` — 2026-09-23

`mecze_zawodnicy.strona` wskazuje stronę **po** zamianie gospodarza. Przy `zamiana=true` wpis `gosp` należy do drużyny z kolumny `mecze.id_zespol_gosc` (wyświetlanego gospodarza), a `gosc` do drużyny z `id_zespol_gosp`. Przy `false`/`NULL` strona odpowiada kolumnie wprost. Potwierdza to stary README (składy mają już docelową stronę) i dane (READ ONLY): w każdym sezonie od 2007/2008 zawodnicy z `strona='gosp'` w meczach z zamianą są w `sklady` drużyny z kolumny gościa (np. 2025/2026: 2370 z 2402 wpisów, 0 w składzie drużyny z kolumny gospodarza). Przykład: mecz #189180 (wyświetlany Galiczanka Lwów – KGHM MKS Zagłębie Lubin), wpis `gosp` = zawodniczka Galiczanki.

Skutki:

- Szczegóły meczu nie zamieniają składów; zamieniane są tylko nazwy i wyniki (`MeczPolicy.para`).
- Każde powiązanie wpisu zawodnika z drużyną lub rywalem korzysta z `StronyMeczuSql` (`infrastructure/database/match_sides.py`): `zespol()`, `rywal()`, `wedlug_kolumny()`, `kolumna_gospodarza()`. Dotyczy to karty zawodnika (drużyny sezonów, filtr przeciwnika), listy zawodników (drużyny), defensywy rywali (drużyna, przeciwnik i wynik zawodnika), karty hali (drużyny zawodników), aktualności (drużyny strzelców) i zakładki Zawodnicy karty drużyny.
- Miejsce „u siebie / na wyjeździe” z `strona` (`gosp` → u siebie) było i pozostaje poprawne, bo `strona` opisuje stronę wyświetlaną.
- Przed poprawką przy 1830 meczach z zamianą zawodnicy byli przypisywani drużynie rywala. Przykład: lista zawodników Wisły Płock (#272) liczyła 329 osób, z czego 152 to zawodnicy rywali z jej 21 meczów z zamianą (tylko jeden z nich był kiedykolwiek w składzie Wisły). Po poprawce lista ma 178 osób, w tym 148 ze składu sezonowego Wisły.
