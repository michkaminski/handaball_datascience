from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych
from handball.domain.matches import DaneMeczu
from handball.domain.news import (
    MeczAktualnosci,
    RozgrywkiAktualnosci,
    SezonAktualnosci,
    StrzelecAktualnosci,
    WystepAktualnosci,
)
from handball.infrastructure.database.match_sides import StronyMeczuSql
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.teams import ZespolSezon


class AktualnosciSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_biezacy_sezon(self) -> SezonAktualnosci | None:
        try:
            rozegrany = select(Mecz.id).where(
                Mecz.id_sezon == Sezon.id, *self._warunki_rozegranego()
            )
            wiersz = self._sesja.execute(
                select(Sezon.id, Sezon.nazwa)
                .where(rozegrany.exists())
                .order_by(Sezon.rok_rozpoczecia.desc().nulls_last(), Sezon.id.desc())
                .limit(1)
            ).first()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać bieżącego sezonu.") from wyjatek
        return SezonAktualnosci(wiersz[0], wiersz[1]) if wiersz else None

    def pobierz_rozgrywki(self, id_sezon: int) -> tuple[RozgrywkiAktualnosci, ...]:
        try:
            wiersze = self._sesja.execute(
                select(Rozgrywki.id, Rozgrywki.nazwa, Rozgrywki.plec)
                .where(Rozgrywki.id_sezon == id_sezon)
                .order_by(Rozgrywki.id)
            ).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać rozgrywek sezonu.") from wyjatek
        return tuple(RozgrywkiAktualnosci(id_r, nazwa, plec) for id_r, nazwa, plec in wiersze)

    def pobierz_rozegrane_mecze(self, id_sezon: int) -> tuple[MeczAktualnosci, ...]:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        try:
            wiersze = self._sesja.execute(
                select(
                    Mecz.id,
                    termin,
                    Mecz.id_rozgrywki,
                    gospodarz.nazwa,
                    gosc.nazwa,
                    Mecz.wynik_gosp_full,
                    Mecz.wynik_gosc_full,
                    Mecz.zamiana,
                )
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
                .where(Mecz.id_sezon == id_sezon, *self._warunki_rozegranego())
                .order_by(termin.desc().nulls_last(), Mecz.id.desc())
            ).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać rozegranych meczów.") from wyjatek
        return tuple(
            MeczAktualnosci(
                id_mecz=id_mecz,
                termin=kiedy,
                id_rozgrywki=id_rozgrywki,
                gospodarz=nazwa_gosp,
                gosc=nazwa_gosc,
                mecz=DaneMeczu(
                    id=id_mecz,
                    wynik_gosp_full=wynik_gosp,
                    wynik_gosc_full=wynik_gosc,
                    zamiana=zamiana,
                ),
            )
            for (
                id_mecz,
                kiedy,
                id_rozgrywki,
                nazwa_gosp,
                nazwa_gosc,
                wynik_gosp,
                wynik_gosc,
                zamiana,
            ) in wiersze
        )

    def pobierz_strzelcow(
        self, id_sezon: int, limit_na_rozgrywki: int
    ) -> tuple[StrzelecAktualnosci, ...]:
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        druzyna = aliased(ZespolSezon)
        suma = func.sum(MeczZawodnik.bramki)
        mecze = func.count(func.distinct(MeczZawodnik.id_mecz))
        zestawienie = (
            select(
                Mecz.id_rozgrywki.label("id_rozgrywki"),
                MeczZawodnik.id_zawodnik.label("id_zawodnik"),
                self._nazwa_zawodnika().label("zawodnik"),
                func.array_agg(aggregate_order_by(druzyna.nazwa, termin.desc()))[1].label(
                    "druzyna"
                ),
                mecze.label("mecze"),
                suma.label("bramki"),
                func.row_number()
                .over(partition_by=Mecz.id_rozgrywki, order_by=(suma.desc(), mecze.asc()))
                .label("pozycja"),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .join(Zawodnik, Zawodnik.id == MeczZawodnik.id_zawodnik)
            .join(druzyna, self._warunek_druzyny(druzyna), isouter=True)
            .where(
                Mecz.id_sezon == id_sezon,
                MeczZawodnik.bramki.is_not(None),
                MeczZawodnik.strona.in_(("gosp", "gosc")),
            )
            .group_by(Mecz.id_rozgrywki, MeczZawodnik.id_zawodnik, Zawodnik.imie, Zawodnik.nazwisko)
            .subquery()
        )
        try:
            wiersze = self._sesja.execute(
                select(
                    zestawienie.c.id_rozgrywki,
                    zestawienie.c.id_zawodnik,
                    zestawienie.c.zawodnik,
                    zestawienie.c.druzyna,
                    zestawienie.c.mecze,
                    zestawienie.c.bramki,
                )
                .where(zestawienie.c.pozycja <= limit_na_rozgrywki, zestawienie.c.bramki > 0)
                .order_by(zestawienie.c.id_rozgrywki, zestawienie.c.pozycja)
            ).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać strzelców sezonu.") from wyjatek
        return tuple(
            StrzelecAktualnosci(id_r, id_z, nazwa, klub, int(liczba), int(bramki))
            for id_r, id_z, nazwa, klub, liczba, bramki in wiersze
        )

    def pobierz_najlepsze_wystepy(self, id_sezon: int, limit: int) -> tuple[WystepAktualnosci, ...]:
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        druzyna = aliased(ZespolSezon)
        suma = func.sum(MeczZawodnik.bramki)
        try:
            wiersze = self._sesja.execute(
                select(
                    Mecz.id_rozgrywki,
                    Mecz.id,
                    termin,
                    MeczZawodnik.id_zawodnik,
                    self._nazwa_zawodnika(),
                    func.min(druzyna.nazwa),
                    suma,
                )
                .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
                .join(Zawodnik, Zawodnik.id == MeczZawodnik.id_zawodnik)
                .join(druzyna, self._warunek_druzyny(druzyna), isouter=True)
                .where(
                    Mecz.id_sezon == id_sezon,
                    MeczZawodnik.bramki.is_not(None),
                    MeczZawodnik.strona.in_(("gosp", "gosc")),
                )
                .group_by(
                    Mecz.id_rozgrywki,
                    Mecz.id,
                    termin,
                    MeczZawodnik.id_zawodnik,
                    Zawodnik.imie,
                    Zawodnik.nazwisko,
                )
                .order_by(suma.desc(), termin.desc().nulls_last(), Mecz.id.desc())
                .limit(limit)
            ).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać najlepszych występów.") from wyjatek
        return tuple(
            WystepAktualnosci(id_r, id_m, kiedy, id_z, nazwa, klub, int(bramki))
            for id_r, id_m, kiedy, id_z, nazwa, klub, bramki in wiersze
        )

    @staticmethod
    def _warunki_rozegranego() -> tuple[Any, ...]:
        return (
            Mecz.wynik_gosp_full.is_not(None),
            Mecz.wynik_gosc_full.is_not(None),
            Mecz.wycofany.is_not(True),
            Mecz.id_zespol_walkower.is_(None),
        )

    @staticmethod
    def _warunek_druzyny(druzyna: type[ZespolSezon]) -> Any:
        id_zespolu = StronyMeczuSql.zespol(MeczZawodnik.strona)
        return (druzyna.id_zespol == id_zespolu) & (druzyna.id_sezon == Mecz.id_sezon)

    @staticmethod
    def _nazwa_zawodnika() -> Any:
        return func.trim(
            func.concat(
                func.coalesce(Zawodnik.imie, ""),
                " ",
                func.trim(func.coalesce(Zawodnik.nazwisko, "")),
            )
        )
