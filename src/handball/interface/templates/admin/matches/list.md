# Lista meczów

Status: etap 4 ukończony i trzykrotnie rozszerzony na wyraźne polecenie użytkownika: (1) filtry bez surowych ID, wyszukiwanie po drużynie/dacie i kolumna Hala; (2) sortowanie przez klik w nagłówek kolumny (zamiast pola w filtrach), kolumny Sezon/Rozgrywki, usunięcie podpowiedzi formatu w polu daty, wyszukiwanie drużyny po tożsamości zespołu (a nie tylko tekście nazwy); (3) filtr Rozgrywki pokazuje każdą nazwę tylko raz (zamiast raz na sezon) i po wyborze pokazuje mecze ze wszystkich sezonów tej nazwy. Szablon `list.html` istnieje.

Docelowy szablon względem katalogu szablony: `admin/matches/list.html`.

## Przeznaczenie

Tabela meczów i zwarte filtry na podstawie matches.html prototypu v6. Kolumny: ID, Data (klikalny nagłówek sortujący), Godz., Sezon, Rozgrywki, Gospodarz, Wynik, Gość, Hala. Kol./Status/Akcje z prototypu wciąż nie są dostarczane przez `PozycjaListyMeczow` — świadomie odłożone.

Filtry sezonu, rozgrywek i hali są rozwijanymi listami z nazwami (nie polami liczbowymi z ID) — użytkownik nigdy nie wpisuje ani nie widzi surowego identyfikatora bazy. Filtr sezonu jest opcjonalny: pusty wybór ("Wszystkie") przeszukuje wszystkie sezony.

**Filtr Rozgrywki filtruje po nazwie, nie po `id_rozgrywki`.** Ta sama nazwa rozgrywek (np. "I Liga Kobiet") ma osobny wiersz w tabeli `rozgrywki` w każdym sezonie, w którym się odbyły — bez tej zmiany lista rozwijana pokazywałaby tę samą nazwę wielokrotnie (raz na sezon). `RozgrywkiSQLAlchemyRepository.pobierz_nazwy()` zwraca `DISTINCT` nazwy, a `MeczSQLAlchemyRepository` filtruje przez `Rozgrywki.nazwa == filtry.rozgrywki` (dokładne dopasowanie, bo nazwa pochodzi z zamkniętej listy rozwijanej, nie z wolnego tekstu) — to samo złączenie z `Rozgrywki`, które i tak istnieje do wyświetlenia kolumny "Rozgrywki". Dzięki temu wybór jednej nazwy pokazuje mecze ze wszystkich sezonów tej nazwy, chyba że dodatkowo zawężono filtrem Sezon.

**Sortowanie jest w nagłówku kolumny "Data", nie w panelu filtrów** — to ustalona konwencja dla wszystkich list z filtrami w tym projekcie, patrz [CODING_STANDARDS](../../../../../../docs/CODING_STANDARDS.md), sekcja "Listy z filtrami". Panel filtrów nie ma już pola "Sortowanie".

## Dane wejściowe

- `filtry`: `FiltryMeczow` (id_sezon opcjonalny, rozgrywki opcjonalny — nazwa, nie ID, id_hala, szukaj_druzyny, data_od/data_do, strona, rozmiar_strony, sortowanie) zbudowany przez `MeczFilterForm` z `request.args`.
- `strona`: `StronaMeczow` (pozycje, liczba_wszystkich, strona, rozmiar_strony) zwrócony przez `MeczService.pobierz_liste(filtry)`. Każda `PozycjaListyMeczow` niesie też `sezon` i `rozgrywki` (nazwy, dołączone przez INNER JOIN — `Mecz.id_sezon`/`id_rozgrywki` są NOT NULL).
- `opcje`: `OpcjeFiltrowMeczow` (sezony: `list[OpcjaWyboru]`; rozgrywki: `list[str]`, unikalne nazwy; hale: `list[OpcjaWyboru]`) zwrócone przez `SlownikiMeczowService.pobierz_opcje(id_sezon)`, użyte do wypełnienia `<select>` w `formularz`.
- `formularz`: instancja `MeczFilterForm` z ustawionymi `choices`, renderowana bezpośrednio w Jinja2 (`{{ formularz.id_sezon() }}` itd.) — pola same wiedzą, która opcja jest wybrana. Pole `data_meczu` renderuje się bez placeholdera — na wyraźne polecenie użytkownika nie podpowiadamy formatu w samym polu (format tłumaczy komunikat błędu, jeśli wpis jest niepoprawny).
- `sekcja_aktywna="mecze"` dla podświetlenia menu.

Pole tekstowe "Data" przyjmuje częściowy zapis: `2026` (cały rok), `2026-01` (miesiąc) albo `2026-01-15` (dzień) — parsuje je `zakres_z_czesciowej_daty()` w `domain/matches.py`. Niepoprawny format zwraca czytelny błąd 400 po polsku, nie 500.

Pole "Drużyna" wyszukuje **po tożsamości zespołu**, nie po samym tekście: `MeczSQLAlchemyRepository` najpierw znajduje `id_zespol` (z `zespoly_sezony`, po dopasowaniu ILIKE do wpisanego tekstu), a dopiero potem filtruje mecze po tym stałym `id_zespol` — dzięki temu wyszukanie jednej historycznej nazwy (np. "Industria Kielce") znajduje też mecze z sezonów, w których ten sam zespół nazywał się inaczej (np. "Vive Kielce"). **Uwaga na krótkie/generyczne nazwy**: potwierdzone w danych (Zagłębie Lubin), że krótszy fragment nazwy może dodatkowo dopasować inne, niepowiązane zespoły (np. drużyny rezerwowe/młodzieżowe o podobnej nazwie) — to naturalne ograniczenie wyszukiwania po tekście, nie błąd; dłuższa/bardziej specyficzna fraza daje dokładniejszy wynik.

## Powiązania

`MeczListView` (interface/admin/views/match_views.py) → `ZaleznosciZadaniaFactory.utworz_serwis_meczow()` / `.utworz_serwis_slownikow()` → `MeczService`/`SlownikiMeczowService` → `MeczReadRepository`/`SezonReadRepository`/`RozgrywkiReadRepository`/`HalaReadRepository`. Trasa: `GET /administracja/mecze`, endpoint `administracja.lista_meczow` — **bez przekierowania**, brak `id_sezon` w adresie oznacza wszystkie sezony. Dziedziczy `base.html` i dołącza `partials/pagination.html`. Formularz filtrów to zwykły GET (bez CSRF, bez zmiany stanu) — `MeczFilterForm` (WTForms). Wybór rozgrywek w dropdownie zależy od wybranego sezonu — zmienia się dopiero po ponownym przesłaniu formularza (bez JS, zwykłe przeładowanie strony).

Link sortowania w nagłówku "Data" buduje adres przez `url_for(request.endpoint, **dict(request.args, sortowanie=..., strona=1))` — zachowuje wszystkie bieżące filtry, przełącza tylko kierunek i resetuje stronę na 1 (ten sam wzorzec co paginacja).

Przycisk "Filtruj" jest w osobnym `<div class="pole-przycisku">` wewnątrz siatki `.filters`, ze stylem `align-self:flex-end` (patrz static/css/admin.css) — bez tego CSS Grid rozciąga `<button>` na całą szerokość kolumny.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj kolumny, etykiety i układ filtrów. Nowe dane dodawaj w `PozycjaListyMeczow` i `MeczSQLAlchemyRepository.pobierz_liste`, nie w tym szablonie. Nowe słowniki (opcje do rozwijanych list) dodawaj jako osobne contracts/repositories (wzór: `contracts/season_repository.py` + `infrastructure/repositories/season_repository.py`) i podłączaj przez `SlownikiMeczowService`, nie przez zapytania wprost w widoku. Nowe sortowalne kolumny dodawaj jako kolejny klikalny nagłówek, tym samym wzorcem co "Data" — nie jako pole w panelu filtrów (patrz CODING_STANDARDS, "Listy z filtrami").

## Sprawdzenie zmiany

Sprawdź brak drużyny/hali/wyniku/sezonu/rozgrywek, pustą listę, paginację z zachowanymi filtrami, sortowanie przez klik w nagłówek (oba kierunki, zachowanie filtrów), każdy format daty (rok/miesiąc/dzień) i niepoprawny format daty (400), wyszukiwanie po fragmencie nazwy drużyny w więcej niż jednym sezonie, rozmiar przycisku "Filtruj" i zgodność z prototypem.

## Stan implementacji

Wykonano: `tests/interface/test_matches.py` (brak filtrów zwraca wszystkie mecze, niepoprawny `id_sezon`/`data_meczu` → 400, dane z sezonem/rozgrywkami/halą renderują się poprawnie, pusty wynik, link sortowania obecny i bez widocznego pola `sortowanie`) z `MeczInMemoryRepository`/`SezonInMemoryRepository`/`RozgrywkiInMemoryRepository`/`HalaInMemoryRepository` jako testowymi implementacjami kontraktów. `tests/unit/test_match_filters.py` sprawdza `zakres_z_czesciowej_daty`.

Zweryfikowane integracyjnie **wobec rzeczywistej bazy**:
- `test_szukaj_druzyny_znajduje_zespol_we_wszystkich_sezonach` — wyszukanie po jednej historycznej nazwie zespołu zwraca dokładnie tyle meczów, ile ten zespół rozegrał łącznie (policzone niezależnie po `id_zespol`), czyli obejmuje wszystkie sezony.
- `test_pobierz_nazwy_rozgrywek_sa_unikalne` — `pobierz_nazwy()` nie zwraca duplikatów.
- `test_filtr_rozgrywki_po_nazwie_obejmuje_wiele_sezonow` — dla realnej nazwy występującej w kilku sezonach (np. "I Liga Kobiet": 6 sezonów, 750 meczów) filtr zwraca dokładnie tę liczbę i te sezony.

Sprawdzono też ręcznie w przeglądarce wobec żywej bazy: dropdown "Rozgrywki" nie ma ani jednej powtórzonej nazwy (sprawdzono zliczeniem wystąpień w wygenerowanym HTML), filtr po nazwie "I Liga Kobiet" zwraca 750 wyników z 6 różnych sezonów zgodnie z bezpośrednim zapytaniem kontrolnym; sortowanie po kliknięciu (strzałka zmienia kierunek, adres zawiera `sortowanie=-data`), kolumny Sezon/Rozgrywki z realnymi danymi, brak podpowiedzi w polu daty. Nie sprawdzono: zachowania przy błędzie połączenia z bazą (503) na żywo, kaskadowego odświeżenia listy rozgrywek bez przeładowania strony (celowo brak JS na tym etapie).
