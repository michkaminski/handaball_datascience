# Szczegóły sędziego

Status: zaimplementowany szablon [detail.html](detail.html).

## Przeznaczenie i routing

Strona `GET /administracja/sedziowie/<id_sedzia>` pokazuje kartę osoby występującej w `public.sedziowie`. Brak rekordu daje 404, błąd odczytu 503, a niepoprawne filtry 400. Widok jest tylko do odczytu.

Przepływ: `SedziaSzczegolyView` → `SzczegolySedziegoService` → `SzczegolySedziegoReadRepository` → `SzczegolySedziegoPresenter` → szablon. Implementacja SQLAlchemy używa `sedziowie`, `mecze_sedziowie`, `mecze`, `sezony`, `rozgrywki`, `zespoly_sezony` i `zespoly`. Partnerzy są pobierani zbiorczo dla strony meczów; rankingi korzystają z agregacji SQL i nie wykonują zapytania na każdy wiersz.

## Dane i zachowanie

Nagłówek pokazuje nazwę przechowywaną w polu `sedziowie.nazwisko`, opcjonalne miasto oraz wiarygodne liczniki różnych meczów, sezonów, nazw rozgrywek i drużyn. Pole źródłowe nie rozdziela imienia i nazwiska, dlatego interfejs nie próbuje ich zgadywać.

Zakładki:

- `Dane`: ID, dostępne dane podstawowe, pierwszy i ostatni mecz oraz aktywność sezonowa.
- `Mecze`: paginowana tabela domyślnie od najnowszych; filtry sezonu, rozgrywek, drużyny, strony oraz zakresu dat; linki do meczu i partnerów.
- `Statystyki`: wspólne filtry sezonu i rozgrywek, podsumowanie, wykresy HTML/CSS oraz pełne tabele sezon × rozgrywki, drużyn i partnerów.

`zamiana` w meczu jest uwzględniana przy nazwach gospodarza/gościa, wyniku i statystyce strony drużyny. Mecz danej drużyny jest liczony raz; obie uczestniczące drużyny otrzymują po jednym wystąpieniu. Partner nie obejmuje analizowanego sędziego i jest liczony raz na wspólny mecz.

Wykresy wykorzystują istniejący mechanizm pasków HTML/CSS z karty hali. Nie wymagają zewnętrznego CDN ani nowej biblioteki i nie zastępują tabel.

## Układ tekstowy i mapa zmian

```text
Start › Dane › Sędziowie › Szczegóły
NAZWA SĘDZIEGO                         [← Powrót do listy]
[Mecze] [Sezony] [Rozgrywki] [Drużyny]

[Dane] [Mecze] [Statystyki]

Dane:
  ID / nazwa / opcjonalne miasto / pierwszy mecz / ostatni mecz
  Aktywność w sezonach: Sezon | Mecze | Rozgrywki

Mecze:
  [Sezon] [Rozgrywki] [Drużyna] [Strona] [Data od] [Data do]
  Data | Sezon | Rozgrywki | Gospodarz | Wynik | Gość | Partner | Akcje
  [paginacja]

Statystyki:
  [Sezon] [Rozgrywki]
  [Mecze] [Sezony] [Rozgrywki] [Drużyny]
  [Mecze wg sezonów] [Rozgrywki]
  [Drużyny] [Partnerzy]
  Sezon × rozgrywki
  Drużyny: mecze / gospodarz / gość
  Partnerzy: wspólne mecze
```

| Element | Plik / selektor / dane |
| --- | --- |
| Routing i walidacja | `interface/admin/views/referee_detail_views.py`, `MeczeSedziegoFilterForm` |
| Karta i agregacje | `infrastructure/repositories/referee_detail_repository.py`, `SzczegolySedziegoService` |
| Teksty i szerokości pasków | `interface/presenters/referee_detail_presenter.py`, `view_models/referee_details.py` |
| Zakładki i tabele | [detail.html](detail.html), `[data-referee-tab]`, `[data-referee-panel]` |
| Obsługa zakładek | `interface/static/js/referee_details.js`, `ZakladkiSedziegoController` |
| Styl i responsywność | `interface/static/css/admin.css`, `.referee-*`, współdzielone `.venue-chart` i `.venue-bars` |
| Wejście z listy | [list.html](list.html), kolumna `Akcje` |