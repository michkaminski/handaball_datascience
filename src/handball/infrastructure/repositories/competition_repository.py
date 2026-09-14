from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.infrastructure.database.models.competitions import Rozgrywki


class RozgrywkiSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_nazwy(self, id_sezon: int | None) -> list[str]:
        try:
            zapytanie = select(Rozgrywki.nazwa).distinct().order_by(Rozgrywki.nazwa.asc())
            if id_sezon is not None:
                zapytanie = zapytanie.where(Rozgrywki.id_sezon == id_sezon)
            return list(self._sesja.scalars(zapytanie))
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udalo sie odczytac listy rozgrywek") from wyjatek
