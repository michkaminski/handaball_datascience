from __future__ import annotations

from datetime import datetime

from handball.domain.match_predictions import KlasaTrafnosci
from handball.domain.match_report import (
    AnalizaModelu,
    AtakDruzyny,
    RaportMeczu,
    StrzelecRaportu,
    TloLigi,
    TloSezonuDruzyny,
)
from handball.domain.match_statistics import StatystykiDruzynyMeczu, StatystykiMeczu
from handball.interface.match_report_charts import (
    HistogramResztBuilder,
    WykresRatinguBuilder,
    WykresSezonuBuilder,
    liczba,
    ze_znakiem,
)
from handball.interface.presenters.match_statistics_presenter import StatystykiMeczuPresenter
from handball.interface.view_models.match_report import (
    AtakRaportuViewModel,
    DruzynaRaportuViewModel,
    HistoriaSpotkanViewModel,
    KafelekRaportu,
    MeczBezposredniViewModel,
    ModelRaportuViewModel,
    RaportMeczuViewModel,
    SegmentAtakuViewModel,
    StrukturaAtakuViewModel,
    StrzelecRaportuViewModel,
    TloRaportuViewModel,
    WierszPorownaniaRaportu,
)

BRAK = "—"
DNI = ("poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela")
MIESIACE = (
    "stycznia",
    "lutego",
    "marca",
    "kwietnia",
    "maja",
    "czerwca",
    "lipca",
    "sierpnia",
    "września",
    "października",
    "listopada",
    "grudnia",
)
OCENY = {
    KlasaTrafnosci.BARDZO_TRAFNA: "bardzo trafna",
    KlasaTrafnosci.TRAFNA: "trafna",
    KlasaTrafnosci.PRZECIETNA: "przeciętna",
    KlasaTrafnosci.SLABA: "słaba",
    KlasaTrafnosci.BARDZO_SLABA: "bardzo słaba",
}


def procent(wartosc: float) -> str:
    return f"{round(100 * wartosc)}%"


def bramki_slowo(n: int) -> str:
    if n == 1:
        return "bramka"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "bramki"
    return "bramek"


class RaportMeczuPresenter:
    LIMIT_STRZELCOW = 9
    LIMIT_HISTORII = 8
    MINIMUM_MECZOW_ZAWODNIKA = 5
    MINIMUM_MECZOW_DRUZYNY = 3
    PROG_WYJATKOWOSCI = 0.1
    MINIMUM_BRAMEK_WYJATKOWOSCI = 3

    def __init__(
        self,
        statystyki: StatystykiMeczuPresenter,
        histogram: HistogramResztBuilder,
        rating: WykresRatinguBuilder,
        sezon: WykresSezonuBuilder,
    ) -> None:
        self._statystyki = statystyki
        self._histogram = histogram
        self._rating = rating
        self._sezon = sezon

    def przygotuj(
        self, raport: RaportMeczu, limit_strzelcow: int | None = None
    ) -> RaportMeczuViewModel:
        limit = limit_strzelcow or self.LIMIT_STRZELCOW
        s = raport.statystyki
        gospodarz = s.gospodarz.nazwa or BRAK
        gosc = s.gosc.nazwa or BRAK
        widok_statystyk = self._statystyki.przygotuj(s)
        model = raport.model
        druzyny = [
            DruzynaRaportuViewModel(
                gospodarz,
                "home",
                self._atak(raport.atak_gospodarza, raport, limit),
                self._tlo(raport.tlo_gospodarza, gospodarz),
                widok_statystyk.forma_gospodarz,
            ),
            DruzynaRaportuViewModel(
                gosc,
                "away",
                self._atak(raport.atak_goscia, raport, limit),
                self._tlo(raport.tlo_goscia, gosc),
                widok_statystyk.forma_gosc,
            ),
        ]
        return RaportMeczuViewModel(
            id_mecz=raport.mecz.id_mecz,
            tytul_dokumentu=f"Raport meczu: {gospodarz} — {gosc}",
            kontekst=self._kontekst(raport),
            termin=self._termin(raport.mecz.data_faktyczna),
            hala=", ".join(x for x in (raport.mecz.hala, raport.mecz.miasto) if x) or BRAK,
            widzowie=self._tysiace(raport.widzowie) if raport.widzowie else "",
            gospodarz=gospodarz,
            gosc=gosc,
            wynik=f"{s.gospodarz.bramki}:{s.gosc.bramki}",
            przebieg=self._przebieg(s),
            dopisek=self._dopisek(s),
            naglowek=self._naglowek(s, model),
            wnioski=self._wnioski(raport),
            kafelki=self._kafelki(raport),
            porownanie=self._porownanie(raport),
            model=self._model(model, raport.nazwa_modelu, gospodarz, gosc, s),
            wykres_ratingu=(
                self._rating.zbuduj(
                    [
                        ("home", model.sciezka_gospodarza, self._skrot(gospodarz, 16)),
                        ("away", model.sciezka_goscia, self._skrot(gosc, 16)),
                    ]
                )
                if model
                else None
            ),
            opis_ratingu=self._opis_ratingu(model, gospodarz, gosc) if model else "",
            druzyny=druzyny,
            przypisy=self._przypisy(druzyny),
            struktura=[] if model else self._struktura(raport, gospodarz, gosc),
            historia=self._historia(raport),
            dlugie_nazwy=max(len(gospodarz), len(gosc)) > 22,
        )

    def _kontekst(self, raport: RaportMeczu) -> str:
        mecz = raport.mecz
        kolejka = mecz.kolejka or (f"{mecz.nr_kolejki}. kolejka" if mecz.nr_kolejki else None)
        return " · ".join(x for x in (mecz.rozgrywki, mecz.sezon, mecz.runda, kolejka) if x)

    def _termin(self, data: datetime | None) -> str:
        if data is None:
            return BRAK
        return (
            f"{DNI[data.weekday()]}, {data.day} {MIESIACE[data.month - 1]} {data.year}"
            f" · {data:%H:%M}"
        )

    def _tysiace(self, wartosc: int) -> str:
        return f"{wartosc:,}".replace(",", " ")

    def _przebieg(self, s: StatystykiMeczu) -> str:
        a, b = s.gospodarz, s.gosc
        if a.bramki_do_przerwy is None or b.bramki_do_przerwy is None:
            return ""
        return (
            f"do przerwy {a.bramki_do_przerwy}:{b.bramki_do_przerwy} · "
            f"druga połowa {a.bramki_druga_polowa}:{b.bramki_druga_polowa}"
        )

    def _dopisek(self, s: StatystykiMeczu) -> str:
        if s.dogrywka_gospodarz is not None and s.dogrywka_gosc is not None:
            return f"po dogrywce {s.dogrywka_gospodarz}:{s.dogrywka_gosc}"
        if s.seria_gospodarz is not None and s.seria_gosc is not None:
            return f"rzuty karne {s.seria_gospodarz}:{s.seria_gosc}"
        return ""

    def _naglowek(self, s: StatystykiMeczu, model: AnalizaModelu | None) -> str:
        a, b = s.gospodarz.bramki or 0, s.gosc.bramki or 0
        wynik = f"{a}:{b}"
        if a == b:
            if s.wnioski and s.wnioski[0].startswith("Po 60 minutach"):
                return s.wnioski[0]
            return f"Remis {wynik}" + (
                f" — model typował {self._oczekiwany(model)}." if model else "."
            )
        zwyciezca = s.gospodarz if a > b else s.gosc
        nazwa = zwyciezca.nazwa or BRAK
        if model is None or model.prawdopodobienstwa is None:
            return f"{nazwa} wygrywa {wynik}."
        szanse = model.prawdopodobienstwa
        szansa = szanse[0] if a > b else szanse[2]
        przewaga = (a - b) - model.oczekiwana_roznica
        if a < b:
            przewaga = -przewaga
        if szansa < 0.4:
            return (
                f"Niespodzianka: {nazwa} wygrywa {wynik}, choć model dawał tej drużynie "
                f"tylko {procent(szansa)} szans."
            )
        if szansa < 0.5:
            return f"{nazwa} wygrywa {wynik} w meczu, który model uznawał za otwarty."
        if przewaga >= 4:
            return (
                f"{nazwa} wygrywa {wynik} — wyżej, niż przewidywał model "
                f"({self._oczekiwany(model)})."
            )
        if przewaga <= -4:
            return (
                f"{nazwa} wygrywa {wynik}, ale skromniej, niż zakładał model "
                f"({self._oczekiwany(model)})."
            )
        return f"{nazwa} wygrywa {wynik} — zgodnie z prognozą modelu ({self._oczekiwany(model)})."

    def _oczekiwany(self, model: AnalizaModelu | None) -> str:
        if model is None:
            return BRAK
        return f"{liczba(model.oczekiwane_gospodarza)} : {liczba(model.oczekiwane_goscia)}"

    def _wnioski(self, raport: RaportMeczu) -> list[str]:
        s = raport.statystyki
        podstawowe = [w for w in s.wnioski if w != self._naglowek(s, raport.model)]
        dodatkowe = [
            w
            for w in (
                self._wniosek_strzelca(raport),
                self._wniosek_sezonu(raport.tlo_gospodarza, s.gospodarz.nazwa),
                self._wniosek_sezonu(raport.tlo_goscia, s.gosc.nazwa),
            )
            if w
        ]
        return (podstawowe[:2] + dodatkowe[:2] + podstawowe[2:] + dodatkowe[2:])[:4]

    def _wniosek_strzelca(self, raport: RaportMeczu) -> str | None:
        kandydaci = [
            (p, strzelec, druzyna)
            for atak, druzyna in (
                (raport.atak_gospodarza, raport.statystyki.gospodarz.nazwa),
                (raport.atak_goscia, raport.statystyki.gosc.nazwa),
            )
            for strzelec in atak.strzelcy
            if (p := self._wyjatkowosc(strzelec)) is not None
        ]
        if not kandydaci:
            return None
        p, strzelec, druzyna = min(kandydaci, key=lambda k: k[0])
        czestosc = (
            "rzadziej niż raz na 1000 meczów"
            if p < 0.001
            else f"średnio raz na {max(10, round(1 / p))} meczów"
        )
        return (
            f"{strzelec.zawodnik} ({druzyna}): {strzelec.bramki} "
            f"{bramki_slowo(strzelec.bramki)} przy średniej "
            f"{liczba(strzelec.srednia_sezonu or 0)} w sezonie — taki występ zdarza się "
            f"{czestosc} (rozkład Poissona)."
        )

    def _wniosek_sezonu(self, tlo: TloSezonuDruzyny | None, nazwa: str | None) -> str | None:
        if tlo is None or tlo.mecze < 5:
            return None
        stracone, zdobyte = tlo.percentyl_straconych, tlo.percentyl_zdobytych
        if stracone is not None and stracone <= 0.1 and tlo.stracone_meczu is not None:
            return (
                f"{nazwa}: tylko {tlo.stracone_meczu} straconych {bramki_slowo(tlo.stracone_meczu)}"
                f" — lepsza obrona niż w {procent(1 - stracone)} meczów sezonu "
                f"(średnia {liczba(tlo.srednia_straconych or 0)})."
            )
        if zdobyte is not None and zdobyte >= 0.9 and tlo.bramki_meczu is not None:
            return (
                f"{nazwa}: {tlo.bramki_meczu} zdobytych {bramki_slowo(tlo.bramki_meczu)} — "
                f"więcej niż w {procent(zdobyte)} meczów sezonu "
                f"(średnia {liczba(tlo.srednia_zdobytych or 0)})."
            )
        return None

    def _kafelki(self, raport: RaportMeczu) -> list[KafelekRaportu]:
        s, model, liga = raport.statystyki, raport.model, raport.liga
        kafelki: list[KafelekRaportu] = []
        a, b = s.gospodarz.bramki or 0, s.gosc.bramki or 0
        if model and model.prawdopodobienstwa:
            szanse = model.prawdopodobienstwa
            if a == b:
                kafelki.append(
                    KafelekRaportu(
                        "Szansa na remis", procent(szanse[1]), "przed meczem, według modelu"
                    )
                )
            else:
                szansa = szanse[0] if a > b else szanse[2]
                kafelki.append(
                    KafelekRaportu(
                        "Szansa zwycięzcy",
                        procent(szansa),
                        f"przed meczem · remis {procent(szanse[1])}",
                        "hot" if szansa < 0.4 else "",
                    )
                )
        if model and model.percentyl_zaskoczenia is not None and model.z is not None:
            percentyl = model.percentyl_zaskoczenia
            kafelki.append(
                KafelekRaportu(
                    "Indeks zaskoczenia",
                    f"{round(100 * percentyl)}. pc.",
                    f"z = {ze_znakiem(model.z, 2)} σ · {len(model.reszty_ligi)} meczów ligi",
                    "hot" if percentyl >= 0.8 else "",
                )
            )
        if model:
            kafelki.append(
                KafelekRaportu(
                    "Zmiana ratingu",
                    f"±{abs(model.zmiana_ratingu):.0f}",
                    f"{self._skrot(s.gospodarz.nazwa or BRAK, 14)} "
                    f"{model.rating_gospodarza:.0f}→{model.rating_gospodarza_po:.0f}",
                )
            )
        kafelki.append(self._kafelek_bramek(a + b, liga))
        if raport.widzowie:
            kafelki.append(
                KafelekRaportu("Widzowie", self._tysiace(raport.widzowie), "na trybunach")
            )
        if len(kafelki) < 5:
            strzelec = self._najlepszy_strzelec(raport)
            if strzelec:
                kafelki.insert(1 if model else 0, strzelec)
        return kafelki[:5]

    def _najlepszy_strzelec(self, raport: RaportMeczu) -> KafelekRaportu | None:
        kandydaci = [
            (s, druzyna)
            for atak, druzyna in (
                (raport.atak_gospodarza, raport.statystyki.gospodarz.nazwa),
                (raport.atak_goscia, raport.statystyki.gosc.nazwa),
            )
            for s in atak.strzelcy[:1]
        ]
        if not kandydaci:
            return None
        s, druzyna = max(kandydaci, key=lambda k: k[0].bramki)
        return KafelekRaportu(
            "Najlepszy strzelec",
            f"{s.bramki} {bramki_slowo(s.bramki)}",
            f"{self._zawodnik(s.zawodnik)} · {self._skrot(druzyna or BRAK, 18)}",
        )

    def _kafelek_bramek(self, suma: int, liga: TloLigi | None) -> KafelekRaportu:
        if liga is None or liga.liczba_meczow < 10:
            return KafelekRaportu("Bramki w meczu", str(suma), "obie drużyny")
        return KafelekRaportu(
            "Bramki w meczu",
            str(suma),
            f"{round(100 * liga.percentyl_sumy)}. pc. sezonu · śr. {liczba(liga.srednia_sumy)}",
        )

    def _porownanie(self, raport: RaportMeczu) -> list[WierszPorownaniaRaportu]:
        a, b = raport.statystyki.gospodarz, raport.statystyki.gosc
        wiersze = [
            self._wiersz("Bramki", a.bramki, b.bramki, True),
            self._wiersz("Do przerwy", a.bramki_do_przerwy, b.bramki_do_przerwy, True),
            self._wiersz("Druga połowa", a.bramki_druga_polowa, b.bramki_druga_polowa, True),
            self._wiersz_karnych(a, b),
            self._wiersz(
                "Strzelcy",
                len(raport.atak_gospodarza.strzelcy) or None,
                len(raport.atak_goscia.strzelcy) or None,
                None,
            ),
            self._wiersz("Kary 2 min", a.dwie_minuty, b.dwie_minuty, False),
            self._wiersz(
                "Czasy drużyny",
                len(a.timeouty) if a.timeouty is not None else None,
                len(b.timeouty) if b.timeouty is not None else None,
                None,
            ),
            self._wiersz("Upomnienia", a.upomnienia, b.upomnienia, False),
            self._wiersz("Dyskwalifikacje", a.dyskwalifikacje, b.dyskwalifikacje, False),
        ]
        return [w for w in wiersze if w is not None]

    def _wiersz(
        self, etykieta: str, a: int | None, b: int | None, wiecej_lepiej: bool | None
    ) -> WierszPorownaniaRaportu | None:
        if a is None or b is None:
            return None
        if a == 0 and b == 0 and etykieta in {"Dyskwalifikacje", "Upomnienia"}:
            return None
        najwiecej = max(a, b, 1)
        lepszy = None
        if wiecej_lepiej is not None and a != b:
            lepszy = "home" if (a > b) == wiecej_lepiej else "away"
        return WierszPorownaniaRaportu(
            etykieta,
            str(a),
            str(b),
            round(100 * a / najwiecej),
            round(100 * b / najwiecej),
            lepszy,
        )

    def _wiersz_karnych(
        self, a: StatystykiDruzynyMeczu, b: StatystykiDruzynyMeczu
    ) -> WierszPorownaniaRaportu | None:
        if not a.karne_wykonane and not b.karne_wykonane:
            return None
        x, y = a.skutecznosc_karnych, b.skutecznosc_karnych
        lepszy = None
        if x is not None and y is not None and x != y:
            lepszy = "home" if x > y else "away"
        return WierszPorownaniaRaportu(
            "Rzuty karne",
            f"{a.karne_trafione or 0}/{a.karne_wykonane or 0}",
            f"{b.karne_trafione or 0}/{b.karne_wykonane or 0}",
            round(100 * (x or 0)),
            round(100 * (y or 0)),
            lepszy,
        )

    def _model(
        self,
        model: AnalizaModelu | None,
        nazwa: str,
        gospodarz: str,
        gosc: str,
        s: StatystykiMeczu,
    ) -> ModelRaportuViewModel | None:
        if model is None:
            return None
        szanse = model.prawdopodobienstwa
        if szanse:
            h, r = round(100 * szanse[0]), round(100 * szanse[1])
            szansa = (h, r, 100 - h - r)
        else:
            szansa = (0, 0, 0)
        percentyl = model.percentyl_zaskoczenia
        histogram = (
            self._histogram.zbuduj(model.reszty_ligi, model.reszta, model.sigma)
            if model.sigma and model.reszty_ligi
            else None
        )
        return ModelRaportuViewModel(
            nazwa=nazwa,
            szansa_gospodarza=szansa[0],
            szansa_remisu=szansa[1],
            szansa_goscia=szansa[2],
            oczekiwany_wynik=self._oczekiwany(model),
            wynik=f"{s.gospodarz.bramki}:{s.gosc.bramki}",
            reszta=ze_znakiem(model.reszta),
            ocena=OCENY.get(model.klasa, model.klasa.value),
            rating_gospodarza=f"{model.rating_gospodarza:.0f}",
            rating_goscia=f"{model.rating_goscia:.0f}",
            zmiana_gospodarza=ze_znakiem(model.zmiana_ratingu, 0),
            zmiana_goscia=ze_znakiem(-model.zmiana_ratingu, 0),
            ranking_gospodarza=(
                f"{model.ranking_gospodarza.miejsce}/{model.ranking_gospodarza.liczba}"
                if model.ranking_gospodarza
                else BRAK
            ),
            ranking_goscia=(
                f"{model.ranking_goscia.miejsce}/{model.ranking_goscia.liczba}"
                if model.ranking_goscia
                else BRAK
            ),
            histogram=histogram,
            opis_histogramu=(
                f"Różnica wynik − prognoza w {len(model.reszty_ligi)} meczach ligi "
                f"(σ = {liczba(model.sigma or 0)}). Pomarańczowe: wyniki co najmniej tak "
                f"zaskakujące jak ten"
                + (f" ({procent(1 - percentyl)})." if percentyl is not None else ".")
            ),
        )

    def _opis_ratingu(self, model: AnalizaModelu, gospodarz: str, gosc: str) -> str:
        rankingi = []
        for nazwa, miejsce in ((gospodarz, model.ranking_gospodarza), (gosc, model.ranking_goscia)):
            if miejsce:
                rankingi.append(f"{nazwa} {miejsce.miejsce}. z {miejsce.liczba}")
        return "Ranking siły po meczu: " + ", ".join(rankingi) + "." if rankingi else ""

    def _atak(
        self, atak: AtakDruzyny, raport: RaportMeczu, limit: int
    ) -> AtakRaportuViewModel | None:
        if not atak.strzelcy:
            return None
        najwiecej = max(
            [s.bramki for s in raport.atak_gospodarza.strzelcy + raport.atak_goscia.strzelcy]
        )
        pokazani = atak.strzelcy[:limit]
        pozostali = atak.strzelcy[limit:]
        efektywna = atak.efektywna_liczba_strzelcow
        udzial = atak.udzial_trzech
        return AtakRaportuViewModel(
            strzelcy=[self._strzelec(s, najwiecej) for s in pokazani],
            pozostali=", ".join(f"{s.zawodnik} {s.bramki}" for s in pozostali),
            efektywna_liczba=liczba(efektywna) if efektywna is not None else BRAK,
            udzial_trzech=procent(udzial) if udzial is not None else BRAK,
            zawodnicy_bez_bramki=str(atak.zawodnicy_bez_bramki),
        )

    def _strzelec(self, s: StrzelecRaportu, najwiecej: int) -> StrzelecRaportuViewModel:
        srednia = s.srednia_sezonu if s.mecze_sezonu >= self.MINIMUM_MECZOW_ZAWODNIKA else None
        roznica = s.bramki - srednia if srednia is not None else None
        p = self._wyjatkowosc(s)
        karne = f"{s.karne_bramki or 0}/{s.karne_liczba}" if s.karne_liczba else ""
        return StrzelecRaportuViewModel(
            nr=str(s.nr_koszulki) if s.nr_koszulki is not None else "",
            zawodnik=self._zawodnik(s.zawodnik),
            pozycja=(s.pozycja or "").strip(),
            bramki=s.bramki,
            pasek=round(100 * s.bramki / najwiecej) if najwiecej else 0,
            karne=karne,
            kary=str(s.dwie_minuty) if s.dwie_minuty else "",
            srednia=liczba(srednia) if srednia is not None else "",
            roznica=ze_znakiem(roznica) if roznica is not None else "",
            klasa_roznicy=(
                "up"
                if roznica is not None and roznica >= 1.5
                else "down"
                if roznica is not None and roznica <= -1.5
                else ""
            ),
            wyjatkowy=p is not None,
        )

    def _rozgrywki(self, nazwa: str | None) -> str:
        czesci = (nazwa or "").split()
        if len(czesci) > 1 and len(czesci[0]) >= 3 and czesci[0].isupper():
            czesci = czesci[1:]
        return " ".join(czesci)

    def _wyjatkowosc(self, s: StrzelecRaportu) -> float | None:
        if s.bramki < self.MINIMUM_BRAMEK_WYJATKOWOSCI:
            return None
        p = s.prawdopodobienstwo_wystepu(self.MINIMUM_MECZOW_ZAWODNIKA)
        return p if p is not None and p < self.PROG_WYJATKOWOSCI else None

    def _zawodnik(self, nazwa: str) -> str:
        czesci = nazwa.split()
        if len(czesci) < 2:
            return nazwa
        poczatek = len(czesci)
        while poczatek > 1 and czesci[poczatek - 1].isupper() and len(czesci[poczatek - 1]) > 1:
            poczatek -= 1
        if poczatek == len(czesci):
            poczatek = len(czesci) - 1
        nazwisko = " ".join(self._wielka(c) for c in czesci[poczatek:])
        return f"{czesci[0][0]}. {nazwisko}"

    def _wielka(self, czesc: str) -> str:
        if not czesc.isupper():
            return czesc
        if czesc.lower() in {"de", "da", "do", "dos", "das", "van", "von", "der", "di", "del"}:
            return czesc.lower()
        return "-".join(fragment.capitalize() for fragment in czesc.split("-"))

    def _przypisy(self, druzyny: list[DruzynaRaportuViewModel]) -> list[str]:
        przypisy = []
        strzelcy = [s for d in druzyny if d.atak for s in d.atak.strzelcy]
        if any(s.wyjatkowy for s in strzelcy):
            przypisy.append(
                "★ występ, który przy średniej zawodnika zdarza się rzadziej niż raz na 10 meczów "
                "(rozkład Poissona)"
            )
        if any(s.srednia for s in strzelcy):
            przypisy.append("Δ — bramki ponad średnią sezonu sprzed meczu (min. 5 meczów)")
        if any(d.tlo for d in druzyny):
            przypisy.append("kropki — wcześniejsze mecze, duża — ten mecz, kreska — średnia")
        return przypisy

    def _struktura(
        self, raport: RaportMeczu, gospodarz: str, gosc: str
    ) -> list[StrukturaAtakuViewModel]:
        wynik = []
        for atak, nazwa, strona in (
            (raport.atak_gospodarza, gospodarz, "home"),
            (raport.atak_goscia, gosc, "away"),
        ):
            suma = atak.suma_indywidualna
            if not suma:
                continue
            segmenty = [
                SegmentAtakuViewModel(
                    self._zawodnik(s.zawodnik).split(" ", 1)[-1],
                    s.bramki,
                    100 * s.bramki / suma,
                    f"s{numer}",
                )
                for numer, s in enumerate(atak.strzelcy[:3], start=1)
            ]
            reszta = sum(s.bramki for s in atak.strzelcy[3:])
            if reszta:
                segmenty.append(
                    SegmentAtakuViewModel(
                        f"pozostali ({len(atak.strzelcy) - 3})", reszta, 100 * reszta / suma, "rest"
                    )
                )
            efektywna = atak.efektywna_liczba_strzelcow
            wynik.append(
                StrukturaAtakuViewModel(
                    nazwa,
                    strona,
                    segmenty,
                    f"{len(atak.strzelcy)} strzelców · efektywnie "
                    f"{liczba(efektywna) if efektywna else BRAK} · lider "
                    f"{procent(atak.strzelcy[0].bramki / suma)} bramek",
                )
            )
        return wynik

    def _historia(self, raport: RaportMeczu) -> HistoriaSpotkanViewModel | None:
        h = raport.bezposrednie
        if h is None or not h.mecze:
            return None
        klasy = {"W": "win", "R": "draw", "P": "loss"}
        return HistoriaSpotkanViewModel(
            mecze=[
                MeczBezposredniViewModel(
                    data=f"{m.data:%d.%m.%y}",
                    miejsce="dom" if m.u_siebie else "wyjazd",
                    wynik=f"{m.bramki_zdobyte}:{m.bramki_stracone}",
                    rezultat=m.rezultat.value,
                    klasa=klasy[m.rezultat.value],
                    rozgrywki=self._rozgrywki(m.rozgrywki),
                )
                for m in h.mecze[: self.LIMIT_HISTORII]
            ],
            bilans=f"{h.bilans.wygrane}W {h.bilans.remisy}R {h.bilans.porazki}P",
            bramki=f"{h.bilans.bramki_zdobyte}:{h.bilans.bramki_stracone}",
            liczba=h.bilans.mecze,
        )

    def _tlo(self, tlo: TloSezonuDruzyny | None, nazwa: str) -> TloRaportuViewModel | None:
        if tlo is None or tlo.mecze < self.MINIMUM_MECZOW_DRUZYNY:
            return None
        wykres = self._sezon.zbuduj(
            [
                ("zdobyte", tlo.zdobyte_sezonu, tlo.bramki_meczu),
                ("stracone", tlo.stracone_sezonu, tlo.stracone_meczu),
            ]
        )
        return TloRaportuViewModel(
            wykres=wykres,
            zdobyte=self._opis_tla(
                tlo.bramki_meczu, tlo.srednia_zdobytych, tlo.percentyl_zdobytych
            ),
            stracone=self._opis_tla(
                tlo.stracone_meczu, tlo.srednia_straconych, tlo.percentyl_straconych
            ),
            opis_aria=(
                f"{nazwa}: bramki zdobyte i stracone w {tlo.mecze} wcześniejszych meczach sezonu "
                f"na tle tego meczu."
            ),
        )

    def _opis_tla(self, wartosc: int | None, srednia: float | None, percentyl: float | None) -> str:
        if wartosc is None or srednia is None:
            return BRAK
        tekst = f"{wartosc} (śr. {liczba(srednia)}, {ze_znakiem(wartosc - srednia)})"
        return tekst + (f" · {round(100 * percentyl)}. pc." if percentyl is not None else "")

    def _skrot(self, nazwa: str, limit: int = 24) -> str:
        nazwa = nazwa.strip()
        return nazwa if len(nazwa) <= limit else nazwa[: limit - 1].rstrip() + "…"
