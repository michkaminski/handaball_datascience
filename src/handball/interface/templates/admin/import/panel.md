# Import / eksport danych

Status: projekt szablonu. Katalog `import/` i ten plik nie mają jeszcze odpowiadającego HTML ani żadnego kodu. Wzorzec: prototyp v6 `imports.html` — placeholder ("Przykładowa strona administracyjna"), bez własnego układu poza wspólnym `base.html`.

Docelowy szablon względem katalogu szablony: `admin/import/panel.html` (nazwa robocza).

## Przeznaczenie

Obsługuje trzy pozycje sidebara z grupy "Import / eksport" ("Import danych", "Historia importów", "Eksport danych") oraz pozycję "Import" w górnym pasku — w prototypie wszystkie cztery linki prowadzą do tego samego `imports.html` (jedna strona, prawdopodobnie z zakładkami). Docelowo: historia przebiegów importu (`logs` — patrz [database/README](../../../../../../docs/database/README.md), tabela "Stan importu i istniejące anomalie") oraz pochodzenie danych (`public.pliki_zrodlowe`, `public.rekordy_zrodla`).

## Dane wejściowe

Nieustalone. Ostatni zapisany przebieg importu ma status `CZESCIOWY` (patrz DATA.md) — ekran historii importów powinien to pokazywać wprost, nie ukrywać. "Import danych" i "Eksport danych" to operacje zmieniające stan — wymagają wyraźnego zlecenia użytkownika przed implementacją zapisu (patrz AGENTS.md, CODING_STANDARDS.md); na start realny może być tylko odczyt historii.

## Powiązania

Dziedziczyłby `base.html`. Modele schematu `logs` jeszcze nie istnieją w `infrastructure/database/models/`. Pozycje menu w `interface/navigation.py` (`GORNY_PASEK` klucz `import`; `SIDEBAR` grupa "Import / eksport", klucze `import_danych`, `historia_importow`, `eksport_danych`) mają obecnie `punkt_koncowy=None`.

## Gdzie wprowadzać zmiany

Nie dotyczy — brak implementacji.

## Sprawdzenie zmiany

Nie dotyczy — brak implementacji.

## Stan implementacji

Nie zaimplementowano. Zbliżone do etapu 7 z [IMPLEMENTATION_PLAN](../../../../../../docs/IMPLEMENTATION_PLAN.md) ("Modele schematu logs oraz repozytoria i widoki diagnostyki — wyłącznie odczyt istniejących importów, anomalii i historii"). Operacje zapisu (uruchomienie importu, eksport) wymagają osobnej, wyraźnej decyzji użytkownika przed implementacją.
