from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.domain.options import OpcjaWyboru
from handball.infrastructure.database.models.competitions import Sezon


class SezonSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_wszystkie(self) -> list[OpcjaWyboru]:
        try:
            zapytanie = select(Sezon).order_by(Sezon.id.desc())
            return [
                OpcjaWyboru(wartosc=sezon.id, etykieta=sezon.nazwa)
                for sezon in self._sesja.scalars(zapytanie)
            ]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udalo sie odczytac listy sezonow") from wyjatek
