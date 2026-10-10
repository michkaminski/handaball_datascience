# MAF — Model Atrakcyjności Frekwencyjnej i biblioteka Matematyka

Moduł Data Science odpowiadający na pytanie: *jaką dodatkową frekwencję wiąże się z obecnością konkretnego klubu jako przeciwnika i z jakim prawdopodobieństwem przyciąga on więcej kibiców niż typowy rywal?* Pełna specyfikacja matematyczna jest stroną biblioteki: `/matematyka/modele-sportowe/atrakcyjnosc-frekwencyjna/` (plik `src/mathlib/content/articles/modele-sportowe/atrakcyjnosc-frekwencyjna.html`). Ten dokument opisuje architekturę, uruchamianie i utrzymanie.

## Gdzie to jest w aplikacji

| Element | Adres |
| --- | --- |
| Dashboard | Raporty › Frekwencja › zakładka **Atrakcyjność (MAF)** (`/administracja/raporty/frekwencja?zakladka=maf`) |
| API dashboardu | `/administracja/raporty/frekwencja/maf/{dane,klub/<id>,gospodarz/<id>,porownanie,prognoza,eksport.csv}` |
| Biblioteka matematyczna | górny pasek **Matematyka** (`/matematyka/`) |

## Architektura

```text
            ┌──────────── proces treningowy (CLI, poza żądaniami HTTP) ───────────┐
 PostgreSQL │ MeczeMafSQLAlchemyRepository → MatchRecord → maf.training.MafTrainer │
 (READ ONLY)│   quality → features → design → model → nuts/fit → diagnostics       │
            │   → posterior (IAF, reszty, PPC) → validation (backtest)            │
            │   → artifacts.ArtifactStore  ⇒  var/maf/<model>/<wersja>/            │
            └──────────────────────────────────────────────────────────────────────┘
                                         │ summary.json, matches.json, draws.npz
            ┌──────────── aplikacja Flask ───────────────────────────────────────┐
            │ ModeleMafReadStore (contract) ← ArtifactStore                      │
            │ AtrakcyjnoscFrekwencyjnaService → maf.forecast (symulator, analiza   │
            │   gospodarza, porównanie) + BibliotekaMatematycznaService (linki)   │
            │ Atrakcyjnosc*View (JSON)  ← attendance_appeal.js (ECharts, KaTeX)   │
            │ Matematyka*View ← mathlib.registry / mathlib.render                 │
            └─────────────────────────────────────────────────────────────────────┘
```

| Warstwa | Pliki |
| --- | --- |
| Dostęp do danych | `infrastructure/repositories/attendance_appeal_repository.py` (SQL tylko do odczytu, `zamiana` gospodarza/gościa jak w raporcie frekwencji), `infrastructure/maf_store.py` (katalog artefaktów i pliki konfiguracji) |
| Przygotowanie i walidacja danych | `maf/quality.py` (NULL ≠ 0, zera, duplikaty, teren neutralny, pojemność nominalna/dostępna, korekty, wartości odstające), `maf/features.py` (forma, pozycja w tabeli, weekend, godzina, faza — bez wycieku przyszłości) |
| Model statystyczny | `maf/design.py`, `maf/zerosum.py`, `maf/model.py` (beta-dwumianowy z łączem logit i ujemny dwumianowy z łączem log, hierarchia, priory, analityczne gradienty) |
| Estymacja | `maf/nuts.py` (NUTS z adaptacją jak w Stanie), `maf/fit.py` (łańcuchy równolegle), `maf/diagnostics.py` (R-hat, ESS bulk/tail, E-BFMI) |
| Wyniki modelu | `maf/posterior.py` (IAF z próbek posterior, IAF sezonowy, indeks gospodarza, reszty predykcyjne, PPC, efekty współczynników), `maf/validation.py` (walidacja chronologiczna) |
| Przechowywanie | `maf/artifacts.py` — wersja, data, konfiguracja, priory, odcisk danych, diagnostyka, podsumowania posterior, zapisane próbki |
| API i prezentacja | `services/attendance_appeal_service.py`, `interface/admin/views/attendance_appeal_views.py`, `templates/admin/reports/attendance/maf_panel.html`, `static/js/attendance_appeal.js`, `static/css/attendance_appeal.css` |
| Dokumentacja matematyczna | pakiet `mathlib` (rejestr pojęć, bibliografia, artykuły, renderer), `services/mathematics_service.py`, `interface/mathematics/`, `templates/mathematics/`, `static/js/mathlib.js`, KaTeX w `static/vendor/katex` |

Pakiety `maf` i `mathlib` nie zależą od Flaska, bazy ani pakietu `handball` i mają angielskie nazwy jak biblioteki zewnętrzne. Są kopiowane bez zmian do `handball_datascience_ehf/handball_ehf/` — obie aplikacje działają niezależnie. Zmianę silnika lub treści wprowadza się w obu repozytoriach; zgodność treści pilnuje `src/mathlib/content/CHECKSUM` (test `test_suma_kontrolna_tresci_odpowiada_plikowi_checksum`), a wersje — `maf.__version__` i `mathlib.__version__`.

## Dlaczego własny sampler zamiast PyMC

Na stanowisku nie ma kompilatora C, a PyMC/PyTensor bez niego działa w trybie interpretowanym, wielokrotnie wolniej. Model ma jawną postać z analitycznymi gradientami, więc NUTS w NumPy/SciPy (ok. 400 linii) jest szybszy, w pełni odtwarzalny i testowany: zgodność gradientów z różnicami skończonymi, odtworzenie rozkładu normalnego o znanej kowariancji, odtworzenie parametrów z danych syntetycznych, teoretyczne ESS procesu AR(1). Diagnostyka odpowiada ArviZ (rank-normalized split R-hat i ESS wg Vehtari i in., 2021).

## Warianty modeli

| Klucz | Płeć | Miara | Dane |
| --- | --- | --- | --- |
| `M-wypelnienie` | M | wypełnienie hali (beta-dwumianowy) | mecze ze znaną frekwencją i pojemnością |
| `M-widzowie` | M | liczba widzów (ujemny dwumianowy) | wszystkie mecze ze znaną frekwencją |
| `K-wypelnienie` | K | wypełnienie hali | jw. |
| `K-widzowie` | K | liczba widzów | jw. |

Konfiguracja: `domain/attendance_appeal.py` (`MODELE_MAF`, `POJECIA_MAF` — mapowanie metryk dashboardu na pojęcia biblioteki).

## Trening

Trening nie zapisuje niczego w bazie. Odczytuje mecze w transakcji tylko do odczytu i zapisuje pliki do `var/maf/` (katalog w `.gitignore`; zmiana: zmienna `MAF_KATALOG`).

```powershell
uv run python -m handball.maf_cli                     # wszystkie modele
uv run python -m handball.maf_cli M-wypelnienie       # jeden model
uv run python -m handball.maf_cli K-widzowie --rozgrzewka 500 --probki 500 --bez-backtestu
```

Domyślnie: 4 łańcuchy równolegle, 1000 iteracji rozgrzewki i 1500 próbek, ziarno 20261010, walidacja chronologiczna (drugi trening bez dwóch ostatnich sezonów). Czas: od kilkunastu minut (kobiety) do kilku godzin (mężczyźni, liczba widzów). Każdy trening tworzy nową wersję `var/maf/<klucz>/<wersja>/` i aktualizuje `latest.json`; dashboard zawsze czyta najnowszą. Odtworzenie wyniku: te same dane (odcisk SHA-256 w `summary.json`), ziarno i wersje bibliotek zapisane w artefakcie.

## Konfiguracja danych

| Plik | Zawartość |
| --- | --- |
| `config/maf/kontynuacje_klubow.json` | Ciągłość klubów, które w bazie dostały nowy identyfikator zespołu (nowy podmiot). Mecze poprzednika są przypisywane następcy. Obecnie: Kielce (zespół 28 → 10813). |
| `config/maf/korekty_pojemnosci.json` | Pojemność dostępna w konkretnym sezonie (`id_hali` + `sezon`) albo meczu (`id_meczu`), gdy różni się od nominalnej `hale.pojemnosc`. |

Zmiana konfiguracji działa po ponownym treningu. Liczba przemapowanych meczów jest w raporcie jakości danych (`lineage_remapped`), a lista kontynuacji — w metadanych modelu.

## Wiarygodność

Dashboard pokazuje status modelu nad wszystkimi wynikami: **ok** (R-hat < 1,01, ESS bulk i tail ≥ 400, brak dywergencji, E-BFMI ≥ 0,3), **ostrzeżenie** albo **niewiarygodny**. Oszacowanie pojedynczego klubu jest oznaczone jako niepewne przy < 6 meczach jako rywal, przedziale 95% szerszym niż 60 pkt IAF albo słabej zbieżności jego IAF.

## Biblioteka Matematyka

- `src/mathlib/content/registry.json` — rejestr pojęć (identyfikator, nazwa, krótka definicja, dział, artykuł, kotwica, powiązania, modele, bibliografia), działy i planowane modele.
- `src/mathlib/content/bibliography.json` — wyłącznie zweryfikowane źródła (DOI w Crossref, URL odpowiedzią HTTP 200, 2026-10-10).
- `src/mathlib/content/articles/<dział>/<slug>.html` — 62 artykuły po 13 sekcji + strona naukowa MAF (20 sekcji).
- `src/mathlib/AUTHORING.md` — zasady pisania (kotwice, wzory numerowane, wykresy interaktywne, cytowania).

Kod odwołuje się do pojęć przez identyfikatory (`rejestr.url("rozklad-beta", "wzor")`), nigdy przez wpisane URL-e. Testy (`tests/unit/test_mathlib.py`, `tests/interface/test_mathematics_pages.py`) sprawdzają strukturę każdego artykułu, istnienie wszystkich linków `data-concept`, kotwic, wzorów, źródeł i typów wykresów, a także że każdy klucz metryki użyty w dashboardzie istnieje i prowadzi do istniejącej kotwicy.

### Dodanie nowego modelu sportowego

1. Dopisz pojęcie w `registry.json` (dział `modele-sportowe`, `"layout": "model"` jeśli strona ma strukturę naukową) i usuń je z `planned_models`.
2. Dodaj artykuł zgodnie z `AUTHORING.md`; brakujące pojęcia ogólne dopisz jako nowe artykuły w odpowiednich działach.
3. Przelicz `CHECKSUM` (`python -c "from mathlib.registry import default_registry; print(default_registry().checksum())"`) i skopiuj `content/` do drugiej aplikacji.
4. W kodzie modelu używaj identyfikatorów pojęć z rejestru.
