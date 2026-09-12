# Schemat `logs` — słownik obiektów

Odczyt: 2026-09-12T19:13:51.748319+02:00. Źródło: katalogi rzeczywistej bazy `localhost:5432/zprp`, w transakcji `REPEATABLE READ READ ONLY`.

[Przegląd bazy](README.md) — [Relacje i różnice](RELATIONSHIPS.md)

To dokumentacja istniejących definicji, a nie skrypt do wykonania. Bazy nie wolno zmieniać bez wyraźnej prośby użytkownika. Liczby wierszy pochodzą z dokładnego COUNT(*) w tej samej migawce co metadane.

Typy, NULL, wartości domyślne i ograniczenia odczytano z PostgreSQL. Opisy przeznaczenia są interpretacją struktury, nie dowodem semantyki każdego pola źródłowego. W definicjach PostgreSQL brak kwalifikatora tabeli oznacza rozstrzygnięcie według search_path użytego podczas odczytu; pełne cele FK są w RELATIONSHIPS.

| Obiekt | Rodzaj | Wiersze | Kolumny |
| --- | --- | --- | --- |
| [anomalie_danych](#anomalie_danych) | tabela | 26197 | 22 |
| [anomalie_danych_log](#anomalie_danych_log) | tabela | 26197 | 32 |
| [anomalie_przeglad](#anomalie_przeglad) | widok | nie liczono | 24 |
| [hale_log](#hale_log) | tabela | 594 | 16 |
| [import_bledy](#import_bledy) | tabela | 0 | 12 |
| [import_pliki](#import_pliki) | tabela | 71061 | 11 |
| [import_przebiegi](#import_przebiegi) | tabela | 1 | 8 |
| [kluby_log](#kluby_log) | tabela | 452 | 27 |
| [kluby_zespoly_historia_log](#kluby_zespoly_historia_log) | tabela | 2948 | 18 |
| [kolejki_log](#kolejki_log) | tabela | 7676 | 18 |
| [licencje_klubowe_log](#licencje_klubowe_log) | tabela | 7256 | 18 |
| [mecze_log](#mecze_log) | tabela | 71291 | 80 |
| [mecze_sedziowie_log](#mecze_sedziowie_log) | tabela | 172923 | 15 |
| [mecze_sztab_log](#mecze_sztab_log) | tabela | 94541 | 19 |
| [mecze_zalaczniki_log](#mecze_zalaczniki_log) | tabela | 23599 | 15 |
| [mecze_zawodnicy_log](#mecze_zawodnicy_log) | tabela | 1113018 | 31 |
| [osoby_sztabu_log](#osoby_sztabu_log) | tabela | 2255 | 14 |
| [pliki_przeglad](#pliki_przeglad) | widok | nie liczono | 14 |
| [pobrania](#pobrania) | tabela | 56583 | 11 |
| [pozycje_log](#pozycje_log) | tabela | 4 | 12 |
| [rozgrywki_log](#rozgrywki_log) | tabela | 506 | 25 |
| [rundy_log](#rundy_log) | tabela | 1330 | 13 |
| [sedziowie_log](#sedziowie_log) | tabela | 2219 | 13 |
| [sezony_log](#sezony_log) | tabela | 20 | 15 |
| [sklady_log](#sklady_log) | tabela | 74745 | 21 |
| [sklady_wersje_log](#sklady_wersje_log) | tabela | 7301 | 15 |
| [sklady_wersje_zawodnicy_log](#sklady_wersje_zawodnicy_log) | tabela | 159137 | 14 |
| [strzelcy_log](#strzelcy_log) | tabela | 62396 | 30 |
| [tabele_grupy_log](#tabele_grupy_log) | tabela | 826 | 14 |
| [tabele_log](#tabele_log) | tabela | 577 | 14 |
| [tabele_wiersze_log](#tabele_wiersze_log) | tabela | 3796 | 35 |
| [zawodnicy_log](#zawodnicy_log) | tabela | 19978 | 16 |
| [zdarzenia](#zdarzenia) | tabela | 1421 | 11 |
| [zespoly_log](#zespoly_log) | tabela | 970 | 16 |
| [zespoly_rozgrywki_log](#zespoly_rozgrywki_log) | tabela | 4496 | 15 |
| [zespoly_sezony_log](#zespoly_sezony_log) | tabela | 16388 | 27 |
| [zwiazki_wojewodzkie_log](#zwiazki_wojewodzkie_log) | tabela | 35 | 12 |

## Mechanizm historii

Tabele `*_log` zawierają kopię kolumn tabeli źródłowej i 10 pól audytu: `log_id`, `log_operacja`, `log_czas`, `log_uzytkownik_bazy`, `log_wykonawca`, `log_id_przebieg`, `log_id_import_pliku`, `log_transakcja`, `log_powod`, `log_klucz`. Ich kluczem jest log_id; identyfikator obiektu domenowego może się wielokrotnie powtarzać.

Nie łącz historii z meczami bez wyboru konkretnej wersji; inaczej zwielokrotnisz wyniki. Tabele historii nie dziedziczą automatycznie FK i ograniczeń domenowych tabeli źródłowej. Ich faktyczne ograniczenia są wypisane poniżej.

`audyt_zmian` działa AFTER INSERT/UPDATE/DELETE jako ENABLE ALWAYS. UPDATE identycznego wiersza nie tworzy wpisu. INSERT i UPDATE zapisują NEW, DELETE zapisuje OLD. Operacja BASELINE jest przewidziana dla zapisu stanu początkowego. UPDATE, DELETE i TRUNCATE historii blokuje trigger `blokada_historii`. Ochrona triggerem nie oznacza, że konto superuser jest technicznie pozbawione możliwości jej zmiany.

<a id="anomalie_danych"></a>

## logs.anomalie_danych

Rejestr wykrytych anomalii z deduplikacją, priorytetem i statusem rozpatrzenia; zmiany tej tabeli również są audytowane.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **26 197**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `klucz_deduplikacji` | `text` | nie | — |
| `id_sezon` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `id_mecz` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `tabela` | `text` | tak | — |
| `klucz_rekordu` | `jsonb` | tak | — |
| `kod` | `text` | nie | — |
| `opis` | `text` | nie | — |
| `szczegoly` | `jsonb` | nie | `'{}'::jsonb` |
| `poziom` | `text` | nie | — |
| `id_pliku` | `bigint` | tak | — |
| `id_przebieg` | `bigint` | tak | — |
| `pierwsze_wykrycie` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `ostatnie_wykrycie` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `licznik` | `bigint` | nie | `1` |
| `status` | `text` | nie | `'OTWARTA'::text` |
| `komentarz` | `text` | tak | — |
| `rozstrzygnal` | `text` | tak | — |
| `czas_rozwiazania` | `timestamp with time zone` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `anomalie_danych_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `anomalie_danych_id_przebieg_fkey` | `FOREIGN KEY (id_przebieg) REFERENCES logs.import_przebiegi(id)` | tak |
| `anomalie_danych_klucz_deduplikacji_key` | `UNIQUE (klucz_deduplikacji)` | tak |
| `anomalie_danych_licznik_check` | `CHECK (licznik > 0)` | tak |
| `anomalie_danych_pkey` | `PRIMARY KEY (id)` | tak |
| `anomalie_danych_poziom_check` | `CHECK (poziom = ANY (ARRAY['INFO'::text, 'OSTRZEZENIE'::text, 'BLAD'::text]))` | tak |
| `anomalie_danych_status_check` | `CHECK (status = ANY (ARRAY['OTWARTA'::text, 'W_ANALIZIE'::text, 'ZAAKCEPTOWANA'::text, 'ROZWIAZANA'::text]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `anomalie_danych_klucz_deduplikacji_key` | `CREATE UNIQUE INDEX anomalie_danych_klucz_deduplikacji_key ON logs.anomalie_danych USING btree (klucz_deduplikacji)` | tak |
| `anomalie_danych_pkey` | `CREATE UNIQUE INDEX anomalie_danych_pkey ON logs.anomalie_danych USING btree (id)` | tak |
| `anomalie_filtr_idx` | `CREATE INDEX anomalie_filtr_idx ON logs.anomalie_danych USING btree (status, id_sezon, id_rozgrywki)` | tak |
| `anomalie_mecz_idx` | `CREATE INDEX anomalie_mecz_idx ON logs.anomalie_danych USING btree (id_mecz)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON logs.anomalie_danych FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON logs.anomalie_danych FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="anomalie_danych_log"></a>

## logs.anomalie_danych_log

Historia wierszy logs.anomalie_danych; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **26 197**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | tak | — |
| `klucz_deduplikacji` | `text` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `id_mecz` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `tabela` | `text` | tak | — |
| `klucz_rekordu` | `jsonb` | tak | — |
| `kod` | `text` | tak | — |
| `opis` | `text` | tak | — |
| `szczegoly` | `jsonb` | tak | — |
| `poziom` | `text` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `id_przebieg` | `bigint` | tak | — |
| `pierwsze_wykrycie` | `timestamp with time zone` | tak | — |
| `ostatnie_wykrycie` | `timestamp with time zone` | tak | — |
| `licznik` | `bigint` | tak | — |
| `status` | `text` | tak | — |
| `komentarz` | `text` | tak | — |
| `rozstrzygnal` | `text` | tak | — |
| `czas_rozwiazania` | `timestamp with time zone` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `anomalie_danych_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `anomalie_danych_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `anomalie_danych_log_log_id_import_pliku_idx` | `CREATE INDEX anomalie_danych_log_log_id_import_pliku_idx ON logs.anomalie_danych_log USING btree (log_id_import_pliku)` | tak |
| `anomalie_danych_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX anomalie_danych_log_log_id_przebieg_log_czas_idx ON logs.anomalie_danych_log USING btree (log_id_przebieg, log_czas)` | tak |
| `anomalie_danych_log_log_klucz_log_id_idx` | `CREATE INDEX anomalie_danych_log_log_klucz_log_id_idx ON logs.anomalie_danych_log USING btree (log_klucz, log_id)` | tak |
| `anomalie_danych_log_pkey` | `CREATE UNIQUE INDEX anomalie_danych_log_pkey ON logs.anomalie_danych_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.anomalie_danych_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="anomalie_przeglad"></a>

## logs.anomalie_przeglad

Widok anomalii wzbogacony o nazwy sezonu i rozgrywek przez LEFT JOIN.

Właściciel: `postgres`. RLS: wyłączone. Widok zwykły; liczby wierszy nie ustalano.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | tak | — |
| `klucz_deduplikacji` | `text` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `id_mecz` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `tabela` | `text` | tak | — |
| `klucz_rekordu` | `jsonb` | tak | — |
| `kod` | `text` | tak | — |
| `opis` | `text` | tak | — |
| `szczegoly` | `jsonb` | tak | — |
| `poziom` | `text` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `id_przebieg` | `bigint` | tak | — |
| `pierwsze_wykrycie` | `timestamp with time zone` | tak | — |
| `ostatnie_wykrycie` | `timestamp with time zone` | tak | — |
| `licznik` | `bigint` | tak | — |
| `status` | `text` | tak | — |
| `komentarz` | `text` | tak | — |
| `rozstrzygnal` | `text` | tak | — |
| `czas_rozwiazania` | `timestamp with time zone` | tak | — |
| `sezon_nazwa` | `text` | tak | — |
| `rozgrywki_nazwa` | `text` | tak | — |

### Ograniczenia

Brak ograniczeń przypisanych w pg_constraint.

### Indeksy

Brak indeksów.

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

### Definicja widoku

```sql
SELECT a.id,
    a.klucz_deduplikacji,
    a.id_sezon,
    a.id_rozgrywki,
    a.id_mecz,
    a.id_zespol,
    a.id_zawodnik,
    a.tabela,
    a.klucz_rekordu,
    a.kod,
    a.opis,
    a.szczegoly,
    a.poziom,
    a.id_pliku,
    a.id_przebieg,
    a.pierwsze_wykrycie,
    a.ostatnie_wykrycie,
    a.licznik,
    a.status,
    a.komentarz,
    a.rozstrzygnal,
    a.czas_rozwiazania,
    s.nazwa AS sezon_nazwa,
    r.nazwa AS rozgrywki_nazwa
   FROM logs.anomalie_danych a
     LEFT JOIN sezony s ON s.id = a.id_sezon
     LEFT JOIN rozgrywki r ON r.id = a.id_rozgrywki;
```

<a id="hale_log"></a>

## logs.hale_log

Historia wierszy public.hale; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **594**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `miasto` | `text` | tak | — |
| `ulica` | `text` | tak | — |
| `numer` | `text` | tak | — |
| `pojemnosc` | `integer` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `hale_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `hale_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `hale_log_log_id_import_pliku_idx` | `CREATE INDEX hale_log_log_id_import_pliku_idx ON logs.hale_log USING btree (log_id_import_pliku)` | tak |
| `hale_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX hale_log_log_id_przebieg_log_czas_idx ON logs.hale_log USING btree (log_id_przebieg, log_czas)` | tak |
| `hale_log_log_klucz_log_id_idx` | `CREATE INDEX hale_log_log_klucz_log_id_idx ON logs.hale_log USING btree (log_klucz, log_id)` | tak |
| `hale_log_pkey` | `CREATE UNIQUE INDEX hale_log_pkey ON logs.hale_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.hale_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="import_bledy"></a>

## logs.import_bledy

Błędy importu z kontekstem przebiegu, próby importu pliku i dokumentu.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **0**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `czas` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `id_przebieg` | `bigint` | tak | — |
| `id_import_pliku` | `bigint` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `zrodlo` | `text` | nie | — |
| `kod` | `text` | nie | — |
| `url` | `text` | tak | — |
| `plik` | `text` | tak | — |
| `wskaznik_json` | `text` | tak | — |
| `blad` | `text` | nie | — |
| `szczegoly` | `jsonb` | nie | `'{}'::jsonb` |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `import_bledy_id_import_pliku_fkey` | `FOREIGN KEY (id_import_pliku) REFERENCES logs.import_pliki(id)` | tak |
| `import_bledy_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `import_bledy_id_przebieg_fkey` | `FOREIGN KEY (id_przebieg) REFERENCES logs.import_przebiegi(id)` | tak |
| `import_bledy_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `import_bledy_pkey` | `CREATE UNIQUE INDEX import_bledy_pkey ON logs.import_bledy USING btree (id)` | tak |
| `import_bledy_przebieg_idx` | `CREATE INDEX import_bledy_przebieg_idx ON logs.import_bledy USING btree (id_przebieg, czas)` | tak |

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

<a id="import_pliki"></a>

## logs.import_pliki

Próby importu pliku, ich status i liczniki operacji.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **71 061**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `id_przebieg` | `bigint` | nie | — |
| `id_pliku` | `bigint` | nie | — |
| `rozpoczecie` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `zakonczenie` | `timestamp with time zone` | tak | — |
| `status` | `text` | nie | `'OCZEKUJE'::text` |
| `dodano` | `bigint` | nie | `0` |
| `zmieniono` | `bigint` | nie | `0` |
| `odrzucono` | `bigint` | nie | `0` |
| `bez_zmian` | `bigint` | nie | `0` |
| `komunikat` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `import_pliki_bez_zmian_check` | `CHECK (bez_zmian >= 0)` | tak |
| `import_pliki_dodano_check` | `CHECK (dodano >= 0)` | tak |
| `import_pliki_id_id_przebieg_key` | `UNIQUE (id, id_przebieg)` | tak |
| `import_pliki_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `import_pliki_id_przebieg_fkey` | `FOREIGN KEY (id_przebieg) REFERENCES logs.import_przebiegi(id)` | tak |
| `import_pliki_odrzucono_check` | `CHECK (odrzucono >= 0)` | tak |
| `import_pliki_pkey` | `PRIMARY KEY (id)` | tak |
| `import_pliki_status_check` | `CHECK (status = ANY (ARRAY['OCZEKUJE'::text, 'W_TRAKCIE'::text, 'SUKCES'::text, 'CZESCIOWY'::text, 'BLAD'::text, 'POMINIETY'::text, 'PRZERWANY'::text]))` | tak |
| `import_pliki_zmieniono_check` | `CHECK (zmieniono >= 0)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `import_pliki_id_id_przebieg_key` | `CREATE UNIQUE INDEX import_pliki_id_id_przebieg_key ON logs.import_pliki USING btree (id, id_przebieg)` | tak |
| `import_pliki_pkey` | `CREATE UNIQUE INDEX import_pliki_pkey ON logs.import_pliki USING btree (id)` | tak |
| `import_pliki_przebieg_idx` | `CREATE INDEX import_pliki_przebieg_idx ON logs.import_pliki USING btree (id_przebieg, status)` | tak |
| `import_pliki_wersja_idx` | `CREATE INDEX import_pliki_wersja_idx ON logs.import_pliki USING btree (id_pliku, id DESC)` | tak |

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

<a id="import_przebiegi"></a>

## logs.import_przebiegi

Przebiegi importera: czas, status, wersja, wykonawca, parametry i podsumowanie.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `rozpoczecie` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `zakonczenie` | `timestamp with time zone` | tak | — |
| `status` | `text` | nie | `'URUCHOMIONY'::text` |
| `wersja_importera` | `text` | nie | — |
| `wykonawca` | `text` | nie | — |
| `parametry` | `jsonb` | nie | `'{}'::jsonb` |
| `podsumowanie` | `jsonb` | nie | `'{}'::jsonb` |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `import_przebiegi_check` | `CHECK (zakonczenie IS NULL OR zakonczenie >= rozpoczecie)` | tak |
| `import_przebiegi_pkey` | `PRIMARY KEY (id)` | tak |
| `import_przebiegi_status_check` | `CHECK (status = ANY (ARRAY['URUCHOMIONY'::text, 'SUKCES'::text, 'CZESCIOWY'::text, 'BLAD'::text, 'PRZERWANY'::text]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `import_przebiegi_pkey` | `CREATE UNIQUE INDEX import_przebiegi_pkey ON logs.import_przebiegi USING btree (id)` | tak |

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

<a id="kluby_log"></a>

## logs.kluby_log

Historia wierszy public.kluby; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **452**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `nr_klubu` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `nr_wzpr` | `integer` | tak | — |
| `miasto` | `text` | tak | — |
| `kod_pocztowy` | `text` | tak | — |
| `ulica` | `text` | tak | — |
| `email` | `text` | tak | — |
| `www` | `text` | tak | — |
| `telefon1` | `text` | tak | — |
| `telefon2` | `text` | tak | — |
| `fax` | `text` | tak | — |
| `skype` | `text` | tak | — |
| `inne_kontakty` | `text` | tak | — |
| `uwagi` | `text` | tak | — |
| `archiwalny` | `boolean` | tak | — |
| `data_aktualizacji` | `timestamp without time zone` | tak | — |
| `logo_url` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `kluby_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `kluby_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `kluby_log_log_id_import_pliku_idx` | `CREATE INDEX kluby_log_log_id_import_pliku_idx ON logs.kluby_log USING btree (log_id_import_pliku)` | tak |
| `kluby_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX kluby_log_log_id_przebieg_log_czas_idx ON logs.kluby_log USING btree (log_id_przebieg, log_czas)` | tak |
| `kluby_log_log_klucz_log_id_idx` | `CREATE INDEX kluby_log_log_klucz_log_id_idx ON logs.kluby_log USING btree (log_klucz, log_id)` | tak |
| `kluby_log_pkey` | `CREATE UNIQUE INDEX kluby_log_pkey ON logs.kluby_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.kluby_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="kluby_zespoly_historia_log"></a>

## logs.kluby_zespoly_historia_log

Historia wierszy public.kluby_zespoly_historia; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **2 948**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `nr_klubu` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `sezon_nazwa` | `text` | tak | — |
| `kategoria` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `kluby_zespoly_historia_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `kluby_zespoly_historia_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `kluby_zespoly_historia_log_log_id_import_pliku_idx` | `CREATE INDEX kluby_zespoly_historia_log_log_id_import_pliku_idx ON logs.kluby_zespoly_historia_log USING btree (log_id_import_pliku)` | tak |
| `kluby_zespoly_historia_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX kluby_zespoly_historia_log_log_id_przebieg_log_czas_idx ON logs.kluby_zespoly_historia_log USING btree (log_id_przebieg, log_czas)` | tak |
| `kluby_zespoly_historia_log_log_klucz_log_id_idx` | `CREATE INDEX kluby_zespoly_historia_log_log_klucz_log_id_idx ON logs.kluby_zespoly_historia_log USING btree (log_klucz, log_id)` | tak |
| `kluby_zespoly_historia_log_pkey` | `CREATE UNIQUE INDEX kluby_zespoly_historia_log_pkey ON logs.kluby_zespoly_historia_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.kluby_zespoly_historia_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="kolejki_log"></a>

## logs.kolejki_log

Historia wierszy public.kolejki; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **7 676**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_runda` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `nr` | `integer` | tak | — |
| `lp` | `integer` | tak | — |
| `data_start` | `timestamp without time zone` | tak | — |
| `data_koniec` | `timestamp without time zone` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `kolejki_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `kolejki_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `kolejki_log_log_id_import_pliku_idx` | `CREATE INDEX kolejki_log_log_id_import_pliku_idx ON logs.kolejki_log USING btree (log_id_import_pliku)` | tak |
| `kolejki_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX kolejki_log_log_id_przebieg_log_czas_idx ON logs.kolejki_log USING btree (log_id_przebieg, log_czas)` | tak |
| `kolejki_log_log_klucz_log_id_idx` | `CREATE INDEX kolejki_log_log_klucz_log_id_idx ON logs.kolejki_log USING btree (log_klucz, log_id)` | tak |
| `kolejki_log_pkey` | `CREATE UNIQUE INDEX kolejki_log_pkey ON logs.kolejki_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.kolejki_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="licencje_klubowe_log"></a>

## logs.licencje_klubowe_log

Historia wierszy public.licencje_klubowe; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **7 256**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `nr_klubu` | `integer` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `plec` | `character(1)` | tak | — |
| `nazwa_licencji` | `text` | tak | — |
| `realizacja` | `text` | tak | — |
| `klucz_zrodlowy` | `text` | tak | — |
| `sezon_nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `licencje_klubowe_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `licencje_klubowe_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `licencje_klubowe_log_log_id_import_pliku_idx` | `CREATE INDEX licencje_klubowe_log_log_id_import_pliku_idx ON logs.licencje_klubowe_log USING btree (log_id_import_pliku)` | tak |
| `licencje_klubowe_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX licencje_klubowe_log_log_id_przebieg_log_czas_idx ON logs.licencje_klubowe_log USING btree (log_id_przebieg, log_czas)` | tak |
| `licencje_klubowe_log_log_klucz_log_id_idx` | `CREATE INDEX licencje_klubowe_log_log_klucz_log_id_idx ON logs.licencje_klubowe_log USING btree (log_klucz, log_id)` | tak |
| `licencje_klubowe_log_pkey` | `CREATE UNIQUE INDEX licencje_klubowe_log_pkey ON logs.licencje_klubowe_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.licencje_klubowe_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_log"></a>

## logs.mecze_log

Historia wierszy public.mecze; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **71 291**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_kolejka` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `id_zespol_gosp` | `integer` | tak | — |
| `id_zespol_gosc` | `integer` | tak | — |
| `id_hala` | `integer` | tak | — |
| `lp` | `integer` | tak | — |
| `alias_gosp` | `integer` | tak | — |
| `alias_gosc` | `integer` | tak | — |
| `wynik_gosp_pol` | `smallint` | tak | — |
| `wynik_gosp_full` | `smallint` | tak | — |
| `wynik_gosc_pol` | `smallint` | tak | — |
| `wynik_gosc_full` | `smallint` | tak | — |
| `wynik_temp_gosp_pol` | `smallint` | tak | — |
| `wynik_temp_gosp_full` | `smallint` | tak | — |
| `wynik_temp_gosc_pol` | `smallint` | tak | — |
| `wynik_temp_gosc_full` | `smallint` | tak | — |
| `wynik_koncowy_gosp` | `smallint` | tak | — |
| `wynik_koncowy_gosc` | `smallint` | tak | — |
| `wynik_bramki_gosp` | `smallint` | tak | — |
| `wynik_bramki_gosc` | `smallint` | tak | — |
| `dogrywka_1_pol_gosp` | `smallint` | tak | — |
| `dogrywka_1_pol_gosc` | `smallint` | tak | — |
| `dogrywka_1_full_gosp` | `smallint` | tak | — |
| `dogrywka_1_full_gosc` | `smallint` | tak | — |
| `dogrywka_2_pol_gosp` | `smallint` | tak | — |
| `dogrywka_2_pol_gosc` | `smallint` | tak | — |
| `dogrywka_2_full_gosp` | `smallint` | tak | — |
| `dogrywka_2_full_gosc` | `smallint` | tak | — |
| `dogrywka_karne_gosp` | `smallint` | tak | — |
| `dogrywka_karne_gosc` | `smallint` | tak | — |
| `karne_bramki_gosp` | `smallint` | tak | — |
| `karne_bramki_gosc` | `smallint` | tak | — |
| `karne_ile_gosp` | `smallint` | tak | — |
| `karne_ile_gosc` | `smallint` | tak | — |
| `kary_gosp` | `smallint` | tak | — |
| `kary_gosc` | `smallint` | tak | — |
| `czy_remis` | `boolean` | tak | — |
| `zwyciezca` | `smallint` | tak | — |
| `timeout1_gosp` | `text` | tak | — |
| `timeout2_gosp` | `text` | tak | — |
| `timeout3_gosp` | `text` | tak | — |
| `timeout1_gosc` | `text` | tak | — |
| `timeout2_gosc` | `text` | tak | — |
| `timeout3_gosc` | `text` | tak | — |
| `data_propozycji` | `timestamp without time zone` | tak | — |
| `data_propozycji_dzien` | `text` | tak | — |
| `data_faktyczna` | `timestamp without time zone` | tak | — |
| `data_faktyczna_dzien` | `text` | tak | — |
| `data_ostatniej_zmiany` | `timestamp without time zone` | tak | — |
| `zamiana` | `boolean` | tak | — |
| `wycofany` | `boolean` | tak | — |
| `wycofany_typ` | `text` | tak | — |
| `id_zespol_wycofany` | `integer` | tak | — |
| `id_zespol_walkower` | `integer` | tak | — |
| `protokol` | `text` | tak | — |
| `protokol_zatwierdzony` | `boolean` | tak | — |
| `protokol_zalacznik_plik` | `text` | tak | — |
| `protokol_zalacznik_typ` | `text` | tak | — |
| `protokol_zalacznik_nazwa` | `text` | tak | — |
| `komentarz` | `text` | tak | — |
| `widzowie` | `integer` | tak | — |
| `transmisja` | `text` | tak | — |
| `transmisja_godzina` | `text` | tak | — |
| `bilety_url` | `text` | tak | — |
| `po_para_id` | `integer` | tak | — |
| `po_para_id_gosp` | `integer` | tak | — |
| `po_para_id_gosc` | `integer` | tak | — |
| `rozgrywki_code` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `mecze_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `mecze_log_log_id_import_pliku_idx` | `CREATE INDEX mecze_log_log_id_import_pliku_idx ON logs.mecze_log USING btree (log_id_import_pliku)` | tak |
| `mecze_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX mecze_log_log_id_przebieg_log_czas_idx ON logs.mecze_log USING btree (log_id_przebieg, log_czas)` | tak |
| `mecze_log_log_klucz_log_id_idx` | `CREATE INDEX mecze_log_log_klucz_log_id_idx ON logs.mecze_log USING btree (log_klucz, log_id)` | tak |
| `mecze_log_pkey` | `CREATE UNIQUE INDEX mecze_log_pkey ON logs.mecze_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.mecze_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_sedziowie_log"></a>

## logs.mecze_sedziowie_log

Historia wierszy public.mecze_sedziowie; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **172 923**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_mecz` | `integer` | tak | — |
| `rola` | `text` | tak | — |
| `id_sedzia` | `integer` | tak | — |
| `nazwisko` | `text` | tak | — |
| `miasto` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_sedziowie_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `mecze_sedziowie_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `mecze_sedziowie_log_log_id_import_pliku_idx` | `CREATE INDEX mecze_sedziowie_log_log_id_import_pliku_idx ON logs.mecze_sedziowie_log USING btree (log_id_import_pliku)` | tak |
| `mecze_sedziowie_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX mecze_sedziowie_log_log_id_przebieg_log_czas_idx ON logs.mecze_sedziowie_log USING btree (log_id_przebieg, log_czas)` | tak |
| `mecze_sedziowie_log_log_klucz_log_id_idx` | `CREATE INDEX mecze_sedziowie_log_log_klucz_log_id_idx ON logs.mecze_sedziowie_log USING btree (log_klucz, log_id)` | tak |
| `mecze_sedziowie_log_pkey` | `CREATE UNIQUE INDEX mecze_sedziowie_log_pkey ON logs.mecze_sedziowie_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.mecze_sedziowie_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_sztab_log"></a>

## logs.mecze_sztab_log

Historia wierszy public.mecze_sztab; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **94 541**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_mecz` | `integer` | tak | — |
| `strona` | `character(4)` | tak | — |
| `id_osoba` | `integer` | tak | — |
| `funkcja` | `text` | tak | — |
| `rola` | `text` | tak | — |
| `licencja` | `text` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_sztab_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `mecze_sztab_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `mecze_sztab_log_log_id_import_pliku_idx` | `CREATE INDEX mecze_sztab_log_log_id_import_pliku_idx ON logs.mecze_sztab_log USING btree (log_id_import_pliku)` | tak |
| `mecze_sztab_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX mecze_sztab_log_log_id_przebieg_log_czas_idx ON logs.mecze_sztab_log USING btree (log_id_przebieg, log_czas)` | tak |
| `mecze_sztab_log_log_klucz_log_id_idx` | `CREATE INDEX mecze_sztab_log_log_klucz_log_id_idx ON logs.mecze_sztab_log USING btree (log_klucz, log_id)` | tak |
| `mecze_sztab_log_pkey` | `CREATE UNIQUE INDEX mecze_sztab_log_pkey ON logs.mecze_sztab_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.mecze_sztab_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_zalaczniki_log"></a>

## logs.mecze_zalaczniki_log

Historia wierszy public.mecze_zalaczniki; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **23 599**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_mecz` | `integer` | tak | — |
| `plik` | `text` | tak | — |
| `nazwa` | `text` | tak | — |
| `typ` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_zalaczniki_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `mecze_zalaczniki_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `mecze_zalaczniki_log_log_id_import_pliku_idx` | `CREATE INDEX mecze_zalaczniki_log_log_id_import_pliku_idx ON logs.mecze_zalaczniki_log USING btree (log_id_import_pliku)` | tak |
| `mecze_zalaczniki_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX mecze_zalaczniki_log_log_id_przebieg_log_czas_idx ON logs.mecze_zalaczniki_log USING btree (log_id_przebieg, log_czas)` | tak |
| `mecze_zalaczniki_log_log_klucz_log_id_idx` | `CREATE INDEX mecze_zalaczniki_log_log_klucz_log_id_idx ON logs.mecze_zalaczniki_log USING btree (log_klucz, log_id)` | tak |
| `mecze_zalaczniki_log_pkey` | `CREATE UNIQUE INDEX mecze_zalaczniki_log_pkey ON logs.mecze_zalaczniki_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.mecze_zalaczniki_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_zawodnicy_log"></a>

## logs.mecze_zawodnicy_log

Historia wierszy public.mecze_zawodnicy; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1 113 018**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_mecz` | `integer` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `strona` | `character(4)` | tak | — |
| `nr_koszulki` | `integer` | tak | — |
| `pozycja` | `text` | tak | — |
| `bramki` | `smallint` | tak | — |
| `dwie_minuty` | `smallint` | tak | — |
| `upomnienie` | `boolean` | tak | — |
| `dyskwalifikacja` | `boolean` | tak | — |
| `kd` | `smallint` | tak | — |
| `wyjscie` | `boolean` | tak | — |
| `karne_liczba` | `smallint` | tak | — |
| `karne_bramki` | `smallint` | tak | — |
| `karne_liczba_seria` | `smallint` | tak | — |
| `karne_bramki_seria` | `smallint` | tak | — |
| `badania_zprp` | `text` | tak | — |
| `badania_wzpr` | `text` | tak | — |
| `foto_url` | `text` | tak | — |
| `data_urodzenia` | `date` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_zawodnicy_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `mecze_zawodnicy_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `mecze_zawodnicy_log_log_id_import_pliku_idx` | `CREATE INDEX mecze_zawodnicy_log_log_id_import_pliku_idx ON logs.mecze_zawodnicy_log USING btree (log_id_import_pliku)` | tak |
| `mecze_zawodnicy_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX mecze_zawodnicy_log_log_id_przebieg_log_czas_idx ON logs.mecze_zawodnicy_log USING btree (log_id_przebieg, log_czas)` | tak |
| `mecze_zawodnicy_log_log_klucz_log_id_idx` | `CREATE INDEX mecze_zawodnicy_log_log_klucz_log_id_idx ON logs.mecze_zawodnicy_log USING btree (log_klucz, log_id)` | tak |
| `mecze_zawodnicy_log_pkey` | `CREATE UNIQUE INDEX mecze_zawodnicy_log_pkey ON logs.mecze_zawodnicy_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.mecze_zawodnicy_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="osoby_sztabu_log"></a>

## logs.osoby_sztabu_log

Historia wierszy public.osoby_sztabu; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **2 255**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_api` | `integer` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `osoby_sztabu_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `osoby_sztabu_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `osoby_sztabu_log_log_id_import_pliku_idx` | `CREATE INDEX osoby_sztabu_log_log_id_import_pliku_idx ON logs.osoby_sztabu_log USING btree (log_id_import_pliku)` | tak |
| `osoby_sztabu_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX osoby_sztabu_log_log_id_przebieg_log_czas_idx ON logs.osoby_sztabu_log USING btree (log_id_przebieg, log_czas)` | tak |
| `osoby_sztabu_log_log_klucz_log_id_idx` | `CREATE INDEX osoby_sztabu_log_log_klucz_log_id_idx ON logs.osoby_sztabu_log USING btree (log_klucz, log_id)` | tak |
| `osoby_sztabu_log_pkey` | `CREATE UNIQUE INDEX osoby_sztabu_log_pkey ON logs.osoby_sztabu_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.osoby_sztabu_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="pliki_przeglad"></a>

## logs.pliki_przeglad

Widok plików z ostatnią próbą importu według największego id import_pliki; brak próby daje NIE_IMPORTOWANO.

Właściciel: `postgres`. RLS: wyłączone. Widok zwykły; liczby wierszy nie ustalano.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | tak | — |
| `sciezka` | `text` | tak | — |
| `sha256` | `text` | tak | — |
| `rodzaj` | `text` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `zarejestrowano` | `timestamp with time zone` | tak | — |
| `id_ostatniej_proby` | `bigint` | tak | — |
| `status` | `text` | tak | — |
| `id_przebieg` | `bigint` | tak | — |
| `zakonczenie` | `timestamp with time zone` | tak | — |
| `dodano` | `bigint` | tak | — |
| `zmieniono` | `bigint` | tak | — |
| `odrzucono` | `bigint` | tak | — |

### Ograniczenia

Brak ograniczeń przypisanych w pg_constraint.

### Indeksy

Brak indeksów.

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

### Definicja widoku

```sql
SELECT p.id,
    p.sciezka,
    p.sha256,
    p.rodzaj,
    p.id_sezon,
    p.id_rozgrywki,
    p.zarejestrowano,
    i.id AS id_ostatniej_proby,
    COALESCE(i.status, 'NIE_IMPORTOWANO'::text) AS status,
    i.id_przebieg,
    i.zakonczenie,
    i.dodano,
    i.zmieniono,
    i.odrzucono
   FROM pliki_zrodlowe p
     LEFT JOIN LATERAL ( SELECT f.id,
            f.id_przebieg,
            f.id_pliku,
            f.rozpoczecie,
            f.zakonczenie,
            f.status,
            f.dodano,
            f.zmieniono,
            f.odrzucono,
            f.bez_zmian,
            f.komunikat
           FROM logs.import_pliki f
          WHERE f.id_pliku = p.id
          ORDER BY f.id DESC
         LIMIT 1) i ON true;
```

<a id="pobrania"></a>

## logs.pobrania

Rejestr pobrań: URL, parametry, czas, status HTTP i błąd.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **56 583**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `id_przebieg` | `bigint` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `url` | `text` | nie | — |
| `parametry` | `jsonb` | nie | `'{}'::jsonb` |
| `rozpoczecie` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `zakonczenie` | `timestamp with time zone` | tak | — |
| `http_status` | `integer` | tak | — |
| `status` | `text` | nie | `'OCZEKUJE'::text` |
| `czas_ms` | `bigint` | tak | — |
| `blad` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `pobrania_czas_ms_check` | `CHECK (czas_ms >= 0)` | tak |
| `pobrania_http_status_check` | `CHECK (http_status >= 100 AND http_status <= 599)` | tak |
| `pobrania_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `pobrania_id_przebieg_fkey` | `FOREIGN KEY (id_przebieg) REFERENCES logs.import_przebiegi(id)` | tak |
| `pobrania_pkey` | `PRIMARY KEY (id)` | tak |
| `pobrania_status_check` | `CHECK (status = ANY (ARRAY['OCZEKUJE'::text, 'W_TRAKCIE'::text, 'SUKCES'::text, 'PUSTA_ODPOWIEDZ'::text, 'BLAD'::text]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `pobrania_pkey` | `CREATE UNIQUE INDEX pobrania_pkey ON logs.pobrania USING btree (id)` | tak |
| `pobrania_przebieg_idx` | `CREATE INDEX pobrania_przebieg_idx ON logs.pobrania USING btree (id_przebieg, rozpoczecie)` | tak |

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

<a id="pozycje_log"></a>

## logs.pozycje_log

Historia wierszy public.pozycje; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **4**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `smallint` | tak | — |
| `nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `pozycje_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `pozycje_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `pozycje_log_log_id_import_pliku_idx` | `CREATE INDEX pozycje_log_log_id_import_pliku_idx ON logs.pozycje_log USING btree (log_id_import_pliku)` | tak |
| `pozycje_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX pozycje_log_log_id_przebieg_log_czas_idx ON logs.pozycje_log USING btree (log_id_przebieg, log_czas)` | tak |
| `pozycje_log_log_klucz_log_id_idx` | `CREATE INDEX pozycje_log_log_klucz_log_id_idx ON logs.pozycje_log USING btree (log_klucz, log_id)` | tak |
| `pozycje_log_pkey` | `CREATE UNIQUE INDEX pozycje_log_pkey ON logs.pozycje_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.pozycje_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="rozgrywki_log"></a>

## logs.rozgrywki_log

Historia wierszy public.rozgrywki; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **506**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `kategoria` | `smallint` | tak | — |
| `plec` | `character(1)` | tak | — |
| `nr_wzpr` | `integer` | tak | — |
| `protokol_typ` | `character(1)` | tak | — |
| `regulamin` | `text` | tak | — |
| `wystartowano` | `boolean` | tak | — |
| `code` | `text` | tak | — |
| `code_export` | `text` | tak | — |
| `ile_zespolow` | `integer` | tak | — |
| `ma_grupy` | `boolean` | tak | — |
| `typ_rozgrywek` | `text` | tak | — |
| `pobrano_szczegoly` | `boolean` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `rozgrywki_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `rozgrywki_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `rozgrywki_log_log_id_import_pliku_idx` | `CREATE INDEX rozgrywki_log_log_id_import_pliku_idx ON logs.rozgrywki_log USING btree (log_id_import_pliku)` | tak |
| `rozgrywki_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX rozgrywki_log_log_id_przebieg_log_czas_idx ON logs.rozgrywki_log USING btree (log_id_przebieg, log_czas)` | tak |
| `rozgrywki_log_log_klucz_log_id_idx` | `CREATE INDEX rozgrywki_log_log_klucz_log_id_idx ON logs.rozgrywki_log USING btree (log_klucz, log_id)` | tak |
| `rozgrywki_log_pkey` | `CREATE UNIQUE INDEX rozgrywki_log_pkey ON logs.rozgrywki_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.rozgrywki_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="rundy_log"></a>

## logs.rundy_log

Historia wierszy public.rundy; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1 330**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `rundy_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `rundy_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `rundy_log_log_id_import_pliku_idx` | `CREATE INDEX rundy_log_log_id_import_pliku_idx ON logs.rundy_log USING btree (log_id_import_pliku)` | tak |
| `rundy_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX rundy_log_log_id_przebieg_log_czas_idx ON logs.rundy_log USING btree (log_id_przebieg, log_czas)` | tak |
| `rundy_log_log_klucz_log_id_idx` | `CREATE INDEX rundy_log_log_klucz_log_id_idx ON logs.rundy_log USING btree (log_klucz, log_id)` | tak |
| `rundy_log_pkey` | `CREATE UNIQUE INDEX rundy_log_pkey ON logs.rundy_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.rundy_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sedziowie_log"></a>

## logs.sedziowie_log

Historia wierszy public.sedziowie; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **2 219**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `nazwisko` | `text` | tak | — |
| `miasto` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sedziowie_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `sedziowie_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sedziowie_log_log_id_import_pliku_idx` | `CREATE INDEX sedziowie_log_log_id_import_pliku_idx ON logs.sedziowie_log USING btree (log_id_import_pliku)` | tak |
| `sedziowie_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX sedziowie_log_log_id_przebieg_log_czas_idx ON logs.sedziowie_log USING btree (log_id_przebieg, log_czas)` | tak |
| `sedziowie_log_log_klucz_log_id_idx` | `CREATE INDEX sedziowie_log_log_klucz_log_id_idx ON logs.sedziowie_log USING btree (log_klucz, log_id)` | tak |
| `sedziowie_log_pkey` | `CREATE UNIQUE INDEX sedziowie_log_pkey ON logs.sedziowie_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.sedziowie_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sezony_log"></a>

## logs.sezony_log

Historia wierszy public.sezony; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **20**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `rok_rozpoczecia` | `integer` | tak | — |
| `ile_rozgrywek` | `integer` | tak | — |
| `stan` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sezony_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `sezony_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sezony_log_log_id_import_pliku_idx` | `CREATE INDEX sezony_log_log_id_import_pliku_idx ON logs.sezony_log USING btree (log_id_import_pliku)` | tak |
| `sezony_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX sezony_log_log_id_przebieg_log_czas_idx ON logs.sezony_log USING btree (log_id_przebieg, log_czas)` | tak |
| `sezony_log_log_klucz_log_id_idx` | `CREATE INDEX sezony_log_log_klucz_log_id_idx ON logs.sezony_log USING btree (log_klucz, log_id)` | tak |
| `sezony_log_pkey` | `CREATE UNIQUE INDEX sezony_log_pkey ON logs.sezony_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.sezony_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sklady_log"></a>

## logs.sklady_log

Historia wierszy public.sklady; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **74 745**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_zespol_sezon` | `bigint` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `nr_koszulki` | `integer` | tak | — |
| `id_pozycja` | `smallint` | tak | — |
| `pozycja_nazwa` | `text` | tak | — |
| `waga` | `numeric(5,1)` | tak | — |
| `wzrost` | `numeric(5,1)` | tak | — |
| `foto_url` | `text` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `data_urodzenia` | `date` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sklady_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `sklady_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sklady_log_log_id_import_pliku_idx` | `CREATE INDEX sklady_log_log_id_import_pliku_idx ON logs.sklady_log USING btree (log_id_import_pliku)` | tak |
| `sklady_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX sklady_log_log_id_przebieg_log_czas_idx ON logs.sklady_log USING btree (log_id_przebieg, log_czas)` | tak |
| `sklady_log_log_klucz_log_id_idx` | `CREATE INDEX sklady_log_log_klucz_log_id_idx ON logs.sklady_log USING btree (log_klucz, log_id)` | tak |
| `sklady_log_pkey` | `CREATE UNIQUE INDEX sklady_log_pkey ON logs.sklady_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.sklady_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sklady_wersje_log"></a>

## logs.sklady_wersje_log

Historia wierszy public.sklady_wersje; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **7 301**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | tak | — |
| `id_zespol_sezon` | `bigint` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `wskaznik_json` | `text` | tak | — |
| `utworzono` | `timestamp with time zone` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sklady_wersje_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `sklady_wersje_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sklady_wersje_log_log_id_import_pliku_idx` | `CREATE INDEX sklady_wersje_log_log_id_import_pliku_idx ON logs.sklady_wersje_log USING btree (log_id_import_pliku)` | tak |
| `sklady_wersje_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX sklady_wersje_log_log_id_przebieg_log_czas_idx ON logs.sklady_wersje_log USING btree (log_id_przebieg, log_czas)` | tak |
| `sklady_wersje_log_log_klucz_log_id_idx` | `CREATE INDEX sklady_wersje_log_log_klucz_log_id_idx ON logs.sklady_wersje_log USING btree (log_klucz, log_id)` | tak |
| `sklady_wersje_log_pkey` | `CREATE UNIQUE INDEX sklady_wersje_log_pkey ON logs.sklady_wersje_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.sklady_wersje_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sklady_wersje_zawodnicy_log"></a>

## logs.sklady_wersje_zawodnicy_log

Historia wierszy public.sklady_wersje_zawodnicy; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **159 137**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_wersja` | `bigint` | tak | — |
| `kolejnosc_zrodlowa` | `integer` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `dane` | `jsonb` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sklady_wersje_zawodnicy_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `sklady_wersje_zawodnicy_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sklady_wersje_zawodnicy_log_log_id_import_pliku_idx` | `CREATE INDEX sklady_wersje_zawodnicy_log_log_id_import_pliku_idx ON logs.sklady_wersje_zawodnicy_log USING btree (log_id_import_pliku)` | tak |
| `sklady_wersje_zawodnicy_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX sklady_wersje_zawodnicy_log_log_id_przebieg_log_czas_idx ON logs.sklady_wersje_zawodnicy_log USING btree (log_id_przebieg, log_czas)` | tak |
| `sklady_wersje_zawodnicy_log_log_klucz_log_id_idx` | `CREATE INDEX sklady_wersje_zawodnicy_log_log_klucz_log_id_idx ON logs.sklady_wersje_zawodnicy_log USING btree (log_klucz, log_id)` | tak |
| `sklady_wersje_zawodnicy_log_pkey` | `CREATE UNIQUE INDEX sklady_wersje_zawodnicy_log_pkey ON logs.sklady_wersje_zawodnicy_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.sklady_wersje_zawodnicy_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="strzelcy_log"></a>

## logs.strzelcy_log

Historia wierszy public.strzelcy; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **62 396**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `id_zawodnik` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `mecze` | `smallint` | tak | — |
| `bramki` | `smallint` | tak | — |
| `srednia` | `numeric(5,2)` | tak | — |
| `dwie_minuty` | `smallint` | tak | — |
| `upomnienie` | `smallint` | tak | — |
| `dyskwalifikacja` | `smallint` | tak | — |
| `kd` | `smallint` | tak | — |
| `karne_liczba` | `smallint` | tak | — |
| `karne_bramki` | `smallint` | tak | — |
| `karne_liczba_seria` | `smallint` | tak | — |
| `karne_bramki_seria` | `smallint` | tak | — |
| `karne_skutecznosc` | `numeric(5,2)` | tak | — |
| `karne_seria_skutecznosc` | `numeric(5,2)` | tak | — |
| `miejsce` | `integer` | tak | — |
| `kolejnosc_zrodlowa` | `integer` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `strzelcy_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `strzelcy_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `strzelcy_log_log_id_import_pliku_idx` | `CREATE INDEX strzelcy_log_log_id_import_pliku_idx ON logs.strzelcy_log USING btree (log_id_import_pliku)` | tak |
| `strzelcy_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX strzelcy_log_log_id_przebieg_log_czas_idx ON logs.strzelcy_log USING btree (log_id_przebieg, log_czas)` | tak |
| `strzelcy_log_log_klucz_log_id_idx` | `CREATE INDEX strzelcy_log_log_klucz_log_id_idx ON logs.strzelcy_log USING btree (log_klucz, log_id)` | tak |
| `strzelcy_log_pkey` | `CREATE UNIQUE INDEX strzelcy_log_pkey ON logs.strzelcy_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.strzelcy_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="tabele_grupy_log"></a>

## logs.tabele_grupy_log

Historia wierszy public.tabele_grupy; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **826**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_tabela` | `integer` | tak | — |
| `grupa_id` | `integer` | tak | — |
| `grupa_nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `tabele_grupy_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `tabele_grupy_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `tabele_grupy_log_log_id_import_pliku_idx` | `CREATE INDEX tabele_grupy_log_log_id_import_pliku_idx ON logs.tabele_grupy_log USING btree (log_id_import_pliku)` | tak |
| `tabele_grupy_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX tabele_grupy_log_log_id_przebieg_log_czas_idx ON logs.tabele_grupy_log USING btree (log_id_przebieg, log_czas)` | tak |
| `tabele_grupy_log_log_klucz_log_id_idx` | `CREATE INDEX tabele_grupy_log_log_klucz_log_id_idx ON logs.tabele_grupy_log USING btree (log_klucz, log_id)` | tak |
| `tabele_grupy_log_pkey` | `CREATE UNIQUE INDEX tabele_grupy_log_pkey ON logs.tabele_grupy_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.tabele_grupy_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="tabele_log"></a>

## logs.tabele_log

Historia wierszy public.tabele; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **577**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `tabela_id` | `integer` | tak | — |
| `tabela_nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `tabele_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `tabele_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `tabele_log_log_id_import_pliku_idx` | `CREATE INDEX tabele_log_log_id_import_pliku_idx ON logs.tabele_log USING btree (log_id_import_pliku)` | tak |
| `tabele_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX tabele_log_log_id_przebieg_log_czas_idx ON logs.tabele_log USING btree (log_id_przebieg, log_czas)` | tak |
| `tabele_log_log_klucz_log_id_idx` | `CREATE INDEX tabele_log_log_klucz_log_id_idx ON logs.tabele_log USING btree (log_klucz, log_id)` | tak |
| `tabele_log_pkey` | `CREATE UNIQUE INDEX tabele_log_pkey ON logs.tabele_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.tabele_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="tabele_wiersze_log"></a>

## logs.tabele_wiersze_log

Historia wierszy public.tabele_wiersze; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **3 796**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `id_tabela_grupa` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `mecze` | `smallint` | tak | — |
| `zwyciestwa` | `smallint` | tak | — |
| `remisy` | `smallint` | tak | — |
| `przegrane` | `smallint` | tak | — |
| `remis_wygrane` | `smallint` | tak | — |
| `remis_przegrane` | `smallint` | tak | — |
| `bramki_zdobyte` | `smallint` | tak | — |
| `bramki_stracone` | `smallint` | tak | — |
| `bramki_zdobyte_ex` | `smallint` | tak | — |
| `bramki_ex` | `smallint` | tak | — |
| `bramki_zdobyte_wyjazd` | `smallint` | tak | — |
| `punkty_zdobyte` | `smallint` | tak | — |
| `punkty_stracone` | `smallint` | tak | — |
| `punkty_ex` | `smallint` | tak | — |
| `punkty_bonusowe` | `smallint` | tak | — |
| `kryteria` | `text` | tak | — |
| `zd_st` | `text` | tak | — |
| `grupa` | `text` | tak | — |
| `grupa_kolor` | `text` | tak | — |
| `miejsce` | `integer` | tak | — |
| `kolejnosc_zrodlowa` | `integer` | tak | — |
| `id_pliku` | `bigint` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `tabele_wiersze_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `tabele_wiersze_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `tabele_wiersze_log_log_id_import_pliku_idx` | `CREATE INDEX tabele_wiersze_log_log_id_import_pliku_idx ON logs.tabele_wiersze_log USING btree (log_id_import_pliku)` | tak |
| `tabele_wiersze_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX tabele_wiersze_log_log_id_przebieg_log_czas_idx ON logs.tabele_wiersze_log USING btree (log_id_przebieg, log_czas)` | tak |
| `tabele_wiersze_log_log_klucz_log_id_idx` | `CREATE INDEX tabele_wiersze_log_log_klucz_log_id_idx ON logs.tabele_wiersze_log USING btree (log_klucz, log_id)` | tak |
| `tabele_wiersze_log_pkey` | `CREATE UNIQUE INDEX tabele_wiersze_log_pkey ON logs.tabele_wiersze_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.tabele_wiersze_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zawodnicy_log"></a>

## logs.zawodnicy_log

Historia wierszy public.zawodnicy; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **19 978**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `data_urodzenia` | `date` | tak | — |
| `foto_url` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zawodnicy_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `zawodnicy_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zawodnicy_log_log_id_import_pliku_idx` | `CREATE INDEX zawodnicy_log_log_id_import_pliku_idx ON logs.zawodnicy_log USING btree (log_id_import_pliku)` | tak |
| `zawodnicy_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX zawodnicy_log_log_id_przebieg_log_czas_idx ON logs.zawodnicy_log USING btree (log_id_przebieg, log_czas)` | tak |
| `zawodnicy_log_log_klucz_log_id_idx` | `CREATE INDEX zawodnicy_log_log_klucz_log_id_idx ON logs.zawodnicy_log USING btree (log_klucz, log_id)` | tak |
| `zawodnicy_log_pkey` | `CREATE UNIQUE INDEX zawodnicy_log_pkey ON logs.zawodnicy_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.zawodnicy_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zdarzenia"></a>

## logs.zdarzenia

Dziennik zdarzeń aplikacji/importera z poziomem i opcjonalnymi powiązaniami operacyjnymi.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1 421**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `czas` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `poziom` | `text` | nie | — |
| `komponent` | `text` | nie | — |
| `operacja` | `text` | tak | — |
| `komunikat` | `text` | nie | — |
| `szczegoly` | `jsonb` | nie | `'{}'::jsonb` |
| `wyjatek` | `text` | tak | — |
| `id_przebieg` | `bigint` | tak | — |
| `id_import_pliku` | `bigint` | tak | — |
| `id_pobranie` | `bigint` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zdarzenia_id_import_pliku_fkey` | `FOREIGN KEY (id_import_pliku) REFERENCES logs.import_pliki(id)` | tak |
| `zdarzenia_id_pobranie_fkey` | `FOREIGN KEY (id_pobranie) REFERENCES logs.pobrania(id)` | tak |
| `zdarzenia_id_przebieg_fkey` | `FOREIGN KEY (id_przebieg) REFERENCES logs.import_przebiegi(id)` | tak |
| `zdarzenia_pkey` | `PRIMARY KEY (id)` | tak |
| `zdarzenia_poziom_check` | `CHECK (poziom = ANY (ARRAY['DEBUG'::text, 'INFO'::text, 'WARNING'::text, 'ERROR'::text, 'CRITICAL'::text]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zdarzenia_czas_idx` | `CREATE INDEX zdarzenia_czas_idx ON logs.zdarzenia USING btree (czas)` | tak |
| `zdarzenia_pkey` | `CREATE UNIQUE INDEX zdarzenia_pkey ON logs.zdarzenia USING btree (id)` | tak |
| `zdarzenia_przebieg_idx` | `CREATE INDEX zdarzenia_przebieg_idx ON logs.zdarzenia USING btree (id_przebieg, czas)` | tak |

### Triggery użytkownika

Brak triggerów użytkownika. Wewnętrzne triggery FK nie są tutaj powtarzane.

<a id="zespoly_log"></a>

## logs.zespoly_log

Historia wierszy public.zespoly; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **970**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | tak | — |
| `nr_klubu` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `kategoria` | `text` | tak | — |
| `wycofany` | `boolean` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zespoly_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `zespoly_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zespoly_log_log_id_import_pliku_idx` | `CREATE INDEX zespoly_log_log_id_import_pliku_idx ON logs.zespoly_log USING btree (log_id_import_pliku)` | tak |
| `zespoly_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX zespoly_log_log_id_przebieg_log_czas_idx ON logs.zespoly_log USING btree (log_id_przebieg, log_czas)` | tak |
| `zespoly_log_log_klucz_log_id_idx` | `CREATE INDEX zespoly_log_log_klucz_log_id_idx ON logs.zespoly_log USING btree (log_klucz, log_id)` | tak |
| `zespoly_log_pkey` | `CREATE UNIQUE INDEX zespoly_log_pkey ON logs.zespoly_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.zespoly_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zespoly_rozgrywki_log"></a>

## logs.zespoly_rozgrywki_log

Historia wierszy public.zespoly_rozgrywki; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **4 496**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_zespol` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `grupa` | `text` | tak | — |
| `grupa_kolor` | `text` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zespoly_rozgrywki_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `zespoly_rozgrywki_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zespoly_rozgrywki_log_log_id_import_pliku_idx` | `CREATE INDEX zespoly_rozgrywki_log_log_id_import_pliku_idx ON logs.zespoly_rozgrywki_log USING btree (log_id_import_pliku)` | tak |
| `zespoly_rozgrywki_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX zespoly_rozgrywki_log_log_id_przebieg_log_czas_idx ON logs.zespoly_rozgrywki_log USING btree (log_id_przebieg, log_czas)` | tak |
| `zespoly_rozgrywki_log_log_klucz_log_id_idx` | `CREATE INDEX zespoly_rozgrywki_log_log_klucz_log_id_idx ON logs.zespoly_rozgrywki_log USING btree (log_klucz, log_id)` | tak |
| `zespoly_rozgrywki_log_pkey` | `CREATE UNIQUE INDEX zespoly_rozgrywki_log_pkey ON logs.zespoly_rozgrywki_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.zespoly_rozgrywki_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zespoly_sezony_log"></a>

## logs.zespoly_sezony_log

Historia wierszy public.zespoly_sezony; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **16 388**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | tak | — |
| `id_api` | `integer` | tak | — |
| `id_zespol` | `integer` | tak | — |
| `id_sezon` | `integer` | tak | — |
| `nr_klubu` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `kategoria` | `text` | tak | — |
| `kod_pocztowy` | `text` | tak | — |
| `miasto` | `text` | tak | — |
| `ulica` | `text` | tak | — |
| `email` | `text` | tak | — |
| `www` | `text` | tak | — |
| `uwagi` | `text` | tak | — |
| `nr_woj` | `integer` | tak | — |
| `wycofany` | `boolean` | tak | — |
| `id_wersja_skladu` | `bigint` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zespoly_sezony_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `zespoly_sezony_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zespoly_sezony_log_log_id_import_pliku_idx` | `CREATE INDEX zespoly_sezony_log_log_id_import_pliku_idx ON logs.zespoly_sezony_log USING btree (log_id_import_pliku)` | tak |
| `zespoly_sezony_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX zespoly_sezony_log_log_id_przebieg_log_czas_idx ON logs.zespoly_sezony_log USING btree (log_id_przebieg, log_czas)` | tak |
| `zespoly_sezony_log_log_klucz_log_id_idx` | `CREATE INDEX zespoly_sezony_log_log_klucz_log_id_idx ON logs.zespoly_sezony_log USING btree (log_klucz, log_id)` | tak |
| `zespoly_sezony_log_pkey` | `CREATE UNIQUE INDEX zespoly_sezony_log_pkey ON logs.zespoly_sezony_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.zespoly_sezony_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zwiazki_wojewodzkie_log"></a>

## logs.zwiazki_wojewodzkie_log

Historia wierszy public.zwiazki_wojewodzkie; kolumny źródłowe oraz metadane audytu. Liczba wierszy oznacza wpisy historii, nie liczbę bieżących obiektów.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **35**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `nr_wzpr` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `log_id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `log_operacja` | `text` | nie | — |
| `log_czas` | `timestamp with time zone` | nie | — |
| `log_uzytkownik_bazy` | `text` | nie | — |
| `log_wykonawca` | `text` | tak | — |
| `log_id_przebieg` | `bigint` | tak | — |
| `log_id_import_pliku` | `bigint` | tak | — |
| `log_transakcja` | `bigint` | nie | — |
| `log_powod` | `text` | tak | — |
| `log_klucz` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zwiazki_wojewodzkie_log_log_operacja_check` | `CHECK (log_operacja = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text, 'BASELINE'::text]))` | tak |
| `zwiazki_wojewodzkie_log_pkey` | `PRIMARY KEY (log_id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zwiazki_wojewodzkie_log_log_id_import_pliku_idx` | `CREATE INDEX zwiazki_wojewodzkie_log_log_id_import_pliku_idx ON logs.zwiazki_wojewodzkie_log USING btree (log_id_import_pliku)` | tak |
| `zwiazki_wojewodzkie_log_log_id_przebieg_log_czas_idx` | `CREATE INDEX zwiazki_wojewodzkie_log_log_id_przebieg_log_czas_idx ON logs.zwiazki_wojewodzkie_log USING btree (log_id_przebieg, log_czas)` | tak |
| `zwiazki_wojewodzkie_log_log_klucz_log_id_idx` | `CREATE INDEX zwiazki_wojewodzkie_log_log_klucz_log_id_idx ON logs.zwiazki_wojewodzkie_log USING btree (log_klucz, log_id)` | tak |
| `zwiazki_wojewodzkie_log_pkey` | `CREATE UNIQUE INDEX zwiazki_wojewodzkie_log_pkey ON logs.zwiazki_wojewodzkie_log USING btree (log_id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `blokada_historii` | ORIGIN | `CREATE TRIGGER blokada_historii BEFORE DELETE OR UPDATE OR TRUNCATE ON logs.zwiazki_wojewodzkie_log FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

## Sekwencje

Odczytano definicje sekwencji, bez wywoływania nextval lub setval i bez odczytu bieżącego licznika.

| Sekwencja | Typ | Start | Krok | Min | Max | Cache | Cykl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `anomalie_danych_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `anomalie_danych_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `hale_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `import_bledy_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `import_pliki_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `import_przebiegi_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `kluby_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `kluby_zespoly_historia_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `kolejki_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `licencje_klubowe_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `mecze_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `mecze_sedziowie_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `mecze_sztab_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `mecze_zalaczniki_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `mecze_zawodnicy_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `osoby_sztabu_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `pobrania_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `pozycje_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `rozgrywki_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `rundy_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `sedziowie_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `sezony_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `sklady_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `sklady_wersje_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `sklady_wersje_zawodnicy_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `strzelcy_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `tabele_grupy_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `tabele_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `tabele_wiersze_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `zawodnicy_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `zdarzenia_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `zespoly_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `zespoly_rozgrywki_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `zespoly_sezony_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `zwiazki_wojewodzkie_log_log_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |

## Funkcje własne

Odczytano definicje przez pg_get_functiondef. Żadnej z tych funkcji nie wywołano. SELECT wywołujący funkcję nie gwarantuje braku zapisów. Funkcje rozszerzeń pg_trgm i plpgsql nie są duplikowane w tej liście.


### logs.audyt_wiersza

`logs.audyt_wiersza()` → `trigger`

Funkcja triggera; zapisuje wiersz do odpowiedniej tabeli *_log. SECURITY DEFINER. Weryfikuje wskazany kontekst importu.

### logs.blokuj_zmiane_archiwum

`logs.blokuj_zmiane_archiwum()` → `trigger`

Funkcja triggera; zgłasza wyjątek, blokując operację objętą triggerem.

### logs.sprawdz_anomalie_meczow

`logs.sprawdz_anomalie_meczow(p_sezon integer, p_przebieg bigint)` → `bigint`

ZAPIS: przez zglos_anomalie dodaje lub aktualizuje anomalie dotyczące uczestników, składów i zawodnika po kilku stronach. Nie uruchamiać podczas inspekcji.

### logs.ustaw_kontekst

`logs.ustaw_kontekst(p_wykonawca text, p_przebieg bigint, p_import_pliku bigint, p_powod text)` → `void`

Zmienia lokalne ustawienia transakcji zprp.* przez set_config; sprawdza zgodność przebiegu i próby importu. Nie była wywoływana.

### logs.utworz_audyt

`logs.utworz_audyt(p_tabela regclass)` → `void`

DDL: tworzy tabelę historii, indeksy i triggery oraz włącza ALWAYS. Nie uruchamiać podczas inspekcji.

### logs.zapisz_stan_poczatkowy

`logs.zapisz_stan_poczatkowy(p_tabela regclass)` → `bigint`

ZAPIS: blokuje tabelę i zapisuje BASELINE do historii, jeśli jest pusta. Nie uruchamiać podczas inspekcji.

### logs.zglos_anomalie

`logs.zglos_anomalie(p_klucz text, p_kod text, p_opis text, p_kontekst jsonb, p_szczegoly jsonb, p_poziom text)` → `bigint`

ZAPIS: INSERT/UPSERT anomalii; zwiększa licznik, uaktualnia kontekst, a rozwiązaną anomalię może ponownie otworzyć.
