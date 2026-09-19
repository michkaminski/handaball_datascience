# Kontrola danych (anomalie i walidacja)

Status: projekt szablonu. Katalog `quality/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `quality.html` — jedna z niewielu podstron z rzeczywistą treścią (nie placeholder): tabela z kolumnami ID, Sezon, Rozgrywki, Opis, Plik, Status (`<span class="badge warn">OTWARTA</span>`).

Docelowy szablon względem katalogu szablony: `admin/quality/panel.html` (nazwa robocza).

## Przeznaczenie

Obsługuje dwie pozycje sidebara z grupy "Narzędzia" ("Anomalie danych", "Walidacja danych") oraz pozycję "Kontrola danych" w górnym pasku — w prototypie oba linki sidebara prowadzą do tego samego `quality.html`. Docelowo: przegląd `logs.anomalie_danych` — **realna tabela w bazie `zprp`, już opisana**: 26 197 wpisów, z kodami takimi jak `NIEPOPRAWNA_WARTOSC` (21 269, OSTRZEZENIE), `NIEUSTALONA_DRUZYNA` (2074, INFO), `BRAK_SKLADU` (870+152), `BLAD_POBRANIA` (14, BLAD) i inne — pełna lista w [database/README](../../../../../../docs/database/README.md), sekcja "Stan importu i istniejące anomalie".

## Dane wejściowe

Nieustalone. Prototyp sugeruje kolumny ID/Sezon/Rozgrywki/Opis/Plik/Status — realne dane w `logs.anomalie_danych` mają dodatkowo kod i poziom (OSTRZEZENIE/INFO/BLAD) i status (OTWARTA i inne). To odczyt istniejącej klasyfikacji zapisanej przez importer, nie nowa diagnoza aplikacji — nie sugerować, że to nowa analiza AI/aplikacji.

## Powiązania

Dziedziczyłby `base.html`. Modele schematu `logs` (w tym `anomalie_danych`) jeszcze nie istnieją w `infrastructure/database/models/`. Pozycje menu w `interface/navigation.py` (`GORNY_PASEK` klucz `kontrola`; `SIDEBAR` grupa "Narzędzia", klucze `anomalie`, `walidacja`) mają obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Zbliżone do etapu 7 z [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md) ("Modele schematu logs oraz repozytoria i widoki diagnostyki — wyłącznie odczyt istniejących importów, anomalii i historii"). Ten ekran ma już realne, opisane dane do wyświetlenia — dobry kandydat na pierwszy ekran diagnostyczny etapu 7.

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Kontrola danych
| [miejsce na: Anomalie danych / Walidacja danych]
| [filtry / wyniki / akcje: do ustalenia]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Prototyp `quality.html` ma treść, ale nie jest to gotowy ekran projektu. Nie należy utożsamiać przeglądania wyników kontroli z uruchamianiem funkcji zapisujących anomalie.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [panel.md](panel.md) | Najpierw uzupełnij ten opis; planowany plik `panel.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
| Pozycja nawigacji | [navigation.py](../../../navigation.py) | Odpowiednia pozycja menu pozostaje bez własnego widoku. Dla szczegółów meczu osobnej pozycji menu nie ma. |
