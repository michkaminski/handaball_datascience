from __future__ import annotations

from typing import Any

from sqlalchemy import Integer, String, TextClause, bindparam, text

GOSPODARZ_ID = "CASE WHEN m.zamiana IS TRUE THEN m.id_zespol_gosc ELSE m.id_zespol_gosp END"
GOSC_ID = "CASE WHEN m.zamiana IS TRUE THEN m.id_zespol_gosp ELSE m.id_zespol_gosc END"
BRAMKI_GOSPODARZA = "CASE WHEN m.zamiana IS TRUE THEN m.wynik_gosc_full ELSE m.wynik_gosp_full END"
BRAMKI_GOSCIA = "CASE WHEN m.zamiana IS TRUE THEN m.wynik_gosp_full ELSE m.wynik_gosc_full END"

ZNANE = "m.widzowie >= 0"
ZNANE_BEZ_ZER = "m.widzowie > 0"

TERMIN = "COALESCE(m.data_faktyczna, m.data_propozycji)"
DZIEN_TYGODNIA = f"(EXTRACT(ISODOW FROM {TERMIN}))::int"
MIESIAC = f"(EXTRACT(MONTH FROM {TERMIN}))::int"
GODZINA = (
    f"(CASE WHEN ({TERMIN})::time = TIME '00:00' THEN NULL "
    f"ELSE (EXTRACT(HOUR FROM {TERMIN}))::int END)"
)
FAZA = "COALESCE(NULLIF(btrim(ru.nazwa), ''), '—')"
FINALY = "(ru.nazwa ILIKE '%fina%' OR k.nazwa ILIKE '%fina%' OR r.nazwa ILIKE '%fina%')"

ZAKRES_MECZOW = """
    public.mecze m
    JOIN public.rozgrywki r ON r.id = m.id_rozgrywki
    LEFT JOIN public.hale h ON h.id = m.id_hala
"""

JOINY_FAZ = """
    LEFT JOIN public.kolejki k ON k.id = m.id_kolejka
    LEFT JOIN public.rundy ru ON ru.id = k.id_runda
"""

WARUNKI_MECZU = f"""
    m.wynik_gosp_full IS NOT NULL
    AND m.wynik_gosc_full IS NOT NULL
    AND m.wynik_gosp_full >= 0
    AND m.wynik_gosc_full >= 0
    AND m.wycofany IS NOT TRUE
    AND m.id_zespol_walkower IS NULL
    AND (CAST(:id_sezon AS INTEGER) IS NULL OR m.id_sezon = :id_sezon)
    AND (CAST(:rozgrywki AS TEXT) IS NULL OR r.nazwa = :rozgrywki)
    AND (CAST(:plec AS TEXT) IS NULL OR r.plec = :plec)
    AND (CAST(:id_zespol AS INTEGER) IS NULL OR ({GOSPODARZ_ID}) = :id_zespol)
    AND (CAST(:id_hala AS INTEGER) IS NULL OR m.id_hala = :id_hala)
"""

PARAMETRY_FILTROW = (
    bindparam("id_sezon", type_=Integer()),
    bindparam("rozgrywki", type_=String()),
    bindparam("plec", type_=String()),
    bindparam("id_zespol", type_=Integer()),
    bindparam("id_hala", type_=Integer()),
)

NAZWA_KLUBU = "NULLIF(btrim({alias}.nazwa), '')"
NAZWA_GOSPODARZA = NAZWA_KLUBU.format(alias="zg")
NAZWA_GOSCIA = NAZWA_KLUBU.format(alias="zw")

JOINY_DRUZYN = f"""
    LEFT JOIN public.sezony s ON s.id = m.id_sezon
    LEFT JOIN public.zespoly_sezony zg
        ON zg.id_zespol = ({GOSPODARZ_ID}) AND zg.id_sezon = m.id_sezon
    LEFT JOIN public.zespoly_sezony zw
        ON zw.id_zespol = ({GOSC_ID}) AND zw.id_sezon = m.id_sezon
"""

POLA_REKORDU = f"""
    m.id AS id_mecz,
    {TERMIN} AS termin,
    COALESCE(NULLIF(btrim(s.nazwa), ''), '—') AS sezon,
    COALESCE(NULLIF(btrim(r.nazwa), ''), '—') AS rozgrywki,
    COALESCE({NAZWA_GOSPODARZA}, '—') AS gospodarz,
    COALESCE({NAZWA_GOSCIA}, '—') AS gosc,
    {BRAMKI_GOSPODARZA} AS bramki_gospodarza,
    {BRAMKI_GOSCIA} AS bramki_goscia,
    NULLIF(
        concat_ws(', ', NULLIF(btrim(h.nazwa), ''), NULLIF(btrim(h.miasto), '')), ''
    ) AS hala,
    m.widzowie AS widzowie
"""


def zapytanie(tresc: str, *parametry_dodatkowe: Any) -> TextClause:
    return text(tresc).bindparams(*PARAMETRY_FILTROW, *parametry_dodatkowe)
