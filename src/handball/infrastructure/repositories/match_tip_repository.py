from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, cast

from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.domain.match_predictions import WzorceNazwLig
from handball.domain.match_tips import PozycjaTypowania
from handball.infrastructure.database.models.competitions import Kolejka, Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.repositories.schedule_repository import ZapytanieMeczowTerminarza


class TypowaniaSQLAlchemyRepository:
    def __init__(self, sesja: Session, zapytanie: ZapytanieMeczowTerminarza | None = None) -> None:
        self._sesja = sesja
        self._zapytanie = zapytanie or ZapytanieMeczowTerminarza()

    def pobierz_rozgrywki(self, data_od: date, data_do: date, wzorce: WzorceNazwLig) -> list[str]:
        if not wzorce.wzorce:
            return []
        zapytanie = (
            select(Rozgrywki.nazwa)
            .join(Mecz, Mecz.id_rozgrywki == Rozgrywki.id)
            .where(self._w_okresie(data_od, data_do), self._ligi_modelu(wzorce))
            .group_by(Rozgrywki.nazwa)
            .order_by(Rozgrywki.nazwa.asc())
        )
        wiersze = self._wykonaj(zapytanie, "Nie udało się odczytać rozgrywek okresu.")
        return [cast(str, w[0]) for w in wiersze if w[0]]

    def pobierz_mecze(
        self,
        data_od: date,
        data_do: date,
        rozgrywki: frozenset[str],
        wzorce: WzorceNazwLig,
    ) -> list[PozycjaTypowania]:
        if not wzorce.wzorce:
            return []
        zapytanie = (
            self._zapytanie.utworz(Rozgrywki.id, Rozgrywki.nazwa, Sezon.nazwa)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .where(self._w_okresie(data_od, data_do), self._ligi_modelu(wzorce))
        )
        if rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa.in_(sorted(rozgrywki)))
        zapytanie = zapytanie.order_by(
            Rozgrywki.nazwa.asc(),
            Rozgrywki.id.asc(),
            Kolejka.nr.asc().nulls_last(),
            Kolejka.id.asc().nulls_last(),
            self._zapytanie.termin.asc(),
            Mecz.id.asc(),
        )
        wiersze = self._wykonaj(zapytanie, "Nie udało się odczytać meczów okresu.")
        n = ZapytanieMeczowTerminarza.LICZBA_KOLUMN
        return [
            PozycjaTypowania(
                id_rozgrywki=cast(int, w[n]),
                rozgrywki=cast(str, w[n + 1] or ""),
                sezon=cast(str, w[n + 2] or ""),
                pozycja=self._zapytanie.pozycja(w),
            )
            for w in wiersze
        ]

    def _w_okresie(self, data_od: date, data_do: date) -> ColumnElement[bool]:
        poczatek = datetime.combine(data_od, time.min)
        koniec = datetime.combine(data_do + timedelta(days=1), time.min)
        termin = self._zapytanie.termin
        return (termin >= poczatek) & (termin < koniec)

    def _ligi_modelu(self, wzorce: WzorceNazwLig) -> ColumnElement[bool]:
        return or_(
            *(
                Rozgrywki.nazwa.regexp_match(wzorzec.wyrazenie, flags="i")
                for wzorzec in wzorce.wzorce
            )
        )

    def _wykonaj(self, zapytanie: Any, komunikat: str) -> list[Any]:
        try:
            return list(self._sesja.execute(zapytanie).all())
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(komunikat) from wyjatek
