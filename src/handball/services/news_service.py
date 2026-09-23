from __future__ import annotations

from collections.abc import Callable, Sequence
from statistics import mean

from handball.contracts.news_repository import AktualnosciReadRepository
from handball.domain.news import (
    Aktualnosci,
    KategoriaRozgrywek,
    MeczAktualnosci,
    PozostalyMecz,
    RekordMeczu,
    RozgrywkiAktualnosci,
    SekcjaRozgrywek,
    StrzelecAktualnosci,
    WystepZRozgrywkami,
)

LICZBA_MECZOW_W_SEKCJI = 6
LICZBA_STRZELCOW_W_SEKCJI = 5
LICZBA_POZOSTALYCH_MECZOW = 12
LICZBA_NAJLEPSZYCH_WYSTEPOW = 3


class KategoriaRozgrywekPolicy:
    def kategoria(self, rozgrywki: RozgrywkiAktualnosci) -> KategoriaRozgrywek:
        nazwa = rozgrywki.nazwa.casefold()
        kobiety = (rozgrywki.plec or "").upper() == "K" or (
            rozgrywki.plec is None and "kobiet" in nazwa
        )
        if "superliga" in nazwa and "superpuchar" not in nazwa:
            return KategoriaRozgrywek.SUPERLIGA_K if kobiety else KategoriaRozgrywek.SUPERLIGA_M
        if "liga centralna" in nazwa:
            return (
                KategoriaRozgrywek.LIGA_CENTRALNA_K
                if kobiety
                else KategoriaRozgrywek.LIGA_CENTRALNA_M
            )
        return KategoriaRozgrywek.POZOSTALE


class AktualnosciService:
    def __init__(
        self,
        repozytorium: AktualnosciReadRepository,
        reguly: KategoriaRozgrywekPolicy | None = None,
    ) -> None:
        self._repozytorium = repozytorium
        self._reguly = reguly or KategoriaRozgrywekPolicy()

    def pobierz_aktualnosci(self) -> Aktualnosci:
        sezon = self._repozytorium.pobierz_biezacy_sezon()
        if sezon is None:
            return Aktualnosci(None, (), (), 0, 0, None, None, None, (), None)
        rozgrywki = {
            r.id_rozgrywki: r for r in self._repozytorium.pobierz_rozgrywki(sezon.id_sezon)
        }
        mecze = [
            m
            for m in self._repozytorium.pobierz_rozegrane_mecze(sezon.id_sezon)
            if m.id_rozgrywki in rozgrywki
        ]
        kategorie = {id_r: self._reguly.kategoria(r) for id_r, r in rozgrywki.items()}
        strzelcy = self._repozytorium.pobierz_strzelcow(sezon.id_sezon, LICZBA_STRZELCOW_W_SEKCJI)
        wystepy = self._repozytorium.pobierz_najlepsze_wystepy(
            sezon.id_sezon, LICZBA_NAJLEPSZYCH_WYSTEPOW
        )
        sekcje = tuple(
            sorted(
                (
                    self._sekcja(
                        kategorie[id_r],
                        rozgrywki[id_r],
                        [m for m in mecze if m.id_rozgrywki == id_r],
                        tuple(s for s in strzelcy if s.id_rozgrywki == id_r),
                    )
                    for id_r in rozgrywki
                    if kategorie[id_r].priorytetowa
                ),
                key=lambda sekcja: (sekcja.kategoria.kolejnosc, sekcja.rozgrywki.nazwa),
            )
        )
        pozostale = tuple(
            PozostalyMecz(m, rozgrywki[m.id_rozgrywki])
            for m in mecze
            if not kategorie[m.id_rozgrywki].priorytetowa
        )[:LICZBA_POZOSTALYCH_MECZOW]
        return Aktualnosci(
            sezon=sezon,
            sekcje=sekcje,
            pozostale_mecze=pozostale,
            liczba_rozegranych=len(mecze),
            suma_bramek=sum(m.suma_bramek for m in mecze),
            ostatni_termin=max((m.termin for m in mecze if m.termin), default=None),
            najwiecej_bramek=self._rekord(mecze, rozgrywki, lambda m: m.suma_bramek),
            najwyzsze_zwyciestwo=self._rekord(mecze, rozgrywki, lambda m: m.roznica_bramek),
            najlepsze_wystepy=tuple(
                WystepZRozgrywkami(w, rozgrywki[w.id_rozgrywki])
                for w in wystepy
                if w.id_rozgrywki in rozgrywki
            ),
            najbardziej_bramkostrzelna=max(
                (s for s in sekcje if s.srednia_bramek is not None),
                key=lambda s: s.srednia_bramek or 0.0,
                default=None,
            ),
        )

    @staticmethod
    def _sekcja(
        kategoria: KategoriaRozgrywek,
        rozgrywki: RozgrywkiAktualnosci,
        mecze: Sequence[MeczAktualnosci],
        strzelcy: tuple[StrzelecAktualnosci, ...],
    ) -> SekcjaRozgrywek:
        return SekcjaRozgrywek(
            kategoria=kategoria,
            rozgrywki=rozgrywki,
            liczba_rozegranych=len(mecze),
            srednia_bramek=mean(m.suma_bramek for m in mecze) if mecze else None,
            ostatnie_mecze=tuple(mecze[:LICZBA_MECZOW_W_SEKCJI]),
            strzelcy=strzelcy,
        )

    @staticmethod
    def _rekord(
        mecze: Sequence[MeczAktualnosci],
        rozgrywki: dict[int, RozgrywkiAktualnosci],
        miara: Callable[[MeczAktualnosci], int],
    ) -> RekordMeczu | None:
        if not mecze:
            return None
        najlepszy = max(mecze, key=miara)
        return RekordMeczu(najlepszy, rozgrywki[najlepszy.id_rozgrywki], miara(najlepszy))
