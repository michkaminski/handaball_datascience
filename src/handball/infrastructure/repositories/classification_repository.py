from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import Select, and_, func, literal, or_, select
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from handball.domain.classifications import (
    FiltryKlasyfikacji,
    Klasyfikacja,
    PozycjaSkladu,
    PozycjaStrzelca,
    PozycjaTabeli,
    Sklad,
    StronaKlasyfikacji,
    SzczegolySkladu,
    SzczegolyTabeli,
)
from handball.domain.errors import BladOdczytuDanych
from handball.domain.options import OpcjaWyboru
from handball.infrastructure.database.models.classifications import (
    Strzelec,
    Tabela,
    TabelaGrupa,
    TabelaWiersz,
    ZespolRozgrywki,
)
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.rosters import SkladSezonowy
from handball.infrastructure.database.models.teams import Zespol, ZespolSezon


class KlasyfikacjaSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_sklady(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Sklad]:
        zawodnik = func.trim(
            func.concat(
                func.coalesce(SkladSezonowy.imie, ""),
                " ",
                func.coalesce(SkladSezonowy.nazwisko, ""),
            )
        )
        rozgrywki = (
            select(
                func.string_agg(
                    Rozgrywki.nazwa,
                    aggregate_order_by(literal(", "), Rozgrywki.nazwa),
                )
            )
            .select_from(ZespolRozgrywki)
            .join(Rozgrywki, Rozgrywki.id == ZespolRozgrywki.id_rozgrywki)
            .where(
                ZespolRozgrywki.id_zespol == ZespolSezon.id_zespol,
                ZespolRozgrywki.id_sezon == ZespolSezon.id_sezon,
            )
            .correlate(ZespolSezon)
            .scalar_subquery()
        )
        zapytanie = (
            select(
                ZespolSezon.id.label("id_zespol_sezon"),
                Sezon.nazwa.label("sezon"),
                ZespolSezon.nazwa.label("druzyna"),
                rozgrywki.label("rozgrywki"),
            )
            .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
            .where(
                select(SkladSezonowy.id_zawodnik)
                .where(SkladSezonowy.id_zespol_sezon == ZespolSezon.id)
                .exists()
            )
        )
        if filtry.id_rozgrywki is not None:
            zapytanie = zapytanie.where(
                select(ZespolRozgrywki.id_zespol)
                .where(
                    ZespolRozgrywki.id_zespol == ZespolSezon.id_zespol,
                    ZespolRozgrywki.id_sezon == ZespolSezon.id_sezon,
                    ZespolRozgrywki.id_rozgrywki == filtry.id_rozgrywki,
                )
                .exists()
            )
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(ZespolSezon.id_sezon == filtry.id_sezon)
        if filtry.szukaj:
            pasujacy_zawodnik = (
                select(SkladSezonowy.id_zawodnik)
                .where(
                    SkladSezonowy.id_zespol_sezon == ZespolSezon.id,
                    or_(
                        zawodnik.icontains(filtry.szukaj, autoescape=True),
                        SkladSezonowy.pozycja_nazwa.icontains(filtry.szukaj, autoescape=True),
                    ),
                )
                .exists()
            )
            zapytanie = zapytanie.where(
                or_(
                    ZespolSezon.nazwa.icontains(filtry.szukaj, autoescape=True),
                    pasujacy_zawodnik,
                )
            )
        return self._strona(zapytanie, filtry, ZespolSezon.id, lambda w: Sklad(**w), "składów")

    def pobierz_szczegoly_skladu(self, id_zespol_sezon: int) -> SzczegolySkladu | None:
        try:
            naglowek = (
                self._sesja.execute(
                    select(
                        ZespolSezon.id.label("id_zespol_sezon"),
                        Sezon.nazwa.label("sezon"),
                        ZespolSezon.nazwa.label("druzyna"),
                    )
                    .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
                    .where(ZespolSezon.id == id_zespol_sezon)
                )
                .mappings()
                .one_or_none()
            )
            if naglowek is None:
                return None
            nazwy_rozgrywek = self._sesja.scalars(
                select(Rozgrywki.nazwa)
                .join(ZespolRozgrywki, ZespolRozgrywki.id_rozgrywki == Rozgrywki.id)
                .join(
                    ZespolSezon,
                    and_(
                        ZespolSezon.id_zespol == ZespolRozgrywki.id_zespol,
                        ZespolSezon.id_sezon == ZespolRozgrywki.id_sezon,
                    ),
                )
                .where(
                    ZespolSezon.id == id_zespol_sezon,
                    select(SkladSezonowy.id_zawodnik)
                    .where(SkladSezonowy.id_zespol_sezon == ZespolSezon.id)
                    .exists(),
                )
                .distinct()
                .order_by(Rozgrywki.nazwa)
            ).all()
            sklad = Sklad(**naglowek, rozgrywki=", ".join(nazwy_rozgrywek) or None)
            zawodnicy = self._sesja.execute(
                select(
                    SkladSezonowy.id_zawodnik.label("id_zawodnik"),
                    Sezon.nazwa.label("sezon"),
                    ZespolSezon.nazwa.label("druzyna"),
                    func.trim(
                        func.concat(
                            func.coalesce(SkladSezonowy.imie, ""),
                            " ",
                            func.coalesce(SkladSezonowy.nazwisko, ""),
                        )
                    ).label("zawodnik"),
                    SkladSezonowy.nr_koszulki.label("nr_koszulki"),
                    SkladSezonowy.pozycja_nazwa.label("pozycja"),
                    SkladSezonowy.wzrost.label("wzrost"),
                    SkladSezonowy.waga.label("waga"),
                )
                .join(ZespolSezon, ZespolSezon.id == SkladSezonowy.id_zespol_sezon)
                .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
                .where(SkladSezonowy.id_zespol_sezon == id_zespol_sezon)
                .order_by(
                    SkladSezonowy.nr_koszulki.nulls_last(),
                    SkladSezonowy.nazwisko,
                    SkladSezonowy.imie,
                )
            ).mappings()
            return SzczegolySkladu(sklad, [PozycjaSkladu(**wiersz) for wiersz in zawodnicy])
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać szczegółów składu.") from wyjatek

    def pobierz_strzelcow(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[PozycjaStrzelca]:
        zawodnik = func.trim(
            func.concat(func.coalesce(Zawodnik.imie, ""), " ", func.coalesce(Zawodnik.nazwisko, ""))
        )
        zapytanie = (
            select(
                Strzelec.id.label("id"),
                Strzelec.id_zawodnik.label("id_zawodnik"),
                Sezon.nazwa.label("sezon"),
                Rozgrywki.nazwa.label("rozgrywki"),
                zawodnik.label("zawodnik"),
                Zespol.nazwa.label("druzyna"),
                Strzelec.miejsce.label("miejsce"),
                Strzelec.mecze.label("mecze"),
                Strzelec.bramki.label("bramki"),
                Strzelec.srednia.label("srednia"),
                Strzelec.karne_bramki.label("karne_bramki"),
                Strzelec.karne_liczba.label("karne_liczba"),
                Strzelec.karne_skutecznosc.label("karne_skutecznosc"),
                Strzelec.dwie_minuty.label("dwie_minuty"),
            )
            .join(Rozgrywki, Rozgrywki.id == Strzelec.id_rozgrywki)
            .join(Sezon, Sezon.id == Rozgrywki.id_sezon)
            .join(Zawodnik, Zawodnik.id == Strzelec.id_zawodnik)
            .outerjoin(Zespol, Zespol.id == Strzelec.id_zespol)
        )
        zapytanie = self._filtry_rozgrywek(zapytanie, filtry)
        if filtry.szukaj:
            zapytanie = zapytanie.where(
                or_(
                    zawodnik.icontains(filtry.szukaj, autoescape=True),
                    Zespol.nazwa.icontains(filtry.szukaj, autoescape=True),
                    Rozgrywki.nazwa.icontains(filtry.szukaj, autoescape=True),
                )
            )
        return self._strona(
            zapytanie, filtry, Strzelec.id, lambda w: PozycjaStrzelca(**w), "strzelców"
        )

    def pobierz_tabele(self, filtry: FiltryKlasyfikacji) -> StronaKlasyfikacji[Klasyfikacja]:
        zapytanie = (
            select(
                TabelaGrupa.id.label("id_tabela_grupa"),
                Sezon.nazwa.label("sezon"),
                Rozgrywki.nazwa.label("rozgrywki"),
                Tabela.tabela_nazwa.label("tabela"),
                TabelaGrupa.grupa_nazwa.label("grupa"),
            )
            .join(Tabela, Tabela.id == TabelaGrupa.id_tabela)
            .join(Rozgrywki, Rozgrywki.id == Tabela.id_rozgrywki)
            .join(Sezon, Sezon.id == Rozgrywki.id_sezon)
        )
        zapytanie = self._filtry_rozgrywek(zapytanie, filtry)
        if filtry.szukaj:
            zapytanie = zapytanie.where(
                or_(
                    Rozgrywki.nazwa.icontains(filtry.szukaj, autoescape=True),
                    Tabela.tabela_nazwa.icontains(filtry.szukaj, autoescape=True),
                    TabelaGrupa.grupa_nazwa.icontains(filtry.szukaj, autoescape=True),
                )
            )
        return self._strona(
            zapytanie, filtry, TabelaGrupa.id, lambda w: Klasyfikacja(**w), "grup tabel"
        )

    def pobierz_szczegoly_tabeli(self, id_tabela_grupa: int) -> SzczegolyTabeli | None:
        try:
            naglowek = (
                self._sesja.execute(
                    select(
                        TabelaGrupa.id.label("id_tabela_grupa"),
                        Sezon.nazwa.label("sezon"),
                        Rozgrywki.nazwa.label("rozgrywki"),
                        Tabela.tabela_nazwa.label("tabela"),
                        TabelaGrupa.grupa_nazwa.label("grupa"),
                    )
                    .join(Tabela, Tabela.id == TabelaGrupa.id_tabela)
                    .join(Rozgrywki, Rozgrywki.id == Tabela.id_rozgrywki)
                    .join(Sezon, Sezon.id == Rozgrywki.id_sezon)
                    .where(TabelaGrupa.id == id_tabela_grupa)
                )
                .mappings()
                .one_or_none()
            )
            if naglowek is None:
                return None
            zapytanie = (
                select(
                    TabelaWiersz.id.label("id"),
                    Sezon.nazwa.label("sezon"),
                    Rozgrywki.nazwa.label("rozgrywki"),
                    Tabela.tabela_nazwa.label("tabela"),
                    TabelaGrupa.grupa_nazwa.label("grupa"),
                    Zespol.nazwa.label("druzyna"),
                    TabelaWiersz.miejsce.label("miejsce"),
                    TabelaWiersz.mecze.label("mecze"),
                    TabelaWiersz.zwyciestwa.label("zwyciestwa"),
                    TabelaWiersz.remisy.label("remisy"),
                    TabelaWiersz.remis_wygrane.label("remis_wygrane"),
                    TabelaWiersz.remis_przegrane.label("remis_przegrane"),
                    TabelaWiersz.przegrane.label("przegrane"),
                    TabelaWiersz.bramki_zdobyte.label("bramki_zdobyte"),
                    TabelaWiersz.bramki_stracone.label("bramki_stracone"),
                    TabelaWiersz.punkty_zdobyte.label("punkty"),
                    TabelaWiersz.punkty_bonusowe.label("punkty_bonusowe"),
                    TabelaWiersz.kryteria.label("kryteria"),
                )
                .join(TabelaGrupa, TabelaGrupa.id == TabelaWiersz.id_tabela_grupa)
                .join(Tabela, Tabela.id == TabelaGrupa.id_tabela)
                .join(Rozgrywki, Rozgrywki.id == Tabela.id_rozgrywki)
                .join(Sezon, Sezon.id == Rozgrywki.id_sezon)
                .join(Zespol, Zespol.id == TabelaWiersz.id_zespol)
                .where(TabelaGrupa.id == id_tabela_grupa)
                .order_by(
                    TabelaWiersz.miejsce.nulls_last(),
                    TabelaWiersz.kolejnosc_zrodlowa,
                )
            )
            pozycje = self._sesja.execute(zapytanie).mappings()
            return SzczegolyTabeli(
                Klasyfikacja(**naglowek), [PozycjaTabeli(**wiersz) for wiersz in pozycje]
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać szczegółów tabeli.") from wyjatek

    def pobierz_opcje_sezonow(self) -> list[OpcjaWyboru]:
        try:
            return [
                OpcjaWyboru(i, n)
                for i, n in self._sesja.execute(
                    select(Sezon.id, Sezon.nazwa).order_by(
                        Sezon.rok_rozpoczecia.desc(), Sezon.id.desc()
                    )
                )
            ]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać sezonów.") from wyjatek

    def pobierz_opcje_rozgrywek(self, id_sezon: int | None) -> list[OpcjaWyboru]:
        zapytanie = select(Rozgrywki.id, Rozgrywki.nazwa).order_by(Rozgrywki.nazwa, Rozgrywki.id)
        if id_sezon is not None:
            zapytanie = zapytanie.where(Rozgrywki.id_sezon == id_sezon)
        try:
            return [OpcjaWyboru(i, n) for i, n in self._sesja.execute(zapytanie)]
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać rozgrywek.") from wyjatek

    def _filtry_rozgrywek(self, zapytanie: Select[Any], filtry: FiltryKlasyfikacji) -> Select[Any]:
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Rozgrywki.id_sezon == filtry.id_sezon)
        if filtry.id_rozgrywki is not None:
            zapytanie = zapytanie.where(Rozgrywki.id == filtry.id_rozgrywki)
        return zapytanie

    def _strona[T](
        self,
        zapytanie: Select[Any],
        filtry: FiltryKlasyfikacji,
        stabilna: object,
        mapper: Callable[[RowMapping], T],
        nazwa: str,
    ) -> StronaKlasyfikacji[T]:
        try:
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            numer = min(filtry.strona, ostatnia)
            kolumna = zapytanie.selected_columns[filtry.sortowanie.removeprefix("-")]
            porzadek = kolumna.desc() if filtry.sortowanie.startswith("-") else kolumna.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(porzadek.nulls_last(), cast(ColumnElement[Any], stabilna))
                .offset((numer - 1) * filtry.rozmiar_strony)
                .limit(filtry.rozmiar_strony)
            ).mappings()
            return StronaKlasyfikacji(
                [mapper(w) for w in wiersze], liczba, numer, filtry.rozmiar_strony
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych(f"Nie udało się odczytać listy {nazwa}.") from wyjatek
