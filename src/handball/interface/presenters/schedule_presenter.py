from __future__ import annotations

from datetime import date, datetime

from handball.domain.match_preview import (
    BezposrednieMecze,
    Bilans,
    CzlonekKadry,
    KadraDruzyny,
    MeczZapowiedzi,
    OpcjeZapowiedzi,
    ProfilDruzynyZapowiedzi,
    RezultatDruzyny,
    Seria,
    WystepZapowiedzi,
    ZapowiedzMeczu,
)
from handball.domain.match_rules import MeczPolicy, StatusMeczu
from handball.domain.schedule import (
    DzienTerminarza,
    KolejkaTerminarza,
    PozycjaTerminarza,
    RundaTerminarza,
    Terminarz,
)
from handball.interface.presenters.match_prediction_presenter import (
    PrognozaFormat,
    PrognozaMeczuPresenter,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.view_models.schedule import (
    BezposrednieMeczeViewModel,
    DzienTerminarzaViewModel,
    FormaDruzynyViewModel,
    GrupaKadryViewModel,
    KadraDruzynyViewModel,
    KolejkaTerminarzaViewModel,
    MeczTerminarzaViewModel,
    RundaTerminarzaViewModel,
    TerminarzViewModel,
    WierszPorownaniaViewModel,
    WierszWystepuViewModel,
    ZapowiedzMeczuViewModel,
    ZawodnikKadryViewModel,
    ZnakFormyViewModel,
)

BRAK = "—"
BRAK_WYNIKU = "– : –"
WSZYSTKIE_LATA = "wszystkie"
GRUPY_POZYCJI = (
    "Bramkarze",
    "Rozgrywający",
    "Skrzydłowi",
    "Obrotowi",
    "Inne pozycje",
    "Pozycja nieznana",
)
DNI_TYGODNIA = ("pon.", "wt.", "śr.", "czw.", "pt.", "sob.", "niedz.")

ETYKIETY_STATUSOW: dict[StatusMeczu, str] = {
    StatusMeczu.ROZEGRANY: "Zakończony",
    StatusMeczu.ZAPLANOWANY: "Zaplanowany",
    StatusMeczu.WALKOWER: "Walkower",
    StatusMeczu.WYCOFANY: "Wycofany",
}

OPISY_REZULTATOW: dict[RezultatDruzyny, str] = {
    RezultatDruzyny.WYGRANA: "wygrana",
    RezultatDruzyny.REMIS: "remis",
    RezultatDruzyny.PORAZKA: "porażka",
}

SERIE: dict[RezultatDruzyny, tuple[str, str, str]] = {
    RezultatDruzyny.WYGRANA: ("wygrana", "wygrane", "wygranych"),
    RezultatDruzyny.REMIS: ("remis", "remisy", "remisów"),
    RezultatDruzyny.PORAZKA: ("porażka", "porażki", "porażek"),
}


class KalendarzFormat:
    def dzien(self, wartosc: date | None) -> str:
        if wartosc is None:
            return "Termin nieustalony"
        return f"{DNI_TYGODNIA[wartosc.weekday()]} {wartosc.strftime('%d.%m.%Y')}"

    def termin(self, wartosc: datetime | None, godzina_znana: bool) -> str:
        if wartosc is None:
            return "Termin nieustalony"
        tekst = self.dzien(wartosc.date())
        return f"{tekst}, godz. {wartosc.strftime('%H:%M')}" if godzina_znana else tekst

    def zakres(self, dni: list[date]) -> str:
        if not dni:
            return BRAK
        pierwszy, ostatni = min(dni), max(dni)
        if pierwszy == ostatni:
            return pierwszy.strftime("%d.%m.%Y")
        return f"{pierwszy.strftime('%d.%m')}–{ostatni.strftime('%d.%m.%Y')}"


class TerminarzPresenter:
    def __init__(
        self, formatowanie: MeczFormat, reguly: MeczPolicy, kalendarz: KalendarzFormat
    ) -> None:
        self._format = formatowanie
        self._reguly = reguly
        self._kalendarz = kalendarz

    def przygotuj(self, terminarz: Terminarz) -> TerminarzViewModel:
        return TerminarzViewModel(
            liczba_meczow=terminarz.liczba_meczow,
            rundy=tuple(self._runda(runda) for runda in terminarz.rundy),
        )

    def _runda(self, runda: RundaTerminarza) -> RundaTerminarzaViewModel:
        return RundaTerminarzaViewModel(
            nazwa=(runda.nazwa or "").strip() or "Bez rundy",
            kolejki=tuple(self._kolejka(kolejka) for kolejka in runda.kolejki),
        )

    def _kolejka(self, kolejka: KolejkaTerminarza) -> KolejkaTerminarzaViewModel:
        mecze = [pozycja for dzien in kolejka.dni for pozycja in dzien.mecze]
        return KolejkaTerminarzaViewModel(
            id_kolejka=kolejka.id_kolejka,
            nazwa=(kolejka.nazwa or "").strip()
            or (f"Kolejka {kolejka.nr}" if kolejka.nr is not None else "Bez kolejki"),
            zakres_dat=self._kalendarz.zakres([d.dzien for d in kolejka.dni if d.dzien]),
            liczba_meczow=len(mecze),
            liczba_zakonczonych=sum(
                1 for p in mecze if self._reguly.status(p.mecz) is StatusMeczu.ROZEGRANY
            ),
            dni=tuple(self._dzien(dzien) for dzien in kolejka.dni),
        )

    def _dzien(self, dzien: DzienTerminarza) -> DzienTerminarzaViewModel:
        return DzienTerminarzaViewModel(
            data=self._kalendarz.dzien(dzien.dzien),
            mecze=tuple(self._mecz(pozycja) for pozycja in dzien.mecze),
        )

    def _mecz(self, pozycja: PozycjaTerminarza) -> MeczTerminarzaViewModel:
        mecz = pozycja.mecz
        gospodarz, gosc = self._reguly.para(mecz, pozycja.gospodarz, pozycja.gosc)
        status = self._reguly.status(mecz)
        bramki_gospodarza, bramki_goscia = self._reguly.para(
            mecz, mecz.wynik_gosp_full, mecz.wynik_gosc_full
        )
        ma_wynik = bramki_gospodarza is not None and bramki_goscia is not None
        termin = pozycja.termin
        return MeczTerminarzaViewModel(
            id_mecz=pozycja.id_mecz,
            godzina=termin.strftime("%H:%M") if termin and pozycja.godzina_znana else BRAK,
            gospodarz=self._format.tekst(gospodarz),
            gosc=self._format.tekst(gosc),
            wynik=f"{bramki_gospodarza} : {bramki_goscia}" if ma_wynik else BRAK_WYNIKU,
            dopisek=self._format.dopisek(mecz, self._reguly) if ma_wynik else None,
            status=status.value,
            etykieta_statusu=ETYKIETY_STATUSOW[status],
            hala=self._format.tekst(pozycja.hala),
            termin_proponowany=termin is not None and not pozycja.godzina_znana,
        )


class ZapowiedzMeczuPresenter:
    def __init__(
        self,
        kalendarz: KalendarzFormat,
        liczby: PrognozaFormat,
        prognozy: PrognozaMeczuPresenter,
    ) -> None:
        self._kalendarz = kalendarz
        self._liczby = liczby
        self._prognozy = prognozy

    def przygotuj(self, zapowiedz: ZapowiedzMeczu) -> ZapowiedzMeczuViewModel:
        mecz, gospodarz, gosc = zapowiedz.mecz, zapowiedz.gospodarz, zapowiedz.gosc
        z_poprzednim = zapowiedz.opcje.kadra_z_poprzedniego_sezonu
        status = self._status(mecz)
        nazwa_gospodarza = self._nazwa(gospodarz)
        nazwa_goscia = self._nazwa(gosc)
        return ZapowiedzMeczuViewModel(
            id_mecz=mecz.id_mecz,
            gospodarz=nazwa_gospodarza,
            gosc=nazwa_goscia,
            id_gospodarza=mecz.gospodarz.id_zespol,
            id_goscia=mecz.gosc.id_zespol,
            termin=self._kalendarz.termin(mecz.termin, mecz.data_faktyczna is not None),
            hala=", ".join(czesc for czesc in (mecz.hala, mecz.miasto) if czesc) or BRAK,
            kontekst=" · ".join(
                czesc for czesc in (mecz.rozgrywki, mecz.sezon, mecz.runda, mecz.kolejka) if czesc
            ),
            status=status.value,
            etykieta_statusu=ETYKIETY_STATUSOW[status],
            wynik=(
                f"{mecz.bramki_gospodarza} : {mecz.bramki_goscia}"
                if mecz.bramki_gospodarza is not None and mecz.bramki_goscia is not None
                else None
            ),
            stan_na=zapowiedz.stan_na.strftime("%d.%m.%Y %H:%M"),
            zamiana=mecz.zamiana,
            porownanie=self._porownanie(gospodarz, gosc),
            formy=(self._forma(gospodarz), self._forma(gosc)),
            bezposrednie=self._bezposrednie(zapowiedz.bezposrednie, zapowiedz.opcje),
            kadry=(self._kadra(gospodarz.kadra), self._kadra(gosc.kadra)),
            sezon=mecz.sezon or BRAK,
            sezon_poprzedni=zapowiedz.sezon_poprzedni.nazwa if zapowiedz.sezon_poprzedni else None,
            kadra_z_poprzednim=z_poprzednim,
            lata_bezposrednich=(
                str(zapowiedz.opcje.lata_bezposrednich)
                if zapowiedz.opcje.lata_bezposrednich is not None
                else WSZYSTKIE_LATA
            ),
            prognoza=self._prognozy.przygotuj_zapowiedz(zapowiedz.prognoza),
        )

    def _status(self, mecz: MeczZapowiedzi) -> StatusMeczu:
        if mecz.wycofany:
            return StatusMeczu.WYCOFANY
        if mecz.walkower:
            return StatusMeczu.WALKOWER
        if mecz.rozegrany:
            return StatusMeczu.ROZEGRANY
        return StatusMeczu.ZAPLANOWANY

    def _nazwa(self, profil: ProfilDruzynyZapowiedzi) -> str:
        return (profil.druzyna.nazwa or "").strip() or BRAK

    def _porownanie(
        self, h: ProfilDruzynyZapowiedzi, a: ProfilDruzynyZapowiedzi
    ) -> tuple[WierszPorownaniaViewModel, ...]:
        n = self._liczby
        bh, ba = h.bilans_rozgrywek, a.bilans_rozgrywek
        return (
            WierszPorownaniaViewModel("Mecze w rozgrywkach", str(bh.mecze), str(ba.mecze)),
            WierszPorownaniaViewModel(
                "Bilans W-R-P",
                self._bilans(bh),
                self._bilans(ba),
                self._przewaga(bh.procent_wygranych, ba.procent_wygranych, True),
            ),
            WierszPorownaniaViewModel(
                "Procent wygranych",
                n.procent(bh.procent_wygranych),
                n.procent(ba.procent_wygranych),
                self._przewaga(bh.procent_wygranych, ba.procent_wygranych, True),
            ),
            WierszPorownaniaViewModel(
                "Bramki zdobyte : stracone",
                self._bramki(bh),
                self._bramki(ba),
            ),
            WierszPorownaniaViewModel(
                "Różnica bramek",
                self._roznica(bh),
                self._roznica(ba),
                self._przewaga(
                    bh.roznica / bh.mecze if bh.mecze else None,
                    ba.roznica / ba.mecze if ba.mecze else None,
                    True,
                ),
            ),
            WierszPorownaniaViewModel(
                "Średnio zdobyte",
                n.liczba(bh.srednia_zdobytych, 1),
                n.liczba(ba.srednia_zdobytych, 1),
                self._przewaga(bh.srednia_zdobytych, ba.srednia_zdobytych, True),
            ),
            WierszPorownaniaViewModel(
                "Średnio stracone",
                n.liczba(bh.srednia_straconych, 1),
                n.liczba(ba.srednia_straconych, 1),
                self._przewaga(bh.srednia_straconych, ba.srednia_straconych, False),
            ),
            WierszPorownaniaViewModel(
                "Mediana zdobytych : straconych",
                self._mediany(h),
                self._mediany(a),
            ),
            WierszPorownaniaViewModel(
                "Gospodarz u siebie / gość na wyjeździe",
                self._bilans(h.bilans_miejsca),
                self._bilans(a.bilans_miejsca),
                self._przewaga(
                    h.bilans_miejsca.procent_wygranych,
                    a.bilans_miejsca.procent_wygranych,
                    True,
                ),
            ),
            WierszPorownaniaViewModel(
                "Forma (ostatnie 5, od najnowszego)",
                " ".join(w.rezultat.value for w in h.forma) or BRAK,
                " ".join(w.rezultat.value for w in a.forma) or BRAK,
                self._przewaga(self._punkty_formy(h), self._punkty_formy(a), True),
            ),
            WierszPorownaniaViewModel("Seria", self._seria(h.seria), self._seria(a.seria)),
        )

    def _bilans(self, bilans: Bilans) -> str:
        if not bilans.mecze:
            return BRAK
        return f"{bilans.wygrane}-{bilans.remisy}-{bilans.porazki}"

    def _bramki(self, bilans: Bilans) -> str:
        if not bilans.mecze:
            return BRAK
        return f"{bilans.bramki_zdobyte} : {bilans.bramki_stracone}"

    def _roznica(self, bilans: Bilans) -> str:
        if not bilans.mecze:
            return BRAK
        return self._liczby.calkowita_ze_znakiem(bilans.roznica)

    def _mediany(self, profil: ProfilDruzynyZapowiedzi) -> str:
        if profil.mediana_zdobytych is None or profil.mediana_straconych is None:
            return BRAK
        return f"{profil.mediana_zdobytych:g} : {profil.mediana_straconych:g}"

    def _punkty_formy(self, profil: ProfilDruzynyZapowiedzi) -> float | None:
        if not profil.forma:
            return None
        wagi = {RezultatDruzyny.WYGRANA: 1.0, RezultatDruzyny.REMIS: 0.5}
        return sum(wagi.get(w.rezultat, 0.0) for w in profil.forma) / len(profil.forma)

    def _seria(self, seria: Seria | None) -> str:
        if seria is None:
            return BRAK
        pojedyncza, kilka, wiele = SERIE[seria.rezultat]
        n = seria.dlugosc
        if n == 1:
            return f"1 {pojedyncza}"
        if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            return f"{n} {kilka} z rzędu"
        return f"{n} {wiele} z rzędu"

    def _przewaga(self, h: float | None, a: float | None, wyzsza_lepsza: bool) -> str:
        if h is None or a is None or h == a:
            return ""
        lepszy_gospodarz = h > a if wyzsza_lepsza else h < a
        return "gospodarz" if lepszy_gospodarz else "gosc"

    def _forma(self, profil: ProfilDruzynyZapowiedzi) -> FormaDruzynyViewModel:
        return FormaDruzynyViewModel(
            druzyna=self._nazwa(profil),
            znaki=tuple(
                ZnakFormyViewModel(
                    w.rezultat.value,
                    self._klasa(w.rezultat),
                    f"{w.data.strftime('%d.%m.%Y')}: {OPISY_REZULTATOW[w.rezultat]} "
                    f"{w.bramki_zdobyte}:{w.bramki_stracone} z {w.rywal or BRAK}",
                )
                for w in profil.forma
            ),
            wiersze=tuple(self._wystep(w) for w in profil.forma),
        )

    def _bezposrednie(
        self, bezposrednie: BezposrednieMecze, opcje: OpcjeZapowiedzi
    ) -> BezposrednieMeczeViewModel:
        bilans = bezposrednie.bilans
        lata = opcje.lata_bezposrednich
        return BezposrednieMeczeViewModel(
            liczba=bilans.mecze,
            wygrane_gospodarza=bilans.wygrane,
            remisy=bilans.remisy,
            wygrane_goscia=bilans.porazki,
            bramki=self._bramki(bilans),
            okres=(
                "wszystkie spotkania w bazie"
                if bezposrednie.od is None or lata is None
                else f"ostatnie {self._lata(lata)} (od {bezposrednie.od.strftime('%d.%m.%Y')})"
            ),
            wiersze=tuple(self._wystep(w) for w in bezposrednie.mecze),
        )

    def _wystep(self, w: WystepZapowiedzi) -> WierszWystepuViewModel:
        return WierszWystepuViewModel(
            id_mecz=w.id_mecz,
            data=w.data.strftime("%d.%m.%Y"),
            rozgrywki=w.rozgrywki or BRAK,
            rywal=w.rywal or BRAK,
            miejsce="dom" if w.u_siebie else "wyjazd",
            wynik=f"{w.bramki_zdobyte}:{w.bramki_stracone}",
            rezultat=w.rezultat.value,
            klasa=self._klasa(w.rezultat),
        )

    def _klasa(self, rezultat: RezultatDruzyny) -> str:
        return {
            RezultatDruzyny.WYGRANA: "form-win",
            RezultatDruzyny.REMIS: "form-draw",
            RezultatDruzyny.PORAZKA: "form-loss",
        }[rezultat]

    def _lata(self, lata: int) -> str:
        if lata == 1:
            return "1 rok"
        if lata % 10 in (2, 3, 4) and lata % 100 not in (12, 13, 14):
            return f"{lata} lata"
        return f"{lata} lat"

    def _kadra(self, kadra: KadraDruzyny) -> KadraDruzynyViewModel:
        return KadraDruzynyViewModel(
            druzyna=(kadra.druzyna.nazwa or "").strip() or BRAK,
            liczba_zawodnikow=kadra.liczba_zawodnikow,
            grupy=tuple(
                GrupaKadryViewModel(
                    nazwa=GRUPY_POZYCJI[min(grupa.kolejnosc, len(GRUPY_POZYCJI) - 1)],
                    zawodnicy=tuple(self._zawodnik(c) for c in grupa.czlonkowie),
                )
                for grupa in kadra.grupy
            ),
        )

    def _zawodnik(self, czlonek: CzlonekKadry) -> ZawodnikKadryViewModel:
        sezon, poprzedni = czlonek.sezon, czlonek.poprzedni_sezon
        return ZawodnikKadryViewModel(
            id_zawodnik=czlonek.id_zawodnik,
            numer="/".join(str(n) for n in czlonek.numery) or BRAK,
            nazwa=" ".join(c for c in (czlonek.imie, czlonek.nazwisko) if c)
            or f"#{czlonek.id_zawodnik}",
            pozycja=czlonek.pozycja or BRAK,
            mecze=str(sezon.mecze) if sezon else BRAK,
            bramki=str(sezon.bramki) if sezon else BRAK,
            srednia=self._liczby.liczba(czlonek.srednia, 2),
            poprzedni=(
                f"{poprzedni.bramki} / {self._liczby.liczba(poprzedni.srednia, 2)}"
                if poprzedni
                else BRAK
            ),
            poprzedni_mecze=(
                (
                    f"{self._mecze(poprzedni.mecze)} w tej drużynie"
                    if poprzedni.tylko_druzyna
                    else self._mecze(poprzedni.mecze)
                )
                if poprzedni
                else ""
            ),
            uwagi_poprzednie=(
                tuple(
                    f"inny klub: {klub.nazwa} — {self._bramki_klubu(klub.bramki)}, "
                    f"{self._mecze(klub.mecze)}"
                    for klub in poprzedni.inne_kluby
                )
                + tuple(f"inna liga: {liga}" for liga in poprzedni.inne_ligi)
                if poprzedni
                else ()
            ),
            miejsce_strzelca=czlonek.miejsce_strzelca,
            data_urodzenia=(
                czlonek.data_urodzenia.strftime("%d.%m.%Y") if czlonek.data_urodzenia else None
            ),
        )

    def _bramki_klubu(self, liczba: int) -> str:
        if liczba == 1:
            return "1 bramka"
        if liczba % 10 in (2, 3, 4) and liczba % 100 not in (12, 13, 14):
            return f"{liczba} bramki"
        return f"{liczba} bramek"

    def _mecze(self, liczba: int) -> str:
        if liczba == 1:
            return "1 mecz"
        if liczba % 10 in (2, 3, 4) and liczba % 100 not in (12, 13, 14):
            return f"{liczba} mecze"
        return f"{liczba} meczów"
