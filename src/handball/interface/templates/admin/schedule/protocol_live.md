# Protokół HTML offline — protokół meczu na żywo

Status: wdrożony 2026-10-21 na polecenie użytkownika („obok Print match sheet było Print HTML protocol offline … HTML ma być dokładnie jak ten co przypiąłem tylko od razu ma być wpięty json … plik do pobrania spakowany ZIP … taki sam wydruk zrób w handball_datascience”). Wzorem jest prototyp `C:\Michal\_ZPRP_PROD\Prototyp\protokol_live.html`; ten sam szablon działa w projekcie EHF (`ehf/interface/templates/print/protokol_live.html`). Szablon `protocol_live.html` istnieje.

Samodzielna strona HTML (CSS i JavaScript w pliku, bez zasobów serwisu i bez połączenia z siecią) do prowadzenia protokołu podczas meczu na tablecie lub laptopie: gole, rzuty karne, kary, zegar, przebieg zawodów i wykres przewagi. Treść strony jest kopią prototypu; zmiany względem prototypu:

- dokument meczu jest wbudowany (`const EMBEDDED = {{ dokument|tojson }}`, `EMBEDDED_FILE` = nazwa pliku JSON), więc po otwarciu pliku od razu widać drużyny i kadry, bez ekranu „Otwórz plik JSON”; „Pobierz JSON” zapisuje stan pod nazwą `EMBEDDED_FILE`, a „Otwórz inny mecz” pozwala podpiąć istniejący JSON z autozapisem;
- zapis (polecenia użytkownika z 2026-10-21: „na tablecie nie zapisuje mi wyniku”, „można nie zapisywać nic w przeglądarce tylko w plikach json, chodzi mi o cały mecz”): cały mecz (składy i zdarzenia) zapisuje się wyłącznie do pliku JSON — przeglądarka niczego nie przechowuje (strona przy starcie usuwa bazę `protokol_live` zostawioną przez wcześniejszą wersję). Przycisk **„Zapisuj do pliku JSON”** (`connectJson()`, `showSaveFilePicker`, widoczny w przeglądarkach z dostępem do plików, np. Chrome/Edge, także Chrome na Androidzie) tworzy albo nadpisuje plik JSON i od tej chwili każda zmiana zapisuje się do niego; „Otwórz inny mecz” otwiera istniejący JSON z autozapisem. Po otwarciu HTML-a w takiej przeglądarce pokazuje się okno „Zapis meczu do pliku” (`#gov`, `showGrant()`, polecenie użytkownika z 2026-10-21) z nazwą pliku meczu, w dwóch krokach, bo każdy wymaga osobnego kliknięcia (Chrome na Androidzie zgłaszał „User activation is required to request permissions”, gdy zgoda była proszona zaraz po wyborze pliku): 1) „Wskaż plik meczu” (`pickJson()`) — użytkownik wskazuje JSON z katalogu z ZIP-a, strona wczytuje z niego stan meczu (inna nazwa pliku → pytanie); 2) **„Udzielam zgody na zapis do pliku”** (`grantWrite()`, `requestPermission`) — od tej chwili każda zmiana zapisuje się do pliku, także zmiany zrobione między krokami. Gdy przeglądarka ma już zgodę, krok 2 jest pomijany. Tak samo działa „Otwórz inny mecz” (`attach()`). Samodzielne wczytanie pliku po nazwie jest niemożliwe — przeglądarka wymaga wskazania pliku przez użytkownika. Okno ma też „Utwórz nowy plik” (`connectJson()`) i „Bez zapisu do pliku”; „Zapisuj do pliku JSON” otwiera je ponownie. W przeglądarkach bez dostępu do plików (np. Safari na iPadzie) zapis tylko przyciskiem „Pobierz JSON”; zamknięcie strony bez zapisu traci zmiany (strona ostrzega przy niezapisanych zmianach);
- kolumna **%B** — skuteczność bramkarza w sezonie (pola `ob`, `rz`, `sk`; w podpowiedzi obrony / rzuty). Kolumna pokazuje się tylko, gdy dokument ma te pola. Protokoły ZPRP nie zawierają obron, więc tu kolumny nie ma (zob. [PLAYER_DATA_SCIENCE](../../../../../../docs/PLAYER_DATA_SCIENCE.md)); w projekcie EHF jest;
- mecz bez `id` ma tytuł z nazw drużyn;
- przycisk **„Koniec meczu”** (`endMatch()`, polecenie użytkownika z 2026-10-21) zatrzymuje zegar, zapisuje `state.finished` i otwiera w nowej karcie raport meczu (`reportHtml()`): samodzielna strona HTML z wynikiem i połowami, „Najważniejsze” (najlepszy strzelec, największa przewaga, najdłuższa seria, remisy i zmiany prowadzenia), porównaniem drużyn (paski), wykresem przewagi w czasie (SVG), bramkami w odcinkach 10 minut, tabelami zawodników (gole, 7m, W, 2', D) i pełnym przebiegiem zawodów; podpis Sportomatyka „Bawimy się danymi”. Raport ma przyciski „Drukuj / PDF” (A4) i „Zapisz raport” (`<nazwa>_raport.html`). Po zakończeniu przycisk nazywa się „Raport meczu” i generuje raport ponownie; „Wyczyść zdarzenia” kasuje też zakończenie. Gdy przeglądarka zablokuje nową kartę, raport się pobiera;
- przyciski „+G” i „Kara” przy składach są większe (dotyk na tablecie).
- przebieg zawodów w panelu (polecenie użytkownika z 2026-10-21: „nie wiadomo który od drużyny gospodarzy który od gości”) ma układ jak na protokole: minuta | zawodnik A | wynik | zawodnik B, z wierszem nagłówka z nazwami drużyn; komórka zawodnika jest w kolorze drużyny (A niebieska po lewej, B czerwona po prawej), kary i niewykorzystane 7 m trafiają na stronę swojej drużyny. Przebieg pełnoekranowy bez zmian (znacznik A/B);
- układ na jednym ekranie (skład A | skład B | przebieg) działa od szerokości 700 px, więc także na tablecie w pionie; przy 700–999 px mniejsze czcionki, bez kolumn Ur., M i Śr (`.opt`, `.opt2`), imię pod nazwiskiem (`.pname .sn`, `.fn`), przycisk „K” zamiast „Kara” i przebieg szeroki na 240 px (na ekranach ≥ 1000 px: 350 px, 1000–1199 px: 290 px, ≥ 1500 px: 470 px; strzelcy w przebiegu drobną czcionką 8–9 px). Poniżej 700 px (telefon) wszystko jedno pod drugim.

Trasa `GET /administracja/terminarz/<id_mecz>/protokol-live`, endpoint `administracja.protokol_meczu_live`, widok `ProtokolMeczuLiveView` ([schedule_views.py](../../../admin/views/schedule_views.py)). Parametry jak w [protokole PDF](protocol_pdf.md) (`ZapowiedzOpcjeForm`: `kadra_poprzedni`, `kolejnosc_protokolu`; błędne → 400, brak meczu → 404). Dane pochodzą z tego samego `ProtokolMeczuService` co protokół PDF; dokument buduje `ProtokolLivePresenter` ([match_protocol_live_presenter.py](../../../presenters/match_protocol_live_presenter.py)).

Odpowiedź to ZIP (`attachment`, `Cache-Control: no-store`) z katalogiem `RRRR-MM-DD_Gospodarz_Gosc/` (polecenie użytkownika z 2026-10-21), a w nim dwa pliki o tej samej nazwie bazowej `RRRR-MM-DD_Gospodarz_Gosc` (`NazwaPlikuProtokoluPolicy`: data meczu, a bez terminu — data stanu kadr; nazwy drużyn bez polskich znaków, odstępy i znaki specjalne → `-`): `.html` (strona z wbudowanymi danymi) i `.json` (ten sam dokument). Archiwum powstaje w pamięci (`ZipResponseBuilder`, `BytesIO`) — nic nie jest zapisywane na dysku serwera.

## Dokument JSON

`{"format": "protokol_live", "version": 1, "match": {...}}`; `state` (zdarzenia) dopisuje dopiero strona.

- `id` — `id_mecz`; `competition` — rozgrywki · sezon · runda · kolejka; `date` (dd.mm.rrrr), `time` (tylko przy `data_faktyczna`); `venue` — hala z adresem; `capacity` — pojemność hali (gdy znana); `statsNote` — sezon statystyk i stan kadr.
- `A`, `B` — `name`, `short` (pełna nazwa) i `players`: `nr`, `name` („NAZWISKO Imię”, nazwisko wielkimi literami, bo strona po nim skraca nazwiska w przebiegu), `pos` (B/R/S/O, `SKROTY_POZYCJI`), `ur` (rocznik dwiema cyframi), `m`, `br`, `sr` (null u zawodnika dodanego z poprzedniego sezonu).
- Strona rozpoznaje zawodnika po numerze, więc numer musi być jednoznaczny (`NumeryProtokoluLivePolicy`): najniższy numer koszulki; brak numeru albo numer zajęty przez wcześniejszego zawodnika → kolejny wolny od 100. Numer można poprawić na stronie (kliknięcie nazwiska).

## Układ tekstowy i mapa zmian

Stan: układ istniejącego `protocol_live.html` (ekran ≥ 700 px, wszystko na jednym ekranie; w pionie 700–999 px węższe kolumny i imię pod nazwiskiem).

```text
+------------------------------------------------------------------------------+
| ORLEN Superliga · 2025/2026 · I runda · Seria 2 · 22.09.2025 godz. 18:00 · … |
|   A · Górnik Zabrze  [+ GOL A]   0 : 0 (do przerwy 0 : 0)  [+ GOL B]  Wisła · B |
|   [I połowa][II połowa]  −1' −10" −1"  00:00  +1" +10" +1'  [▶]              |
+-------------------------------+-------------------------------+--------------+
| A — Górnik Zabrze             | B — Wisła Płock               | Przebieg     |
| Nr Zawodnik P Ur M Br Śr (%B) | Nr Zawodnik P Ur M Br Śr (%B) | I połowa     |
|    Gol 7m W 2' D [+G][Kara]   |    Gol 7m W 2' D [+G][Kara]   |  min wynik … |
| …                             | …                             | min A wyn. B |
|                               |                               | 3' 20 MÖL 1:0|
|                               |                               | 4'   1:1 3 KR|
| …                             | …                             | II połowa    |
| [+ Zawodnik] Osoby tow. A–E   | [+ Zawodnik] Osoby tow. A–E   | podsumowanie |
+-------------------------------+-------------------------------+--------------+
| [Pobierz JSON] [Otwórz inny mecz] [Wyczyść zdarzenia]   status pliku          |
+------------------------------------------------------------------------------+
```

| Element | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Wygląd i zachowanie strony | [protocol_live.html](protocol_live.html) | `<style>`, funkcje `render()`, `renderTimeline()`; zmiany wprowadzaj także w prototypie i w projekcie EHF. |
| Zapis do pliku JSON | [protocol_live.html](protocol_live.html) | `showGrant()`, `pickJson()`, `grantWrite()`, `showConsent()`, `connectJson()`, `save()`, `attach()`, `startEmbedded()`, `#gov`, `#connectBtn`. |
| Wbudowane dane | [protocol_live.html](protocol_live.html), [schedule_views.py](../../../admin/views/schedule_views.py) | `EMBEDDED`, `EMBEDDED_FILE`, `initStart()`; `ProtokolMeczuLiveView`. |
| Przebieg w panelu (strony A/B) | [protocol_live.html](protocol_live.html) | `evHead` i wiersze `ev1`/`ev2` w `render()`; style `.ev .side`, `.ev .evh`. |
| Tablet w pionie | [protocol_live.html](protocol_live.html) | `@media (min-width: 700px) and (max-width: 999px)`. |
| Kolumna %B | [protocol_live.html](protocol_live.html) | `hasSaves()`, `SORT_KEYS.sk`, komórka `sk` w `render()`. |
| Treść JSON, numery, nazwy plików | [match_protocol_live_presenter.py](../../../presenters/match_protocol_live_presenter.py) | `ProtokolLivePresenter`, `NumeryProtokoluLivePolicy`, `NazwaPlikuProtokoluPolicy`. |
| Raport po meczu | [protocol_live.html](protocol_live.html) | `endMatch()`, `matchStats()`, `reportLeadChart()`, `reportSegChart()`, `reportHtml()`, `#endBtn`. |
| ZIP | [schedule_views.py](../../../admin/views/schedule_views.py) | `ZipResponseBuilder`. |
| Przycisk w zapowiedzi | [preview.html](preview.html) | `[data-preview-protocol-live]`. |
