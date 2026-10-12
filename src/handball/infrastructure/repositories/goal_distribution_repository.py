from __future__ import annotations

from sqlalchemy import Integer, String, bindparam, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.errors import BladOdczytuDanych
from handball.domain.goal_distribution import (
    FiltryRozkladuBramek,
    LiniaWyniku,
    MeczRozkladu,
    OpcjaFiltrow,
    OpcjeFiltrowRozkladu,
    RodzajSerii,
)

WARUNKI_MECZU = """
    m.wynik_gosp_full IS NOT NULL
    AND m.wynik_gosc_full IS NOT NULL
    AND m.wynik_gosp_full >= 0
    AND m.wynik_gosc_full >= 0
    AND m.wycofany IS NOT TRUE
    AND m.id_zespol_walkower IS NULL
    AND (CAST(:id_sezon AS INTEGER) IS NULL OR m.id_sezon = :id_sezon)
    AND (CAST(:rozgrywki AS TEXT) IS NULL OR r.nazwa = :rozgrywki)
    AND (CAST(:plec AS TEXT) IS NULL OR r.plec = :plec)
"""

PARAMETRY_FILTROW = (
    bindparam("id_sezon", type_=Integer()),
    bindparam("rozgrywki", type_=String()),
    bindparam("plec", type_=String()),
)

WARUNEK_SERII = {
    RodzajSerii.SUMA: "m.wynik_gosp_full + m.wynik_gosc_full = :bramki",
    RodzajSerii.GOSPODARZE: "m.wynik_gosp_full = :bramki",
    RodzajSerii.GOSCIE: "m.wynik_gosc_full = :bramki",
}

WYNIKI_SQL = text(
    f"""
    SELECT
        m.wynik_gosp_full AS gospodarz,
        m.wynik_gosc_full AS gosc,
        COUNT(*)::int AS mecze
    FROM public.mecze m
    JOIN public.rozgrywki r ON r.id = m.id_rozgrywki
    WHERE {WARUNKI_MECZU}
    GROUP BY m.wynik_gosp_full, m.wynik_gosc_full
    """
).bindparams(*PARAMETRY_FILTROW)

MECZE_SQL = {
    rodzaj: text(
        f"""
        SELECT
            id_mecz, termin, sezon, rozgrywki, gospodarz, gosc,
            bramki_gospodarza, bramki_goscia
        FROM (
            SELECT DISTINCT ON (m.id)
                m.id AS id_mecz,
                m.data_faktyczna AS termin,
                COALESCE(NULLIF(btrim(s.nazwa), ''), '—') AS sezon,
                COALESCE(NULLIF(btrim(r.nazwa), ''), '—') AS rozgrywki,
                COALESCE(NULLIF(btrim(gospodarz.nazwa), ''), '—') AS gospodarz,
                COALESCE(NULLIF(btrim(gosc.nazwa), ''), '—') AS gosc,
                m.wynik_gosp_full AS bramki_gospodarza,
                m.wynik_gosc_full AS bramki_goscia
            FROM public.mecze m
            JOIN public.rozgrywki r ON r.id = m.id_rozgrywki
            LEFT JOIN public.sezony s ON s.id = m.id_sezon
            LEFT JOIN public.zespoly_sezony gospodarz
                ON gospodarz.id_zespol = m.id_zespol_gosp
               AND gospodarz.id_sezon = m.id_sezon
            LEFT JOIN public.zespoly_sezony gosc
                ON gosc.id_zespol = m.id_zespol_gosc
               AND gosc.id_sezon = m.id_sezon
            WHERE {WARUNKI_MECZU}
              AND {WARUNEK_SERII[rodzaj]}
            ORDER BY m.id
        ) mecze
        ORDER BY termin DESC NULLS LAST, id_mecz DESC
        """
    ).bindparams(*PARAMETRY_FILTROW, bindparam("bramki", type_=Integer()))
    for rodzaj in RodzajSerii
}

SEZONY_SQL = text(
    """
    SELECT id, nazwa
    FROM public.sezony
    ORDER BY rok_rozpoczecia DESC NULLS LAST, id DESC
    """
)

ROZGRYWKI_SQL = text(
    """
    SELECT DISTINCT nazwa
    FROM public.rozgrywki
    WHERE nazwa IS NOT NULL AND btrim(nazwa) <> ''
    ORDER BY nazwa
    """
)


class RozkladBramekSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_opcje(self) -> OpcjeFiltrowRozkladu:
        try:
            sezony = self._sesja.execute(SEZONY_SQL).all()
            rozgrywki = self._sesja.execute(ROZGRYWKI_SQL).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                f"Nie udało się odczytać filtrów rozkładu bramek: {wyjatek}"
            ) from wyjatek
        return OpcjeFiltrowRozkladu(
            sezony=tuple(OpcjaFiltrow(str(wiersz[0]), str(wiersz[1])) for wiersz in sezony),
            rozgrywki=tuple(OpcjaFiltrow(str(wiersz[0]), str(wiersz[0])) for wiersz in rozgrywki),
        )

    def pobierz_wyniki(self, filtry: FiltryRozkladuBramek) -> tuple[LiniaWyniku, ...]:
        try:
            wiersze = (
                self._sesja.execute(
                    WYNIKI_SQL,
                    {
                        "id_sezon": filtry.id_sezon,
                        "rozgrywki": filtry.rozgrywki,
                        "plec": filtry.plec,
                    },
                )
                .mappings()
                .all()
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                f"Nie udało się odczytać rozkładu bramek: {wyjatek}"
            ) from wyjatek
        return tuple(
            LiniaWyniku(int(wiersz["gospodarz"]), int(wiersz["gosc"]), int(wiersz["mecze"]))
            for wiersz in wiersze
        )

    def pobierz_mecze(
        self, filtry: FiltryRozkladuBramek, rodzaj: RodzajSerii, bramki: int
    ) -> tuple[MeczRozkladu, ...]:
        try:
            wiersze = (
                self._sesja.execute(
                    MECZE_SQL[rodzaj],
                    {
                        "id_sezon": filtry.id_sezon,
                        "rozgrywki": filtry.rozgrywki,
                        "plec": filtry.plec,
                        "bramki": bramki,
                    },
                )
                .mappings()
                .all()
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                f"Nie udało się odczytać meczów rozkładu bramek: {wyjatek}"
            ) from wyjatek
        return tuple(
            MeczRozkladu(
                id_mecz=int(wiersz["id_mecz"]),
                termin=wiersz["termin"],
                sezon=str(wiersz["sezon"]),
                rozgrywki=str(wiersz["rozgrywki"]),
                gospodarz=str(wiersz["gospodarz"]),
                gosc=str(wiersz["gosc"]),
                bramki_gospodarza=int(wiersz["bramki_gospodarza"]),
                bramki_goscia=int(wiersz["bramki_goscia"]),
            )
            for wiersz in wiersze
        )
