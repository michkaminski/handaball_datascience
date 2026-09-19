# Dane i ich interpretacja

## Materiały odniesienia

- [Rzeczywista baza — przegląd](database/README.md), [schemat public](database/PUBLIC_SCHEMA.md), [schemat logs](database/LOGS_SCHEMA.md) i [relacje oraz różnice](database/RELATIONSHIPS.md): inspekcja `localhost:5432/zprp` z 2026-09-12. Pierwszy punkt odniesienia dla nowej aplikacji.
- [Archiwalny schemat PostgreSQL](database/schema_postgres_archive.sql) (kopia wcześniejszego projektu bazy z katalogu nadrzędnego, stan 2026-09-10): encje i relacje zaprojektowane dla archiwum ZPRP.
- README starszego serwisu poza katalogiem tego projektu (`_ZPRP_API/README.md` w katalogu nadrzędnym): opis źródeł i zaobserwowanej normalizacji.
- Normalizacja starszego serwisu poza katalogiem tego projektu (`_ZPRP_API/handball/normalize.py` w katalogu nadrzędnym): przykład istniejącej interpretacji danych, wymagający weryfikacji przed ponownym użyciem.
- Testy starszego serwisu poza katalogiem tego projektu (`_ZPRP_API/tests/test_import.py` w katalogu nadrzędnym): przypadki regresyjne istniejącego importu.

Ścieżki dotyczą obecnego układu katalogów na dysku, poza katalogiem tego projektu. Nie kopiuj całego archiwum ani schematu do kontekstu AI. Czytaj pola i próbki potrzebne w zadaniu.

## Skrócona mapa danych

| Obszar | Tabele |
| --- | --- |
| Sezon i rozgrywki | `sezony`, `rozgrywki`, `rundy`, `kolejki` |
| Kluby i drużyny | `kluby`, `zespoly`, `zespoly_sezony`, `zespoly_rozgrywki` |
| Mecze i występy | `mecze`, `mecze_zawodnicy`, `zawodnicy`, `sklady` |
| Klasyfikacje | `tabele`, `tabele_grupy`, `tabele_wiersze`, `strzelcy` |
| Wersje składów | `sklady_wersje`, `sklady_wersje_zawodnicy` |
| Pochodzenie danych | `pliki_zrodlowe`, `rekordy_zrodla` |
| Import, anomalie i historia | Schemat `logs`: rejestry, widoki i tabele `*_log` |

Tabele domenowe są w `public`. Stan rzeczywisty obejmuje 30 tabel `public`, 35 tabel `logs` i 2 widoki `logs`. Pełne kolumny, klucze i indeksy znajdują się w dokumentacji bazy. Przy późniejszej zmianie schematu odśwież odpowiedni fragment dokumentacji tylko do odczytu.

## Zasady domenowe

- Rozróżniaj klub, drużynę i jej migawkę sezonową. Historyczna nazwa nie musi być nazwą aktualną.
- Łącz rekordy po identyfikatorach i odpowiednim kontekście sezonu/rozgrywek, nie po samej nazwie.
- Brak wartości nie oznacza zera. Nie licz pełnych sum i skuteczności bez określenia kompletności danych i mianownika.
- Nie sumuj zamiennie wyniku końcowego, wyników tymczasowych, dogrywek i serii karnych. Najpierw ustal semantykę wyświetlanego pola.
- Starszy README opisuje specjalną obsługę `zamiana`: część metadanych i wyników jest odwracana, a składy już mają docelową stronę. Przed zastosowaniem tej logiki sprawdź, czy import do bazy już ją wykonał. Podwójna zamiana zepsuje wynik.
- Nie wliczaj kar sztabu do kar zawodników. Nie utożsamiaj obecności w składzie z występem.
- Identyfikatory lig, kody płci, statusy i zasady punktacji potwierdzaj w danych lub odpowiedniej dokumentacji; nie zgaduj ich z nazw rozgrywek.
- Dane kontaktowe, licencyjne i pola badań dostępne w bazie nie są domyślnie polami widoku meczu ani publicznego eksportu.

## Braki do ustalenia podczas integracji

Schemat oraz obecność 20 sezonów od 2007/2008 do 2026/2027 potwierdzono. Do ustalenia pozostają sposób normalizacji podczas importu oraz mapowanie statusów i wariantów wyniku na prezentację. Ostatni zapisany przebieg importu ma status `CZESCIOWY`; liczby rekordów nie dowodzą kompletności archiwum.

Nie naprawiaj danych ani nie uruchamiaj ponownie importu na podstawie tych obserwacji. Zmiany w bazie są dozwolone dopiero na wyraźną prośbę użytkownika.


## Prezentacja zmiany gospodarza — 2026-09-19

Na polecenie użytkownika lista meczów uwzględnia `mecze.zamiana=True`: odwraca nazwy obu drużyn oraz części wyniku `wynik_gosp_full` / `wynik_gosc_full`. Dla `False` lub `NULL` pozostawia kolejność. Reguła jest stosowana raz, przy budowaniu pozycji listy w repozytorium, bez zmiany danych źródłowych. Nie rozszerza automatycznie tej interpretacji na składy ani przyszłe statystyki.
