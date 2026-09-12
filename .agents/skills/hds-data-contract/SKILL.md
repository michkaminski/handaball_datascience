---
name: hds-data-contract
description: Mapowanie istniejącej bazy ZPRP do widoków i statystyk Handball DataScience. Używaj przy projektowaniu zapytań, relacji i interpretacji wyników meczów.
---

# Kontrakt danych Handball DataScience

Katalog projektu to trzeci katalog nadrzędny względem folderu tego skilla. Przeczytaj [DATA](../../../docs/DATA.md) i odpowiedni fragment wskazanego tam schematu.

Zacznij od informacji potrzebnych w widoku lub obliczeniu. Dla każdej wskaż tabelę, kolumnę, klucz łączenia, obsługę braku danych i ewentualne przekształcenie. Oznacz osobno fakty ze schematu, obserwacje z bazy i założenia.

Jeżeli połączenie jest dostępne w ramach zadania, sprawdź metadane i małą próbkę tylko do odczytu. Bez połączenia przygotuj mapowanie wstępne i nazwij elementy wymagające potwierdzenia. Nie uruchamiaj importu ani DDL.

Sprawdź kardynalność połączeń, aby składy i inne relacje jeden-do-wielu nie mnożyły sum bramek. Przy sezonach używaj odpowiedniej migawki drużyny. Przy wynikach ustal normalizację `zamiana` i odrębność serii karnych. Przy agregatach określ mianownik oraz kompletność danych.

Zakończ mapowaniem wystarczającym do implementacji oraz listą rzeczywistych niepewności. Trwałe ustalenia domenowe dopisz do DATA, bez kopiowania rekordów i danych osobowych.
