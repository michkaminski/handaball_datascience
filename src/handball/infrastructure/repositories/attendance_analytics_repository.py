from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Integer, TextClause, bindparam, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.attendance_analytics import (
    FiltryFrekwencji,
    KlubFrekwencji,
    OpcjeFiltrowFrekwencji,
    PodsumowanieFrekwencji,
    SezonFrekwencji,
    SredniaKlubuSezonu,
)
from handball.domain.attendance_calendar import (
    DaneKalendarza,
    KomorkaKalendarza,
    WierszKalendarza,
)
from handball.domain.attendance_cities import DaneMiast
from handball.domain.attendance_opponents import PrzeciwnikFrekwencji
from handball.domain.attendance_records import RekordFrekwencji, RekordyRozszerzoneFrekwencji
from handball.domain.attendance_sample import MeczProbki
from handball.domain.errors import BladOdczytuDanych
from handball.domain.goal_distribution import OpcjaFiltrow
from handball.infrastructure.repositories.attendance_cities_queries import ZESTAWY_MIAST
from handball.infrastructure.repositories.attendance_city_rows import (
    hala_z_wiersza,
    miasto_z_wiersza,
    rozgrywki_z_wiersza,
    sezon_z_wiersza,
    wklad_z_wiersza,
)
from handball.infrastructure.repositories.attendance_extended_queries import (
    ZESTAWY_ROZSZERZONE,
)
from handball.infrastructure.repositories.attendance_rows import agregat_z_wiersza
from handball.infrastructure.repositories.attendance_sql import (
    GOSPODARZ_ID,
    JOINY_DRUZYN,
    NAZWA_GOSPODARZA,
    POLA_REKORDU,
    TERMIN,
    WARUNKI_MECZU,
    ZAKRES_MECZOW,
    ZNANE,
    ZNANE_BEZ_ZER,
    zapytanie,
)

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

KLUBY_SQL = text(
    """
    SELECT id_zespol, etykieta
    FROM (
        SELECT DISTINCT ON (zs.id_zespol)
            zs.id_zespol,
            btrim(zs.nazwa)
                || CASE WHEN zs.plec IN ('M', 'K') THEN ' (' || zs.plec || ')' ELSE '' END
                AS etykieta
        FROM public.zespoly_sezony zs
        LEFT JOIN public.sezony s ON s.id = zs.id_sezon
        WHERE zs.nazwa IS NOT NULL AND btrim(zs.nazwa) <> ''
        ORDER BY zs.id_zespol, s.rok_rozpoczecia DESC NULLS LAST, zs.id_sezon DESC
    ) kluby
    ORDER BY lower(etykieta), id_zespol
    """
)

HALE_SQL = text(
    """
    SELECT id, etykieta
    FROM (
        SELECT
            h.id,
            concat_ws(', ', NULLIF(btrim(h.nazwa), ''), NULLIF(btrim(h.miasto), '')) AS etykieta
        FROM public.hale h
    ) hale
    WHERE etykieta <> ''
    ORDER BY lower(etykieta), id
    """
)


def _kolumny_agregacji(znane: str) -> str:
    return f"""
        COUNT(*)::int AS rozegrane,
        (COUNT(*) FILTER (WHERE {znane}))::int AS znane,
        COALESCE(SUM(m.widzowie) FILTER (WHERE {znane}), 0)::bigint AS suma,
        (AVG(m.widzowie) FILTER (WHERE {znane}))::float8 AS srednia,
        (percentile_cont(0.5) WITHIN GROUP (ORDER BY m.widzowie)
            FILTER (WHERE {znane}))::float8 AS mediana,
        (percentile_cont(0.25) WITHIN GROUP (ORDER BY m.widzowie)
            FILTER (WHERE {znane}))::float8 AS q1,
        (percentile_cont(0.75) WITHIN GROUP (ORDER BY m.widzowie)
            FILTER (WHERE {znane}))::float8 AS q3,
        (MIN(m.widzowie) FILTER (WHERE {znane}))::int AS minimum,
        (MAX(m.widzowie) FILTER (WHERE {znane}))::int AS maksimum,
        (COUNT(*) FILTER (WHERE m.widzowie = 0))::int AS mecze_zero,
        COALESCE(
            SUM(m.widzowie) FILTER (WHERE {znane} AND h.pojemnosc > 0), 0
        )::bigint AS widzowie_z_pojemnoscia,
        COALESCE(
            SUM(h.pojemnosc) FILTER (WHERE {znane} AND h.pojemnosc > 0), 0
        )::bigint AS pojemnosc_laczna
    """


@dataclass(frozen=True)
class ZestawZapytanFrekwencji:
    podsumowanie: TextClause
    sezony: TextClause
    kluby: TextClause
    srednie_klubow: TextClause
    rekordy: TextClause


def _zestaw(znane: str) -> ZestawZapytanFrekwencji:
    return ZestawZapytanFrekwencji(
        podsumowanie=zapytanie(
            f"""
            SELECT {_kolumny_agregacji(znane)}
            FROM {ZAKRES_MECZOW}
            WHERE {WARUNKI_MECZU}
            """
        ),
        sezony=zapytanie(
            f"""
            SELECT
                s.id AS id_sezon,
                s.nazwa AS nazwa,
                s.rok_rozpoczecia AS rok_poczatku,
                {_kolumny_agregacji(znane)}
            FROM {ZAKRES_MECZOW}
            JOIN public.sezony s ON s.id = m.id_sezon
            WHERE {WARUNKI_MECZU}
            GROUP BY s.id, s.nazwa, s.rok_rozpoczecia
            ORDER BY s.rok_rozpoczecia NULLS FIRST, s.id
            """
        ),
        kluby=zapytanie(
            f"""
            SELECT
                {GOSPODARZ_ID} AS id_zespol,
                COALESCE(
                    (ARRAY_AGG(
                        {NAZWA_GOSPODARZA}
                        ORDER BY s.rok_rozpoczecia DESC NULLS LAST, m.id_sezon DESC
                    ) FILTER (WHERE {NAZWA_GOSPODARZA} IS NOT NULL))[1],
                    '—'
                ) AS nazwa,
                {_kolumny_agregacji(znane)}
            FROM {ZAKRES_MECZOW}
            LEFT JOIN public.sezony s ON s.id = m.id_sezon
            LEFT JOIN public.zespoly_sezony zg
                ON zg.id_zespol = ({GOSPODARZ_ID}) AND zg.id_sezon = m.id_sezon
            WHERE {WARUNKI_MECZU}
              AND ({GOSPODARZ_ID}) IS NOT NULL
            GROUP BY 1
            HAVING COUNT(*) FILTER (WHERE {znane}) > 0
            """
        ),
        srednie_klubow=zapytanie(
            f"""
            SELECT
                {GOSPODARZ_ID} AS id_zespol,
                m.id_sezon AS id_sezon,
                (AVG(m.widzowie) FILTER (WHERE {znane}))::float8 AS srednia
            FROM {ZAKRES_MECZOW}
            WHERE {WARUNKI_MECZU}
              AND ({GOSPODARZ_ID}) IS NOT NULL
            GROUP BY 1, 2
            HAVING COUNT(*) FILTER (WHERE {znane}) > 0
            """
        ),
        rekordy=zapytanie(
            f"""
            SELECT {POLA_REKORDU}
            FROM {ZAKRES_MECZOW} {JOINY_DRUZYN}
            WHERE {WARUNKI_MECZU}
              AND {znane}
            ORDER BY m.widzowie DESC, {TERMIN} DESC NULLS LAST, m.id DESC
            LIMIT :limit
            """,
            bindparam("limit", type_=Integer()),
        ),
    )


ZESTAWY_ZAPYTAN = {False: _zestaw(ZNANE), True: _zestaw(ZNANE_BEZ_ZER)}


def _podsumowanie(wiersz: Mapping[str, Any]) -> PodsumowanieFrekwencji:
    return PodsumowanieFrekwencji(
        rozegrane=int(wiersz["rozegrane"]),
        znane=int(wiersz["znane"]),
        suma=int(wiersz["suma"]),
        srednia=wiersz["srednia"],
        mediana=wiersz["mediana"],
        q1=wiersz["q1"],
        q3=wiersz["q3"],
        minimum=wiersz["minimum"],
        maksimum=wiersz["maksimum"],
        mecze_zero=int(wiersz["mecze_zero"]),
        widzowie_z_pojemnoscia=int(wiersz["widzowie_z_pojemnoscia"]),
        pojemnosc_laczna=int(wiersz["pojemnosc_laczna"]),
    )


def _rekord(wiersz: Mapping[str, Any]) -> RekordFrekwencji:
    return RekordFrekwencji(
        id_mecz=int(wiersz["id_mecz"]),
        termin=wiersz["termin"],
        sezon=str(wiersz["sezon"]),
        rozgrywki=str(wiersz["rozgrywki"]),
        gospodarz=str(wiersz["gospodarz"]),
        gosc=str(wiersz["gosc"]),
        bramki_gospodarza=wiersz["bramki_gospodarza"],
        bramki_goscia=wiersz["bramki_goscia"],
        hala=wiersz["hala"],
        widzowie=int(wiersz["widzowie"]),
    )


def _wiersz_kalendarza(wiersz: Mapping[str, Any]) -> WierszKalendarza:
    klucz = wiersz["klucz"]
    return WierszKalendarza(
        **agregat_z_wiersza(wiersz), klucz=klucz if isinstance(klucz, str) else int(klucz)
    )


def _meczprobki(wiersz: Mapping[str, Any]) -> MeczProbki:
    return MeczProbki(
        id_mecz=int(wiersz["id_mecz"]),
        widzowie=int(wiersz["widzowie"]),
        termin=wiersz["termin"],
        dzien_tygodnia=wiersz["dzien_tygodnia"],
        godzina=wiersz["godzina"],
        miesiac=wiersz["miesiac"],
        id_gospodarza=wiersz["id_gospodarza"],
        id_goscia=wiersz["id_goscia"],
        gospodarz=str(wiersz["gospodarz"]),
        gosc=str(wiersz["gosc"]),
        bramki_gospodarza=wiersz["bramki_gospodarza"],
        bramki_goscia=wiersz["bramki_goscia"],
    )


def _parametry(filtry: FiltryFrekwencji) -> dict[str, Any]:
    return {
        "id_sezon": filtry.id_sezon,
        "rozgrywki": filtry.rozgrywki,
        "plec": filtry.plec,
        "id_zespol": filtry.id_zespol,
        "id_hala": filtry.id_hala,
    }


class FrekwencjaSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_opcje(self) -> OpcjeFiltrowFrekwencji:
        try:
            sezony = self._sesja.execute(SEZONY_SQL).all()
            rozgrywki = self._sesja.execute(ROZGRYWKI_SQL).all()
            kluby = self._sesja.execute(KLUBY_SQL).all()
            hale = self._sesja.execute(HALE_SQL).all()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                f"Nie udało się odczytać filtrów frekwencji: {wyjatek}"
            ) from wyjatek
        return OpcjeFiltrowFrekwencji(
            sezony=self._opcje(sezony),
            rozgrywki=tuple(OpcjaFiltrow(str(wiersz[0]), str(wiersz[0])) for wiersz in rozgrywki),
            kluby=self._opcje(kluby),
            hale=self._opcje(hale),
        )

    def pobierz_podsumowanie(self, filtry: FiltryFrekwencji) -> PodsumowanieFrekwencji:
        wiersze = self._wiersze(
            ZESTAWY_ZAPYTAN[filtry.bez_zer].podsumowanie, _parametry(filtry), "podsumowanie"
        )
        return _podsumowanie(wiersze[0])

    def pobierz_sezony(self, filtry: FiltryFrekwencji) -> tuple[SezonFrekwencji, ...]:
        wiersze = self._wiersze(
            ZESTAWY_ZAPYTAN[filtry.bez_zer].sezony,
            _parametry(filtry.bez_sezonu()),
            "trend sezonowy",
        )
        return tuple(
            SezonFrekwencji(
                id_sezon=int(wiersz["id_sezon"]),
                nazwa=str(wiersz["nazwa"]),
                rok_poczatku=wiersz["rok_poczatku"],
                podsumowanie=_podsumowanie(wiersz),
            )
            for wiersz in wiersze
        )

    def pobierz_kluby(self, filtry: FiltryFrekwencji) -> tuple[KlubFrekwencji, ...]:
        wiersze = self._wiersze(
            ZESTAWY_ZAPYTAN[filtry.bez_zer].kluby, _parametry(filtry), "ranking klubów"
        )
        return tuple(
            KlubFrekwencji(
                id_zespol=int(wiersz["id_zespol"]),
                nazwa=str(wiersz["nazwa"]),
                podsumowanie=_podsumowanie(wiersz),
            )
            for wiersz in wiersze
        )

    def pobierz_srednie_klubow(self, filtry: FiltryFrekwencji) -> tuple[SredniaKlubuSezonu, ...]:
        wiersze = self._wiersze(
            ZESTAWY_ZAPYTAN[filtry.bez_zer].srednie_klubow,
            _parametry(filtry.bez_sezonu()),
            "średnie klubów w sezonach",
        )
        return tuple(
            SredniaKlubuSezonu(
                id_zespol=int(wiersz["id_zespol"]),
                id_sezon=int(wiersz["id_sezon"]),
                srednia=float(wiersz["srednia"]),
            )
            for wiersz in wiersze
        )

    def pobierz_rekordy(self, filtry: FiltryFrekwencji, limit: int) -> tuple[RekordFrekwencji, ...]:
        wiersze = self._wiersze(
            ZESTAWY_ZAPYTAN[filtry.bez_zer].rekordy,
            {**_parametry(filtry), "limit": limit},
            "rekordy frekwencji",
        )
        return tuple(_rekord(wiersz) for wiersz in wiersze)

    def pobierz_przeciwnikow(self, filtry: FiltryFrekwencji) -> tuple[PrzeciwnikFrekwencji, ...]:
        wiersze = self._wiersze(
            ZESTAWY_ROZSZERZONE[filtry.bez_zer].przeciwnicy, _parametry(filtry), "przeciwnicy"
        )
        return tuple(
            PrzeciwnikFrekwencji(
                **agregat_z_wiersza(wiersz),
                id_zespol=int(wiersz["id_zespol"]),
                nazwa=str(wiersz["nazwa"]),
            )
            for wiersz in wiersze
        )

    def pobierz_kalendarz(self, filtry: FiltryFrekwencji) -> DaneKalendarza:
        zestaw = ZESTAWY_ROZSZERZONE[filtry.bez_zer]
        parametry = _parametry(filtry)
        return DaneKalendarza(
            miesiace=self._grupy_kalendarza(zestaw.miesiace, parametry, "kalendarz: miesiące"),
            dni=self._grupy_kalendarza(zestaw.dni, parametry, "kalendarz: dni tygodnia"),
            godziny=self._grupy_kalendarza(zestaw.godziny, parametry, "kalendarz: godziny"),
            rundy=self._grupy_kalendarza(zestaw.rundy, parametry, "kalendarz: rundy"),
            komorki=tuple(
                KomorkaKalendarza(
                    **agregat_z_wiersza(wiersz),
                    dzien=int(wiersz["dzien"]),
                    godzina=int(wiersz["godzina"]),
                )
                for wiersz in self._wiersze(zestaw.heatmapa, parametry, "kalendarz: heatmapa")
            ),
        )

    def pobierz_rekordy_rozszerzone(
        self, filtry: FiltryFrekwencji, limit: int
    ) -> RekordyRozszerzoneFrekwencji:
        zestaw = ZESTAWY_ROZSZERZONE[filtry.bez_zer]
        parametry = _parametry(filtry)
        z_limitem = {**parametry, "limit": limit}
        return RekordyRozszerzoneFrekwencji(
            sezony=self._rekordy(zestaw.rekordy_sezonow, parametry, "rekordy sezonów"),
            kluby=self._rekordy(zestaw.rekordy_klubow, z_limitem, "rekordy klubów"),
            hale=self._rekordy(zestaw.rekordy_hal, z_limitem, "rekordy hal"),
            finaly=self._rekordy(zestaw.rekordy_finalow, z_limitem, "rekordy finałów"),
            pary=self._rekordy(zestaw.rekordy_par, z_limitem, "rekordy par drużyn"),
        )

    def pobierz_miasta(self, filtry: FiltryFrekwencji) -> DaneMiast:
        zestaw = ZESTAWY_MIAST[filtry.bez_zer]
        parametry = _parametry(filtry)
        bez_miasta = self._wiersze(zestaw.bez_miasta, parametry, "miasta: mecze bez miasta")
        return DaneMiast(
            miasta=self._mapuj(zestaw.miasta, parametry, "ranking miast", miasto_z_wiersza),
            wklady=self._mapuj(zestaw.wklady, parametry, "wkład klubów w miasta", wklad_z_wiersza),
            mecze_bez_miasta=int(bez_miasta[0]["rozegrane"]),
            sezony=self._mapuj(zestaw.sezony, parametry, "sezony miast", sezon_z_wiersza),
            rozgrywki=self._mapuj(
                zestaw.rozgrywki, parametry, "rozgrywki miast", rozgrywki_z_wiersza
            ),
            hale=self._mapuj(zestaw.hale, parametry, "hale miast", hala_z_wiersza),
        )

    def pobierz_probke(self, filtry: FiltryFrekwencji, limit: int) -> tuple[MeczProbki, ...]:
        wiersze = self._wiersze(
            ZESTAWY_ROZSZERZONE[filtry.bez_zer].probka,
            {**_parametry(filtry), "limit": limit},
            "próbka meczów",
        )
        return tuple(_meczprobki(wiersz) for wiersz in wiersze)

    def _grupy_kalendarza(
        self, zapytanie_sql: TextClause, parametry: Mapping[str, Any], opis: str
    ) -> tuple[WierszKalendarza, ...]:
        return tuple(
            _wiersz_kalendarza(wiersz) for wiersz in self._wiersze(zapytanie_sql, parametry, opis)
        )

    def _mapuj[T](
        self,
        zapytanie_sql: TextClause,
        parametry: Mapping[str, Any],
        opis: str,
        mapper: Callable[[Mapping[str, Any]], T],
    ) -> tuple[T, ...]:
        return tuple(mapper(wiersz) for wiersz in self._wiersze(zapytanie_sql, parametry, opis))

    def _rekordy(
        self, zapytanie_sql: TextClause, parametry: Mapping[str, Any], opis: str
    ) -> tuple[RekordFrekwencji, ...]:
        return tuple(_rekord(wiersz) for wiersz in self._wiersze(zapytanie_sql, parametry, opis))

    def _wiersze(
        self, zapytanie_sql: TextClause, parametry: Mapping[str, Any], opis: str
    ) -> Sequence[Mapping[str, Any]]:
        try:
            wynik = self._sesja.execute(zapytanie_sql, dict(parametry))
            return [dict(wiersz) for wiersz in wynik.mappings()]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(
                f"Nie udało się odczytać frekwencji ({opis}): {wyjatek}"
            ) from wyjatek

    @staticmethod
    def _opcje(wiersze: Sequence[Any]) -> tuple[OpcjaFiltrow, ...]:
        return tuple(OpcjaFiltrow(str(wiersz[0]), str(wiersz[1])) for wiersz in wiersze)
