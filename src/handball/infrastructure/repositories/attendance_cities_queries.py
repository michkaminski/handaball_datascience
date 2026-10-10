from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import TextClause

from handball.infrastructure.repositories.attendance_extended_queries import kolumny_agregatu
from handball.infrastructure.repositories.attendance_sql import (
    GOSPODARZ_ID,
    JOINY_DRUZYN,
    NAZWA_GOSPODARZA,
    WARUNKI_MECZU,
    ZAKRES_MECZOW,
    ZNANE,
    ZNANE_BEZ_ZER,
    zapytanie,
)

MIASTO_ETYKIETA = r"NULLIF(btrim(regexp_replace(zg.miasto, '\s+', ' ', 'g')), '')"
MIASTO_KLUCZ = f"lower({MIASTO_ETYKIETA})"
ETYKIETA_MIASTA_NAJCZESTSZA = f"(mode() WITHIN GROUP (ORDER BY {MIASTO_ETYKIETA}))"
ROZGRYWKI_MECZU = "COALESCE(NULLIF(btrim(r.nazwa), ''), '—')"
ZAKRES_Z_DRUZYNAMI = f"{ZAKRES_MECZOW} {JOINY_DRUZYN}"


@dataclass(frozen=True)
class ZestawZapytanMiast:
    miasta: TextClause
    wklady: TextClause
    sezony: TextClause
    rozgrywki: TextClause
    hale: TextClause
    bez_miasta: TextClause


def kolumny_rozkladu(znane: str) -> str:
    return f"""
        (percentile_cont(0.5) WITHIN GROUP (ORDER BY m.widzowie)
            FILTER (WHERE {znane}))::float8 AS mediana,
        (mode() WITHIN GROUP (ORDER BY m.widzowie) FILTER (WHERE {znane}))::int AS dominanta,
        (MIN(m.widzowie) FILTER (WHERE {znane}))::int AS minimum
    """


def _zapytanie_miasta(
    znane: str,
    wybor: str,
    grupowanie: str,
    kolejnosc: str,
    warunek_dodatkowy: str = "TRUE",
) -> TextClause:
    return zapytanie(
        f"""
        SELECT {wybor}
        FROM {ZAKRES_Z_DRUZYNAMI}
        WHERE {WARUNKI_MECZU}
          AND {MIASTO_KLUCZ} IS NOT NULL
          AND {warunek_dodatkowy}
        GROUP BY {grupowanie}
        HAVING COUNT(*) FILTER (WHERE {znane}) > 0
        ORDER BY {kolejnosc}
        """
    )


def _miary(znane: str) -> str:
    return f"{kolumny_agregatu(znane)}, {kolumny_rozkladu(znane)}"


def _miasta(znane: str) -> TextClause:
    return _zapytanie_miasta(
        znane,
        f"""
            {MIASTO_KLUCZ} AS klucz,
            {ETYKIETA_MIASTA_NAJCZESTSZA} AS miasto,
            {_miary(znane)},
            (COUNT(DISTINCT ({GOSPODARZ_ID})) FILTER (WHERE {znane}))::int AS liczba_klubow,
            (COUNT(DISTINCT {ROZGRYWKI_MECZU}) FILTER (WHERE {znane}))::int
                AS liczba_rozgrywek
        """,
        "1",
        "suma DESC, klucz",
    )


def _wklady(znane: str) -> TextClause:
    return _zapytanie_miasta(
        znane,
        f"""
            {MIASTO_KLUCZ} AS klucz,
            {GOSPODARZ_ID} AS id_zespol,
            {ROZGRYWKI_MECZU} AS rozgrywki,
            {ETYKIETA_MIASTA_NAJCZESTSZA} AS miasto,
            COALESCE(
                (ARRAY_AGG(
                    {NAZWA_GOSPODARZA}
                    ORDER BY s.rok_rozpoczecia DESC NULLS LAST, m.id_sezon DESC
                ) FILTER (WHERE {NAZWA_GOSPODARZA} IS NOT NULL))[1],
                '—'
            ) AS klub,
            {kolumny_agregatu(znane)}
        """,
        "1, 2, 3",
        "suma DESC, klucz, klub, rozgrywki",
        f"({GOSPODARZ_ID}) IS NOT NULL",
    )


def _sezony(znane: str) -> TextClause:
    return _zapytanie_miasta(
        znane,
        f"""
            {MIASTO_KLUCZ} AS klucz,
            m.id_sezon AS id_sezon,
            COALESCE(NULLIF(btrim(s.nazwa), ''), '—') AS sezon,
            s.rok_rozpoczecia AS rok_poczatku,
            {_miary(znane)}
        """,
        "1, 2, 3, 4",
        "klucz, rok_poczatku NULLS FIRST, id_sezon",
    )


def _rozgrywki(znane: str) -> TextClause:
    return _zapytanie_miasta(
        znane,
        f"""
            {MIASTO_KLUCZ} AS klucz,
            {ROZGRYWKI_MECZU} AS rozgrywki,
            {_miary(znane)},
            (COUNT(DISTINCT ({GOSPODARZ_ID})) FILTER (WHERE {znane}))::int AS liczba_klubow
        """,
        "1, 2",
        "klucz, suma DESC, rozgrywki",
    )


def _hale(znane: str) -> TextClause:
    return _zapytanie_miasta(
        znane,
        f"""
            {MIASTO_KLUCZ} AS klucz,
            h.id AS id_hala,
            COALESCE(NULLIF(btrim(h.nazwa), ''), '—') AS hala,
            NULLIF(btrim(h.miasto), '') AS miasto_hali,
            {_miary(znane)}
        """,
        "1, 2, 3, 4",
        "klucz, suma DESC, hala, id_hala",
        "h.id IS NOT NULL",
    )


def _bez_miasta() -> TextClause:
    return zapytanie(
        f"""
        SELECT COUNT(*)::int AS rozegrane
        FROM {ZAKRES_Z_DRUZYNAMI}
        WHERE {WARUNKI_MECZU}
          AND {MIASTO_KLUCZ} IS NULL
        """
    )


def zestaw_miast(znane: str) -> ZestawZapytanMiast:
    return ZestawZapytanMiast(
        miasta=_miasta(znane),
        wklady=_wklady(znane),
        sezony=_sezony(znane),
        rozgrywki=_rozgrywki(znane),
        hale=_hale(znane),
        bez_miasta=_bez_miasta(),
    )


ZESTAWY_MIAST = {False: zestaw_miast(ZNANE), True: zestaw_miast(ZNANE_BEZ_ZER)}
