from __future__ import annotations

from dataclasses import dataclass

from handball.interface.view_models.match_predictions import (
    OpcjaViewModel,
    PozycjaPrognozyViewModel,
    PrognozaPrzyszlaViewModel,
    WskaznikZapowiedziViewModel,
)


@dataclass(frozen=True)
class TypowanieKolejkiViewModel:
    id_mecz: int
    naglowek: str
    wskazniki: tuple[WskaznikZapowiedziViewModel, ...]
    opis_braku: str | None


@dataclass(frozen=True)
class TypowaniaKolejkiViewModel:
    tytul: str
    mecze: tuple[TypowanieKolejkiViewModel, ...]


@dataclass(frozen=True)
class WierszTypowaniaViewModel:
    id_mecz: int
    tryb: str
    data: str
    godzina: str
    sezon: str
    kolejka: str
    gospodarz: str
    gosc: str
    wynik: str
    po_meczu: PozycjaPrognozyViewModel | None = None
    przyszla: PrognozaPrzyszlaViewModel | None = None
    opis_braku: str | None = None


@dataclass(frozen=True)
class GrupaTypowanViewModel:
    naglowek: str
    wiersze: tuple[WierszTypowaniaViewModel, ...]


@dataclass(frozen=True)
class RaportTypowanViewModel:
    tytul_modelu: str
    wersja_modelu: str
    okres: str
    liczba_meczow: int
    liczba_rozegranych: int
    liczba_przyszlych: int
    rozgrywki: tuple[OpcjaViewModel, ...]
    modele: tuple[OpcjaViewModel, ...]
    grupy: tuple[GrupaTypowanViewModel, ...]
