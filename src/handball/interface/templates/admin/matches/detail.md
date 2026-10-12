# Szczegóły meczu

Status: zaimplementowany szablon [detail.html](detail.html), oparty na ekranie match_detail.html prototypu v6.

## Przeznaczenie i powiązania

Przycisk „Szczegóły” na liście otwiera pełną stronę w nowej karcie. Dwuklik w wiersz lub Enter na wierszu pobiera tę samą stronę do natywnego modalu na liście. Kontroler pobiera wyłącznie element `[data-match-detail]` i usuwa z podglądu link powrotu. Modal nie kopiuje nagłówka, menu i stopki. Zamknięcie przyciskiem lub Escape zachowuje listę i filtry oraz przywraca fokus do wiersza. Nieudany odczyt pokazuje komunikat z możliwością otwarcia nowej karty.

Przepływ: `MeczSzczegolyView` → `StatystykiMeczuService` → `MeczReadRepository` (szczegóły i składy) oraz `FormaMeczuReadRepository` (forma obu drużyn) → `StatystykiMeczuCalculator`; następnie `MeczPresenter` (z `SkladMeczuPresenter`, `MeczFormat` i domenowym `MeczPolicy`) tworzy `szczegoly`, a `StatystykiMeczuPresenter` tworzy `statystyki` → szablon. Trasa: `GET /administracja/mecze/<id_mecz>`. Brak meczu daje 404, błąd odczytu 503. Dla meczu z wynikiem pod paskiem powrotu jest przyciski „Raport meczu (PDF, A4)” i „Raport skrócony (PDF)” (`.match-report-bar`, nowa karta) do [report_pdf.md](report_pdf.md); w modalu listy przycisk pozostaje. Pełna strona dziedziczy `base.html`.

## Dane wejściowe

`szczegoly: SzczegolyMeczuViewModel` zawiera nazwy gospodarza i gościa, ich `id_gospodarz` i `id_gosc` (`int | None`), wynik nagłówka, wynik do przerwy, dopisek wyniku, rozgrywki, kolejkę, termin, halę, status, pary danych podstawowych, statystyki porównawcze i trzy listy `ZawodnikMeczuViewModel`: `sklad_gospodarz`, `sklad_gosc`, `sklad_inne`. `statystyki: StatystykiMeczuViewModel` zasila zakładkę „Analiza meczu” (opis niżej). `sekcja_aktywna="mecze"` podświetla nawigację.

Zawodnik zawiera numer koszulki, nazwę, pozycję, bramki, kary dwuminutowe, upomnienie, dyskwalifikację, KD, wyjście, karne i serię karnych. Repozytorium dostarcza typowane dane domenowe; teksty i wyróżnienia przygotowują presentery. Szablon nie wykonuje zapytań. Dane tekstowe są automatycznie escapowane przez Jinja2.

Repozytorium i serwis zwracają `SzczegolyMeczu` z `DaneMeczu` oraz składami `ZawodnikMeczu`. Numery koszulek i bramki są typu `int | None`, daty mają typ `datetime | None`, a flagi `bool | None`. `ZaleznosciZadaniaFactory.utworz_presenter_meczow()` składa zależności presentera. Dopiero `MeczPresenter.przygotuj_szczegoly()` tworzy model widoku opisany powyżej.

## Kolejność, kolory i najlepsi strzelcy

Składy nie są zamieniane przy `zamiana=true`: `mecze_zawodnicy.strona` wskazuje już stronę po zamianie, więc `sklad_gospodarz` (wpisy `gosp`) należy do wyświetlanego gospodarza. `MeczPolicy.para` odwraca tylko nazwy drużyn, ich identyfikatory (`mecze.id_zespol_gosp`/`id_zespol_gosc` w `DaneMeczu`) i wyniki. Uzasadnienie i dane: [DATA](../../../../../../docs/DATA.md#strona-wpisów-zawodników-przy-zamiana--2026-09-23).


`SkladMeczuPresenter` grupuje składy alfabetycznie według źródłowego tekstu pozycji (bez rozróżniania wielkości liter), następnie według liczbowego numeru koszulki i nazwy. Nie zgaduje znaczenia skrótów. Brak pozycji trafia na koniec i pozostaje bez koloru. Różne pozycje mają delikatne pastelowe tła; ta sama pozycja ma ten sam kolor w obu zespołach danego meczu. Kolor może różnić się między meczami o innym zestawie pozycji.

Model widoku zawodnika zawiera `kolor_pozycji: int | None` i `najlepszy_strzelec: bool`. Wyróżnia komórkę „Br.” u każdego zawodnika z największą dodatnią liczbą bramek osobno w każdej drużynie, także przy remisie. Osoby z `sklad_inne` nie uczestniczą w porównaniu. Nie dodaje ponownie bramek z karnych ani z serii karnych. Zera i braki nie otrzymują wyróżnienia. Przy niepełnych danych maksimum dotyczy dostępnych statystyk zawodników.

Czerwone tło jest uzupełnione pogrubieniem, opisem przy najechaniu, etykietą dostępną dla czytnika i legendą pod wszystkimi tabelami zakładki „Składy”. Puste składy pokazują „Brak danych o składzie.”. Pozostałe osoby są wyświetlane tylko przy niepustej liście.

## Okno zawodnika

Nazwisko w składzie jest linkiem do karty zawodnika (`a[data-player-modal-link]`, `id_zawodnik` z `mecze_zawodnicy` przez `ZawodnikMeczu` i `ZawodnikMeczuViewModel`). Pojedyncze kliknięcie otwiera kartę w oknie modalnym `dialog[data-player-modal-dialog]`, umieszczonym wewnątrz `[data-match-detail]`, więc działa także wtedy, gdy szczegóły meczu są już w modalu listy. Okno leży nad oknem meczu, a Escape zamyka najpierw okno zawodnika. Dwuklik otwiera kartę w nowej karcie. Kliknięcie jest opóźnione o 250 ms, żeby odróżnić je od dwukliku. Enter otwiera okno od razu. Ctrl, Shift, Alt i środkowy przycisk zostawiają zwykłe zachowanie przeglądarki, a bez JavaScriptu link otwiera kartę w nowej karcie.

Mechanika jest wspólna z kartą drużyny: `LinkiZawodnikowController` i `OknoZawodnikaController` w [player_details.js](../../../static/js/player_details.js), eksportowane jako `HandballZawodnik`. Kolejność skryptów opisuje sekcja „Okno drużyny”.

## Okno drużyny

Nazwy gospodarza i gościa w nagłówku wyniku są linkami `a.team-link[data-team-modal-link]` do `administracja.szczegoly_druzyny` (makro `nazwa_druzyny`). Pojedyncze kliknięcie otwiera kartę drużyny w oknie `dialog[data-team-modal-dialog]` wewnątrz `[data-match-detail]`, a dwuklik otwiera ją w nowej karcie. Opóźnienie 250 ms, Enter, modyfikatory i zachowanie bez JavaScriptu działają tak samo jak w oknie zawodnika. Drużyna bez identyfikatora pozostaje zwykłym tekstem.

Okno używa istniejących `LinkiDruzynController` i `OknoDruzynyController` z [classification_details.js](../../../static/js/classification_details.js) (`HandballKlasyfikacja`), tych samych co w tabelach ligowych. Okno pobiera `[data-team-detail]`, uruchamia zakładki drużyny (`team_details.js`) i okno zawodnika, a filtry, sortowanie i paginację karty wczytuje w tym samym oknie. Kolejność skryptów na stronie i liście meczów: `goal_charts.js`, `player_details.js`, `team_details.js`, `classification_details.js`, `matches.js`.

## Analiza meczu

Zakładka `#match-panel-analysis` pokazuje statystyki liczone w Pythonie (`handball.domain.match_statistics`):

- **Wnioski** — do trzech zdań z `WnioskiMeczuGenerator`, w kolejności: rozstrzygnięcie remisu (dogrywka, seria karnych), przebieg (odrobiona strata z przerwy albo lepsza druga połowa), najlepszy strzelec meczu z udziałem w bramkach drużyny (pomijany przy ex aequo), rzuty karne, wyraźna różnica kar 2 min (co najmniej 2).
- **Porównanie drużyn** — tabela lustrzana: bramki, do przerwy, druga połowa, rzuty karne, skuteczność karnych, czasy drużyny (liczba i minuty, `00:` w czasie jest obcinane), kary 2 min, upomnienia, dyskwalifikacje. Wiersz z brakiem obu wartości jest pomijany. Kary i karne drużyny liczone są z sumy zawodników tylko wtedy, gdy mecz ma indywidualne bramki; brak danych meczu dla karnych jest uzupełniany sumą zawodników ze znaną liczbą karnych. Pod etykietą jest pasek `.compare-bar` z udziałem gospodarza (`--home-share`), a pole przewagi (`td.lead`) dostaje tylko drużyna lepsza w bramkach lub skuteczności karnych. Liczby w tabeli są tekstowym odpowiednikiem paska.
- **Najlepsi strzelcy** — do pięciu zawodników każdej drużyny z bramkami z karnych; sortowanie po bramkach, potem nazwisku. Przy braku indywidualnych bramek: „Brak indywidualnych statystyk bramek.”.
- **Forma w sezonie** — ostatnie 5 rozegranych meczów każdej drużyny w sezonie analizowanego meczu, do tego meczu włącznie (`data_faktyczna` nie późniejsza), bez walkowerów i meczów wycofanych, we wszystkich rozgrywkach sezonu. Kafelek: W/R/P według wyniku po 60 minutach (kolor i litera), wynik z perspektywy drużyny, dopisek rozstrzygnięcia („po dogrywce a:b” albo „k. a:b”), rywal (`vs` u siebie, `@` na wyjeździe), data i miejsce. Analizowany mecz ma ramkę `.current` i dopisek „ten mecz”. Nad listą bilans W/R/P i bramki z pokazanych meczów.

Mecz bez wyniku pokazuje tylko notatkę i formę sprzed meczu. Nazwy drużyn są oczyszczane ze spacji na końcu (dane źródłowe je zawierają). `u_siebie` uwzględnia `zamiana` tak samo jak zapowiedź meczu.

## Zakładki

Pod nagłówkiem meczu są cztery zakładki: „Dane podstawowe”, „Analiza meczu”, „Wynik i statystyki”, „Składy”. Pierwsza jest domyślna przy każdym otwarciu. Wynik i metadane meczu pozostają nad zakładkami. Zakładka składów obejmuje obie drużyny, opcjonalne pozostałe osoby i opis kolorów na samym dole.

`ZakladkiMeczuController` w [matches.js](../../../static/js/matches.js) działa zarówno na pełnej stronie, jak i po załadowaniu fragmentu do modalu. Przyciski mają role tab, panelom nadawana jest rola tabpanel, a aria-selected i tabindex są aktualizowane przy wyborze. Strzałki lewo/prawo, Home i End zmieniają zakładkę i fokus. Bez JavaScript pasek zakładek pozostaje ukryty, wszystkie sekcje są dostępne jedna pod drugą.

## Wygląd

Korzeń `.match-detail` definiuje kolory stron: `--home` (niebieski gospodarza) i `--away` (pomarańczowy gościa). Te same akcenty oznaczają pasek przy nazwie drużyny w nagłówku, nagłówki kolumn statystyk i lewą krawędź paneli składów. Style są zawężone do `.match-detail`, bo `.hero` i `.score-hero` współdzielą inne strony szczegółów. Rozmiary i kroje czcionek pozostają wspólne z resztą administracji.

Wynik stoi w ciemnym polu, chipy metadanych mają wyciszone etykiety (poza kolejką, której wartość zawiera już słowo „Kolejka”), a status jest wyrównany do prawej. „Dane podstawowe” to siatka par etykieta–wartość (`dl.match-fields`, kolumny `auto-fill` od 250px); puste wartości „—” są wyciszone. „Wynik i statystyki” to tabela lustrzana: gospodarz | statystyka | gość; wiersze z brakiem obu wartości są wyciszone. W tabelach składów numery i kolumny liczbowe są wyśrodkowane, nazwisko pogrubione; legenda ma próbkę koloru wyróżnienia.

## Weryfikacja

`tests/unit/test_match_statistics.py` sprawdza rozstrzygnięcia remisu, bilans formy, serwis przy `zamiana` i braku drużyny, porównanie, strzelców, formę i mapowanie wierszy repozytorium. `tests/interface/test_matches.py` sprawdza zakładkę analizy i mecz bez wyniku. `tests/interface/test_match_rosters.py` sprawdza kolejność pozycji i numerów, braki, osobne maksima drużyn i remis liderów, oddzielność serii karnych oraz renderowanie wyróżnień i struktury modalu, a także linki drużyn w nagłówku (z zamianą i bez identyfikatora) i kolejność skryptów. Dotychczasowe testy szczegółów pozostają w `tests/interface/test_matches.py`. Dane testowe są pamięciowe; nie wymagają bazy. `node --test tests/javascript/match_detail.test.cjs` sprawdza otwieranie, zamykanie, fokus, Enter, błąd HTTP, anulowanie pobierania i pomijanie dwukliku na linku. `tests/javascript/match_team_links.test.cjs` sprawdza, że kliknięcie drużyny otwiera okno po opóźnieniu, a dwuklik nową kartę. Testy JS korzystają z atrap DOM; nie zastępują kontroli wizualnej w przeglądarce.

## Układ tekstowy i mapa zmian

Rzeczywisty układ strony; w modalu pomijana jest wspólna rama i przycisk powrotu.

```text
[Szczegóły meczu #ID]
[▌Gospodarz*       [ Wynik / do przerwy / dopisek ]       Gość*▐]
  * link: klik → okno karty drużyny, dwuklik → nowa karta
[Rozgrywki …] [Kolejka N] [Termin …] [Hala …]            [Status]
[← Powrót do listy] (tylko pełna strona)
[Zakładki: Dane podstawowe | Analiza meczu | Wynik i statystyki | Składy]
[Dane podstawowe: siatka  Etykieta/wartość | Etykieta/wartość | …]
[Analiza meczu:
  • wniosek 1 / • wniosek 2 / • wniosek 3
  Porównanie drużyn:  26 | Bramki ▬▬▬▬▬▬ | 26   (pasek: udział gosp./gościa)
  Najlepsi strzelcy:  [▌1. Nazwisko 8 (4 z karnych) …] [▌1. Nazwisko 11 …]
  Forma w sezonie:    [▌bilans, bramki        ] [▌bilans, bramki        ]
                      [W 30:28 | vs Rywal     ] [P 27:30 | @ Rywal      ]
                      [   data · dom          ] [   data · wyjazd       ]
  bez wyniku: notatka zamiast wniosków, porównania i strzelców]
[Statystyki:  wartość gosp. |  Statystyka  | wartość gościa]
[▌Skład gospodarza              |▌Skład gościa]
[# | Zawodnik | Poz. | Br. | 2 min | Upomn. | Dyskw. | KD |
 Wyjście | Karne | Karne seria]
[Wiersze grupowane po pozycji; pastelowe tło; liderzy: czerwone Br.]
[Pozostałe osoby przypisane do meczu — opcjonalnie]
[■ Legenda wyróżnień pod tabelami składów]

Okno drużyny (nad stroną lub modalem meczu):
[Karta drużyny                                           ×]
[karta drużyny z zakładkami, bez „Powrót do listy drużyn”]
[Otwórz w nowej karcie] [Zamknij]

Modal na liście:
[Szczegóły meczu                                         ×]
[powyższa treść, przewijana]
[Otwórz w nowej karcie] [Zamknij]
```

Poniżej 1100px nagłówek wyniku układa się pionowo, a akcenty drużyn stają się krótkimi poziomymi paskami. Na wąskim ekranie sekcje `.grid2` układają się pionowo; tabele przewijają się poziomo we własnych `.table-wrap`.

| Element | Plik i miejsce |
| --- | --- |
| Wynik i metadane | [detail.html](detail.html): `.hero`, `.score-hero`, `.team-box.home/.away`, `.hero-meta`, `.meta-label`, `.meta-chip.status` |
| Dane podstawowe | [detail.html](detail.html): `dl.match-fields`, `.match-field.empty`; dane `dane_podstawowe` |
| Statystyki | [detail.html](detail.html): `table.match-stats`, `.home`, `.away`, `tr.empty`; dane `statystyki` |
| Fragment do modalu | [detail.html](detail.html): `[data-match-detail]`, `[data-detail-navigation]` |
| Składy i komórki bramek | [detail.html](detail.html): `.panel.roster.home/.away`, `.roster-table`, `.roster-player`, `.top-scorer`, `.roster-legend`, `.roster-legend-swatch` |
| Okno drużyny | [detail.html](detail.html): makro `nazwa_druzyny`, `a.team-link[data-team-modal-link]`, `dialog[data-team-modal-dialog]`; dane `id_gospodarz`, `id_gosc`; [classification_details.js](../../../static/js/classification_details.js): `LinkiDruzynController`, `OknoDruzynyController`; CSS `.match-detail .team-name .team-link` |
| Okno zawodnika | [detail.html](detail.html): `dialog[data-player-modal-dialog]`; [player_details.js](../../../static/js/player_details.js): `LinkiZawodnikowController`, `OknoZawodnikaController`; [matches.js](../../../static/js/matches.js): `uruchomSzczegolyMeczu()` |
| Kolejność i wyróżnienia | [match_presenter.py](../../../presenters/match_presenter.py): `SkladMeczuPresenter` |
| Źródło danych | [match_repository.py](../../../../infrastructure/repositories/match_repository.py): `pobierz_szczegoly`, `_zawodnik` |
| Modal i jego obsługa | [list.html](list.html): `#match-detail-dialog`; [matches.js](../../../static/js/matches.js): `SzczegolyMeczuController` |
| Kolory i rozmiary | [admin.css](../../../static/css/admin.css): `.match-detail` (zmienne `--home`, `--away`), `.match-fields`, `.match-stats`, `.roster-table`, `.match-detail-dialog`, `.roster-player[style] td`, `.top-scorer` |
| Analiza meczu | [detail.html](detail.html): `#match-panel-analysis`, `.match-insights`, `table.match-compare`, `.compare-bar`, `td.lead`, makra `strzelcy_druzyny` i `forma_druzyny`, `.form-match.win/.draw/.loss/.current`; dane `statystyki` ([match_statistics.py](../../../view_models/match_statistics.py)); [match_statistics_presenter.py](../../../presenters/match_statistics_presenter.py); [match_statistics.py](../../../../domain/match_statistics.py); [match_statistics_service.py](../../../../services/match_statistics_service.py); [match_statistics_repository.py](../../../../infrastructure/repositories/match_statistics_repository.py); CSS `.match-analysis`, `.form-*`, `.scorers-*` |
| Zakładki | [detail.html](detail.html): [data-match-tabs], [data-match-panel]; [matches.js](../../../static/js/matches.js): ZakladkiMeczuController; CSS .match-tabs |
| Kontrakty szablonu | [matches.py](../../../view_models/matches.py): `SzczegolyMeczuViewModel`, `ZawodnikMeczuViewModel` |
