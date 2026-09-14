---
name: hds-flask-feature
description: Obiektowa implementacja widoków, filtrów i administracji Flask w Handball DataScience, zgodnie z SOLID i z użyciem SQLAlchemy do istniejącej bazy. Używaj do zmian aplikacji, nie do pobierania archiwum ani budowy publicznego eksportu.
---

# Funkcja Flaska

Przeczytaj [PROJECT](../../../docs/PROJECT.md), [ARCHITECTURE](../../../docs/ARCHITECTURE.md) i [CODING_STANDARDS](../../../docs/CODING_STANDARDS.md). Przy konfiguracji lub zależnościach użyj [TECH_STACK](../../../docs/TECH_STACK.md). Sprawdź aktualny kod i komendy projektu; brak szkieletu oznacza potrzebę minimalnej implementacji, a nie użycia starszego `run.py`.

Ustal zachowanie użytkownika i kryterium ukończenia konkretnej funkcji. Dla funkcji opartej na danych sprawdź odpowiednie reguły w [DATA](../../../docs/DATA.md), w szczególności przy wyświetlaniu wyników lub obliczaniu statystyk.

Pracuj jako specjalista Flask, SQLAlchemy i obiektowego Pythona. Widoki implementuj jako MethodView, przypadki użycia jako klasy serwisów, a dostęp do bazy jako repozytoria SQLAlchemy z wąskimi kontraktami. Zależności przekazuj przez konstruktor; stosuj typowane obiekty wejścia i wyniku oraz kryteria SOLID z CODING_STANDARDS.

Zachowaj istniejący schemat. Definiowanie modeli nie upoważnia do create_all(), migracji ani zapisów; operacje na bazie wymagają wyraźnej prośby użytkownika. Oddziel zapytania i interpretację danych od szablonów. Dodawaj tylko strukturę potrzebną funkcji. Obsłuż pusty wynik, brak rekordu i niedostępną bazę jako różne stany. W listach zadbaj o paginację, stabilne sortowanie oraz zachowanie filtrów. Sortowanie na liście z filtrami realizuj przez klikalny nagłówek kolumny (rosnąco/malejąco), nie przez osobne pole w panelu filtrów — patrz [CODING_STANDARDS](../../../docs/CODING_STANDARDS.md), sekcja "Listy z filtrami".

Dla operacji administracyjnej określ, kto może ją wykonać i które dane zmienia. Sprawdź uwierzytelnienie, uprawnienia, walidację i ochronę formularza przed wdrożeniem zapisu. Nie zakładaj, że administracja oznacza edycję wszystkich tabel źródłowych.

Zweryfikuj zachowanie testem odpowiadającym ryzyku zmiany, używając odizolowanych danych. Zaktualizuj komendy w README, jeśli dodano rzeczywistą możliwość uruchomienia. Nie opisuj poleceń jako sprawdzonych, jeśli nie zostały wykonane.
