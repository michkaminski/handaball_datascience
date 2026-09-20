# Karta zawodnika

Status: zaimplementowane Profil, Sezony i drużyny oraz Mecze. Trasa `GET /administracja/zawodnicy/<id_zawodnik>`, endpoint `administracja.szczegoly_zawodnika`. Widok odczytu bez edycji. Wzorzec: `player_detail.html` prototypu v6 i działające szczegóły meczu.

## Otwieranie

Przycisk „Szczegóły” na liście otwiera pełną kartę w nowej karcie przeglądarki. Dwuklik lub Enter na wierszu otwiera natywny modal. Kliknięcie linku w wierszu nie otwiera dodatkowo modalu. Modal pobiera ten sam endpoint, wycina `[data-player-detail]` i usuwa przycisk powrotu do listy. Escape, × i „Zamknij” zamykają okno oraz przywracają fokus na wiersz.

Filtry, czyszczenie, sortowanie i paginacja działają także w modalu: pobierają nowy fragment bez opuszczania listy. „Otwórz w nowej karcie” zachowuje aktualne filtry, stronę i zakładkę. Nowsze żądanie anuluje poprzednie; zamknięcie modalu anuluje oczekujące pobranie. Błąd pobrania daje komunikat i pozostawia link do pełnej karty.

## Zakładki i dane

### Profil

Imię i nazwisko, ID, data urodzenia, wzrost, waga i opcjonalne zdjęcie ze słownika `zawodnicy`. Brak zdjęcia lub błąd jego wczytania jest obsłużony tekstem. Akceptowane są wyłącznie adresy HTTP/HTTPS; obraz nie wysyła nagłówka Referer. Brak daty oznacza „—”. Wzrost i waga pochodzą osobno z najnowszego, według porządku historii, niepustego zapisu `sklady`. Nie wyznaczamy bieżącego numeru, pozycji ani klubu.

### Sezony i drużyny

Tabela: Sezon, Drużyna, Rozgrywki, Numer, Pozycja, Bramki, Karne i Kary. Jeden rekord składu jest rozwijany do osobnego wiersza dla każdych rozgrywek, w których zawodnik ma przypisane statystyki meczowe dla tej drużyny. Skład bez takich wpisów pozostaje jednym wierszem z „—”. Nazwa i sezon pochodzą z `zespoly_sezony` oraz `sezony`. Pozycja pochodzi z `sklady.pozycja_nazwa`, a przy jej braku z `pozycje.nazwa`. Numer 0, jeśli zapisany, pozostaje zerem.

Podsumowanie powstaje z `mecze_zawodnicy` połączonych z `mecze` i `rozgrywki`, grupowanych według sezonu, drużyny wynikającej ze strony `gosp`/`gosc` oraz nazwy rozgrywek. Bramki to suma znanych `bramki`; karne pokazują sumę `karne_bramki/karne_liczba`; kary pokazują sumy `dwie_minuty`, upomnień i dyskwalifikacji. `NULL` pozostaje „—”, jeżeli w grupie nie ma żadnej znanej wartości danego pola. Wpisy strony `inne` nie mają jednoznacznej drużyny i nie trafiają do tego zestawienia.

Sortowanie historii: rok rozpoczęcia sezonu malejąco, ID sezonu malejąco, nazwa i identyfikator migawki drużyny. Historia pokazuje wszystkie istniejące rekordy składów sezonowych zawodnika; filtry meczów jej nie zawężają. To nie jest historia wszystkich wersji JSON ani rejestr dat transferów.

### Mecze

Proste filtry: sezon (lista nazw), rozgrywki (unikalne nazwy), przeciwnik (tekst). Przeciwnik rozwiązywany jest przez historyczne nazwy do ID zespołu; następnie dobierany według strony wpisu zawodnika. `inne` nie przypisuje przeciwnika. Puste filtry oznaczają cały dostępny zakres.

Paginacja domyślnie po 20 różnych meczów, rozmiar strony 1–100. Sortowanie daty przez nagłówek, domyślnie najnowsze; ID rozstrzyga remisy, brak terminu na końcu. Termin to data faktyczna lub, przy jej braku, propozycja. Filtrowanie i sortowanie resetują stronę do 1, paginacja zachowuje filtry i zakładkę Mecze. Numer ponad zakres jest ograniczany do ostatniej strony.

Kolumny: Data, Sezon / rozgrywki, Drużyna (z numerem i pozycją z meczu), Przeciwnik, Wynik, Bramki, Karne, Kary, Akcje. Wynik w kolejności gospodarz–gość, zgodnie z presenterem meczu i regułą zamiany stron. Nazwy obu drużyn przy wyniku wyjaśniają kolejność; drużyna zawodnika i przeciwnik zachowują źródłową parę skład–zespół.

Karne pokazują trafione/próby, serie osobno. Nieznana część ułamka pozostaje „—”, np. `0/—`. Kary pokazują zapisane `dwie_minuty` pod etykietą „2 min”, upomnienie i dyskwalifikację; nie przeliczamy pola na minuty. Wpis w składzie nie dowodzi występu na boisku.

Zapytanie wybiera mecze przez EXISTS, zlicza je i paginuje przed pobraniem wpisów. Wpisy zawodnika są pobierane jednym dodatkowym zapytaniem dla bieżącej strony, bez N+1. Kilka stron jednego meczu pozostaje jednym meczem w paginacji; źródłowe statystyki pokazane są osobno z komunikatem o kilku stronach. Nie są sumowane. „Szczegóły meczu” prowadzą do istniejącej karty meczu w nowej karcie przeglądarki.

## Kontrakt i powiązania

- `szczegoly`: `SzczegolyZawodnikaViewModel`: id_zawodnik, nazwa, data_urodzenia, foto_url, najnowszy dostępny wzrost i wagę oraz sezony z podsumowaniami rozgrywek.
- `strona`: `StronaMeczowZawodnikaViewModel`: pozycje, liczba_wszystkich, strona i rozmiar_strony. Każda pozycja zawiera model meczu, termin, wpisy i flagę wiele_stron.
- `formularz`: `MeczeZawodnikaFilterForm`; `filtry`: `FiltryMeczowZawodnika`.
- `aktywna_zakladka`: profil / sezony / mecze. Bez parametrów profil; przy parametrach meczów bez jawnej zakładki — mecze.
- `parametry_paginacji`: bieżące parametry GET z nadpisanym prawidłowym id_zawodnik i zakladka=mecze, używane przez wspólną paginację.
- `sekcja_aktywna="zawodnicy"`: sidebar Zawodnicy i górna sekcja Dane.

`ZawodnikSzczegolyView` → `SzczegolyZawodnikaService` → `SzczegolyZawodnikaReadRepository` → `SzczegolyZawodnikaSQLAlchemyRepository`. `SzczegolyZawodnikaPresenter` korzysta z istniejącego `MeczPresenter` i `MeczFormat`; zależności składa `ZaleznosciZadaniaFactory`. ORM nie opuszcza repozytorium. Odczyt zachowuje istniejące READ ONLY i ROLLBACK na końcu kontekstu.

Brak zawodnika daje 404, błąd odczytu 503, błędne filtry 400. Brak historii lub pasujących meczów daje osobny komunikat i nie usuwa profilu. Nazwy są escapowane przez Jinja2. Bez JavaScript wszystkie trzy sekcje są widoczne i formularz/paginacja działają jako zwykły GET.

## Weryfikacja

Testy: `tests/interface/test_player_details.py`, `tests/unit/test_player_detail_repository.py` i `tests/javascript/player_details.test.cjs`. Sprawdzają historię i braki, błędy, walidację, stronę 2, parametry linków, zamianę stron meczu, oddzielne wpisy i brak zamiany NULL karnych na zero.

W Edge na izolowanych danych sprawdzono przycisk, dwuklik, Enter, Escape, przywrócenie fokusu, zakładki, historię, stronę 2 w modalu, filtrowanie i czyszczenie bez opuszczania listy oraz pełną kartę. Kontrola 1440 px i 390 px: bez poziomego przewijania dokumentu; tabela na telefonie przewija się we własnym kontenerze.

Po odświeżeniu lokalnego serwera potwierdzono GET listy i karty z rzeczywistymi danymi (200), w tym pierwszą i drugą stronę zawodnika z 551 meczami: 1–20 i 21–40. To sprawdzenie działania odczytu, nie pełny audyt historycznego importu ani pomiar kompletności wszystkich pól. Bazy nie zmieniano.

## Dalszy plan

Statystyki (agregaty, wykresy, najlepsze mecze), Klasyfikacje (`strzelcy`) oraz Źródła i jakość (wersje składów, konflikty i braki) pozostają propozycjami; nie mają nieczynnych zakładek w interfejsie. Przed obliczeniami trzeba potwierdzić mianowniki, kompletność i znaczenie pól. Nie ma potwierdzonych danych do minut gry, asyst czy ogólnej skuteczności rzutów.

## Układ tekstowy i mapa zmian

Rzeczywisty układ `detail.html`, wspólny dla pełnej karty i modalu:

```text
[pełna karta: rama base.html; modal: nagłówek Szczegóły zawodnika / ×]
Start › Dane › Zawodnicy › Szczegóły
IMIĘ NAZWISKO
Karta zawodnika #ID
[Powrót do listy] — tylko w pełnej karcie

[Profil] [Sezony i drużyny] [Mecze]

Profil:
  [zdjęcie / brak]  ID / Imię i nazwisko / Data urodzenia / Wzrost / Waga
Sezony i drużyny:
  Sezon | Drużyna | Rozgrywki | Numer | Pozycja | Bramki | Karne | Kary
  [rekordy składów rozwinięte według rozgrywek / brak danych]
Mecze:
  [Sezon v] [Rozgrywki v] [Przeciwnik] [Filtruj] [Wyczyść filtry]
  Data ↕ | Sezon/rozgrywki | Drużyna | Przeciwnik | Wynik |
  Bramki | Karne | Kary | Szczegóły meczu
  [mecze bieżącej strony / pusty wynik]
  Wyniki od–do z wszystkich   [« Poprzednia] [Następna »]

[modal: Otwórz w nowej karcie / Zamknij]
```

Z JavaScript widoczna jest jedna zakładka. Na wąskim ekranie filtry układają się pionowo, tabele przewijają w swoich kontenerach, a modal ma przewijaną treść i osobną stopkę. Zawinięcie tabeli meczów w rysunku służy czytelności.

### Mapa zmian

| Element | Plik | Blok / selektor / dane |
| --- | --- | --- |
| Nagłówek i profil | [detail.html](detail.html) | tytul, tresc, .pagehead, .player-profile, szczegoly. |
| Dane sezonowe | [detail.html](detail.html), [repozytorium](../../../../infrastructure/repositories/player_detail_repository.py) | .player-season-table, pobierz_szczegoly(), _pobierz_statystyki_sezonowe(), modele SkladSezonowy/Pozycja/MeczZawodnik. |
| Filtry i walidacja | [player_match_filters.py](../../../admin/forms/player_match_filters.py) | MeczeZawodnikaFilterForm; do_filtrow(). |
| Tabela meczów | [detail.html](detail.html), [repozytorium](../../../../infrastructure/repositories/player_detail_repository.py) | .player-matches-table, pobierz_mecze(), _zapytanie_meczow(). |
| HTTP i parametry | [player_detail_views.py](../../../admin/views/player_detail_views.py) | ZawodnikSzczegolyView.get(), parametry_paginacji. |
| Formatowanie | [player_detail_presenter.py](../../../presenters/player_detail_presenter.py) | SzczegolyZawodnikaPresenter i modele w interface/view_models/player_details.py. |
| Zakładki i modal | [player_details.js](../../../static/js/player_details.js) | ZakladkiZawodnikaController, SzczegolyZawodnikaController, data-player-*. |
| Przycisk i dwuklik | [list.html](list.html), [list.md](list.md) | data-player-href, #player-detail-dialog, link Szczegóły. |
| Paginacja | [pagination.html](../../partials/pagination.html) | parametry_paginacji, strona. |
| Style i responsywność | [admin.css](../../../static/css/admin.css) | .match-detail-dialog, .match-tabs, .player-*, data-player-panel. |
