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
