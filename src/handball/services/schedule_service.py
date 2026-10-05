from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from handball.contracts.schedule_repository import TerminarzReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.options import OpcjaWyboru
from handball.domain.schedule import (
    DzienTerminarza,
    FiltryTerminarza,
    KolejkaTerminarza,
    OpcjeTerminarza,
    PozycjaTerminarza,
    RundaTerminarza,
    Terminarz,
    WyborTerminarza,
)


class NieznanySezonTerminarza(ValueError):
    pass


class TerminarzService:
    def __init__(
        self,
        repozytorium: TerminarzReadRepository,
        repozytorium_sezonow: SezonReadRepository,
        kolejnosc: KolejnoscRozgrywekPolicy,
    ) -> None:
        self._repozytorium = repozytorium
        self._repozytorium_sezonow = repozytorium_sezonow
        self._kolejnosc = kolejnosc

    def pobierz_opcje(self, wybor: WyborTerminarza) -> OpcjeTerminarza:
        sezony = self._repozytorium_sezonow.pobierz_wszystkie()
        id_sezon = self._sezon(sezony, wybor.id_sezon)
        if id_sezon is None:
            return OpcjeTerminarza(WyborTerminarza(), sezony)
        rozgrywki = self._kolejnosc.uporzadkuj_opcje(self._repozytorium.pobierz_rozgrywki(id_sezon))
        id_rozgrywki = self._dostepny(rozgrywki, wybor.id_rozgrywki)
        if id_rozgrywki is None:
            return OpcjeTerminarza(WyborTerminarza(id_sezon), sezony, rozgrywki)
        rundy = self._repozytorium.pobierz_rundy(id_rozgrywki)
        id_runda = self._dostepny(rundy, wybor.id_runda)
        kolejki = self._repozytorium.pobierz_kolejki(id_rozgrywki, id_runda)
        id_kolejka = self._dostepny(kolejki, wybor.id_kolejka)
        return OpcjeTerminarza(
            WyborTerminarza(id_sezon, id_rozgrywki, id_runda, id_kolejka),
            sezony,
            rozgrywki,
            rundy,
            kolejki,
        )

    def pobierz_terminarz(self, filtry: FiltryTerminarza) -> Terminarz:
        return Terminarz(filtry, self._grupuj(self._repozytorium.pobierz_mecze(filtry)))

    def _sezon(self, sezony: Sequence[OpcjaWyboru], id_sezon: int | None) -> int | None:
        if id_sezon is None:
            return sezony[0].wartosc if sezony else None
        if not any(sezon.wartosc == id_sezon for sezon in sezony):
            raise NieznanySezonTerminarza(f"Nieznany sezon: {id_sezon}.")
        return id_sezon

    def _dostepny(self, opcje: Sequence[OpcjaWyboru], wartosc: int | None) -> int | None:
        return wartosc if any(opcja.wartosc == wartosc for opcja in opcje) else None

    def _grupuj(self, pozycje: Sequence[PozycjaTerminarza]) -> tuple[RundaTerminarza, ...]:
        rundy: dict[int | None, tuple[str | None, dict[int | None, list[PozycjaTerminarza]]]] = {}
        for pozycja in pozycje:
            _, kolejki = rundy.setdefault(pozycja.id_runda, (pozycja.runda, {}))
            kolejki.setdefault(pozycja.id_kolejka, []).append(pozycja)
        return tuple(
            RundaTerminarza(
                id_runda, nazwa, tuple(self._kolejka(mecze) for mecze in kolejki.values())
            )
            for id_runda, (nazwa, kolejki) in rundy.items()
        )

    def _kolejka(self, mecze: Sequence[PozycjaTerminarza]) -> KolejkaTerminarza:
        dni: dict[date | None, list[PozycjaTerminarza]] = {}
        for pozycja in mecze:
            termin = pozycja.termin
            dni.setdefault(termin.date() if termin else None, []).append(pozycja)
        pierwszy = mecze[0]
        return KolejkaTerminarza(
            pierwszy.id_kolejka,
            pierwszy.kolejka,
            pierwszy.nr_kolejki,
            tuple(DzienTerminarza(dzien, tuple(pozycje)) for dzien, pozycje in dni.items()),
        )
