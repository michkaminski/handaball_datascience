from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Integer, TextClause, bindparam

from handball.infrastructure.repositories.attendance_sql import (
    BRAMKI_GOSCIA,
    BRAMKI_GOSPODARZA,
    DZIEN_TYGODNIA,
    FAZA,
    FINALY,
    GODZINA,
    GOSC_ID,
    GOSPODARZ_ID,
    JOINY_DRUZYN,
    JOINY_FAZ,
    MIESIAC,
    NAZWA_GOSCIA,
    NAZWA_GOSPODARZA,
    POLA_REKORDU,
    TERMIN,
    WARUNKI_MECZU,
    ZAKRES_MECZOW,
    ZNANE,
    ZNANE_BEZ_ZER,
    zapytanie,
)

ZAKRES_Z_FAZAMI = f"{ZAKRES_MECZOW} {JOINY_FAZ}"
KOLEJNOSC_REKORDOW = "widzowie DESC, termin DESC NULLS LAST, id_mecz DESC"
PARAMETR_LIMITU = bindparam("limit", type_=Integer())


@dataclass(frozen=True)
class ZestawRozszerzonychZapytan:
    przeciwnicy: TextClause
    miesiace: TextClause
    dni: TextClause
    godziny: TextClause
    rundy: TextClause
    heatmapa: TextClause
    rekordy_sezonow: TextClause
    rekordy_klubow: TextClause
    rekordy_hal: TextClause
    rekordy_finalow: TextClause
    rekordy_par: TextClause
    probka: TextClause


def kolumny_agregatu(znane: str) -> str:
    return f"""
        COUNT(*)::int AS rozegrane,
        (COUNT(*) FILTER (WHERE {znane}))::int AS znane,
        COALESCE(SUM(m.widzowie) FILTER (WHERE {znane}), 0)::bigint AS suma,
        (MAX(m.widzowie) FILTER (WHERE {znane}))::int AS maksimum
    """


def _grupa_kalendarza(znane: str, klucz: str, kolejnosc: str) -> TextClause:
    return zapytanie(
        f"""
        SELECT {klucz} AS klucz, {kolumny_agregatu(znane)}
        FROM {ZAKRES_Z_FAZAMI}
        WHERE {WARUNKI_MECZU}
          AND ({klucz}) IS NOT NULL
        GROUP BY 1
        ORDER BY {kolejnosc}
        """
    )


def _rekordy_najlepsze_w_grupie(
    znane: str, partycja: str, warunek: str, kolejnosc: str, z_limitem: bool
) -> TextClause:
    limit = "LIMIT :limit" if z_limitem else ""
    return zapytanie(
        f"""
        SELECT id_mecz, termin, sezon, rozgrywki, gospodarz, gosc,
               bramki_gospodarza, bramki_goscia, hala, widzowie
        FROM (
            SELECT
                {POLA_REKORDU},
                s.rok_rozpoczecia AS rok_sezonu,
                ROW_NUMBER() OVER (
                    PARTITION BY {partycja}
                    ORDER BY m.widzowie DESC, {TERMIN} DESC NULLS LAST, m.id DESC
                ) AS pozycja
            FROM {ZAKRES_MECZOW} {JOINY_DRUZYN}
            WHERE {WARUNKI_MECZU}
              AND {znane}
              {warunek}
        ) najlepsze
        WHERE pozycja = 1
        ORDER BY {kolejnosc}
        {limit}
        """,
        *((PARAMETR_LIMITU,) if z_limitem else ()),
    )


def zestaw_rozszerzony(znane: str) -> ZestawRozszerzonychZapytan:
    para_min = f"LEAST(({GOSPODARZ_ID}), ({GOSC_ID}))"
    para_max = f"GREATEST(({GOSPODARZ_ID}), ({GOSC_ID}))"
    return ZestawRozszerzonychZapytan(
        przeciwnicy=zapytanie(
            f"""
            SELECT
                {GOSC_ID} AS id_zespol,
                COALESCE(
                    (ARRAY_AGG(
                        {NAZWA_GOSCIA}
                        ORDER BY s.rok_rozpoczecia DESC NULLS LAST, m.id_sezon DESC
                    ) FILTER (WHERE {NAZWA_GOSCIA} IS NOT NULL))[1],
                    '—'
                ) AS nazwa,
                {kolumny_agregatu(znane)}
            FROM {ZAKRES_MECZOW} {JOINY_DRUZYN}
            WHERE {WARUNKI_MECZU}
              AND ({GOSC_ID}) IS NOT NULL
            GROUP BY 1
            HAVING COUNT(*) FILTER (WHERE {znane}) > 0
            """
        ),
        miesiace=_grupa_kalendarza(znane, MIESIAC, "1"),
        dni=_grupa_kalendarza(znane, DZIEN_TYGODNIA, "1"),
        godziny=_grupa_kalendarza(znane, GODZINA, "1"),
        rundy=_grupa_kalendarza(znane, FAZA, "znane DESC, 1"),
        heatmapa=zapytanie(
            f"""
            SELECT
                {DZIEN_TYGODNIA} AS dzien,
                {GODZINA} AS godzina,
                {kolumny_agregatu(znane)}
            FROM {ZAKRES_MECZOW}
            WHERE {WARUNKI_MECZU}
              AND ({DZIEN_TYGODNIA}) IS NOT NULL
              AND ({GODZINA}) IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1, 2
            """
        ),
        rekordy_sezonow=_rekordy_najlepsze_w_grupie(
            znane, "m.id_sezon", "", "rok_sezonu DESC NULLS LAST, id_mecz DESC", False
        ),
        rekordy_klubow=_rekordy_najlepsze_w_grupie(
            znane,
            f"({GOSPODARZ_ID})",
            f"AND ({GOSPODARZ_ID}) IS NOT NULL",
            KOLEJNOSC_REKORDOW,
            True,
        ),
        rekordy_hal=_rekordy_najlepsze_w_grupie(
            znane, "m.id_hala", "AND m.id_hala IS NOT NULL", KOLEJNOSC_REKORDOW, True
        ),
        rekordy_finalow=zapytanie(
            f"""
            SELECT {POLA_REKORDU}
            FROM {ZAKRES_Z_FAZAMI} {JOINY_DRUZYN}
            WHERE {WARUNKI_MECZU}
              AND {znane}
              AND {FINALY}
            ORDER BY m.widzowie DESC, {TERMIN} DESC NULLS LAST, m.id DESC
            LIMIT :limit
            """,
            PARAMETR_LIMITU,
        ),
        rekordy_par=_rekordy_najlepsze_w_grupie(
            znane,
            f"{para_min}, {para_max}",
            f"AND ({GOSPODARZ_ID}) IS NOT NULL AND ({GOSC_ID}) IS NOT NULL",
            KOLEJNOSC_REKORDOW,
            True,
        ),
        probka=zapytanie(
            f"""
            SELECT
                m.id AS id_mecz,
                {TERMIN} AS termin,
                {DZIEN_TYGODNIA} AS dzien_tygodnia,
                {GODZINA} AS godzina,
                {MIESIAC} AS miesiac,
                ({GOSPODARZ_ID}) AS id_gospodarza,
                ({GOSC_ID}) AS id_goscia,
                COALESCE({NAZWA_GOSPODARZA}, '—') AS gospodarz,
                COALESCE({NAZWA_GOSCIA}, '—') AS gosc,
                {BRAMKI_GOSPODARZA} AS bramki_gospodarza,
                {BRAMKI_GOSCIA} AS bramki_goscia,
                m.widzowie AS widzowie
            FROM {ZAKRES_MECZOW} {JOINY_DRUZYN}
            WHERE {WARUNKI_MECZU}
              AND {znane}
            ORDER BY {TERMIN} DESC NULLS LAST, m.id DESC
            LIMIT :limit
            """,
            PARAMETR_LIMITU,
        ),
    )


ZESTAWY_ROZSZERZONE = {False: zestaw_rozszerzony(ZNANE), True: zestaw_rozszerzony(ZNANE_BEZ_ZER)}
