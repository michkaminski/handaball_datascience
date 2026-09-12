# Role i skillsy AI

Role opisują odpowiedzialność podczas zadania. Jeden agent może wykonywać je kolejno. Dokument nie uruchamia subagentów i nie włącza delegowania; równoległa praca wymaga osobnego polecenia użytkownika.

| Rola | Zadanie | Wynik pracy |
| --- | --- | --- |
| Prowadzący / architekt | Utrzymuje zakres, rozstrzyga potrzebne decyzje i integruje wynik | Spójna zmiana z aktualnym statusem |
| Specjalista danych | Sprawdza schemat, relacje i znaczenie statystyk | Mapowanie pól, wykryte niepewności i reguły obliczeń |
| Specjalista Flask / obiektowego Pythona | Projektuje i implementuje klasy Flask, serwisy, repozytoria SQLAlchemy oraz jawne kontrakty zgodnie z SOLID | Typowana, działająca funkcja z poprawnym zakresem sesji i właściwą weryfikacją |
| Recenzent | Sprawdza SOLID, odpowiedzialności klas, zależności, sesje ORM, błędy i uprawnienia | Ustalenia z lokalizacją, skutkiem i sposobem odtworzenia |

Implementacja wymaga kompetencji specjalisty Flask, SQLAlchemy i obiektowego Pythona. Konkretne kryteria jakości określa [CODING_STANDARDS](CODING_STANDARDS.md), a wybór bibliotek [TECH_STACK](TECH_STACK.md).

## Skillsy projektu

- [hds-data-contract](../.agents/skills/hds-data-contract/SKILL.md): mapowanie bazy i interpretacja danych przed zapytaniami lub statystykami.
- [hds-flask-feature](../.agents/skills/hds-flask-feature/SKILL.md): implementacja funkcji Flaska w granicach istniejącego modelu danych.
- [hds-review](../.agents/skills/hds-review/SKILL.md): przegląd zmian w aplikacji i danych, gdy zostanie zlecony.

Dobieraj skill do zadania; nie czytaj wszystkich automatycznie. Instrukcje wspólne są w AGENTS.md, a fakty domenowe w DATA.md.

## Przekazanie pracy

Przy zmianie sesji lub przekazaniu zadania podaj: cel, zmienione pliki, podjęte decyzje, wykonane sprawdzenia i pozostały problem. STATUS ma przechowywać aktualny stan projektu, bez transkrypcji rozmów i sekretów.

Jeśli użytkownik zleci równoległą pracę, podziel ją na niezależne zadania z jawną odpowiedzialnością za pliki. Prowadzący sprawdza razem rezultaty przed ogłoszeniem ukończenia.
