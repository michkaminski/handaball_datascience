from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

from handball.domain.match_preview import WystepSezonuZawodnika
from handball.domain.team_details import (
    BilansDruzyny,
    RezultatMeczu,
    RozstrzygniecieRemisu,
    StatystykiZestawienia,
    WierszZestawienia,
)
from handball.domain.team_report import (
    KolejnoscZawodnikowRaportuPolicy,
    MeczRaportu,
    MiejscaPolicy,
    RaportDruzyny,
    StronaZestawien,
    ZawodnikRaportu,
    ZestawieniaDruzyny,
)
from handball.interface.presenters.match_protocol_presenter import SKROTY_POZYCJI
from handball.interface.presenters.team_detail_presenter import (
    PLCIE,
    SzczegolyDruzynyPresenter,
)
from handball.interface.view_models.team_report import (
    KolumnaZestawieniaRaportuViewModel,
    KomorkaZestawieniaRaportuViewModel,
    LiczbaRaportuViewModel,
    MeczRaportuViewModel,
    PoprzedniSezonViewModel,
    RaportDruzynyViewModel,
    StronaZestawienViewModel,
    SumaZestawieniaRaportuViewModel,
    UkladRaportuViewModel,
    UkladZestawieniaViewModel,
    WierszZestawieniaRaportuViewModel,
    ZawodnikRaportuViewModel,
    ZestawieniaDruzynyViewModel,
)

BRAK = "—"
GRUPY_POZYCJI = (
    "Bramkarze",
    "Rozgrywający",
    "Skrzydłowi",
    "Obrotowi",
    "Inne pozycje",
    "Pozycja nieznana",
)
LITERY_REZULTATOW = {
    RezultatMeczu.WYGRANA: ("W", "wygrana"),
    RezultatMeczu.REMIS: ("R", "remis"),
    RezultatMeczu.PORAZKA: ("P", "porazka"),
}
ZNACZNIKI_ROZSTRZYGNIEC = {
    RozstrzygniecieRemisu.WYGRANA_PO_DOGRYWCE: "d",
    RozstrzygniecieRemisu.PORAZKA_PO_DOGRYWCE: "d",
    RozstrzygniecieRemisu.WYGRANA_PO_KARNYCH: "k",
    RozstrzygniecieRemisu.PORAZKA_PO_KARNYCH: "k",
}
NAJLEPSZYCH_STRZELCOW = 3
NAJLEPSZYCH_KARNYCH = 3
NAJMNIEJ_KARNYCH = 5


def rocznik(data_urodzenia: date | None) -> str:
    return str(data_urodzenia.year) if data_urodzenia else ""


def nazwa_zawodnika(imie: str | None, nazwisko: str | None, id_zawodnik: int) -> str:
    return " ".join(c for c in (nazwisko, imie) if c) or f"#{id_zawodnik}"


def skrot_pozycji(pozycja: str | None) -> str:
    nazwa = (pozycja or "").casefold()
    return next((skrot for prefiks, skrot in SKROTY_POZYCJI if nazwa.startswith(prefiks)), "")


def skutecznosc(trafione: int | None, wszystkie: int | None) -> float:
    return (trafione or 0) / wszystkie if wszystkie else 0.0


def procent(trafione: int | None, wszystkie: int | None) -> str:
    if not wszystkie:
        return ""
    return f"{round(100 * (trafione or 0) / wszystkie)}%"


class UkladRaportuPolicy:
    MIEJSCE_WIERSZY_MM = 205.0
    NAJWYZSZY_WIERSZ_MM = 4.4
    NAJNIZSZY_WIERSZ_MM = 2.6
    OBRAMOWANIE_WIERSZA_MM = 0.7

    def uklad(self, liczba_wierszy: int) -> UkladRaportuViewModel:
        wysokosc = self.MIEJSCE_WIERSZY_MM / max(liczba_wierszy, 1) - self.OBRAMOWANIE_WIERSZA_MM
        wysokosc = max(self.NAJNIZSZY_WIERSZ_MM, min(self.NAJWYZSZY_WIERSZ_MM, wysokosc))
        return UkladRaportuViewModel(
            wysokosc_wiersza_mm=round(wysokosc, 2),
            czcionka_pt=round(min(7.4, wysokosc * 1.8), 1),
        )


class UkladZestawieniaPolicy:
    MIEJSCE_WIERSZY_MM = 116.0
    NAJWYZSZY_WIERSZ_MM = 6.0
    NAJNIZSZY_WIERSZ_MM = 3.3
    MIEJSCE_MECZOW_MM = 178.0
    NAJSZERSZY_MECZ_MM = 13.0

    def uklad(self, liczba_zawodnikow: int, liczba_meczow: int) -> UkladZestawieniaViewModel:
        wysokosc = self.MIEJSCE_WIERSZY_MM / max(liczba_zawodnikow + 1, 1)
        wysokosc = max(self.NAJNIZSZY_WIERSZ_MM, min(self.NAJWYZSZY_WIERSZ_MM, wysokosc))
        szerokosc = min(self.NAJSZERSZY_MECZ_MM, self.MIEJSCE_MECZOW_MM / max(liczba_meczow, 1))
        return UkladZestawieniaViewModel(
            wysokosc_wiersza_mm=round(wysokosc, 2),
            czcionka_pt=round(min(8.0, wysokosc * 1.5, szerokosc * 0.85), 1),
            szerokosc_meczu_mm=round(szerokosc, 2),
        )


class RaportDruzynyPresenter:
    def __init__(
        self,
        druzyna: SzczegolyDruzynyPresenter,
        kolejnosc: KolejnoscZawodnikowRaportuPolicy,
        miejsca: MiejscaPolicy,
        uklad_raportu: UkladRaportuPolicy,
        uklad_zestawien: UkladZestawieniaPolicy,
    ) -> None:
        self._druzyna = druzyna
        self._kolejnosc = kolejnosc
        self._miejsca = miejsca
        self._uklad_raportu = uklad_raportu
        self._uklad_zestawien = uklad_zestawien

    def przygotuj_raport(self, raport: RaportDruzyny) -> RaportDruzynyViewModel:
        sezony = tuple(
            w
            for w in self._druzyna.przygotuj_sezony(raport.sezony)
            if w.podsumowanie_sezonu or w.sezon == raport.sezon.sezon
        )
        zawodnicy = self._zawodnicy(raport)
        mecze = self._mecze(raport.mecze)
        grupy = len({z.grupa for z in zawodnicy})
        return RaportDruzynyViewModel(
            druzyna=(raport.sezon.nazwa or raport.szczegoly.nazwa or "").strip(),
            opis=" · ".join(
                c
                for c in (
                    PLCIE.get(raport.szczegoly.plec or "", ""),
                    raport.szczegoly.kategoria,
                    raport.sezon.miasto,
                )
                if c
            ),
            sezon=raport.sezon.sezon,
            poprzedni_sezon=raport.poprzedni_sezon or "",
            rozgrywki=", ".join(raport.rozgrywki),
            stan_na=raport.stan_na.strftime("%d.%m.%Y"),
            liczby=self._liczby(raport),
            sezony=sezony,
            zawodnicy=zawodnicy,
            ze_skladu=raport.ze_skladu,
            mecze=mecze,
            uklad=self._uklad_raportu.uklad(len(sezony) + len(zawodnicy) + grupy + len(mecze)),
        )

    def przygotuj_zestawienia(self, dane: ZestawieniaDruzyny) -> ZestawieniaDruzynyViewModel:
        return ZestawieniaDruzynyViewModel(
            druzyna=(dane.szczegoly.nazwa or "").strip(),
            stan_na=dane.stan_na.strftime("%d.%m.%Y"),
            strony=tuple(self._strona(strona, dane.szczegoly.nazwa) for strona in dane.strony),
        )

    def _liczby(self, raport: RaportDruzyny) -> tuple[LiczbaRaportuViewModel, ...]:
        bilans = self._druzyna.przygotuj_bilans(raport.bilans)
        najlepszy = max(
            (z for z in raport.zawodnicy if z.sezon and z.sezon.bramki),
            key=lambda z: z.sezon.bramki or 0 if z.sezon else 0,
            default=None,
        )
        forma = " ".join(
            LITERY_REZULTATOW[m.wystep.rezultat][0] if m.wystep.rezultat else "·"
            for m in reversed(raport.mecze[:5])
        )
        return (
            LiczbaRaportuViewModel("Mecze", str(bilans.rozegrane)),
            LiczbaRaportuViewModel(
                "W – R – P", f"{bilans.wygrane} – {bilans.remisy} – {bilans.porazki}"
            ),
            LiczbaRaportuViewModel("Bramki", bilans.bramki, bilans.roznica),
            LiczbaRaportuViewModel(
                "Średnio", f"{bilans.srednia_zdobytych} : {bilans.srednia_straconych}"
            ),
            LiczbaRaportuViewModel(
                "Najlepszy strzelec",
                nazwa_zawodnika(najlepszy.imie, najlepszy.nazwisko, najlepszy.id_zawodnik)
                if najlepszy
                else BRAK,
                str(najlepszy.sezon.bramki) if najlepszy and najlepszy.sezon else "",
            ),
            LiczbaRaportuViewModel("Ostatnie 5", forma or BRAK),
        )

    def _zawodnicy(self, raport: RaportDruzyny) -> tuple[ZawodnikRaportuViewModel, ...]:
        zawodnicy = raport.zawodnicy
        bramki = self._miejsca.najlepsi(
            {z.id_zawodnik: z.sezon.bramki for z in zawodnicy if z.sezon and z.sezon.bramki},
            NAJLEPSZYCH_STRZELCOW,
        )
        karne = self._miejsca.najlepsi(
            {
                z.id_zawodnik: skutecznosc(z.sezon.karne_bramki, z.sezon.karne_liczba)
                for z in zawodnicy
                if z.sezon and (z.sezon.karne_liczba or 0) >= NAJMNIEJ_KARNYCH
            },
            NAJLEPSZYCH_KARNYCH,
        )
        poprzednie = self._miejsca.najlepsi(
            {z.id_zawodnik: z.poprzedni.bramki for z in zawodnicy if z.poprzedni.bramki},
            NAJLEPSZYCH_STRZELCOW,
        )
        wynik = []
        poprzednia_grupa: int | None = None
        for zawodnik in zawodnicy:
            grupa = self._kolejnosc.grupa(zawodnik)
            wynik.append(
                self._zawodnik(
                    zawodnik,
                    raport,
                    grupa,
                    poprzednia_grupa is not None and grupa != poprzednia_grupa,
                    zawodnik.id_zawodnik in bramki,
                    zawodnik.id_zawodnik in karne,
                    zawodnik.id_zawodnik in poprzednie,
                )
            )
            poprzednia_grupa = grupa
        return tuple(wynik)

    def _zawodnik(
        self,
        zawodnik: ZawodnikRaportu,
        raport: RaportDruzyny,
        grupa: int,
        nowa_grupa: bool,
        wyroznij_bramki: bool,
        wyroznij_karne: bool,
        wyroznij_poprzednie: bool,
    ) -> ZawodnikRaportuViewModel:
        sezon = zawodnik.sezon
        mecze = sezon.mecze if sezon else 0
        bramki = sezon.bramki if sezon else None
        return ZawodnikRaportuViewModel(
            numer=", ".join(str(n) for n in zawodnik.numery),
            nazwa=nazwa_zawodnika(zawodnik.imie, zawodnik.nazwisko, zawodnik.id_zawodnik),
            rocznik=rocznik(zawodnik.data_urodzenia),
            pozycja=skrot_pozycji(zawodnik.pozycja),
            grupa=GRUPY_POZYCJI[min(grupa, len(GRUPY_POZYCJI) - 1)],
            nowa_grupa=nowa_grupa,
            mecze=str(mecze) if sezon else "0",
            bramki=str(bramki) if bramki is not None else ("0" if not sezon else BRAK),
            srednia=f"{bramki / mecze:.1f}" if bramki is not None and mecze else BRAK,
            karne=f"{sezon.karne_bramki or 0}/{sezon.karne_liczba}"
            if sezon and sezon.karne_liczba
            else "",
            karne_procent=procent(sezon.karne_bramki, sezon.karne_liczba) if sezon else "",
            dwie_minuty=str(sezon.dwie_minuty) if sezon and sezon.dwie_minuty else "",
            upomnienia=str(sezon.upomnienia) if sezon and sezon.upomnienia else "",
            dyskwalifikacje=str(sezon.dyskwalifikacje) if sezon and sezon.dyskwalifikacje else "",
            poprzedni=self._poprzedni(zawodnik, raport, wyroznij_poprzednie),
            wyroznij_bramki=wyroznij_bramki,
            wyroznij_karne=wyroznij_karne,
        )

    @staticmethod
    def _poprzedni(
        zawodnik: ZawodnikRaportu, raport: RaportDruzyny, wyroznij: bool
    ) -> PoprzedniSezonViewModel:
        poprzedni = zawodnik.poprzedni
        if not poprzedni.zagral:
            return PoprzedniSezonViewModel(False, "", "", "", "brak meczów", False)
        grupy: dict[int | None, list[WystepSezonuZawodnika]] = {}
        for wystep in poprzedni.wystepy:
            grupy.setdefault(wystep.id_zespol, []).append(wystep)
        kluby = []
        for id_zespol, wystepy in grupy.items():
            glowne = max(wystepy, key=lambda w: w.mecze)
            if id_zespol == raport.szczegoly.id_zespol:
                if any(w.rozgrywki in raport.rozgrywki for w in wystepy):
                    kluby.append("ten sam klub")
                else:
                    kluby.append(f"ten sam klub · {glowne.rozgrywki or BRAK}")
            else:
                kluby.append(f"{(glowne.zespol or BRAK).strip()} · {glowne.rozgrywki or BRAK}")
        return PoprzedniSezonViewModel(
            zagral=True,
            mecze=str(poprzedni.mecze),
            bramki=str(poprzedni.bramki),
            srednia=f"{poprzedni.bramki / poprzedni.mecze:.1f}" if poprzedni.mecze else BRAK,
            klub="; ".join(dict.fromkeys(kluby)),
            inny_klub=all(w.id_zespol != raport.szczegoly.id_zespol for w in poprzedni.wystepy),
            wyroznij_bramki=wyroznij,
        )

    @staticmethod
    def _mecze(mecze: Sequence[MeczRaportu]) -> tuple[MeczRaportuViewModel, ...]:
        wynik = []
        for indeks, mecz in enumerate(mecze):
            wystep = mecz.wystep
            litera, klasa = (
                LITERY_REZULTATOW[wystep.rezultat] if wystep.rezultat else ("wo", "inny")
            )
            wynik.append(
                MeczRaportuViewModel(
                    data=wystep.termin.strftime("%d.%m.%y") if wystep.termin else BRAK,
                    rozgrywki=wystep.rozgrywki or BRAK,
                    miejsce="D" if wystep.miejsce == "dom" else "W",
                    przeciwnik=(wystep.przeciwnik or BRAK).strip(),
                    wynik=f"{wystep.bramki}:{wystep.stracone}"
                    if wystep.bramki is not None and wystep.stracone is not None
                    else BRAK,
                    rezultat=litera,
                    rezultat_klasa=klasa,
                    rozstrzygniecie=ZNACZNIKI_ROZSTRZYGNIEC.get(wystep.rozstrzygniecie, "")
                    if wystep.rozstrzygniecie
                    else "",
                    karne=f"{mecz.karne_bramki or 0}/{mecz.karne_liczba}"
                    if mecz.karne_liczba
                    else BRAK,
                    dwie_minuty=str(mecz.dwie_minuty) if mecz.dwie_minuty is not None else BRAK,
                    widzowie=str(wystep.widzowie) if wystep.widzowie is not None else BRAK,
                    strzelcy=", ".join(f"{s.nazwisko} {s.bramki}" for s in mecz.strzelcy) or BRAK,
                    nowy_sezon=indeks > 0 and wystep.sezon != mecze[indeks - 1].wystep.sezon,
                )
            )
        return tuple(wynik)

    def _strona(self, strona: StronaZestawien, nazwa_klubu: str | None) -> StronaZestawienViewModel:
        zestawienie = strona.zestawienie
        if zestawienie is None or not zestawienie.mecze:
            return StronaZestawienViewModel(
                sezon=strona.sezon,
                opis=self._opis_strony(strona),
                brak=(
                    f"{(nazwa_klubu or 'Drużyna').strip()} nie ma wpisu w sezonie {strona.sezon}."
                    if zestawienie is None
                    else f"Brak protokołów meczów drużyny w sezonie {strona.sezon}."
                ),
                mecze=(),
                wiersze=(),
                sumy_meczow=(),
                suma=None,
                uklad=self._uklad_zestawien.uklad(0, 0),
            )
        najlepsi_meczu = tuple(
            max((k.bramki or 0 for w in zestawienie.wiersze if (k := w.komorki[i])), default=0)
            for i in range(len(zestawienie.mecze))
        )
        bramki = self._miejsca.najlepsi(
            {w.id_zawodnik: w.suma.bramki for w in zestawienie.wiersze if w.suma.bramki},
            NAJLEPSZYCH_STRZELCOW,
        )
        karne = self._miejsca.najlepsi(
            {
                w.id_zawodnik: skutecznosc(w.suma.karne_trafione, w.suma.karne_wszystkie)
                for w in zestawienie.wiersze
                if (w.suma.karne_wszystkie or 0) >= NAJMNIEJ_KARNYCH
            },
            NAJLEPSZYCH_KARNYCH,
        )
        wiersze = []
        poprzednia: int | None = None
        for wiersz in zestawienie.wiersze:
            grupa = self._kolejnosc.grupa_pozycji(wiersz.pozycje)
            wiersze.append(
                self._wiersz(
                    wiersz,
                    strona.roczniki,
                    najlepsi_meczu,
                    poprzednia is not None and grupa != poprzednia,
                    wiersz.id_zawodnik in bramki,
                    wiersz.id_zawodnik in karne,
                )
            )
            poprzednia = grupa
        return StronaZestawienViewModel(
            sezon=strona.sezon,
            opis=self._opis_strony(strona),
            brak="",
            mecze=tuple(
                KolumnaZestawieniaRaportuViewModel(
                    data=w.termin.strftime("%d.%m") if w.termin else "",
                    przeciwnik=(w.przeciwnik or BRAK).strip(),
                    miejsce="D" if w.miejsce == "dom" else "W",
                    wynik=f"{w.bramki}:{w.stracone}"
                    if w.bramki is not None and w.stracone is not None
                    else BRAK,
                    zdobyte=str(w.bramki) if w.bramki is not None else BRAK,
                    stracone=str(w.stracone) if w.stracone is not None else "",
                    wygrana=w.rezultat == RezultatMeczu.WYGRANA,
                )
                for w in zestawienie.mecze
            ),
            wiersze=tuple(wiersze),
            sumy_meczow=tuple(self._komorka(k) for k in zestawienie.sumy_meczow),
            suma=self._suma(zestawienie.suma),
            uklad=self._uklad_zestawien.uklad(len(wiersze), len(zestawienie.mecze)),
        )

    def _opis_strony(self, strona: StronaZestawien) -> str:
        czesci = [", ".join(strona.rozgrywki)] if strona.rozgrywki else []
        if strona.bilans is not None:
            bilans: BilansDruzyny = strona.bilans
            czesci.append(f"{bilans.rozegrane} meczów")
            czesci.append(f"{bilans.wygrane}–{bilans.remisy}–{bilans.porazki}")
            czesci.append(f"bramki {bilans.bramki_zdobyte}:{bilans.bramki_stracone}")
        return " · ".join(czesci)

    def _wiersz(
        self,
        wiersz: WierszZestawienia,
        roczniki: Mapping[int, date | None],
        najlepsi_meczu: tuple[int, ...],
        nowa_grupa: bool,
        wyroznij_bramki: bool,
        wyroznij_karne: bool,
    ) -> WierszZestawieniaRaportuViewModel:
        return WierszZestawieniaRaportuViewModel(
            nazwa=nazwa_zawodnika(wiersz.imie, wiersz.nazwisko, wiersz.id_zawodnik),
            numery=", ".join(str(n) for n in wiersz.numery),
            rocznik=rocznik(roczniki.get(wiersz.id_zawodnik)),
            pozycja=skrot_pozycji(wiersz.pozycje[0] if wiersz.pozycje else None),
            nowa_grupa=nowa_grupa,
            komorki=tuple(
                self._komorka(k, najlepszy=najlepsi_meczu[i] > 0 and k.bramki == najlepsi_meczu[i])
                if k
                else None
                for i, k in enumerate(wiersz.komorki)
            ),
            suma=self._suma(wiersz.suma, wyroznij_bramki, wyroznij_karne),
        )

    @staticmethod
    def _kary(dane: StatystykiZestawienia) -> str:
        kary = []
        if dane.dwie_minuty:
            kary.append("′" * dane.dwie_minuty if dane.dwie_minuty < 4 else f"{dane.dwie_minuty}′")
        if dane.upomnienia:
            kary.append("U" if dane.upomnienia == 1 else f"{dane.upomnienia}U")
        if dane.dyskwalifikacje:
            kary.append("D" if dane.dyskwalifikacje == 1 else f"{dane.dyskwalifikacje}D")
        return "".join(kary)

    def _komorka(
        self, dane: StatystykiZestawienia, najlepszy: bool = False
    ) -> KomorkaZestawieniaRaportuViewModel:
        karne = f"{dane.karne_trafione or 0}/{dane.karne_wszystkie}" if dane.karne_wszystkie else ""
        opis = [f"bramki {dane.bramki if dane.bramki is not None else BRAK}"]
        if dane.dwie_minuty:
            opis.append(f"2 min ×{dane.dwie_minuty}")
        if dane.upomnienia:
            opis.append(f"upomnienia {dane.upomnienia}")
        if dane.dyskwalifikacje:
            opis.append(f"dyskwalifikacje {dane.dyskwalifikacje}")
        if karne:
            opis.append(f"karne {karne}")
        return KomorkaZestawieniaRaportuViewModel(
            bramki=str(dane.bramki) if dane.bramki is not None else "–",
            kary=self._kary(dane),
            karne=karne,
            opis=" · ".join(opis),
            najlepszy=najlepszy,
        )

    def _suma(
        self,
        dane: StatystykiZestawienia,
        wyroznij_bramki: bool = False,
        wyroznij_karne: bool = False,
    ) -> SumaZestawieniaRaportuViewModel:
        kary = []
        if dane.dwie_minuty:
            kary.append(f"{dane.dwie_minuty}×2′")
        if dane.upomnienia:
            kary.append(f"{dane.upomnienia}U")
        if dane.dyskwalifikacje:
            kary.append(f"{dane.dyskwalifikacje}D")
        return SumaZestawieniaRaportuViewModel(
            mecze=str(dane.mecze),
            bramki=str(dane.bramki) if dane.bramki is not None else BRAK,
            karne=f"{dane.karne_trafione or 0}/{dane.karne_wszystkie} "
            f"({procent(dane.karne_trafione, dane.karne_wszystkie)})"
            if dane.karne_wszystkie
            else "",
            kary=" ".join(kary),
            wyroznij_bramki=wyroznij_bramki,
            wyroznij_karne=wyroznij_karne,
        )
