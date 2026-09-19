# Szczegóły meczu

Status: zaimplementowany szablon [detail.html](detail.html), oparty na ekranie match_detail.html prototypu v6.

## Przeznaczenie i powiązania

Przycisk „Szczegóły” na liście otwiera pełną stronę w nowej karcie. Dwuklik w wiersz lub Enter na wierszu pobiera tę samą stronę do natywnego modalu na liście. Kontroler pobiera wyłącznie element `[data-match-detail]` i usuwa z podglądu link powrotu. Modal nie kopiuje nagłówka, menu i stopki. Zamknięcie przyciskiem lub Escape zachowuje listę i filtry oraz przywraca fokus do wiersza. Nieudany odczyt pokazuje komunikat z możliwością otwarcia nowej karty.

Przepływ: `MeczSzczegolyView` → `MeczService` → `MeczReadRepository`, następnie `MeczPresenter` (z `SkladMeczuPresenter`, `MeczFormat` i domenowym `MeczPolicy`) → model widoku → szablon. Trasa: `GET /administracja/mecze/<id_mecz>`. Brak meczu daje 404, błąd odczytu 503. Pełna strona dziedziczy `base.html`.

## Dane wejściowe

`szczegoly: SzczegolyMeczuViewModel` zawiera nazwy gospodarza i gościa, wynik nagłówka, wynik do przerwy, dopisek wyniku, rozgrywki, kolejkę, termin, halę, status, pary danych podstawowych, statystyki porównawcze i trzy listy `ZawodnikMeczuViewModel`: `sklad_gospodarz`, `sklad_gosc`, `sklad_inne`. `sekcja_aktywna="mecze"` podświetla nawigację.

Zawodnik zawiera numer koszulki, nazwę, pozycję, bramki, kary dwuminutowe, upomnienie, dyskwalifikację, KD, wyjście, karne i serię karnych. Repozytorium dostarcza typowane dane domenowe; teksty i wyróżnienia przygotowują presentery. Szablon nie wykonuje zapytań. Dane tekstowe są automatycznie escapowane przez Jinja2.

Repozytorium i serwis zwracają `SzczegolyMeczu` z `DaneMeczu` oraz składami `ZawodnikMeczu`. Numery koszulek i bramki są typu `int | None`, daty mają typ `datetime | None`, a flagi `bool | None`. `ZaleznosciZadaniaFactory.utworz_presenter_meczow()` składa zależności presentera. Dopiero `MeczPresenter.przygotuj_szczegoly()` tworzy model widoku opisany powyżej.

## Kolejność, kolory i najlepsi strzelcy

`SkladMeczuPresenter` grupuje składy alfabetycznie według źródłowego tekstu pozycji (bez rozróżniania wielkości liter), następnie według liczbowego numeru koszulki i nazwy. Nie zgaduje znaczenia skrótów. Brak pozycji trafia na koniec i pozostaje bez koloru. Różne pozycje mają delikatne pastelowe tła; ta sama pozycja ma ten sam kolor w obu zespołach danego meczu. Kolor może różnić się między meczami o innym zestawie pozycji.

Model widoku zawodnika zawiera `kolor_pozycji: int | None` i `najlepszy_strzelec: bool`. Wyróżnia komórkę „Br.” u każdego zawodnika z największą dodatnią liczbą bramek osobno w każdej drużynie, także przy remisie. Osoby z `sklad_inne` nie uczestniczą w porównaniu. Nie dodaje ponownie bramek z karnych ani z serii karnych. Zera i braki nie otrzymują wyróżnienia. Przy niepełnych danych maksimum dotyczy dostępnych statystyk zawodników.

Czerwone tło jest uzupełnione pogrubieniem, opisem przy najechaniu, etykietą dostępną dla czytnika i legendą pod wszystkimi tabelami zakładki „Składy”. Puste składy pokazują „Brak danych o składzie.”. Pozostałe osoby są wyświetlane tylko przy niepustej liście.

## Zakładki

Pod nagłówkiem meczu są trzy zakładki: „Dane podstawowe”, „Wynik i statystyki”, „Składy”. Pierwsza jest domyślna przy każdym otwarciu. Wynik i metadane meczu pozostają nad zakładkami. Zakładka składów obejmuje obie drużyny, opcjonalne pozostałe osoby i opis kolorów na samym dole.

`ZakladkiMeczuController` w [matches.js](../../../static/js/matches.js) działa zarówno na pełnej stronie, jak i po załadowaniu fragmentu do modalu. Przyciski mają role tab, panelom nadawana jest rola tabpanel, a aria-selected i tabindex są aktualizowane przy wyborze. Strzałki lewo/prawo, Home i End zmieniają zakładkę i fokus. Bez JavaScript pasek zakładek pozostaje ukryty, wszystkie sekcje są dostępne jedna pod drugą.

## Weryfikacja

`tests/interface/test_match_rosters.py` sprawdza kolejność pozycji i numerów, braki, osobne maksima drużyn i remis liderów, oddzielność serii karnych oraz renderowanie wyróżnień i struktury modalu. Dotychczasowe testy szczegółów pozostają w `tests/interface/test_matches.py`. Dane testowe są pamięciowe; nie wymagają bazy. `node --test tests/javascript/match_detail.test.cjs` sprawdza otwieranie, zamykanie, fokus, Enter, błąd HTTP, anulowanie pobierania i pomijanie dwukliku na linku. Testy JS korzystają z atrap DOM; nie zastępują kontroli wizualnej w przeglądarce.

## Układ tekstowy i mapa zmian

Rzeczywisty układ strony; w modalu pomijana jest wspólna rama i przycisk powrotu.

```text
[Szczegóły meczu #ID]
[Gospodarz          Wynik / do przerwy / dopisek          Gość]
[Rozgrywki] [Kolejka] [Termin] [Hala] [Status]
[← Powrót do listy] (tylko pełna strona)
[Zakładki: Dane podstawowe | Wynik i statystyki | Składy]
[Skład gospodarza               | Skład gościa]
[# | Zawodnik | Poz. | Br. | 2 min | Upomn. | Dyskw. | KD |
 Wyjście | Karne | Karne seria]
[Wiersze grupowane po pozycji; pastelowe tło; liderzy: czerwone Br.]
[Pozostałe osoby przypisane do meczu — opcjonalnie]
[Legenda wyróżnień pod tabelami składów]

Modal na liście:
[Szczegóły meczu                                         ×]
[powyższa treść, przewijana]
[Otwórz w nowej karcie] [Zamknij]
```

Na wąskim ekranie sekcje `.grid2` układają się pionowo; tabele przewijają się poziomo we własnych `.table-wrap`.

| Element | Plik i miejsce |
| --- | --- |
| Wynik i metadane | [detail.html](detail.html): `.hero`, `.score-hero`, `.hero-meta` |
| Fragment do modalu | [detail.html](detail.html): `[data-match-detail]`, `[data-detail-navigation]` |
| Składy i komórki bramek | [detail.html](detail.html): `.roster-player`, `.top-scorer`, `.roster-legend` |
| Kolejność i wyróżnienia | [match_presenter.py](../../../presenters/match_presenter.py): `SkladMeczuPresenter` |
| Źródło danych | [match_repository.py](../../../../infrastructure/repositories/match_repository.py): `pobierz_szczegoly`, `_zawodnik` |
| Modal i jego obsługa | [list.html](list.html): `#match-detail-dialog`; [matches.js](../../../static/js/matches.js): `SzczegolyMeczuController` |
| Kolory i rozmiary | [admin.css](../../../static/css/admin.css): `.match-detail-dialog`, `.roster-player[style] td`, `.top-scorer` |
| Zakładki | [detail.html](detail.html): [data-match-tabs], [data-match-panel]; [matches.js](../../../static/js/matches.js): ZakladkiMeczuController; CSS .match-tabs |
| Kontrakty szablonu | [matches.py](../../../view_models/matches.py): `SzczegolyMeczuViewModel`, `ZawodnikMeczuViewModel` |
