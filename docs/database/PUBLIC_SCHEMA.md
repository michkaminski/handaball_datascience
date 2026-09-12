# Schemat `public` — słownik obiektów

Odczyt: 2026-09-12T19:13:51.748319+02:00. Źródło: katalogi rzeczywistej bazy `localhost:5432/zprp`, w transakcji `REPEATABLE READ READ ONLY`.

[Przegląd bazy](README.md) — [Relacje i różnice](RELATIONSHIPS.md)

To dokumentacja istniejących definicji, a nie skrypt do wykonania. Bazy nie wolno zmieniać bez wyraźnej prośby użytkownika. Liczby wierszy pochodzą z dokładnego COUNT(*) w tej samej migawce co metadane.

Typy, NULL, wartości domyślne i ograniczenia odczytano z PostgreSQL. Opisy przeznaczenia są interpretacją struktury, nie dowodem semantyki każdego pola źródłowego. W definicjach PostgreSQL brak kwalifikatora tabeli oznacza rozstrzygnięcie według search_path użytego podczas odczytu; pełne cele FK są w RELATIONSHIPS.

| Obiekt | Rodzaj | Wiersze | Kolumny |
| --- | --- | --- | --- |
| [hale](#hale) | tabela | 301 | 6 |
| [kluby](#kluby) | tabela | 452 | 17 |
| [kluby_zespoly_historia](#kluby_zespoly_historia) | tabela | 2948 | 8 |
| [kolejki](#kolejki) | tabela | 7676 | 8 |
| [licencje_klubowe](#licencje_klubowe) | tabela | 7256 | 8 |
| [mecze](#mecze) | tabela | 37734 | 70 |
| [mecze_sedziowie](#mecze_sedziowie) | tabela | 86719 | 5 |
| [mecze_sztab](#mecze_sztab) | tabela | 94541 | 9 |
| [mecze_zalaczniki](#mecze_zalaczniki) | tabela | 23599 | 5 |
| [mecze_zawodnicy](#mecze_zawodnicy) | tabela | 1113018 | 21 |
| [osoby_sztabu](#osoby_sztabu) | tabela | 2255 | 4 |
| [pliki_zrodlowe](#pliki_zrodlowe) | tabela | 71061 | 12 |
| [pozycje](#pozycje) | tabela | 4 | 2 |
| [rekordy_zrodla](#rekordy_zrodla) | tabela | 4499100 | 6 |
| [rozgrywki](#rozgrywki) | tabela | 506 | 15 |
| [rundy](#rundy) | tabela | 1330 | 3 |
| [sedziowie](#sedziowie) | tabela | 1158 | 3 |
| [sezony](#sezony) | tabela | 20 | 5 |
| [sklady](#sklady) | tabela | 74731 | 11 |
| [sklady_wersje](#sklady_wersje) | tabela | 7301 | 5 |
| [sklady_wersje_zawodnicy](#sklady_wersje_zawodnicy) | tabela | 159137 | 4 |
| [strzelcy](#strzelcy) | tabela | 62396 | 20 |
| [tabele](#tabele) | tabela | 577 | 4 |
| [tabele_grupy](#tabele_grupy) | tabela | 826 | 4 |
| [tabele_wiersze](#tabele_wiersze) | tabela | 3796 | 25 |
| [zawodnicy](#zawodnicy) | tabela | 19850 | 6 |
| [zespoly](#zespoly) | tabela | 909 | 6 |
| [zespoly_rozgrywki](#zespoly_rozgrywki) | tabela | 4362 | 5 |
| [zespoly_sezony](#zespoly_sezony) | tabela | 3584 | 17 |
| [zwiazki_wojewodzkie](#zwiazki_wojewodzkie) | tabela | 19 | 2 |

<a id="hale"></a>

## public.hale

Hale meczowe, adres i pojemność. Unikalność adresu uwzględnia również NULL.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **301**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('hale_id_seq'::regclass)` |
| `nazwa` | `text` | tak | — |
| `miasto` | `text` | tak | — |
| `ulica` | `text` | tak | — |
| `numer` | `text` | tak | — |
| `pojemnosc` | `integer` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `hale_nazwa_miasto_ulica_numer_key` | `UNIQUE NULLS NOT DISTINCT (nazwa, miasto, ulica, numer)` | tak |
| `hale_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `hale_nazwa_miasto_ulica_numer_key` | `CREATE UNIQUE INDEX hale_nazwa_miasto_ulica_numer_key ON public.hale USING btree (nazwa, miasto, ulica, numer) NULLS NOT DISTINCT` | tak |
| `hale_pkey` | `CREATE UNIQUE INDEX hale_pkey ON public.hale USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON hale FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON hale FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="kluby"></a>

## public.kluby

Kluby jako organizacje; dane kontaktowe, związek wojewódzki i logo.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **452**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `nr_klubu` | `integer` | nie | — |
| `nazwa` | `text` | nie | — |
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

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `kluby_nr_wzpr_fkey` | `FOREIGN KEY (nr_wzpr) REFERENCES zwiazki_wojewodzkie(nr_wzpr)` | tak |
| `kluby_pkey` | `PRIMARY KEY (nr_klubu)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_kluby_nazwa_trgm` | `CREATE INDEX idx_kluby_nazwa_trgm ON public.kluby USING gin (nazwa gin_trgm_ops)` | tak |
| `idx_kluby_nr_wzpr` | `CREATE INDEX idx_kluby_nr_wzpr ON public.kluby USING btree (nr_wzpr)` | tak |
| `kluby_pkey` | `CREATE UNIQUE INDEX kluby_pkey ON public.kluby USING btree (nr_klubu)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON kluby FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON kluby FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="kluby_zespoly_historia"></a>

## public.kluby_zespoly_historia

Historia przypisań zespołów do klubów ze źródłowymi oznaczeniami sezonu. id_zespol i id_sezon nie mają tutaj kluczy obcych.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **2 948**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `nr_klubu` | `integer` | nie | — |
| `id_zespol` | `integer` | nie | — |
| `id_sezon` | `integer` | tak | — |
| `sezon_nazwa` | `text` | tak | — |
| `kategoria` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `nazwa` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `kluby_zespoly_historia_kategoria_check` | `CHECK (kategoria IS NULL OR kategoria = 'Senior'::text)` | tak |
| `kluby_zespoly_historia_nr_klubu_fkey` | `FOREIGN KEY (nr_klubu) REFERENCES kluby(nr_klubu)` | tak |
| `kluby_zespoly_historia_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_kzh_id_zespol` | `CREATE INDEX idx_kzh_id_zespol ON public.kluby_zespoly_historia USING btree (id_zespol)` | tak |
| `idx_kzh_nr_klubu` | `CREATE INDEX idx_kzh_nr_klubu ON public.kluby_zespoly_historia USING btree (nr_klubu)` | tak |
| `kluby_zespoly_historia_pkey` | `CREATE UNIQUE INDEX kluby_zespoly_historia_pkey ON public.kluby_zespoly_historia USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON kluby_zespoly_historia FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON kluby_zespoly_historia FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="kolejki"></a>

## public.kolejki

Kolejki rundy z terminami i identyfikatorem rozgrywek. Złożony FK kontroluje zgodność rundy i rozgrywek.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **7 676**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `id_runda` | `integer` | nie | — |
| `nazwa` | `text` | tak | — |
| `nr` | `integer` | tak | — |
| `lp` | `integer` | tak | — |
| `data_start` | `timestamp without time zone` | tak | — |
| `data_koniec` | `timestamp without time zone` | tak | — |
| `id_rozgrywki` | `integer` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `kolejki_id_id_rozgrywki_key` | `UNIQUE (id, id_rozgrywki)` | tak |
| `kolejki_id_runda_fkey` | `FOREIGN KEY (id_runda) REFERENCES rundy(id)` | tak |
| `kolejki_id_runda_id_rozgrywki_fkey` | `FOREIGN KEY (id_runda, id_rozgrywki) REFERENCES rundy(id, id_rozgrywki) DEFERRABLE` | tak |
| `kolejki_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_kolejki_data_start` | `CREATE INDEX idx_kolejki_data_start ON public.kolejki USING btree (data_start)` | tak |
| `idx_kolejki_id_runda` | `CREATE INDEX idx_kolejki_id_runda ON public.kolejki USING btree (id_runda)` | tak |
| `kolejki_id_id_rozgrywki_key` | `CREATE UNIQUE INDEX kolejki_id_id_rozgrywki_key ON public.kolejki USING btree (id, id_rozgrywki)` | tak |
| `kolejki_pkey` | `CREATE UNIQUE INDEX kolejki_pkey ON public.kolejki USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON kolejki FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON kolejki FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="licencje_klubowe"></a>

## public.licencje_klubowe

Licencje klubu z kluczem źródłowym i opcjonalnym sezonem.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **7 256**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('licencje_klubowe_id_seq'::regclass)` |
| `nr_klubu` | `integer` | nie | — |
| `id_sezon` | `integer` | tak | — |
| `plec` | `character(1)` | tak | — |
| `nazwa_licencji` | `text` | tak | — |
| `realizacja` | `text` | tak | — |
| `klucz_zrodlowy` | `text` | nie | — |
| `sezon_nazwa` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `licencje_klubowe_id_sezon_fkey` | `FOREIGN KEY (id_sezon) REFERENCES sezony(id)` | tak |
| `licencje_klubowe_nr_klubu_fkey` | `FOREIGN KEY (nr_klubu) REFERENCES kluby(nr_klubu)` | tak |
| `licencje_klubowe_nr_klubu_klucz_zrodlowy_key` | `UNIQUE (nr_klubu, klucz_zrodlowy)` | tak |
| `licencje_klubowe_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_licencje_id_sezon` | `CREATE INDEX idx_licencje_id_sezon ON public.licencje_klubowe USING btree (id_sezon)` | tak |
| `idx_licencje_nr_klubu` | `CREATE INDEX idx_licencje_nr_klubu ON public.licencje_klubowe USING btree (nr_klubu)` | tak |
| `licencje_klubowe_nr_klubu_klucz_zrodlowy_key` | `CREATE UNIQUE INDEX licencje_klubowe_nr_klubu_klucz_zrodlowy_key ON public.licencje_klubowe USING btree (nr_klubu, klucz_zrodlowy)` | tak |
| `licencje_klubowe_pkey` | `CREATE UNIQUE INDEX licencje_klubowe_pkey ON public.licencje_klubowe USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON licencje_klubowe FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON licencje_klubowe FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze"></a>

## public.mecze

Centralna tabela meczu: sezon, rozgrywki, kolejka, uczestnicy, warianty wyniku, dogrywki, kary, terminy i protokół. Obaj uczestnicy mogą być NULL.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **37 734**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `id_kolejka` | `integer` | nie | — |
| `id_rozgrywki` | `integer` | nie | — |
| `id_sezon` | `integer` | nie | — |
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

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_id_hala_fkey` | `FOREIGN KEY (id_hala) REFERENCES hale(id)` | tak |
| `mecze_id_kolejka_fkey` | `FOREIGN KEY (id_kolejka) REFERENCES kolejki(id)` | tak |
| `mecze_id_kolejka_id_rozgrywki_fkey` | `FOREIGN KEY (id_kolejka, id_rozgrywki) REFERENCES kolejki(id, id_rozgrywki) DEFERRABLE` | tak |
| `mecze_id_rozgrywki_fkey` | `FOREIGN KEY (id_rozgrywki) REFERENCES rozgrywki(id)` | tak |
| `mecze_id_rozgrywki_id_sezon_fkey` | `FOREIGN KEY (id_rozgrywki, id_sezon) REFERENCES rozgrywki(id, id_sezon) DEFERRABLE` | tak |
| `mecze_id_sezon_fkey` | `FOREIGN KEY (id_sezon) REFERENCES sezony(id)` | tak |
| `mecze_id_zespol_gosc_fkey` | `FOREIGN KEY (id_zespol_gosc) REFERENCES zespoly(id)` | tak |
| `mecze_id_zespol_gosc_id_rozgrywki_fkey` | `FOREIGN KEY (id_zespol_gosc, id_rozgrywki) REFERENCES zespoly_rozgrywki(id_zespol, id_rozgrywki) DEFERRABLE` | tak |
| `mecze_id_zespol_gosp_fkey` | `FOREIGN KEY (id_zespol_gosp) REFERENCES zespoly(id)` | tak |
| `mecze_id_zespol_gosp_id_rozgrywki_fkey` | `FOREIGN KEY (id_zespol_gosp, id_rozgrywki) REFERENCES zespoly_rozgrywki(id_zespol, id_rozgrywki) DEFERRABLE` | tak |
| `mecze_id_zespol_walkower_fkey` | `FOREIGN KEY (id_zespol_walkower) REFERENCES zespoly(id)` | tak |
| `mecze_id_zespol_wycofany_fkey` | `FOREIGN KEY (id_zespol_wycofany) REFERENCES zespoly(id)` | tak |
| `mecze_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_mecze_data_faktyczna` | `CREATE INDEX idx_mecze_data_faktyczna ON public.mecze USING btree (data_faktyczna)` | tak |
| `idx_mecze_id_hala` | `CREATE INDEX idx_mecze_id_hala ON public.mecze USING btree (id_hala)` | tak |
| `idx_mecze_id_kolejka` | `CREATE INDEX idx_mecze_id_kolejka ON public.mecze USING btree (id_kolejka)` | tak |
| `idx_mecze_id_rozgrywki` | `CREATE INDEX idx_mecze_id_rozgrywki ON public.mecze USING btree (id_rozgrywki)` | tak |
| `idx_mecze_id_sezon` | `CREATE INDEX idx_mecze_id_sezon ON public.mecze USING btree (id_sezon)` | tak |
| `idx_mecze_po_para_id` | `CREATE INDEX idx_mecze_po_para_id ON public.mecze USING btree (po_para_id) WHERE (po_para_id IS NOT NULL)` | tak |
| `idx_mecze_zespol_dowolna_strona` | `CREATE INDEX idx_mecze_zespol_dowolna_strona ON public.mecze USING btree (id_zespol_gosp, id_zespol_gosc)` | tak |
| `idx_mecze_zespol_gosc` | `CREATE INDEX idx_mecze_zespol_gosc ON public.mecze USING btree (id_zespol_gosc)` | tak |
| `idx_mecze_zespol_gosp` | `CREATE INDEX idx_mecze_zespol_gosp ON public.mecze USING btree (id_zespol_gosp)` | tak |
| `mecze_pkey` | `CREATE UNIQUE INDEX mecze_pkey ON public.mecze USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON mecze FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON mecze FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_sedziowie"></a>

## public.mecze_sedziowie

Obsada meczu według roli; oprócz identyfikatora sędziego przechowuje migawkę nazwiska i miasta.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **86 719**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_mecz` | `integer` | nie | — |
| `rola` | `text` | nie | — |
| `id_sedzia` | `integer` | nie | — |
| `nazwisko` | `text` | tak | — |
| `miasto` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_sedziowie_id_mecz_fkey` | `FOREIGN KEY (id_mecz) REFERENCES mecze(id)` | tak |
| `mecze_sedziowie_id_sedzia_fkey` | `FOREIGN KEY (id_sedzia) REFERENCES sedziowie(id)` | tak |
| `mecze_sedziowie_pkey` | `PRIMARY KEY (id_mecz, rola)` | tak |
| `mecze_sedziowie_rola_check` | `CHECK (rola = ANY (ARRAY['pierwszy'::text, 'drugi'::text, 'delegat'::text, 'delegat2'::text, 'sekretarz'::text, 'czas'::text]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_mecze_sedziowie_sedzia` | `CREATE INDEX idx_mecze_sedziowie_sedzia ON public.mecze_sedziowie USING btree (id_sedzia)` | tak |
| `mecze_sedziowie_pkey` | `CREATE UNIQUE INDEX mecze_sedziowie_pkey ON public.mecze_sedziowie USING btree (id_mecz, rola)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON mecze_sedziowie FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON mecze_sedziowie FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_sztab"></a>

## public.mecze_sztab

Sztab po stronie gospodarza lub gościa; funkcja, rola, licencja i migawka danych osoby.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **94 541**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('mecze_sztab_id_seq'::regclass)` |
| `id_mecz` | `integer` | nie | — |
| `strona` | `character(4)` | nie | — |
| `id_osoba` | `integer` | nie | — |
| `funkcja` | `text` | tak | — |
| `rola` | `text` | tak | — |
| `licencja` | `text` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_sztab_id_mecz_fkey` | `FOREIGN KEY (id_mecz) REFERENCES mecze(id)` | tak |
| `mecze_sztab_id_mecz_strona_id_osoba_rola_key` | `UNIQUE NULLS NOT DISTINCT (id_mecz, strona, id_osoba, rola)` | tak |
| `mecze_sztab_id_osoba_fkey` | `FOREIGN KEY (id_osoba) REFERENCES osoby_sztabu(id)` | tak |
| `mecze_sztab_pkey` | `PRIMARY KEY (id)` | tak |
| `mecze_sztab_strona_check` | `CHECK (strona = ANY (ARRAY['gosp'::bpchar, 'gosc'::bpchar]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_mecze_sztab_mecz` | `CREATE INDEX idx_mecze_sztab_mecz ON public.mecze_sztab USING btree (id_mecz)` | tak |
| `idx_mecze_sztab_osoba` | `CREATE INDEX idx_mecze_sztab_osoba ON public.mecze_sztab USING btree (id_osoba)` | tak |
| `mecze_sztab_id_mecz_strona_id_osoba_rola_key` | `CREATE UNIQUE INDEX mecze_sztab_id_mecz_strona_id_osoba_rola_key ON public.mecze_sztab USING btree (id_mecz, strona, id_osoba, rola) NULLS NOT DISTINCT` | tak |
| `mecze_sztab_pkey` | `CREATE UNIQUE INDEX mecze_sztab_pkey ON public.mecze_sztab USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON mecze_sztab FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON mecze_sztab FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_zalaczniki"></a>

## public.mecze_zalaczniki

Załączniki przypisane do meczu; ścieżka, nazwa i typ.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **23 599**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('mecze_zalaczniki_id_seq'::regclass)` |
| `id_mecz` | `integer` | nie | — |
| `plik` | `text` | tak | — |
| `nazwa` | `text` | tak | — |
| `typ` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_zalaczniki_id_mecz_fkey` | `FOREIGN KEY (id_mecz) REFERENCES mecze(id)` | tak |
| `mecze_zalaczniki_id_mecz_plik_nazwa_typ_key` | `UNIQUE NULLS NOT DISTINCT (id_mecz, plik, nazwa, typ)` | tak |
| `mecze_zalaczniki_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_mecze_zalaczniki_mecz` | `CREATE INDEX idx_mecze_zalaczniki_mecz ON public.mecze_zalaczniki USING btree (id_mecz)` | tak |
| `mecze_zalaczniki_id_mecz_plik_nazwa_typ_key` | `CREATE UNIQUE INDEX mecze_zalaczniki_id_mecz_plik_nazwa_typ_key ON public.mecze_zalaczniki USING btree (id_mecz, plik, nazwa, typ) NULLS NOT DISTINCT` | tak |
| `mecze_zalaczniki_pkey` | `CREATE UNIQUE INDEX mecze_zalaczniki_pkey ON public.mecze_zalaczniki USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON mecze_zalaczniki FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON mecze_zalaczniki FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="mecze_zawodnicy"></a>

## public.mecze_zawodnicy

Skład i statystyki osoby po konkretnej stronie meczu. Klucz zawiera id_mecz, strona i id_zawodnik; ten sam zawodnik może wystąpić w kilku stronach.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1 113 018**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_mecz` | `integer` | nie | — |
| `id_zawodnik` | `integer` | nie | — |
| `strona` | `character(4)` | nie | — |
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

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `mecze_zawodnicy_id_mecz_fkey` | `FOREIGN KEY (id_mecz) REFERENCES mecze(id)` | tak |
| `mecze_zawodnicy_id_zawodnik_fkey` | `FOREIGN KEY (id_zawodnik) REFERENCES zawodnicy(id)` | tak |
| `mecze_zawodnicy_pkey` | `PRIMARY KEY (id_mecz, strona, id_zawodnik)` | tak |
| `mecze_zawodnicy_strona_check` | `CHECK (strona = ANY (ARRAY['gosp'::bpchar, 'gosc'::bpchar, 'inne'::bpchar]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_mecze_zawodnicy_zawodnik` | `CREATE INDEX idx_mecze_zawodnicy_zawodnik ON public.mecze_zawodnicy USING btree (id_zawodnik)` | tak |
| `mecze_zawodnicy_pkey` | `CREATE UNIQUE INDEX mecze_zawodnicy_pkey ON public.mecze_zawodnicy USING btree (id_mecz, strona, id_zawodnik)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON mecze_zawodnicy FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON mecze_zawodnicy FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="osoby_sztabu"></a>

## public.osoby_sztabu

Osoby sztabu z wewnętrznym id i osobnym, opcjonalnym id_api.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **2 255**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('osoby_sztabu_id_seq'::regclass)` |
| `id_api` | `integer` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `osoby_sztabu_id_api_key` | `UNIQUE (id_api)` | tak |
| `osoby_sztabu_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_osoby_sztabu_nazwisko_trgm` | `CREATE INDEX idx_osoby_sztabu_nazwisko_trgm ON public.osoby_sztabu USING gin (nazwisko gin_trgm_ops)` | tak |
| `osoby_sztabu_id_api_key` | `CREATE UNIQUE INDEX osoby_sztabu_id_api_key ON public.osoby_sztabu USING btree (id_api)` | tak |
| `osoby_sztabu_pkey` | `CREATE UNIQUE INDEX osoby_sztabu_pkey ON public.osoby_sztabu USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON osoby_sztabu FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON osoby_sztabu FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="pliki_zrodlowe"></a>

## public.pliki_zrodlowe

Archiwum plików źródłowych: bajty, JSON, hash i kontekst. CHECK weryfikuje długość oraz SHA-256 rzeczywistej treści; trigger blokuje modyfikację i usunięcie.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **71 061**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `sciezka` | `text` | nie | — |
| `sha256` | `text` | nie | — |
| `rozmiar` | `bigint` | nie | — |
| `rodzaj` | `text` | nie | — |
| `id_sezon` | `integer` | tak | — |
| `id_rozgrywki` | `integer` | tak | — |
| `zarejestrowano` | `timestamp with time zone` | nie | `clock_timestamp()` |
| `kodowanie` | `text` | nie | `'UTF-8'::text` |
| `tresc` | `bytea` | nie | — |
| `dokument` | `jsonb` | tak | — |
| `blad_parsowania` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `pliki_zrodlowe_check` | `CHECK (rozmiar = octet_length(tresc))` | tak |
| `pliki_zrodlowe_check1` | `CHECK (sha256 = encode(sha256(tresc), 'hex'::text))` | tak |
| `pliki_zrodlowe_id_rozgrywki_fkey` | `FOREIGN KEY (id_rozgrywki) REFERENCES rozgrywki(id)` | tak |
| `pliki_zrodlowe_id_sezon_fkey` | `FOREIGN KEY (id_sezon) REFERENCES sezony(id)` | tak |
| `pliki_zrodlowe_pkey` | `PRIMARY KEY (id)` | tak |
| `pliki_zrodlowe_rozmiar_check` | `CHECK (rozmiar >= 0)` | tak |
| `pliki_zrodlowe_sciezka_sha256_key` | `UNIQUE (sciezka, sha256)` | tak |
| `pliki_zrodlowe_sha256_check` | `CHECK (sha256 ~ '^[0-9a-f]{64}$'::text)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `pliki_kontekst_idx` | `CREATE INDEX pliki_kontekst_idx ON public.pliki_zrodlowe USING btree (id_sezon, id_rozgrywki)` | tak |
| `pliki_zrodlowe_pkey` | `CREATE UNIQUE INDEX pliki_zrodlowe_pkey ON public.pliki_zrodlowe USING btree (id)` | tak |
| `pliki_zrodlowe_sciezka_sha256_key` | `CREATE UNIQUE INDEX pliki_zrodlowe_sciezka_sha256_key ON public.pliki_zrodlowe USING btree (sciezka, sha256)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `pliki_niezmienne` | ORIGIN | `CREATE TRIGGER pliki_niezmienne BEFORE DELETE OR UPDATE OR TRUNCATE ON pliki_zrodlowe FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="pozycje"></a>

## public.pozycje

Słownik pozycji zawodnika, używany przez sklady.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **4**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `smallint` | nie | — |
| `nazwa` | `text` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `pozycje_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `pozycje_pkey` | `CREATE UNIQUE INDEX pozycje_pkey ON public.pozycje USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON pozycje FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON pozycje FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="rekordy_zrodla"></a>

## public.rekordy_zrodla

Pochodzenie rekordu: nazwa tabeli i klucz JSON wskazują dokument oraz ścieżkę JSON. Jest FK do pliku, ale nie do dynamicznie wskazanego rekordu domenowego.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **4 499 100**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `tabela` | `text` | nie | — |
| `klucz_rekordu` | `jsonb` | nie | — |
| `id_pliku` | `bigint` | nie | — |
| `wskaznik_json` | `text` | nie | — |
| `zarejestrowano` | `timestamp with time zone` | nie | `clock_timestamp()` |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `rekordy_zrodla_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `rekordy_zrodla_klucz_rekordu_check` | `CHECK (jsonb_typeof(klucz_rekordu) = 'object'::text)` | tak |
| `rekordy_zrodla_pkey` | `PRIMARY KEY (id)` | tak |
| `rekordy_zrodla_tabela_klucz_rekordu_id_pliku_wskaznik_json_key` | `UNIQUE (tabela, klucz_rekordu, id_pliku, wskaznik_json)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `rekordy_zrodla_pkey` | `CREATE UNIQUE INDEX rekordy_zrodla_pkey ON public.rekordy_zrodla USING btree (id)` | tak |
| `rekordy_zrodla_plik_idx` | `CREATE INDEX rekordy_zrodla_plik_idx ON public.rekordy_zrodla USING btree (id_pliku)` | tak |
| `rekordy_zrodla_tabela_klucz_rekordu_id_pliku_wskaznik_json_key` | `CREATE UNIQUE INDEX rekordy_zrodla_tabela_klucz_rekordu_id_pliku_wskaznik_json_key ON public.rekordy_zrodla USING btree (tabela, klucz_rekordu, id_pliku, wskaznik_json)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `pochodzenie_niezmienne` | ORIGIN | `CREATE TRIGGER pochodzenie_niezmienne BEFORE DELETE OR UPDATE OR TRUNCATE ON rekordy_zrodla FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="rozgrywki"></a>

## public.rozgrywki

Rozgrywki danego sezonu. CHECK ogranicza kategorię do 1 i niepustą płeć do K/M; plec może być NULL. Zawiera flagę pobrano_szczegoly.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **506**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `id_sezon` | `integer` | nie | — |
| `nazwa` | `text` | nie | — |
| `kategoria` | `smallint` | nie | — |
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
| `pobrano_szczegoly` | `boolean` | nie | `false` |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `rozgrywki_id_id_sezon_key` | `UNIQUE (id, id_sezon)` | tak |
| `rozgrywki_id_sezon_fkey` | `FOREIGN KEY (id_sezon) REFERENCES sezony(id)` | tak |
| `rozgrywki_kategoria_check` | `CHECK (kategoria = 1)` | tak |
| `rozgrywki_nr_wzpr_fkey` | `FOREIGN KEY (nr_wzpr) REFERENCES zwiazki_wojewodzkie(nr_wzpr)` | tak |
| `rozgrywki_pkey` | `PRIMARY KEY (id)` | tak |
| `rozgrywki_plec_check` | `CHECK (plec = ANY (ARRAY['K'::bpchar, 'M'::bpchar]))` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_rozgrywki_id_sezon` | `CREATE INDEX idx_rozgrywki_id_sezon ON public.rozgrywki USING btree (id_sezon)` | tak |
| `idx_rozgrywki_nazwa_trgm` | `CREATE INDEX idx_rozgrywki_nazwa_trgm ON public.rozgrywki USING gin (nazwa gin_trgm_ops)` | tak |
| `idx_rozgrywki_nr_wzpr` | `CREATE INDEX idx_rozgrywki_nr_wzpr ON public.rozgrywki USING btree (nr_wzpr)` | tak |
| `rozgrywki_id_id_sezon_key` | `CREATE UNIQUE INDEX rozgrywki_id_id_sezon_key ON public.rozgrywki USING btree (id, id_sezon)` | tak |
| `rozgrywki_pkey` | `CREATE UNIQUE INDEX rozgrywki_pkey ON public.rozgrywki USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON rozgrywki FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON rozgrywki FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="rundy"></a>

## public.rundy

Etapy rozgrywek. Unikalność pary id i id_rozgrywki jest celem złożonego FK z kolejki.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1 330**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `id_rozgrywki` | `integer` | nie | — |
| `nazwa` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `rundy_id_id_rozgrywki_key` | `UNIQUE (id, id_rozgrywki)` | tak |
| `rundy_id_rozgrywki_fkey` | `FOREIGN KEY (id_rozgrywki) REFERENCES rozgrywki(id)` | tak |
| `rundy_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_rundy_id_rozgrywki` | `CREATE INDEX idx_rundy_id_rozgrywki ON public.rundy USING btree (id_rozgrywki)` | tak |
| `rundy_id_id_rozgrywki_key` | `CREATE UNIQUE INDEX rundy_id_id_rozgrywki_key ON public.rundy USING btree (id, id_rozgrywki)` | tak |
| `rundy_pkey` | `CREATE UNIQUE INDEX rundy_pkey ON public.rundy USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON rundy FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON rundy FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sedziowie"></a>

## public.sedziowie

Słownik sędziów; migawka meczowa może być dostępna osobno w mecze_sedziowie.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **1 158**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `nazwisko` | `text` | tak | — |
| `miasto` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sedziowie_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_sedziowie_nazwisko_trgm` | `CREATE INDEX idx_sedziowie_nazwisko_trgm ON public.sedziowie USING gin (nazwisko gin_trgm_ops)` | tak |
| `sedziowie_pkey` | `CREATE UNIQUE INDEX sedziowie_pkey ON public.sedziowie USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON sedziowie FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON sedziowie FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sezony"></a>

## public.sezony

Katalog sezonów z unikalną nazwą i opcjonalnym rokiem rozpoczęcia.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **20**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `nazwa` | `text` | nie | — |
| `rok_rozpoczecia` | `integer` | tak | — |
| `ile_rozgrywek` | `integer` | tak | — |
| `stan` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sezony_nazwa_key` | `UNIQUE (nazwa)` | tak |
| `sezony_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sezony_nazwa_key` | `CREATE UNIQUE INDEX sezony_nazwa_key ON public.sezony USING btree (nazwa)` | tak |
| `sezony_pkey` | `CREATE UNIQUE INDEX sezony_pkey ON public.sezony USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON sezony FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON sezony FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sklady"></a>

## public.sklady

Znormalizowany skład zespołu w sezonie z pozycją i migawką danych zawodnika. Nie jest to lista występów meczowych.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **74 731**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_zespol_sezon` | `bigint` | nie | — |
| `id_zawodnik` | `integer` | nie | — |
| `nr_koszulki` | `integer` | tak | — |
| `id_pozycja` | `smallint` | tak | — |
| `pozycja_nazwa` | `text` | tak | — |
| `waga` | `numeric(5,1)` | tak | — |
| `wzrost` | `numeric(5,1)` | tak | — |
| `foto_url` | `text` | tak | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `data_urodzenia` | `date` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sklady_id_pozycja_fkey` | `FOREIGN KEY (id_pozycja) REFERENCES pozycje(id)` | tak |
| `sklady_id_zawodnik_fkey` | `FOREIGN KEY (id_zawodnik) REFERENCES zawodnicy(id)` | tak |
| `sklady_id_zespol_sezon_fkey` | `FOREIGN KEY (id_zespol_sezon) REFERENCES zespoly_sezony(id)` | tak |
| `sklady_pkey` | `PRIMARY KEY (id_zespol_sezon, id_zawodnik)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_sklady_id_zawodnik` | `CREATE INDEX idx_sklady_id_zawodnik ON public.sklady USING btree (id_zawodnik)` | tak |
| `sklady_pkey` | `CREATE UNIQUE INDEX sklady_pkey ON public.sklady USING btree (id_zespol_sezon, id_zawodnik)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON sklady FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON sklady FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sklady_wersje"></a>

## public.sklady_wersje

Wersje składów sezonowych, powiązane z konkretnym plikiem źródłowym i wskaźnikiem JSON.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **7 301**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `id_zespol_sezon` | `bigint` | nie | — |
| `id_pliku` | `bigint` | nie | — |
| `wskaznik_json` | `text` | nie | `''::text` |
| `utworzono` | `timestamp with time zone` | nie | `clock_timestamp()` |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sklady_wersje_id_id_zespol_sezon_key` | `UNIQUE (id, id_zespol_sezon)` | tak |
| `sklady_wersje_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `sklady_wersje_id_zespol_sezon_fkey` | `FOREIGN KEY (id_zespol_sezon) REFERENCES zespoly_sezony(id)` | tak |
| `sklady_wersje_id_zespol_sezon_id_pliku_wskaznik_json_key` | `UNIQUE (id_zespol_sezon, id_pliku, wskaznik_json)` | tak |
| `sklady_wersje_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sklady_wersje_id_id_zespol_sezon_key` | `CREATE UNIQUE INDEX sklady_wersje_id_id_zespol_sezon_key ON public.sklady_wersje USING btree (id, id_zespol_sezon)` | tak |
| `sklady_wersje_id_zespol_sezon_id_pliku_wskaznik_json_key` | `CREATE UNIQUE INDEX sklady_wersje_id_zespol_sezon_id_pliku_wskaznik_json_key ON public.sklady_wersje USING btree (id_zespol_sezon, id_pliku, wskaznik_json)` | tak |
| `sklady_wersje_pkey` | `CREATE UNIQUE INDEX sklady_wersje_pkey ON public.sklady_wersje USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON sklady_wersje FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON sklady_wersje FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="sklady_wersje_zawodnicy"></a>

## public.sklady_wersje_zawodnicy

Wiersze wersji składu w kolejności źródłowej. JSON zachowuje dane, nawet gdy nie ustalono id_zawodnik.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **159 137**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_wersja` | `bigint` | nie | — |
| `kolejnosc_zrodlowa` | `integer` | nie | — |
| `id_zawodnik` | `integer` | tak | — |
| `dane` | `jsonb` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `sklady_wersje_zawodnicy_id_wersja_fkey` | `FOREIGN KEY (id_wersja) REFERENCES sklady_wersje(id)` | tak |
| `sklady_wersje_zawodnicy_id_zawodnik_fkey` | `FOREIGN KEY (id_zawodnik) REFERENCES zawodnicy(id)` | tak |
| `sklady_wersje_zawodnicy_kolejnosc_zrodlowa_check` | `CHECK (kolejnosc_zrodlowa > 0)` | tak |
| `sklady_wersje_zawodnicy_pkey` | `PRIMARY KEY (id_wersja, kolejnosc_zrodlowa)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `sklady_wersje_zawodnicy_pkey` | `CREATE UNIQUE INDEX sklady_wersje_zawodnicy_pkey ON public.sklady_wersje_zawodnicy USING btree (id_wersja, kolejnosc_zrodlowa)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON sklady_wersje_zawodnicy FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON sklady_wersje_zawodnicy FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="strzelcy"></a>

## public.strzelcy

Źródłowa klasyfikacja strzelców rozgrywek z miejscem, kolejnością źródłową i opcjonalnym plikiem. Unikalność obejmuje rozgrywki i zawodnika, nie drużynę.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **62 396**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('strzelcy_id_seq'::regclass)` |
| `id_rozgrywki` | `integer` | nie | — |
| `id_zawodnik` | `integer` | nie | — |
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
| `kolejnosc_zrodlowa` | `integer` | nie | — |
| `id_pliku` | `bigint` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `strzelcy_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `strzelcy_id_rozgrywki_fkey` | `FOREIGN KEY (id_rozgrywki) REFERENCES rozgrywki(id)` | tak |
| `strzelcy_id_rozgrywki_id_zawodnik_key` | `UNIQUE (id_rozgrywki, id_zawodnik)` | tak |
| `strzelcy_id_zawodnik_fkey` | `FOREIGN KEY (id_zawodnik) REFERENCES zawodnicy(id)` | tak |
| `strzelcy_id_zespol_fkey` | `FOREIGN KEY (id_zespol) REFERENCES zespoly(id)` | tak |
| `strzelcy_kolejnosc_zrodlowa_check` | `CHECK (kolejnosc_zrodlowa > 0)` | tak |
| `strzelcy_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_strzelcy_zawodnik` | `CREATE INDEX idx_strzelcy_zawodnik ON public.strzelcy USING btree (id_zawodnik)` | tak |
| `idx_strzelcy_zespol` | `CREATE INDEX idx_strzelcy_zespol ON public.strzelcy USING btree (id_zespol)` | tak |
| `strzelcy_id_rozgrywki_id_zawodnik_key` | `CREATE UNIQUE INDEX strzelcy_id_rozgrywki_id_zawodnik_key ON public.strzelcy USING btree (id_rozgrywki, id_zawodnik)` | tak |
| `strzelcy_pkey` | `CREATE UNIQUE INDEX strzelcy_pkey ON public.strzelcy USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON strzelcy FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON strzelcy FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="tabele"></a>

## public.tabele

Nazwane tabele klasyfikacji w obrębie rozgrywek; tabela_id jest identyfikatorem źródłowym.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **577**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('tabele_id_seq'::regclass)` |
| `id_rozgrywki` | `integer` | nie | — |
| `tabela_id` | `integer` | nie | — |
| `tabela_nazwa` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `tabele_id_rozgrywki_fkey` | `FOREIGN KEY (id_rozgrywki) REFERENCES rozgrywki(id)` | tak |
| `tabele_id_rozgrywki_tabela_id_key` | `UNIQUE (id_rozgrywki, tabela_id)` | tak |
| `tabele_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_tabele_id_rozgrywki` | `CREATE INDEX idx_tabele_id_rozgrywki ON public.tabele USING btree (id_rozgrywki)` | tak |
| `tabele_id_rozgrywki_tabela_id_key` | `CREATE UNIQUE INDEX tabele_id_rozgrywki_tabela_id_key ON public.tabele USING btree (id_rozgrywki, tabela_id)` | tak |
| `tabele_pkey` | `CREATE UNIQUE INDEX tabele_pkey ON public.tabele USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON tabele FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON tabele FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="tabele_grupy"></a>

## public.tabele_grupy

Grupy konkretnej tabeli klasyfikacji; grupa_id jest identyfikatorem źródłowym.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **826**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('tabele_grupy_id_seq'::regclass)` |
| `id_tabela` | `integer` | nie | — |
| `grupa_id` | `integer` | nie | — |
| `grupa_nazwa` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `tabele_grupy_id_tabela_fkey` | `FOREIGN KEY (id_tabela) REFERENCES tabele(id)` | tak |
| `tabele_grupy_id_tabela_grupa_id_key` | `UNIQUE (id_tabela, grupa_id)` | tak |
| `tabele_grupy_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `tabele_grupy_id_tabela_grupa_id_key` | `CREATE UNIQUE INDEX tabele_grupy_id_tabela_grupa_id_key ON public.tabele_grupy USING btree (id_tabela, grupa_id)` | tak |
| `tabele_grupy_pkey` | `CREATE UNIQUE INDEX tabele_grupy_pkey ON public.tabele_grupy USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON tabele_grupy FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON tabele_grupy FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="tabele_wiersze"></a>

## public.tabele_wiersze

Wiersze klasyfikacji zespołów, punkty, bramki, miejsce i kolejność źródłowa. Unikalna para grupa tabeli i zespół.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **3 796**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | `nextval('tabele_wiersze_id_seq'::regclass)` |
| `id_tabela_grupa` | `integer` | nie | — |
| `id_zespol` | `integer` | nie | — |
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
| `kolejnosc_zrodlowa` | `integer` | nie | — |
| `id_pliku` | `bigint` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `tabele_wiersze_id_pliku_fkey` | `FOREIGN KEY (id_pliku) REFERENCES pliki_zrodlowe(id)` | tak |
| `tabele_wiersze_id_tabela_grupa_fkey` | `FOREIGN KEY (id_tabela_grupa) REFERENCES tabele_grupy(id)` | tak |
| `tabele_wiersze_id_tabela_grupa_id_zespol_key` | `UNIQUE (id_tabela_grupa, id_zespol)` | tak |
| `tabele_wiersze_id_zespol_fkey` | `FOREIGN KEY (id_zespol) REFERENCES zespoly(id)` | tak |
| `tabele_wiersze_kolejnosc_zrodlowa_check` | `CHECK (kolejnosc_zrodlowa > 0)` | tak |
| `tabele_wiersze_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_tabele_wiersze_grupa` | `CREATE INDEX idx_tabele_wiersze_grupa ON public.tabele_wiersze USING btree (id_tabela_grupa)` | tak |
| `idx_tabele_wiersze_zespol` | `CREATE INDEX idx_tabele_wiersze_zespol ON public.tabele_wiersze USING btree (id_zespol)` | tak |
| `tabele_wiersze_id_tabela_grupa_id_zespol_key` | `CREATE UNIQUE INDEX tabele_wiersze_id_tabela_grupa_id_zespol_key ON public.tabele_wiersze USING btree (id_tabela_grupa, id_zespol)` | tak |
| `tabele_wiersze_pkey` | `CREATE UNIQUE INDEX tabele_wiersze_pkey ON public.tabele_wiersze USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON tabele_wiersze FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON tabele_wiersze FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zawodnicy"></a>

## public.zawodnicy

Słownik zawodników; dane osobowe mogą mieć historyczne migawki w składach i wpisach meczowych.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **19 850**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `imie` | `text` | tak | — |
| `nazwisko` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `data_urodzenia` | `date` | tak | — |
| `foto_url` | `text` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zawodnicy_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_zawodnicy_data_ur` | `CREATE INDEX idx_zawodnicy_data_ur ON public.zawodnicy USING btree (data_urodzenia)` | tak |
| `idx_zawodnicy_nazwisko_trgm` | `CREATE INDEX idx_zawodnicy_nazwisko_trgm ON public.zawodnicy USING gin (nazwisko gin_trgm_ops)` | tak |
| `zawodnicy_pkey` | `CREATE UNIQUE INDEX zawodnicy_pkey ON public.zawodnicy USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON zawodnicy FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON zawodnicy FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zespoly"></a>

## public.zespoly

Tożsamość zespołu, opcjonalny klub i dane ogólne. Nie zastępuje migawki sezonowej.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **909**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `integer` | nie | — |
| `nr_klubu` | `integer` | tak | — |
| `nazwa` | `text` | tak | — |
| `plec` | `character(1)` | tak | — |
| `kategoria` | `text` | tak | — |
| `wycofany` | `boolean` | tak | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zespoly_kategoria_check` | `CHECK (kategoria IS NULL OR kategoria = 'Senior'::text)` | tak |
| `zespoly_nr_klubu_fkey` | `FOREIGN KEY (nr_klubu) REFERENCES kluby(nr_klubu)` | tak |
| `zespoly_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_zespoly_nazwa_trgm` | `CREATE INDEX idx_zespoly_nazwa_trgm ON public.zespoly USING gin (nazwa gin_trgm_ops)` | tak |
| `idx_zespoly_nr_klubu` | `CREATE INDEX idx_zespoly_nr_klubu ON public.zespoly USING btree (nr_klubu)` | tak |
| `zespoly_pkey` | `CREATE UNIQUE INDEX zespoly_pkey ON public.zespoly USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON zespoly FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON zespoly FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zespoly_rozgrywki"></a>

## public.zespoly_rozgrywki

Udział zespołu w rozgrywkach z przypisaniem sezonu i grupy. Złożone FK pilnują sezonu rozgrywek oraz istnienia migawki zespołu.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **4 362**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id_zespol` | `integer` | nie | — |
| `id_rozgrywki` | `integer` | nie | — |
| `grupa` | `text` | tak | — |
| `grupa_kolor` | `text` | tak | — |
| `id_sezon` | `integer` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zespoly_rozgrywki_id_rozgrywki_fkey` | `FOREIGN KEY (id_rozgrywki) REFERENCES rozgrywki(id)` | tak |
| `zespoly_rozgrywki_id_rozgrywki_id_sezon_fkey` | `FOREIGN KEY (id_rozgrywki, id_sezon) REFERENCES rozgrywki(id, id_sezon) DEFERRABLE` | tak |
| `zespoly_rozgrywki_id_zespol_fkey` | `FOREIGN KEY (id_zespol) REFERENCES zespoly(id)` | tak |
| `zespoly_rozgrywki_id_zespol_id_sezon_fkey` | `FOREIGN KEY (id_zespol, id_sezon) REFERENCES zespoly_sezony(id_zespol, id_sezon) DEFERRABLE` | tak |
| `zespoly_rozgrywki_pkey` | `PRIMARY KEY (id_zespol, id_rozgrywki)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_zespoly_rozgrywki_rozgrywki` | `CREATE INDEX idx_zespoly_rozgrywki_rozgrywki ON public.zespoly_rozgrywki USING btree (id_rozgrywki)` | tak |
| `zespoly_rozgrywki_pkey` | `CREATE UNIQUE INDEX zespoly_rozgrywki_pkey ON public.zespoly_rozgrywki USING btree (id_zespol, id_rozgrywki)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON zespoly_rozgrywki FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON zespoly_rozgrywki FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zespoly_sezony"></a>

## public.zespoly_sezony

Migawka zespołu w sezonie z wewnętrznym bigint id i osobnym id_api. id_wersja_skladu wskazuje wersję należącą do tej samej migawki.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **3 584**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `id` | `bigint` | nie | `GENERATED ALWAYS AS IDENTITY` |
| `id_api` | `integer` | tak | — |
| `id_zespol` | `integer` | nie | — |
| `id_sezon` | `integer` | nie | — |
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

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zespoly_sezony_id_api_key` | `UNIQUE (id_api)` | tak |
| `zespoly_sezony_id_sezon_fkey` | `FOREIGN KEY (id_sezon) REFERENCES sezony(id)` | tak |
| `zespoly_sezony_id_wersja_skladu_id_fkey` | `FOREIGN KEY (id_wersja_skladu, id) REFERENCES sklady_wersje(id, id_zespol_sezon) DEFERRABLE` | tak |
| `zespoly_sezony_id_zespol_fkey` | `FOREIGN KEY (id_zespol) REFERENCES zespoly(id)` | tak |
| `zespoly_sezony_id_zespol_id_sezon_key` | `UNIQUE (id_zespol, id_sezon)` | tak |
| `zespoly_sezony_kategoria_check` | `CHECK (kategoria IS NULL OR kategoria = 'Senior'::text)` | tak |
| `zespoly_sezony_nr_klubu_fkey` | `FOREIGN KEY (nr_klubu) REFERENCES kluby(nr_klubu)` | tak |
| `zespoly_sezony_pkey` | `PRIMARY KEY (id)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `idx_zespoly_sezony_id_sezon` | `CREATE INDEX idx_zespoly_sezony_id_sezon ON public.zespoly_sezony USING btree (id_sezon)` | tak |
| `idx_zespoly_sezony_id_zespol` | `CREATE INDEX idx_zespoly_sezony_id_zespol ON public.zespoly_sezony USING btree (id_zespol)` | tak |
| `zespoly_sezony_id_api_key` | `CREATE UNIQUE INDEX zespoly_sezony_id_api_key ON public.zespoly_sezony USING btree (id_api)` | tak |
| `zespoly_sezony_id_zespol_id_sezon_key` | `CREATE UNIQUE INDEX zespoly_sezony_id_zespol_id_sezon_key ON public.zespoly_sezony USING btree (id_zespol, id_sezon)` | tak |
| `zespoly_sezony_pkey` | `CREATE UNIQUE INDEX zespoly_sezony_pkey ON public.zespoly_sezony USING btree (id)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON zespoly_sezony FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON zespoly_sezony FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

<a id="zwiazki_wojewodzkie"></a>

## public.zwiazki_wojewodzkie

Słownik wojewódzkich związków piłki ręcznej.

Właściciel: `postgres`. RLS: wyłączone. Wiersze: **19**.

### Kolumny

| Kolumna | Typ PostgreSQL | NULL dozwolone | Domyślne / generowanie |
| --- | --- | --- | --- |
| `nr_wzpr` | `integer` | nie | — |
| `nazwa` | `text` | nie | — |

### Ograniczenia

| Nazwa | Definicja | Zweryfikowane |
| --- | --- | --- |
| `zwiazki_wojewodzkie_pkey` | `PRIMARY KEY (nr_wzpr)` | tak |

### Indeksy

| Nazwa | Definicja | Ważny |
| --- | --- | --- |
| `zwiazki_wojewodzkie_pkey` | `CREATE UNIQUE INDEX zwiazki_wojewodzkie_pkey ON public.zwiazki_wojewodzkie USING btree (nr_wzpr)` | tak |

### Triggery użytkownika

| Nazwa | Tryb | Definicja |
| --- | --- | --- |
| `audyt_zmian` | ALWAYS | `CREATE TRIGGER audyt_zmian AFTER INSERT OR DELETE OR UPDATE ON zwiazki_wojewodzkie FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()` |
| `blokada_truncate` | ORIGIN | `CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON zwiazki_wojewodzkie FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()` |

## Sekwencje

Odczytano definicje sekwencji, bez wywoływania nextval lub setval i bez odczytu bieżącego licznika.

| Sekwencja | Typ | Start | Krok | Min | Max | Cache | Cykl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hale_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `licencje_klubowe_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `mecze_sztab_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `mecze_zalaczniki_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `osoby_sztabu_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `pliki_zrodlowe_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `rekordy_zrodla_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `sklady_wersje_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
| `strzelcy_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `tabele_grupy_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `tabele_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `tabele_wiersze_id_seq` | integer | 1 | 1 | 1 | 2147483647 | 1 | nie |
| `zespoly_sezony_id_seq` | bigint | 1 | 1 | 1 | 9223372036854775807 | 1 | nie |
