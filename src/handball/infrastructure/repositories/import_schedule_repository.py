from __future__ import annotations

from dataclasses import replace
from typing import Any

from sqlalchemy import ColumnElement, and_, exists, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.domain.schedule import FiltryPobierania, PozycjaTerminarza
from handball.infrastructure.database.models.competitions import Kolejka, Rozgrywki
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.repositories.schedule_repository import ZapytanieMeczowTerminarza


class PobieranieMeczowSQLAlchemyRepository:
    def __init__(self, sesja: Session, zapytanie: ZapytanieMeczowTerminarza | None = None) -> None:
        self._sesja = sesja
        self._zapytanie = zapytanie or ZapytanieMeczowTerminarza()

    def pobierz(self, filtry: FiltryPobierania) -> list[tuple[PozycjaTerminarza, bool]]:
        brak_danych = _brak_danych_meczu()
        zapytanie = self._zapytanie.utworz(brak_danych, Rozgrywki.nazwa).join(
            Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki
        )
        zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.id_rozgrywki is not None:
            zapytanie = zapytanie.where(Mecz.id_rozgrywki == filtry.id_rozgrywki)
        if filtry.id_runda is not None:
            zapytanie = zapytanie.where(Kolejka.id_runda == filtry.id_runda)
        if filtry.id_kolejka is not None:
            zapytanie = zapytanie.where(Mecz.id_kolejka == filtry.id_kolejka)
        zapytanie = zapytanie.order_by(
            Rozgrywki.nazwa.asc(),
            Rozgrywki.id.asc(),
            Kolejka.nr.asc().nulls_last(),
            Kolejka.id.asc().nulls_last(),
            self._zapytanie.termin.asc().nulls_last(),
            Mecz.id.asc(),
        )
        try:
            wiersze = list(self._sesja.execute(zapytanie).all())
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów do pobrania.") from wyjatek
        return [self._pozycja(wiersz, filtry) for wiersz in wiersze]

    def _pozycja(self, wiersz: Any, filtry: FiltryPobierania) -> tuple[PozycjaTerminarza, bool]:
        pozycja = self._zapytanie.pozycja(wiersz)
        if filtry.id_rozgrywki is None:
            nazwa = str(wiersz[23] or "").strip() or "Rozgrywki"
            runda = (pozycja.runda or "").strip() or "Bez rundy"
            pozycja = replace(pozycja, runda=f"{nazwa} · {runda}")
        return pozycja, bool(wiersz[22])


def _brak_zawodnikow(strona: str, z_bramkami: bool) -> ColumnElement[bool]:
    warunki = [MeczZawodnik.id_mecz == Mecz.id, MeczZawodnik.strona == strona]
    if z_bramkami:
        warunki.append(MeczZawodnik.bramki > 0)
    return ~exists(select(MeczZawodnik.id_zawodnik).where(*warunki))


def _brak_danych_meczu() -> ColumnElement[bool]:
    return and_(
        Mecz.wynik_gosp_full.is_not(None),
        Mecz.wynik_gosc_full.is_not(None),
        Mecz.wycofany.is_not(True),
        Mecz.id_zespol_walkower.is_(None),
        or_(
            _brak_zawodnikow("gosp", False),
            _brak_zawodnikow("gosc", False),
            and_(Mecz.wynik_gosp_full > 0, _brak_zawodnikow("gosp", True)),
            and_(Mecz.wynik_gosc_full > 0, _brak_zawodnikow("gosc", True)),
        ),
    )
