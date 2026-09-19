from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.domain.matches import (
    DaneMeczu,
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
                gospodarz=wiersz[3],
                gosc=wiersz[4],
                mecz=self._dane_meczu(wiersz.Mecz),
                hala=wiersz[5],
                runda=wiersz[6],
                kolejka=wiersz[7],
            )
            for wiersz in wiersze
        ]

        return StronaMeczow(
            pozycje=pozycje,
            liczba_wszystkich=liczba_wszystkich,
            strona=filtry.strona,
            rozmiar_strony=filtry.rozmiar_strony,
        )

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
        return SzczegolyMeczu(
            mecz=self._dane_meczu(mecz),
            nazwa_sezon=nazwa_sezon,
            nazwa_rozgrywki=nazwa_rozgrywki,
            nazwa_gospodarz=nazwa_gospodarz,
            nazwa_gosc=nazwa_gosc,
            nazwa_hala=nazwa_hala,
            miasto_hala=miasto_hala,
            nazwa_runda=nazwa_runda,
            nazwa_kolejka=nazwa_kolejka,
            nr_kolejka=nr_kolejka,
            nazwa_zespol_wycofany=nazwa_zespol_wycofany,
            nazwa_zespol_walkower=nazwa_zespol_walkower,
            sklad_gospodarz=[self._zawodnik(z) for z in zawodnicy if z.strona.strip() == "gosp"],
            sklad_gosc=[self._zawodnik(z) for z in zawodnicy if z.strona.strip() == "gosc"],
            sklad_inne=[self._zawodnik(z) for z in zawodnicy if z.strona.strip() == "inne"],
        )

    def _zawodnik(self, z: MeczZawodnik) -> ZawodnikMeczu:
        return ZawodnikMeczu(
            zawodnik=" ".join(filter(None, [z.imie, z.nazwisko])).strip() or None,
            nr_koszulki=z.nr_koszulki,
            pozycja=z.pozycja,
            bramki=z.bramki,
            dwie_minuty=z.dwie_minuty,
            upomnienie=z.upomnienie,
            dyskwalifikacja=z.dyskwalifikacja,
            kd=z.kd,
            wyjscie=z.wyjscie,
            karne_bramki=z.karne_bramki,
            karne_liczba=z.karne_liczba,
            karne_bramki_seria=z.karne_bramki_seria,
            karne_liczba_seria=z.karne_liczba_seria,
        )

    def _dane_meczu(self, mecz: Mecz) -> DaneMeczu:
        return DaneMeczu(
            id=mecz.id,
            lp=mecz.lp,
            alias_gosp=mecz.alias_gosp,
            alias_gosc=mecz.alias_gosc,
            wynik_gosp_pol=mecz.wynik_gosp_pol,
            wynik_gosp_full=mecz.wynik_gosp_full,
            wynik_gosc_pol=mecz.wynik_gosc_pol,
            wynik_gosc_full=mecz.wynik_gosc_full,
            wynik_temp_gosp_pol=mecz.wynik_temp_gosp_pol,
            wynik_temp_gosp_full=mecz.wynik_temp_gosp_full,
            wynik_temp_gosc_pol=mecz.wynik_temp_gosc_pol,
            wynik_temp_gosc_full=mecz.wynik_temp_gosc_full,
            wynik_koncowy_gosp=mecz.wynik_koncowy_gosp,
            wynik_koncowy_gosc=mecz.wynik_koncowy_gosc,
            wynik_bramki_gosp=mecz.wynik_bramki_gosp,
            wynik_bramki_gosc=mecz.wynik_bramki_gosc,
            dogrywka_1_pol_gosp=mecz.dogrywka_1_pol_gosp,
            dogrywka_1_pol_gosc=mecz.dogrywka_1_pol_gosc,
            dogrywka_1_full_gosp=mecz.dogrywka_1_full_gosp,
            dogrywka_1_full_gosc=mecz.dogrywka_1_full_gosc,
            dogrywka_2_pol_gosp=mecz.dogrywka_2_pol_gosp,
            dogrywka_2_pol_gosc=mecz.dogrywka_2_pol_gosc,
            dogrywka_2_full_gosp=mecz.dogrywka_2_full_gosp,
            dogrywka_2_full_gosc=mecz.dogrywka_2_full_gosc,
            dogrywka_karne_gosp=mecz.dogrywka_karne_gosp,
            dogrywka_karne_gosc=mecz.dogrywka_karne_gosc,
            karne_bramki_gosp=mecz.karne_bramki_gosp,
            karne_bramki_gosc=mecz.karne_bramki_gosc,
            karne_ile_gosp=mecz.karne_ile_gosp,
            karne_ile_gosc=mecz.karne_ile_gosc,
            kary_gosp=mecz.kary_gosp,
            kary_gosc=mecz.kary_gosc,
            czy_remis=mecz.czy_remis,
            zwyciezca=mecz.zwyciezca,
            timeout1_gosp=mecz.timeout1_gosp,
            timeout2_gosp=mecz.timeout2_gosp,
            timeout3_gosp=mecz.timeout3_gosp,
            timeout1_gosc=mecz.timeout1_gosc,
            timeout2_gosc=mecz.timeout2_gosc,
            timeout3_gosc=mecz.timeout3_gosc,
            data_propozycji=mecz.data_propozycji,
            data_faktyczna=mecz.data_faktyczna,
            data_ostatniej_zmiany=mecz.data_ostatniej_zmiany,
            zamiana=mecz.zamiana,
            wycofany=mecz.wycofany,
            wycofany_typ=mecz.wycofany_typ,
            id_zespol_walkower=mecz.id_zespol_walkower,
            protokol=mecz.protokol,
            protokol_zatwierdzony=mecz.protokol_zatwierdzony,
            protokol_zalacznik_typ=mecz.protokol_zalacznik_typ,
            protokol_zalacznik_nazwa=mecz.protokol_zalacznik_nazwa,
            komentarz=mecz.komentarz,
            widzowie=mecz.widzowie,
            transmisja=mecz.transmisja,
            transmisja_godzina=mecz.transmisja_godzina,
            bilety_url=mecz.bilety_url,
            po_para_id=mecz.po_para_id,
            po_para_id_gosp=mecz.po_para_id_gosp,
            po_para_id_gosc=mecz.po_para_id_gosc,
            rozgrywki_code=mecz.rozgrywki_code,
        )
