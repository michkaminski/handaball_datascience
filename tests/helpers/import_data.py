import json
from urllib.parse import urlencode

from handball.domain.imports import BladImportu, ZadaniePobrania
from handball.infrastructure.zprp_client import ZprpClient


class ImportTestClient(ZprpClient):
    def __init__(self) -> None:
        self.wynik = "29"
        self.awaria = False
        self.zapytania: list[str] = []

    def pobierz(self, zadanie: ZadaniePobrania) -> tuple[str, bytes]:
        self.zapytania.append(zadanie.endpoint)
        if self.awaria:
            raise BladImportu("Testowa awaria API")
        mecz = {
            "Id": "206511",
            "ID_sezon": "195",
            "Id_rozgrywki": "12007",
            "ID_zespoly_gosp": "15890",
            "ID_zespoly_gosc": "0",
            "ID_zespoly_gosp_ZespolNazwa": "Testowy zespół",
            "wynik_gosp_full": self.wynik,
            "wynik_gosc_full": None,
            "data_fakt": "2026-09-06 15:00:00",
            "zamiana": "1",
            "Hala_nazwa": "Hala testowa",
            "Hala_miasto": "Testowo",
            "Hala_ulica": None,
            "Hala_numer": None,
        }
        dokumenty = {
            "pokaz_sezony.php": {"1": {"ID_sezon": "195", "Nazwa": "2026/2027"}},
            "pokaz_rozgrywki.php": {
                "1": {
                    "Id_rozgrywki": "12007",
                    "ID_sezon": "195",
                    "Kategoria": "1",
                    "Nazwa": "Superliga",
                }
            },
            "pokaz_rundy.php": {"1": {"Id": "31116", "Nazwa": "I runda"}},
            "pokaz_kolejki.php": {"1": {"ID_kolejka": "66727", "Nazwa": "Seria 1"}},
            "pokaz_mecze.php": {"1": mecz},
            "pokaz_mecze_szczegoly.php": {
                "0": [mecz],
                "gosp": {"100": {"imie": "Test", "nazwisko": "Testowy", "bramki": "3"}},
                "gosc": {},
            },
            "pokaz_sklad.php": [
                {
                    "ID_zespol": "15890",
                    "Sezon": "2026/2027",
                    "Kategoria": "Senior",
                    "Nazwa": "Testowy zespół",
                }
            ],
        }
        url = (
            "https://rozgrywki.zprp.pl/api/" + zadanie.endpoint + "?" + urlencode(zadanie.parametry)
        )
        return url, json.dumps(dokumenty[zadanie.endpoint], ensure_ascii=False).encode()
