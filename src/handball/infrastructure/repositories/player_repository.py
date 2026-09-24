from __future__ import annotations

from decimal import Decimal
from typing import cast

from sqlalchemy import Integer, Select, and_, distinct, extract, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.sql.selectable import CTE

from handball.domain.errors import BladOdczytuDanych
from handball.domain.players import FiltryZawodnikow, PozycjaListyZawodnikow, StronaZawodnikow
from handball.infrastructure.database.match_sides import StronyMeczuSql
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.rosters import SkladSezonowy
from handball.infrastructure.database.models.teams import ZespolSezon


class ZawodnikSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_pozycje(self) -> list[str]:
        pozycja = func.nullif(func.trim(MeczZawodnik.pozycja), "")
        try:
            wynik = self._sesja.scalars(
                select(pozycja).where(pozycja.is_not(None)).distinct().order_by(pozycja)
            )
            return [str(wartosc) for wartosc in wynik]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać pozycji zawodników.") from wyjatek

    def pobierz_liste(self, filtry: FiltryZawodnikow) -> StronaZawodnikow:
        try:
            zapytanie = self._zapytanie(filtry)
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            numer = min(filtry.strona, ostatnia)
            kolumna = zapytanie.selected_columns[filtry.sortowanie.removeprefix("-")]
            porzadek = kolumna.desc() if filtry.sortowanie.startswith("-") else kolumna.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(porzadek.nulls_last(), Zawodnik.id.asc())
                .offset((numer - 1) * filtry.rozmiar_strony)
                .limit(filtry.rozmiar_strony)
            ).mappings()
            pozycje = [
                PozycjaListyZawodnikow(
                    id_zawodnik=w["id"],
                    imie=w["imie"],
                    nazwisko=w["nazwisko"],
                    rocznik=w["rocznik"],
                    pozycje=tuple(sorted(p for p in (w["pozycje"] or []) if p)),
                    druzyny=tuple(sorted(n for n in (w["druzyny"] or []) if n)),
                    wzrost=w["wzrost"],
                    waga=w["waga"],
                )
                for w in wiersze
            ]
            return StronaZawodnikow(pozycje, liczba, numer, filtry.rozmiar_strony)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać listy zawodników.") from wyjatek

    def _wpisy(self, filtry: FiltryZawodnikow) -> CTE:
        zespol = StronyMeczuSql.zespol(MeczZawodnik.strona)
        zapytanie = (
            select(
                MeczZawodnik.id_zawodnik,
                func.nullif(func.trim(MeczZawodnik.pozycja), "").label("pozycja"),
                Mecz.id_sezon,
                zespol.label("id_zespol"),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
        )
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
        return zapytanie.cte("wpisy_zawodnikow")

    def _statystyki(self, filtry: FiltryZawodnikow) -> CTE:
        wpisy = self._wpisy(filtry)
        zapytanie = (
            select(
                wpisy.c.id_zawodnik,
                func.array_agg(distinct(wpisy.c.pozycja)).label("pozycje"),
                func.array_agg(distinct(ZespolSezon.nazwa)).label("druzyny"),
            )
            .select_from(wpisy)
            .outerjoin(
                ZespolSezon,
                and_(
                    ZespolSezon.id_zespol == wpisy.c.id_zespol,
                    ZespolSezon.id_sezon == wpisy.c.id_sezon,
                ),
            )
            .group_by(wpisy.c.id_zawodnik)
        )
        if filtry.druzyna:
            identyfikatory = select(ZespolSezon.id_zespol).where(
                ZespolSezon.nazwa.icontains(filtry.druzyna, autoescape=True)
            )
            zapytanie = zapytanie.where(wpisy.c.id_zespol.in_(identyfikatory))
        if filtry.pozycja:
            zapytanie = zapytanie.where(wpisy.c.pozycja == filtry.pozycja)
        return zapytanie.cte("statystyki_zawodnikow")

    def _ostatnie_pomiary(self, pole: InstrumentedAttribute[Decimal | None], etykieta: str) -> CTE:
        return (
            select(SkladSezonowy.id_zawodnik, pole.label(etykieta))
            .join(ZespolSezon, ZespolSezon.id == SkladSezonowy.id_zespol_sezon)
            .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
            .where(pole.is_not(None))
            .distinct(SkladSezonowy.id_zawodnik)
            .order_by(
                SkladSezonowy.id_zawodnik,
                Sezon.rok_rozpoczecia.desc().nulls_last(),
                Sezon.id.desc(),
                ZespolSezon.id.desc(),
            )
            .cte(f"ostatni_{etykieta}")
        )

    def _zapytanie(self, filtry: FiltryZawodnikow) -> Select[tuple[object, ...]]:
        statystyki = self._statystyki(filtry)
        wzrosty = self._ostatnie_pomiary(SkladSezonowy.wzrost, "wzrost")
        wagi = self._ostatnie_pomiary(SkladSezonowy.waga, "waga")
        rocznik = extract("year", Zawodnik.data_urodzenia).cast(Integer)
        zapytanie = (
            select(
                Zawodnik.id,
                Zawodnik.imie,
                Zawodnik.nazwisko,
                rocznik.label("rocznik"),
                statystyki.c.pozycje,
                statystyki.c.druzyny,
                wzrosty.c.wzrost,
                wagi.c.waga,
            )
            .outerjoin(statystyki, statystyki.c.id_zawodnik == Zawodnik.id)
            .outerjoin(wzrosty, wzrosty.c.id_zawodnik == Zawodnik.id)
            .outerjoin(wagi, wagi.c.id_zawodnik == Zawodnik.id)
        )
        if filtry.id_sezon is not None or filtry.rozgrywki or filtry.druzyna or filtry.pozycja:
            zapytanie = zapytanie.where(statystyki.c.id_zawodnik.is_not(None))
        if filtry.rocznik is not None:
            zapytanie = zapytanie.where(rocznik == filtry.rocznik)
        if filtry.szukaj:
            for slowo in filtry.szukaj.split():
                zapytanie = zapytanie.where(
                    or_(
                        Zawodnik.imie.icontains(slowo, autoescape=True),
                        Zawodnik.nazwisko.icontains(slowo, autoescape=True),
                    )
                )
        return cast(Select[tuple[object, ...]], zapytanie)
