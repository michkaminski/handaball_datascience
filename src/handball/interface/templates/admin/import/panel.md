# Import danych ZPRP

Istniejący szablon [panel.html](panel.html) obsługuje wybór rozgrywek sezonu 2026/2027, import wybranych meczów, osobny import tabel wybranego sezonu i rozgrywek, podgląd przebiegu i historię pobrań. Dziedziczy `base.html`; definiuje bloki `tytul` i `tresc`. Wzorzec v6 `imports.html` dostarcza wspólną ramę administracji, a jego treść była placeholderem.

Opis całego procesu, magazynów danych i tekstowy UML: [Importy — krok po kroku](../../../../../../docs/IMPORTS.md).

## Dane i powiązania

[ImportPanelView](../../../admin/views/import_views.py) przekazuje:

| Pole | Znaczenie |
| --- | --- |
| `sekcja_aktywna` | `import` — aktywna pozycja menu |
| `konfiguracja` | Czy skonfigurowano dostęp administratora |
| `csrf` | Token formularzy POST, przekazywany przy skonfigurowanym dostępie |
| `ligi` | Słownik identyfikatorów i nazw `LIGI_IMPORTU` z [imports.py](../../../../domain/imports.py) |
| `przebieg` | `PrzebiegImportu` lub `None` |
| `historia` | Lista przebiegów z magazynu serwisu |
| `opcje_tabel` | `OpcjeImportuTabel` (sezony z bazy, wybrany sezon — domyślnie bieżący, rozgrywki wybranego sezonu) lub `None` |
| `blad_opcji` | Komunikat, gdy nie udało się odczytać sezonów i rozgrywek z bazy (sekcja tabel pokazuje go zamiast formularza) |

Widok korzysta z `ImportService`. Brak konfiguracji zwraca ekran instrukcji dostępu (503), brak poprawnego logowania HTTP Basic — 401. Formularze POST wymagają tokenu CSRF. Dokument opisuje istniejący interfejs; zmiana zaznaczenia nie uruchamia importu.

## Dwa tryby importu

Formularz rozpoczynania ma dwa przyciski `name="tryb"`: `pelny` pobiera cały wybrany zakres, a `uzupelniajacy` pobiera tylko szczegóły znanych meczów sprzed dzisiejszego dnia (Europe/Warsaw), którym brakuje dowolnej części wyniku `*_full` albo zawodników po stronie `gosp` lub `gosc`. Wycofane mecze i walkowery są pomijane. Nie obejmuje to nieznanych meczów, dzisiejszych spotkań, meczów bez daty ani niepełnych statystyk wewnątrz istniejących składów.

Tryb uzupełniający nie pobiera składów sezonowych i nie nadpisuje istniejących niepustych wartości. Nowych zawodników dodaje z danych szczegółów meczu. Pełny import służy także korektom. `przebieg.nazwa_trybu` jest widoczna nad postępem oraz w kolumnie „Tryb” historii. Starsze lokalne przebiegi bez pola `tryb` są odczytywane jako pełne.

Brak kandydatów prowadzi od razu do podglądu z komunikatem „Nie znaleziono meczów wymagających uzupełnienia”, bez żądań do ZPRP. Przy pustej liście rekordów przycisk zatwierdzenia nie jest wyświetlany. Każdy klient API w procesie aplikacji zachowuje odstęp co najmniej 3 sekund między rozpoczęciami żądań.

## Import wybranych meczów

Sekcja `#import-meczu` ma formularz POST `akcja=rozpocznij_mecz` z polem `mecz` (textarea). Przyjmuje jeden albo wiele numerów meczów ZPRP (`mecze.id`) albo adresów stron; widok wyciąga numery (`ImportPanelView._numery_meczow()`: 4–9 cyfr na początku fragmentu, po spacji, przecinku lub średniku, po `Zawody=` albo jako segment ścieżki). Jeden numer uruchamia `ImportService.rozpocznij_mecz()` i tryb `mecz` („Jeden mecz”). Więcej numerów uruchamia `rozpocznij_mecze()` i tryb `mecze` („Wybrane mecze”). Odczyt jest tylko do odczytu (`pobierz_mecz()` / `pobierz_mecze()`): mecz musi być w bazie i mieć kolejkę; sezon przebiegu jest sezonem meczu. Nieznany numer odrzuca wybór z podpowiedzią, aby pobrać go pełnym importem rozgrywek — szczegóły meczu nie podają identyfikatora kolejki.

To samo pobranie startuje ze strony [Pobieranie meczów](schedule.md): checkboxy `name="mecze"` i POST `akcja=rozpocznij_mecze`. Jedno zaznaczenie zostaje trybem „Jeden mecz”. Limit to 80 meczów. Publiczny Terminarz nie ma tego zaznaczenia.

Tryb działa jak pełny import ograniczony do jednego meczu: aktualizuje zmienione wartości (korekty wyniku, widzów, hali, składów), dopisuje brakujących zawodników i wpisy `mecze_zawodnicy`, nie pobiera składów sezonowych i niczego nie usuwa. Przebieg pokazuje numer, drużyny, termin i rozgrywki meczu (`przebieg.id_mecz`, `przebieg.opis`); po zapisie link prowadzi do karty meczu, a historia dopisuje „mecz N” w kolumnie „Ligi”. Parametry przebiegu w `logs.import_przebiegi` zawierają `mecz`.

## Import tabel

Sekcja `#import-tabel` ma formularz GET z listą sezonów (`sezon_tabel`, pierwszy oznaczony „(bieżący)”), który w JavaScript przeładowuje stronę po zmianie wyboru, a bez JavaScript przyciskiem „Pokaż rozgrywki sezonu”. Poniżej formularz POST `akcja=rozpocznij_tabele` z ukrytym `sezon_tabel` i checkboxami `name="ligi"` rozgrywek wybranego sezonu; Superligi i Ligi Centralne są domyślnie zaznaczone. Przebieg tabel pokazuje tryb „Tylko tabele”, sezon i listę rozgrywek; potwierdzenie zapisu wymienia sezon przebiegu, a po zapisie link prowadzi do listy tabel tego sezonu. Opis procesu: [IMPORTS.md](../../../../../../docs/IMPORTS.md#import-tabel-wybranego-sezonu).

## Szybki wybór rozgrywek

Nad checkboxami znajduje się siedem przycisków typu `button`: „Zaznacz wszystkie”, „Odznacz wszystkie”, „Tylko Superligi”, „Tylko Ligi Centralne”, „Tylko I ligi”, „Tylko II ligi” i „Tylko Puchar Polski”. Przyciski „Tylko…” zastępują cały wybór, zaznaczając rozgrywki obu płci danej grupy. Następnie można ręcznie zmienić dowolny checkbox.

Klasa `WyborLigController` w [import.js](../../../static/js/import.js) operuje wyłącznie wewnątrz swojego `[data-wybor-lig]` (w panelu są dwa: import sezonu 2026/2027 i import tabel). Wzorzec z prefiksem `*` dopasowuje fragment nazwy (bez Superpucharów), a `|` łączy kilka wzorców — używane w sekcji tabel, gdzie nazwy z bazy mają przedrostki sponsorów. Nazwy pochodzą z `data-nazwa` checkboxów, a prefiksy z `data-wybor` przycisków. Porównanie ignoruje wielkość liter. Prefiksy `i liga ` i `ii liga ` są rozłączne. `puchar polski ` obejmuje rozgrywki wojewódzkie i eliminacje, ale nie Superpuchar Polski. „Zaznacz wszystkie” obejmuje również Superpuchary.

Obsługa inicjalizuje się również bez formularza pobierania `#pobieranie`. Przyciski nie wysyłają formularza ani żądania sieciowego. Bez JavaScript pasek pozostaje ukryty, a checkboxy działają ręcznie. Domyślnie wszystkie ligi są zaznaczone. Pusty wybór po wysłaniu odrzuca istniejąca walidacja serwisu.

## Pozostałe stany

Przy `konfiguracja=False` widoczny jest tylko panel dostępu administratora. Przy braku przebiegu formularz wyboru i historia pozostają dostępne. Pusta historia pokazuje komunikat o braku przebiegów.

`POBIERANIE` i `BLAD` pokazują formularz kontynuacji oraz status pobierania; istniejący skrypt obsługuje automatyczne kroki i ponowienia. `PODGLAD` pokazuje liczniki zmian, osobne potwierdzenie zastosowania oraz odświeżenie podglądu. `ZAPISANO` pokazuje potwierdzenie i link do meczów sezonu, tabel sezonu albo karty pobranego meczu. Tabela zmian występuje dla `PODGLAD` i `ZAPISANO`. Historia zawiera rozpoczęcie, tryb, status, ligi i błąd.

## Weryfikacja

Testy [test_imports.py](../../../../../../tests/interface/test_imports.py) sprawdzają widok z podmienionym serwisem i repozytorium testowym. Przy zmianie szybkiego wyboru sprawdź wszystkie siedem akcji, zastępowanie wcześniejszego wyboru, rozdzielenie I/II ligi oraz wyłączenie Superpucharów z Pucharu Polski. Kontrole wyboru nie wymagają API ZPRP ani połączenia z bazą.

## Układ tekstowy i mapa zmian

```text
[wspólna rama base.html: nagłówek, menu, sidebar]
Aktualizacja danych ZPRP
[brak konfiguracji: Dostęp administratora]
[skonfigurowany dostęp:]
  Zakres pobierania
    Sezon [2026/2027]
    Rozgrywki
      [Zaznacz wszystkie] [Odznacz wszystkie]
      [Tylko Superligi] [Tylko Ligi Centralne]
      [Tylko I ligi] [Tylko II ligi] [Tylko Puchar Polski]
      [x] Nazwa rozgrywek ...
    Informacja o pobieraniu
    [Pełny import — sprawdź aktualizacje ZPRP]
    [Uzupełnij brakujące dane meczów]
    Opis zakresu uzupełniania
  Jeden mecz (#import-meczu)
    Numer meczu ZPRP albo adres strony meczu [_______]
    [Pobierz mecz — sprawdź zmiany]
    Opis: szczegóły jednego znanego meczu, aktualizacja bez usuwania, zapis po zatwierdzeniu
  Import tabel (#import-tabel)
    Opis: tylko tabele, zapis po zatwierdzeniu, bez usuwania
    Sezon [2026/2027 (bieżący) v]  [Pokaż rozgrywki sezonu — tylko bez JS]
    Rozgrywki sezonu ...
      [Zaznacz wszystkie] [Odznacz wszystkie] [Tylko Superligi] [Tylko Ligi Centralne]
      [Superligi i Ligi Centralne] [Tylko I ligi] [Tylko II ligi]
      [x] LOTTO Superliga ... [ ] I Liga ...
    [Pobierz tabele — sprawdź zmiany]
  [jeśli istnieje przebieg:]
    Przebieg: status, tryb · sezon, [jeden mecz: numer, drużyny, termin, rozgrywki], liczba pobrań i zadań, ewentualny błąd
    [uzupełnianie bez kandydatów: komunikat o braku meczów]
    [kontynuacja / podgląd i zatwierdzenie / potwierdzenie zapisu]
    [dla podglądu i zapisu: rozwijane tabele zmian rekordów]
  Historia pobrań w Handball DataScience
    Rozpoczęcie | Tryb | Sezon | Status | Ligi | Błąd
[wspólna stopka]
```

Pasek przycisków zawija się według dostępnej szerokości; rysunek pokazuje umowny podział na wiersze. Historia i zmiany rekordów korzystają z `.table-wrap`.

| Element | Plik | Miejsce zmiany |
| --- | --- | --- |
| Nagłówek, formularze i warunki widoczności | [panel.html](panel.html) | Bloki `tytul`, `tresc`, warunki `konfiguracja` i `przebieg.status` |
| Wybór trybu | [panel.html](panel.html) | Przyciski `name="tryb"`, `przebieg.tryb`, `przebieg.nazwa_trybu`; selekcja w `ImportSQLAlchemyRepository.pobierz_brakujace()` |
| Przyciski i checkboxy | [panel.html](panel.html) | `[data-wybor-lig]`, `.import-selection`, `data-wybor`, `data-nazwa`, `name="ligi"` |
| Zaznaczanie grup | [import.js](../../../static/js/import.js) | `WyborLigController.uruchom()` i `zaznacz()` |
| Odstępy i zawijanie przycisków | [admin.css](../../../static/css/admin.css) | `.import-selection:not([hidden])`, `.btn.secondary.small`, `.import-form`, `.import-choice` |
| Lista nazw i identyfikatorów | [imports.py](../../../../domain/imports.py) | `LIGI_IMPORTU` |
| Import jednego meczu | [panel.html](panel.html), [import_views.py](../../../admin/views/import_views.py), [import_service.py](../../../../services/import_service.py), [import_repository.py](../../../../infrastructure/repositories/import_repository.py) | `#import-meczu`, `akcja=rozpocznij_mecz`, `NUMER_MECZU`, `_numer_meczu()`, `rozpocznij_mecz()`, `pobierz_mecz()`, `przebieg.id_mecz`, `przebieg.opis` |
| Import tabel | [panel.html](panel.html), [import_service.py](../../../../services/import_service.py), [import_mapping.py](../../../../services/import_mapping.py) | `#import-tabel`, `data-import-sezon`, `opcje_tabel()`, `rozpocznij_tabele()`, `tabele_spis()`, `tabela()` |
| Łańcuch kluczy tabel | [import_repository.py](../../../../infrastructure/repositories/import_repository.py) | `KOLEJNOSC`, `_rozwiaz_klucz()`, `_identyfikator()`, `_warunek_klucza()`, `pobierz_sezony()`, `pobierz_rozgrywki_sezonu()` |
| Dane widoku i obsługa formularzy | [import_views.py](../../../admin/views/import_views.py) | `ImportPanelView.get()` i `post()` |
| Postęp pobierania | [import.js](../../../static/js/import.js) | `#pobieranie`, `#stan-pobierania`, liczniki odpowiedzi i zadań |
| Historia i różnice | [panel.html](panel.html) | `#historia`, `przebieg.rekordy`, `.table-wrap` |
| Wspólna rama | [base.md](../../base.md) | Nagłówek, nawigacja, sidebar i stopka |
