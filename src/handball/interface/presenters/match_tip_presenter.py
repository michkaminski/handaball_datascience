from __future__ import annotations

from dataclasses import replace

from handball.domain.match_rules import MeczPolicy
from handball.domain.match_tips import GrupaTypowan, RaportTypowan, TypowaniaKolejki, TypowanieMeczu
from handball.interface.presenters.match_prediction_presenter import PrognozaMeczuPresenter
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.presenters.schedule_presenter import KalendarzFormat
from handball.interface.view_models.match_predictions import OpcjaViewModel
from handball.interface.view_models.match_tips import (
    GrupaTypowanViewModel,
    RaportTypowanViewModel,
    TypowaniaKolejkiViewModel,
    TypowanieKolejkiViewModel,
    WierszTypowaniaViewModel,
)

BRAK = "—"


class TypowaniaPresenter:
    def __init__(
        self,
        prognozy: PrognozaMeczuPresenter,
        formatowanie: MeczFormat,
        reguly: MeczPolicy,
        kalendarz: KalendarzFormat,
    ) -> None:
        self._prognozy = prognozy
        self._format = formatowanie
        self._reguly = reguly
        self._kalendarz = kalendarz

    def przygotuj_kolejke(self, typowania: TypowaniaKolejki) -> TypowaniaKolejkiViewModel:
        return TypowaniaKolejkiViewModel(
            tytul=self._nazwa_kolejki(typowania.kolejka, typowania.nr_kolejki),
            mecze=tuple(self._typowanie_kolejki(t) for t in typowania.typowania),
        )

    def przygotuj_raport(self, raport: RaportTypowan) -> RaportTypowanViewModel:
        typowania = [t for grupa in raport.grupy for t in grupa.typowania]
        return RaportTypowanViewModel(
            tytul_modelu=raport.model.nazwa,
            wersja_modelu=raport.model.wersja,
            okres=self._okres(raport),
            liczba_meczow=len(typowania),
            liczba_rozegranych=sum(1 for t in typowania if t.prognoza.po_meczu is not None),
            liczba_przyszlych=sum(1 for t in typowania if t.prognoza.biezaca is not None),
            rozgrywki=tuple(OpcjaViewModel(nazwa, nazwa) for nazwa in raport.dostepne_rozgrywki),
            modele=tuple(OpcjaViewModel(opis.wersja, opis.nazwa) for opis in raport.modele),
            grupy=tuple(self._grupa(grupa) for grupa in raport.grupy),
        )

    def _okres(self, raport: RaportTypowan) -> str:
        od, do = raport.filtry.data_od, raport.filtry.data_do
        if od == do:
            return self._kalendarz.dzien(od)
        return f"{self._kalendarz.dzien(od)} – {self._kalendarz.dzien(do)}"

    def _grupa(self, grupa: GrupaTypowan) -> GrupaTypowanViewModel:
        czesci = (
            grupa.rozgrywki.strip(),
            grupa.sezon.strip(),
            (grupa.runda or "").strip(),
            self._nazwa_kolejki(grupa.kolejka, grupa.nr_kolejki),
        )
        return GrupaTypowanViewModel(
            naglowek=" · ".join(czesc for czesc in czesci if czesc),
            wiersze=tuple(self._wiersz(t, grupa.sezon) for t in grupa.typowania),
        )

    def _wiersz(self, typowanie: TypowanieMeczu, sezon: str) -> WierszTypowaniaViewModel:
        pozycja, prognoza = typowanie.pozycja, typowanie.prognoza
        termin = pozycja.termin
        gospodarz, gosc = self._druzyny(typowanie)
        wiersz = WierszTypowaniaViewModel(
            id_mecz=pozycja.id_mecz,
            tryb="brak",
            data=termin.strftime("%d.%m.%Y") if termin else BRAK,
            godzina=termin.strftime("%H:%M") if termin and pozycja.godzina_znana else BRAK,
            sezon=sezon or BRAK,
            kolejka=str(pozycja.nr_kolejki) if pozycja.nr_kolejki is not None else BRAK,
            gospodarz=gospodarz,
            gosc=gosc,
            wynik=self._wynik(typowanie),
        )
        if prognoza.po_meczu is not None:
            return replace(
                wiersz, tryb="po_meczu", po_meczu=self._prognozy.pozycja(prognoza.po_meczu)
            )
        if prognoza.biezaca is not None:
            return replace(
                wiersz,
                tryb="biezaca",
                przyszla=self._prognozy.prognoza_przyszla(prognoza.biezaca),
            )
        return replace(wiersz, opis_braku=self._prognozy.opis_braku(prognoza.powod_braku))

    def _typowanie_kolejki(self, typowanie: TypowanieMeczu) -> TypowanieKolejkiViewModel:
        prognoza = typowanie.prognoza
        punktowa = (
            prognoza.po_meczu.prognoza
            if prognoza.po_meczu is not None
            else prognoza.biezaca.prognoza
            if prognoza.biezaca is not None
            else None
        )
        gospodarz, gosc = self._druzyny(typowanie)
        return TypowanieKolejkiViewModel(
            id_mecz=typowanie.pozycja.id_mecz,
            naglowek=f"{gospodarz} — {gosc}",
            wskazniki=self._prognozy.wskazniki_typowania(punktowa) if punktowa else (),
            opis_braku=(None if punktowa else self._prognozy.opis_braku(prognoza.powod_braku)),
        )

    def _druzyny(self, typowanie: TypowanieMeczu) -> tuple[str, str]:
        prognoza = typowanie.prognoza
        mecz = (
            prognoza.po_meczu.mecz
            if prognoza.po_meczu is not None
            else prognoza.biezaca.mecz
            if prognoza.biezaca is not None
            else None
        )
        if mecz is not None:
            return mecz.gospodarz.nazwa, mecz.gosc.nazwa
        pozycja = typowanie.pozycja
        gospodarz, gosc = self._reguly.para(pozycja.mecz, pozycja.gospodarz, pozycja.gosc)
        return self._format.tekst(gospodarz), self._format.tekst(gosc)

    def _wynik(self, typowanie: TypowanieMeczu) -> str:
        mecz = typowanie.pozycja.mecz
        gospodarza, goscia = self._reguly.para(mecz, mecz.wynik_gosp_full, mecz.wynik_gosc_full)
        if gospodarza is None or goscia is None:
            return BRAK
        return f"{gospodarza}:{goscia}"

    def _nazwa_kolejki(self, nazwa: str | None, nr: int | None) -> str:
        return (nazwa or "").strip() or (f"Kolejka {nr}" if nr is not None else "Bez kolejki")
