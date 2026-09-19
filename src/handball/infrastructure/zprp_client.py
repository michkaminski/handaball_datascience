from __future__ import annotations

import json
from http.client import HTTPException
from threading import Lock
from time import monotonic, sleep
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from handball.domain.imports import BladImportu, ZadaniePobrania


class ZprpClient:
    def __init__(self) -> None:
        self._blokada = Lock()
        self._ostatnie_pobranie: float | None = None

    def pobierz(self, zadanie: ZadaniePobrania) -> tuple[str, bytes]:
        with self._blokada:
            if self._ostatnie_pobranie is not None:
                sleep(max(0.0, 3.0 - (monotonic() - self._ostatnie_pobranie)))
            self._ostatnie_pobranie = monotonic()
            return self._pobierz(zadanie)

    def _pobierz(self, zadanie: ZadaniePobrania) -> tuple[str, bytes]:
        url = "https://rozgrywki.zprp.pl/api/" + zadanie.endpoint
        if zadanie.parametry:
            url += "?" + urlencode(zadanie.parametry)
        zadanie_http = Request(
            url, headers={"Accept": "application/json", "User-Agent": "HandballDataScience/1.0"}
        )
        try:
            with urlopen(zadanie_http, timeout=25) as odpowiedz:
                tresc = odpowiedz.read(10_000_001)
            if len(tresc) > 10_000_000:
                raise BladImportu("Odpowiedź API przekroczyła limit 10 MB.")
            json.loads(tresc.decode("utf-8-sig"))
            return url, tresc
        except (OSError, HTTPException, ValueError) as blad:
            raise BladImportu(
                f"Nie udało się pobrać poprawnego JSON: {zadanie.endpoint}. Możesz ponowić krok."
            ) from blad
