from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, bindparam, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.infrastructure.repositories.attendance_sql import (
    BRAMKI_GOSCIA,
    BRAMKI_GOSPODARZA,
    GOSC_ID,
    GOSPODARZ_ID,
    TERMIN,
)
from maf.records import MatchRecord

MECZE_MAF_SQL = text(
    f"""
    SELECT
        m.id AS id_mecz,
        {TERMIN} AS termin,
        s.nazwa AS sezon,
        COALESCE(s.rok_rozpoczecia, 0) AS rok_sezonu,
        r.nazwa AS rozgrywki,
        ({GOSPODARZ_ID}) AS id_gospodarz,
        COALESCE(NULLIF(btrim(zg.nazwa), ''), NULLIF(btrim(z1.nazwa), ''), '—') AS gospodarz,
        ({GOSC_ID}) AS id_gosc,
        COALESCE(NULLIF(btrim(zw.nazwa), ''), NULLIF(btrim(z2.nazwa), ''), '—') AS gosc,
        m.id_hala AS id_hala,
        NULLIF(
            concat_ws(', ', NULLIF(btrim(h.nazwa), ''), NULLIF(btrim(h.miasto), '')), ''
        ) AS hala,
        m.widzowie AS widzowie,
        h.pojemnosc AS pojemnosc,
        NULLIF(
            concat_ws(' · ', NULLIF(btrim(ru.nazwa), ''), NULLIF(btrim(k.nazwa), '')), ''
        ) AS faza,
        {BRAMKI_GOSPODARZA} AS bramki_gospodarza,
        {BRAMKI_GOSCIA} AS bramki_goscia
    FROM public.mecze m
    JOIN public.rozgrywki r ON r.id = m.id_rozgrywki
    JOIN public.sezony s ON s.id = m.id_sezon
    LEFT JOIN public.hale h ON h.id = m.id_hala
    LEFT JOIN public.kolejki k ON k.id = m.id_kolejka
    LEFT JOIN public.rundy ru ON ru.id = k.id_runda
    LEFT JOIN public.zespoly_sezony zg
        ON zg.id_zespol = ({GOSPODARZ_ID}) AND zg.id_sezon = m.id_sezon
    LEFT JOIN public.zespoly_sezony zw
        ON zw.id_zespol = ({GOSC_ID}) AND zw.id_sezon = m.id_sezon
    LEFT JOIN public.zespoly z1 ON z1.id = ({GOSPODARZ_ID})
    LEFT JOIN public.zespoly z2 ON z2.id = ({GOSC_ID})
    WHERE m.wynik_gosp_full IS NOT NULL
      AND m.wynik_gosc_full IS NOT NULL
      AND m.wynik_gosp_full >= 0
      AND m.wynik_gosc_full >= 0
      AND m.wycofany IS NOT TRUE
      AND m.id_zespol_walkower IS NULL
      AND m.id_zespol_gosp IS NOT NULL
      AND m.id_zespol_gosc IS NOT NULL
      AND r.plec = :plec
    ORDER BY m.id
    """
).bindparams(bindparam("plec", type_=String()))

NAZWY_KLUBOW_SQL = text(
    """
    SELECT DISTINCT ON (zs.id_zespol) zs.id_zespol, btrim(zs.nazwa) AS nazwa
    FROM public.zespoly_sezony zs
    JOIN public.sezony s ON s.id = zs.id_sezon
    WHERE NULLIF(btrim(zs.nazwa), '') IS NOT NULL
    ORDER BY zs.id_zespol, s.rok_rozpoczecia DESC NULLS LAST, zs.id DESC
    """
)


class MeczeMafSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_mecze(self, plec: str) -> list[MatchRecord]:
        try:
            wiersze = self._sesja.execute(MECZE_MAF_SQL, {"plec": plec}).mappings().all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów do modelu MAF.") from wyjatek
        return [self._rekord(wiersz) for wiersz in wiersze]

    def pobierz_nazwy_klubow(self) -> dict[int, str]:
        try:
            wiersze = self._sesja.execute(NAZWY_KLUBOW_SQL).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać nazw klubów.") from wyjatek
        return {int(wiersz[0]): str(wiersz[1]) for wiersz in wiersze}

    def _rekord(self, wiersz: object) -> MatchRecord:
        dane = dict(wiersz)  # type: ignore[call-overload]
        termin = dane["termin"]
        return MatchRecord(
            match_id=int(dane["id_mecz"]),
            kickoff=termin if isinstance(termin, datetime) else None,
            season_key=str(dane["sezon"]),
            season_order=int(dane["rok_sezonu"]),
            competition_key=str(dane["rozgrywki"]),
            competition_name=str(dane["rozgrywki"]),
            host_id=int(dane["id_gospodarz"]),
            host_name=str(dane["gospodarz"]),
            opponent_id=int(dane["id_gosc"]),
            opponent_name=str(dane["gosc"]),
            venue_id=int(dane["id_hala"]) if dane["id_hala"] is not None else None,
            venue_name=dane["hala"],
            spectators=int(dane["widzowie"]) if dane["widzowie"] is not None else None,
            capacity=int(dane["pojemnosc"]) if dane["pojemnosc"] is not None else None,
            phase=dane["faza"],
            host_goals=dane["bramki_gospodarza"],
            opponent_goals=dane["bramki_goscia"],
        )
