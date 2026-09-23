# Aktualizacja i import danych ZPRP

Opis aktualnego kodu na dzień 2026-09-23. Dokument dotyczy importera w pakiecie `handball`, dostępnego pod `/administracja/import`. Starszy importer z katalogu nadrzędnego działa osobno.

Tryby pełny i uzupełniający pobierają dane wybranych seniorskich rozgrywek sezonu **2026/2027 (ID 195)**; tryb „Tylko tabele” — tabele wybranych rozgrywek dowolnego sezonu z bazy (opis niżej). Importer przygotowuje różnice względem bazy i pokazuje je administratorowi. **Dane w PostgreSQL zapisuje dopiero po zatwierdzeniu podglądu.** Podczas pobierania zapisuje już lokalne pliki i stan roboczy w SQLite.

## Tryb pełny i uzupełniający

Na stronie są dwa osobne przyciski korzystające ze wspólnego wyboru lig:

| Tryb | Zakres |
| --- | --- |
| Pełny import | Pobiera strukturę rozgrywek i wszystkie dostępne mecze; sprawdza też korekty istniejących wartości |
| Uzupełnij brakujące dane meczów | Wybiera znane mecze z bazy i pobiera wyłącznie ich szczegóły; uzupełnia `NULL` i dodaje nowe rekordy |

`ImportSQLAlchemyRepository.pobierz_brakujace()` wybiera sezon 195 i zaznaczone ligi. Mecz musi mieć `data_faktyczna` wcześniejszą niż początek dzisiejszego dnia w Europe/Warsaw oraz brak przynajmniej jednej wartości `wynik_gosp_full` / `wynik_gosc_full` lub brak wierszy `mecze_zawodnicy` dla `gosp` albo `gosc`. Zapytanie używa `NOT EXISTS`, więc nie mnoży meczów przez liczbę zawodników. Pomija `wycofany=True` oraz mecze z `id_zespol_walkower`. Selekcja jest wykonywana w transakcji READ ONLY / REPEATABLE READ zakończonej ROLLBACK.

To przybliżenie rozegrania na podstawie daty, a nie potwierdzony status zakończenia z API. Dzisiejsze i przyszłe mecze oraz mecze bez daty są pomijane. Jeżeli miniony termin dotyczy przełożonego meczu i API nie ma szczegółów, odpowiedź jest pomijana zgodnie z dotychczasową obsługą braków. Obecność przynajmniej jednego zawodnika obu stron nie gwarantuje kompletności statystyk; pełny import pozostaje dostępny do ich sprawdzenia.

```text
Wybrane ligi
    -> READ ONLY: znane mecze po terminie z brakami
    -> zadania szczegółów tylko tych meczów (od najnowszych)
    -> dane meczu, występy i brakujący zawodnicy
    -> porównanie: uzupełnianie pustych pól, zachowanie istniejących wartości
    -> podgląd i osobne zatwierdzenie
```

W tym trybie mapper nie zleca pobierania składów sezonowych. Dane nowych zawodników pochodzą ze szczegółów meczu; istniejące dane osobowe są tylko uzupełniane. Nie odkrywa nowych meczów ani nie sprawdza całego terminarza. Brak kandydatów daje od razu pusty podgląd, bez wywołań API. Każdy nowy przebieg ponownie ocenia braki — nie ma jeszcze odraczania kolejnej próby dla konkretnego meczu.

Pole `PrzebiegImportu.tryb` jest zapisywane w lokalnym stanie i parametrach historii PostgreSQL. Stare przebiegi bez tego pola mają domyślnie `pelny`. Tryb jest widoczny na stronie przebiegu i w historii. Poniższy opis przechodzenia przez sezony, rundy i kolejki dotyczy trybu pełnego; porównanie i zatwierdzenie są wspólne.

## Import tabel wybranego sezonu

Trzeci, osobny tryb (`tryb="tabele"`, „Tylko tabele”) pobiera wyłącznie tabele (klasyfikacje) wybranych rozgrywek dowolnego sezonu obecnego w bazie. Dwa dotychczasowe tryby działają bez zmian i nadal dotyczą sezonu 2026/2027 oraz listy `LIGI_IMPORTU`.

Sekcja „Import tabel” w panelu ma listę sezonów i rozgrywek odczytaną z bazy (`ImportSQLAlchemyRepository.pobierz_sezony()` i `pobierz_rozgrywki_sezonu()`, transakcja READ ONLY zakończona ROLLBACK). Domyślnie wybrany jest bieżący sezon — z najwyższym `rok_rozpoczecia` wśród sezonów mających rozgrywki. Zmiana sezonu przeładowuje listę rozgrywek (GET `?sezon_tabel=`); bez JavaScript służy do tego przycisk „Pokaż rozgrywki sezonu”. Domyślnie zaznaczone są Superligi i Ligi Centralne (bez Superpucharów); przyciski szybkiego wyboru dopasowują nazwy z bazy także w środku nazwy (np. „LOTTO Superliga”). `ImportService.rozpocznij_tabele()` odrzuca sezon spoza listy i rozgrywki spoza wybranego sezonu.

```text
Wybrany sezon i rozgrywki (z bazy, READ ONLY)
    -> pokaz_tabele_spis.php?Rozgrywki=...            (dla każdych rozgrywek)
    -> pokaz_tabela.php?Rozgrywki=...&Tabela=...&Tabela2=...   (dla każdej tabeli i grupy; grupa 0, gdy brak menu2)
    -> rekordy: tabele, tabele_grupy, tabele_wiersze (+ brakujące zespoly, zespoly_sezony, zespoly_rozgrywki)
    -> porównanie z bazą, podgląd i osobne zatwierdzenie (jak w pozostałych trybach)
```

Mapowanie pól wierszy tabeli odpowiada staremu importerowi (`data/desktop/zprp_desktop/importers/standings.py`): mecze, zwycięstwa, remisy, porażki, bramki, punkty, `Zd_St`, `Kryteria`, `Grupa`, `GrupaKolor`; `miejsce` i `kolejnosc_zrodlowa` to kolejność wiersza w odpowiedzi. Wiersz nagłówka (`"0"`, bez `ID_zespoly`) nie jest drużyną — z niego pochodzą `Kryteria`, gdy wiersz ich nie ma. Wiersz bez poprawnego `ID_zespoly` jest pomijany (numeracja miejsc zostaje zachowana). Rozgrywki bez tabel (pusty spis, np. puchary) nie przerywają importu. Drużyny z tabeli są dopisywane do `zespoly`, `zespoly_sezony` i `zespoly_rozgrywki` wybranego sezonu z `uzupelnij=True` — istniejące wartości, w tym nazwy sezonowe, nie są nadpisywane. Składów nie pobiera.

Tabele w bazie mają sztuczne klucze (`tabele.id` → `tabele_grupy.id_tabela` → `tabele_wiersze.id_tabela_grupa`), więc klucze rekordów zawierają łańcuch odwołań po kluczach naturalnych (`id_rozgrywki`+`tabela_id`, grupa `grupa_id`, wiersz `id_zespol`). Repozytorium rozwiązuje go rekurencyjnie od rodzica (`_rozwiaz_klucz()`, `_identyfikator()`); gdy rodzica nie ma w bazie, rekord jest nowy, a przy zapisie rodzic powstaje wcześniej dzięki kolejności `KOLEJNOSC`. Aktualizacja bez rozwiązanego klucza jest przerywana błędem, żeby nie powstał `UPDATE` bez warunku. Blokada doradcza, parametry historii (`sezon`) i opis kontekstu audytu używają sezonu przebiegu (`id_sezon`, `nazwa_sezonu`); przebiegi zapisane przed tą zmianą mają domyślnie sezon 195.

Import nie usuwa wierszy: drużyna wycofana z tabeli w ZPRP pozostanie w starym stanie (stary importer przycinał takie wiersze). Do sprawdzenia rzeczywistego zachowania użyto API ZPRP i bazy tylko do podglądu (sezon 2026/2027, Superliga M i Liga Centralna M): 4 odpowiedzi, istniejące tabele i grupy rozpoznane jako bez zmian, 14 nowych i 12 zmienionych wierszy; zapisu nie wykonano.

## 1. Przebieg w skrócie

```text
Administrator wybiera ligi
          |
          v
[Sprawdź aktualizacje ZPRP]
          |
          v
Utworzenie przebiegu i kolejki zadań
          |
          v
Pobieranie API ZPRP <---------+
          |                  |
          v                  |
Zapis odpowiedzi na dysku    |
          |                  |
          v                  |
Mapowanie na rekordy        |
i odkrywanie kolejnych zadań-+
          |
          | kolejka pusta
          v
Porównanie z PostgreSQL (READ ONLY)
          |
          v
Podgląd: nowe / zmienione / bez zmian
          |
          | administrator zaznacza potwierdzenie
          | i klika [Zastosuj aktualizację]
          v
Kontrola, czy baza i pliki źródłowe się nie zmieniły
          |
          v
Jedna transakcja zapisu danych i historii w PostgreSQL
          |
          v
ZAPISANO + numer przebiegu w bazie
```

Samo zaznaczenie lig nie rozpoczyna pobierania. Przycisk „Odśwież podgląd” ponownie porównuje wcześniej pobrane dane z bazą; nie pobiera ponownie API.

## 2. Krok po kroku

### Krok 1 — wejście i wybór zakresu

`ImportPanelView` sprawdza logowanie HTTP Basic: użytkownik `admin`, hasło ze zmiennej środowiskowej `HDS_IMPORT_PASSWORD`. Brak konfiguracji daje ekran informacyjny z kodem 503, a brak poprawnego logowania — 401. Formularze POST wymagają tokenu CSRF przechowywanego w sesji.

Lista dozwolonych rozgrywek pochodzi z `LIGI_IMPORTU` w [imports.py](../src/handball/domain/imports.py). Przyciski szybkiego wyboru zmieniają checkboxy, a „Tylko…” zastępuje wcześniejszy wybór. Puchar Polski obejmuje eliminacje wojewódzkie, bez Superpucharów. Wszystkie ligi są domyślnie zaznaczone.

### Krok 2 — utworzenie przebiegu

Kliknięcie „Pełny import — sprawdź aktualizacje ZPRP” wysyła `akcja=rozpocznij`. Widok sprawdza sezon, a `ImportService.rozpocznij()` odrzuca pustą listę i identyfikatory spoza dozwolonego zakresu.

Serwis tworzy `PrzebiegImportu`: własny UUID, czas rozpoczęcia, uporządkowaną listę lig bez duplikatów i status `POBIERANIE`. Na początek wpisuje dwa zadania: pobranie sezonów oraz rozgrywek sezonu 195. Zapisuje stan lokalnie i przekierowuje do `/administracja/import/<uuid>`.

### Krok 3 — pobieranie kolejnych odpowiedzi

[import.js](../src/handball/interface/static/js/import.js) wysyła kolejne żądania POST z `akcja=krok`. `ImportService.krok()` pobiera co najwyżej jedną nową odpowiedź API w jednym wywołaniu. Zadania już wykonane pomija na podstawie skrótu nazwy endpointu i parametrów.

`ZprpClient` wykonuje GET do `https://rozgrywki.zprp.pl/api/`. Ma limit odpowiedzi 10 000 000 bajtów, timeout 25 sekund i sprawdza poprawność JSON. `ImportFileStore` zapisuje surowy JSON i adres źródła. Serwis zapamiętuje SHA-256 treści do późniejszej kontroli integralności.

Mapper odkrywa następne zadania w trakcie odczytu odpowiedzi:

| Kolejność odkrywania | Endpoint | Co następuje dalej |
| --- | --- | --- |
| Sezony | `pokaz_sezony.php` | Potwierdzenie sezonu 195 i nazwy 2026/2027 |
| Rozgrywki | `pokaz_rozgrywki.php?Sezon=195` | Sprawdzenie wybranych lig i kategorii seniorów; zadania rund |
| Rundy | `pokaz_rundy.php?Rozgrywki=...` | Zadania kolejek |
| Kolejki | `pokaz_kolejki.php?Runda=...` | Zadania list meczów |
| Mecze | `pokaz_mecze.php?Kolejka=...` | Zadania szczegółów meczów i składów odkrytych drużyn |
| Szczegóły meczu | `pokaz_mecze_szczegoly.php?Zawody=...` | Uzupełnienie meczu, zawodników i statystyk występu |
| Skład sezonowy | `pokaz_sklad.php?Sezon=195&Zespol=...` | Dane drużyny w sezonie i dane osobowe zawodników |

Pusta lista meczów kolejki (`[]` lub `{}`) jest pomijana. Brak nagłówka szczegółów meczu, również pusta odpowiedź JSON lub `null`, nie zatrzymuje importu: pozostają dane meczu pobrane z listy, a importer przechodzi do następnych zadań. Odpowiedź zostaje zachowana jako źródło, a zadanie oznaczone jako wykonane w tym przebiegu. Nowy przebieg spróbuje pobrać je ponownie. Nie dotyczy to błędów sieciowych, niepoprawnego JSON, błędnego identyfikatora w obecnym nagłówku ani niezgodności sezonu lub ligi — te nadal zgłaszają błąd.

To kolejność odkrywania zależności, nie sztywne oddzielne fazy. Zadania trafiają na koniec kolejki, więc szczegóły i składy mogą być przeplatane. Liczba zadań rośnie w trakcie pobierania.

### Krok 4 — mapowanie danych

`ZprpImportMapper` zamienia pola API na `RekordImportu`: nazwę tabeli, klucz rekordu, dane i listę źródeł. Gdy ten sam rekord pojawia się ponownie, mapper scala pola; później przetworzone wartości zastępują wcześniejsze wartości tych samych pól.

Sprawdza wymagane identyfikatory, sezon, kategorię i zgodność szczegółów z meczem. Rozróżnia brak pola w odpowiedzi od pola przekazanego z pustą wartością. Brak pola nie zleca jego aktualizacji; pusta wartość obecnego pola może zostać zamieniona na `None`. Niepoprawna data również jest zamieniana na `None`.

Na tym etapie rekordy są propozycjami w lokalnym stanie przebiegu. Mapper nie zapisuje ich do PostgreSQL.

### Krok 5 — porównanie z bazą

Gdy kolejka jest pusta, `ImportSQLAlchemyRepository.porownaj()` odczytuje rzeczywisty schemat potrzebnych tabel i ich rekordy. Pracuje w transakcji `READ ONLY`, z izolacją `REPEATABLE READ`, zakończonej `ROLLBACK`.

Dla każdego rekordu zapisuje poprzedni stan oraz różnice:

- **Nowy:** w bazie nie ma rekordu o danym kluczu.
- **Zmieniony:** istniejący rekord ma inne wartości importowanych pól.
- **Bez zmian:** nie ma pól wymagających zapisu.

Dla rekordów oznaczonych `uzupelnij=True` — podstawowych danych zespołów i zawodników — istniejące niepuste wartości są zachowywane; uzupełniane są pola mające w bazie `NULL`. Pozostałe rekordy mogą aktualizować istniejące wartości. Kolizja identyfikatora z innym sezonem lub ligą przerywa porównanie.

Po udanym porównaniu status zmienia się na `PODGLAD`.

### Krok 6 — decyzja administratora

Strona pokazuje liczniki oraz różnice „Przed” i „Po”, pogrupowane według tabel. Administrator może odświeżyć porównanie albo zaznaczyć „Zatwierdzam pokazane zmiany…” i kliknąć „Zastosuj aktualizację”.

Żądanie zapisu wymaga `akcja=zastosuj`, `potwierdzenie=tak`, poprawnego CSRF i dostępu administratora. Serwis dopuszcza zapis tylko ze stanu `PODGLAD`.

### Krok 7 — zapis w PostgreSQL

`ImportSQLAlchemyRepository.zastosuj()` otwiera transakcję zapisu z izolacją `SERIALIZABLE`. Ustawia lokalne limity oczekiwania na blokadę (5 sekund) i wykonania polecenia (60 sekund), a następnie pobiera transakcyjną blokadę doradczą dla tego importera i sezonu.

W ramach tej transakcji:

1. Sprawdza w `logs.import_przebiegi`, czy ten UUID został już zapisany z sukcesem. Jeśli tak, zwraca istniejący numer przebiegu.
2. Porównuje bieżące wiersze z migawką z podglądu. Jeśli się zmieniły, przerywa zapis i wymaga odświeżenia podglądu.
3. Tworzy wpis przebiegu, kontroluje skróty plików źródłowych oraz rejestruje źródła i próby ich importu.
4. Dodaje nowe rekordy i aktualizuje zmienione pola istniejących rekordów, w kolejności zależności tabel. Nie wykonuje usuwania rekordów.
5. Ustawia kontekst audytu przez `logs.ustaw_kontekst` i wiąże rekordy z plikami źródłowymi.
6. Zapisuje liczniki i status `SUKCES` w historii PostgreSQL. Pomyślne wyjście z transakcji zatwierdza całość.

Serwis zapisuje następnie lokalny status `ZAPISANO` oraz numer przebiegu z PostgreSQL. Ponowne zatwierdzenie tego samego przebiegu jest chronione przed powtórnym wykonaniem, również gdy wcześniejszy zapis bazy zakończył się, ale lokalny status nie został jeszcze utrwalony.

## 3. Podstawowy UML tekstowy — obiekty i zależności

```text
                         +------------------+
                         | ImportRegistrar  |
                         | składa zależności|
                         +--------+---------+
                                  |
                                  v
+-----------------+      +------------------+      +-----------------+
| Przeglądarka    |----->| ImportPanelView  |----->| ImportService   |
| panel + JS      | HTTP | get() / post()   |      | rozpocznij()    |
+-----------------+      +------------------+      | krok()          |
                                                  | odswiez_podglad()|
                                                  | zastosuj()      |
                                                  +--------+--------+
                                                           |
                  +------------------+---------------------+------------------+
                  |                  |                     |                  |
                  v                  v                     v                  v
         <<Protocol>>       <<Protocol>>          <<Protocol>>       +------------------+
         ZprpReadClient      ImportStore           ImportRepository   | ZprpImportMapper |
                  ^                  ^                     ^          | przetworz()      |
                  | realizuje        | realizuje           | realizuje+------------------+
         +--------+-----+   +--------+-------+   +---------+----------------+
         | ZprpClient   |   | ImportFileStore |   | ImportSQLAlchemyRepository|
         +--------+-----+   +--------+-------+   +---------+----------------+
                  |                  |                     |
                  v                  v                     v
              API ZPRP        SQLite + JSON/URL        PostgreSQL
```

Strzałki pokazują wywołania i używane zależności. Serwis zależy od kontraktów `Protocol`; fabryka dostarcza ich konkretne implementacje. Repozytorium dodatkowo korzysta z `ImportStore`, aby odczytać i sprawdzić pliki przy zapisie.

Dane przekazywane między obiektami:

| Obiekt | Co przechowuje |
| --- | --- |
| `PrzebiegImportu` | UUID, ligi, status, kolejkę, wykonane zadania, skróty źródeł, rekordy, błąd i numer zapisu w bazie |
| `ZadaniePobrania` | Endpoint, parametry GET, rodzaj odpowiedzi i kontekst, np. identyfikator meczu |
| `RekordImportu` | Tabelę, klucz, dane, źródła, poprzedni stan i wykryte zmiany |

## 4. Statusy, błędy i wznowienie

```text
rozpocznij()
     |
     v
POBIERANIE -- koniec kolejki i porównanie --> PODGLAD -- zatwierdzenie --> ZAPISANO
     |                                         |
     | obsłużony błąd kroku                     | błąd zapisu / zmiana bazy
     v                                         v
   BLAD                                    PODGLAD + komunikat
     |                                         |
     +-- ponowienie kroku --> POBIERANIE        +-- odświeżenie podglądu
                                                   i ponowne zatwierdzenie
```

Obsłużony błąd pobierania lub porównania (`BladImportu`) zachowuje wcześniejszy stan roboczy i kolejkę. Nieudany krok można ponowić. Skrypt przeglądarki ponawia status `BLAD` maksymalnie pięć razy z opóźnieniami 1–5 sekund; udany krok zeruje licznik. Błąd HTTP lub sieciowy po stronie przeglądarki zatrzymuje automatyczną pętlę i pokazuje komunikat.

Po udanym kroku skrypt czeka 150 ms przed następnym żądaniem do aplikacji. Klient `ZprpClient` po stronie serwera dodatkowo serializuje pobrania i zachowuje co najmniej 3 sekundy między rozpoczęciami żądań do ZPRP, w obu trybach. Limit obejmuje wspólną instancję klienta w danym procesie aplikacji; nie jest globalnym limitem między osobnymi procesami lub uruchomieniami. Nie stanowi gwarancji zgodności z nieznanym limitem operatora API. **Nie ma osobnego procesu pobierającego w tle:** kolejne kroki inicjuje otwarta strona. Zamknięcie strony zatrzymuje wysyłanie następnych żądań; trwające żądanie może się jeszcze zakończyć na serwerze. Otwarcie zapisanego przebiegu w stanie `POBIERANIE` lub `BLAD` automatycznie uruchamia dalsze kroki.

Wyjątek podczas transakcji PostgreSQL wycofuje jej zmiany. Przy utracie potwierdzenia zapisu wynik może być nieznany klientowi; ponowne zatwierdzenie sprawdza istniejący sukces po UUID. SQLite i PostgreSQL są osobnymi magazynami i nie mają wspólnej transakcji.

## 5. Gdzie trafiają dane

| Miejsce | Zawartość i moment zapisu |
| --- | --- |
| `<Flask instance_path>/imports/imports.sqlite3` | Lokalny stan przebiegów; zapisywany od rozpoczęcia pobierania |
| `<Flask instance_path>/imports/<id>/<skrót>.json` | Surowa odpowiedź API |
| `<Flask instance_path>/imports/<id>/<skrót>.url` | Adres pobranej odpowiedzi |
| Tabele domenowe PostgreSQL | Dane dodawane lub aktualizowane po zatwierdzeniu |
| `public.pliki_zrodlowe`, `public.rekordy_zrodla` | Treści źródłowe i ich powiązania z rekordami, po zatwierdzeniu |
| `logs.import_przebiegi`, `logs.import_pliki` | Historia i liczniki zapisu, w tej samej transakcji PostgreSQL |

Kolejność zapisu tabel domenowych:

```text
sezony -> rozgrywki -> zespoly -> zespoly_sezony -> rundy -> kolejki
       -> zespoly_rozgrywki -> hale -> mecze -> zawodnicy -> mecze_zawodnicy
```

Historia widoczna na stronie pochodzi z lokalnego magazynu SQLite i pokazuje ostatnie 30 przebiegów. Nie jest odczytem całej historii `logs` z PostgreSQL.

## 6. Zakres i ograniczenia obecnej implementacji

- Obsługiwany jest tylko sezon 2026/2027 i zamknięta lista rozgrywek z `LIGI_IMPORTU`.
- Nowy przebieg ponownie pobiera dane wybranego zakresu, także rozegrane mecze. Dzięki temu może wykryć korekty wcześniejszych wyników; nie jest to wyłącznie pobranie nowych meczów.
- Importer nie usuwa rekordów nieobecnych w kolejnej odpowiedzi API. Takie zniknięcie nie powoduje automatycznego skasowania danych.
- Skład sezonowy służy obecnie do uzupełnienia drużyny i zawodników; mapper nie zapisuje tabeli `sklady`. Statystyki występów pochodzą ze szczegółów meczu i trafiają do `mecze_zawodnicy`.
- Wartości wyników i flaga `zamiana` są mapowane z API. Lista meczów przy `zamiana=True` odwraca kolejność drużyn i obu części wyniku; nie zmienia zapisu źródłowego.
- Odpowiedzi API są pobierane kolejno, więc nie tworzą jednej gwarantowanej migawki źródła z tego samego momentu.

## 7. Mapa kodu i dokumentacji

| Plik | Odpowiedzialność |
| --- | --- |
| [import_factory.py](../src/handball/import_factory.py) | Konfiguracja magazynu, serwisu, repozytorium i tras |
| [import_views.py](../src/handball/interface/admin/views/import_views.py) | Logowanie, CSRF, akcje HTTP, renderowanie |
| [imports.py](../src/handball/domain/imports.py) | Lista lig, obiekty danych i błąd domenowy |
| [import_service.py](../src/handball/services/import_service.py) | Przebieg, kolejka, kroki, porównanie i zatwierdzenie |
| [import_mapping.py](../src/handball/services/import_mapping.py) | Mapowanie odpowiedzi API i odkrywanie zadań |
| [zprp_client.py](../src/handball/infrastructure/zprp_client.py) | Pobieranie HTTP i kontrola JSON |
| [import_store.py](../src/handball/infrastructure/import_store.py) | Stan lokalny i surowe pliki źródłowe |
| [import_repository.py](../src/handball/infrastructure/repositories/import_repository.py) | Porównanie, zapis transakcyjny, pochodzenie rekordów i historia |
| [Kontrakt repozytorium](../src/handball/contracts/import_repository.py) / [kontrakty magazynu i klienta](../src/handball/contracts/import_storage.py) | Granice zależności serwisu |
| [panel.md](../src/handball/interface/templates/admin/import/panel.md) | Ekran, formularze, selektory i mapa układu |
| [import.js](../src/handball/interface/static/js/import.js) | Szybki wybór lig i pętla pobierania w przeglądarce |
| [Schemat logs](database/LOGS_SCHEMA.md) | Opis tabel i funkcji audytu bazy |

Testy zachowania znajdują się w [test_import_service.py](../tests/unit/test_import_service.py), [test_import_mapping.py](../tests/unit/test_import_mapping.py) i [test_imports.py](../tests/interface/test_imports.py). Osobny [test_import_repository.py](../tests/integration/test_import_repository.py) dotyczy integracji z bazą i wymaga środowiska zgodnego z zasadami projektu.

Dokument zweryfikowano przez odczyt kodu i kontrolę odnośników. W ramach jego przygotowania nie uruchamiano aplikacji, API ani operacji na bazie.
