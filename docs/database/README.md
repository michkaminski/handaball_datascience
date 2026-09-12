# Baza danych zprp — stan rzeczywisty

## Połączenie i zasada użytkownika

| Parametr | Wartość |
| --- | --- |
| Host | `localhost` |
| Port | `5432` — zweryfikowany |
| Baza | `zprp` |
| Użytkownik | `postgres` |
| Hasło | Przekazane przez użytkownika; nie zapisujemy go w MD. Przekazuj je do procesu przez konfigurację środowiska, bez wypisywania. |
| Serwer | PostgreSQL 15.1, Windows 64-bit |
| Schematy aplikacyjne | `public`, `logs` |
| search_path sesji | `"$user", public` |
| Uprawnienia użytej roli | `postgres` ma atrybut superuser; nie jest kontem ograniczonym do odczytu. |

**Nie wykonuj żadnych zmian w bazie samodzielnie. Dopiero wyraźna prośba użytkownika o konkretną zmianę upoważnia do jej wykonania.** Dotyczy to danych, schematu, indeksów, sekwencji, uprawnień, konfiguracji, importów i migracji. Polecenie zbadania schematu ani tworzenia aplikacji nie jest zgodą na zapis.

Do analiz ustawiaj tryb tylko do odczytu dla połączenia (`default_transaction_read_only=on`) i otwieraj `BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY`. Kończ `ROLLBACK`. Nie zmieniaj w tym celu ustawień globalnych ani roli. Hasło było użyte tylko w środowisku procesu inspekcji.

Nie wywołuj funkcji aplikacyjnych podczas odczytu schematu. Część funkcji w logs wykonuje zapis lub DDL także po wywołaniu przez SELECT. Ich działanie opisano w [LOGS_SCHEMA](LOGS_SCHEMA.md).

## Jak czytać dokumentację

- [PUBLIC_SCHEMA](PUBLIC_SCHEMA.md): wszystkie 30 tabel public, kolumny i typy, NULL, wartości domyślne, klucze, indeksy, triggery oraz sekwencje. Czytaj sekcję konkretnej tabeli zamiast całego pliku.
- [LOGS_SCHEMA](LOGS_SCHEMA.md): wszystkie 35 tabel logs i 2 widoki, historia zmian, funkcje własne i sekwencje.
- [RELATIONSHIPS](RELATIONSHIPS.md): diagram, pełny wykaz FK, praktyczne zasady łączenia i różnice względem starego SQL.
- [DATA](../DATA.md): zasady interpretacji danych meczowych.

## Metoda i granice badania

Metadane i dokładne liczby wierszy: **2026-09-12T19:13:51.748319+02:00**. Profil sezonów, rozgrywek, flag i istniejących anomalii: **2026-09-12T19:14:48.05666+02:00**, w osobnej transakcji tylko do odczytu.

Odczytano katalogi pg_namespace, pg_class, pg_attribute, pg_attrdef, pg_constraint, pg_index, pg_trigger, pg_proc, pg_extension, pg_sequences oraz pg_type/pg_enum. Definicje pobrano przez funkcje systemowe pg_get_*. Policzono wiersze tabel i wykonano ograniczone agregacje domenowe. Nie pobierano treści plików, danych kontaktowych ani pełnych rekordów zawodników.

W obu transakcjach potwierdzono lub wymuszono READ ONLY; zakończono je ROLLBACK. Nie wykonano DML, DDL, importu, napraw, migracji, ANALYZE, VACUUM, nextval, setval ani funkcji aplikacyjnych. Liczby opisują migawki odczytu i mogą się zmieniać niezależnie od tej dokumentacji. Nie przeprowadzano pełnego audytu kompletności danych ani testów wydajności.

## Inwentarz

| Element | Liczba |
| --- | --- |
| Tabele public | 30 |
| Tabele logs | 35 |
| Widoki logs | 2 |
| Kolumny tabel public | 316 |
| Kolumny tabel i widoków logs | 723 |
| Klucze obce public / logs | 56 / 12 |
| Wszystkie ograniczenia | 213 |
| Indeksy | 224 |
| Triggery użytkownika | 89 |
| Sekwencje | 48 |
| Funkcje własne poza rozszerzeniami | 7 |

Rozszerzenia: `pg_trgm 1.6` oraz `plpgsql 1.0`. W badanych schematach nie znaleziono typów enum, widoków materializowanych ani tabel partycjonowanych/obcych. Wszystkie odczytane indeksy mają indisvalid=true, a ograniczenia convalidated=true; nie oznacza to potwierdzenia poprawności biznesowej rekordów. RLS jest wyłączone we wszystkich opisanych relacjach.

## Wielkość danych domenowych

| Tabela | Wiersze |
| --- | --- |
| `public.sezony` | 20 |
| `public.rozgrywki` | 506 |
| `public.rundy` | 1 330 |
| `public.kolejki` | 7 676 |
| `public.mecze` | 37 734 |
| `public.zespoly` | 909 |
| `public.zespoly_sezony` | 3 584 |
| `public.kluby` | 452 |
| `public.zawodnicy` | 19 850 |
| `public.mecze_zawodnicy` | 1 113 018 |
| `public.sklady` | 74 731 |
| `public.sklady_wersje` | 7 301 |
| `public.sklady_wersje_zawodnicy` | 159 137 |
| `public.pliki_zrodlowe` | 71 061 |
| `public.rekordy_zrodla` | 4 499 100 |

Liczba rekordów mecze obejmuje również wpisy bez pełnego wyniku. Liczba w mecze_zawodnicy oznacza wpisy zawodnik–strona–mecz, nie unikalnych zawodników ani potwierdzonych występów.

## Sezony obecne w bazie

| ID | Sezon | Rozgrywki | Mecze |
| --- | --- | --- | --- |
| 41 | 2007/2008 | 5 | 756 |
| 42 | 2008/2009 | 6 | 792 |
| 61 | 2009/2010 | 6 | 792 |
| 81 | 2010/2011 | 6 | 792 |
| 82 | 2011/2012 | 16 | 1535 |
| 102 | 2012/2013 | 12 | 1436 |
| 104 | 2013/2014 | 23 | 1960 |
| 147 | 2014/2015 | 24 | 2132 |
| 164 | 2015/2016 | 23 | 1979 |
| 184 | 2016/2017 | 23 | 2162 |
| 185 | 2017/2018 | 22 | 2186 |
| 186 | 2018/2019 | 26 | 2264 |
| 187 | 2019/2020 | 34 | 2239 |
| 188 | 2020/2021 | 39 | 2342 |
| 190 | 2021/2022 | 41 | 2653 |
| 191 | 2022/2023 | 44 | 2551 |
| 192 | 2023/2024 | 45 | 2514 |
| 193 | 2024/2025 | 43 | 2440 |
| 194 | 2025/2026 | 46 | 2392 |
| 195 | 2026/2027 | 22 | 1817 |

## Priorytetowe rozgrywki sezonu 2026/2027

Poniższe nazwy i identyfikatory pochodzą z lokalnej bazy, nie z weryfikacji aktualnej oferty lig w internecie. W aplikacji wybór rozgrywek powinien zależeć od sezonu; nie utrwalaj tych ID dla wszystkich sezonów.

| ID rozgrywek | Nazwa w bazie | Płeć | ID sezonu | Mecze |
| --- | --- | --- | --- | --- |
| 12011 | Liga Centralna Kobiet | K | 195 | 132 |
| 12009 | LOTTO Superliga kobiet | K | 195 | 90 |
| 12010 | Liga Centralna Mężczyzn | M | 195 | 182 |
| 12007 | LOTTO Superliga | M | 195 | 132 |

We wszystkich czterech rekordach typ_rozgrywek jest NULL, a pobrano_szczegoly=false. Samą flagą nie należy zastępować sprawdzenia dostępności konkretnego meczu lub jego składu.

## Obserwacje ważne dla widoków

- Dla 1 232 meczów nie ustalono gospodarza, dla 1 247 nie ustalono gościa. Zbiory mogą się nakładać; lista meczów wymaga LEFT JOIN dla uczestników.
- 5 627 meczów nie ma przynajmniej jednej wartości wynik_gosp_full/wynik_gosc_full. Nie zamieniaj tego na 0:0.
- 1 796 meczów ma zamiana=true. Inspekcja struktury nie ustala, czy importer już zamienił strony; wymaga to porównania konkretnych rekordów z ich źródłem.

## Stan importu i istniejące anomalie

| Przebieg | Rozpoczęcie | Zakończenie | Status | Wersja importera |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-10T18:34:31.487047+02:00 | 2026-09-10T20:22:43.471994+02:00 | CZESCIOWY | 1.0.0 |

`logs.import_bledy` ma 0 wierszy, natomiast `logs.anomalie_danych` ma 26 197 wpisów. Są to różne rejestry; pusta tabela błędów nie dowodzi kompletnego importu. Poniżej odczytano istniejące wpisy, bez uruchamiania funkcji wykrywania anomalii. Kod i poziom przedstawiają klasyfikację zapisaną przez importer, nie nową diagnozę AI.

| Kod | Poziom | Status | Wpisy |
| --- | --- | --- | --- |
| NIEPOPRAWNA_WARTOSC | OSTRZEZENIE | OTWARTA | 21269 |
| NIEUSTALONA_DRUZYNA | INFO | OTWARTA | 2074 |
| BRAK_SKLADU | OSTRZEZENIE | OTWARTA | 870 |
| BRAK_ID_SEZONOWEGO | OSTRZEZENIE | OTWARTA | 636 |
| BRAK_ID_DRUZYNY | OSTRZEZENIE | OTWARTA | 496 |
| PUSTY_SKLAD | OSTRZEZENIE | OTWARTA | 412 |
| ZAWODNIK_PO_KILKU_STRONACH | OSTRZEZENIE | OTWARTA | 252 |
| BRAK_SKLADU | INFO | OTWARTA | 152 |
| BLAD_POBRANIA | BLAD | OTWARTA | 14 |
| ROZBIEZNE_SKLADY | OSTRZEZENIE | OTWARTA | 13 |
| KATEGORIA_POZA_ZAKRESEM | INFO | OTWARTA | 7 |
| POWTORZONY_ZAWODNIK | OSTRZEZENIE | OTWARTA | 2 |

Na podstawie tego badania nie zmieniono żadnych danych. Do dalszego rozpoznania pozostają kompletność importu, interpretacja wariantów wyniku, semantyka wyjscie oraz sposób normalizacji zamiana.
