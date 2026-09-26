from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, literal_column, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu
from handball.domain.match_preview import (
    DruzynaZapowiedzi,
    MeczZapowiedzi,
    SezonKadry,
    WystepSezonuZawodnika,
    WystepZapowiedzi,
    ZawodnikKadry,
)
from handball.infrastructure.database.match_sides import StronyMeczuSql
from handball.infrastructure.database.models.competitions import Kolejka, Rozgrywki, Runda, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon
from handball.infrastructure.database.models.venues import Hala


class ZapowiedzMeczuSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_mecz(self, id_mecz: int) -> MeczZapowiedzi:
        gospodarz, gosc = aliased(ZespolSezon), aliased(ZespolSezon)
        zespol_gospodarza, zespol_goscia = aliased(Zespol), aliased(Zespol)
        zapytanie = (
            select(
                Mecz.id,
                Mecz.id_sezon,
                Sezon.nazwa,
                Mecz.id_rozgrywki,
                Rozgrywki.nazwa,
                Runda.nazwa,
                Kolejka.nazwa,
                Kolejka.nr,
                Mecz.data_faktyczna,
                Mecz.data_propozycji,
                Mecz.id_zespol_gosp,
                func.coalesce(gospodarz.nazwa, zespol_gospodarza.nazwa),
                Mecz.id_zespol_gosc,
                func.coalesce(gosc.nazwa, zespol_goscia.nazwa),
                Mecz.wynik_gosp_full,
                Mecz.wynik_gosc_full,
                Hala.nazwa,
                Hala.miasto,
                Mecz.zamiana,
                Mecz.wycofany,
                Mecz.id_zespol_walkower,
            )
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
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
            .where(Mecz.id == id_mecz)
        )
        try:
            w = self._sesja.execute(zapytanie).first()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczu do zapowiedzi.") from wyjatek
        if w is None:
            raise NieZnalezionoMeczu(f"Nie znaleziono meczu o id {id_mecz}")
        return MeczZapowiedzi(
            id_mecz=w[0],
            id_sezon=w[1],
            sezon=w[2],
            id_rozgrywki=w[3],
            rozgrywki=w[4],
            runda=w[5],
            kolejka=w[6],
            nr_kolejki=w[7],
            data_faktyczna=w[8],
            data_propozycji=w[9],
            kolumna_gosp=DruzynaZapowiedzi(w[10], w[11]),
            kolumna_gosc=DruzynaZapowiedzi(w[12], w[13]),
            wynik_gosp=w[14],
            wynik_gosc=w[15],
            hala=w[16],
            miasto=w[17],
            zamiana=bool(w[18]),
            wycofany=bool(w[19]),
            walkower=w[20] is not None,
        )

    def pobierz_wystepy(self, id_zespol: int, przed: datetime) -> list[WystepZapowiedzi]:
        rywal_sezon = aliased(ZespolSezon)
        rywal = aliased(Zespol)
        id_rywala = func.coalesce(func.nullif(Mecz.id_zespol_gosc, id_zespol), Mecz.id_zespol_gosp)
        zapytanie = (
            select(
                Mecz.id,
                Mecz.data_faktyczna,
                Mecz.id_sezon,
                Mecz.id_rozgrywki,
                Rozgrywki.nazwa,
                Mecz.id_zespol_gosp,
                Mecz.id_zespol_gosc,
                Mecz.wynik_gosp_full,
                Mecz.wynik_gosc_full,
                Mecz.zamiana,
                func.coalesce(rywal_sezon.nazwa, rywal.nazwa),
            )
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(
                rywal_sezon,
                (rywal_sezon.id_zespol == id_rywala) & (rywal_sezon.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(rywal, rywal.id == id_rywala, isouter=True)
            .where(
                or_(Mecz.id_zespol_gosp == id_zespol, Mecz.id_zespol_gosc == id_zespol),
                Mecz.data_faktyczna < przed,
                Mecz.wynik_gosp_full.is_not(None),
                Mecz.wynik_gosc_full.is_not(None),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .order_by(Mecz.data_faktyczna.desc(), Mecz.id.desc())
        )
        try:
            wiersze = self._sesja.execute(zapytanie).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów drużyny.") from wyjatek
        return [self._wystep(w, id_zespol) for w in wiersze]

    def pobierz_kadre(self, id_zespol: int, id_sezon: int, przed: datetime) -> list[ZawodnikKadry]:
        numery = func.array_remove(
            func.array_agg(func.distinct(MeczZawodnik.nr_koszulki)), literal_column("NULL")
        )
        zapytanie = (
            select(
                MeczZawodnik.id_zawodnik,
                func.max(func.coalesce(Zawodnik.imie, MeczZawodnik.imie)),
                func.max(func.coalesce(Zawodnik.nazwisko, MeczZawodnik.nazwisko)),
                numery,
                func.mode().within_group(MeczZawodnik.pozycja.asc()),
                func.count(func.distinct(MeczZawodnik.id_mecz)),
                func.coalesce(func.sum(MeczZawodnik.bramki), 0),
                func.count(func.distinct(MeczZawodnik.id_mecz)).filter(
                    MeczZawodnik.wyjscie.is_(True)
                ),
                func.max(Zawodnik.data_urodzenia),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .join(Zawodnik, Zawodnik.id == MeczZawodnik.id_zawodnik, isouter=True)
            .where(
                StronyMeczuSql.zespol(MeczZawodnik.strona) == id_zespol,
                Mecz.id_sezon == id_sezon,
                Mecz.data_faktyczna < przed,
                and_(Mecz.wynik_gosp_full.is_not(None), Mecz.wynik_gosc_full.is_not(None)),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .group_by(MeczZawodnik.id_zawodnik)
        )
        try:
            wiersze = self._sesja.execute(zapytanie).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać kadry drużyny.") from wyjatek
        return [
            ZawodnikKadry(
                id_zawodnik=w[0],
                imie=w[1],
                nazwisko=w[2],
                numery=tuple(sorted(int(n) for n in (w[3] or ()))),
                pozycja=w[4],
                mecze=int(w[5]),
                bramki=int(w[6]),
                zagrane=int(w[7]),
                data_urodzenia=w[8],
            )
            for w in wiersze
        ]

    def pobierz_wystepy_zawodnikow(
        self, id_zawodnikow: Sequence[int], id_sezon: int, przed: datetime
    ) -> list[WystepSezonuZawodnika]:
        if not id_zawodnikow:
            return []
        id_zespolu = StronyMeczuSql.zespol(MeczZawodnik.strona)
        zespol_sezon = aliased(ZespolSezon)
        zespol = aliased(Zespol)
        zapytanie = (
            select(
                MeczZawodnik.id_zawodnik,
                id_zespolu,
                func.max(func.coalesce(zespol_sezon.nazwa, zespol.nazwa)),
                Rozgrywki.nazwa,
                func.count(func.distinct(MeczZawodnik.id_mecz)),
                func.coalesce(func.sum(MeczZawodnik.bramki), 0),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .join(
                zespol_sezon,
                (zespol_sezon.id_zespol == id_zespolu) & (zespol_sezon.id_sezon == Mecz.id_sezon),
                isouter=True,
            )
            .join(zespol, zespol.id == id_zespolu, isouter=True)
            .where(
                MeczZawodnik.id_zawodnik.in_(sorted(set(id_zawodnikow))),
                Mecz.id_sezon == id_sezon,
                Mecz.data_faktyczna < przed,
                and_(Mecz.wynik_gosp_full.is_not(None), Mecz.wynik_gosc_full.is_not(None)),
                Mecz.wycofany.is_not(True),
                Mecz.id_zespol_walkower.is_(None),
            )
            .group_by(MeczZawodnik.id_zawodnik, id_zespolu, Rozgrywki.nazwa)
        )
        try:
            wiersze = self._sesja.execute(zapytanie).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                "Nie udało się odczytać poprzedniego sezonu kadry."
            ) from wyjatek
        return [
            WystepSezonuZawodnika(
                id_zawodnik=w[0],
                id_zespol=w[1],
                zespol=w[2],
                rozgrywki=w[3],
                mecze=int(w[4]),
                bramki=int(w[5]),
            )
            for w in wiersze
        ]

    def pobierz_poprzedni_sezon(self, id_sezon: int) -> SezonKadry | None:
        biezacy = aliased(Sezon)
        zapytanie = (
            select(Sezon.id, Sezon.nazwa)
            .join(biezacy, biezacy.id == id_sezon)
            .where(Sezon.rok_rozpoczecia < biezacy.rok_rozpoczecia)
            .order_by(Sezon.rok_rozpoczecia.desc(), Sezon.id.desc())
            .limit(1)
        )
        try:
            w = self._sesja.execute(zapytanie).first()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać poprzedniego sezonu.") from wyjatek
        return SezonKadry(w[0], w[1]) if w else None

    def _wystep(self, w: Any, id_zespol: int) -> WystepZapowiedzi:
        w_kolumnie_gospodarza = w[5] == id_zespol
        zamiana = bool(w[9])
        return WystepZapowiedzi(
            id_mecz=w[0],
            data=w[1],
            id_sezon=w[2],
            id_rozgrywki=w[3],
            rozgrywki=w[4],
            id_zespol=id_zespol,
            id_rywal=w[6] if w_kolumnie_gospodarza else w[5],
            rywal=w[10],
            u_siebie=w_kolumnie_gospodarza != zamiana,
            bramki_zdobyte=w[7] if w_kolumnie_gospodarza else w[8],
            bramki_stracone=w[8] if w_kolumnie_gospodarza else w[7],
        )
