from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import Select, and_, distinct, func, or_, select
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from handball.domain.catalogs import (
    FiltryKatalogu,
    PozycjaDruzyny,
    PozycjaRozgrywek,
    PozycjaSezonu,
    StronaKatalogu,
)
from handball.domain.errors import BladOdczytuDanych
from handball.domain.options import OpcjaWyboru
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.teams import ZespolSezon


class KatalogPodstawowySQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_sezony(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaSezonu]:
        zapytanie = (
            select(
                Sezon.id.label("id"),
                Sezon.nazwa.label("nazwa"),
                Sezon.rok_rozpoczecia.label("rok_rozpoczecia"),
                func.count(distinct(Rozgrywki.id)).label("liczba_rozgrywek"),
                Sezon.stan.label("stan"),
                func.count(distinct(Mecz.id)).label("liczba_meczow"),
            )
            .outerjoin(Rozgrywki, Rozgrywki.id_sezon == Sezon.id)
            .outerjoin(Mecz, Mecz.id_rozgrywki == Rozgrywki.id)
            .group_by(Sezon.id, Sezon.nazwa, Sezon.rok_rozpoczecia, Sezon.stan)
        )
        if filtry.szukaj:
            zapytanie = zapytanie.where(Sezon.nazwa.icontains(filtry.szukaj, autoescape=True))
        if filtry.stan:
            zapytanie = zapytanie.where(Sezon.stan == filtry.stan)
        return self._strona(
            zapytanie,
            filtry,
            Sezon.id,
            lambda w: PozycjaSezonu(
                w["id"],
                w["nazwa"],
                w["rok_rozpoczecia"],
                w["liczba_rozgrywek"],
                w["stan"],
                w["liczba_meczow"],
            ),
            "sezonów",
        )

    def pobierz_rozgrywki(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaRozgrywek]:
        zapytanie = (
            select(
                Rozgrywki.id.label("id"),
                Rozgrywki.id_sezon.label("id_sezon"),
                Sezon.nazwa.label("sezon"),
                Rozgrywki.nazwa.label("nazwa"),
                Rozgrywki.plec.label("plec"),
                Rozgrywki.ile_zespolow.label("liczba_zespolow"),
                func.count(distinct(Mecz.id)).label("liczba_meczow"),
            )
            .join(Sezon, Sezon.id == Rozgrywki.id_sezon)
            .outerjoin(Mecz, Mecz.id_rozgrywki == Rozgrywki.id)
            .group_by(
                Rozgrywki.id, Sezon.nazwa, Rozgrywki.nazwa, Rozgrywki.plec, Rozgrywki.ile_zespolow
            )
        )
        if filtry.szukaj:
            zapytanie = zapytanie.where(Rozgrywki.nazwa.icontains(filtry.szukaj, autoescape=True))
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Rozgrywki.id_sezon == filtry.id_sezon)
        if filtry.plec:
            zapytanie = zapytanie.where(Rozgrywki.plec == filtry.plec)
        return self._strona(
            zapytanie,
            filtry,
            Rozgrywki.id,
            lambda w: PozycjaRozgrywek(
                w["id"],
                w["id_sezon"],
                w["sezon"],
                w["nazwa"],
                w["plec"],
                w["liczba_zespolow"],
                w["liczba_meczow"],
            ),
            "rozgrywek",
        )

    def pobierz_druzyny(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaDruzyny]:
        mecze = or_(
            and_(
                Mecz.id_zespol_gosp == ZespolSezon.id_zespol, Mecz.id_sezon == ZespolSezon.id_sezon
            ),
            and_(
                Mecz.id_zespol_gosc == ZespolSezon.id_zespol, Mecz.id_sezon == ZespolSezon.id_sezon
            ),
        )
        zapytanie = (
            select(
                ZespolSezon.id.label("id"),
                ZespolSezon.id_zespol.label("id_zespol"),
                ZespolSezon.id_sezon.label("id_sezon"),
                Sezon.nazwa.label("sezon"),
                ZespolSezon.nazwa.label("nazwa"),
                ZespolSezon.plec.label("plec"),
                ZespolSezon.miasto.label("miasto"),
                ZespolSezon.wycofany.label("wycofany"),
                func.count(distinct(Mecz.id)).label("liczba_meczow"),
            )
            .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
            .outerjoin(Mecz, mecze)
            .group_by(
                ZespolSezon.id,
                ZespolSezon.id_zespol,
                Sezon.nazwa,
                ZespolSezon.nazwa,
                ZespolSezon.plec,
                ZespolSezon.miasto,
                ZespolSezon.wycofany,
            )
        )
        if filtry.szukaj:
            zapytanie = zapytanie.where(
                or_(
                    ZespolSezon.nazwa.icontains(filtry.szukaj, autoescape=True),
                    ZespolSezon.miasto.icontains(filtry.szukaj, autoescape=True),
                )
            )
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(ZespolSezon.id_sezon == filtry.id_sezon)
        if filtry.plec:
            zapytanie = zapytanie.where(ZespolSezon.plec == filtry.plec)
        if filtry.miasto:
            zapytanie = zapytanie.where(
                ZespolSezon.miasto.icontains(filtry.miasto, autoescape=True)
            )
        if filtry.wycofany is not None:
            zapytanie = zapytanie.where(ZespolSezon.wycofany.is_(filtry.wycofany))
        return self._strona(
            zapytanie,
            filtry,
            ZespolSezon.id,
            lambda w: PozycjaDruzyny(
                w["id"],
                w["id_zespol"],
                w["id_sezon"],
                w["sezon"],
                w["nazwa"],
                w["plec"],
                w["miasto"],
                w["wycofany"],
                w["liczba_meczow"],
            ),
            "drużyn",
        )

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        try:
            return [
                OpcjaWyboru(id_sezon, nazwa)
                for id_sezon, nazwa in self._sesja.execute(
                    select(Sezon.id, Sezon.nazwa).order_by(
                        Sezon.rok_rozpoczecia.desc(), Sezon.id.desc()
                    )
                )
            ]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać sezonów.") from wyjatek

    def _strona[T](
        self,
        zapytanie: Select[Any],
        filtry: FiltryKatalogu,
        stabilna: object,
        mapper: Callable[[RowMapping], T],
        nazwa: str,
    ) -> StronaKatalogu[T]:
        try:
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            numer = min(filtry.strona, ostatnia)
            kolumna = zapytanie.selected_columns[filtry.sortowanie.removeprefix("-")]
            porzadek = kolumna.desc() if filtry.sortowanie.startswith("-") else kolumna.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(porzadek.nulls_last(), cast(ColumnElement[Any], stabilna))
                .offset((numer - 1) * filtry.rozmiar_strony)
                .limit(filtry.rozmiar_strony)
            ).mappings()
            return StronaKatalogu(
                [mapper(w) for w in wiersze], liczba, numer, filtry.rozmiar_strony
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(f"Nie udało się odczytać listy {nazwa}.") from wyjatek
