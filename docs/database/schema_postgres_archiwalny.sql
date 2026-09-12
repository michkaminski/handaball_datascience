-- ZPRP: schemat docelowy dla NOWEJ, PUSTEJ bazy PostgreSQL 15+.
-- Wersja 2026-09-10. To nie jest migracja istniejacej bazy.
-- Dane domenowe: seniorzy K/M. Pelne zrodla zachowujemy w pliki_zrodlowe.
-- Instalacja jako wlasciciel schematow, nie konto aplikacji.
-- Kontrakt importera: README_import_audyt.md.
BEGIN;
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS logs;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA logs FROM PUBLIC;
SET LOCAL search_path = pg_catalog, public;

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public; -- do wyszukiwania rozmytego po nazwiskach


-- ============================================================================
-- 1. SŁOWNIKI / ENCJE PODSTAWOWE
-- ============================================================================

CREATE TABLE public.sezony (
    id                  INTEGER PRIMARY KEY,           -- ID_sezon
    nazwa               TEXT NOT NULL UNIQUE,          -- Nazwa, np. "2007/2008"
    rok_rozpoczecia     INTEGER,                       -- Rok_rozpoczecia
    ile_rozgrywek       INTEGER,                       -- IleRozgrywek (deklarowane przez API; może się różnić od faktycznie pobranych z uwagi na filtr Kategoria=1)
    stan                TEXT                           -- Stan
);

CREATE TABLE public.zwiazki_wojewodzkie (
    nr_wzpr             INTEGER PRIMARY KEY,           -- NrWZPR
    nazwa               TEXT NOT NULL                  -- NazwaWZPR (agregowane z pól rozgrywki.NazwaWZPR, brak osobnego endpointu źródłowego)
);

CREATE TABLE public.kluby (
    nr_klubu            INTEGER PRIMARY KEY,           -- NrKlubu
    nazwa               TEXT NOT NULL,                 -- Nazwa
    nr_wzpr             INTEGER REFERENCES public.zwiazki_wojewodzkie(nr_wzpr),
    miasto              TEXT,
    kod_pocztowy        TEXT,                          -- KodPocztowy
    ulica               TEXT,                          -- Ulica
    email               TEXT,
    www                 TEXT,
    telefon1            TEXT,
    telefon2            TEXT,
    fax                 TEXT,
    skype               TEXT,
    inne_kontakty       TEXT,                          -- Inne_kontakty
    uwagi               TEXT,
    archiwalny          BOOLEAN,                       -- Archiwalny (0/1)
    data_aktualizacji   TIMESTAMP,                     -- Data_akt
    logo_url            TEXT                           -- Logo
);
CREATE INDEX idx_kluby_nr_wzpr ON public.kluby(nr_wzpr);
CREATE INDEX idx_kluby_nazwa_trgm ON public.kluby USING gin (nazwa gin_trgm_ops);

-- Seniorskie wpisy historii klubowej; pełny niefiltrowany wykaz pozostaje
-- w pliki_zrodlowe. Brak FK pozwala zachować historyczne identyfikatory,
-- dla których nie pobrano jeszcze odrębnej encji drużyny lub sezonu.
CREATE TABLE public.kluby_zespoly_historia (
    id                  INTEGER PRIMARY KEY,           -- Id (rekord członkostwa zespołu w sezonie wg API klubu)
    nr_klubu            INTEGER NOT NULL REFERENCES public.kluby(nr_klubu),
    id_zespol           INTEGER NOT NULL,              -- ID_zespol (bez FK - patrz komentarz wyżej)
    id_sezon            INTEGER,                       -- ID_sezon (bez FK - może wykraczać poza 20 pobranych sezonów)
    sezon_nazwa         TEXT,                          -- Sezon (tekstowo, dla sezonów spoza zakresu archiwum)
    kategoria           TEXT CHECK (kategoria IS NULL OR kategoria = 'Senior'), -- tylko seniorzy
    plec                CHAR(1),
    nazwa               TEXT
);
CREATE INDEX idx_kzh_nr_klubu ON public.kluby_zespoly_historia(nr_klubu);
CREATE INDEX idx_kzh_id_zespol ON public.kluby_zespoly_historia(id_zespol);

CREATE TABLE public.licencje_klubowe (
    id                  SERIAL PRIMARY KEY,
    nr_klubu            INTEGER NOT NULL REFERENCES public.kluby(nr_klubu),
    id_sezon            INTEGER REFERENCES public.sezony(id),  -- dopasowane z pola tekstowego "Sezon" w ETL
    plec                CHAR(1),
    nazwa_licencji      TEXT,                          -- NazwaLicencji
    realizacja          TEXT                           -- Realizacja
);
CREATE INDEX idx_licencje_nr_klubu ON public.licencje_klubowe(nr_klubu);
CREATE INDEX idx_licencje_id_sezon ON public.licencje_klubowe(id_sezon);

CREATE TABLE public.pozycje (
    id                  SMALLINT PRIMARY KEY,          -- IdPozycja
    nazwa               TEXT NOT NULL                  -- Pozycja: 1=Bramkarz, 2=Rozgrywający, 3=Obrotowy, 4=Skrzydłowy
);

CREATE TABLE public.zawodnicy (
    id                  INTEGER PRIMARY KEY,           -- NrZawodnika (zweryfikowane: globalnie stabilny i unikalny)
    imie                TEXT,
    nazwisko            TEXT,
    plec                CHAR(1),
    data_urodzenia      DATE,                          -- DataUr / dataUr
    foto_url            TEXT                           -- Foto (najnowszy znany link)
);
CREATE INDEX idx_zawodnicy_nazwisko_trgm ON public.zawodnicy USING gin (nazwisko gin_trgm_ops);
CREATE INDEX idx_zawodnicy_data_ur ON public.zawodnicy(data_urodzenia);


-- ============================================================================
-- 2. ROZGRYWKI / STRUKTURA SEZONU
-- ============================================================================

CREATE TABLE public.rozgrywki (
    id                  INTEGER PRIMARY KEY,           -- Id_rozgrywki (globalnie unikalne, niezależnie od sezonu)
    id_sezon            INTEGER NOT NULL REFERENCES public.sezony(id),
    nazwa               TEXT NOT NULL,
    kategoria           SMALLINT NOT NULL CHECK (kategoria = 1), -- 1 = seniorzy
    plec                CHAR(1) CHECK (plec IN ('K','M')),
    nr_wzpr             INTEGER REFERENCES public.zwiazki_wojewodzkie(nr_wzpr),
    protokol_typ        CHAR(1),                       -- Protokol_typ (T/N/K - kod źródłowy, znaczenie nie w pełni potwierdzone)
    regulamin           TEXT,                          -- Regulamin
    wystartowano        BOOLEAN,                       -- Wystartowano
    code                TEXT,
    code_export         TEXT,
    ile_zespolow        INTEGER,                       -- IleZespolow
    ma_grupy            BOOLEAN,                       -- Grupy (flaga 0/1: czy rozgrywki mają podgrupy)
    typ_rozgrywek       TEXT,                          -- RozgrywkiTypCode (z terminarz.json)
    pobrano_szczegoly   BOOLEAN NOT NULL DEFAULT FALSE -- szczegółowy stan w logs.pobrania
);
CREATE INDEX idx_rozgrywki_id_sezon ON public.rozgrywki(id_sezon);
CREATE INDEX idx_rozgrywki_nr_wzpr ON public.rozgrywki(nr_wzpr);
CREATE INDEX idx_rozgrywki_nazwa_trgm ON public.rozgrywki USING gin (nazwa gin_trgm_ops);

CREATE TABLE public.rundy (
    id                  INTEGER PRIMARY KEY,           -- Id
    id_rozgrywki        INTEGER NOT NULL REFERENCES public.rozgrywki(id),
    nazwa               TEXT
);
CREATE INDEX idx_rundy_id_rozgrywki ON public.rundy(id_rozgrywki);

CREATE TABLE public.kolejki (
    id                  INTEGER PRIMARY KEY,           -- ID_kolejka
    id_runda            INTEGER NOT NULL REFERENCES public.rundy(id),
    nazwa               TEXT,
    nr                  INTEGER,
    lp                  INTEGER,
    data_start          TIMESTAMP,                     -- DataStart
    data_koniec         TIMESTAMP                      -- DataKoniec
);
CREATE INDEX idx_kolejki_id_runda ON public.kolejki(id_runda);
CREATE INDEX idx_kolejki_data_start ON public.kolejki(data_start);


-- ============================================================================
-- 3. DRUŻYNY (tożsamość stała + migawka sezonowa)
-- ============================================================================

-- Tożsamość drużyny (ID_zespol) - może istnieć przez wiele sezonów bez zmiany ID
-- (potwierdzone empirycznie, np. drużyna mężczyzn klubu przez 4 kolejne sezony
-- pod tym samym ID_zespol). Kolumny poniżej to NAJNOWSZA znana migawka
-- (aktualizowana przy każdym uruchomieniu ETL) - pełna historia jest w
-- zespoly_sezony.
CREATE TABLE public.zespoly (
    id                  INTEGER PRIMARY KEY,           -- ID_zespol
    nr_klubu            INTEGER REFERENCES public.kluby(nr_klubu),
    nazwa               TEXT,
    plec                CHAR(1),
    kategoria           TEXT CHECK (kategoria IS NULL OR kategoria = 'Senior'),                          -- "Senior"
    wycofany            BOOLEAN                        -- najnowszy znany stan wycofania
);
CREATE INDEX idx_zespoly_nr_klubu ON public.zespoly(nr_klubu);
CREATE INDEX idx_zespoly_nazwa_trgm ON public.zespoly USING gin (nazwa gin_trgm_ops);

-- Migawka drużyny W KONKRETNYM SEZONIE (adres, kontakt, nazwa i in. mogą się
-- różnić rok do roku nawet przy tym samym ID_zespol). Własne id pozwala
-- zapisać skład również wtedy, gdy API nie dostarczyło sezonowego Id.
CREATE TABLE public.zespoly_sezony (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_api              INTEGER UNIQUE,           -- Id (rekord "zespół w sezonie")
    id_zespol           INTEGER NOT NULL REFERENCES public.zespoly(id),
    id_sezon            INTEGER NOT NULL REFERENCES public.sezony(id),
    nr_klubu            INTEGER REFERENCES public.kluby(nr_klubu),  -- powtórzone z sezonu źródłowego (może różnić się od aktualnego klubu w zespoly, jeśli drużyna zmieniła klub)
    nazwa               TEXT,
    plec                CHAR(1),
    kategoria           TEXT CHECK (kategoria IS NULL OR kategoria = 'Senior'),
    kod_pocztowy        TEXT,
    miasto              TEXT,
    ulica               TEXT,
    email               TEXT,
    www                 TEXT,
    uwagi               TEXT,
    nr_woj              INTEGER,                       -- ZespolNrWoj (numer województwa)
    wycofany            BOOLEAN,                       -- ZespolWycofany w tym sezonie
    UNIQUE (id_zespol, id_sezon)
);
CREATE INDEX idx_zespoly_sezony_id_zespol ON public.zespoly_sezony(id_zespol);
CREATE INDEX idx_zespoly_sezony_id_sezon ON public.zespoly_sezony(id_sezon);

-- Udział drużyny w konkretnych rozgrywkach danego sezonu (drużyna może grać
-- jednocześnie w lidze i pucharze) wraz z przypisaniem do grupy/koloru grupy.
CREATE TABLE public.zespoly_rozgrywki (
    id_zespol           INTEGER NOT NULL REFERENCES public.zespoly(id),
    id_rozgrywki        INTEGER NOT NULL REFERENCES public.rozgrywki(id),
    grupa               TEXT,                          -- ZespolGrupa
    grupa_kolor         TEXT,                           -- ZespolGrupaKolor
    PRIMARY KEY (id_zespol, id_rozgrywki)
);
CREATE INDEX idx_zespoly_rozgrywki_rozgrywki ON public.zespoly_rozgrywki(id_rozgrywki);


-- ============================================================================
-- 4. SKŁADY DRUŻYN W SEZONIE
-- ============================================================================

CREATE TABLE public.sklady (
    id_zespol_sezon     BIGINT NOT NULL REFERENCES public.zespoly_sezony(id),
    id_zawodnik         INTEGER NOT NULL REFERENCES public.zawodnicy(id),
    nr_koszulki         INTEGER,                       -- NrKoszulki
    id_pozycja          SMALLINT REFERENCES public.pozycje(id), -- IdPozycja
    pozycja_nazwa       TEXT,                          -- Pozycja (tekst źródłowy - zachowany też wprost, gdy IdPozycja=0/brak)
    waga                NUMERIC(5,1),                  -- Waga
    wzrost              NUMERIC(5,1),                  -- Wzrost
    foto_url            TEXT,                          -- Foto (migawka z tego sezonu)
    imie                TEXT,                          -- migawka na wypadek zmiany danych w zawodnicy
    nazwisko            TEXT,
    data_urodzenia      DATE,
    PRIMARY KEY (id_zespol_sezon, id_zawodnik)
);
CREATE INDEX idx_sklady_id_zawodnik ON public.sklady(id_zawodnik);


-- ============================================================================
-- 5. HALE, SĘDZIOWIE, SZTAB
-- ============================================================================

CREATE TABLE public.hale (
    id                  SERIAL PRIMARY KEY,
    nazwa               TEXT,                          -- Hala_nazwa
    miasto              TEXT,                          -- Hala_miasto
    ulica               TEXT,                          -- Hala_ulica
    numer               TEXT,                          -- Hala_numer
    pojemnosc           INTEGER,                       -- Hala_pojemnosc
    UNIQUE NULLS NOT DISTINCT (nazwa, miasto, ulica, numer)
);

CREATE TABLE public.sedziowie (
    id                  INTEGER PRIMARY KEY,           -- NrSedzia_*
    nazwisko            TEXT,
    miasto              TEXT
);
CREATE INDEX idx_sedziowie_nazwisko_trgm ON public.sedziowie USING gin (nazwisko gin_trgm_ops);

CREATE TABLE public.osoby_sztabu (
    id                  SERIAL PRIMARY KEY,
    id_api              INTEGER UNIQUE, -- ID osoby z API
    imie                TEXT,
    nazwisko            TEXT
);
CREATE INDEX idx_osoby_sztabu_nazwisko_trgm ON public.osoby_sztabu USING gin (nazwisko gin_trgm_ops);


-- ============================================================================
-- 6. MECZE
-- ============================================================================

CREATE TABLE public.mecze (
    id                          INTEGER PRIMARY KEY,   -- Id / IdZawody
    id_kolejka                  INTEGER NOT NULL REFERENCES public.kolejki(id),
    id_rozgrywki                INTEGER NOT NULL REFERENCES public.rozgrywki(id), -- zdenormalizowane (wynika z kolejka->runda->rozgrywki), zachowane dla wydajności zapytań
    id_sezon                    INTEGER NOT NULL REFERENCES public.sezony(id),    -- zdenormalizowane jw.
    id_zespol_gosp               INTEGER REFERENCES public.zespoly(id),
    id_zespol_gosc               INTEGER REFERENCES public.zespoly(id),
    id_hala                      INTEGER REFERENCES public.hale(id),
    lp                           INTEGER,
    alias_gosp                   INTEGER,
    alias_gosc                   INTEGER,
    -- wynik
    wynik_gosp_pol                SMALLINT,
    wynik_gosp_full               SMALLINT,
    wynik_gosc_pol                SMALLINT,
    wynik_gosc_full               SMALLINT,
    wynik_temp_gosp_pol            SMALLINT,           -- wynik tymczasowy (przed zatwierdzeniem protokołu)
    wynik_temp_gosp_full           SMALLINT,
    wynik_temp_gosc_pol            SMALLINT,
    wynik_temp_gosc_full           SMALLINT,
    wynik_koncowy_gosp             SMALLINT,
    wynik_koncowy_gosc             SMALLINT,
    wynik_bramki_gosp              SMALLINT,
    wynik_bramki_gosc              SMALLINT,
    -- dogrywki i rzuty karne
    dogrywka_1_pol_gosp             SMALLINT,
    dogrywka_1_pol_gosc             SMALLINT,
    dogrywka_1_full_gosp            SMALLINT,
    dogrywka_1_full_gosc            SMALLINT,
    dogrywka_2_pol_gosp             SMALLINT,
    dogrywka_2_pol_gosc             SMALLINT,
    dogrywka_2_full_gosp            SMALLINT,
    dogrywka_2_full_gosc            SMALLINT,
    dogrywka_karne_gosp             SMALLINT,
    dogrywka_karne_gosc             SMALLINT,
    karne_bramki_gosp               SMALLINT,
    karne_bramki_gosc               SMALLINT,
    karne_ile_gosp                  SMALLINT,
    karne_ile_gosc                  SMALLINT,
    -- kary drużynowe i wynik meczu
    kary_gosp                       SMALLINT,           -- KaryGosp
    kary_gosc                       SMALLINT,           -- KaryGosc
    czy_remis                       BOOLEAN,
    zwyciezca                       SMALLINT,           -- kod źródłowy (obserwacja: 1=gosp, 2=gosc)
    -- czasy meczowe (timeouty, 3 na drużynę)
    timeout1_gosp                   TEXT,
    timeout2_gosp                   TEXT,
    timeout3_gosp                   TEXT,
    timeout1_gosc                   TEXT,
    timeout2_gosc                   TEXT,
    timeout3_gosc                   TEXT,
    -- terminy
    data_propozycji                 TIMESTAMP,          -- data_prop
    data_propozycji_dzien           TEXT,               -- data_prop_dzien
    data_faktyczna                  TIMESTAMP,          -- data_fakt (przyjmowana też jako data z terminarz.ZawodyData)
    data_faktyczna_dzien            TEXT,               -- data_fakt_dzien
    data_ostatniej_zmiany           TIMESTAMP,          -- DataOstatnieZmiany (z terminarz.json)
    -- walkower / wycofanie
    zamiana                         BOOLEAN,            -- zamiana gospodarza/gościa
    wycofany                        BOOLEAN,
    wycofany_typ                    TEXT,
    id_zespol_wycofany               INTEGER REFERENCES public.zespoly(id),
    id_zespol_walkower                INTEGER REFERENCES public.zespoly(id),
    -- protokół
    protokol                        TEXT,
    protokol_zatwierdzony            BOOLEAN,           -- protokol_zatwierdz
    protokol_zalacznik_plik          TEXT,
    protokol_zalacznik_typ           TEXT,              -- protokol_zalcznik_plik_typ
    protokol_zalacznik_nazwa         TEXT,
    -- media / frekwencja
    komentarz                       TEXT,
    widzowie                        INTEGER,
    transmisja                      TEXT,
    transmisja_godzina              TEXT,
    bilety_url                      TEXT,
    -- powiązanie par pucharowych (dwumecz)
    po_para_id                      INTEGER,           -- PO_para_ID - wspólny dla obu meczów dwumeczu pucharowego
    po_para_id_gosp                 INTEGER,
    po_para_id_gosc                 INTEGER
);
CREATE INDEX idx_mecze_id_kolejka ON public.mecze(id_kolejka);
CREATE INDEX idx_mecze_id_rozgrywki ON public.mecze(id_rozgrywki);
CREATE INDEX idx_mecze_id_sezon ON public.mecze(id_sezon);
CREATE INDEX idx_mecze_zespol_gosp ON public.mecze(id_zespol_gosp);
CREATE INDEX idx_mecze_zespol_gosc ON public.mecze(id_zespol_gosc);
CREATE INDEX idx_mecze_data_faktyczna ON public.mecze(data_faktyczna);
CREATE INDEX idx_mecze_po_para_id ON public.mecze(po_para_id) WHERE po_para_id IS NOT NULL;
CREATE INDEX idx_mecze_id_hala ON public.mecze(id_hala);
-- Szybkie wyszukanie "wszystkie mecze drużyny X" (dowolna strona):
CREATE INDEX idx_mecze_zespol_dowolna_strona ON public.mecze(id_zespol_gosp, id_zespol_gosc);

CREATE TABLE public.mecze_zalaczniki (
    id                  SERIAL PRIMARY KEY,
    id_mecz             INTEGER NOT NULL REFERENCES public.mecze(id),
    plik                TEXT,                          -- protokol_zalcznik_plik (z tablicy Zalczniki[*])
    nazwa               TEXT,
    typ                 TEXT
);
CREATE INDEX idx_mecze_zalaczniki_mecz ON public.mecze_zalaczniki(id_mecz);

CREATE TABLE public.mecze_sedziowie (
    id_mecz             INTEGER NOT NULL REFERENCES public.mecze(id),
    rola                TEXT NOT NULL CHECK (rola IN ('pierwszy','drugi','delegat','delegat2','sekretarz','czas')),
    id_sedzia           INTEGER NOT NULL REFERENCES public.sedziowie(id),
    PRIMARY KEY (id_mecz, rola)
);
CREATE INDEX idx_mecze_sedziowie_sedzia ON public.mecze_sedziowie(id_sedzia);

CREATE TABLE public.mecze_sztab (
    id                  SERIAL PRIMARY KEY,
    id_mecz             INTEGER NOT NULL REFERENCES public.mecze(id),
    strona              CHAR(4) NOT NULL CHECK (strona IN ('gosp','gosc')),
    id_osoba            INTEGER NOT NULL REFERENCES public.osoby_sztabu(id),
    funkcja             TEXT,
    rola                TEXT
);
CREATE INDEX idx_mecze_sztab_mecz ON public.mecze_sztab(id_mecz);
CREATE INDEX idx_mecze_sztab_osoba ON public.mecze_sztab(id_osoba);

-- Skład meczowy + statystyki zawodnika w konkretnym meczu.
-- Klucz zawodnika pochodzi z klucza obiektu JSON w mecze/<id>.json (gosp/gosc),
-- zweryfikowany jako ten sam identyfikator co NrZawodnika.
CREATE TABLE public.mecze_zawodnicy (
    id_mecz             INTEGER NOT NULL REFERENCES public.mecze(id),
    id_zawodnik         INTEGER NOT NULL REFERENCES public.zawodnicy(id),
    strona              CHAR(4) NOT NULL CHECK (strona IN ('gosp','gosc','inne')), -- 'inne' wystąpiło w 1/20 sezonów - prawdopodobnie anomalia API, zachowane bez utraty danych
    nr_koszulki         INTEGER,
    pozycja             TEXT,
    bramki              SMALLINT,
    dwie_minuty         SMALLINT,                      -- "2minuty"
    upomnienie          BOOLEAN,
    dyskwalifikacja     BOOLEAN,
    kd                  SMALLINT,
    wyjscie             BOOLEAN,                       -- czy wystąpił w meczu (starting/used)
    karne_liczba        SMALLINT,
    karne_bramki        SMALLINT,
    karne_liczba_seria  SMALLINT,
    karne_bramki_seria  SMALLINT,
    badania_zprp        TEXT,
    badania_wzpr        TEXT,
    foto_url            TEXT,
    data_urodzenia      DATE,                          -- migawka (dataUr) z tego meczu
    PRIMARY KEY (id_mecz, strona, id_zawodnik)
);
CREATE INDEX idx_mecze_zawodnicy_zawodnik ON public.mecze_zawodnicy(id_zawodnik);


-- ============================================================================
-- 7. TABELE (klasyfikacje) I KLASYFIKACJA STRZELCÓW
-- ============================================================================

CREATE TABLE public.tabele (
    id                  SERIAL PRIMARY KEY,
    id_rozgrywki        INTEGER NOT NULL REFERENCES public.rozgrywki(id),
    tabela_id           INTEGER NOT NULL,              -- tabela_id (id widoku tabeli w API)
    tabela_nazwa        TEXT,
    UNIQUE (id_rozgrywki, tabela_id)
);
CREATE INDEX idx_tabele_id_rozgrywki ON public.tabele(id_rozgrywki);

CREATE TABLE public.tabele_grupy (
    id                  SERIAL PRIMARY KEY,
    id_tabela           INTEGER NOT NULL REFERENCES public.tabele(id),
    grupa_id            INTEGER NOT NULL,              -- tabela_Id2
    grupa_nazwa         TEXT,                          -- tabela_nazwa2
    UNIQUE (id_tabela, grupa_id)
);

CREATE TABLE public.tabele_wiersze (
    id                  SERIAL PRIMARY KEY,
    id_tabela_grupa     INTEGER NOT NULL REFERENCES public.tabele_grupy(id),
    id_zespol           INTEGER NOT NULL REFERENCES public.zespoly(id),
    mecze               SMALLINT,
    zwyciestwa          SMALLINT,
    remisy              SMALLINT,
    przegrane           SMALLINT,
    remis_wygrane       SMALLINT,                      -- RemisWygrane
    remis_przegrane     SMALLINT,                      -- RemisPrzegrane
    bramki_zdobyte      SMALLINT,
    bramki_stracone     SMALLINT,
    bramki_zdobyte_ex   SMALLINT,                      -- BramkiZdobyteEx
    bramki_ex           SMALLINT,                      -- BramkiEx (odrębne pole źródłowe od BramkiZdobyteEx)
    bramki_zdobyte_wyjazd SMALLINT,                    -- BramkiZdobyteWyjazd
    punkty_zdobyte      SMALLINT,
    punkty_stracone     SMALLINT,
    punkty_ex           SMALLINT,
    punkty_bonusowe     SMALLINT,                      -- PunktyBonusowe
    kryteria            TEXT,
    zd_st               TEXT,                          -- Zd_St (bilans bramkowy w formie tekstowej)
    grupa               TEXT,
    grupa_kolor         TEXT
);
CREATE INDEX idx_tabele_wiersze_grupa ON public.tabele_wiersze(id_tabela_grupa);
CREATE INDEX idx_tabele_wiersze_zespol ON public.tabele_wiersze(id_zespol);

CREATE TABLE public.strzelcy (
    id                  SERIAL PRIMARY KEY,
    id_rozgrywki        INTEGER NOT NULL REFERENCES public.rozgrywki(id),
    id_zawodnik         INTEGER NOT NULL REFERENCES public.zawodnicy(id),
    id_zespol           INTEGER REFERENCES public.zespoly(id),
    mecze               SMALLINT,
    bramki              SMALLINT,
    srednia             NUMERIC(5,2),                  -- Srednia (bramek/mecz)
    dwie_minuty         SMALLINT,
    upomnienie          SMALLINT,
    dyskwalifikacja     SMALLINT,
    kd                  SMALLINT,
    karne_liczba        SMALLINT,
    karne_bramki        SMALLINT,
    karne_liczba_seria  SMALLINT,
    karne_bramki_seria  SMALLINT,
    karne_skutecznosc   NUMERIC(5,2),
    karne_seria_skutecznosc NUMERIC(5,2),
    UNIQUE (id_rozgrywki, id_zawodnik)
);
CREATE INDEX idx_strzelcy_zawodnik ON public.strzelcy(id_zawodnik);
CREATE INDEX idx_strzelcy_zespol ON public.strzelcy(id_zespol);



-- 8. ŹRÓDŁA I DZIENNIKI. Pliki są niezmiennymi wersjami, nie logami do rotacji.
CREATE TABLE public.pliki_zrodlowe (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sciezka TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    rozmiar BIGINT NOT NULL CHECK (rozmiar >= 0),
    rodzaj TEXT NOT NULL,
    id_sezon INTEGER REFERENCES public.sezony(id),
    id_rozgrywki INTEGER REFERENCES public.rozgrywki(id),
    zarejestrowano TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    kodowanie TEXT NOT NULL DEFAULT 'UTF-8',
    tresc BYTEA NOT NULL, -- dokładne bajty, także gdy źródło ma błędny JSON
    dokument JSONB, -- NULL przy błędzie parsowania; JSON null jest odrębną wartością
    blad_parsowania TEXT,
    CHECK (rozmiar = octet_length(tresc)),
    CHECK (sha256 = encode(sha256(tresc), 'hex')),
    UNIQUE (sciezka, sha256)
);
CREATE INDEX pliki_kontekst_idx ON public.pliki_zrodlowe(id_sezon, id_rozgrywki);

CREATE TABLE logs.import_przebiegi (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rozpoczecie TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    zakonczenie TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'URUCHOMIONY'
        CHECK (status IN ('URUCHOMIONY','SUKCES','CZESCIOWY','BLAD','PRZERWANY')),
    wersja_importera TEXT NOT NULL,
    wykonawca TEXT NOT NULL,
    parametry JSONB NOT NULL DEFAULT '{}',
    podsumowanie JSONB NOT NULL DEFAULT '{}',
    CHECK (zakonczenie IS NULL OR zakonczenie >= rozpoczecie)
);
CREATE TABLE logs.pobrania (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_przebieg BIGINT REFERENCES logs.import_przebiegi(id),
    id_pliku BIGINT REFERENCES public.pliki_zrodlowe(id),
    url TEXT NOT NULL,
    parametry JSONB NOT NULL DEFAULT '{}',
    rozpoczecie TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    zakonczenie TIMESTAMPTZ,
    http_status INTEGER CHECK (http_status BETWEEN 100 AND 599),
    status TEXT NOT NULL DEFAULT 'OCZEKUJE'
        CHECK (status IN ('OCZEKUJE','W_TRAKCIE','SUKCES','PUSTA_ODPOWIEDZ','BLAD')),
    czas_ms BIGINT CHECK (czas_ms >= 0),
    blad TEXT
);
CREATE TABLE logs.import_pliki (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_przebieg BIGINT NOT NULL REFERENCES logs.import_przebiegi(id),
    id_pliku BIGINT NOT NULL REFERENCES public.pliki_zrodlowe(id),
    rozpoczecie TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    zakonczenie TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'OCZEKUJE'
        CHECK (status IN ('OCZEKUJE','W_TRAKCIE','SUKCES','CZESCIOWY','BLAD','POMINIETY','PRZERWANY')),
    dodano BIGINT NOT NULL DEFAULT 0 CHECK (dodano >= 0),
    zmieniono BIGINT NOT NULL DEFAULT 0 CHECK (zmieniono >= 0),
    odrzucono BIGINT NOT NULL DEFAULT 0 CHECK (odrzucono >= 0),
    bez_zmian BIGINT NOT NULL DEFAULT 0 CHECK (bez_zmian >= 0),
    komunikat TEXT,
    UNIQUE (id, id_przebieg)
);
-- Każde ponowienie to nowy wpis; nie ograniczamy liczby prób importu pliku.
CREATE INDEX import_pliki_wersja_idx ON logs.import_pliki(id_pliku, id DESC);
CREATE INDEX import_pliki_przebieg_idx ON logs.import_pliki(id_przebieg, status);
CREATE INDEX pobrania_przebieg_idx ON logs.pobrania(id_przebieg, rozpoczecie);
CREATE TABLE logs.import_bledy (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    czas TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    id_przebieg BIGINT REFERENCES logs.import_przebiegi(id),
    id_import_pliku BIGINT REFERENCES logs.import_pliki(id),
    id_pliku BIGINT REFERENCES public.pliki_zrodlowe(id),
    zrodlo TEXT NOT NULL,
    kod TEXT NOT NULL,
    url TEXT,
    plik TEXT,
    wskaznik_json TEXT,
    blad TEXT NOT NULL,
    szczegoly JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX import_bledy_przebieg_idx ON logs.import_bledy(id_przebieg, czas);
CREATE TABLE logs.zdarzenia (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    czas TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    poziom TEXT NOT NULL CHECK (poziom IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
    komponent TEXT NOT NULL,
    operacja TEXT,
    komunikat TEXT NOT NULL,
    szczegoly JSONB NOT NULL DEFAULT '{}',
    wyjatek TEXT,
    id_przebieg BIGINT REFERENCES logs.import_przebiegi(id),
    id_import_pliku BIGINT REFERENCES logs.import_pliki(id),
    id_pobranie BIGINT REFERENCES logs.pobrania(id)
);
CREATE INDEX zdarzenia_przebieg_idx ON logs.zdarzenia(id_przebieg, czas);
CREATE INDEX zdarzenia_czas_idx ON logs.zdarzenia(czas);

-- Polimorficzne powiązania celowo bez FK do rekordu docelowego: ślad pozostaje
-- po DELETE i może opisywać rekord, który odrzucono podczas normalizacji.
CREATE TABLE public.rekordy_zrodla (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tabela TEXT NOT NULL,
    klucz_rekordu JSONB NOT NULL CHECK (jsonb_typeof(klucz_rekordu) = 'object'),
    id_pliku BIGINT NOT NULL REFERENCES public.pliki_zrodlowe(id),
    wskaznik_json TEXT NOT NULL, -- JSON Pointer, pusty tekst oznacza korzeń
    zarejestrowano TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (tabela, klucz_rekordu, id_pliku, wskaznik_json)
);
CREATE INDEX rekordy_zrodla_plik_idx ON public.rekordy_zrodla(id_pliku);

-- 9. POPRAWKI MODELU I INTEGRALNOŚĆ HIERARCHII (również przy UPDATE rodziców).
ALTER TABLE public.rozgrywki ADD UNIQUE (id, id_sezon);
ALTER TABLE public.rundy ADD UNIQUE (id, id_rozgrywki);
ALTER TABLE public.kolejki ADD COLUMN id_rozgrywki INTEGER NOT NULL;
ALTER TABLE public.kolejki ADD UNIQUE (id, id_rozgrywki);
ALTER TABLE public.kolejki ADD FOREIGN KEY (id_runda, id_rozgrywki)
    REFERENCES public.rundy(id, id_rozgrywki) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.zespoly_rozgrywki ADD COLUMN id_sezon INTEGER NOT NULL;
ALTER TABLE public.zespoly_rozgrywki ADD FOREIGN KEY (id_rozgrywki, id_sezon)
    REFERENCES public.rozgrywki(id, id_sezon) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.zespoly_rozgrywki ADD FOREIGN KEY (id_zespol, id_sezon)
    REFERENCES public.zespoly_sezony(id_zespol, id_sezon) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.mecze ADD COLUMN rozgrywki_code TEXT;
ALTER TABLE public.mecze ADD FOREIGN KEY (id_kolejka, id_rozgrywki)
    REFERENCES public.kolejki(id, id_rozgrywki) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.mecze ADD FOREIGN KEY (id_rozgrywki, id_sezon)
    REFERENCES public.rozgrywki(id, id_sezon) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.mecze ADD FOREIGN KEY (id_zespol_gosp, id_rozgrywki)
    REFERENCES public.zespoly_rozgrywki(id_zespol, id_rozgrywki) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.mecze ADD FOREIGN KEY (id_zespol_gosc, id_rozgrywki)
    REFERENCES public.zespoly_rozgrywki(id_zespol, id_rozgrywki) DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE public.mecze_zawodnicy ADD COLUMN imie TEXT;
ALTER TABLE public.mecze_zawodnicy ADD COLUMN nazwisko TEXT;
ALTER TABLE public.mecze_sedziowie ADD COLUMN nazwisko TEXT;
ALTER TABLE public.mecze_sedziowie ADD COLUMN miasto TEXT;
ALTER TABLE public.mecze_sztab ADD COLUMN licencja TEXT; -- migawka z tego meczu
ALTER TABLE public.mecze_sztab ADD COLUMN imie TEXT;
ALTER TABLE public.mecze_sztab ADD COLUMN nazwisko TEXT;
ALTER TABLE public.mecze_sztab ADD UNIQUE NULLS NOT DISTINCT (id_mecz, strona, id_osoba, rola);
ALTER TABLE public.mecze_zalaczniki ADD UNIQUE NULLS NOT DISTINCT (id_mecz, plik, nazwa, typ);
-- Dla rekordów bez stabilnego ID importer nadaje powtarzalny klucz w obrębie
-- źródła (np. nazwa/rodzaj + numer wystąpienia), NIE losowy UUID na każde pobranie.
ALTER TABLE public.licencje_klubowe ADD COLUMN klucz_zrodlowy TEXT NOT NULL;
ALTER TABLE public.licencje_klubowe ADD COLUMN sezon_nazwa TEXT;
ALTER TABLE public.licencje_klubowe ADD UNIQUE (nr_klubu, klucz_zrodlowy);
ALTER TABLE public.tabele_wiersze ADD COLUMN miejsce INTEGER;
ALTER TABLE public.tabele_wiersze ADD COLUMN kolejnosc_zrodlowa INTEGER NOT NULL CHECK (kolejnosc_zrodlowa > 0);
ALTER TABLE public.tabele_wiersze ADD COLUMN id_pliku BIGINT REFERENCES public.pliki_zrodlowe(id);
ALTER TABLE public.tabele_wiersze ADD UNIQUE (id_tabela_grupa, id_zespol);
ALTER TABLE public.strzelcy ADD COLUMN miejsce INTEGER;
ALTER TABLE public.strzelcy ADD COLUMN kolejnosc_zrodlowa INTEGER NOT NULL CHECK (kolejnosc_zrodlowa > 0);
ALTER TABLE public.strzelcy ADD COLUMN id_pliku BIGINT REFERENCES public.pliki_zrodlowe(id);
-- Aktualna projekcja klasyfikacji w tabelach powyżej; wcześniejsze zestawienia
-- w niezmiennych plikach źródłowych oraz w automatycznych *_log.

CREATE TABLE public.sklady_wersje (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_zespol_sezon BIGINT NOT NULL REFERENCES public.zespoly_sezony(id),
    id_pliku BIGINT NOT NULL REFERENCES public.pliki_zrodlowe(id),
    wskaznik_json TEXT NOT NULL DEFAULT '',
    utworzono TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (id_zespol_sezon, id_pliku, wskaznik_json),
    UNIQUE (id, id_zespol_sezon)
);
CREATE TABLE public.sklady_wersje_zawodnicy (
    id_wersja BIGINT NOT NULL REFERENCES public.sklady_wersje(id),
    kolejnosc_zrodlowa INTEGER NOT NULL CHECK (kolejnosc_zrodlowa > 0),
    id_zawodnik INTEGER REFERENCES public.zawodnicy(id),
    dane JSONB NOT NULL, -- zachowuje również duplikaty i błędne wartości źródła
    PRIMARY KEY (id_wersja, kolejnosc_zrodlowa)
);
ALTER TABLE public.zespoly_sezony ADD COLUMN id_wersja_skladu BIGINT;
ALTER TABLE public.zespoly_sezony ADD FOREIGN KEY (id_wersja_skladu, id)
    REFERENCES public.sklady_wersje(id, id_zespol_sezon) DEFERRABLE INITIALLY IMMEDIATE;
-- public.sklady jest uzgodnioną projekcją wybranej wersji, nie archiwum wariantów.

-- 10. ANOMALIE: bez twardych FK do obiektów sportowych, bo ich brak też jest błędem.
CREATE TABLE logs.anomalie_danych (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    klucz_deduplikacji TEXT NOT NULL UNIQUE,
    id_sezon INTEGER,
    id_rozgrywki INTEGER,
    id_mecz INTEGER,
    id_zespol INTEGER,
    id_zawodnik INTEGER,
    tabela TEXT,
    klucz_rekordu JSONB,
    kod TEXT NOT NULL,
    opis TEXT NOT NULL,
    szczegoly JSONB NOT NULL DEFAULT '{}',
    poziom TEXT NOT NULL CHECK (poziom IN ('INFO','OSTRZEZENIE','BLAD')),
    id_pliku BIGINT REFERENCES public.pliki_zrodlowe(id),
    id_przebieg BIGINT REFERENCES logs.import_przebiegi(id),
    pierwsze_wykrycie TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    ostatnie_wykrycie TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    licznik BIGINT NOT NULL DEFAULT 1 CHECK (licznik > 0),
    status TEXT NOT NULL DEFAULT 'OTWARTA'
        CHECK (status IN ('OTWARTA','W_ANALIZIE','ZAAKCEPTOWANA','ROZWIAZANA')),
    komentarz TEXT,
    rozstrzygnal TEXT,
    czas_rozwiazania TIMESTAMPTZ
);
CREATE INDEX anomalie_filtr_idx ON logs.anomalie_danych(status, id_sezon, id_rozgrywki);
CREATE INDEX anomalie_mecz_idx ON logs.anomalie_danych(id_mecz);
CREATE VIEW logs.anomalie_przeglad AS
SELECT a.*, s.nazwa AS sezon_nazwa, r.nazwa AS rozgrywki_nazwa
FROM logs.anomalie_danych a
LEFT JOIN public.sezony s ON s.id = a.id_sezon
LEFT JOIN public.rozgrywki r ON r.id = a.id_rozgrywki;

-- Jedno wywołanie na problem podczas danej kontroli, po wykryciu przez importer.
CREATE FUNCTION logs.zglos_anomalie(p_klucz TEXT, p_kod TEXT, p_opis TEXT,
    p_kontekst JSONB DEFAULT '{}', p_szczegoly JSONB DEFAULT '{}',
    p_poziom TEXT DEFAULT 'OSTRZEZENIE') RETURNS BIGINT
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE wynik BIGINT;
BEGIN
    INSERT INTO logs.anomalie_danych AS a
        (klucz_deduplikacji,kod,opis,szczegoly,poziom,id_sezon,id_rozgrywki,
         id_mecz,id_zespol,id_zawodnik,tabela,klucz_rekordu,id_pliku,id_przebieg)
    VALUES (p_klucz,p_kod,p_opis,p_szczegoly,p_poziom,
        (p_kontekst->>'id_sezon')::INTEGER,(p_kontekst->>'id_rozgrywki')::INTEGER,
        (p_kontekst->>'id_mecz')::INTEGER,(p_kontekst->>'id_zespol')::INTEGER,
        (p_kontekst->>'id_zawodnik')::INTEGER,p_kontekst->>'tabela',p_kontekst->'klucz_rekordu',
        (p_kontekst->>'id_pliku')::BIGINT,(p_kontekst->>'id_przebieg')::BIGINT)
    ON CONFLICT (klucz_deduplikacji) DO UPDATE SET
        ostatnie_wykrycie = clock_timestamp(), licznik = a.licznik + 1,
        opis = EXCLUDED.opis, szczegoly = EXCLUDED.szczegoly, poziom = EXCLUDED.poziom,
        id_pliku = COALESCE(EXCLUDED.id_pliku,a.id_pliku),
        id_przebieg = COALESCE(EXCLUDED.id_przebieg,a.id_przebieg),
        id_sezon = COALESCE(EXCLUDED.id_sezon,a.id_sezon),
        id_rozgrywki = COALESCE(EXCLUDED.id_rozgrywki,a.id_rozgrywki),
        id_mecz = COALESCE(EXCLUDED.id_mecz,a.id_mecz),
        id_zespol = COALESCE(EXCLUDED.id_zespol,a.id_zespol),
        id_zawodnik = COALESCE(EXCLUDED.id_zawodnik,a.id_zawodnik),
        tabela = COALESCE(EXCLUDED.tabela,a.tabela),
        klucz_rekordu = COALESCE(EXCLUDED.klucz_rekordu,a.klucz_rekordu),
        status = CASE WHEN a.status = 'ROZWIAZANA' THEN 'OTWARTA' ELSE a.status END,
        czas_rozwiazania = CASE WHEN a.status = 'ROZWIAZANA' THEN NULL ELSE a.czas_rozwiazania END,
        rozstrzygnal = CASE WHEN a.status = 'ROZWIAZANA' THEN NULL ELSE a.rozstrzygnal END
    RETURNING id INTO wynik;
    RETURN wynik;
END $$;

-- 11. AUDYT WIERSZOWY: fizyczna kopia kolumn każdej tabeli, bez FK/UNIQUE źródła.
CREATE FUNCTION logs.blokuj_zmiane_archiwum() RETURNS TRIGGER
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    RAISE EXCEPTION 'Archiwum %.% jest niezmienne; operacja % niedozwolona',
        TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP;
END $$;

CREATE FUNCTION logs.ustaw_kontekst(p_wykonawca TEXT, p_przebieg BIGINT DEFAULT NULL,
    p_import_pliku BIGINT DEFAULT NULL, p_powod TEXT DEFAULT NULL) RETURNS VOID
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    IF p_import_pliku IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM logs.import_pliki WHERE id = p_import_pliku AND id_przebieg = p_przebieg
    ) THEN RAISE EXCEPTION 'Niezgodny kontekst przebiegu i pliku'; END IF;
    PERFORM set_config('zprp.wykonawca', COALESCE(p_wykonawca,''), true);
    PERFORM set_config('zprp.id_przebieg', COALESCE(p_przebieg::TEXT,''), true);
    PERFORM set_config('zprp.id_import_pliku', COALESCE(p_import_pliku::TEXT,''), true);
    PERFORM set_config('zprp.powod', COALESCE(p_powod,''), true);
END $$;

CREATE FUNCTION logs.audyt_wiersza() RETURNS TRIGGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE
    obraz JSONB;
    klucz JSONB;
    kolumny TEXT;
    przebieg BIGINT := NULLIF(current_setting('zprp.id_przebieg', true),'')::BIGINT;
    import_pliku BIGINT := NULLIF(current_setting('zprp.id_import_pliku', true),'')::BIGINT;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW IS NOT DISTINCT FROM OLD THEN RETURN NULL; END IF;
    IF TG_OP = 'DELETE' THEN obraz := to_jsonb(OLD); ELSE obraz := to_jsonb(NEW); END IF;
    IF import_pliku IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM logs.import_pliki WHERE id = import_pliku AND id_przebieg = przebieg
    ) THEN RAISE EXCEPTION 'Niezgodny kontekst audytu'; END IF;
    IF przebieg IS NOT NULL AND NOT EXISTS (SELECT 1 FROM logs.import_przebiegi WHERE id=przebieg)
        THEN RAISE EXCEPTION 'Nieznany przebieg importu'; END IF;
    SELECT string_agg(quote_ident(a.attname), ', ' ORDER BY a.attnum)
      INTO kolumny FROM pg_attribute a
      WHERE a.attrelid = TG_RELID AND a.attnum > 0 AND NOT a.attisdropped;
    SELECT jsonb_object_agg(a.attname, obraz->a.attname) INTO klucz
      FROM pg_index i JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey)
      WHERE i.indrelid=TG_RELID AND i.indisprimary;
    EXECUTE format('INSERT INTO logs.%I (%s, log_operacja, log_czas, log_uzytkownik_bazy,
        log_wykonawca, log_id_przebieg, log_id_import_pliku, log_transakcja, log_powod, log_klucz)
        SELECT (jsonb_populate_record(NULL::%I.%I, $1)).*, $2,$3,$4,$5,$6,$7,$8,$9,$10',
        TG_TABLE_NAME || '_log',kolumny,TG_TABLE_SCHEMA,TG_TABLE_NAME)
    USING obraz, TG_OP, clock_timestamp(), session_user::TEXT,
        NULLIF(current_setting('zprp.wykonawca',true),''), przebieg, import_pliku,
        txid_current(), NULLIF(current_setting('zprp.powod',true),''), klucz;
    RETURN NULL;
END $$;

-- Funkcja instalacyjna tylko dla właściciela, nie dla aplikacji. CTAS kopiuje typy,
-- ale nie domyślne wartości, klucze, identity i NOT NULL tabeli źródłowej.
CREATE FUNCTION logs.utworz_audyt(p_tabela REGCLASS) RETURNS VOID
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE schemat TEXT; tabela TEXT; historia TEXT;
BEGIN
    SELECT n.nspname,c.relname INTO schemat,tabela FROM pg_class c
      JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.oid=p_tabela;
    IF schemat <> 'public' AND NOT (schemat='logs' AND tabela='anomalie_danych') THEN
        RAISE EXCEPTION 'Niedozwolona tabela audytu'; END IF;
    historia := tabela || '_log';
    EXECUTE format('CREATE TABLE logs.%I AS SELECT * FROM %s WITH NO DATA',historia,p_tabela);
    EXECUTE format('ALTER TABLE logs.%I
        ADD COLUMN log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        ADD COLUMN log_operacja TEXT NOT NULL CHECK (log_operacja IN (''INSERT'',''UPDATE'',''DELETE'',''BASELINE'')),
        ADD COLUMN log_czas TIMESTAMPTZ NOT NULL,
        ADD COLUMN log_uzytkownik_bazy TEXT NOT NULL,
        ADD COLUMN log_wykonawca TEXT,
        ADD COLUMN log_id_przebieg BIGINT,
        ADD COLUMN log_id_import_pliku BIGINT,
        ADD COLUMN log_transakcja BIGINT NOT NULL,
        ADD COLUMN log_powod TEXT,
        ADD COLUMN log_klucz JSONB NOT NULL',historia);
    EXECUTE format('CREATE INDEX ON logs.%I (log_klucz, log_id)',historia);
    EXECUTE format('CREATE INDEX ON logs.%I (log_id_przebieg, log_czas)',historia);
    EXECUTE format('CREATE INDEX ON logs.%I (log_id_import_pliku)',historia);
    EXECUTE format('CREATE TRIGGER audyt_zmian AFTER INSERT OR UPDATE OR DELETE ON %s
        FOR EACH ROW EXECUTE FUNCTION logs.audyt_wiersza()',p_tabela);
    EXECUTE format('ALTER TABLE %s ENABLE ALWAYS TRIGGER audyt_zmian',p_tabela);
    EXECUTE format('CREATE TRIGGER blokada_truncate BEFORE TRUNCATE ON %s
        FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()',p_tabela);
    EXECUTE format('CREATE TRIGGER blokada_historii BEFORE UPDATE OR DELETE OR TRUNCATE ON logs.%I
        FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum()',historia);
END $$;

DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'sezony','zwiazki_wojewodzkie','kluby','kluby_zespoly_historia','licencje_klubowe',
        'pozycje','zawodnicy','rozgrywki','rundy','kolejki','zespoly','zespoly_sezony',
        'zespoly_rozgrywki','sklady','hale','sedziowie','osoby_sztabu','mecze',
        'mecze_zalaczniki','mecze_sedziowie','mecze_sztab','mecze_zawodnicy',
        'tabele','tabele_grupy','tabele_wiersze','strzelcy','sklady_wersje','sklady_wersje_zawodnicy'
    ] LOOP
        PERFORM logs.utworz_audyt(format('public.%I',t)::REGCLASS);
    END LOOP;
    PERFORM logs.utworz_audyt('logs.anomalie_danych'::REGCLASS);
END $$;

CREATE TRIGGER pliki_niezmienne BEFORE UPDATE OR DELETE OR TRUNCATE ON public.pliki_zrodlowe
    FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum();
CREATE TRIGGER pochodzenie_niezmienne BEFORE UPDATE OR DELETE OR TRUNCATE ON public.rekordy_zrodla
    FOR EACH STATEMENT EXECUTE FUNCTION logs.blokuj_zmiane_archiwum();

CREATE VIEW logs.pliki_przeglad AS
SELECT p.id, p.sciezka, p.sha256, p.rodzaj, p.id_sezon, p.id_rozgrywki,
    p.zarejestrowano, i.id AS id_ostatniej_proby, COALESCE(i.status,'NIE_IMPORTOWANO') AS status,
    i.id_przebieg, i.zakonczenie, i.dodano, i.zmieniono, i.odrzucono
FROM public.pliki_zrodlowe p
LEFT JOIN LATERAL (SELECT * FROM logs.import_pliki f WHERE f.id_pliku=p.id ORDER BY f.id DESC LIMIT 1) i ON true;

-- Przy przyszłym wdrażaniu audytu do wypełnionej bazy wywołać raz, w migracji,
-- po utworzeniu tabeli historii. Blokada nie dopuszcza równoległych zmian danych.
CREATE FUNCTION logs.zapisz_stan_poczatkowy(p_tabela REGCLASS) RETURNS BIGINT
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE sch TEXT; tab TEXT; kol TEXT; pk_expr TEXT; liczba BIGINT; istnieje BOOLEAN;
BEGIN
    SELECT n.nspname,c.relname INTO sch,tab FROM pg_class c
        JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.oid=p_tabela;
    IF sch <> 'public' AND NOT (sch='logs' AND tab='anomalie_danych') THEN
        RAISE EXCEPTION 'Niedozwolona tabela'; END IF;
    EXECUTE format('LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE',p_tabela);
    EXECUTE format('SELECT EXISTS (SELECT 1 FROM logs.%I)',tab||'_log') INTO istnieje;
    IF istnieje THEN RAISE EXCEPTION 'Historia % nie jest pusta',tab; END IF;
    SELECT string_agg(quote_ident(attname), ', ' ORDER BY attnum) INTO kol
        FROM pg_attribute WHERE attrelid=p_tabela AND attnum>0 AND NOT attisdropped;
    SELECT string_agg(format('%L, to_jsonb(s)->%L',a.attname,a.attname),', ' ORDER BY a.attnum)
        INTO pk_expr FROM pg_index i JOIN pg_attribute a
        ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey)
        WHERE i.indrelid=p_tabela AND i.indisprimary;
    EXECUTE format('INSERT INTO logs.%I (%s,log_operacja,log_czas,log_uzytkownik_bazy,
        log_wykonawca,log_transakcja,log_powod,log_klucz)
        SELECT s.*, ''BASELINE'',clock_timestamp(),session_user,$1,txid_current(),
        ''Stan poczatkowy audytu'',jsonb_build_object(%s) FROM %s s',tab||'_log',kol,pk_expr,p_tabela)
        USING NULLIF(current_setting('zprp.wykonawca',true),'');
    GET DIAGNOSTICS liczba = ROW_COUNT;
    RETURN liczba;
END $$;

-- Wywołać po zakończeniu importu całej partii, nie po każdym wierszu składu.
-- Dalsze reguły dotyczące duplikatów surowego JSON i licencji realizuje importer,
-- bo normalizacja może już usunąć identyczne powtórzenia.
CREATE FUNCTION logs.sprawdz_anomalie_meczow(p_sezon INTEGER DEFAULT NULL,
    p_przebieg BIGINT DEFAULT NULL) RETURNS BIGINT
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE r RECORD; kontekst JSONB; n BIGINT := 0;
BEGIN
    FOR r IN SELECT m.*, count(DISTINCT z.strona) FILTER (WHERE z.strona IN ('gosp','gosc')) AS strony
        FROM public.mecze m LEFT JOIN public.mecze_zawodnicy z ON z.id_mecz=m.id
        WHERE p_sezon IS NULL OR m.id_sezon=p_sezon GROUP BY m.id
    LOOP
        kontekst := jsonb_build_object('id_sezon',r.id_sezon,'id_rozgrywki',r.id_rozgrywki,
            'id_mecz',r.id,'id_przebieg',p_przebieg,'tabela','public.mecze',
            'klucz_rekordu',jsonb_build_object('id',r.id));
        IF r.id_zespol_gosp IS NULL OR r.id_zespol_gosc IS NULL THEN
            PERFORM logs.zglos_anomalie('mecz:'||r.id||':uczestnicy','NIEUSTALONA_DRUZYNA',
                'Nieustalony gospodarz lub gosc',kontekst,'{}','INFO'); n := n+1;
        END IF;
        IF r.wynik_gosp_full IS NOT NULL AND r.wynik_gosc_full IS NOT NULL AND r.strony<2 THEN
            PERFORM logs.zglos_anomalie('mecz:'||r.id||':sklady','BRAK_SKLADU',
                'Mecz z wynikiem bez skladu przynajmniej jednej strony',kontekst,
                jsonb_build_object('id_zespol_walkower',r.id_zespol_walkower),
                CASE WHEN r.id_zespol_walkower IS NOT NULL THEN 'INFO' ELSE 'OSTRZEZENIE' END);
            n := n+1;
        END IF;
    END LOOP;
    FOR r IN SELECT z.id_mecz,z.id_zawodnik,m.id_sezon,m.id_rozgrywki,
            jsonb_agg(to_jsonb(z) ORDER BY z.strona) AS wpisy
        FROM public.mecze_zawodnicy z JOIN public.mecze m ON m.id=z.id_mecz
        WHERE p_sezon IS NULL OR m.id_sezon=p_sezon
        GROUP BY z.id_mecz,z.id_zawodnik,m.id_sezon,m.id_rozgrywki HAVING count(*)>1
    LOOP
        PERFORM logs.zglos_anomalie('mecz:'||r.id_mecz||':zawodnik:'||r.id_zawodnik,
            'ZAWODNIK_PO_KILKU_STRONACH','Zawodnik wystepuje po kilku stronach meczu',
            jsonb_build_object('id_mecz',r.id_mecz,'id_zawodnik',r.id_zawodnik,
                'id_sezon',r.id_sezon,'id_rozgrywki',r.id_rozgrywki,'id_przebieg',p_przebieg),
            jsonb_build_object('wpisy',r.wpisy)); n := n+1;
    END LOOP;
    RETURN n;
END $$;

REVOKE ALL ON ALL TABLES IN SCHEMA logs FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA logs FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA logs FROM PUBLIC;
-- Uprawnienia ról aplikacyjnych nadaje administrator wg README_import_audyt.md.
-- Konto aplikacji NIE jest właścicielem tabel i nie może wyłączać triggerów.
COMMIT;
