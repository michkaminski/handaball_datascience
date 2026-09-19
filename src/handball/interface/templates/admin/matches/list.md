# Lista meczów

Status: etap 4 ukończony i trzykrotnie rozszerzony na wyraźne polecenie użytkownika: (1) filtry bez surowych ID, wyszukiwanie po drużynie/dacie i kolumna Hala; (2) sortowanie przez klik w nagłówek kolumny (zamiast pola w filtrach), kolumny Sezon/Rozgrywki, usunięcie podpowiedzi formatu w polu daty, wyszukiwanie drużyny po tożsamości zespołu (a nie tylko tekście nazwy); (3) filtr Rozgrywki pokazuje każdą nazwę tylko raz (zamiast raz na sezon) i po wyborze pokazuje mecze ze wszystkich sezonów tej nazwy. Szablon `list.html` istnieje.

Docelowy szablon względem katalogu szablony: `admin/matches/list.html`.

## Szybka lista elementów do zgłaszania zmian

Elementy poniżej są wymienione w kolejności na stronie. Oznaczenia F/T/P/M są stałe, dlatego nowe pozycje mogą mieć wyższy numer mimo wcześniejszego miejsca na stronie. Służą do wskazywania zmian w rozmowie; nie są wyświetlane w aplikacji.

### Filtry — F

| Oznaczenie | Element | Obecne działanie |
| --- | --- | --- |
| F1 | Sezon | Lista rozwijana; „Wszystkie” albo wybrany sezon |
| F2 | Rozgrywki | Lista rozwijana z unikalnymi nazwami rozgrywek |
| F7 | Runda | Lista rozwijana z unikalnymi nazwami rund; „Wszystkie” bez zawężenia |
| F8 | Kolejka | Lista rozwijana z unikalnymi nazwami kolejek; „Wszystkie” bez zawężenia |
| F3 | Hala | Lista rozwijana z nazwami hal |
| F4 | Drużyna | Pole tekstowe; wyszukiwanie po nazwie drużyny, także historycznej |
| F5 | Data | Pole tekstowe: rok, rok-miesiąc albo pełna data |
| F6 | Filtruj | Przycisk zastosowania wybranych filtrów |

### Tabela meczów — T

| Oznaczenie | Kolumna | Obecna zawartość |
| --- | --- | --- |
| T1 | ID | Identyfikator meczu |
| T2 | Data | Dzień meczu w formacie DD.MM.RRRR; kliknięcie nagłówka zmienia sortowanie |
| T3 | Godz. | Godzina meczu w formacie GG:MM |
| T4 | Sezon | Nazwa sezonu, np. 2026/2027 |
| T5 | Rozgrywki | Nazwa rozgrywek |
| T10 | Runda | Nazwa rundy; kolumna opcjonalna, domyślnie ukryta |
| T11 | Kolejka | Nazwa kolejki; kolumna opcjonalna, domyślnie ukryta |
| T6 | Gospodarz | Nazwa gospodarza z uwzględnieniem zmiany gospodarza |
| T7 | Wynik | Pogrubiony wynik, np. 19 : 46; kolejność zgodna z drużynami |
| T8 | Gość | Nazwa gościa z uwzględnieniem zmiany gospodarza |
| T9 | Hala | Nazwa hali |

### Widoczność kolumn — M

| Oznaczenie | Element | Obecne działanie |
| --- | --- | --- |
| M1 | Widoczne kolumny | Przycisk nad tabelą otwierający modal |
| M2 | Runda / Kolejka | Dwa niezależne checkboxy widoczności kolumn |
| M3 | Zastosuj | Zmienia widoczność i zapamiętuje wybór w przeglądarce |
| M4 | Anuluj / × / Escape | Zamyka modal bez zastosowania zmian |

### Pod tabelą — P

| Oznaczenie | Element | Obecne działanie |
| --- | --- | --- |
| P1 | Licznik wyników | Zakres wyświetlanych pozycji i liczba wszystkich wyników |
| P2 | Poprzednia / Następna | Przejście między stronami z zachowaniem filtrów |

Przykłady krótkich poleceń: „F4: poszerz pole drużyny”, „T9: usuń kolumnę Hala”, „T2: ustaw domyślnie najnowsze mecze”, „T11 przenieś za T1”. To przykłady sposobu zgłaszania, nie lista zmian do wykonania.

## Przeznaczenie

Tabela meczów i zwarte filtry na podstawie matches.html prototypu v6. Kolumny: ID, Data (klikalny nagłówek sortujący), Godz., Sezon, Rozgrywki, Runda (opcjonalna), Kolejka (opcjonalna), Gospodarz, Wynik, Gość, Hala. Status/Akcje z prototypu wciąż nie są dostarczane przez `PozycjaListyMeczow` — świadomie odłożone.

Filtry sezonu, rozgrywek, rundy, kolejki i hali są rozwijanymi listami z nazwami (nie polami liczbowymi z ID) — użytkownik nigdy nie wpisuje ani nie widzi surowego identyfikatora bazy. Filtr sezonu jest opcjonalny: pusty wybór ("Wszystkie") przeszukuje wszystkie sezony.

**Filtr Rozgrywki filtruje po nazwie, nie po `id_rozgrywki`.** Ta sama nazwa rozgrywek (np. "I Liga Kobiet") ma osobny wiersz w tabeli `rozgrywki` w każdym sezonie, w którym się odbyły — bez tej zmiany lista rozwijana pokazywałaby tę samą nazwę wielokrotnie (raz na sezon). `RozgrywkiSQLAlchemyRepository.pobierz_nazwy()` zwraca `DISTINCT` nazwy, a `MeczSQLAlchemyRepository` filtruje przez `Rozgrywki.nazwa == filtry.rozgrywki` (dokładne dopasowanie, bo nazwa pochodzi z zamkniętej listy rozwijanej, nie z wolnego tekstu) — to samo złączenie z `Rozgrywki`, które i tak istnieje do wyświetlenia kolumny "Rozgrywki". Dzięki temu wybór jednej nazwy pokazuje mecze ze wszystkich sezonów tej nazwy, chyba że dodatkowo zawężono filtrem Sezon.

**Sortowanie jest w nagłówku kolumny "Data", nie w panelu filtrów** — to ustalona konwencja dla wszystkich list z filtrami w tym projekcie, patrz [CODING_STANDARDS](../../../../../../docs/CODING_STANDARDS.md), sekcja "Listy z filtrami". Panel filtrów nie ma już pola "Sortowanie".

## Podgląd szczegółów

Link „Szczegóły” otwiera mecz w nowej karcie (`target="_blank"`). Dwuklik w wiersz lub Enter na aktywnym wierszu otwiera `#match-detail-dialog`. `SzczegolyMeczuController` z `matches.js` pobiera stronę szczegółów i wyświetla jej `[data-match-detail]`, bez ramy i linku powrotu. Kliknięcia w link nie otwierają dodatkowo modalu. Zamknięcie i Escape anulują trwający odczyt, zachowują stan listy i przywracają fokus. Treść modalu ma zakładki „Dane podstawowe”, „Wynik i statystyki” i „Składy”, inicjalizowane przez `ZakladkiMeczuController`. Modal pokazuje ładowanie i błąd pobrania; link nowej karty pozostaje dostępny. Bez obsługi dialogu lub JavaScript działa zwykły link szczegółów.

## Pamięć i czyszczenie filtrów

Klasa `FiltryMeczowController` w [matches.js](../../../static/js/matches.js) obsługuje formularz `[data-match-filters]`. Po poprawnym wyświetleniu listy zapisuje siedem zastosowanych filtrów w `localStorage` pod kluczem `hds.mecze.filtry.v1`. Pamięć dotyczy tej przeglądarki i adresu aplikacji; przetrwa jej zamknięcie. Niezatwierdzone zmiany pól nie są zapisywane.

Wejście na listę bez parametrów przywraca filtry przez przekierowanie JavaScript. Jawne parametry adresu mają pierwszeństwo. Powrót zaczyna się od pierwszej strony i domyślnego sortowania; numer strony, sortowanie i rozmiar strony nie są zapamiętywane. Nieaktualne wartości list wyboru są pomijane. Przed przywróceniem zapis jest usuwany, a udane wyświetlenie zapisuje go ponownie, aby błędny filtr nie powodował powtarzanych przekierowań.

„Wyczyść filtry” prowadzi do listy z pustym `id_sezon`: pokazuje wszystkie mecze, resetuje paginację i sortowanie, usuwa pamięć filtrów, zachowuje ustawienia widoczności kolumn. Bez JavaScript czyszczenie i zwykłe filtrowanie nadal działają; pamięć wymaga JavaScript i dostępnego magazynu przeglądarki.

Testy zachowania pamięci: `node --test tests/javascript/match_filters.test.cjs` (bez dodatkowych zależności ani bazy).

## Runda, kolejka i modal widoczności

Filtry `runda` i `kolejka` są stale dostępne. Wybierają po dokładnej nazwie, niezależnie od sezonowego ID. Słowniki zawierają unikalne, niepuste nazwy ze wszystkich rund i kolejek; nie zawężają się kaskadowo po zmianie sezonu lub rozgrywek. Wybrane filtry łączą się z pozostałymi warunkami, więc kombinacja bez pasujących meczów daje pustą tabelę. Nieznana wartość spoza słownika zwraca 400. Sortowanie i paginacja zachowują oba parametry.

`MeczSQLAlchemyRepository` łączy `mecze.id_kolejka → kolejki.id → kolejki.id_runda → rundy.id` przez LEFT JOIN. Dostarcza `PozycjaListyMeczow.runda` i `.kolejka` (obie `str | None`). Brak nazwy wyświetla `—`; nie usuwa meczu z listy. Ustawienia widoczności nie zmieniają zapytania ani filtrów.

Kolumny znajdują się za Rozgrywkami i są domyślnie ukryte. „Widoczne kolumny” otwiera natywny `<dialog>` z dwoma checkboxami. „Zastosuj” aktualizuje nagłówki i wszystkie komórki wybranej kolumny oraz `colspan` pustego wyniku. „Anuluj”, × i Escape odrzucają niezastosowane zmiany. Modal obsługuje fokus klawiatury; po zamknięciu fokus wraca do przycisku otwierającego.

Klasa `KolumnyMeczowController` w [matches.js](../../../static/js/matches.js) zapisuje wybór w `localStorage` pod kluczem `hds.mecze.kolumny.v1`, wspólnie dla listy meczów w tej przeglądarce i adresie aplikacji. Ustawienia przetrwają filtrowanie, paginację i odświeżenie. Przy zablokowanym magazynie zmiana działa na bieżącej stronie; błędny zapis jest traktowany jak domyślnie ukryte kolumny. Bez JavaScript lub obsługi `dialog.showModal()` przycisk pozostaje ukryty, a filtry działają normalnie.

## Zmiana gospodarza

`MeczPresenter` przez `MeczPolicy` uwzględnia `DaneMeczu.zamiana`: dla wartości `True` przekazuje gościa źródłowego jako gospodarza prezentowanego, gospodarza jako gościa i odwraca wynik `*_full`. Przykład: Wisła Płock — 46 : 19 — MMTS Kwidzyn staje się MMTS Kwidzyn — 19 : 46 — Wisła Płock. Dla `False` i `NULL` zachowuje kolejność. Brak którejkolwiek części wyniku nadal daje `- : -`. Szablon otrzymuje już gotowe nazwy i wynik; nie wykonuje drugiej zamiany. Zmiana dotyczy prezentacji, bez aktualizacji danych w bazie.

## Dane wejściowe

- `filtry`: `FiltryMeczow` (id_sezon opcjonalny, rozgrywki opcjonalny — nazwa, nie ID, id_hala, runda, kolejka, szukaj_druzyny, data_od/data_do, strona, rozmiar_strony, sortowanie) zbudowany przez `MeczFilterForm` z `request.args`.
- `strona`: `StronaMeczowViewModel` (pozycje, liczba_wszystkich, strona, rozmiar_strony) przygotowany przez `MeczPresenter.przygotuj_liste()` z domenowego wyniku `MeczService.pobierz_liste(filtry)`. Każda `PozycjaListyMeczowViewModel` niesie też `sezon` i `rozgrywki` (nazwy, dołączone przez INNER JOIN — `Mecz.id_sezon`/`id_rozgrywki` są NOT NULL).
- `opcje`: `OpcjeFiltrowMeczow` (sezony: `list[OpcjaWyboru]`; rozgrywki: `list[str]`, unikalne nazwy; hale: `list[OpcjaWyboru]`; rundy i kolejki: `list[str]`) zwrócone przez `SlownikiMeczowService.pobierz_opcje(id_sezon)`, użyte do wypełnienia `<select>` w `formularz`.
- `formularz`: instancja `MeczFilterForm` z ustawionymi `choices`, renderowana bezpośrednio w Jinja2 (`{{ formularz.id_sezon() }}` itd.) — pola same wiedzą, która opcja jest wybrana. Pole `data_meczu` renderuje się bez placeholdera — na wyraźne polecenie użytkownika nie podpowiadamy formatu w samym polu (format tłumaczy komunikat błędu, jeśli wpis jest niepoprawny).
- `sekcja_aktywna="mecze"` dla podświetlenia menu.

Pole tekstowe "Data" przyjmuje częściowy zapis: `2026` (cały rok), `2026-01` (miesiąc) albo `2026-01-15` (dzień) — parsuje je `zakres_z_czesciowej_daty()` w `domain/matches.py`. Niepoprawny format zwraca czytelny błąd 400 po polsku, nie 500.

Pole "Drużyna" wyszukuje **po tożsamości zespołu**, nie po samym tekście: `MeczSQLAlchemyRepository` najpierw znajduje `id_zespol` (z `zespoly_sezony`, po dopasowaniu ILIKE do wpisanego tekstu), a dopiero potem filtruje mecze po tym stałym `id_zespol` — dzięki temu wyszukanie jednej historycznej nazwy (np. "Industria Kielce") znajduje też mecze z sezonów, w których ten sam zespół nazywał się inaczej (np. "Vive Kielce"). **Uwaga na krótkie/generyczne nazwy**: potwierdzone w danych (Zagłębie Lubin), że krótszy fragment nazwy może dodatkowo dopasować inne, niepowiązane zespoły (np. drużyny rezerwowe/młodzieżowe o podobnej nazwie) — to naturalne ograniczenie wyszukiwania po tekście, nie błąd; dłuższa/bardziej specyficzna fraza daje dokładniejszy wynik.

## Powiązania

`MeczListView` (interface/admin/views/match_views.py) → `ZaleznosciZadaniaFactory.utworz_serwis_meczow()` / `.utworz_serwis_slownikow()` → `MeczService`/`SlownikiMeczowService` → `MeczReadRepository`/`SezonReadRepository`/`RozgrywkiReadRepository`/`HalaReadRepository`/`EtapMeczowReadRepository`. Trasa: `GET /administracja/mecze`, endpoint `administracja.lista_meczow` — backend bez przekierowania; brak filtrów oznacza wszystkie mecze, ale JavaScript może przywrócić zapamiętany wybór. Dziedziczy `base.html` i dołącza `partials/pagination.html`. Formularz filtrów to zwykły GET (bez CSRF, bez zmiany stanu) — `MeczFilterForm` (WTForms). Wybór rozgrywek w dropdownie zależy od wybranego sezonu — zmienia się dopiero po ponownym przesłaniu formularza (bez JS, zwykłe przeładowanie strony).

Link sortowania w nagłówku "Data" buduje adres przez `url_for(request.endpoint, **dict(request.args, sortowanie=..., strona=1))` — zachowuje wszystkie bieżące filtry, przełącza tylko kierunek i resetuje stronę na 1 (ten sam wzorzec co paginacja).

Przycisk "Filtruj" jest w osobnym `<div class="pole-przycisku">` wewnątrz siatki `.filters`, ze stylem `align-self:flex-end` (patrz static/css/admin.css) — bez tego CSS Grid rozciąga `<button>` na całą szerokość kolumny.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj kolumny, etykiety i układ filtrów. Nowe dane dodawaj w `PozycjaListyMeczow` i `MeczSQLAlchemyRepository.pobierz_liste`, nie w tym szablonie. Nowe słowniki (opcje do rozwijanych list) dodawaj jako osobne contracts/repositories (wzór: `contracts/season_repository.py` + `infrastructure/repositories/season_repository.py`) i podłączaj przez `SlownikiMeczowService`, nie przez zapytania wprost w widoku. Nowe sortowalne kolumny dodawaj jako kolejny klikalny nagłówek, tym samym wzorcem co "Data" — nie jako pole w panelu filtrów (patrz CODING_STANDARDS, "Listy z filtrami").

## Sprawdzenie zmiany

Sprawdź modal (zapis, anulowanie, Escape, pamięć ustawień, szerokość mobilna), niezależne i łączne filtry rundy/kolejki, brak drużyny/hali/wyniku/sezonu/rozgrywek/rundy/kolejki, pustą listę, paginację z zachowanymi filtrami, sortowanie przez klik w nagłówek (oba kierunki, zachowanie filtrów), każdy format daty (rok/miesiąc/dzień) i niepoprawny format daty (400), wyszukiwanie po fragmencie nazwy drużyny w więcej niż jednym sezonie, rozmiar przycisku "Filtruj" i zgodność z prototypem.

## Stan implementacji

Wykonano: `tests/interface/test_matches.py` (brak filtrów zwraca wszystkie mecze, niepoprawny `id_sezon`/`data_meczu` → 400, dane z sezonem/rozgrywkami/halą renderują się poprawnie, pusty wynik, link sortowania obecny i bez widocznego pola `sortowanie`) z `MeczInMemoryRepository`/`SezonInMemoryRepository`/`RozgrywkiInMemoryRepository`/`HalaInMemoryRepository` jako testowymi implementacjami kontraktów. `tests/unit/test_match_filters.py` sprawdza `zakres_z_czesciowej_daty`.

Zweryfikowane integracyjnie **wobec rzeczywistej bazy**:
- `test_szukaj_druzyny_znajduje_zespol_we_wszystkich_sezonach` — wyszukanie po jednej historycznej nazwie zespołu zwraca dokładnie tyle meczów, ile ten zespół rozegrał łącznie (policzone niezależnie po `id_zespol`), czyli obejmuje wszystkie sezony.
- `test_pobierz_nazwy_rozgrywek_sa_unikalne` — `pobierz_nazwy()` nie zwraca duplikatów.
- `test_filtr_rozgrywki_po_nazwie_obejmuje_wiele_sezonow` — dla realnej nazwy występującej w kilku sezonach (np. "I Liga Kobiet": 6 sezonów, 750 meczów) filtr zwraca dokładnie tę liczbę i te sezony.

Sprawdzono też ręcznie w przeglądarce wobec żywej bazy: dropdown "Rozgrywki" nie ma ani jednej powtórzonej nazwy (sprawdzono zliczeniem wystąpień w wygenerowanym HTML), filtr po nazwie "I Liga Kobiet" zwraca 750 wyników z 6 różnych sezonów zgodnie z bezpośrednim zapytaniem kontrolnym; sortowanie po kliknięciu (strzałka zmienia kierunek, adres zawiera `sortowanie=-data`), kolumny Sezon/Rozgrywki z realnymi danymi, brak podpowiedzi w polu daty. Nie sprawdzono: zachowania przy błędzie połączenia z bazą (503) na żywo, kaskadowego odświeżenia listy rozgrywek bez przeładowania strony (celowo brak JS na tym etapie).

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `list.html`. Numery 1–7 oznaczają miejsca opisane w tabeli poniżej. Nagłówek, górne menu, sidebar i stopka pochodzą z `base.html`.

```text
[HD  Handball DataScience / Administracja danych]             wspólna rama
[Start | Dane | Import | Kontrola danych | Logi]              wspólne menu
+-------------------+----------------------------------------------------------+
| Administracja     | [☰ Menu] tylko na wąskim ekranie                        |
| Dane              | [komunikaty, jeżeli są]                                |
| ...               |                                                          |
| Mecze [aktywne]   | (1) Start › Dane › Mecze                                 |
| ...               |     MECZE                                                |
| Import / eksport  |     Zwarta lista meczów. Tabela jest głównym elementem.   |
| Narzędzia         |                                                          |
|                   | (2) FILTRY                                               |
|                   | [Sezon v] [Rozgrywki v] [Runda v] [Kolejka v] [Hala v]                         |
|                   | [Drużyna: tekst] [Data: tekst] [Filtruj] [Wyczyść filtry]                  |
|                   |                                                          |
|                   | (7) [Widoczne kolumny] → modal poniżej
|                   | (3) TABELA                                               |
|                   | ID | Data ▲/▼ | Godz. | Sezon | Rozgrywki |              |
|                   | [Runda] | [Kolejka] | Gospodarz | Wynik | Gość | Hala                          |
|                   | (4) dane kolejnego meczu w tych samych kolumnach          |
|                   |     ...                                                  |
|                   | (5) albo: Brak meczów spełniających wybrane filtry.        |
|                   |                                                          |
|                   | (6) Wyniki od–do z wszystkich    [« Poprzednia] [Następna »]|
+-------------------+----------------------------------------------------------+
[Handball DataScience                                      Flask + PostgreSQL]

(8) Modal po dwukliku: Szczegóły meczu [×]
    [wynik, dane, statystyki, składy — przewijana treść]
    [Otwórz w nowej karcie] [Zamknij]

(7) Modal: Widoczne kolumny                               [×]
    Opis: dodatkowe kolumny nie zmieniają dostępności filtrów
    [ ] Runda
    [ ] Kolejka
                                    [Anuluj] [Zastosuj]
```

Podział filtrów i nagłówków tabeli na dwa wiersze w rysunku służy czytelności. HTML ma jedną tabelę z jedenastoma kolumnami, z których domyślnie widocznych jest dziewięć. Nawiasy przy Rundzie i Kolejce oznaczają opcjonalną widoczność; filtrami steruje siatka CSS. Przycisk „Filtruj” jest ósmym elementem siatki, a „Wyczyść filtry” dziewiątym.

**Zachowanie i warianty:**

- „Filtruj” wysyła GET. `id_sezon`, `rozgrywki`, `runda`, `kolejka` i `id_hala` to listy wyboru; `druzyna` i `data_meczu` to pola tekstowe. Pusty sezon oznacza wszystkie sezony.
- Kliknięcie „Data” przełącza kierunek, zachowuje filtry i ustawia stronę 1. Pozostałe nagłówki nie są linkami sortowania.
- Przy `zamiana=True` kolumny Gospodarz/Wynik/Gość pokazują odwrócone drużyny i wynik.
- Brak terminu, nazwy lub hali jest pokazany jako `—`; brak wyniku jako `- : -`. Wynik jest pogrubiony przez `.score`.
- Pusty wynik obejmuje wszystkie widoczne kolumny (`colspan` od 9 do 11). Paginacja wtedy nie jest renderowana.
- Siatka `.filters` ma 7 kolumn powyżej 1100 px, 4 przy szerokości do 1100 px, 2 do 700 px i 1 do 430 px. Nie wszystkie kolumny muszą być zajęte. Tabela przewija się poziomo we własnym `.table-wrap`.
- Do 920 px sidebar jest początkowo ukryty. Przycisk „☰ Menu” przełącza go przez wspólny JS.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| 1. Ścieżka, tytuł i opis | [list.html](list.html) | `.pagehead`, `.crumb`, `<h1>` i `<p>`; tytuł karty w bloku `tytul`. |
| 2. Etykiety, kolejność i przycisk filtrów | [list.html](list.html) | Sekcja „Filtry”, `<form method="get">`, `.filters` i `.pole-przycisku`. |
| 2. Pamięć i czyszczenie | [matches.js](../../../static/js/matches.js), [list.html](list.html) | `FiltryMeczowController`, `[data-match-filters]`, link „Wyczyść filtry”. |
| 2. Rodzaj pola, walidacja i konwersja | [match_filters.py](../../../admin/forms/match_filters.py) | `MeczFilterForm` i `do_filtrow()`. |
| 2. Opcje list rozwijanych | [match_views.py](../../../admin/views/match_views.py) | `MeczListView.get()` ustawia `choices`; źródła opcji zbiera `SlownikiMeczowService`. |
| 3. Kolumny i kierunek sortowania | [list.html](list.html) | `<thead>`, link w nagłówku „Data” i odpowiadające im `<td>` w `<tbody>`. Przy zmianie liczby kolumn popraw również `colspan` pustego wiersza. |
| 4. Pobierane dane i wynik meczu | [match_repository.py](../../../../infrastructure/repositories/match_repository.py) | `_pobierz_liste()` mapuje źródłowe dane; `MeczPresenter.przygotuj_liste()` przygotowuje nazwy, wynik i dopisek w modelu widoku. |
| 7. Modal i opcjonalne kolumny | [list.html](list.html), [matches.js](../../../static/js/matches.js) | `#match-columns-dialog`, `[data-columns-open]`, `[data-match-column]`, `KolumnyMeczowController`; styl `.match-columns-dialog` i `.column-choice` w CSS. |
| 2/4. Nazwy rund i kolejek | [match_stage_repository.py](../../../../infrastructure/repositories/match_stage_repository.py) | Słowniki w `EtapMeczowSQLAlchemyRepository`; filtry i złączenia tabeli w `MeczSQLAlchemyRepository`. |
| 5. Treść pustego wyniku | [list.html](list.html) | Gałąź `{% else %}` pętli po `strona.pozycje`. |
| 6. Licznik i przyciski stron | [pagination.html](../../partials/pagination.html) | Wspólny fragment; jego opis jest w `partials/pagination.md`. |
| Odstępy, szerokości i responsywność | [admin.css](../../../static/css/admin.css) | `.pagehead`, `.filters`, `.pole-przycisku`, `.table-wrap`, `th`, `td`, `.score` oraz zapytania `@media`. |
| Nagłówek, sidebar i stopka | [base.md](../../base.md) | Wspólny układ opisany osobno; lista meczów wypełnia tylko blok `tresc`. |
| 8. Podgląd meczu | [list.html](list.html), [matches.js](../../../static/js/matches.js), [detail.md](detail.md) | #match-detail-dialog, SzczegolyMeczuController, [data-match-detail]. |
| Prezentacja listy | [match_presenter.py](../../../presenters/match_presenter.py), [matches.py](../../../view_models/matches.py) | `MeczPresenter`, `StronaMeczowViewModel`, `PozycjaListyMeczowViewModel`. |
