from __future__ import annotations

from typing import Any, cast

from sqlalchemy import Select, and_, case, distinct, func, literal, or_, select, union_all
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoSedziego
from handball.domain.referee_details import (
    AktywnoscSezonuSedziego,
    FiltryMeczowSedziego,
    MeczSedziego,
    StatystykaDruzynySedziego,
    StatystykaPartneraSedziego,
    StatystykaRozgrywekSedziego,
    StatystykaSezonRozgrywkiSedziego,
    StatystykiSedziego,
    StronaMeczowSedziego,
    SzczegolySedziego,
)
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.officials import MeczSedzia, Sedzia
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon


class SzczegolySedziegoSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_szczegoly(self, id_sedzia: int) -> SzczegolySedziego:
        try:
            sedzia = self._sesja.get(Sedzia, id_sedzia)
            if sedzia is None:
                raise NieZnalezionoSedziego(id_sedzia)
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            podsumowanie = self._sesja.execute(
                select(
                    func.min(termin),
                    func.max(termin),
                    func.count(distinct(Mecz.id)),
                    func.count(distinct(Mecz.id_sezon)),
                    func.count(distinct(Rozgrywki.nazwa)),
                )
                .select_from(MeczSedzia)
                .join(Mecz, Mecz.id == MeczSedzia.id_mecz)
                .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
                .where(MeczSedzia.id_sedzia == id_sedzia)
            ).one()
            zespoly = union_all(
                select(Mecz.id_zespol_gosp.label("id_zespol"))
                .join(MeczSedzia, MeczSedzia.id_mecz == Mecz.id)
                .where(MeczSedzia.id_sedzia == id_sedzia, Mecz.id_zespol_gosp.is_not(None)),
                select(Mecz.id_zespol_gosc.label("id_zespol"))
                .join(MeczSedzia, MeczSedzia.id_mecz == Mecz.id)
                .where(MeczSedzia.id_sedzia == id_sedzia, Mecz.id_zespol_gosc.is_not(None)),
            ).subquery()
            liczba_druzyn = (
                self._sesja.scalar(select(func.count(distinct(zespoly.c.id_zespol)))) or 0
            )
            return SzczegolySedziego(
                sedzia.id,
                sedzia.nazwisko,
                sedzia.miasto,
                podsumowanie[0],
                podsumowanie[1],
                podsumowanie[2],
                podsumowanie[3],
                podsumowanie[4],
                liczba_druzyn,
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać karty sędziego.") from wyjatek

    def pobierz_mecze(self, id_sedzia: int, filtry: FiltryMeczowSedziego) -> StronaMeczowSedziego:
        try:
            zapytanie = self._zapytanie_meczow(id_sedzia, filtry)
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            numer = min(filtry.strona, ostatnia)
            porzadek = zapytanie.selected_columns.data
            porzadek = porzadek.desc() if filtry.sortowanie.startswith("-") else porzadek.asc()
            wiersze = (
                self._sesja.execute(
                    zapytanie.order_by(porzadek.nulls_last(), Mecz.id.desc())
                    .offset((numer - 1) * filtry.rozmiar_strony)
                    .limit(filtry.rozmiar_strony)
                )
                .mappings()
                .all()
            )
            identyfikatory = [cast(int, w["id_mecz"]) for w in wiersze]
            partnerzy = self._partnerzy_meczow(id_sedzia, identyfikatory)
            return StronaMeczowSedziego(
                [
                    MeczSedziego(
                        cast(int, w["id_mecz"]),
                        w["data"],
                        cast(str, w["sezon"]),
                        cast(str, w["rozgrywki"]),
                        cast(str | None, w["gospodarz"]),
                        cast(int | None, w["wynik_gospodarza"]),
                        cast(int | None, w["wynik_goscia"]),
                        cast(str | None, w["gosc"]),
                        partnerzy.get(cast(int, w["id_mecz"]), ()),
                    )
                    for w in wiersze
                ],
                liczba,
                numer,
                filtry.rozmiar_strony,
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów sędziego.") from wyjatek

    def pobierz_statystyki(
        self, id_sedzia: int, filtry: FiltryMeczowSedziego
    ) -> StatystykiSedziego:
        try:
            baza = self._zapytanie_meczow(id_sedzia, filtry).cte("mecze_wybranego_sedziego")
            sezony = [
                AktywnoscSezonuSedziego(id_sezon, sezon, mecze, tuple(r or ()))
                for id_sezon, sezon, mecze, r in self._sesja.execute(
                    select(
                        baza.c.id_sezon,
                        baza.c.sezon,
                        func.count(distinct(baza.c.id_mecz)),
                        func.array_agg(distinct(baza.c.rozgrywki)),
                    )
                    .group_by(baza.c.id_sezon, baza.c.sezon)
                    .order_by(baza.c.sezon.desc())
                )
            ]
            rozgrywki = [
                StatystykaRozgrywekSedziego(nazwa, mecze)
                for nazwa, mecze in self._sesja.execute(
                    select(baza.c.rozgrywki, func.count(distinct(baza.c.id_mecz)).label("mecze"))
                    .group_by(baza.c.rozgrywki)
                    .order_by(func.count(distinct(baza.c.id_mecz)).desc(), baza.c.rozgrywki)
                )
            ]
            sezon_rozgrywki = [
                StatystykaSezonRozgrywkiSedziego(sezon, nazwa, mecze)
                for sezon, nazwa, mecze in self._sesja.execute(
                    select(baza.c.sezon, baza.c.rozgrywki, func.count(distinct(baza.c.id_mecz)))
                    .group_by(baza.c.sezon, baza.c.rozgrywki)
                    .order_by(baza.c.sezon.desc(), baza.c.rozgrywki)
                )
            ]
            druzyny = self._ranking_druzyn(baza)
            partnerzy = [
                StatystykaPartneraSedziego(id_partner, nazwa or f"Sędzia #{id_partner}", mecze)
                for id_partner, nazwa, mecze in self._sesja.execute(
                    select(
                        MeczSedzia.id_sedzia,
                        Sedzia.nazwisko,
                        func.count(distinct(MeczSedzia.id_mecz)).label("mecze"),
                    )
                    .join(baza, baza.c.id_mecz == MeczSedzia.id_mecz)
                    .join(Sedzia, Sedzia.id == MeczSedzia.id_sedzia)
                    .where(MeczSedzia.id_sedzia != id_sedzia)
                    .group_by(MeczSedzia.id_sedzia, Sedzia.nazwisko)
                    .order_by(func.count(distinct(MeczSedzia.id_mecz)).desc(), Sedzia.nazwisko)
                )
            ]
            liczba_meczow = self._sesja.scalar(select(func.count()).select_from(baza)) or 0
            return StatystykiSedziego(
                liczba_meczow,
                len(sezony),
                len(rozgrywki),
                len(druzyny),
                sezony,
                rozgrywki,
                sezon_rozgrywki,
                druzyny,
                partnerzy,
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać statystyk sędziego.") from wyjatek

    def _zapytanie_meczow(self, id_sedzia: int, filtry: FiltryMeczowSedziego) -> Select[Any]:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
        nazwa_gospodarza = case((Mecz.zamiana.is_(True), gosc.nazwa), else_=gospodarz.nazwa)
        nazwa_goscia = case((Mecz.zamiana.is_(True), gospodarz.nazwa), else_=gosc.nazwa)
        id_gospodarza = case(
            (Mecz.zamiana.is_(True), Mecz.id_zespol_gosc), else_=Mecz.id_zespol_gosp
        )
        id_goscia = case((Mecz.zamiana.is_(True), Mecz.id_zespol_gosp), else_=Mecz.id_zespol_gosc)
        wynik_gospodarza = case(
            (Mecz.zamiana.is_(True), Mecz.wynik_gosc_full), else_=Mecz.wynik_gosp_full
        )
        wynik_goscia = case(
            (Mecz.zamiana.is_(True), Mecz.wynik_gosp_full), else_=Mecz.wynik_gosc_full
        )
        zapytanie = (
            select(
                Mecz.id.label("id_mecz"),
                Mecz.id_sezon.label("id_sezon"),
                termin.label("data"),
                Sezon.nazwa.label("sezon"),
                Rozgrywki.nazwa.label("rozgrywki"),
                id_gospodarza.label("id_gospodarza"),
                id_goscia.label("id_goscia"),
                nazwa_gospodarza.label("gospodarz"),
                wynik_gospodarza.label("wynik_gospodarza"),
                wynik_goscia.label("wynik_goscia"),
                nazwa_goscia.label("gosc"),
            )
            .select_from(MeczSedzia)
            .join(Mecz, Mecz.id == MeczSedzia.id_mecz)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .outerjoin(
                gospodarz,
                and_(
                    gospodarz.id_zespol == Mecz.id_zespol_gosp, gospodarz.id_sezon == Mecz.id_sezon
                ),
            )
            .outerjoin(
                gosc, and_(gosc.id_zespol == Mecz.id_zespol_gosc, gosc.id_sezon == Mecz.id_sezon)
            )
            .where(MeczSedzia.id_sedzia == id_sedzia)
            .distinct()
        )
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
        if filtry.druzyna:
            zapytanie = zapytanie.where(
                or_(
                    nazwa_gospodarza.icontains(filtry.druzyna, autoescape=True),
                    nazwa_goscia.icontains(filtry.druzyna, autoescape=True),
                )
            )
        if filtry.strona_meczu == "gospodarz" and filtry.druzyna:
            zapytanie = zapytanie.where(nazwa_gospodarza.icontains(filtry.druzyna, autoescape=True))
        if filtry.strona_meczu == "gosc" and filtry.druzyna:
            zapytanie = zapytanie.where(nazwa_goscia.icontains(filtry.druzyna, autoescape=True))
        if filtry.data_od:
            zapytanie = zapytanie.where(termin >= filtry.data_od)
        if filtry.data_do:
            zapytanie = zapytanie.where(termin <= filtry.data_do)
        return zapytanie

    def _partnerzy_meczow(
        self, id_sedzia: int, identyfikatory: list[int]
    ) -> dict[int, tuple[tuple[int, str], ...]]:
        if not identyfikatory:
            return {}
        wynik: dict[int, list[tuple[int, str]]] = {}
        for id_mecz, id_partner, nazwa in self._sesja.execute(
            select(MeczSedzia.id_mecz, MeczSedzia.id_sedzia, Sedzia.nazwisko)
            .join(Sedzia, Sedzia.id == MeczSedzia.id_sedzia)
            .where(MeczSedzia.id_mecz.in_(identyfikatory), MeczSedzia.id_sedzia != id_sedzia)
            .distinct()
            .order_by(MeczSedzia.id_mecz, Sedzia.nazwisko)
        ):
            wynik.setdefault(id_mecz, []).append((id_partner, nazwa or f"Sędzia #{id_partner}"))
        return {id_mecz: tuple(partnerzy) for id_mecz, partnerzy in wynik.items()}

    def _ranking_druzyn(self, baza: Any) -> list[StatystykaDruzynySedziego]:
        strony = union_all(
            select(
                baza.c.id_mecz,
                baza.c.id_gospodarza.label("id_zespol"),
                literal("gospodarz").label("strona"),
            ).where(baza.c.id_gospodarza.is_not(None)),
            select(
                baza.c.id_mecz,
                baza.c.id_goscia.label("id_zespol"),
                literal("gosc").label("strona"),
            ).where(baza.c.id_goscia.is_not(None)),
        ).cte("druzyny_meczow_sedziego")
        return [
            StatystykaDruzynySedziego(
                id_zespol, nazwa or f"Zespół #{id_zespol}", mecze, gospodarze, goscie
            )
            for id_zespol, nazwa, mecze, gospodarze, goscie in self._sesja.execute(
                select(
                    strony.c.id_zespol,
                    Zespol.nazwa,
                    func.count(distinct(strony.c.id_mecz)),
                    func.count(distinct(strony.c.id_mecz)).filter(strony.c.strona == "gospodarz"),
                    func.count(distinct(strony.c.id_mecz)).filter(strony.c.strona == "gosc"),
                )
                .join(Zespol, Zespol.id == strony.c.id_zespol, isouter=True)
                .group_by(strony.c.id_zespol, Zespol.nazwa)
                .order_by(func.count(distinct(strony.c.id_mecz)).desc(), Zespol.nazwa)
            )
        ]
