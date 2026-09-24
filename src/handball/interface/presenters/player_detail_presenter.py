from urllib.parse import urlsplit

from handball.domain.goal_statistics import FormaIRegularnosc
from handball.domain.matches import StronaMeczow
from handball.domain.player_details import (
    PodsumowanieAnalityczneZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
)
from handball.interface.presenters.goal_statistics_presenter import StatystykiBramekPresenter
from handball.interface.presenters.match_presenter import MeczFormat, MeczPresenter
from handball.interface.view_models.goal_statistics import FormaIRegularnoscViewModel
from handball.interface.view_models.player_details import (
    DaneSezonoweZawodnikaViewModel,
    MeczZawodnikaViewModel,
    PodsumowanieAnalityczneZawodnikaViewModel,
    StronaMeczowZawodnikaViewModel,
    SzczegolyZawodnikaViewModel,
    WpisMeczowyZawodnikaViewModel,
)


class SzczegolyZawodnikaPresenter:
    def __init__(
        self,
        formatowanie: MeczFormat,
        mecze: MeczPresenter,
        statystyki: StatystykiBramekPresenter,
    ) -> None:
        self._format = formatowanie
        self._mecze = mecze
        self._statystyki = statystyki

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
                    druzyna, przeciwnik = mecz.gospodarz, mecz.gosc
                elif wpis.strona == "gosc":
                    druzyna, przeciwnik = mecz.gosc, mecz.gospodarz
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

    def przygotuj_podsumowanie(
        self, dane: PodsumowanieAnalityczneZawodnika
    ) -> PodsumowanieAnalityczneZawodnikaViewModel:
        proby = dane.karne_liczba
        skutecznosc = (
            f"{100 * dane.karne_bramki / proby:.1f}%"
            if dane.karne_bramki is not None and proby
            else "—"
        )
        mecze_znane = dane.liczba_znanych_bramek
        udzial_z_bramka = (
            f"{dane.mecze_z_bramka}/{mecze_znane} ({100 * dane.mecze_z_bramka / mecze_znane:.1f}%)"
            if mecze_znane
            else "—"
        )
        return PodsumowanieAnalityczneZawodnikaViewModel(
            liczba_meczow=str(dane.liczba_meczow),
            bramki=self._liczba(dane.suma_bramek),
            srednia=self._liczba(dane.srednia_bramek),
            mediana=self._liczba(dane.mediana_bramek),
            dominanta=self._statystyki.dominanta(dane.dominanty_bramek),
            kwartyle=self._statystyki.kwartyle(dane.kwartyl_pierwszy, dane.kwartyl_trzeci),
            mecze_z_bramka=udzial_z_bramka,
            karne=f"{self._liczba(dane.karne_bramki)}/{self._liczba(proby)}",
            skutecznosc_karnych=skutecznosc,
            dwie_minuty=self._liczba(dane.dwie_minuty),
            upomnienia=self._liczba(dane.upomnienia),
            dyskwalifikacje=self._liczba(dane.dyskwalifikacje),
            pokrycie_bramek=f"{mecze_znane}/{dane.liczba_meczow}",
            punkty=[
                {
                    "id_mecz": mecz.id_mecz,
                    "data": mecz.termin.isoformat() if mecz.termin else None,
                    "etykieta": self._format.data(mecz.termin),
                    "sezon": mecz.sezon,
                    "rozgrywki": mecz.rozgrywki,
                    "bramki": mecz.bramki,
                    "karne_bramki": mecz.karne_bramki,
                    "karne_liczba": mecz.karne_liczba,
                    "dwie_minuty": mecz.dwie_minuty,
                    "upomnienia": mecz.upomnienia,
                    "dyskwalifikacje": mecz.dyskwalifikacje,
                    "miejsce": mecz.miejsce,
                    "miejsce_etykieta": self._miejsce_etykieta(mecz.miejsce),
                }
                for mecz in dane.mecze
            ],
            rozklad=self._statystyki.rozklad(dane.mecze),
            statystyki_sezonow=self._statystyki.statystyki_sezonow(dane.statystyki_sezonow),
            mediana_wartosc=dane.mediana_bramek,
            mediana_dom_wartosc=dane.mediana_bramek_dom,
            mediana_wyjazd_wartosc=dane.mediana_bramek_wyjazd,
            rekord_bramek=self._liczba(dane.rekord_bramek),
            rekordowe_mecze=[
                punkt
                for punkt in [
                    {
                        "id_mecz": mecz.id_mecz,
                        "data": self._format.data(mecz.termin),
                        "sezon": mecz.sezon,
                        "rozgrywki": mecz.rozgrywki,
                        "bramki": mecz.bramki,
                    }
                    for mecz in dane.mecze
                    if mecz.id_mecz in dane.rekordowe_mecze
                ]
            ],
            najdluzsza_seria=str(dane.najdluzsza_seria_z_bramka),
            jakosc=self._przygotuj_jakosc(dane),
        )

    def przygotuj_forme(self, dane: FormaIRegularnosc) -> FormaIRegularnoscViewModel:
        return self._statystyki.przygotuj_forme(dane)

    def _miejsce_etykieta(self, miejsce: str | None) -> str:
        return self._statystyki.miejsce_etykieta(miejsce)

    def _liczba(self, wartosc: int | float | None) -> str:
        return self._statystyki.liczba(wartosc)

    @staticmethod
    def _przygotuj_jakosc(
        dane: PodsumowanieAnalityczneZawodnika,
    ) -> list[dict[str, int | str | float]]:
        pola = (
            ("Bramki", dane.liczba_znanych_bramek),
            ("Karne trafione", dane.znane_karne_bramki),
            ("Karne próby", dane.znane_karne_liczba),
            ("Kary 2 min", dane.znane_dwie_minuty),
            ("Upomnienia", dane.znane_upomnienia),
            ("Dyskwalifikacje", dane.znane_dyskwalifikacje),
        )
        return [
            {
                "pole": pole,
                "znane": znane,
                "wszystkie": dane.liczba_meczow,
                "procent": 100 * znane / dane.liczba_meczow if dane.liczba_meczow else 0,
            }
            for pole, znane in pola
        ]
