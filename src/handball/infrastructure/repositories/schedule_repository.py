from __future__ import annotations

from typing import Any, cast

from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych
from handball.domain.matches import DaneMeczu
from handball.domain.options import OpcjaWyboru
from handball.domain.schedule import FiltryTerminarza, PozycjaTerminarza
from handball.infrastructure.database.models.competitions import Kolejka, Rozgrywki, Runda
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon
from handball.infrastructure.database.models.venues import Hala


class ZapytanieMeczowTerminarza:
    LICZBA_KOLUMN = 22

    def __init__(self) -> None:
        self.termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)

    def utworz(self, *dodatkowe: Any) -> Select[Any]:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        zespol_gospodarza = aliased(Zespol)
        zespol_goscia = aliased(Zespol)
        return (
            select(
                Mecz.id,
                Mecz.wynik_gosp_full,
                Mecz.wynik_gosc_full,
                Mecz.dogrywka_1_full_gosp,
                Mecz.dogrywka_1_full_gosc,
                Mecz.dogrywka_karne_gosp,
                Mecz.dogrywka_karne_gosc,
                Mecz.data_propozycji,
                Mecz.data_faktyczna,
                Mecz.zamiana,
                Mecz.wycofany,
                Mecz.id_zespol_walkower,
                Mecz.id_zespol_gosp,
                Mecz.id_zespol_gosc,
                func.coalesce(gospodarz.nazwa, zespol_gospodarza.nazwa),
                func.coalesce(gosc.nazwa, zespol_goscia.nazwa),
                Hala.nazwa,
                Runda.id,
                Runda.nazwa,
                Kolejka.id,
                Kolejka.nazwa,
                Kolejka.nr,
                *dodatkowe,
            )
            .join(Kolejka, Kolejka.id == Mecz.id_kolejka, isouter=True)
            .join(Runda, Runda.id == Kolejka.id_runda, isouter=True)
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
            .join(Hala, Hala.id == Mecz.id_hala, isouter=True)
        )

    def pozycja(self, w: Any) -> PozycjaTerminarza:
        return PozycjaTerminarza(
            id_mecz=w[0],
            mecz=DaneMeczu(
                id=w[0],
                wynik_gosp_full=w[1],
                wynik_gosc_full=w[2],
                dogrywka_1_full_gosp=w[3],
                dogrywka_1_full_gosc=w[4],
                dogrywka_karne_gosp=w[5],
                dogrywka_karne_gosc=w[6],
                data_propozycji=w[7],
                data_faktyczna=w[8],
                zamiana=w[9],
                wycofany=w[10],
                id_zespol_walkower=w[11],
                id_zespol_gosp=w[12],
                id_zespol_gosc=w[13],
            ),
            gospodarz=w[14],
            gosc=w[15],
            hala=w[16],
            id_runda=w[17],
            runda=w[18],
            id_kolejka=w[19],
            kolejka=w[20],
            nr_kolejki=w[21],
        )


class TerminarzSQLAlchemyRepository:
    def __init__(self, sesja: Session, zapytanie: ZapytanieMeczowTerminarza | None = None) -> None:
        self._sesja = sesja
        self._zapytanie = zapytanie or ZapytanieMeczowTerminarza()

    def pobierz_rozgrywki(self, id_sezon: int) -> list[OpcjaWyboru]:
        zapytanie = (
            select(Rozgrywki.id, Rozgrywki.nazwa)
            .where(Rozgrywki.id_sezon == id_sezon)
            .order_by(Rozgrywki.nazwa.asc(), Rozgrywki.id.asc())
        )
        wiersze = self._wykonaj(zapytanie, "Nie udało się odczytać rozgrywek sezonu.")
        return [OpcjaWyboru(cast(int, w[0]), cast(str, w[1])) for w in wiersze]

    def pobierz_rundy(self, id_rozgrywki: int) -> list[OpcjaWyboru]:
        pierwsza_kolejka = func.min(Kolejka.nr)
        zapytanie = (
            select(Runda.id, Runda.nazwa)
            .join(Kolejka, Kolejka.id_runda == Runda.id, isouter=True)
            .where(Runda.id_rozgrywki == id_rozgrywki)
            .group_by(Runda.id, Runda.nazwa)
            .order_by(pierwsza_kolejka.asc().nulls_last(), Runda.id.asc())
        )
        wiersze = self._wykonaj(zapytanie, "Nie udało się odczytać rund rozgrywek.")
        return [
            OpcjaWyboru(cast(int, w[0]), (w[1] or "").strip() or f"Runda #{w[0]}") for w in wiersze
        ]

    def pobierz_kolejki(self, id_rozgrywki: int, id_runda: int | None) -> list[OpcjaWyboru]:
        zapytanie = select(Kolejka.id, Kolejka.nazwa, Kolejka.nr).where(
            Kolejka.id_rozgrywki == id_rozgrywki
        )
        if id_runda is not None:
            zapytanie = zapytanie.where(Kolejka.id_runda == id_runda)
        zapytanie = zapytanie.order_by(Kolejka.nr.asc().nulls_last(), Kolejka.id.asc())
        wiersze = self._wykonaj(zapytanie, "Nie udało się odczytać kolejek rozgrywek.")
        return [
            OpcjaWyboru(
                cast(int, w[0]),
                (w[1] or "").strip() or (f"Kolejka {w[2]}" if w[2] is not None else f"#{w[0]}"),
            )
            for w in wiersze
        ]

    def pobierz_mecze(self, filtry: FiltryTerminarza) -> list[PozycjaTerminarza]:
        zapytanie = self._zapytanie.utworz().where(
            Mecz.id_sezon == filtry.id_sezon, Mecz.id_rozgrywki == filtry.id_rozgrywki
        )
        if filtry.id_runda is not None:
            zapytanie = zapytanie.where(Kolejka.id_runda == filtry.id_runda)
        if filtry.id_kolejka is not None:
            zapytanie = zapytanie.where(Mecz.id_kolejka == filtry.id_kolejka)
        zapytanie = zapytanie.order_by(
            Kolejka.nr.asc().nulls_last(),
            Kolejka.id.asc().nulls_last(),
            self._zapytanie.termin.asc().nulls_last(),
            Mecz.id.asc(),
        )
        wiersze = self._wykonaj(zapytanie, "Nie udało się odczytać terminarza.")
        return [self._zapytanie.pozycja(w) for w in wiersze]

    def _wykonaj(self, zapytanie: Any, komunikat: str) -> list[Any]:
        try:
            return list(self._sesja.execute(zapytanie).all())
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(komunikat) from wyjatek
