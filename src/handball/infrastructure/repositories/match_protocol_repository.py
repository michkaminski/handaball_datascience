from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.domain.match_protocol import DaneProtokolu, HalaProtokolu, SedziaProtokolu
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.officials import MeczSedzia
from handball.infrastructure.database.models.venues import Hala


class ProtokolMeczuSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_dane_protokolu(self, id_mecz: int) -> DaneProtokolu:
        mecz = (
            select(
                Mecz.id_hala,
                Hala.nazwa,
                Hala.miasto,
                Hala.ulica,
                Hala.numer,
                Hala.pojemnosc,
            )
            .join(Hala, Hala.id == Mecz.id_hala, isouter=True)
            .where(Mecz.id == id_mecz)
        )
        sedziowie = (
            select(MeczSedzia.rola, MeczSedzia.nazwisko, MeczSedzia.miasto)
            .where(MeczSedzia.id_mecz == id_mecz)
            .order_by(MeczSedzia.rola)
        )
        try:
            w = self._sesja.execute(mecz).first()
            obsada = self._sesja.execute(sedziowie).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać danych protokołu meczu.") from wyjatek
        if w is None:
            raise NieZnalezionoMeczu(f"Nie znaleziono meczu o id {id_mecz}")
        return DaneProtokolu(
            hala=HalaProtokolu(w[1], w[2], w[3], w[4], w[5]) if w[0] is not None else None,
            sedziowie=tuple(SedziaProtokolu(s[0], s[1], s[2]) for s in obsada),
        )
