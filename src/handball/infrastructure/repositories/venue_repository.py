from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.domain.options import OpcjaWyboru
from handball.infrastructure.database.models.venues import Hala


class HalaSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_wszystkie(self) -> list[OpcjaWyboru]:
        try:
            zapytanie = select(Hala).where(Hala.nazwa.is_not(None)).order_by(Hala.nazwa.asc())
            opcje = []
            for hala in self._sesja.scalars(zapytanie):
                assert hala.nazwa is not None
                opcje.append(OpcjaWyboru(wartosc=hala.id, etykieta=hala.nazwa))
            return opcje
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udalo sie odczytac listy hal") from wyjatek
