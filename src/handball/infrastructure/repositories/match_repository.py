from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.domain.matches import (
    FiltryMeczow,
    PozycjaListyMeczow,
    StronaMeczow,
    SzczegolyMeczu,
    ZawodnikMeczu,
)
from handball.infrastructure.database.models.competitions import Kolejka, Rozgrywki, Runda, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon
from handball.infrastructure.database.models.venues import Hala

BRAK = "—"


class MeczSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow:
        try:
            return self._pobierz_liste(filtry)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udalo sie odczytac listy meczow") from wyjatek

    def _pobierz_liste(self, filtry: FiltryMeczow) -> StronaMeczow:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)

        zapytanie = (
            select(
                Mecz,
                Sezon.nazwa,
                Rozgrywki.nazwa,
                gospodarz.nazwa,
                gosc.nazwa,
                Hala.nazwa,
                Runda.nazwa,
                Kolejka.nazwa,
            )
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(
                gospodarz,
                (gospodarz.id_zespol == Mecz.id_zespol_gosp)
                & (gospodarz.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(
                gosc,
                (gosc.id_zespol == Mecz.id_zespol_gosc) & (gosc.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(Hala, Hala.id == Mecz.id_hala, isouter=True)
            .join(Kolejka, Kolejka.id == Mecz.id_kolejka, isouter=True)
            .join(Runda, Runda.id == Kolejka.id_runda, isouter=True)
        )

        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
        if filtry.runda:
            zapytanie = zapytanie.where(Runda.nazwa == filtry.runda)
        if filtry.kolejka:
            zapytanie = zapytanie.where(Kolejka.nazwa == filtry.kolejka)
        if filtry.id_hala is not None:
            zapytanie = zapytanie.where(Mecz.id_hala == filtry.id_hala)
        if filtry.szukaj_druzyny:
            wzorzec = f"%{filtry.szukaj_druzyny}%"
            tozsamosci_zespolow = select(ZespolSezon.id_zespol).where(
                ZespolSezon.nazwa.ilike(wzorzec)
            )
            zapytanie = zapytanie.where(
                or_(
                    Mecz.id_zespol_gosp.in_(tozsamosci_zespolow),
                    Mecz.id_zespol_gosc.in_(tozsamosci_zespolow),
                )
            )
        if filtry.data_od is not None and filtry.data_do is not None:
            zapytanie = zapytanie.where(
                Mecz.data_faktyczna >= filtry.data_od, Mecz.data_faktyczna < filtry.data_do
            )

        liczba_wszystkich = (
            self._sesja.scalar(
                select(func.count()).select_from(zapytanie.with_only_columns(Mecz.id).subquery())
            )
            or 0
        )

        porzadek = (
            Mecz.data_faktyczna.desc()
            if filtry.sortowanie == "-data"
            else Mecz.data_faktyczna.asc()
        )
        zapytanie = zapytanie.order_by(porzadek, Mecz.id.asc())
        zapytanie = zapytanie.limit(filtry.rozmiar_strony).offset(
            (filtry.strona - 1) * filtry.rozmiar_strony
        )

        wiersze = self._sesja.execute(zapytanie).all()

        pozycje = [
            PozycjaListyMeczow(
                id_mecz=wiersz.Mecz.id,
                termin=wiersz.Mecz.data_faktyczna,
                sezon=wiersz[1],
                rozgrywki=wiersz[2],
                gospodarz=wiersz[4] if wiersz.Mecz.zamiana else wiersz[3],
                gosc=wiersz[3] if wiersz.Mecz.zamiana else wiersz[4],
                wynik=self._sformatuj_wynik(wiersz.Mecz),
                hala=wiersz[5],
                runda=wiersz[6],
                kolejka=wiersz[7],
                dopisek_wyniku=self._dopisek_wyniku(wiersz.Mecz),
            )
            for wiersz in wiersze
        ]

        return StronaMeczow(
            pozycje=pozycje,
            liczba_wszystkich=liczba_wszystkich,
            strona=filtry.strona,
            rozmiar_strony=filtry.rozmiar_strony,
        )

    @staticmethod
    def _sformatuj_wynik(mecz: Mecz) -> str:
        if mecz.wynik_gosp_full is None or mecz.wynik_gosc_full is None:
            return "- : -"
        if mecz.zamiana:
            return f"{mecz.wynik_gosc_full} : {mecz.wynik_gosp_full}"
        return f"{mecz.wynik_gosp_full} : {mecz.wynik_gosc_full}"

    @staticmethod
    def _dopisek_wyniku(mecz: Mecz) -> str | None:
        zamiana = bool(mecz.zamiana)
        if mecz.dogrywka_karne_gosp is not None or mecz.dogrywka_karne_gosc is not None:
            a, b = MeczSQLAlchemyRepository._para(
                zamiana, mecz.dogrywka_karne_gosp, mecz.dogrywka_karne_gosc
            )
            a = a if a is not None else 0
            b = b if b is not None else 0
            return f"k {a}-{b}"
        if mecz.dogrywka_1_full_gosp is not None or mecz.dogrywka_1_full_gosc is not None:
            return "dogrywka"
        return None

    def pobierz_szczegoly(self, id_mecz: int) -> SzczegolyMeczu:
        try:
            return self._pobierz_szczegoly(id_mecz)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udalo sie odczytac szczegolow meczu") from wyjatek

    def _pobierz_szczegoly(self, id_mecz: int) -> SzczegolyMeczu:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        zespol_wycofany = aliased(Zespol)
        zespol_walkower = aliased(Zespol)

        wiersz = self._sesja.execute(
            select(
                Mecz,
                Sezon.nazwa,
                Rozgrywki.nazwa,
                gospodarz.nazwa,
                gosc.nazwa,
                Hala.nazwa,
                Hala.miasto,
                Runda.nazwa,
                Kolejka.nazwa,
                Kolejka.nr,
                zespol_wycofany.nazwa,
                zespol_walkower.nazwa,
            )
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(
                gospodarz,
                (gospodarz.id_zespol == Mecz.id_zespol_gosp)
                & (gospodarz.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(
                gosc,
                (gosc.id_zespol == Mecz.id_zespol_gosc) & (gosc.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(Hala, Hala.id == Mecz.id_hala, isouter=True)
            .join(Kolejka, Kolejka.id == Mecz.id_kolejka, isouter=True)
            .join(Runda, Runda.id == Kolejka.id_runda, isouter=True)
            .join(zespol_wycofany, zespol_wycofany.id == Mecz.id_zespol_wycofany, isouter=True)
            .join(zespol_walkower, zespol_walkower.id == Mecz.id_zespol_walkower, isouter=True)
            .where(Mecz.id == id_mecz)
        ).first()

        if wiersz is None:
            raise NieZnalezionoMeczu(f"Nie znaleziono meczu o id {id_mecz}")

        (
            mecz,
            nazwa_sezon,
            nazwa_rozgrywki,
            nazwa_gospodarz,
            nazwa_gosc,
            nazwa_hala,
            miasto_hala,
            nazwa_runda,
            nazwa_kolejka,
            nr_kolejka,
            nazwa_zespol_wycofany,
            nazwa_zespol_walkower,
        ) = wiersz
        zamiana = bool(mecz.zamiana)
        gospodarz_nazwa, gosc_nazwa = self._para(zamiana, nazwa_gospodarz, nazwa_gosc)

        zawodnicy = (
            self._sesja.execute(
                select(MeczZawodnik)
                .where(MeczZawodnik.id_mecz == id_mecz)
                .order_by(
                    MeczZawodnik.strona,
                    MeczZawodnik.nr_koszulki.nulls_last(),
                    MeczZawodnik.nazwisko,
                )
            )
            .scalars()
            .all()
        )
        strona_gospodarz, strona_gosc = self._para(zamiana, "gosp", "gosc")
        sklad_gospodarz = [
            self._zawodnik(z) for z in zawodnicy if z.strona.strip() == strona_gospodarz
        ]
        sklad_gosc = [self._zawodnik(z) for z in zawodnicy if z.strona.strip() == strona_gosc]
        sklad_inne = [self._zawodnik(z) for z in zawodnicy if z.strona.strip() == "inne"]

        wynik_gosp, wynik_gosc = self._para(zamiana, mecz.wynik_gosp_full, mecz.wynik_gosc_full)
        pol_gosp, pol_gosc = self._para(zamiana, mecz.wynik_gosp_pol, mecz.wynik_gosc_pol)
        wynik_naglowek = f"{self._tekst(wynik_gosp)} : {self._tekst(wynik_gosc)}"
        wynik_do_przerwy = (
            f"do przerwy {self._tekst(pol_gosp)} : {self._tekst(pol_gosc)}"
            if pol_gosp is not None or pol_gosc is not None
            else ""
        )
        dopisek_wyniku = self._dopisek_wyniku(mecz) or ""

        if mecz.wycofany:
            status = "Wycofany"
        elif mecz.id_zespol_walkower is not None:
            status = "Walkower"
        elif mecz.wynik_gosp_full is not None and mecz.wynik_gosc_full is not None:
            status = "Rozegrany"
        else:
            status = "Zaplanowany"

        kolejka_etykieta = nazwa_kolejka or (f"Kolejka {nr_kolejka}" if nr_kolejka else BRAK)

        def stat(etykieta: str, a: Any, b: Any) -> tuple[str, str, str]:
            x, y = self._para(zamiana, a, b)
            return etykieta, self._tekst(x), self._tekst(y)

        dane_podstawowe = [
            ("Sezon", self._tekst(nazwa_sezon)),
            ("Rozgrywki", self._tekst(nazwa_rozgrywki)),
            ("Kod rozgrywek", self._tekst(mecz.rozgrywki_code)),
            ("Runda", self._tekst(nazwa_runda)),
            ("Kolejka", kolejka_etykieta),
            ("Kolejność w kolejce (lp)", self._tekst(mecz.lp)),
            ("Data faktyczna", self._data(mecz.data_faktyczna)),
            ("Data propozycji", self._data(mecz.data_propozycji)),
            ("Data ostatniej zmiany", self._data(mecz.data_ostatniej_zmiany)),
            ("Gospodarz", self._tekst(gospodarz_nazwa)),
            ("Gość", self._tekst(gosc_nazwa)),
            ("Hala", self._tekst(nazwa_hala)),
            ("Miasto hali", self._tekst(miasto_hala)),
            ("Status", status),
            ("Zwycięzca (kod)", self._tekst(mecz.zwyciezca)),
            ("Remis", self._flaga(mecz.czy_remis)),
            ("Widzowie", self._tekst(mecz.widzowie)),
            ("Transmisja", self._tekst(mecz.transmisja)),
            ("Godzina transmisji", self._tekst(mecz.transmisja_godzina)),
            ("Bilety", self._tekst(mecz.bilety_url)),
            ("Zamiana stron", self._flaga(mecz.zamiana)),
            ("Wycofany", self._flaga(mecz.wycofany)),
            ("Typ wycofania", self._tekst(mecz.wycofany_typ)),
            ("Zespół wycofany", self._tekst(nazwa_zespol_wycofany)),
            ("Zespół — walkower", self._tekst(nazwa_zespol_walkower)),
            ("Protokół", self._tekst(mecz.protokol)),
            ("Protokół zatwierdzony", self._flaga(mecz.protokol_zatwierdzony)),
            ("Załącznik protokołu", self._tekst(mecz.protokol_zalacznik_nazwa)),
            ("Typ załącznika", self._tekst(mecz.protokol_zalacznik_typ)),
            ("Komentarz", self._tekst(mecz.komentarz)),
            ("Alias — gospodarz", self._tekst(mecz.alias_gosp)),
            ("Alias — gość", self._tekst(mecz.alias_gosc)),
            ("ID pary play-off", self._tekst(mecz.po_para_id)),
            ("ID pary play-off — gospodarz", self._tekst(mecz.po_para_id_gosp)),
            ("ID pary play-off — gość", self._tekst(mecz.po_para_id_gosc)),
        ]

        statystyki = [
            stat("Wynik (pełny)", mecz.wynik_gosp_full, mecz.wynik_gosc_full),
            stat("Do przerwy", mecz.wynik_gosp_pol, mecz.wynik_gosc_pol),
            stat(
                "Wynik tymczasowy (pełny)", mecz.wynik_temp_gosp_full, mecz.wynik_temp_gosc_full
            ),
            stat(
                "Wynik tymczasowy (do przerwy)", mecz.wynik_temp_gosp_pol, mecz.wynik_temp_gosc_pol
            ),
            stat("Wynik końcowy", mecz.wynik_koncowy_gosp, mecz.wynik_koncowy_gosc),
            stat("Bramki", mecz.wynik_bramki_gosp, mecz.wynik_bramki_gosc),
            stat("Dogrywka 1 — do przerwy", mecz.dogrywka_1_pol_gosp, mecz.dogrywka_1_pol_gosc),
            stat("Dogrywka 1 — pełna", mecz.dogrywka_1_full_gosp, mecz.dogrywka_1_full_gosc),
            stat("Dogrywka 2 — do przerwy", mecz.dogrywka_2_pol_gosp, mecz.dogrywka_2_pol_gosc),
            stat("Dogrywka 2 — pełna", mecz.dogrywka_2_full_gosp, mecz.dogrywka_2_full_gosc),
            stat("Rzuty karne — po dogrywce", mecz.dogrywka_karne_gosp, mecz.dogrywka_karne_gosc),
            stat("Rzuty karne — bramki", mecz.karne_bramki_gosp, mecz.karne_bramki_gosc),
            stat("Rzuty karne — liczba", mecz.karne_ile_gosp, mecz.karne_ile_gosc),
            stat("Kary drużynowe", mecz.kary_gosp, mecz.kary_gosc),
            stat("Timeout 1", mecz.timeout1_gosp, mecz.timeout1_gosc),
            stat("Timeout 2", mecz.timeout2_gosp, mecz.timeout2_gosc),
            stat("Timeout 3", mecz.timeout3_gosp, mecz.timeout3_gosc),
        ]

        return SzczegolyMeczu(
            id_mecz=mecz.id,
            gospodarz=self._tekst(gospodarz_nazwa),
            gosc=self._tekst(gosc_nazwa),
            wynik_naglowek=wynik_naglowek,
            wynik_do_przerwy=wynik_do_przerwy,
            dopisek_wyniku=dopisek_wyniku,
            rozgrywki=self._tekst(nazwa_rozgrywki),
            kolejka=kolejka_etykieta,
            termin=self._data(mecz.data_faktyczna),
            hala=self._tekst(nazwa_hala),
            status=status,
            dane_podstawowe=dane_podstawowe,
            statystyki=statystyki,
            sklad_gospodarz=sklad_gospodarz,
            sklad_gosc=sklad_gosc,
            sklad_inne=sklad_inne,
        )

    def _zawodnik(self, z: MeczZawodnik) -> ZawodnikMeczu:
        imie_nazwisko = " ".join(filter(None, [z.imie, z.nazwisko])).strip()
        return ZawodnikMeczu(
            nr_koszulki=self._tekst(z.nr_koszulki),
            zawodnik=self._tekst(imie_nazwisko or None),
            pozycja=self._tekst(z.pozycja),
            bramki=self._tekst(z.bramki),
            dwie_minuty=self._tekst(z.dwie_minuty),
            upomnienie=self._flaga(z.upomnienie),
            dyskwalifikacja=self._flaga(z.dyskwalifikacja),
            kd=self._tekst(z.kd),
            wyjscie=self._flaga(z.wyjscie),
            karne=self._ulamek(z.karne_bramki, z.karne_liczba),
            karne_seria=self._ulamek(z.karne_bramki_seria, z.karne_liczba_seria),
        )

    @staticmethod
    def _para(zamiana: bool, a: Any, b: Any) -> tuple[Any, Any]:
        return (b, a) if zamiana else (a, b)

    @staticmethod
    def _tekst(wartosc: Any) -> str:
        if wartosc is None or wartosc == "":
            return BRAK
        return str(wartosc)

    @staticmethod
    def _flaga(wartosc: bool | None) -> str:
        if wartosc is None:
            return BRAK
        return "Tak" if wartosc else "Nie"

    @staticmethod
    def _data(wartosc: datetime.datetime | None) -> str:
        if wartosc is None:
            return BRAK
        return wartosc.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def _ulamek(licznik: int | None, mianownik: int | None) -> str:
        if licznik is None and mianownik is None:
            return BRAK
        licznik = licznik if licznik is not None else 0
        mianownik = mianownik if mianownik is not None else 0
        return f"{licznik}/{mianownik}"
