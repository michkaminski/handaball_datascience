from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from datetime import date

from handball.domain.match_preview import CzlonekKadry, KadraDruzyny
from handball.domain.match_protocol import KolejnoscZawodnikowProtokoluPolicy, ProtokolMeczu
from handball.interface.presenters.match_protocol_presenter import SKROTY_POZYCJI
from handball.interface.view_models.match_protocol import PlikProtokoluLiveViewModel

FORMAT_PROTOKOLU_LIVE = "protokol_live"
WERSJA_PROTOKOLU_LIVE = 1


class NazwaPlikuProtokoluPolicy:
    ZAMIANY = str.maketrans(
        {"ł": "l", "Ł": "L", "ß": "ss", "æ": "ae", "Æ": "AE", "ø": "o", "Ø": "O"}
    )

    def nazwa(self, dzien: date, gospodarz: str, gosc: str) -> str:
        return f"{dzien.isoformat()}_{self.czesc(gospodarz)}_{self.czesc(gosc)}"

    def czesc(self, tekst: str) -> str:
        ascii_ = (
            unicodedata.normalize("NFKD", tekst.translate(self.ZAMIANY))
            .encode("ascii", "ignore")
            .decode()
        )
        return re.sub(r"[^A-Za-z0-9]+", "-", ascii_).strip("-") or "druzyna"


class NumeryProtokoluLivePolicy:
    PIERWSZY_WOLNY = 100

    def numery(self, czlonkowie: Sequence[CzlonekKadry]) -> list[int]:
        zajete: set[int] = set()
        wlasne: list[int | None] = []
        for czlonek in czlonkowie:
            numer = min(czlonek.numery) if czlonek.numery else None
            if numer is not None and numer not in zajete:
                zajete.add(numer)
                wlasne.append(numer)
            else:
                wlasne.append(None)
        wolny = self.PIERWSZY_WOLNY
        wynik = []
        for numer in wlasne:
            if numer is None:
                while wolny in zajete:
                    wolny += 1
                numer = wolny
                zajete.add(wolny)
            wynik.append(numer)
        return wynik


class ProtokolLivePresenter:
    def __init__(
        self,
        kolejnosc: KolejnoscZawodnikowProtokoluPolicy,
        numery: NumeryProtokoluLivePolicy,
        nazwy: NazwaPlikuProtokoluPolicy,
    ) -> None:
        self._kolejnosc = kolejnosc
        self._numery = numery
        self._nazwy = nazwy

    def przygotuj(self, protokol: ProtokolMeczu) -> PlikProtokoluLiveViewModel:
        mecz, hala = protokol.mecz, protokol.dane.hala
        termin = mecz.termin
        dzien = (termin or protokol.stan_na).date()
        gospodarz = (protokol.gospodarz.druzyna.nazwa or "").strip()
        gosc = (protokol.gosc.druzyna.nazwa or "").strip()
        nazwa_hali = ((hala.nazwa or "") if hala else "").strip() or (mecz.hala or "")
        adres = ""
        if hala:
            ulica = " ".join(c for c in (hala.ulica, hala.numer) if c)
            adres = ", ".join(c for c in (ulica, hala.miasto) if c)
        dane_meczu: dict[str, object] = {
            "id": mecz.id_mecz,
            "competition": " · ".join(
                c for c in (mecz.rozgrywki, mecz.sezon, mecz.runda, mecz.kolejka) if c
            ),
            "date": dzien.strftime("%d.%m.%Y"),
            "time": termin.strftime("%H:%M") if termin and mecz.data_faktyczna else "",
            "venue": ", ".join(c for c in (nazwa_hali, adres or mecz.miasto) if c),
            "statsNote": f"Statystyki sezonu {mecz.sezon or ''} (M, Br, Śr) — stan na "
            f"{protokol.stan_na.strftime('%d.%m.%Y %H:%M')}.",
            "A": self._druzyna(protokol.gospodarz, protokol),
            "B": self._druzyna(protokol.gosc, protokol),
        }
        if hala and hala.pojemnosc:
            dane_meczu["capacity"] = hala.pojemnosc
        return PlikProtokoluLiveViewModel(
            nazwa_bazowa=self._nazwy.nazwa(dzien, gospodarz, gosc),
            dokument={
                "format": FORMAT_PROTOKOLU_LIVE,
                "version": WERSJA_PROTOKOLU_LIVE,
                "match": dane_meczu,
            },
        )

    def _druzyna(self, kadra: KadraDruzyny, protokol: ProtokolMeczu) -> dict[str, object]:
        czlonkowie = [w.czlonek for w in self._kolejnosc.wiersze(kadra, protokol.kolejnosc)]
        nazwa = (kadra.druzyna.nazwa or "").strip()
        return {
            "name": nazwa,
            "short": nazwa,
            "players": [
                self._zawodnik(czlonek, numer)
                for czlonek, numer in zip(czlonkowie, self._numery.numery(czlonkowie), strict=True)
            ],
        }

    def _zawodnik(self, czlonek: CzlonekKadry, numer: int) -> dict[str, object]:
        sezon = czlonek.sezon
        nazwa = (
            " ".join(c for c in ((czlonek.nazwisko or "").upper(), czlonek.imie or "") if c)
            or f"#{czlonek.id_zawodnik}"
        )
        return {
            "nr": numer,
            "name": nazwa,
            "pos": self._pozycja(czlonek.pozycja),
            "ur": f"{czlonek.data_urodzenia.year % 100:02d}" if czlonek.data_urodzenia else "",
            "m": sezon.mecze if sezon else None,
            "br": sezon.bramki if sezon else None,
            "sr": round(czlonek.srednia, 2) if czlonek.srednia is not None else None,
        }

    def _pozycja(self, pozycja: str | None) -> str:
        nazwa = (pozycja or "").casefold()
        return next((skrot for prefiks, skrot in SKROTY_POZYCJI if nazwa.startswith(prefiks)), "")
