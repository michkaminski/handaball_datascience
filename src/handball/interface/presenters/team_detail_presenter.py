from collections.abc import Sequence

from handball.domain.match_rules import StatusMeczu
from handball.domain.matches import StronaMeczow
from handball.domain.team_details import (
    BilansDruzyny,
    BilansSezonuDruzyny,
    FrekwencjaDruzyny,
    FrekwencjaMiejsca,
    PodsumowanieDruzyny,
    RezultatMeczu,
    RozstrzygniecieRemisu,
    SeriaBramekDruzyny,
    StatystykiZestawienia,
    StronaMeczowDruzyny,
    StronaZawodnikowDruzyny,
    SzczegolyDruzyny,
    WystepDruzyny,
    WystepDruzynyPolicy,
    ZestawienieSezonuDruzyny,
)
from handball.interface.presenters.goal_statistics_presenter import StatystykiBramekPresenter
from handball.interface.presenters.match_presenter import MeczFormat, MeczPresenter
from handball.interface.view_models.goal_statistics import FormaIRegularnoscViewModel
from handball.interface.view_models.team_details import (
    AnalizaBramekDruzynyViewModel,
    BilansViewModel,
    FrekwencjaDruzynyViewModel,
    FrekwencjaMiejscaViewModel,
    GrupaMiarBramekDruzynyViewModel,
    HalaDruzynyViewModel,
    KolumnaMeczuZestawieniaViewModel,
    KomorkaZestawieniaViewModel,
    MeczDruzynyViewModel,
    MiaraBramekDruzynyViewModel,
    NazwaHistorycznaDruzynyViewModel,
    PodsumowanieDruzynyViewModel,
    RekordMeczuDruzynyViewModel,
    SezonDruzynyViewModel,
    StronaMeczowDruzynyViewModel,
    StronaZawodnikowDruzynyViewModel,
    SzczegolyDruzynyViewModel,
    WierszSezonuDruzynyViewModel,
    WierszZestawieniaViewModel,
    ZawodnikDruzynyViewModel,
    ZestawienieSezonuDruzynyViewModel,
)

PLCIE = {"M": "Mężczyźni", "K": "Kobiety"}
REZULTATY = {
    RezultatMeczu.WYGRANA: ("Zwycięstwo", "ok"),
    RezultatMeczu.REMIS: ("Remis", "plan"),
    RezultatMeczu.PORAZKA: ("Porażka", "loss"),
}
STATUSY = {
    StatusMeczu.WALKOWER: "Walkower",
    StatusMeczu.WYCOFANY: "Wycofany",
    StatusMeczu.ZAPLANOWANY: "Bez wyniku",
}
GRUPY_MIAR_FORMY = (
    (
        "Poziom",
        (
            ("Średnia", "srednia"),
            ("Mediana", "mediana"),
            ("Dominanta", "dominanta"),
            ("Średnia ucięta 10%", "srednia_ucieta"),
        ),
    ),
    (
        "Zakres",
        (
            ("Minimum", "minimum"),
            ("Maksimum", "maksimum"),
            ("Q1–Q3", "kwartyle"),
            ("P10", "percentyl_10"),
            ("P90", "percentyl_90"),
        ),
    ),
    (
        "Rozrzut",
        (
            ("IQR", "iqr"),
            ("Odchylenie standardowe", "odchylenie_standardowe"),
            ("MAD", "mad"),
            ("Współczynnik zmienności", "wspolczynnik_zmiennosci"),
        ),
    ),
)
ROZSTRZYGNIECIA = {
    RozstrzygniecieRemisu.WYGRANA_PO_DOGRYWCE: "wygrana po dogrywce",
    RozstrzygniecieRemisu.PORAZKA_PO_DOGRYWCE: "porażka po dogrywce",
    RozstrzygniecieRemisu.WYGRANA_PO_KARNYCH: "wygrana po karnych",
    RozstrzygniecieRemisu.PORAZKA_PO_KARNYCH: "porażka po karnych",
}


class SzczegolyDruzynyPresenter:
    def __init__(
        self,
        formatowanie: MeczFormat,
        mecze: MeczPresenter,
        statystyki: StatystykiBramekPresenter,
        wystepy: WystepDruzynyPolicy,
    ) -> None:
        self._format = formatowanie
        self._mecze = mecze
        self._statystyki = statystyki
        self._wystepy = wystepy

    def przygotuj_szczegoly(self, dane: SzczegolyDruzyny) -> SzczegolyDruzynyViewModel:
        najnowszy = dane.sezony[0] if dane.sezony else None
        miasto = next((s.miasto for s in dane.sezony if s.miasto), None)
        chronologicznie = list(reversed(dane.sezony))
        grupy: list[tuple[str, list[str]]] = []
        for sezon in chronologicznie:
            nazwa = sezon.nazwa or "—"
            if grupy and grupy[-1][0] == nazwa:
                grupy[-1][1].append(sezon.sezon)
            else:
                grupy.append((nazwa, [sezon.sezon]))
        return SzczegolyDruzynyViewModel(
            id_zespol=dane.id_zespol,
            nazwa=dane.nazwa or (najnowszy.nazwa if najnowszy else None) or "Drużyna bez nazwy",
            nr_klubu=self._format.tekst(dane.nr_klubu),
            plec=PLCIE.get((dane.plec or "").strip(), self._format.tekst(dane.plec)),
            kategoria=self._format.tekst(dane.kategoria),
            miasto=self._format.tekst(miasto),
            status="Wycofana" if dane.wycofany else "Aktywna",
            wycofana=bool(dane.wycofany),
            liczba_sezonow=len(dane.sezony),
            zakres_sezonow=self._zakres([s.sezon for s in chronologicznie]),
            liczba_meczow=dane.liczba_meczow,
            nazwy=[
                NazwaHistorycznaDruzynyViewModel(nazwa, self._zakres(sezony), len(sezony))
                for nazwa, sezony in reversed(grupy)
            ],
            sezony=[
                SezonDruzynyViewModel(
                    id_zespol_sezon=s.id_zespol_sezon,
                    sezon=s.sezon,
                    nazwa=self._format.tekst(s.nazwa),
                    miasto=self._format.tekst(s.miasto),
                    kategoria=self._format.tekst(s.kategoria),
                    status="Wycofana" if s.wycofany else "Aktywna",
                    wycofana=bool(s.wycofany),
                )
                for s in dane.sezony
            ],
            hale=[
                HalaDruzynyViewModel(
                    h.id_hala,
                    self._format.tekst(h.nazwa),
                    self._format.tekst(h.miasto),
                    h.liczba_meczow,
                    self._format.widzowie(h.srednia_widzow),
                )
                for h in dane.hale
            ],
        )

    def przygotuj_sezony(
        self, sezony: Sequence[BilansSezonuDruzyny]
    ) -> list[WierszSezonuDruzynyViewModel]:
        wiersze = []
        for sezon in sezony:
            jedne = len(sezon.rozgrywki) == 1
            wiersze.append(
                WierszSezonuDruzynyViewModel(
                    sezon=sezon.sezon,
                    rozgrywki=(
                        sezon.rozgrywki[0].rozgrywki
                        if jedne
                        else f"Wszystkie rozgrywki ({len(sezon.rozgrywki)})"
                    ),
                    nazwa_druzyny=self._format.tekst(sezon.nazwa_druzyny),
                    bilans=self.przygotuj_bilans(sezon.bilans),
                    podsumowanie_sezonu=True,
                )
            )
            if not jedne:
                wiersze.extend(
                    WierszSezonuDruzynyViewModel(
                        sezon=sezon.sezon,
                        rozgrywki=grupa.rozgrywki,
                        nazwa_druzyny="",
                        bilans=self.przygotuj_bilans(grupa.bilans),
                        podsumowanie_sezonu=False,
                    )
                    for grupa in sezon.rozgrywki
                )
        return wiersze

    def przygotuj_bilans(self, bilans: BilansDruzyny) -> BilansViewModel:
        rozegrane = bilans.rozegrane
        roznica = bilans.bramki_zdobyte - bilans.bramki_stracone
        rozstrzygniecia = [
            f"{etykieta}: W {wygrane} / P {przegrane}"
            for etykieta, wygrane, przegrane in (
                (
                    "dogrywka",
                    bilans.remisy_wygrane_po_dogrywce,
                    bilans.remisy_przegrane_po_dogrywce,
                ),
                ("karne", bilans.remisy_wygrane_po_karnych, bilans.remisy_przegrane_po_karnych),
            )
            if wygrane or przegrane
        ]
        inne = [
            f"{etykieta}: {liczba}"
            for etykieta, liczba in (
                ("walkowery", bilans.walkowery),
                ("wycofane", bilans.wycofane),
                ("bez wyniku", bilans.bez_wyniku),
            )
            if liczba
        ]
        return BilansViewModel(
            rozegrane=rozegrane,
            wygrane=bilans.wygrane,
            remisy=bilans.remisy,
            porazki=bilans.porazki,
            rozstrzygniecia=" · ".join(rozstrzygniecia) or "—",
            bramki=f"{bilans.bramki_zdobyte}:{bilans.bramki_stracone}" if rozegrane else "—",
            roznica=f"{roznica:+d}" if rozegrane else "—",
            srednia_zdobytych=(
                self._statystyki.liczba(bilans.bramki_zdobyte / rozegrane) if rozegrane else "—"
            ),
            srednia_straconych=(
                self._statystyki.liczba(bilans.bramki_stracone / rozegrane) if rozegrane else "—"
            ),
            procent_zwyciestw=(
                self._statystyki.procent(100 * bilans.wygrane / rozegrane) if rozegrane else "—"
            ),
            inne=" · ".join(inne) or "—",
            widzowie_dom=self._format.widzowie(bilans.frekwencja.dom.srednia),
            widzowie_wyjazd=self._format.widzowie(bilans.frekwencja.wyjazd.srednia),
            widzowie_dom_suma=self._format.widzowie(bilans.frekwencja.dom.suma),
            pokrycie_widzow=self._pokrycie(bilans.frekwencja),
        )

    def przygotuj_frekwencje(self, dane: FrekwencjaDruzyny) -> FrekwencjaDruzynyViewModel:
        return FrekwencjaDruzynyViewModel(
            dom=self._frekwencja_miejsca(dane.dom),
            wyjazd=self._frekwencja_miejsca(dane.wyjazd),
            ma_dane=bool(dane.dom.znane or dane.wyjazd.znane),
        )

    def _frekwencja_miejsca(self, dane: FrekwencjaMiejsca) -> FrekwencjaMiejscaViewModel:
        rekord = dane.rekord
        return FrekwencjaMiejscaViewModel(
            srednia=self._format.widzowie(dane.srednia),
            mediana=self._format.widzowie(dane.mediana),
            suma=self._format.widzowie(dane.suma),
            pokrycie=f"{dane.znane}/{dane.mecze}",
            rekord=self._format.widzowie(rekord.widzowie if rekord else None),
            rekord_mecz=rekord.id_mecz if rekord else None,
            rekord_opis=(
                f"{self._format.tekst(rekord.przeciwnik)} · {self._format.data(rekord.termin)}"
                if rekord
                else ""
            ),
        )

    @staticmethod
    def _pokrycie(frekwencja: FrekwencjaDruzyny) -> str:
        dom, wyjazd = frekwencja.dom, frekwencja.wyjazd
        return f"{dom.znane + wyjazd.znane}/{dom.mecze + wyjazd.mecze}"

    def przygotuj_mecze(self, dane: StronaMeczowDruzyny) -> StronaMeczowDruzynyViewModel:
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
            wystep = self._wystepy.wystep(dane_meczu)
            rezultat, klasa = self._rezultat(wystep)
            pozycje.append(
                MeczDruzynyViewModel(
                    mecz=mecz,
                    termin=self._format.data(mecz.termin),
                    miejsce=self._statystyki.miejsce_etykieta(wystep.miejsce),
                    przeciwnik=self._format.tekst(wystep.przeciwnik),
                    wynik_druzyny=self._wynik(wystep),
                    rezultat=rezultat,
                    rezultat_klasa=klasa,
                    rozstrzygniecie=(
                        ROZSTRZYGNIECIA[wystep.rozstrzygniecie] if wystep.rozstrzygniecie else ""
                    ),
                    widzowie=mecz.widzowie,
                )
            )
        return StronaMeczowDruzynyViewModel(
            pozycje, dane.liczba_wszystkich, dane.strona, dane.rozmiar_strony
        )

    def przygotuj_zestawienie(
        self, dane: ZestawienieSezonuDruzyny, sezon: str
    ) -> ZestawienieSezonuDruzynyViewModel:
        return ZestawienieSezonuDruzynyViewModel(
            sezon=sezon,
            mecze=[
                KolumnaMeczuZestawieniaViewModel(
                    id_mecz=w.id_mecz,
                    data=w.termin.strftime("%d.%m.%Y") if w.termin else "—",
                    przeciwnik=self._format.tekst(w.przeciwnik),
                    miejsce="u siebie" if w.miejsce == "dom" else "wyjazd",
                    wynik=self._wynik(w),
                    rezultat=self._rezultat(w)[0],
                    rezultat_klasa=self._rezultat(w)[1],
                )
                for w in dane.mecze
            ],
            wiersze=[
                WierszZestawieniaViewModel(
                    id_zawodnik=w.id_zawodnik,
                    nazwa=" ".join(n for n in (w.imie, w.nazwisko) if n)
                    or f"Zawodnik #{w.id_zawodnik}",
                    numery=", ".join(str(n) for n in w.numery),
                    pozycje=", ".join(w.pozycje) or "—",
                    komorki=[self._komorka(k) if k else None for k in w.komorki],
                    suma=self._komorka(w.suma),
                    mecze=w.suma.mecze,
                )
                for w in dane.wiersze
            ],
            sumy_meczow=[self._komorka(k) for k in dane.sumy_meczow],
            suma=self._komorka(dane.suma),
        )

    def _komorka(self, dane: StatystykiZestawienia) -> KomorkaZestawieniaViewModel:
        kary = []
        if dane.dwie_minuty:
            kary.append(f"{dane.dwie_minuty}×2′")
        if dane.upomnienia:
            kary.append("U" if dane.upomnienia == 1 else f"{dane.upomnienia}U")
        if dane.dyskwalifikacje:
            kary.append("D" if dane.dyskwalifikacje == 1 else f"{dane.dyskwalifikacje}D")
        trafione, wszystkie = dane.karne_trafione, dane.karne_wszystkie
        karne = f"{trafione or 0}/{wszystkie}" if wszystkie else ""
        bramki = self._format.tekst(dane.bramki)
        opis = [f"bramki: {bramki}"]
        if kary:
            opis.append(
                "kary: "
                + ", ".join(
                    czesc
                    for czesc in (
                        f"2 min ×{dane.dwie_minuty}" if dane.dwie_minuty else "",
                        f"upomnienia {dane.upomnienia}" if dane.upomnienia else "",
                        f"dyskwalifikacje {dane.dyskwalifikacje}" if dane.dyskwalifikacje else "",
                    )
                    if czesc
                )
            )
        if karne:
            opis.append(f"karne: {trafione or 0} wykorzystane z {wszystkie}")
        return KomorkaZestawieniaViewModel(
            bramki=bramki, kary=" ".join(kary), karne=karne, opis="; ".join(opis)
        )

    def przygotuj_zawodnikow(
        self, dane: StronaZawodnikowDruzyny
    ) -> StronaZawodnikowDruzynyViewModel:
        pozycje = [
            ZawodnikDruzynyViewModel(
                id_zawodnik=z.id_zawodnik,
                nazwa=" ".join(n for n in (z.imie, z.nazwisko) if n)
                or f"Zawodnik #{z.id_zawodnik}",
                mecze=z.mecze,
                bramki=self._format.tekst(z.bramki),
                srednia=(
                    f"{z.bramki / z.mecze_ze_znanymi_bramkami:.2f}"
                    if z.bramki is not None and z.mecze_ze_znanymi_bramkami
                    else "—"
                ),
                karne=f"{self._format.tekst(z.karne_bramki)}/{self._format.tekst(z.karne_liczba)}",
                kary=(
                    f"2 min: {self._format.tekst(z.dwie_minuty)} · "
                    f"U: {self._format.tekst(z.upomnienia)} · "
                    f"D: {self._format.tekst(z.dyskwalifikacje)}"
                ),
                sezony=(f"{self._zakres(list(z.sezony))} ({len(z.sezony)})" if z.sezony else "—"),
                ostatni_mecz=self._format.data(z.ostatni_mecz),
            )
            for z in dane.pozycje
        ]
        return StronaZawodnikowDruzynyViewModel(
            pozycje, dane.liczba_wszystkich, dane.strona, dane.rozmiar_strony
        )

    def przygotuj_podsumowanie(self, dane: PodsumowanieDruzyny) -> PodsumowanieDruzynyViewModel:
        return PodsumowanieDruzynyViewModel(
            bilans=self.przygotuj_bilans(dane.bilans),
            seria_zwyciestw=str(dane.najdluzsza_seria_zwyciestw),
            seria_bez_porazki=str(dane.najdluzsza_seria_bez_porazki),
            rekordy=[
                ("Najwyższe zwycięstwo", self._rekord(dane.najwyzsze_zwyciestwo)),
                ("Najwyższa porażka", self._rekord(dane.najwyzsza_porazka)),
                ("Najwięcej zdobytych bramek", self._rekord(dane.najwiecej_zdobytych)),
                ("Najwięcej straconych bramek", self._rekord(dane.najwiecej_straconych)),
            ],
            bilanse_sezonow=[
                {
                    "sezon": sezon.sezon,
                    "rozegrane": sezon.bilans.rozegrane,
                    "wygrane": sezon.bilans.wygrane,
                    "remisy": sezon.bilans.remisy,
                    "porazki": sezon.bilans.porazki,
                    "zdobyte": sezon.bilans.bramki_zdobyte,
                    "stracone": sezon.bilans.bramki_stracone,
                    "srednia_zdobytych": sezon.bilans.bramki_zdobyte / sezon.bilans.rozegrane,
                    "srednia_straconych": sezon.bilans.bramki_stracone / sezon.bilans.rozegrane,
                    "roznica_na_mecz": (sezon.bilans.bramki_zdobyte - sezon.bilans.bramki_stracone)
                    / sezon.bilans.rozegrane,
                }
                for sezon in dane.bilanse_sezonow
                if sezon.bilans.rozegrane
            ],
        )

    def przygotuj_analize_bramek(
        self,
        zdobyte: SeriaBramekDruzyny,
        stracone: SeriaBramekDruzyny,
        roznica: SeriaBramekDruzyny,
    ) -> AnalizaBramekDruzynyViewModel:
        statystyki = self._statystyki
        formy = [statystyki.przygotuj_forme(seria.forma) for seria in (zdobyte, stracone, roznica)]
        return AnalizaBramekDruzynyViewModel(
            liczba_meczow=formy[0].liczba_meczow,
            liczba_znanych=formy[0].liczba_znanych,
            miary=[
                self._miara(etykieta, *(wartosc(seria) for seria in (zdobyte, stracone, roznica)))
                for etykieta, wartosc in (
                    ("Średnia na mecz", lambda s: statystyki.liczba(s.statystyki.srednia)),
                    ("Mediana", lambda s: statystyki.liczba(s.statystyki.mediana)),
                    ("Dominanta", lambda s: statystyki.dominanta(s.statystyki.dominanty)),
                    (
                        "Q1–Q3",
                        lambda s: statystyki.kwartyle(
                            s.statystyki.kwartyl_pierwszy, s.statystyki.kwartyl_trzeci
                        ),
                    ),
                    ("Min–maks", self._zakres_serii),
                    ("Mediana u siebie", lambda s: statystyki.liczba(s.mediana_dom)),
                    ("Mediana na wyjeździe", lambda s: statystyki.liczba(s.mediana_wyjazd)),
                )
            ],
            grupy=[
                GrupaMiarBramekDruzynyViewModel(
                    nazwa,
                    [
                        self._miara(
                            etykieta,
                            getattr(formy[0], pole),
                            getattr(formy[1], pole),
                            "—" if pole == "wspolczynnik_zmiennosci" else getattr(formy[2], pole),
                        )
                        for etykieta, pole in pola
                    ],
                )
                for nazwa, pola in GRUPY_MIAR_FORMY
            ],
            sezony=self._sezony_bramek(zdobyte, stracone),
            rozklad=self._rozklad_bramek(zdobyte, stracone),
            mecze=self._mecze_bramek(zdobyte, stracone, roznica, formy),
            rozstepy=self._rozstepy_bramek(formy[0], formy[1]),
        )

    def _sezony_bramek(
        self, zdobyte: SeriaBramekDruzyny, stracone: SeriaBramekDruzyny
    ) -> list[dict[str, object]]:
        wynik: list[dict[str, object]] = []
        pary = zip(
            self._statystyki.statystyki_sezonow(zdobyte.statystyki_sezonow),
            self._statystyki.statystyki_sezonow(stracone.statystyki_sezonow),
            strict=True,
        )
        for sezon_z, sezon_s in pary:
            rozgrywki_z = sezon_z.pop("rozgrywki")
            rozgrywki_s = sezon_s.pop("rozgrywki")
            assert isinstance(rozgrywki_z, list) and isinstance(rozgrywki_s, list)
            wynik.append(
                {
                    "sezon": sezon_z["sezon"],
                    "zdobyte": sezon_z,
                    "stracone": sezon_s,
                    "rozgrywki": [
                        {"rozgrywki": grupa_z["rozgrywki"], "zdobyte": grupa_z, "stracone": grupa_s}
                        for grupa_z, grupa_s in zip(rozgrywki_z, rozgrywki_s, strict=True)
                    ],
                }
            )
        return wynik

    def _rozklad_bramek(
        self, zdobyte: SeriaBramekDruzyny, stracone: SeriaBramekDruzyny
    ) -> list[dict[str, object]]:
        serie = {
            "zdobyte": {p["bramki"]: p for p in self._statystyki.rozklad(zdobyte.mecze)},
            "stracone": {p["bramki"]: p for p in self._statystyki.rozklad(stracone.mecze)},
        }
        wartosci = sorted(set(serie["zdobyte"]) | set(serie["stracone"]))
        return [
            {
                "bramki": wartosc,
                **{
                    rodzaj: {
                        klucz: punkty.get(wartosc, {}).get(pole, 0)
                        for klucz, pole in (
                            ("wszystkie", "mecze"),
                            ("dom", "dom"),
                            ("wyjazd", "wyjazd"),
                        )
                    }
                    for rodzaj, punkty in serie.items()
                },
            }
            for wartosc in wartosci
        ]

    def _mecze_bramek(
        self,
        zdobyte: SeriaBramekDruzyny,
        stracone: SeriaBramekDruzyny,
        roznica: SeriaBramekDruzyny,
        formy: list[FormaIRegularnoscViewModel],
    ) -> dict[str, dict[str, object]]:
        wystepy = {mecz.id_mecz: mecz.wystep for mecz in zdobyte.mecze}
        mediany = {
            "wszystkie": (zdobyte.statystyki.mediana, stracone.statystyki.mediana),
            "dom": (zdobyte.mediana_dom, stracone.mediana_dom),
            "wyjazd": (zdobyte.mediana_wyjazd, stracone.mediana_wyjazd),
        }
        wynik: dict[str, dict[str, object]] = {}
        for miejsce, (mediana_z, mediana_s) in mediany.items():
            forma_z, forma_s, forma_r = (getattr(forma, miejsce) for forma in formy)
            punkty = []
            for punkt_z, punkt_s, punkt_r in zip(
                forma_z.punkty, forma_s.punkty, forma_r.punkty, strict=True
            ):
                wystep = wystepy[int(str(punkt_z["id_mecz"]))]
                punkty.append(
                    {
                        "id_mecz": punkt_z["id_mecz"],
                        "etykieta": punkt_z["etykieta"],
                        "sezon": punkt_z["sezon"],
                        "rozgrywki": wystep.rozgrywki,
                        "przeciwnik": wystep.przeciwnik,
                        "miejsce_etykieta": self._statystyki.miejsce_etykieta(wystep.miejsce),
                        "wynik": self._wynik(wystep),
                        "rezultat": self._rezultat(wystep)[0],
                        "zdobyte": punkt_z["bramki"],
                        "stracone": punkt_s["bramki"],
                        "roznica": punkt_r["bramki"],
                        "zdobyte_srednia_5": punkt_z["srednia_5"],
                        "zdobyte_mediana_10": punkt_z["mediana_10"],
                        "stracone_srednia_5": punkt_s["srednia_5"],
                        "stracone_mediana_10": punkt_s["mediana_10"],
                        "roznica_srednia_5": punkt_r["srednia_5"],
                    }
                )
            wynik[miejsce] = {
                "punkty": punkty,
                "mediana_zdobytych": mediana_z,
                "mediana_straconych": mediana_s,
                "liczba": len(punkty),
                "trend_5": forma_z.wystarczajaco_na_trend_5,
                "trend_10": forma_z.wystarczajaco_na_trend_10,
            }
        return wynik

    @staticmethod
    def _rozstepy_bramek(
        zdobyte: FormaIRegularnoscViewModel, stracone: FormaIRegularnoscViewModel
    ) -> list[dict[str, object]]:
        straconych = {sezon["sezon"]: sezon for sezon in stracone.sezony}
        return [
            {
                "sezon": sezon["sezon"],
                "zdobyte": sezon,
                "stracone": straconych.get(str(sezon["sezon"])),
            }
            for sezon in zdobyte.sezony
        ]

    def _zakres_serii(self, seria: SeriaBramekDruzyny) -> str:
        grupa = seria.statystyki
        if grupa.minimum is None or grupa.maksimum is None:
            return "—"
        return f"{grupa.minimum}–{grupa.maksimum}"

    @staticmethod
    def _miara(
        etykieta: str, zdobyte: str, stracone: str, roznica: str
    ) -> MiaraBramekDruzynyViewModel:
        return MiaraBramekDruzynyViewModel(etykieta, zdobyte, stracone, roznica)

    def _rekord(self, wystep: WystepDruzyny | None) -> RekordMeczuDruzynyViewModel | None:
        if wystep is None:
            return None
        return RekordMeczuDruzynyViewModel(
            id_mecz=wystep.id_mecz,
            opis=f"{self._wynik(wystep)} — {self._format.tekst(wystep.przeciwnik)}",
            szczegoly=(
                f"{self._format.data(wystep.termin)} · {wystep.sezon} · {wystep.rozgrywki} · "
                f"{self._statystyki.miejsce_etykieta(wystep.miejsce).lower()}"
            ),
        )

    @staticmethod
    def _wynik(wystep: WystepDruzyny) -> str:
        if wystep.bramki is None or wystep.stracone is None:
            return "—"
        return f"{wystep.bramki}:{wystep.stracone}"

    @staticmethod
    def _rezultat(wystep: WystepDruzyny) -> tuple[str, str]:
        if wystep.rezultat is not None:
            return REZULTATY[wystep.rezultat]
        return STATUSY.get(wystep.status, "—"), "warn"

    @staticmethod
    def _zakres(sezony: list[str]) -> str:
        if not sezony:
            return "—"
        return sezony[0] if sezony[0] == sezony[-1] else f"{sezony[0]}–{sezony[-1]}"
