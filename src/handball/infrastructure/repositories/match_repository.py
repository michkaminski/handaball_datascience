from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych
from handball.domain.matches import FiltryMeczow, PozycjaListyMeczow, StronaMeczow
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.teams import ZespolSezon
from handball.infrastructure.database.models.venues import Hala


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
            select(Mecz, Sezon.nazwa, Rozgrywki.nazwa, gospodarz.nazwa, gosc.nazwa, Hala.nazwa)
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
        )

        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
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
