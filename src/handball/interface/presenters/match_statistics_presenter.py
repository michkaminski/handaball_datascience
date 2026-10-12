from __future__ import annotations

from handball.domain.match_statistics import (
    FormaDruzyny,
    MeczFormy,
    RezultatFormy,
    StatystykiDruzynyMeczu,
    StatystykiMeczu,
    StrzelecMeczu,
)
from handball.interface.presenters.match_presenter import BRAK, MeczFormat
from handball.interface.view_models.match_statistics import (
    FormaDruzynyViewModel,
    MeczFormyViewModel,
    StatystykiMeczuViewModel,
    StrzelecMeczuViewModel,
    WierszPorownaniaViewModel,
)

KLASY_REZULTATU = {
    RezultatFormy.WYGRANA: "win",
    RezultatFormy.REMIS: "draw",
    RezultatFormy.PORAZKA: "loss",
}


class StatystykiMeczuPresenter:
    LIMIT_FORMY = 5

    def __init__(self, formatowanie: MeczFormat) -> None:
        self._format = formatowanie

    def przygotuj(self, statystyki: StatystykiMeczu) -> StatystykiMeczuViewModel:
        a, b = statystyki.gospodarz, statystyki.gosc
        return StatystykiMeczuViewModel(
            rozegrany=statystyki.rozegrany,
            wnioski=list(statystyki.wnioski),
            porownanie=self._porownanie(a, b) if statystyki.rozegrany else [],
            strzelcy_gospodarz=[self._strzelec(s) for s in a.strzelcy],
            strzelcy_gosc=[self._strzelec(s) for s in b.strzelcy],
            forma_gospodarz=self._forma(statystyki.forma_gospodarza),
            forma_gosc=self._forma(statystyki.forma_goscia),
            limit_formy=self.LIMIT_FORMY,
        )

    def _porownanie(
        self, a: StatystykiDruzynyMeczu, b: StatystykiDruzynyMeczu
    ) -> list[WierszPorownaniaViewModel]:
        wiersze = [
            self._liczby("Bramki", a.bramki, b.bramki, True),
            self._liczby("Do przerwy", a.bramki_do_przerwy, b.bramki_do_przerwy, True),
            self._liczby("Druga połowa", a.bramki_druga_polowa, b.bramki_druga_polowa, True),
            self._karne(a, b),
            self._skutecznosc(a, b),
            self._timeouty(a, b),
            self._liczby("Kary 2 min", a.dwie_minuty, b.dwie_minuty, False),
            self._liczby("Upomnienia", a.upomnienia, b.upomnienia, False),
            self._liczby("Dyskwalifikacje", a.dyskwalifikacje, b.dyskwalifikacje, False),
        ]
        return [w for w in wiersze if w is not None]

    def _liczby(
        self, etykieta: str, a: int | None, b: int | None, wiecej_lepiej: bool
    ) -> WierszPorownaniaViewModel | None:
        if a is None and b is None:
            return None
        przewaga = None
        if wiecej_lepiej and a is not None and b is not None and a != b:
            przewaga = "home" if a > b else "away"
        return WierszPorownaniaViewModel(
            etykieta, self._format.tekst(a), self._format.tekst(b), self._udzial(a, b), przewaga
        )

    def _karne(
        self, a: StatystykiDruzynyMeczu, b: StatystykiDruzynyMeczu
    ) -> WierszPorownaniaViewModel | None:
        if a.karne_wykonane is None and b.karne_wykonane is None:
            return None
        return WierszPorownaniaViewModel(
            "Rzuty karne",
            self._format.ulamek(a.karne_trafione, a.karne_wykonane),
            self._format.ulamek(b.karne_trafione, b.karne_wykonane),
            self._udzial(a.karne_trafione, b.karne_trafione),
        )

    def _skutecznosc(
        self, a: StatystykiDruzynyMeczu, b: StatystykiDruzynyMeczu
    ) -> WierszPorownaniaViewModel | None:
        x, y = a.skutecznosc_karnych, b.skutecznosc_karnych
        if x is None and y is None:
            return None
        przewaga = None
        if x is not None and y is not None and x != y:
            przewaga = "home" if x > y else "away"
        return WierszPorownaniaViewModel(
            "Skuteczność karnych", self._procent(x), self._procent(y), None, przewaga
        )

    def _timeouty(
        self, a: StatystykiDruzynyMeczu, b: StatystykiDruzynyMeczu
    ) -> WierszPorownaniaViewModel | None:
        if a.timeouty is None and b.timeouty is None:
            return None
        return WierszPorownaniaViewModel(
            "Czasy drużyny", self._lista_czasow(a.timeouty), self._lista_czasow(b.timeouty)
        )

    def _lista_czasow(self, czasy: tuple[str, ...] | None) -> str:
        if not czasy:
            return "0"
        return f"{len(czasy)} ({', '.join(self._minuta(c) for c in czasy)})"

    def _minuta(self, czas: str) -> str:
        czas = czas.strip()
        return czas[3:] if len(czas) == 8 and czas.startswith("00:") else czas

    def _procent(self, wartosc: float | None) -> str:
        return BRAK if wartosc is None else f"{wartosc:.0%}"

    def _udzial(self, a: int | None, b: int | None) -> int | None:
        if a is None or b is None or a + b <= 0:
            return None
        return round(100 * a / (a + b))

    def _strzelec(self, strzelec: StrzelecMeczu) -> StrzelecMeczuViewModel:
        karne = f"{strzelec.karne_bramki} z karnych" if strzelec.karne_bramki else ""
        return StrzelecMeczuViewModel(strzelec.zawodnik, str(strzelec.bramki), karne)

    def _forma(self, forma: FormaDruzyny | None) -> FormaDruzynyViewModel | None:
        if forma is None:
            return None
        mecze = forma.ostatnie(self.LIMIT_FORMY)
        bilans = forma.bilans(self.LIMIT_FORMY)
        return FormaDruzynyViewModel(
            mecze=[self._mecz_formy(m, m.id_mecz == forma.id_analizowany) for m in mecze],
            bilans=(
                f"{bilans[RezultatFormy.WYGRANA]}W {bilans[RezultatFormy.REMIS]}R "
                f"{bilans[RezultatFormy.PORAZKA]}P"
            ),
            bramki=(
                f"{sum(m.bramki_zdobyte for m in mecze)}:{sum(m.bramki_stracone for m in mecze)}"
            ),
        )

    def _mecz_formy(self, mecz: MeczFormy, analizowany: bool) -> MeczFormyViewModel:
        return MeczFormyViewModel(
            id_mecz=mecz.id_mecz,
            rezultat=mecz.rezultat.value,
            klasa=KLASY_REZULTATU[mecz.rezultat],
            wynik=f"{mecz.bramki_zdobyte}:{mecz.bramki_stracone}",
            dopisek=self._dopisek(mecz),
            rywal=self._format.tekst(mecz.rywal),
            data=mecz.data.strftime("%d.%m") if mecz.data else BRAK,
            miejsce="dom" if mecz.u_siebie else "wyjazd",
            rozgrywki=self._format.tekst(mecz.rozgrywki),
            analizowany=analizowany,
        )

    def _dopisek(self, mecz: MeczFormy) -> str:
        if mecz.rozstrzygniecie is None:
            return ""
        if mecz.dogrywka and mecz.dogrywka_zdobyte != mecz.dogrywka_stracone:
            return f"po dogrywce {mecz.dogrywka_zdobyte}:{mecz.dogrywka_stracone}"
        return f"k. {mecz.seria_zdobyte}:{mecz.seria_stracone}"
