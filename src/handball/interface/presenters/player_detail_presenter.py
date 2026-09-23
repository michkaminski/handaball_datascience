from collections import Counter
from urllib.parse import urlsplit

from handball.domain.matches import StronaMeczow
from handball.domain.player_details import (
    FormaIRegularnoscZawodnika,
    FormaWedlugMiejscaZawodnika,
    PodsumowanieAnalityczneZawodnika,
    StatystykiBramekGrupy,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
)
from handball.interface.presenters.match_presenter import MeczFormat, MeczPresenter
from handball.interface.view_models.player_details import (
    DaneSezonoweZawodnikaViewModel,
    FormaIRegularnoscZawodnikaViewModel,
    FormaWedlugMiejscaZawodnikaViewModel,
    MeczZawodnikaViewModel,
    PodsumowanieAnalityczneZawodnikaViewModel,
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

    def przygotuj_podsumowanie(
        self, dane: PodsumowanieAnalityczneZawodnika
    ) -> PodsumowanieAnalityczneZawodnikaViewModel:
        rozklad = Counter(m.bramki for m in dane.mecze if m.bramki is not None)
        rozklad_dom = Counter(
            m.bramki for m in dane.mecze if m.bramki is not None and m.miejsce == "dom"
        )
        rozklad_wyjazd = Counter(
            m.bramki for m in dane.mecze if m.bramki is not None and m.miejsce == "wyjazd"
        )
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
            dominanta=", ".join(str(w) for w in dane.dominanty_bramek) or "—",
            kwartyle=(
                f"{self._liczba(dane.kwartyl_pierwszy)}–{self._liczba(dane.kwartyl_trzeci)}"
                if dane.kwartyl_pierwszy is not None and dane.kwartyl_trzeci is not None
                else "—"
            ),
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
            rozklad=[
                {
                    "bramki": wartosc,
                    "mecze": rozklad[wartosc],
                    "dom": rozklad_dom.get(wartosc, 0),
                    "wyjazd": rozklad_wyjazd.get(wartosc, 0),
                }
                for wartosc in sorted(rozklad)
            ],
            statystyki_sezonow=[
                {
                    "sezon": sezon.sezon,
                    **self._statystyki_grupy(sezon.statystyki),
                    "rozgrywki": [
                        {"rozgrywki": grupa.rozgrywki, **self._statystyki_grupy(grupa.statystyki)}
                        for grupa in sezon.rozgrywki
                    ],
                }
                for sezon in dane.statystyki_sezonow
            ],
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

    @staticmethod
    def _statystyki_grupy(statystyki: StatystykiBramekGrupy) -> dict[str, object]:
        return {
            "mecze": statystyki.liczba_meczow,
            "znane": statystyki.liczba_znanych,
            "suma": statystyki.suma,
            "srednia": statystyki.srednia,
            "mediana": statystyki.mediana,
            "dominanty": list(statystyki.dominanty),
            "q1": statystyki.kwartyl_pierwszy,
            "q3": statystyki.kwartyl_trzeci,
            "minimum": statystyki.minimum,
            "maksimum": statystyki.maksimum,
        }

    def przygotuj_forme(
        self, dane: FormaIRegularnoscZawodnika
    ) -> FormaIRegularnoscZawodnikaViewModel:
        return FormaIRegularnoscZawodnikaViewModel(
            liczba_meczow=str(dane.liczba_meczow),
            liczba_znanych=str(dane.liczba_znanych),
            srednia=self._liczba(dane.srednia),
            mediana=self._liczba(dane.mediana),
            dominanta=", ".join(str(w) for w in dane.dominanty) or "—",
            minimum=self._liczba(dane.minimum),
            maksimum=self._liczba(dane.maksimum),
            kwartyle=(
                f"{self._liczba(dane.kwartyl_pierwszy)}–{self._liczba(dane.kwartyl_trzeci)}"
                if dane.kwartyl_pierwszy is not None and dane.kwartyl_trzeci is not None
                else "—"
            ),
            iqr=self._liczba(dane.rozstep_miedzykwartylowy),
            odchylenie_standardowe=self._liczba(dane.odchylenie_standardowe),
            mad=self._liczba(dane.mad),
            wspolczynnik_zmiennosci=(
                f"{dane.wspolczynnik_zmiennosci:.1f}%"
                if dane.wspolczynnik_zmiennosci is not None
                else "—"
            ),
            percentyl_10=self._liczba(dane.percentyl_10),
            percentyl_90=self._liczba(dane.percentyl_90),
            srednia_ucieta=self._liczba(dane.srednia_ucieta),
            udzial_0_bramek=self._procent(dane.udzial_0_bramek),
            udzial_1_2_bramki=self._procent(dane.udzial_1_2_bramki),
            udzial_3_5_bramek=self._procent(dane.udzial_3_5_bramek),
            udzial_6_plus_bramek=self._procent(dane.udzial_6_plus_bramek),
            wszystkie=self._przygotuj_forme_wedlug_miejsca(dane.wszystkie),
            dom=self._przygotuj_forme_wedlug_miejsca(dane.dom),
            wyjazd=self._przygotuj_forme_wedlug_miejsca(dane.wyjazd),
            sezony=[
                {
                    "sezon": sezon.sezon,
                    "n": sezon.liczba_znanych,
                    "mala_proba": sezon.mala_proba,
                    "mediana": sezon.mediana,
                    "q1": sezon.kwartyl_pierwszy,
                    "q3": sezon.kwartyl_trzeci,
                    "minimum": sezon.minimum,
                    "maksimum": sezon.maksimum,
                    "odstajace": list(sezon.wartosci_odstajace),
                }
                for sezon in dane.sezony
            ],
        )

    def _przygotuj_forme_wedlug_miejsca(
        self, dane: FormaWedlugMiejscaZawodnika
    ) -> FormaWedlugMiejscaZawodnikaViewModel:
        return FormaWedlugMiejscaZawodnikaViewModel(
            liczba_znanych=str(dane.liczba_znanych),
            wystarczajaco_na_trend_5=dane.wystarczajaco_na_trend_5,
            wystarczajaco_na_trend_10=dane.wystarczajaco_na_trend_10,
            punkty=[
                {
                    "id_mecz": punkt.id_mecz,
                    "etykieta": self._format.data(punkt.termin),
                    "sezon": punkt.sezon,
                    "bramki": punkt.bramki,
                    "mediana_5": punkt.mediana_kroczaca_5,
                    "srednia_5": punkt.srednia_kroczaca_5,
                    "mediana_10": punkt.mediana_kroczaca_10,
                }
                for punkt in dane.punkty
            ],
        )

    @staticmethod
    def _miejsce_etykieta(miejsce: str | None) -> str:
        return {"dom": "U siebie", "wyjazd": "Na wyjeździe"}.get(miejsce or "", "—")

    @staticmethod
    def _procent(wartosc: float | None) -> str:
        return f"{wartosc:.1f}%" if wartosc is not None else "—"

    @staticmethod
    def _liczba(wartosc: int | float | None) -> str:
        if wartosc is None:
            return "—"
        if isinstance(wartosc, float):
            return f"{wartosc:.1f}"
        return str(wartosc)

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
