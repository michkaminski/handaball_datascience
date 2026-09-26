from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol

from handball.contracts.match_tip_repository import TypowaniaReadRepository
from handball.contracts.schedule_repository import TerminarzReadRepository
from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.match_predictions import PrognozaZapowiedzi, WzorceNazwLig
from handball.domain.match_tips import (
    FiltryTypowan,
    GrupaTypowan,
    PozycjaTypowania,
    RaportTypowan,
    TypowaniaKolejki,
    TypowanieMeczu,
    WyborTypowan,
)
from handball.domain.schedule import FiltryTerminarza
from handball.services.match_prediction_service import KatalogModeliPrognoz
from handball.services.match_preview_service import Zegar


class PrognozyMeczowProvider(Protocol):
    def pobierz_wiele(
        self, wersja_modelu: str, id_meczow: Iterable[int]
    ) -> dict[int, PrognozaZapowiedzi]: ...


class TypowaniaKolejkiService:
    def __init__(
        self,
        repozytorium: TerminarzReadRepository,
        prognozy: PrognozyMeczowProvider,
        katalog: KatalogModeliPrognoz,
    ) -> None:
        self._repozytorium = repozytorium
        self._prognozy = prognozy
        self._katalog = katalog

    def pobierz(self, filtry: FiltryTerminarza, wersja_modelu: str) -> TypowaniaKolejki:
        opis = self._katalog.definicja(wersja_modelu).opis
        pozycje = self._repozytorium.pobierz_mecze(filtry)
        prognozy = (
            self._prognozy.pobierz_wiele(wersja_modelu, [p.id_mecz for p in pozycje])
            if pozycje
            else {}
        )
        pierwsza = pozycje[0] if pozycje else None
        return TypowaniaKolejki(
            model=opis,
            kolejka=pierwsza.kolejka if pierwsza else None,
            nr_kolejki=pierwsza.nr_kolejki if pierwsza else None,
            typowania=tuple(TypowanieMeczu(p, prognozy[p.id_mecz]) for p in pozycje),
        )


class RaportTypowanService:
    def __init__(
        self,
        repozytorium: TypowaniaReadRepository,
        prognozy: PrognozyMeczowProvider,
        katalog: KatalogModeliPrognoz,
        wzorce: WzorceNazwLig,
        zegar: Zegar,
        kolejnosc: KolejnoscRozgrywekPolicy,
    ) -> None:
        self._repozytorium = repozytorium
        self._prognozy = prognozy
        self._katalog = katalog
        self._wzorce = wzorce
        self._zegar = zegar
        self._kolejnosc = kolejnosc

    def filtry(self, wybor: WyborTypowan) -> FiltryTypowan:
        dzis = self._zegar.teraz().date()
        data_od = wybor.data_od or wybor.data_do or dzis
        data_do = wybor.data_do or wybor.data_od or dzis
        if data_od > data_do:
            raise ValueError("Data od nie może być późniejsza niż data do.")
        wersja = wybor.wersja_modelu or self._katalog.domyslna_wersja
        self._katalog.definicja(wersja)
        return FiltryTypowan(data_od, data_do, wersja, wybor.rozgrywki)

    def pobierz_raport(self, filtry: FiltryTypowan) -> RaportTypowan:
        opis = self._katalog.definicja(filtry.wersja_modelu).opis
        dostepne = self._repozytorium.pobierz_rozgrywki(
            filtry.data_od, filtry.data_do, self._wzorce
        )
        pozycje = self._repozytorium.pobierz_mecze(
            filtry.data_od, filtry.data_do, filtry.rozgrywki, self._wzorce
        )
        prognozy = (
            self._prognozy.pobierz_wiele(filtry.wersja_modelu, [p.pozycja.id_mecz for p in pozycje])
            if pozycje
            else {}
        )
        return RaportTypowan(
            filtry=filtry,
            model=opis,
            modele=self._katalog.modele(),
            dostepne_rozgrywki=tuple(
                sorted({*dostepne, *filtry.rozgrywki}, key=self._kolejnosc.klucz)
            ),
            grupy=self._grupuj(pozycje, prognozy),
        )

    def _grupuj(
        self, pozycje: Sequence[PozycjaTypowania], prognozy: dict[int, PrognozaZapowiedzi]
    ) -> tuple[GrupaTypowan, ...]:
        grupy: dict[tuple[int, int | None, int | None], list[PozycjaTypowania]] = {}
        for p in pozycje:
            klucz = (p.id_rozgrywki, p.pozycja.id_runda, p.pozycja.id_kolejka)
            grupy.setdefault(klucz, []).append(p)
        uporzadkowane = sorted(
            grupy.values(), key=lambda elementy: self._kolejnosc.poziom(elementy[0].rozgrywki)
        )
        return tuple(
            GrupaTypowan(
                rozgrywki=elementy[0].rozgrywki,
                sezon=elementy[0].sezon,
                runda=elementy[0].pozycja.runda,
                kolejka=elementy[0].pozycja.kolejka,
                nr_kolejki=elementy[0].pozycja.nr_kolejki,
                typowania=tuple(
                    TypowanieMeczu(e.pozycja, prognozy[e.pozycja.id_mecz])
                    for e in sorted(elementy, key=self._klucz_czasu)
                ),
            )
            for elementy in uporzadkowane
        )

    def _klucz_czasu(self, p: PozycjaTypowania) -> tuple[bool, str, int]:
        termin = p.pozycja.termin
        return (termin is None, termin.isoformat() if termin else "", p.pozycja.id_mecz)
