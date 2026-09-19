from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.infrastructure.database.models.competitions import Kolejka, Runda


class EtapMeczowSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_rundy(self) -> list[str]:
        try:
            zapytanie = (
                select(Runda.nazwa)
                .where(Runda.nazwa.is_not(None), Runda.nazwa != "")
                .distinct()
                .order_by(Runda.nazwa)
            )
            return [nazwa for nazwa in self._sesja.scalars(zapytanie) if nazwa is not None]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać listy rund") from wyjatek

    def pobierz_kolejki(self) -> list[str]:
        try:
            zapytanie = (
                select(Kolejka.nazwa)
                .where(Kolejka.nazwa.is_not(None), Kolejka.nazwa != "")
                .distinct()
                .order_by(Kolejka.nazwa)
            )
            return [nazwa for nazwa in self._sesja.scalars(zapytanie) if nazwa is not None]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać listy kolejek") from wyjatek
