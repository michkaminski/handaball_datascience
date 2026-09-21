from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from handball.domain.catalogs import FiltryKatalogu, PozycjaHali, StronaKatalogu
from handball.domain.errors import BladOdczytuDanych
from handball.infrastructure.database.models.matches import Mecz
from handball.infrastructure.database.models.venues import Hala


class HalaKatalogSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_hale(self, filtry: FiltryKatalogu) -> StronaKatalogu[PozycjaHali]:
        try:
            zapytanie = self._zapytanie(filtry)
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            ostatnia = max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            numer = min(filtry.strona, ostatnia)
            kolumna = zapytanie.selected_columns[filtry.sortowanie.removeprefix("-")]
            porzadek = kolumna.desc() if filtry.sortowanie.startswith("-") else kolumna.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(porzadek.nulls_last(), Hala.id.asc())
                .offset((numer - 1) * filtry.rozmiar_strony)
                .limit(filtry.rozmiar_strony)
            ).mappings()
            pozycje = [
                PozycjaHali(
                    id=wiersz["id"],
                    nazwa=wiersz["nazwa"],
                    miasto=wiersz["miasto"],
                    adres=wiersz["adres"] or None,
                    pojemnosc=wiersz["pojemnosc"],
                    liczba_meczow=wiersz["liczba_meczow"],
                )
                for wiersz in wiersze
            ]
            return StronaKatalogu(pozycje, liczba, numer, filtry.rozmiar_strony)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać listy hal.") from wyjatek

    def _zapytanie(self, filtry: FiltryKatalogu) -> Select[tuple[object, ...]]:
        adres = func.concat_ws(
            " ",
            func.nullif(func.trim(Hala.ulica), ""),
            func.nullif(func.trim(Hala.numer), ""),
        )
        zapytanie = (
            select(
                Hala.id.label("id"),
                Hala.nazwa.label("nazwa"),
                Hala.miasto.label("miasto"),
                adres.label("adres"),
                Hala.pojemnosc.label("pojemnosc"),
                func.count(Mecz.id).label("liczba_meczow"),
            )
            .outerjoin(Mecz, Mecz.id_hala == Hala.id)
            .group_by(Hala.id, Hala.nazwa, Hala.miasto, Hala.ulica, Hala.numer, Hala.pojemnosc)
        )
        if filtry.szukaj:
            zapytanie = zapytanie.where(
                or_(
                    Hala.nazwa.icontains(filtry.szukaj, autoescape=True),
                    Hala.miasto.icontains(filtry.szukaj, autoescape=True),
                    Hala.ulica.icontains(filtry.szukaj, autoescape=True),
                    Hala.numer.icontains(filtry.szukaj, autoescape=True),
                )
            )
        if filtry.miasto:
            zapytanie = zapytanie.where(Hala.miasto.icontains(filtry.miasto, autoescape=True))
        if filtry.pojemnosc_min is not None:
            zapytanie = zapytanie.where(Hala.pojemnosc >= filtry.pojemnosc_min)
        return zapytanie
