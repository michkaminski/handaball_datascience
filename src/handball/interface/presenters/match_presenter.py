from datetime import datetime

from handball.domain.match_rules import MeczPolicy, StatusMeczu
from handball.domain.matches import DaneMeczu, StronaMeczow, SzczegolyMeczu, ZawodnikMeczu
from handball.interface.view_models.matches import (
    PozycjaListyMeczowViewModel,
    StronaMeczowViewModel,
    SzczegolyMeczuViewModel,
    ZawodnikMeczuViewModel,
)

BRAK = "—"


class MeczFormat:
    def tekst(self, wartosc: object) -> str:
        if wartosc is None or wartosc == "":
            return BRAK
        return str(wartosc)

    def flaga(self, wartosc: bool | None) -> str:
        if wartosc is None:
            return BRAK
        return "Tak" if wartosc else "Nie"

    def data(self, wartosc: datetime | None) -> str:
        if wartosc is None:
            return BRAK
        return wartosc.strftime("%d.%m.%Y %H:%M")

    def ulamek(self, licznik: int | None, mianownik: int | None) -> str:
        if licznik is None and mianownik is None:
            return BRAK
        licznik = licznik if licznik is not None else 0
        mianownik = mianownik if mianownik is not None else 0
        return f"{licznik}/{mianownik}"

    def dopisek(self, mecz: DaneMeczu, reguly: MeczPolicy) -> str | None:
        if reguly.ma_serie_karnych(mecz):
            a, b = reguly.para(mecz, mecz.dogrywka_karne_gosp, mecz.dogrywka_karne_gosc)
            return f"k {a if a is not None else 0}-{b if b is not None else 0}"
        return "dogrywka" if reguly.ma_dogrywke(mecz) else None


class SkladMeczuPresenter:
    def __init__(self, formatowanie: MeczFormat, reguly: MeczPolicy) -> None:
        self._format = formatowanie
        self._reguly = reguly

    def przygotuj(
        self, sklad: list[ZawodnikMeczu], kolory: dict[str, int], wyroznij: bool = True
    ) -> list[ZawodnikMeczuViewModel]:
        maksimum = self._reguly.najwiecej_bramek(sklad) if wyroznij else None
        return [
            ZawodnikMeczuViewModel(
                nr_koszulki=self._format.tekst(z.nr_koszulki),
                zawodnik=self._format.tekst(z.zawodnik),
                pozycja=self._format.tekst(z.pozycja),
                bramki=self._format.tekst(z.bramki),
                dwie_minuty=self._format.tekst(z.dwie_minuty),
                upomnienie=self._format.flaga(z.upomnienie),
                dyskwalifikacja=self._format.flaga(z.dyskwalifikacja),
                kd=self._format.tekst(z.kd),
                wyjscie=self._format.flaga(z.wyjscie),
                karne=self._format.ulamek(z.karne_bramki, z.karne_liczba),
                karne_seria=self._format.ulamek(z.karne_bramki_seria, z.karne_liczba_seria),
                kolor_pozycji=kolory.get((z.pozycja or "").strip().casefold()),
                najlepszy_strzelec=maksimum is not None and maksimum > 0 and z.bramki == maksimum,
            )
            for z in sorted(sklad, key=self._kolejnosc)
        ]

    def _kolejnosc(self, zawodnik: ZawodnikMeczu) -> tuple[bool, str, bool, int, str]:
        pozycja = (zawodnik.pozycja or "").strip().casefold()
        return (
            pozycja in {"", "—", "-"},
            pozycja,
            zawodnik.nr_koszulki is None,
            zawodnik.nr_koszulki or 0,
            (zawodnik.zawodnik or "").casefold(),
        )


class MeczPresenter:
    def __init__(
        self, reguly: MeczPolicy, formatowanie: MeczFormat, sklady: SkladMeczuPresenter
    ) -> None:
        self._reguly = reguly
        self._format = formatowanie
        self._sklady = sklady

    def przygotuj_szczegoly(self, szczegoly: SzczegolyMeczu) -> SzczegolyMeczuViewModel:
        mecz = szczegoly.mecz
        nazwa_sezon = szczegoly.nazwa_sezon
        nazwa_rozgrywki = szczegoly.nazwa_rozgrywki
        nazwa_gospodarz = szczegoly.nazwa_gospodarz
        nazwa_gosc = szczegoly.nazwa_gosc
        nazwa_hala = szczegoly.nazwa_hala
        miasto_hala = szczegoly.miasto_hala
        nazwa_runda = szczegoly.nazwa_runda
        nazwa_kolejka = szczegoly.nazwa_kolejka
        nr_kolejka = szczegoly.nr_kolejka
        nazwa_zespol_wycofany = szczegoly.nazwa_zespol_wycofany
        nazwa_zespol_walkower = szczegoly.nazwa_zespol_walkower
        gospodarz_nazwa, gosc_nazwa = self._reguly.para(mecz, nazwa_gospodarz, nazwa_gosc)
        sklad_gospodarz, sklad_gosc = self._reguly.para(
            mecz, szczegoly.sklad_gospodarz, szczegoly.sklad_gosc
        )
        pozycje = sorted(
            {
                (z.pozycja or "").strip().casefold()
                for z in sklad_gospodarz + sklad_gosc + szczegoly.sklad_inne
            }
            - {"", "—", "-"}
        )
        kolory = {pozycja: indeks * 137 % 360 for indeks, pozycja in enumerate(pozycje)}
        wynik_gosp, wynik_gosc = self._reguly.para(mecz, mecz.wynik_gosp_full, mecz.wynik_gosc_full)
        pol_gosp, pol_gosc = self._reguly.para(mecz, mecz.wynik_gosp_pol, mecz.wynik_gosc_pol)
        wynik_naglowek = f"{self._format.tekst(wynik_gosp)} : {self._format.tekst(wynik_gosc)}"
        wynik_do_przerwy = (
            f"do przerwy {self._format.tekst(pol_gosp)} : {self._format.tekst(pol_gosc)}"
            if pol_gosp is not None or pol_gosc is not None
            else ""
        )
        dopisek_wyniku = self._format.dopisek(mecz, self._reguly) or ""

        status = {
            StatusMeczu.WYCOFANY: "Wycofany",
            StatusMeczu.WALKOWER: "Walkower",
            StatusMeczu.ROZEGRANY: "Rozegrany",
            StatusMeczu.ZAPLANOWANY: "Zaplanowany",
        }[self._reguly.status(mecz)]

        kolejka_etykieta = nazwa_kolejka or (f"Kolejka {nr_kolejka}" if nr_kolejka else BRAK)

        dane_podstawowe = [
            ("Sezon", self._format.tekst(nazwa_sezon)),
            ("Rozgrywki", self._format.tekst(nazwa_rozgrywki)),
            ("Kod rozgrywek", self._format.tekst(mecz.rozgrywki_code)),
            ("Runda", self._format.tekst(nazwa_runda)),
            ("Kolejka", kolejka_etykieta),
            ("Kolejność w kolejce (lp)", self._format.tekst(mecz.lp)),
            ("Data faktyczna", self._format.data(mecz.data_faktyczna)),
            ("Data propozycji", self._format.data(mecz.data_propozycji)),
            ("Data ostatniej zmiany", self._format.data(mecz.data_ostatniej_zmiany)),
            ("Gospodarz", self._format.tekst(gospodarz_nazwa)),
            ("Gość", self._format.tekst(gosc_nazwa)),
            ("Hala", self._format.tekst(nazwa_hala)),
            ("Miasto hali", self._format.tekst(miasto_hala)),
            ("Status", status),
            ("Zwycięzca (kod)", self._format.tekst(mecz.zwyciezca)),
            ("Remis", self._format.flaga(mecz.czy_remis)),
            ("Widzowie", self._format.tekst(mecz.widzowie)),
            ("Transmisja", self._format.tekst(mecz.transmisja)),
            ("Godzina transmisji", self._format.tekst(mecz.transmisja_godzina)),
            ("Bilety", self._format.tekst(mecz.bilety_url)),
            ("Zamiana stron", self._format.flaga(mecz.zamiana)),
            ("Wycofany", self._format.flaga(mecz.wycofany)),
            ("Typ wycofania", self._format.tekst(mecz.wycofany_typ)),
            ("Zespół wycofany", self._format.tekst(nazwa_zespol_wycofany)),
            ("Zespół — walkower", self._format.tekst(nazwa_zespol_walkower)),
            ("Protokół", self._format.tekst(mecz.protokol)),
            ("Protokół zatwierdzony", self._format.flaga(mecz.protokol_zatwierdzony)),
            ("Załącznik protokołu", self._format.tekst(mecz.protokol_zalacznik_nazwa)),
            ("Typ załącznika", self._format.tekst(mecz.protokol_zalacznik_typ)),
            ("Komentarz", self._format.tekst(mecz.komentarz)),
            ("Alias — gospodarz", self._format.tekst(mecz.alias_gosp)),
            ("Alias — gość", self._format.tekst(mecz.alias_gosc)),
            ("ID pary play-off", self._format.tekst(mecz.po_para_id)),
            ("ID pary play-off — gospodarz", self._format.tekst(mecz.po_para_id_gosp)),
            ("ID pary play-off — gość", self._format.tekst(mecz.po_para_id_gosc)),
        ]

        statystyki = [
            self._stat(mecz, "Wynik (pełny)", mecz.wynik_gosp_full, mecz.wynik_gosc_full),
            self._stat(mecz, "Do przerwy", mecz.wynik_gosp_pol, mecz.wynik_gosc_pol),
            self._stat(
                mecz,
                "Wynik tymczasowy (pełny)",
                mecz.wynik_temp_gosp_full,
                mecz.wynik_temp_gosc_full,
            ),
            self._stat(
                mecz,
                "Wynik tymczasowy (do przerwy)",
                mecz.wynik_temp_gosp_pol,
                mecz.wynik_temp_gosc_pol,
            ),
            self._stat(mecz, "Wynik końcowy", mecz.wynik_koncowy_gosp, mecz.wynik_koncowy_gosc),
            self._stat(mecz, "Bramki", mecz.wynik_bramki_gosp, mecz.wynik_bramki_gosc),
            self._stat(
                mecz, "Dogrywka 1 — do przerwy", mecz.dogrywka_1_pol_gosp, mecz.dogrywka_1_pol_gosc
            ),
            self._stat(
                mecz, "Dogrywka 1 — pełna", mecz.dogrywka_1_full_gosp, mecz.dogrywka_1_full_gosc
            ),
            self._stat(
                mecz, "Dogrywka 2 — do przerwy", mecz.dogrywka_2_pol_gosp, mecz.dogrywka_2_pol_gosc
            ),
            self._stat(
                mecz, "Dogrywka 2 — pełna", mecz.dogrywka_2_full_gosp, mecz.dogrywka_2_full_gosc
            ),
            self._stat(
                mecz,
                "Rzuty karne — po dogrywce",
                mecz.dogrywka_karne_gosp,
                mecz.dogrywka_karne_gosc,
            ),
            self._stat(
                mecz, "Rzuty karne — bramki", mecz.karne_bramki_gosp, mecz.karne_bramki_gosc
            ),
            self._stat(mecz, "Rzuty karne — liczba", mecz.karne_ile_gosp, mecz.karne_ile_gosc),
            self._stat(mecz, "Kary drużynowe", mecz.kary_gosp, mecz.kary_gosc),
            self._stat(mecz, "Timeout 1", mecz.timeout1_gosp, mecz.timeout1_gosc),
            self._stat(mecz, "Timeout 2", mecz.timeout2_gosp, mecz.timeout2_gosc),
            self._stat(mecz, "Timeout 3", mecz.timeout3_gosp, mecz.timeout3_gosc),
        ]

        return SzczegolyMeczuViewModel(
            id_mecz=mecz.id,
            gospodarz=self._format.tekst(gospodarz_nazwa),
            gosc=self._format.tekst(gosc_nazwa),
            wynik_naglowek=wynik_naglowek,
            wynik_do_przerwy=wynik_do_przerwy,
            dopisek_wyniku=dopisek_wyniku,
            rozgrywki=self._format.tekst(nazwa_rozgrywki),
            kolejka=kolejka_etykieta,
            termin=self._format.data(mecz.data_faktyczna),
            hala=self._format.tekst(nazwa_hala),
            status=status,
            dane_podstawowe=dane_podstawowe,
            statystyki=statystyki,
            sklad_gospodarz=self._sklady.przygotuj(sklad_gospodarz, kolory),
            sklad_gosc=self._sklady.przygotuj(sklad_gosc, kolory),
            sklad_inne=self._sklady.przygotuj(szczegoly.sklad_inne, kolory, False),
        )

    def przygotuj_liste(self, strona: StronaMeczow) -> StronaMeczowViewModel:
        pozycje = []
        for pozycja in strona.pozycje:
            mecz = pozycja.mecz
            gospodarz, gosc = self._reguly.para(mecz, pozycja.gospodarz, pozycja.gosc)
            a, b = self._reguly.para(mecz, mecz.wynik_gosp_full, mecz.wynik_gosc_full)
            pozycje.append(
                PozycjaListyMeczowViewModel(
                    id_mecz=pozycja.id_mecz,
                    termin=pozycja.termin,
                    sezon=pozycja.sezon,
                    rozgrywki=pozycja.rozgrywki,
                    gospodarz=gospodarz,
                    gosc=gosc,
                    hala=pozycja.hala,
                    runda=pozycja.runda,
                    kolejka=pozycja.kolejka,
                    wynik=f"{a} : {b}" if a is not None and b is not None else "- : -",
                    dopisek_wyniku=self._format.dopisek(mecz, self._reguly),
                )
            )
        return StronaMeczowViewModel(
            pozycje=pozycje,
            liczba_wszystkich=strona.liczba_wszystkich,
            strona=strona.strona,
            rozmiar_strony=strona.rozmiar_strony,
        )

    def _stat(
        self, mecz: DaneMeczu, etykieta: str, a: int | str | None, b: int | str | None
    ) -> tuple[str, str, str]:
        x, y = self._reguly.para(mecz, a, b)
        return etykieta, self._format.tekst(x), self._format.tekst(y)
