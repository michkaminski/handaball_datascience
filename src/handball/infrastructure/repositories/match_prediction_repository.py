from __future__ import annotations

from typing import cast

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych
from handball.domain.match_predictions import MeczLigowy, WzorceNazwLig
from handball.infrastructure.database.models.competitions import Kolejka, Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon


class MeczeLigoweSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_mecze(self, wzorce: WzorceNazwLig) -> list[MeczLigowy]:
        if not wzorce.wzorce:
            return []
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        zespol_gospodarza = aliased(Zespol)
        zespol_goscia = aliased(Zespol)
        zapytanie = (
            select(
                Mecz.id,
                Rozgrywki.plec,
                Rozgrywki.nazwa,
                Mecz.id_sezon,
                Sezon.nazwa,
                Sezon.rok_rozpoczecia,
                Kolejka.nr,
                Mecz.data_faktyczna,
                Mecz.id_zespol_gosp,
                Mecz.id_zespol_gosc,
                gospodarz.nazwa,
                zespol_gospodarza.nazwa,
                gosc.nazwa,
                zespol_goscia.nazwa,
                Mecz.wynik_gosp_full,
                Mecz.wynik_gosc_full,
                Mecz.zamiana,
                Mecz.wycofany,
                Mecz.id_zespol_walkower,
            )
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Kolejka, Kolejka.id == Mecz.id_kolejka, isouter=True)
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
            .join(zespol_gospodarza, zespol_gospodarza.id == Mecz.id_zespol_gosp, isouter=True)
            .join(zespol_goscia, zespol_goscia.id == Mecz.id_zespol_gosc, isouter=True)
            .where(
                or_(
                    *(
                        Rozgrywki.nazwa.regexp_match(wzorzec.wyrazenie, flags="i")
                        for wzorzec in wzorce.wzorce
                    )
                )
            )
            .order_by(Mecz.data_faktyczna.asc().nulls_last(), Mecz.id.asc())
        )
        try:
            wiersze = self._sesja.execute(zapytanie).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów ligowych.") from wyjatek
        return [
            MeczLigowy(
                id_mecz=cast(int, w[0]),
                plec=cast(str | None, w[1]),
                nazwa_rozgrywek=cast(str | None, w[2]),
                id_sezon=cast(int, w[3]),
                sezon=cast(str, w[4]),
                rok_sezonu=cast(int | None, w[5]),
                kolejka=cast(int | None, w[6]),
                data=w[7],
                id_zespol_gosp=cast(int | None, w[8]),
                id_zespol_gosc=cast(int | None, w[9]),
                nazwa_gosp=cast(str | None, w[10] or w[11]),
                nazwa_gosc=cast(str | None, w[12] or w[13]),
                wynik_gosp=cast(int | None, w[14]),
                wynik_gosc=cast(int | None, w[15]),
                zamiana=cast(bool | None, w[16]),
                wycofany=cast(bool | None, w[17]),
                walkower=w[18] is not None,
            )
            for w in wiersze
        ]
