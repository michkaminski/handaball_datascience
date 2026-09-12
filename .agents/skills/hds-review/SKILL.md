---
name: hds-review
description: Przegląd zmian Handball DataScience pod kątem błędów Flaska, uprawnień administracji i poprawności statystyk meczowych. Używaj przy zleconym review lub audycie konkretnej zmiany.
---

# Przegląd zmiany

Ustal zakres przeglądu i przeczytaj zmienione pliki wraz z ich wywołaniami. Odnieś zachowanie do [PROJECT](../../../docs/PROJECT.md), a obliczenia do [DATA](../../../docs/DATA.md).

Dla zmian kodu zastosuj [CODING_STANDARDS](../../../docs/CODING_STANDARDS.md), a dobór bibliotek sprawdź w [TECH_STACK](../../../docs/TECH_STACK.md).

Sprawdź obszary dotyczące zmiany:

- Obiektową implementację, zasady SOLID, spójność odpowiedzialności klas i wstrzykiwanie zależności.
- Typowanie kontraktów, izolację logiki od Flaska, cykl życia sesji SQLAlchemy, lazy loading oraz zapytania N+1.

- Poprawność identyfikatorów, filtrów sezonu i rozgrywek, kardynalności JOIN oraz paginacji.
- Brak danych wobec zera, normalizacja gospodarza, wynik końcowy wobec serii karnych i mianowniki statystyk.
- Uprawnienia operacji administracyjnych, walidacja, parametryzacja SQL i renderowanie tekstu źródłowego.
- Brak niezamierzonego importu, DDL i zapisów do rzeczywistej bazy przy starcie lub testach.
- Testy potwierdzające zachowanie, a nie tylko odwzorowujące kod.

Zgłaszaj konkretne problemy wraz z plikiem, linią, warunkiem wystąpienia i skutkiem. Oddziel potwierdzone błędy od pytań wymagających danych. Nie wymyślaj problemów, aby zapełnić listę; napisz wprost, jeśli ich nie wykryto, i podaj ograniczenia weryfikacji.

Samo zlecenie review nie oznacza zlecenia zmian kodu. Jeśli użytkownik zlecił również naprawy, wykonaj je i zweryfikuj w odpowiednim zakresie.
