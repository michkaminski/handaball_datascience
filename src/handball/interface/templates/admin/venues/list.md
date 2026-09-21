# Hale

Status: zaimplementowany widok odczytowy GET /administracja/hale.

## Przeznaczenie

Lista tabeli public.hale z adresem, pojemnością i liczbą powiązanych meczów. Widok nie udostępnia zapisu. Każdy wiersz prowadzi do [karty hali](detail.md).

## Dane wejściowe

HalaFilterForm buduje FiltryKatalogu z parametrów szukaj, miasto, pojemnosc_min, sortowanie, strona i rozmiar_strony. Strona otrzymuje StronaKatalogu z elementami PozycjaHali.

## Powiązania

HalaListView → HalaService → HalaKatalogReadRepository → HalaKatalogSQLAlchemyRepository. Repozytorium łączy hale z meczami przez mecze.id_hala. Szablon dziedziczy base.html i dołącza partials/pagination.html.

## Sprawdzenie zmiany

Testy interfejsu sprawdzają renderowanie, nawigację, filtry, walidację, pusty wynik, błąd odczytu, escapowanie i brak zapisu.

## Układ tekstowy i mapa zmian

~~~text
+---------------------------------------------------------------+
| Start › Dane › Hale                                           |
| [Szukaj...] [Miasto...] [Pojemność od] [Filtruj] [Wyczyść]    |
+---------------------------------------------------------------+
| ID | Nazwa | Miasto | Adres | Pojemność | Mecze | Akcje       |
| Wyniki X–Y z N                      [Poprzednia] [Następna]     |
+---------------------------------------------------------------+
~~~

| Element | Odpowiedzialność |
| --- | --- |
| Nagłówek i filtry | list.html, .pagehead, .venue-filters |
| Tabela i osobna kolumna Akcje | list.html, #venues-table, PozycjaHali, endpoint szczegoly_hali |
| Paginacja | partials/pagination.html, StronaKatalogu |
| Nawigacja | navigation.py, klucz hale |
