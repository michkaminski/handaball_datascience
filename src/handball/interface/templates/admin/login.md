# Logowanie administratora

Status: projekt szablonu. Plik `login.html` nie został jeszcze utworzony. Ten MD będzie znajdował się obok niego i będzie aktualizowany wraz ze zmianą szablonu.

Docelowy szablon względem katalogu szablony: `admin/login.html`.

## Przeznaczenie

Formularz dostępu do panelu, planowany na etap 6. Nie potwierdzono osobnego ekranu logowania w prototypie; korzysta ze wspólnej stylistyki v6.

## Dane wejściowe

Formularz logowania, błędy walidacji i bezpieczny adres powrotu z warstwy HTTP. Sposób logowania zależy od przyszłej decyzji o kontach.

## Powiązania

Planowany widok i formularz logowania oraz Flask-Login. Korzysta z base.html; nawigacja powinna uwzględnić brak zalogowania.

## Gdzie wprowadzać zmiany

Tutaj zmieniaj pola i wygląd formularza zgodnie z ustalonym mechanizmem. Uwierzytelnianie, CSRF, uprawnienia i walidację przekierowania implementuj poza szablonem.

## Sprawdzenie zmiany

Sprawdź błędne logowanie, walidację, dostępność formularza i przekierowanie. Nie zapisuj haseł ani nie twórz tabel kont na podstawie tego dokumentu.

## Stan implementacji

Nie ma jeszcze bloków Jinja2, selektorów CSS ani powiązań JS do potwierdzenia. Przy implementacji zastąp ten zapis rzeczywistymi nazwami bloków, selektorów i plików testów; nie wpisuj planowanych kontroli jako wykonanych.

## Układ tekstowy i mapa zmian

Stan: **plan — brak odpowiadającego HTML**. Poniżej tekstowa mapa zakresu z dotychczasowej notatki, nie zatwierdzony projekt rozmieszczenia pól.

```text
[planowana wspólna rama: base.html]
+------------------------------------------------------------+
| Logowanie administratora
| [formularz dostępu: pola jeszcze nieustalone]
| [komunikat błędu / wynik logowania]
| [akcja wysłania formularza — do zaprojektowania]
+------------------------------------------------------------+
[planowana stopka wspólnego układu]
```

Nie ustalono źródła kont ani dokładnego sposobu logowania; rysunek nie przesądza, że użyty zostanie login i hasło.

Układ mobilny, dokładne etykiety i selektory nie są jeszcze ustalone. Po powstaniu HTML zastąp ten schemat rzeczywistym rozmieszczeniem, opisz warunki widoczności oraz dodaj mapę konkretnych pól i przycisków.

### Mapa zmian

| Element rysunku / zmiana | Gdzie zmieniać | Co zmieniać |
| --- | --- | --- |
| Zakres i przyszły układ | [login.md](login.md) | Najpierw uzupełnij ten opis; planowany plik `login.html` jeszcze nie istnieje. |
| Wspólna rama strony | [base.md](../base.md) | Opis nagłówka, menu, sidebara, miejsca treści i stopki; sposób użycia dla tego ekranu potwierdź przy implementacji. |
