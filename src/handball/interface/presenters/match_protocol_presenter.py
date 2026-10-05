from __future__ import annotations

from handball.domain.match_preview import KadraDruzyny
from handball.domain.match_protocol import (
    DaneProtokolu,
    HalaProtokolu,
    KolejnoscProtokolu,
    KolejnoscZawodnikowProtokoluPolicy,
    ProtokolMeczu,
    WierszZawodnikaProtokolu,
)
from handball.interface.view_models.match_protocol import (
    DruzynaProtokoluViewModel,
    ProtokolMeczuViewModel,
    SedziaProtokoluViewModel,
    UkladProtokoluViewModel,
    ZawodnikProtokoluViewModel,
)

SKROTY_POZYCJI = (("bramkarz", "B"), ("rozgrywający", "R"), ("skrzydłowy", "S"), ("obrotowy", "O"))
BRAK = "–"
LICZBA_WYROZNIONYCH_STRZELCOW = 4

OBSADA_PROTOKOLU = (
    ("pierwszy", "sędzia główny"),
    ("drugi", "sędzia główny"),
    ("sekretarz", "sekretarz"),
    ("czas", "m. czas"),
    ("delegat", "delegat ZPRP"),
)


class UkladProtokoluPolicy:
    MIEJSCE_ZAWODNIKOW_MM = 173.0
    NAJWYZSZY_WIERSZ_MM = 5.2
    NAJNIZSZY_WIERSZ_MM = 3.0
    WIERSZE_PRZEBIEGU = 34
    OBRAMOWANIE_WIERSZA_MM = 0.2

    def uklad(self, liczba_zawodnikow: int) -> UkladProtokoluViewModel:
        wysokosc = (
            self.MIEJSCE_ZAWODNIKOW_MM / max(liczba_zawodnikow, 1) - self.OBRAMOWANIE_WIERSZA_MM
        )
        wysokosc = max(self.NAJNIZSZY_WIERSZ_MM, min(self.NAJWYZSZY_WIERSZ_MM, wysokosc))
        return UkladProtokoluViewModel(
            wysokosc_zawodnika_mm=round(wysokosc, 2),
            czcionka_zawodnika_pt=round(min(8.5, wysokosc * 1.6), 1),
            wiersze_przebiegu=self.WIERSZE_PRZEBIEGU,
        )


class ProtokolMeczuPresenter:
    def __init__(
        self, uklad: UkladProtokoluPolicy, kolejnosc: KolejnoscZawodnikowProtokoluPolicy
    ) -> None:
        self._uklad = uklad
        self._kolejnosc = kolejnosc

    def przygotuj(self, protokol: ProtokolMeczu) -> ProtokolMeczuViewModel:
        mecz, dane = protokol.mecz, protokol.dane
        termin = mecz.termin
        druzyny = (
            self._druzyna("A", protokol.gospodarz, protokol.kolejnosc),
            self._druzyna("B", protokol.gosc, protokol.kolejnosc),
        )
        return ProtokolMeczuViewModel(
            id_mecz=mecz.id_mecz,
            gospodarz=druzyny[0].druzyna,
            gosc=druzyny[1].druzyna,
            rozgrywki=mecz.rozgrywki or "",
            sezon=mecz.sezon or "",
            etap=" · ".join(czesc for czesc in (mecz.runda, mecz.kolejka) if czesc),
            data=termin.strftime("%d.%m.%Y") if termin else "",
            godzina=termin.strftime("%H:%M") if termin and mecz.data_faktyczna else "",
            hala=self._hala(dane.hala) or (mecz.hala or ""),
            adres=self._adres(dane.hala) or (mecz.miasto or ""),
            pojemnosc=str(dane.hala.pojemnosc) if dane.hala and dane.hala.pojemnosc else "",
            stan_na=protokol.stan_na.strftime("%d.%m.%Y %H:%M"),
            druzyny=druzyny,
            sedziowie=self._sedziowie(dane),
            uklad=self._uklad.uklad(sum(len(d.zawodnicy) for d in druzyny)),
        )

    def _druzyna(
        self, litera: str, kadra: KadraDruzyny, kolejnosc: KolejnoscProtokolu
    ) -> DruzynaProtokoluViewModel:
        return DruzynaProtokoluViewModel(
            litera=litera,
            druzyna=(kadra.druzyna.nazwa or "").strip(),
            zawodnicy=tuple(
                self._zawodnik(wiersz) for wiersz in self._kolejnosc.wiersze(kadra, kolejnosc)
            ),
            ze_skladu=kadra.ze_skladu,
        )

    def _zawodnik(self, wiersz: WierszZawodnikaProtokolu) -> ZawodnikProtokoluViewModel:
        czlonek = wiersz.czlonek
        sezon = czlonek.sezon
        return ZawodnikProtokoluViewModel(
            numer="/".join(str(n) for n in czlonek.numery),
            nazwa=" ".join(c for c in (czlonek.nazwisko, czlonek.imie) if c)
            or f"#{czlonek.id_zawodnik}",
            nowa_grupa=wiersz.nowa_grupa,
            pozycja=self._pozycja(czlonek.pozycja),
            rocznik=f"{czlonek.data_urodzenia.year % 100:02d}" if czlonek.data_urodzenia else "",
            mecze=str(sezon.mecze) if sezon else BRAK,
            bramki=str(sezon.bramki) if sezon else BRAK,
            srednia=f"{czlonek.srednia:.1f}" if czlonek.srednia is not None else BRAK,
            wyroznij_bramki=czlonek.miejsce_strzelca is not None
            and czlonek.miejsce_strzelca <= LICZBA_WYROZNIONYCH_STRZELCOW,
        )

    def _pozycja(self, pozycja: str | None) -> str:
        nazwa = (pozycja or "").casefold()
        return next((skrot for prefiks, skrot in SKROTY_POZYCJI if nazwa.startswith(prefiks)), "")

    def _hala(self, hala: HalaProtokolu | None) -> str:
        return (hala.nazwa or "").strip() if hala else ""

    def _adres(self, hala: HalaProtokolu | None) -> str:
        if hala is None:
            return ""
        ulica = " ".join(c for c in (hala.ulica, hala.numer) if c)
        return ", ".join(c for c in (ulica, hala.miasto) if c)

    def _sedziowie(self, dane: DaneProtokolu) -> tuple[SedziaProtokoluViewModel, ...]:
        wynik = []
        for rola, funkcja in OBSADA_PROTOKOLU:
            sedzia = dane.sedzia(rola)
            wynik.append(
                SedziaProtokoluViewModel(
                    funkcja=funkcja,
                    nazwisko=(sedzia.nazwisko or "") if sedzia else "",
                    miasto=(sedzia.miasto or "") if sedzia else "",
                )
            )
        return tuple(wynik)
