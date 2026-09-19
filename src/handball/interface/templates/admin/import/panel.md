# Import danych ZPRP

Istniejący szablon [panel.html](panel.html) obsługuje wybór rozgrywek sezonu 2026/2027, podgląd przebiegu i historię pobrań. Dziedziczy `base.html`; definiuje bloki `tytul` i `tresc`. Wzorzec v6 `imports.html` dostarcza wspólną ramę administracji, a jego treść była placeholderem.

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

Widok korzysta z `ImportService`. Brak konfiguracji zwraca ekran instrukcji dostępu (503), brak poprawnego logowania HTTP Basic — 401. Formularze POST wymagają tokenu CSRF. Dokument opisuje istniejący interfejs; zmiana zaznaczenia nie uruchamia importu.

## Dwa tryby importu

Formularz rozpoczynania ma dwa przyciski `name="tryb"`: `pelny` pobiera cały wybrany zakres, a `uzupelniajacy` pobiera tylko szczegóły znanych meczów sprzed dzisiejszego dnia (Europe/Warsaw), którym brakuje dowolnej części wyniku `*_full` albo zawodników po stronie `gosp` lub `gosc`. Wycofane mecze i walkowery są pomijane. Nie obejmuje to nieznanych meczów, dzisiejszych spotkań, meczów bez daty ani niepełnych statystyk wewnątrz istniejących składów.

Tryb uzupełniający nie pobiera składów sezonowych i nie nadpisuje istniejących niepustych wartości. Nowych zawodników dodaje z danych szczegółów meczu. Pełny import służy także korektom. `przebieg.nazwa_trybu` jest widoczna nad postępem oraz w kolumnie „Tryb” historii. Starsze lokalne przebiegi bez pola `tryb` są odczytywane jako pełne.

Brak kandydatów prowadzi od razu do podglądu z komunikatem „Nie znaleziono meczów wymagających uzupełnienia”, bez żądań do ZPRP. Przy pustej liście rekordów przycisk zatwierdzenia nie jest wyświetlany. Każdy klient API w procesie aplikacji zachowuje odstęp co najmniej 3 sekund między rozpoczęciami żądań.

## Szybki wybór rozgrywek

Nad checkboxami znajduje się siedem przycisków typu `button`: „Zaznacz wszystkie”, „Odznacz wszystkie”, „Tylko Superligi”, „Tylko Ligi Centralne”, „Tylko I ligi”, „Tylko II ligi” i „Tylko Puchar Polski”. Przyciski „Tylko…” zastępują cały wybór, zaznaczając rozgrywki obu płci danej grupy. Następnie można ręcznie zmienić dowolny checkbox.

Klasa `WyborLigController` w [import.js](../../../static/js/import.js) operuje wyłącznie wewnątrz `[data-wybor-lig]`. Nazwy pochodzą z `data-nazwa` checkboxów, a prefiksy z `data-wybor` przycisków. Porównanie ignoruje wielkość liter. Prefiksy `i liga ` i `ii liga ` są rozłączne. `puchar polski ` obejmuje rozgrywki wojewódzkie i eliminacje, ale nie Superpuchar Polski. „Zaznacz wszystkie” obejmuje również Superpuchary.

Obsługa inicjalizuje się również bez formularza pobierania `#pobieranie`. Przyciski nie wysyłają formularza ani żądania sieciowego. Bez JavaScript pasek pozostaje ukryty, a checkboxy działają ręcznie. Domyślnie wszystkie ligi są zaznaczone. Pusty wybór po wysłaniu odrzuca istniejąca walidacja serwisu.

## Pozostałe stany

Przy `konfiguracja=False` widoczny jest tylko panel dostępu administratora. Przy braku przebiegu formularz wyboru i historia pozostają dostępne. Pusta historia pokazuje komunikat o braku przebiegów.

`POBIERANIE` i `BLAD` pokazują formularz kontynuacji oraz status pobierania; istniejący skrypt obsługuje automatyczne kroki i ponowienia. `PODGLAD` pokazuje liczniki zmian, osobne potwierdzenie zastosowania oraz odświeżenie podglądu. `ZAPISANO` pokazuje potwierdzenie i link do meczów. Tabela zmian występuje dla `PODGLAD` i `ZAPISANO`. Historia zawiera rozpoczęcie, tryb, status, ligi i błąd.

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
  [jeśli istnieje przebieg:]
    Przebieg: status, tryb, liczba pobrań i zadań, ewentualny błąd
    [uzupełnianie bez kandydatów: komunikat o braku meczów]
    [kontynuacja / podgląd i zatwierdzenie / potwierdzenie zapisu]
    [dla podglądu i zapisu: rozwijane tabele zmian rekordów]
  Historia pobrań w Handball DataScience
    Rozpoczęcie | Tryb | Status | Ligi | Błąd
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
| Dane widoku i obsługa formularzy | [import_views.py](../../../admin/views/import_views.py) | `ImportPanelView.get()` i `post()` |
| Postęp pobierania | [import.js](../../../static/js/import.js) | `#pobieranie`, `#stan-pobierania`, liczniki odpowiedzi i zadań |
| Historia i różnice | [panel.html](panel.html) | `#historia`, `przebieg.rekordy`, `.table-wrap` |
| Wspólna rama | [base.md](../../base.md) | Nagłówek, nawigacja, sidebar i stopka |
