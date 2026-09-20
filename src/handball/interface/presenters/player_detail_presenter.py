from urllib.parse import urlsplit

from handball.domain.matches import StronaMeczow
from handball.domain.player_details import StronaMeczowZawodnika, SzczegolyZawodnika
from handball.interface.presenters.match_presenter import MeczFormat, MeczPresenter
from handball.interface.view_models.player_details import (
    DaneSezonoweZawodnikaViewModel,
    MeczZawodnikaViewModel,
    StronaMeczowZawodnikaViewModel,
    SzczegolyZawodnikaViewModel,
    WpisMeczowyZawodnikaViewModel,
)


class SzczegolyZawodnikaPresenter:
    def __init__(self, formatowanie: MeczFormat, mecze: MeczPresenter) -> None:
        self._format = formatowanie
        self._mecze = mecze

    def przygotuj_szczegoly(self, dane: SzczegolyZawodnika) -> SzczegolyZawodnikaViewModel:
        adres = dane.foto_url
        try:
            url = urlsplit(adres or "")
            if url.scheme not in {"http", "https"} or not url.netloc:
                adres = None
        except ValueError:
            adres = None
        wzrost = next((s.wzrost for s in dane.sezony if s.wzrost is not None), None)
        waga = next((s.waga for s in dane.sezony if s.waga is not None), None)
        return SzczegolyZawodnikaViewModel(
            id_zawodnik=dane.id_zawodnik,
            nazwa=" ".join(n for n in (dane.imie, dane.nazwisko) if n) or "Brak imienia i nazwiska",
            data_urodzenia=dane.data_urodzenia.strftime("%d.%m.%Y") if dane.data_urodzenia else "—",
            foto_url=adres,
            wzrost=self._format.tekst(wzrost),
            waga=self._format.tekst(waga),
            sezony=[
                DaneSezonoweZawodnikaViewModel(
                    sezon=s.sezon,
                    druzyna=self._format.tekst(s.druzyna),
                    nr_koszulki=self._format.tekst(s.nr_koszulki),
                    pozycja=self._format.tekst(s.pozycja),
                    rozgrywki=self._format.tekst(s.rozgrywki),
                    bramki=self._format.tekst(s.bramki),
                    karne=f"{self._format.tekst(s.karne_bramki)}/{self._format.tekst(s.karne_liczba)}",
                    kary=(
                        f"2 min: {self._format.tekst(s.dwie_minuty)} · "
                        f"U: {self._format.tekst(s.upomnienia)} · "
                        f"D: {self._format.tekst(s.dyskwalifikacje)}"
                    ),
                )
                for s in dane.sezony
            ],
        )

    def przygotuj_mecze(self, dane: StronaMeczowZawodnika) -> StronaMeczowZawodnikaViewModel:
        mecze = self._mecze.przygotuj_liste(
            StronaMeczow(
                [p.mecz for p in dane.pozycje],
                dane.liczba_wszystkich,
                dane.strona,
                dane.rozmiar_strony,
            )
        )
        pozycje = []
        for dane_meczu, mecz in zip(dane.pozycje, mecze.pozycje, strict=True):
            wpisy = []
            for wpis in dane_meczu.wpisy:
                druzyna = przeciwnik = None
                if wpis.strona == "gosp":
                    druzyna, przeciwnik = dane_meczu.mecz.gospodarz, dane_meczu.mecz.gosc
                elif wpis.strona == "gosc":
                    druzyna, przeciwnik = dane_meczu.mecz.gosc, dane_meczu.mecz.gospodarz
                stat = wpis.statystyki
                wpisy.append(
                    WpisMeczowyZawodnikaViewModel(
                        strona=wpis.strona,
                        druzyna=self._format.tekst(druzyna),
                        przeciwnik=self._format.tekst(przeciwnik),
                        nr_koszulki=self._format.tekst(stat.nr_koszulki),
                        pozycja=self._format.tekst(stat.pozycja),
                        bramki=self._format.tekst(stat.bramki),
                        karne=f"{self._format.tekst(stat.karne_bramki)}/{self._format.tekst(stat.karne_liczba)}",
                        karne_seria=f"{self._format.tekst(stat.karne_bramki_seria)}/{self._format.tekst(stat.karne_liczba_seria)}",
                        dwie_minuty=self._format.tekst(stat.dwie_minuty),
                        upomnienie=self._format.flaga(stat.upomnienie),
                        dyskwalifikacja=self._format.flaga(stat.dyskwalifikacja),
                    )
                )
            pozycje.append(
                MeczZawodnikaViewModel(
                    mecz=mecz,
                    termin=self._format.data(mecz.termin),
                    wpisy=wpisy,
                    wiele_stron=len(wpisy) > 1,
                )
            )
        return StronaMeczowZawodnikaViewModel(
            pozycje, dane.liczba_wszystkich, dane.strona, dane.rozmiar_strony
        )
