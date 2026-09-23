from __future__ import annotations

from datetime import datetime

from handball.domain.match_rules import MeczPolicy
from handball.domain.news import (
    Aktualnosci,
    MeczAktualnosci,
    RekordMeczu,
    SekcjaRozgrywek,
    StrzelecAktualnosci,
    WystepZRozgrywkami,
)
from handball.interface.view_models.news import (
    AktualnosciViewModel,
    CiekawostkaViewModel,
    MeczAktualnosciViewModel,
    SekcjaAktualnosciViewModel,
    StrzelecAktualnosciViewModel,
)

BRAK = "—"


class AktualnosciPresenter:
    def __init__(self, reguly: MeczPolicy | None = None) -> None:
        self._reguly = reguly or MeczPolicy()

    def przygotuj(self, dane: Aktualnosci) -> AktualnosciViewModel:
        return AktualnosciViewModel(
            sezon=dane.sezon.nazwa if dane.sezon else None,
            id_sezon=dane.sezon.id_sezon if dane.sezon else None,
            stan_danych=self._data(dane.ostatni_termin),
            liczba_rozegranych=dane.liczba_rozegranych,
            suma_bramek=dane.suma_bramek,
            srednia_bramek=self._liczba(
                dane.suma_bramek / dane.liczba_rozegranych if dane.liczba_rozegranych else None
            ),
            sekcje=[self._sekcja(sekcja) for sekcja in dane.sekcje],
            pozostale_mecze=[
                self._mecz(pozycja.mecz, pozycja.rozgrywki.nazwa)
                for pozycja in dane.pozostale_mecze
            ],
            ciekawostki=self._ciekawostki(dane),
        )

    def _sekcja(self, sekcja: SekcjaRozgrywek) -> SekcjaAktualnosciViewModel:
        return SekcjaAktualnosciViewModel(
            klucz=sekcja.kategoria.value,
            etykieta=sekcja.kategoria.etykieta,
            rozgrywki=sekcja.rozgrywki.nazwa,
            liczba_rozegranych=sekcja.liczba_rozegranych,
            srednia_bramek=self._liczba(sekcja.srednia_bramek),
            mecze=[self._mecz(mecz) for mecz in sekcja.ostatnie_mecze],
            strzelcy=[
                self._strzelec(pozycja, strzelec)
                for pozycja, strzelec in enumerate(sekcja.strzelcy, 1)
            ],
        )

    def _mecz(
        self, mecz: MeczAktualnosci, rozgrywki: str | None = None
    ) -> MeczAktualnosciViewModel:
        gospodarz, gosc = self._reguly.para(mecz.mecz, mecz.gospodarz, mecz.gosc)
        a, b = self._reguly.para(mecz.mecz, mecz.mecz.wynik_gosp_full, mecz.mecz.wynik_gosc_full)
        zwyciezca = None
        if a is not None and b is not None and a != b:
            zwyciezca = "gospodarz" if a > b else "gosc"
        return MeczAktualnosciViewModel(
            id_mecz=mecz.id_mecz,
            dzien=mecz.termin.strftime("%d.%m") if mecz.termin else BRAK,
            godzina=(
                mecz.termin.strftime("%H:%M")
                if mecz.termin and (mecz.termin.hour or mecz.termin.minute)
                else ""
            ),
            gospodarz=self._tekst(gospodarz),
            gosc=self._tekst(gosc),
            wynik=f"{a}:{b}" if a is not None and b is not None else "-:-",
            zwyciezca=zwyciezca,
            rozgrywki=rozgrywki,
        )

    def _strzelec(
        self, pozycja: int, strzelec: StrzelecAktualnosci
    ) -> StrzelecAktualnosciViewModel:
        return StrzelecAktualnosciViewModel(
            pozycja=pozycja,
            id_zawodnik=strzelec.id_zawodnik,
            zawodnik=self._tekst(strzelec.zawodnik),
            druzyna=self._tekst(strzelec.druzyna),
            mecze=strzelec.mecze,
            bramki=strzelec.bramki,
            srednia=self._liczba(strzelec.bramki / strzelec.mecze if strzelec.mecze else None),
        )

    def _ciekawostki(self, dane: Aktualnosci) -> list[CiekawostkaViewModel]:
        wynik = []
        if dane.liczba_rozegranych:
            wynik.append(
                CiekawostkaViewModel(
                    tytul="Sezon w liczbach",
                    wartosc=self._bramki(dane.suma_bramek),
                    opis=(
                        f"rozegrane mecze: {dane.liczba_rozegranych}, średnio "
                        f"{self._liczba(dane.suma_bramek / dane.liczba_rozegranych)} na mecz"
                    ),
                )
            )
        if dane.najwiecej_bramek:
            wynik.append(
                self._rekord(
                    "Najwięcej bramek w meczu",
                    self._bramki(dane.najwiecej_bramek.wartosc),
                    dane.najwiecej_bramek,
                )
            )
        if dane.najwyzsze_zwyciestwo and dane.najwyzsze_zwyciestwo.wartosc > 0:
            wynik.append(
                self._rekord(
                    "Najwyższe zwycięstwo",
                    f"różnica {self._bramki(dane.najwyzsze_zwyciestwo.wartosc)}",
                    dane.najwyzsze_zwyciestwo,
                )
            )
        if dane.najlepsze_wystepy:
            wynik.append(self._wystep(dane.najlepsze_wystepy[0]))
        if dane.najbardziej_bramkostrzelna:
            sekcja = dane.najbardziej_bramkostrzelna
            wynik.append(
                CiekawostkaViewModel(
                    tytul="Najbardziej bramkostrzelna liga",
                    wartosc=f"{self._liczba(sekcja.srednia_bramek)} bramki na mecz",
                    opis=f"{sekcja.rozgrywki.nazwa} · rozegrane mecze: {sekcja.liczba_rozegranych}",
                )
            )
        return wynik

    def _rekord(self, tytul: str, wartosc: str, rekord: RekordMeczu) -> CiekawostkaViewModel:
        mecz = self._mecz(rekord.mecz)
        return CiekawostkaViewModel(
            tytul=tytul,
            wartosc=wartosc,
            opis=(
                f"{mecz.gospodarz} {mecz.wynik} {mecz.gosc} · {rekord.rozgrywki.nazwa}, "
                f"{self._data(rekord.mecz.termin)}"
            ),
            id_mecz=rekord.mecz.id_mecz,
        )

    def _wystep(self, pozycja: WystepZRozgrywkami) -> CiekawostkaViewModel:
        wystep = pozycja.wystep
        druzyna = (
            f" ({wystep.druzyna.strip()})" if wystep.druzyna and wystep.druzyna.strip() else ""
        )
        return CiekawostkaViewModel(
            tytul="Najlepszy występ indywidualny",
            wartosc=f"{self._bramki(wystep.bramki)} w meczu",
            opis=(
                f"{self._tekst(wystep.zawodnik)}{druzyna} · {pozycja.rozgrywki.nazwa}, "
                f"{self._data(wystep.termin)}"
            ),
            id_mecz=wystep.id_mecz,
            id_zawodnik=wystep.id_zawodnik,
        )

    @staticmethod
    def _tekst(wartosc: str | None) -> str:
        return " ".join(wartosc.split()) if wartosc and wartosc.strip() else BRAK

    @staticmethod
    def _bramki(liczba: int) -> str:
        if liczba == 1:
            return "1 bramka"
        if liczba % 10 in (2, 3, 4) and liczba % 100 not in (12, 13, 14):
            return f"{liczba} bramki"
        return f"{liczba} bramek"

    @staticmethod
    def _data(wartosc: datetime | None) -> str:
        return wartosc.strftime("%d.%m.%Y") if wartosc else BRAK

    @staticmethod
    def _liczba(wartosc: float | None) -> str:
        return f"{wartosc:.1f}".replace(".", ",") if wartosc is not None else BRAK
