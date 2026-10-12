from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych
from handball.domain.match_statistics import MeczFormy
from handball.infrastructure.database.models.competitions import Rozgrywki
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon


class FormaMeczuSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_forme(self, id_mecz: int, id_zespol: int) -> list[MeczFormy]:
        analizowany = aliased(Mecz)
        rywal_sezon = aliased(ZespolSezon)
        rywal = aliased(Zespol)
        id_rywala = func.coalesce(func.nullif(Mecz.id_zespol_gosc, id_zespol), Mecz.id_zespol_gosp)
        sezon_analizowanego = (
            select(analizowany.id_sezon).where(analizowany.id == id_mecz).scalar_subquery()
        )
        termin_analizowanego = (
            select(analizowany.data_faktyczna).where(analizowany.id == id_mecz).scalar_subquery()
        )
        zapytanie = (
            select(
                Mecz.id,
                Mecz.data_faktyczna,
                Mecz.id_zespol_gosp,
                Mecz.zamiana,
                Mecz.wynik_gosp_full,
                Mecz.wynik_gosc_full,
                Mecz.dogrywka_karne_gosp,
                Mecz.dogrywka_karne_gosc,
                Mecz.dogrywka_1_full_gosp,
                Mecz.dogrywka_1_full_gosc,
                Mecz.dogrywka_2_full_gosp,
                Mecz.dogrywka_2_full_gosc,
                Rozgrywki.nazwa,
                func.coalesce(rywal_sezon.nazwa, rywal.nazwa),
            )
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(
                rywal_sezon,
                (rywal_sezon.id_zespol == id_rywala) & (rywal_sezon.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(rywal, rywal.id == id_rywala, isouter=True)
            .where(
                Mecz.id_sezon == sezon_analizowanego,
                or_(Mecz.id_zespol_gosp == id_zespol, Mecz.id_zespol_gosc == id_zespol),
                or_(Mecz.id == id_mecz, Mecz.data_faktyczna <= termin_analizowanego),
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .order_by(Mecz.data_faktyczna.asc().nulls_last(), Mecz.id.asc())
        )
        try:
            wiersze = self._sesja.execute(zapytanie).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać formy drużyny.") from wyjatek
        return [self._mecz(w, id_zespol) for w in wiersze]

    def _mecz(self, w: Any, id_zespol: int) -> MeczFormy:
        w_kolumnie_gospodarza = w[2] == id_zespol

        def strony(gosp: int | None, gosc: int | None) -> tuple[int | None, int | None]:
            return (gosp, gosc) if w_kolumnie_gospodarza else (gosc, gosp)

        zdobyte, stracone = strony(w[4], w[5])
        seria_zdobyte, seria_stracone = strony(w[6], w[7])
        if w[10] is not None and w[11] is not None:
            dogrywka_zdobyte, dogrywka_stracone = strony(w[10], w[11])
        else:
            dogrywka_zdobyte, dogrywka_stracone = strony(w[8], w[9])
        return MeczFormy(
            id_mecz=w[0],
            data=w[1],
            rywal=w[13].strip() if w[13] else w[13],
            u_siebie=w_kolumnie_gospodarza != bool(w[3]),
            bramki_zdobyte=zdobyte or 0,
            bramki_stracone=stracone or 0,
            seria_zdobyte=seria_zdobyte,
            seria_stracone=seria_stracone,
            dogrywka_zdobyte=dogrywka_zdobyte,
            dogrywka_stracone=dogrywka_stracone,
            rozgrywki=w[12],
        )
