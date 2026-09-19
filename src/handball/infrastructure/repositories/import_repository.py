from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from typing import Any

from sqlalchemy import Date, DateTime, MetaData, Table, and_, bindparam, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

from handball.contracts.import_storage import ImportStore
from handball.domain.imports import BladImportu, PrzebiegImportu, RekordImportu, ZadaniePobrania

KOLEJNOSC = (
    "sezony",
    "rozgrywki",
    "zespoly",
    "zespoly_sezony",
    "rundy",
    "kolejki",
    "zespoly_rozgrywki",
    "hale",
    "mecze",
    "zawodnicy",
    "mecze_zawodnicy",
)


class ImportSQLAlchemyRepository:
    def __init__(self, silnik: Engine, magazyn: ImportStore) -> None:
        self._silnik = silnik
        self._magazyn = magazyn

    def pobierz_brakujace(self, ligi: list[int]) -> list[ZadaniePobrania]:
        zapytanie = text("""
            SELECT m.id, m.id_rozgrywki, m.id_kolejka
            FROM public.mecze m
            WHERE m.id_sezon = :sezon AND m.id_rozgrywki IN :ligi
              AND m.data_faktyczna < CAST(CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Warsaw' AS date)
              AND m.wycofany IS NOT TRUE AND m.id_zespol_walkower IS NULL
              AND (
                m.wynik_gosp_full IS NULL OR m.wynik_gosc_full IS NULL
                OR NOT EXISTS (
                    SELECT 1 FROM public.mecze_zawodnicy z
                    WHERE z.id_mecz = m.id AND z.strona = 'gosp'
                )
                OR NOT EXISTS (
                    SELECT 1 FROM public.mecze_zawodnicy z
                    WHERE z.id_mecz = m.id AND z.strona = 'gosc'
                )
              )
            ORDER BY m.data_faktyczna DESC, m.id
        """).bindparams(bindparam("ligi", expanding=True))
        try:
            with self._silnik.connect().execution_options(
                postgresql_readonly=True, isolation_level="REPEATABLE READ"
            ) as polaczenie:
                try:
                    wiersze = (
                        polaczenie.execute(zapytanie, {"sezon": 195, "ligi": ligi}).mappings().all()
                    )
                    return [
                        ZadaniePobrania(
                            "pokaz_mecze_szczegoly.php",
                            {"Zawody": int(wiersz["id"])},
                            "szczegoly",
                            {
                                "mid": int(wiersz["id"]),
                                "cid": int(wiersz["id_rozgrywki"]),
                                "did": int(wiersz["id_kolejka"]),
                            },
                        )
                        for wiersz in wiersze
                    ]
                finally:
                    polaczenie.rollback()
        except SQLAlchemyError as blad:
            raise BladImportu("Nie można odczytać meczów wymagających uzupełnienia.") from blad

    def _tabele(self, polaczenie: Connection) -> dict[str, Table]:
        metadane = MetaData()
        return {
            nazwa: Table(
                nazwa, metadane, schema="public", autoload_with=polaczenie, resolve_fks=False
            )
            for nazwa in KOLEJNOSC
        }

    def _json(self, wartosc: Any) -> Any:
        if isinstance(wartosc, (date, datetime)):
            return wartosc.isoformat()
        if isinstance(wartosc, Decimal):
            return str(wartosc)
        return wartosc

    def _dane(self, tabela: Table, dane: dict[str, Any]) -> dict[str, Any]:
        wynik = dict(dane)
        for nazwa, wartosc in wynik.items():
            if wartosc is None:
                continue
            if isinstance(tabela.c[nazwa].type, DateTime):
                wynik[nazwa] = datetime.fromisoformat(str(wartosc))
            elif isinstance(tabela.c[nazwa].type, Date):
                wynik[nazwa] = date.fromisoformat(str(wartosc)[:10])
        return wynik

    def _rozwiaz(
        self, polaczenie: Connection, tabela: Table, dane: dict[str, Any]
    ) -> dict[str, Any]:
        wynik = dict(dane)
        for pole, wartosc in dane.items():
            if isinstance(wartosc, dict) and "tabela" in wartosc:
                rodzic = tabela.metadata.tables["public." + wartosc["tabela"]]
                ident = polaczenie.execute(
                    select(rodzic.c.id).where(
                        and_(*(rodzic.c[k] == v for k, v in wartosc["klucz"].items()))
                    )
                ).scalar_one_or_none()
                wynik[pole] = ident
        return wynik

    def _wiersz(
        self, polaczenie: Connection, tabela: Table, rekord: RekordImportu
    ) -> dict[str, Any] | None:
        warunek = and_(*(tabela.c[k] == v for k, v in rekord.klucz.items()))
        wiersz = polaczenie.execute(select(tabela).where(warunek)).mappings().first()
        return {k: self._json(v) for k, v in wiersz.items()} if wiersz is not None else None

    def porownaj(self, przebieg: PrzebiegImportu) -> None:
        try:
            with self._silnik.connect().execution_options(
                postgresql_readonly=True, isolation_level="REPEATABLE READ"
            ) as polaczenie:
                tabele = self._tabele(polaczenie)
                for rekord in przebieg.rekordy:
                    poprzednio = self._wiersz(polaczenie, tabele[rekord.tabela], rekord)
                    for pole in ("id_sezon", "id_rozgrywki"):
                        if (
                            poprzednio
                            and pole in rekord.dane
                            and poprzednio.get(pole) != rekord.dane[pole]
                        ):
                            raise BladImportu(
                                "Identyfikator API koliduje z innym sezonem lub ligą w bazie."
                            )
                    rekord.poprzednio = poprzednio
                    rozwiazane = self._rozwiaz(polaczenie, tabele[rekord.tabela], rekord.dane)
                    rekord.zmiany = {
                        k: v
                        for k, v in rekord.dane.items()
                        if (
                            poprzednio is None
                            or poprzednio.get(k) != rozwiazane[k]
                            or (isinstance(v, dict) and rozwiazane[k] is None)
                        )
                        and (
                            not rekord.uzupelnij or poprzednio is None or poprzednio.get(k) is None
                        )
                    }
                polaczenie.rollback()
        except SQLAlchemyError as blad:
            raise BladImportu("Nie można porównać danych z bazą. Sprawdź połączenie.") from blad

    def zastosuj(self, przebieg: PrzebiegImportu) -> int:
        try:
            with (
                self._silnik.connect().execution_options(
                    postgresql_readonly=False, isolation_level="SERIALIZABLE"
                ) as polaczenie,
                polaczenie.begin(),
            ):
                polaczenie.execute(text("SET LOCAL lock_timeout = '5s'"))
                polaczenie.execute(text("SET LOCAL statement_timeout = '60s'"))
                polaczenie.execute(text("SELECT pg_advisory_xact_lock(195, 20262027)"))
                poprzedni = polaczenie.execute(
                    text(
                        "SELECT id FROM logs.import_przebiegi "
                        "WHERE parametry->>'hds_id' = :id AND status = 'SUKCES'"
                    ),
                    {"id": przebieg.id},
                ).scalar_one_or_none()
                if poprzedni is not None:
                    return int(poprzedni)
                tabele = self._tabele(polaczenie)
                for rekord in przebieg.rekordy:
                    if self._wiersz(polaczenie, tabele[rekord.tabela], rekord) != rekord.poprzednio:
                        raise BladImportu(
                            "Baza zmieniła się od przygotowania podglądu. Odśwież podgląd i "
                            "zatwierdź ponownie."
                        )
                id_przebieg = int(
                    polaczenie.execute(
                        text(
                            "INSERT INTO logs.import_przebiegi (wersja_importera, wykonawca, "
                            "parametry) "
                            "VALUES ('hds-1.0', 'hds-admin', CAST(:parametry AS jsonb)) "
                            "RETURNING id"
                        ),
                        {
                            "parametry": json.dumps(
                                {
                                    "hds_id": przebieg.id,
                                    "sezon": 195,
                                    "ligi": przebieg.ligi,
                                    "tryb": przebieg.tryb,
                                }
                            )
                        },
                    ).scalar_one()
                )
                pliki = self._zrodla(polaczenie, przebieg, id_przebieg)
                liczniki: dict[str, dict[str, int]] = {
                    k: {"dodano": 0, "zmieniono": 0, "bez_zmian": 0} for k in pliki
                }
                for rekord in sorted(przebieg.rekordy, key=lambda r: KOLEJNOSC.index(r.tabela)):
                    id_pliku, id_proby = pliki[rekord.zrodlo]
                    polaczenie.execute(
                        text(
                            "SELECT logs.ustaw_kontekst('hds-admin', :przebieg, :proba, "
                            "'Aktualizacja API 2026/2027')"
                        ),
                        {"przebieg": id_przebieg, "proba": id_proby},
                    )
                    tabela = tabele[rekord.tabela]
                    if rekord.poprzednio is None:
                        polaczenie.execute(
                            tabela.insert().values(
                                **self._dane(tabela, self._rozwiaz(polaczenie, tabela, rekord.dane))
                            )
                        )
                        liczniki[rekord.zrodlo]["dodano"] += 1
                    elif rekord.zmiany:
                        polaczenie.execute(
                            tabela.update()
                            .where(and_(*(tabela.c[k] == v for k, v in rekord.klucz.items())))
                            .values(
                                **self._dane(
                                    tabela, self._rozwiaz(polaczenie, tabela, rekord.zmiany)
                                )
                            )
                        )
                        liczniki[rekord.zrodlo]["zmieniono"] += 1
                    else:
                        liczniki[rekord.zrodlo]["bez_zmian"] += 1
                    for zrodlo in rekord.zrodla or [rekord.zrodlo]:
                        polaczenie.execute(
                            text(
                                "INSERT INTO public.rekordy_zrodla (tabela, klucz_rekordu, "
                                "id_pliku, wskaznik_json) "
                                "VALUES (:tabela, CAST(:klucz AS jsonb), :plik, '') ON CONFLICT "
                                "DO NOTHING"
                            ),
                            {
                                "tabela": rekord.tabela,
                                "klucz": json.dumps(rekord.klucz),
                                "plik": pliki[zrodlo][0],
                            },
                        )
                for klucz, (_, proba) in pliki.items():
                    polaczenie.execute(
                        text(
                            "UPDATE logs.import_pliki SET status='SUKCES', "
                            "zakonczenie=clock_timestamp(), "
                            "dodano=:dodano, zmieniono=:zmieniono, bez_zmian=:bez_zmian WHERE "
                            "id=:id"
                        ),
                        {"id": proba, **liczniki[klucz]},
                    )
                polaczenie.execute(
                    text(
                        "UPDATE logs.import_przebiegi SET status='SUKCES', "
                        "zakonczenie=clock_timestamp(), "
                        "podsumowanie=CAST(:podsumowanie AS jsonb) WHERE id=:id"
                    ),
                    {"id": id_przebieg, "podsumowanie": json.dumps(przebieg.podsumowanie)},
                )
                return id_przebieg
        except SQLAlchemyError as blad:
            raise BladImportu(
                "Zapis nie został potwierdzony. Ponów operację, aby sprawdzić jej wynik; "
                "zatwierdzony przebieg nie zostanie wykonany drugi raz."
            ) from blad

    def _zrodla(
        self, polaczenie: Connection, przebieg: PrzebiegImportu, id_przebieg: int
    ) -> dict[str, tuple[int, int]]:
        tabela = Table(
            "pliki_zrodlowe",
            MetaData(),
            schema="public",
            autoload_with=polaczenie,
            resolve_fks=False,
        )
        wynik = {}
        for identyfikator in przebieg.wykonane:
            url, tresc = self._magazyn.zrodlo(przebieg.id, identyfikator)
            skrot = sha256(tresc).hexdigest()
            if skrot != przebieg.skroty_zrodel.get(identyfikator):
                raise BladImportu("Plik ?r?d?owy zmieni? si? po pobraniu. Rozpocznij nowy import.")
            dokument = json.loads(tresc.decode("utf-8-sig"))
            sciezka = "hds/api/" + identyfikator + ".json"
            polaczenie.execute(
                insert(tabela)
                .values(
                    sciezka=sciezka,
                    sha256=skrot,
                    rozmiar=len(tresc),
                    rodzaj="zprp_api",
                    tresc=tresc,
                    dokument=dokument,
                )
                .on_conflict_do_nothing(index_elements=["sciezka", "sha256"])
            )
            id_pliku = int(
                polaczenie.execute(
                    select(tabela.c.id).where(tabela.c.sciezka == sciezka, tabela.c.sha256 == skrot)
                ).scalar_one()
            )
            id_proby = int(
                polaczenie.execute(
                    text(
                        "INSERT INTO logs.import_pliki (id_przebieg, id_pliku, status, komunikat) "
                        "VALUES (:przebieg, :plik, 'W_TRAKCIE', :url) RETURNING id"
                    ),
                    {"przebieg": id_przebieg, "plik": id_pliku, "url": url},
                ).scalar_one()
            )
            wynik[identyfikator] = (id_pliku, id_proby)
        return wynik
