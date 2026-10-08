from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.database_stats import (
    PozycjaTabeliBazy,
    PodsumowanieBazy,
    SnapshotStatystykBazy,
)
from handball.domain.errors import BladOdczytuDanych

TABELE_SQL = text(
    """
    SELECT
        s.schemaname AS schemat,
        s.relname AS tabela,
        GREATEST(COALESCE(s.n_live_tup, 0), 0)::bigint AS rekordy,
        pg_total_relation_size(s.relid)::bigint AS rozmiar_bajty,
        pg_relation_size(s.relid)::bigint AS dane_bajty,
        pg_indexes_size(s.relid)::bigint AS indeksy_bajty
    FROM pg_stat_user_tables s
    ORDER BY s.schemaname, s.relname
    """
)

PODSUMOWANIE_SQL = text(
    """
    SELECT
        current_database() AS nazwa,
        pg_database_size(current_database())::bigint AS rozmiar_bajty
    """
)


class StatystykiBazySQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_snapshot(self) -> SnapshotStatystykBazy:
        try:
            wiersze = self._sesja.execute(TABELE_SQL).mappings().all()
            podsumowanie_wiersz = self._sesja.execute(PODSUMOWANIE_SQL).mappings().one()
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(f"Nie udało się odczytać statystyk bazy: {wyjatek}") from wyjatek
        tabele = tuple(
            PozycjaTabeliBazy(
                schemat=wiersz["schemat"],
                tabela=wiersz["tabela"],
                rekordy=int(wiersz["rekordy"] or 0),
                rozmiar_bajty=int(wiersz["rozmiar_bajty"] or 0),
                dane_bajty=int(wiersz["dane_bajty"] or 0),
                indeksy_bajty=int(wiersz["indeksy_bajty"] or 0),
            )
            for wiersz in wiersze
        )
        schematy = tuple(sorted({tabela.schemat for tabela in tabele}))
        podsumowanie = PodsumowanieBazy(
            nazwa=str(podsumowanie_wiersz["nazwa"]),
            rozmiar_bajty=int(podsumowanie_wiersz["rozmiar_bajty"] or 0),
            liczba_tabel=len(tabele),
            suma_rekordow=sum(tabela.rekordy for tabela in tabele),
            suma_rozmiarow_bajty=sum(tabela.rozmiar_bajty for tabela in tabele),
            suma_indeksow_bajty=sum(tabela.indeksy_bajty for tabela in tabele),
        )
        return SnapshotStatystykBazy(podsumowanie, tabele, schematy)
