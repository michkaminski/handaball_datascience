from __future__ import annotations

import json
import math
from collections.abc import Sequence

from handball.domain.match_predictions import (
    KlasaTrafnosci,
    KlasaWyniku,
    KonfiguracjaSilyDruzyn,
    Liga,
    Plec,
    PodsumowaniePrognoz,
    PowodWykluczenia,
    PoziomRozgrywek,
    PrognozaMeczu,
    RaportPrognoz,
    RatingPrzedMeczem,
    SezonPrognoz,
    SzczegolyPrognozy,
    Typ1X2,
    UczestnikPrognozy,
)
from handball.interface.presenters.match_presenter import MeczFormat
from handball.interface.view_models.match_predictions import (
    DefinicjaPojeciaViewModel,
    HistoriaDruzynyViewModel,
    KrokObliczeniaViewModel,
    OpcjaViewModel,
    PozycjaPrognozyViewModel,
    RaportPrognozViewModel,
    StronaPrognozViewModel,
    SzczegolyPrognozyViewModel,
    WierszHistoriiViewModel,
    WierszRatinguViewModel,
    WskaznikViewModel,
)

BRAK = "—"

ETYKIETY_POZIOMOW: dict[PoziomRozgrywek, str] = {
    PoziomRozgrywek.SUPERLIGA: "Superliga",
    PoziomRozgrywek.LIGA_CENTRALNA: "Liga Centralna",
    PoziomRozgrywek.I_LIGA: "I Liga",
}

SKROTY_POZIOMOW: dict[PoziomRozgrywek, str] = {
    PoziomRozgrywek.SUPERLIGA: "SL",
    PoziomRozgrywek.LIGA_CENTRALNA: "LC",
    PoziomRozgrywek.I_LIGA: "1L",
}

ETYKIETY_PLCI: dict[Plec, str] = {Plec.MEZCZYZN: "Mężczyźni", Plec.KOBIET: "Kobiety"}

DOPELNIACZE_PLCI: dict[Plec, str] = {Plec.MEZCZYZN: "mężczyzn", Plec.KOBIET: "kobiet"}

ETYKIETY_KLAS: dict[KlasaTrafnosci, str] = {
    KlasaTrafnosci.BARDZO_TRAFNA: "Bardzo trafna",
    KlasaTrafnosci.TRAFNA: "Trafna",
    KlasaTrafnosci.PRZECIETNA: "Przeciętna",
    KlasaTrafnosci.SLABA: "Słaba",
    KlasaTrafnosci.BARDZO_SLABA: "Bardzo słaba",
}

ETYKIETY_TYPOW: dict[Typ1X2, str] = {
    Typ1X2.GOSPODARZ: "H — gospodarz",
    Typ1X2.REMIS: "X — remis",
    Typ1X2.GOSC: "A — gość",
}

ETYKIETY_KLAS_WYNIKU: dict[KlasaWyniku, str] = {
    KlasaWyniku.DOKLADNY_WYNIK: "Dokładny wynik",
    KlasaWyniku.DOKLADNA_ROZNICA: "Dokładna różnica",
    KlasaWyniku.ROZNICA_1: "Różnica ±1",
    KlasaWyniku.ROZNICA_2_3: "Różnica ±2–3",
    KlasaWyniku.ROZNICA_4_PLUS: "Różnica ±4 i więcej",
}

ETYKIETY_WYKLUCZEN: dict[PowodWykluczenia, str] = {
    PowodWykluczenia.NIEZNANA_LIGA: "Nieznana płeć rozgrywek",
    PowodWykluczenia.BRAK_DATY: "Brak data_faktyczna",
    PowodWykluczenia.NIEPRAWIDLOWA_DATA: "Data poza latami sezonu",
    PowodWykluczenia.WYCOFANY: "Mecz wycofany",
    PowodWykluczenia.WALKOWER: "Walkower",
    PowodWykluczenia.BRAK_GOSPODARZA: "Brak gospodarza",
    PowodWykluczenia.BRAK_GOSCIA: "Brak gościa",
    PowodWykluczenia.BRAK_WYNIKU: "Brak pełnego wyniku po 60 minutach",
}

SYMBOLE_PARAMETROW: tuple[tuple[str, str, str], ...] = (
    ("rating_poczatkowy", "INITIAL_RATING", "Rating drużyny bez historii w modelu"),
    ("przewaga_wlasnego_parkietu", "HOME_ADVANTAGE", "Bonus ratingowy faktycznego gospodarza"),
    ("wyraz_wolny_roznicy", "MARGIN_INTERCEPT", "Wyraz wolny przeliczenia na bramki"),
    ("nachylenie_roznicy", "MARGIN_SLOPE", "Bramki na punkt różnicy ratingów"),
    ("poczatkowa_suma_bramek", "INITIAL_EXPECTED_TOTAL", "Suma bramek ligi bez historii"),
    ("alfa_ewma", "EWMA_ALPHA", "Waga ostatniego meczu w średniej sumy bramek"),
    ("wspolczynnik_k", "K_FACTOR", "Maksymalna zmiana ratingu po meczu"),
    ("skala_roznicy", "MARGIN_SCALE", "Czułość funkcji tanh"),
    ("zachowanie_miedzy_sezonami", "SEASON_RETENTION", "Część przewagi przenoszona na sezon"),
    ("prog_remisu", "DRAW_MARGIN_THRESHOLD", "Próg typu X dla przewidywanej różnicy"),
)

DEFINICJE_MODELU: tuple[tuple[str, str], ...] = (
    (
        "Rating",
        "Dynamiczna liczba opisująca bieżącą siłę drużyny. Wyższy rating to silniejsza "
        "drużyna. Nowa drużyna startuje z INITIAL_RATING.",
    ),
    (
        "Home advantage",
        "Stały bonus ratingowy za grę we własnej hali. Otrzymuje go faktyczny "
        "gospodarz wyznaczony z uwzględnieniem pola zamiana.",
    ),
    (
        "Predicted margin",
        "Oczekiwana różnica bramek z perspektywy faktycznego gospodarza. "
        "Wartość dodatnia oznacza przewagę gospodarza, ujemna przewagę gościa.",
    ),
    ("Predicted total", "Oczekiwana suma bramek meczu, równa średniej EWMA ligi przed meczem."),
    (
        "EWMA",
        "Wykładniczo ważona średnia historycznych sum bramek, liczona osobno dla każdej ligi "
        "(poziom rozgrywek i płeć) wyłącznie z meczów rozegranych wcześniej.",
    ),
    (
        "Margin residual",
        "Różnica pomiędzy rzeczywistą i przewidywaną różnicą bramek. Dodatnia "
        "oznacza wynik gospodarza lepszy od oczekiwania.",
    ),
    (
        "K factor",
        "Maksymalna skala pojedynczej aktualizacji ratingu. Funkcja tanh nie przekracza "
        "±1, więc jeden mecz zmienia rating najwyżej o K_FACTOR.",
    ),
    (
        "Margin scale",
        "Kontroluje czułość funkcji tanh: przy reszcie równej MARGIN_SCALE poprawka "
        "wynosi około 76% K_FACTOR, a bardzo wysokie wyniki nie rozwalają skali.",
    ),
    (
        "Season retention",
        "Określa, jaka część przewagi ratingowej nad INITIAL_RATING przechodzi "
        "na następny sezon (regresja do średniej zamiast resetu).",
    ),
    (
        "Typ 1X2",
        "H — gospodarz, X — remis, A — gość. Model punktowy wskazuje typ progiem "
        "DRAW_MARGIN_THRESHOLD i nie podaje prawdopodobieństw.",
    ),
    (
        "Typ prognozy",
        "Typ 1X2 odczytany z zaokrąglonego wyniku prognozy (kolumna Prognoza) i porównany z "
        "rzeczywistym wynikiem. 38:20 przy wyniku 20:38 to typ nieprzewidziany. Różni się od "
        "typu modelu, który stosuje próg DRAW_MARGIN_THRESHOLD do dokładnej różnicy.",
    ),
    (
        "Score error",
        "Suma bezwzględnych błędów bramek gospodarza i gościa, liczona na "
        "wartościach zmiennoprzecinkowych, nie na zaokrąglonej prezentacji.",
    ),
    (
        "Ocena wyniku",
        "Porównanie zaokrąglonej prognozy z wynikiem: dokładny wynik, dokładna różnica "
        "bramek (np. 29:30 przy wyniku 30:31) albo odchylenie różnicy o 1, 2–3 lub 4+ "
        "bramki. Warstwa prezentacyjna, niezależna od score error.",
    ),
    (
        "Klasa trafności",
        "Warstwa prezentacyjna dzieląca score error progami 2, 4, 7 i 10 bramek; "
        "nie jest częścią modelu matematycznego.",
    ),
)


class PrognozaFormat:
    def liczba(self, wartosc: float | None, miejsca: int = 2) -> str:
        return BRAK if wartosc is None else f"{wartosc:.{miejsca}f}"

    def ze_znakiem(self, wartosc: float, miejsca: int = 2) -> str:
        return f"{wartosc:+.{miejsca}f}".replace("-", "−")

    def calkowita_ze_znakiem(self, wartosc: int) -> str:
        return f"{wartosc:+d}".replace("-", "−") if wartosc else "0"

    def parametr(self, wartosc: float) -> str:
        return f"{wartosc:.4f}".rstrip("0").rstrip(".")

    def skladnik(self, wartosc: float, miejsca: int = 2) -> str:
        tekst = f"{abs(wartosc):.{miejsca}f}"
        return f"(−{tekst})" if wartosc < 0 else tekst

    def procent(self, wartosc: float | None) -> str:
        return BRAK if wartosc is None else f"{100 * wartosc:.1f}%"


class PrognozaMeczuPresenter:
    def __init__(self, formatowanie: MeczFormat, liczby: PrognozaFormat) -> None:
        self._format = formatowanie
        self._liczby = liczby

    def opcje_poziomow(self) -> tuple[OpcjaViewModel, ...]:
        return tuple(
            OpcjaViewModel(poziom.value, etykieta) for poziom, etykieta in ETYKIETY_POZIOMOW.items()
        )

    def opcje_plci(self) -> tuple[OpcjaViewModel, ...]:
        return tuple(
            OpcjaViewModel(plec.value, etykieta) for plec, etykieta in ETYKIETY_PLCI.items()
        )

    def _nazwa_ligi(self, liga: Liga) -> str:
        return f"{ETYKIETY_POZIOMOW[liga.poziom]} {DOPELNIACZE_PLCI[liga.plec]}"

    def opcje_klas(self) -> tuple[OpcjaViewModel, ...]:
        return tuple(
            OpcjaViewModel(klasa.value, etykieta) for klasa, etykieta in ETYKIETY_KLAS.items()
        )

    def opcje_typow(self) -> tuple[OpcjaViewModel, ...]:
        return tuple(
            OpcjaViewModel(typ.value, etykieta) for typ, etykieta in ETYKIETY_TYPOW.items()
        )

    def opcje_klas_wyniku(self) -> tuple[OpcjaViewModel, ...]:
        return tuple(
            OpcjaViewModel(klasa.value, etykieta)
            for klasa, etykieta in ETYKIETY_KLAS_WYNIKU.items()
        )

    def opcje_sezonow(self, sezony: Sequence[SezonPrognoz]) -> tuple[OpcjaViewModel, ...]:
        return tuple(OpcjaViewModel(str(sezon.id_sezon), sezon.nazwa) for sezon in sezony)

    def przygotuj_raport(self, raport: RaportPrognoz) -> RaportPrognozViewModel:
        return RaportPrognozViewModel(
            tytul_modelu=raport.model.nazwa,
            wersja_modelu=raport.model.wersja,
            strona=StronaPrognozViewModel(
                tuple(self._pozycja(p) for p in raport.strona.pozycje),
                raport.strona.liczba_wszystkich,
                raport.strona.strona,
                raport.strona.rozmiar_strony,
            ),
            wskazniki=self._wskazniki(raport.podsumowanie),
            progi=tuple(
                WskaznikViewModel(
                    f"score_error ≤ {self._liczby.parametr(licznik.prog)}",
                    f"{licznik.liczba} ({self._liczby.procent(licznik.procent)})",
                )
                for licznik in raport.podsumowanie.progi
            ),
            zakres_raportu=self._zakres(raport.sezony),
            zakres_rozgrzewki=self._zakres(raport.sezony_rozgrzewki),
            sezon_w_toku=raport.sezon_w_toku.nazwa if raport.sezon_w_toku else None,
            wykluczenia=tuple(
                WskaznikViewModel(ETYKIETY_WYKLUCZEN[powod], str(liczba))
                for powod, liczba in sorted(raport.wykluczenia.items(), key=lambda e: -e[1])
            ),
            parametry=self._parametry(raport.parametry),
        )

    def przygotuj_szczegoly(self, szczegoly: SzczegolyPrognozy) -> SzczegolyPrognozyViewModel:
        p = szczegoly.prognoza
        mecz, stan, prognoza, ocena = p.mecz, p.stan, p.prognoza, p.ocena
        n = self._liczby
        return SzczegolyPrognozyViewModel(
            id_mecz=mecz.id_mecz,
            tytul_modelu=szczegoly.model.nazwa,
            wersja_modelu=szczegoly.model.wersja,
            naglowek=f"{mecz.gospodarz.nazwa} — {mecz.gosc.nazwa}",
            kontekst=" · ".join(
                czesc
                for czesc in (
                    self._nazwa_ligi(mecz.liga),
                    mecz.sezon.nazwa,
                    f"kolejka {mecz.kolejka}" if mecz.kolejka is not None else None,
                    self._format.data(mecz.data),
                )
                if czesc
            ),
            zamiana=(
                f"W danych źródłowych strony są zamienione (zamiana = true). Faktycznym "
                f"gospodarzem jest {mecz.gospodarz.nazwa} (kolumna id_zespol_gosc) i to on "
                f"otrzymał HOME_ADVANTAGE. Wynik pozostał przypisany do kolumn drużyn."
                if mecz.zamiana
                else None
            ),
            okres=(
                "Mecz z zakresu raportu — wchodzi do metryk."
                if p.w_raporcie
                else "Mecz z okresu rozgrzewki — prognoza istnieje, ale nie wchodzi do metryk."
            ),
            wynik_prognozy=(
                WskaznikViewModel("Prognoza", self._prognoza(p)),
                WskaznikViewModel("Rzeczywisty wynik", self._wynik(p)),
                WskaznikViewModel("Typ modelu", prognoza.typ.value),
                WskaznikViewModel("Rzeczywisty typ", ocena.typ.value),
                WskaznikViewModel("Trafiony", "TAK" if ocena.trafiony else "NIE"),
                WskaznikViewModel("Ocena wyniku", ETYKIETY_KLAS_WYNIKU[ocena.klasa_wyniku]),
                WskaznikViewModel(
                    "Typ prognozy",
                    f"{ocena.typ_prezentowany.value} — "
                    f"{self._ocena_typu_prognozy(ocena.poprawny_typ_prognozy)}",
                ),
            ),
            trafiony=ocena.trafiony,
            klasa_oceny=self._klasa_css(ocena.klasa),
            klasa_oceny_wyniku=self._klasa_wyniku_css(ocena.klasa_wyniku),
            bledy=(
                WskaznikViewModel("score_error", n.liczba(ocena.blad_wyniku, 3)),
                WskaznikViewModel("margin_error", n.liczba(ocena.blad_roznicy, 3)),
                WskaznikViewModel("total_error", n.liczba(ocena.blad_sumy, 3)),
                WskaznikViewModel("Ocena", ETYKIETY_KLAS[ocena.klasa]),
            ),
            dane_wejsciowe=self._dane_wejsciowe(p),
            uwagi_ratingow=tuple(
                uwaga
                for uwaga in (
                    self._uwaga_ratingu(mecz.gospodarz, stan.gospodarz, p.parametry),
                    self._uwaga_ratingu(mecz.gosc, stan.gosc, p.parametry),
                )
                if uwaga
            ),
            ostatnie_ewma=tuple(
                f"mecz #{a.id_mecz}: {n.parametr(a.alfa)} × {a.suma_bramek} + "
                f"{n.parametr(1 - a.alfa)} × {a.stan_przed:.2f} = {a.stan_po:.2f}"
                for a in stan.ostatnie_aktualizacje_ewma
            ),
            kroki=self._kroki(p),
            znaczenie_aktualizacji=self._znaczenie(p),
            ratingi=(
                self._wiersz_ratingu(
                    mecz.gospodarz.nazwa,
                    stan.gospodarz.rating,
                    p.aktualizacja.poprawka,
                    p.aktualizacja.rating_gospodarza_po,
                ),
                self._wiersz_ratingu(
                    mecz.gosc.nazwa,
                    stan.gosc.rating,
                    -p.aktualizacja.poprawka,
                    p.aktualizacja.rating_goscia_po,
                ),
            ),
            historia=(
                self._historia(mecz.gospodarz, szczegoly.historia_gospodarza),
                self._historia(mecz.gosc, szczegoly.historia_goscia),
            ),
            parametry=json.dumps(
                {"model_version": p.wersja_modelu, **p.parametry.jako_slownik()},
                indent=4,
                ensure_ascii=False,
            ),
            definicje=tuple(DefinicjaPojeciaViewModel(a, b) for a, b in DEFINICJE_MODELU),
        )

    def _pozycja(self, p: PrognozaMeczu) -> PozycjaPrognozyViewModel:
        n = self._liczby
        mecz, prognoza, ocena = p.mecz, p.prognoza, p.ocena
        return PozycjaPrognozyViewModel(
            id_mecz=mecz.id_mecz,
            data=mecz.data.strftime("%d.%m.%Y"),
            sezon=mecz.sezon.nazwa,
            liga=f"{SKROTY_POZIOMOW[mecz.liga.poziom]} {mecz.liga.plec.value}",
            kolejka=str(mecz.kolejka) if mecz.kolejka is not None else BRAK,
            gospodarz=mecz.gospodarz.nazwa,
            gosc=mecz.gosc.nazwa,
            rating_gospodarza=n.liczba(p.stan.gospodarz.rating),
            rating_goscia=n.liczba(p.stan.gosc.rating),
            roznica_ratingow=n.ze_znakiem(prognoza.roznica_ratingow),
            prognoza=self._prognoza(p),
            wynik=self._wynik(p),
            prognoza_gospodarza=n.liczba(prognoza.bramki_gospodarza),
            bramki_gospodarza=str(mecz.bramki_gospodarza),
            blad_gospodarza=n.liczba(ocena.blad_gospodarza),
            prognoza_goscia=n.liczba(prognoza.bramki_goscia),
            bramki_goscia=str(mecz.bramki_goscia),
            blad_goscia=n.liczba(ocena.blad_goscia),
            prognoza_roznicy=n.ze_znakiem(prognoza.przewidywana_roznica),
            roznica=n.calkowita_ze_znakiem(ocena.roznica),
            blad_roznicy=n.liczba(ocena.blad_roznicy),
            prognoza_sumy=n.liczba(prognoza.przewidywana_suma),
            suma=str(ocena.suma),
            blad_sumy=n.liczba(ocena.blad_sumy),
            typ=prognoza.typ.value,
            typ_rzeczywisty=ocena.typ.value,
            trafiony=ocena.trafiony,
            trafiony_tekst="TAK" if ocena.trafiony else "NIE",
            blad_wyniku=n.liczba(ocena.blad_wyniku),
            ocena=ETYKIETY_KLAS[ocena.klasa],
            klasa_oceny=self._klasa_css(ocena.klasa),
            ocena_wyniku=ETYKIETY_KLAS_WYNIKU[ocena.klasa_wyniku],
            klasa_oceny_wyniku=self._klasa_wyniku_css(ocena.klasa_wyniku),
            poprawny_typ_prognozy=ocena.poprawny_typ_prognozy,
            typ_prognozy=ocena.typ_prezentowany.value,
            ocena_typu_prognozy=self._ocena_typu_prognozy(ocena.poprawny_typ_prognozy),
            opis_oceny_wyniku=(
                f"Różnica prognozy {n.calkowita_ze_znakiem(prognoza.roznica_prezentowana)}, "
                f"wyniku {n.calkowita_ze_znakiem(ocena.roznica)}"
            ),
        )

    def _prognoza(self, p: PrognozaMeczu) -> str:
        return (
            f"{p.prognoza.bramki_gospodarza_prezentowane}:{p.prognoza.bramki_goscia_prezentowane}"
        )

    def _wynik(self, p: PrognozaMeczu) -> str:
        return f"{p.mecz.bramki_gospodarza}:{p.mecz.bramki_goscia}"

    def _klasa_css(self, klasa: KlasaTrafnosci) -> str:
        return "ocena-" + klasa.value.replace("_", "-")

    def _klasa_wyniku_css(self, klasa: KlasaWyniku) -> str:
        return "wynik-" + klasa.value.replace("_", "-")

    def _ocena_typu_prognozy(self, poprawny: bool) -> str:
        return "Poprawny" if poprawny else "Nieprzewidziany"

    def _udzial(self, liczba: int, wszystkie: int) -> str:
        return f"{liczba} ({self._liczby.procent(liczba / wszystkie if wszystkie else None)})"

    def _wskazniki(self, podsumowanie: PodsumowaniePrognoz) -> tuple[WskaznikViewModel, ...]:
        n = self._liczby
        return (
            WskaznikViewModel("Liczba prognoz", str(podsumowanie.liczba)),
            WskaznikViewModel("Trafione 1X2", str(podsumowanie.trafione)),
            WskaznikViewModel("Trafność 1X2", n.procent(podsumowanie.trafnosc)),
            WskaznikViewModel("MAE gospodarza", n.liczba(podsumowanie.mae_gospodarza)),
            WskaznikViewModel("MAE gościa", n.liczba(podsumowanie.mae_goscia)),
            WskaznikViewModel("MAE różnicy", n.liczba(podsumowanie.mae_roznicy)),
            WskaznikViewModel("MAE sumy", n.liczba(podsumowanie.mae_sumy)),
            WskaznikViewModel("Średni score_error", n.liczba(podsumowanie.sredni_blad_wyniku)),
            WskaznikViewModel("Mediana score_error", n.liczba(podsumowanie.mediana_bledu_wyniku)),
            WskaznikViewModel(
                "Poprawny typ prognozy",
                self._udzial(podsumowanie.poprawne_typy_prognozy, podsumowanie.liczba),
            ),
            WskaznikViewModel(
                "Dokładny wynik", self._udzial(podsumowanie.dokladne_wyniki, podsumowanie.liczba)
            ),
            WskaznikViewModel(
                "Dokładna różnica bramek",
                self._udzial(podsumowanie.poprawne_roznice, podsumowanie.liczba),
            ),
            WskaznikViewModel(
                "Różnica ±1 lub lepiej",
                self._udzial(podsumowanie.roznice_do_1, podsumowanie.liczba),
            ),
        )

    def _zakres(self, sezony: Sequence[SezonPrognoz]) -> str:
        if not sezony:
            return BRAK
        kolejne = sorted(sezony, key=lambda sezon: sezon.klucz)
        if len(kolejne) == 1:
            return kolejne[0].nazwa
        return f"{kolejne[0].nazwa} – {kolejne[-1].nazwa} ({len(kolejne)} sezonów)"

    def _parametry(self, k: KonfiguracjaSilyDruzyn) -> tuple[WskaznikViewModel, ...]:
        return tuple(
            WskaznikViewModel(symbol, self._liczby.parametr(getattr(k, pole)), opis)
            for pole, symbol, opis in SYMBOLE_PARAMETROW
        )

    def _dane_wejsciowe(self, p: PrognozaMeczu) -> tuple[WskaznikViewModel, ...]:
        n, k = self._liczby, p.parametry
        return (
            WskaznikViewModel(
                "Rating gospodarza przed meczem",
                n.liczba(p.stan.gospodarz.rating),
                p.mecz.gospodarz.nazwa,
            ),
            WskaznikViewModel(
                "Rating gościa przed meczem", n.liczba(p.stan.gosc.rating), p.mecz.gosc.nazwa
            ),
            WskaznikViewModel("Home advantage", n.parametr(k.przewaga_wlasnego_parkietu)),
            WskaznikViewModel("Różnica ratingów", n.ze_znakiem(p.prognoza.roznica_ratingow)),
            WskaznikViewModel(
                "Średnia suma bramek ligi przed meczem", n.liczba(p.stan.oczekiwana_suma_ligi)
            ),
            *(
                WskaznikViewModel(symbol, n.parametr(getattr(k, pole)))
                for pole, symbol, _ in SYMBOLE_PARAMETROW
                if symbol
                in {
                    "MARGIN_INTERCEPT",
                    "MARGIN_SLOPE",
                    "K_FACTOR",
                    "MARGIN_SCALE",
                    "SEASON_RETENTION",
                    "EWMA_ALPHA",
                    "DRAW_MARGIN_THRESHOLD",
                }
            ),
        )

    def _uwaga_ratingu(
        self, druzyna: UczestnikPrognozy, rating: RatingPrzedMeczem, k: KonfiguracjaSilyDruzyn
    ) -> str | None:
        n = self._liczby
        if rating.nowa_druzyna:
            return (
                f"{druzyna.nazwa}: pierwszy mecz w danych modelu — rating początkowy "
                f"INITIAL_RATING = {n.parametr(k.rating_poczatkowy)}."
            )
        regresja = rating.regresja
        if regresja is None:
            return None
        if regresja.liczba_regresji == 1:
            return (
                f"{druzyna.nazwa}: pierwszy mecz nowego sezonu. Rating z końca sezonu "
                f"{regresja.sezon_poprzedni}: {regresja.rating_konca_sezonu:.2f} → "
                f"{n.parametr(k.rating_poczatkowy)} + {n.parametr(k.zachowanie_miedzy_sezonami)}"
                f" × ({regresja.rating_konca_sezonu:.2f} − {n.parametr(k.rating_poczatkowy)}) = "
                f"{regresja.rating_po_regresji:.2f}."
            )
        return (
            f"{druzyna.nazwa}: pierwszy mecz po przerwie od sezonu {regresja.sezon_poprzedni}. "
            f"Regresję do średniej zastosowano {regresja.liczba_regresji} razy (raz na każde "
            f"przejście sezonu): {regresja.rating_konca_sezonu:.2f} → "
            f"{regresja.rating_po_regresji:.2f}."
        )

    def _kroki(self, p: PrognozaMeczu) -> tuple[KrokObliczeniaViewModel, ...]:
        n, k = self._liczby, p.parametry
        mecz, stan, prognoza, ocena, akt = p.mecz, p.stan, p.prognoza, p.ocena, p.aktualizacja
        rh, ra = stan.gospodarz.rating, stan.gosc.rating
        d, m, t = (
            prognoza.roznica_ratingow,
            prognoza.przewidywana_roznica,
            prognoza.przewidywana_suma,
        )
        h, a = prognoza.bramki_gospodarza, prognoza.bramki_goscia
        ostatnia = stan.ostatnie_aktualizacje_ewma[-1] if stan.ostatnie_aktualizacje_ewma else None
        return (
            KrokObliczeniaViewModel(
                "krok-1",
                "Krok 1 — różnica ratingów",
                "Różnica sił obu drużyn na wspólnej skali ratingowej, powiększona o przewagę "
                "własnego parkietu faktycznego gospodarza.",
                "rating_diff =\n    rating_home\n    − rating_away\n    + HOME_ADVANTAGE",
                f"rating_diff =\n    {rh:.2f}\n    − {ra:.2f}\n    + "
                f"{n.parametr(k.przewaga_wlasnego_parkietu)}",
                f"rating_diff = {n.ze_znakiem(d)}",
                self._opis_roznicy_ratingow(p),
            ),
            KrokObliczeniaViewModel(
                "krok-2",
                "Krok 2 — przewidywana różnica bramek",
                "Liniowe przeliczenie różnicy ratingów na oczekiwaną różnicę bramek z perspektywy "
                "faktycznego gospodarza.",
                "predicted_margin =\n    MARGIN_INTERCEPT\n    + MARGIN_SLOPE × rating_diff",
                f"predicted_margin =\n    {n.parametr(k.wyraz_wolny_roznicy)}\n    + "
                f"{n.parametr(k.nachylenie_roznicy)} × {n.skladnik(d)}",
                f"predicted_margin = {n.ze_znakiem(m)}",
                self._opis_przewidywanej_roznicy(p),
            ),
            KrokObliczeniaViewModel(
                "krok-3",
                "Krok 3 — przewidywana suma bramek",
                "Wykładniczo ważona średnia (EWMA) sum bramek ligi. Dla tego meczu użyto wartości "
                "wyliczonej wyłącznie z meczów rozegranych wcześniej.",
                "EWMA_new =\n    alpha × previous_match_total\n    + (1 − alpha) × EWMA_old",
                (
                    f"poprzedni stan: {ostatnia.stan_przed:.2f}\nostatni mecz:   "
                    f"{ostatnia.suma_bramek}\nalpha:          {n.parametr(ostatnia.alfa)}\n\n"
                    f"nowy stan =\n    {n.parametr(ostatnia.alfa)} × {ostatnia.suma_bramek}\n"
                    f"    + {n.parametr(1 - ostatnia.alfa)} × {ostatnia.stan_przed:.2f}\n"
                    f"    = {ostatnia.stan_po:.2f}"
                    if ostatnia
                    else "Brak wcześniejszych meczów ligi w modelu:\n"
                    f"EWMA = INITIAL_EXPECTED_TOTAL = {n.parametr(k.poczatkowa_suma_bramek)}"
                ),
                f"league_expected_total_before_match = {t:.2f}",
                f"Wartość pochodzi tylko z meczów rozgrywek {self._nazwa_ligi(mecz.liga)} "
                "rozegranych przed tym spotkaniem. Każda liga (poziom i płeć) ma osobną średnią.",
            ),
            KrokObliczeniaViewModel(
                "krok-4",
                "Krok 4 — przewidywane bramki",
                "Suma i różnica jednoznacznie wyznaczają bramki obu drużyn.",
                "pred_home = (predicted_total + predicted_margin) / 2\n"
                "pred_away = (predicted_total − predicted_margin) / 2",
                f"pred_home = ({t:.2f} + {n.skladnik(m)}) / 2 = {h:.3f}\n"
                f"pred_away = ({t:.2f} − {n.skladnik(m)}) / 2 = {a:.3f}",
                f"wartość modelowa:   {h:.2f} : {a:.2f}\n"
                f"wynik prezentowany: {self._prognoza(p).replace(':', ' : ')}",
                "Zaokrąglenie (połówki w górę) służy tylko prezentacji. Błędy i metryki są "
                "liczone na wartościach dokładnych, dlatego zaokrąglony wynik może wyglądać na "
                "remis przy typie H lub A.",
            ),
            KrokObliczeniaViewModel(
                "krok-5",
                "Krok 5 — typ 1X2",
                "Prosta reguła punktowa oparta na przewidywanej różnicy bramek. Model nie "
                "podaje prawdopodobieństw 1X2.",
                "if predicted_margin > DRAW_MARGIN_THRESHOLD:\n    H\n"
                "elif predicted_margin < −DRAW_MARGIN_THRESHOLD:\n    A\nelse:\n    X",
                f"predicted_margin = {n.ze_znakiem(m)}\nthreshold = "
                f"{n.parametr(k.prog_remisu)}\n\n{self._porownanie_progu(m, k.prog_remisu)}",
                f"typ: {prognoza.typ.value}",
                self._opis_typu(p),
            ),
            KrokObliczeniaViewModel(
                "krok-6",
                "Krok 6 — rzeczywisty mecz",
                "Wynik po 60 minutach z kolumn wynik_gosp_full i wynik_gosc_full, przypisany "
                "do faktycznego gospodarza i gościa. Dogrywki i serie karnych nie wchodzą do "
                "wyniku.",
                "actual_margin = real_home − real_away\nactual_total  = real_home + real_away",
                f"actual_margin = {mecz.bramki_gospodarza} − {mecz.bramki_goscia} = "
                f"{n.calkowita_ze_znakiem(ocena.roznica)}\n"
                f"actual_total  = {mecz.bramki_gospodarza} + {mecz.bramki_goscia} = {ocena.suma}",
                f"rzeczywisty wynik: {self._wynik(p)} (typ {ocena.typ.value})",
                "Wynik jest odczytywany dopiero po zapisaniu prognozy i nie wpływa na nią.",
            ),
            KrokObliczeniaViewModel(
                "krok-7",
                "Krok 7 — błędy prognozy",
                "Bezwzględne błędy liczone na wartościach zmiennoprzecinkowych.",
                "error_home   = |pred_home − real_home|\n"
                "error_away   = |pred_away − real_away|\n"
                "score_error  = error_home + error_away\n"
                "margin_error = |predicted_margin − actual_margin|\n"
                "total_error  = |predicted_total − actual_total|",
                f"error_home   = |{h:.3f} − {mecz.bramki_gospodarza}| = "
                f"{ocena.blad_gospodarza:.3f}\n"
                f"error_away   = |{a:.3f} − {mecz.bramki_goscia}| = {ocena.blad_goscia:.3f}\n"
                f"score_error  = {ocena.blad_gospodarza:.3f} + {ocena.blad_goscia:.3f} = "
                f"{ocena.blad_wyniku:.3f}\n"
                f"margin_error = |{m:.2f} − {n.skladnik(ocena.roznica, 0)}| = "
                f"{ocena.blad_roznicy:.2f}\n"
                f"total_error  = |{t:.2f} − {ocena.suma}| = {ocena.blad_sumy:.2f}\n\n"
                f"wynik prezentowany {self._prognoza(p)}: różnica "
                f"{n.calkowita_ze_znakiem(prognoza.roznica_prezentowana)}\n"
                f"wynik rzeczywisty  {self._wynik(p)}: różnica "
                f"{n.calkowita_ze_znakiem(ocena.roznica)}\n"
                f"|{prognoza.roznica_prezentowana} − {n.skladnik(ocena.roznica, 0)}| = "
                f"{ocena.blad_roznicy_prezentowanej}",
                f"score_error = {ocena.blad_wyniku:.3f} → {ETYKIETY_KLAS[ocena.klasa]}\n"
                f"ocena wyniku → {ETYKIETY_KLAS_WYNIKU[ocena.klasa_wyniku]}\n"
                f"typ prognozy: {ocena.typ_prezentowany.value} (z wyniku {self._prognoza(p)}), "
                f"wynik {ocena.typ.value} → "
                f"{self._ocena_typu_prognozy(ocena.poprawny_typ_prognozy)}",
                f"Typ {'trafiony' if ocena.trafiony else 'nietrafiony'}: prognoza "
                f"{prognoza.typ.value}, wynik {ocena.typ.value}. Klasa trafności jest wyłącznie "
                "warstwą prezentacji.",
            ),
            KrokObliczeniaViewModel(
                "krok-8",
                "Krok 8 — aktualizacja ratingów",
                "Po ocenie prognozy ratingi są przesuwane o tę samą wartość w przeciwnych "
                "kierunkach. Funkcja tanh ogranicza zmianę do ±K_FACTOR, więc wynik typu 45:20 "
                "nie rozwala skali ratingowej.",
                "margin_residual = actual_margin − predicted_margin\n"
                "rating_adjustment = K_FACTOR × tanh(margin_residual / MARGIN_SCALE)\n"
                "rating_home_after = rating_home_before + rating_adjustment\n"
                "rating_away_after = rating_away_before − rating_adjustment",
                f"margin_residual = {n.calkowita_ze_znakiem(ocena.roznica)} − {n.skladnik(m)} = "
                f"{n.ze_znakiem(akt.reszta_roznicy)}\n"
                f"rating_adjustment = {n.parametr(k.wspolczynnik_k)} × tanh("
                f"{n.skladnik(akt.reszta_roznicy)} / {n.parametr(k.skala_roznicy)})\n"
                f"                  = {n.parametr(k.wspolczynnik_k)} × "
                f"{n.skladnik(math.tanh(akt.reszta_roznicy / k.skala_roznicy), 4)}\n"
                f"rating_home_after = {rh:.2f} + {n.skladnik(akt.poprawka)} = "
                f"{akt.rating_gospodarza_po:.2f}\n"
                f"rating_away_after = {ra:.2f} − {n.skladnik(akt.poprawka)} = "
                f"{akt.rating_goscia_po:.2f}",
                f"rating_adjustment = {n.ze_znakiem(akt.poprawka)}",
                f"{self._opis_poprawki(p)} Średnia EWMA ligi po meczu: "
                f"{n.parametr(k.alfa_ewma)} × {ocena.suma} + {n.parametr(1 - k.alfa_ewma)} × "
                f"{t:.2f} = {akt.oczekiwana_suma_po:.2f}.",
            ),
        )

    def _opis_roznicy_ratingow(self, p: PrognozaMeczu) -> str:
        d = p.prognoza.roznica_ratingow
        if d > 0:
            return (
                f"Po uwzględnieniu własnego parkietu {p.mecz.gospodarz.nazwa} ma przewagę "
                f"{d:.2f} pkt ratingu."
            )
        if d < 0:
            return (
                f"Mimo przewagi własnego parkietu {p.mecz.gosc.nazwa} jest silniejszy o "
                f"{abs(d):.2f} pkt ratingu."
            )
        return "Po uwzględnieniu własnego parkietu siły drużyn są równe."

    def _opis_przewidywanej_roznicy(self, p: PrognozaMeczu) -> str:
        m = p.prognoza.przewidywana_roznica
        if m > 0:
            return (
                f"{self._liczby.ze_znakiem(m)} oznacza, że model oczekiwał zwycięstwa gospodarza "
                f"średnio o około {m:.2f} bramki."
            )
        if m < 0:
            return (
                f"{self._liczby.ze_znakiem(m)} oznacza, że model oczekiwał zwycięstwa gościa "
                f"średnio o około {abs(m):.2f} bramki."
            )
        return "Model oczekiwał wyrównanego meczu."

    def _porownanie_progu(self, m: float, prog: float) -> str:
        n = self._liczby
        if m > prog:
            return f"{n.ze_znakiem(m)} > {n.ze_znakiem(prog)}"
        if m < -prog:
            return f"{n.ze_znakiem(m)} < {n.ze_znakiem(-prog)}"
        return f"{n.ze_znakiem(-prog)} ≤ {n.ze_znakiem(m)} ≤ {n.ze_znakiem(prog)}"

    def _opis_typu(self, p: PrognozaMeczu) -> str:
        if p.prognoza.typ is Typ1X2.GOSPODARZ:
            return f"H — model wskazał zwycięstwo gospodarza ({p.mecz.gospodarz.nazwa})."
        if p.prognoza.typ is Typ1X2.GOSC:
            return f"A — model wskazał zwycięstwo gościa ({p.mecz.gosc.nazwa})."
        return "X — przewidywana różnica mieści się w progu remisu."

    def _znaczenie(self, p: PrognozaMeczu) -> tuple[str, ...]:
        m, r = p.prognoza.przewidywana_roznica, p.ocena.roznica
        reszta, poprawka = p.aktualizacja.reszta_roznicy, p.aktualizacja.poprawka
        if m > 0:
            oczekiwanie = f"zwycięstwa gospodarza różnicą około {m:.2f} bramki"
        elif m < 0:
            oczekiwanie = f"zwycięstwa gościa różnicą około {abs(m):.2f} bramki"
        else:
            oczekiwanie = "remisu"
        if r > 0:
            rzeczywistosc = f"gospodarze wygrali różnicą {self._bramki(r)}"
        elif r < 0:
            rzeczywistosc = f"goście wygrali różnicą {self._bramki(abs(r))}"
        else:
            rzeczywistosc = "padł remis"
        if reszta > 0:
            porownanie = f"wynik gospodarza lepszy od oczekiwania o około {reszta:.2f} bramki"
        elif reszta < 0:
            porownanie = f"wynik gospodarza gorszy od oczekiwania o około {abs(reszta):.2f} bramki"
        else:
            porownanie = "wynik dokładnie zgodny z oczekiwaniem"
        if poprawka > 0:
            skutek = "Dlatego rating gospodarza wzrósł, a rating gościa spadł."
        elif poprawka < 0:
            skutek = "Dlatego rating gospodarza spadł, a rating gościa wzrósł."
        else:
            skutek = "Dlatego ratingi się nie zmieniły."
        return (
            f"Model spodziewał się {oczekiwanie}.",
            f"Rzeczywiście {rzeczywistosc}.",
            f"Oznacza to {porownanie}.",
            skutek,
        )

    def _bramki(self, liczba: int) -> str:
        return "1 bramki" if liczba == 1 else f"{liczba} bramek"

    def _opis_poprawki(self, p: PrognozaMeczu) -> str:
        poprawka = abs(p.aktualizacja.poprawka)
        if p.aktualizacja.poprawka > 0:
            return (
                f"Wynik gospodarza był lepszy od oczekiwania, więc {p.mecz.gospodarz.nazwa} "
                f"zyskuje {poprawka:.2f} pkt, a {p.mecz.gosc.nazwa} traci tyle samo."
            )
        if p.aktualizacja.poprawka < 0:
            return (
                f"Wynik gospodarza był gorszy od oczekiwania, więc {p.mecz.gospodarz.nazwa} "
                f"traci {poprawka:.2f} pkt, a {p.mecz.gosc.nazwa} zyskuje tyle samo."
            )
        return "Wynik był zgodny z oczekiwaniem, więc ratingi się nie zmieniły."

    def _wiersz_ratingu(
        self, druzyna: str, przed: float, zmiana: float, po: float
    ) -> WierszRatinguViewModel:
        return WierszRatinguViewModel(
            druzyna,
            f"{przed:.2f}",
            self._liczby.ze_znakiem(zmiana),
            f"{po:.2f}",
            self._klasa_zmiany(zmiana),
        )

    def _klasa_zmiany(self, zmiana: float) -> str:
        if zmiana > 0:
            return "zmiana-plus"
        if zmiana < 0:
            return "zmiana-minus"
        return ""

    def _historia(
        self, druzyna: UczestnikPrognozy, prognozy: Sequence[PrognozaMeczu]
    ) -> HistoriaDruzynyViewModel:
        wiersze = []
        for p in prognozy:
            u_siebie = p.mecz.gospodarz.id_zespol == druzyna.id_zespol
            przed = p.stan.gospodarz.rating if u_siebie else p.stan.gosc.rating
            po = (
                p.aktualizacja.rating_gospodarza_po if u_siebie else p.aktualizacja.rating_goscia_po
            )
            wlasne = p.mecz.bramki_gospodarza if u_siebie else p.mecz.bramki_goscia
            rywala = p.mecz.bramki_goscia if u_siebie else p.mecz.bramki_gospodarza
            wiersze.append(
                WierszHistoriiViewModel(
                    id_mecz=p.mecz.id_mecz,
                    data=p.mecz.data.strftime("%d.%m.%Y"),
                    sezon=p.mecz.sezon.nazwa,
                    rywal=(p.mecz.gosc if u_siebie else p.mecz.gospodarz).nazwa,
                    miejsce="dom" if u_siebie else "wyjazd",
                    wynik=f"{wlasne}:{rywala}",
                    przed=f"{przed:.2f}",
                    zmiana=self._liczby.ze_znakiem(po - przed),
                    po=f"{po:.2f}",
                    klasa_zmiany=self._klasa_zmiany(po - przed),
                )
            )
        return HistoriaDruzynyViewModel(druzyna.nazwa, tuple(wiersze))
