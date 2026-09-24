from collections import defaultdict
from dataclasses import fields

from sqlalchemy import Integer, Select, and_, case, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoZawodnika
from handball.domain.matches import DaneMeczu, PozycjaListyMeczow, ZawodnikMeczu
from handball.domain.player_details import (
    AnalitykaMeczuZawodnika,
    DaneSezonoweZawodnika,
    FiltryMeczowZawodnika,
    MeczZawodnika,
    StronaMeczowZawodnika,
    SzczegolyZawodnika,
    WpisMeczowyZawodnika,
)
from handball.infrastructure.database.match_sides import StronyMeczuSql
from handball.infrastructure.database.models.competitions import Rozgrywki, Sezon
from handball.infrastructure.database.models.matches import Mecz, MeczZawodnik
from handball.infrastructure.database.models.players import Zawodnik
from handball.infrastructure.database.models.rosters import Pozycja, SkladSezonowy
from handball.infrastructure.database.models.teams import ZespolSezon


class SzczegolyZawodnikaSQLAlchemyRepository:
    def __init__(self, sesja: Session) -> None:
        self._sesja = sesja

    def pobierz_szczegoly(self, id_zawodnik: int) -> SzczegolyZawodnika:
        try:
            zawodnik = self._sesja.get(Zawodnik, id_zawodnik)
            if zawodnik is None:
                raise NieZnalezionoZawodnika(id_zawodnik)
            wiersze = self._sesja.execute(
                select(
                    SkladSezonowy,
                    Sezon.nazwa,
                    ZespolSezon.nazwa,
                    Pozycja.nazwa,
                    ZespolSezon.id_sezon,
                    ZespolSezon.id_zespol,
                )
                .join(ZespolSezon, ZespolSezon.id == SkladSezonowy.id_zespol_sezon)
                .join(Sezon, Sezon.id == ZespolSezon.id_sezon)
                .outerjoin(Pozycja, Pozycja.id == SkladSezonowy.id_pozycja)
                .where(SkladSezonowy.id_zawodnik == id_zawodnik)
                .order_by(
                    Sezon.rok_rozpoczecia.desc().nulls_last(),
                    Sezon.id.desc(),
                    ZespolSezon.nazwa.asc().nulls_last(),
                    SkladSezonowy.id_zespol_sezon,
                )
            ).all()
            statystyki = self._pobierz_statystyki_sezonowe(id_zawodnik)
            sezony = []
            for sklad, sezon, druzyna, pozycja, id_sezon, id_zespol in wiersze:
                podsumowania = statystyki.get((id_sezon, id_zespol), [None])
                for podsumowanie in podsumowania:
                    sezony.append(
                        DaneSezonoweZawodnika(
                            sklad.id_zespol_sezon,
                            sezon,
                            druzyna,
                            sklad.nr_koszulki,
                            sklad.pozycja_nazwa or pozycja,
                            sklad.wzrost,
                            sklad.waga,
                            *(podsumowanie or (None,) * 7),
                        )
                    )
            return SzczegolyZawodnika(
                id_zawodnik=zawodnik.id,
                imie=zawodnik.imie,
                nazwisko=zawodnik.nazwisko,
                data_urodzenia=zawodnik.data_urodzenia,
                foto_url=zawodnik.foto_url,
                sezony=tuple(sezony),
            )
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać karty zawodnika.") from wyjatek

    def _pobierz_statystyki_sezonowe(
        self, id_zawodnik: int
    ) -> dict[
        tuple[int, int],
        list[
            tuple[
                str,
                int | None,
                int | None,
                int | None,
                int | None,
                int | None,
                int | None,
            ]
        ],
    ]:
        id_zespol = StronyMeczuSql.zespol(MeczZawodnik.strona)
        zapytanie = (
            select(
                Mecz.id_sezon,
                id_zespol.label("id_zespol"),
                Rozgrywki.nazwa,
                func.sum(MeczZawodnik.bramki),
                func.sum(MeczZawodnik.karne_bramki),
                func.sum(MeczZawodnik.karne_liczba),
                func.sum(MeczZawodnik.dwie_minuty),
                func.sum(func.cast(MeczZawodnik.upomnienie, Integer)),
                func.sum(func.cast(MeczZawodnik.dyskwalifikacja, Integer)),
            )
            .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .where(
                MeczZawodnik.id_zawodnik == id_zawodnik,
                MeczZawodnik.strona.in_(("gosp", "gosc")),
            )
            .group_by(Mecz.id_sezon, id_zespol, Rozgrywki.nazwa)
            .order_by(Rozgrywki.nazwa)
        )
        wynik = defaultdict(list)
        for id_sezon, zespol, *wartosci in self._sesja.execute(zapytanie).all():
            if zespol is not None:
                wynik[(id_sezon, zespol)].append(tuple(wartosci))
        return dict(wynik)

    def pobierz_mecze(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> StronaMeczowZawodnika:
        try:
            zapytanie = self._zapytanie_meczow(id_zawodnik, filtry)
            liczba = self._sesja.scalar(select(func.count()).select_from(zapytanie.subquery())) or 0
            numer = min(
                filtry.strona, max(1, (liczba + filtry.rozmiar_strony - 1) // filtry.rozmiar_strony)
            )
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            porzadek = termin.desc() if filtry.sortowanie == "-data" else termin.asc()
            wiersze = self._sesja.execute(
                zapytanie.order_by(porzadek.nulls_last(), Mecz.id)
                .limit(filtry.rozmiar_strony)
                .offset((numer - 1) * filtry.rozmiar_strony)
            ).all()
            wpisy: dict[int, list[WpisMeczowyZawodnika]] = defaultdict(list)
            identyfikatory = [wiersz[0].id for wiersz in wiersze]
            if identyfikatory:
                for wpis in self._sesja.scalars(
                    select(MeczZawodnik)
                    .where(
                        MeczZawodnik.id_zawodnik == id_zawodnik,
                        MeczZawodnik.id_mecz.in_(identyfikatory),
                    )
                    .order_by(MeczZawodnik.id_mecz, MeczZawodnik.strona)
                ):
                    wpisy[wpis.id_mecz].append(
                        WpisMeczowyZawodnika(
                            wpis.strona.strip(),
                            ZawodnikMeczu(
                                nr_koszulki=wpis.nr_koszulki,
                                pozycja=wpis.pozycja,
                                bramki=wpis.bramki,
                                dwie_minuty=wpis.dwie_minuty,
                                upomnienie=wpis.upomnienie,
                                dyskwalifikacja=wpis.dyskwalifikacja,
                                kd=wpis.kd,
                                wyjscie=wpis.wyjscie,
                                karne_bramki=wpis.karne_bramki,
                                karne_liczba=wpis.karne_liczba,
                                karne_bramki_seria=wpis.karne_bramki_seria,
                                karne_liczba_seria=wpis.karne_liczba_seria,
                            ),
                        )
                    )
            pozycje = [
                MeczZawodnika(
                    PozycjaListyMeczow(
                        id_mecz=mecz.id,
                        termin=mecz.data_faktyczna or mecz.data_propozycji,
                        sezon=sezon,
                        rozgrywki=rozgrywki,
                        gospodarz=gospodarz,
                        gosc=gosc,
                        mecz=DaneMeczu(
                            **{pole.name: getattr(mecz, pole.name) for pole in fields(DaneMeczu)}
                        ),
                        hala=None,
                    ),
                    tuple(wpisy[mecz.id]),
                )
                for mecz, sezon, rozgrywki, gospodarz, gosc in wiersze
            ]
            return StronaMeczowZawodnika(pozycje, liczba, numer, filtry.rozmiar_strony)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać meczów zawodnika.") from wyjatek

    def pobierz_analityke(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> tuple[AnalitykaMeczuZawodnika, ...]:
        try:
            termin = func.coalesce(Mecz.data_faktyczna, Mecz.data_propozycji)
            miejsce = case(
                (MeczZawodnik.strona == "gosp", "dom"), (MeczZawodnik.strona == "gosc", "wyjazd")
            )
            zapytanie = (
                select(
                    Mecz.id,
                    termin,
                    Sezon.nazwa,
                    Rozgrywki.nazwa,
                    func.sum(MeczZawodnik.bramki),
                    func.sum(MeczZawodnik.karne_bramki),
                    func.sum(MeczZawodnik.karne_liczba),
                    func.sum(MeczZawodnik.dwie_minuty),
                    func.sum(func.cast(MeczZawodnik.upomnienie, Integer)),
                    func.sum(func.cast(MeczZawodnik.dyskwalifikacja, Integer)),
                    func.max(miejsce),
                    func.count(func.distinct(miejsce)),
                )
                .join(Mecz, Mecz.id == MeczZawodnik.id_mecz)
                .join(Sezon, Sezon.id == Mecz.id_sezon)
                .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
                .where(MeczZawodnik.id_zawodnik == id_zawodnik)
                .group_by(Mecz.id, termin, Sezon.nazwa, Rozgrywki.nazwa)
                .order_by(termin.asc().nulls_last(), Mecz.id)
            )
            if filtry.id_sezon is not None:
                zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
            if filtry.rozgrywki:
                zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
            if filtry.przeciwnik:
                zespoly = select(ZespolSezon.id_zespol).where(
                    ZespolSezon.nazwa.icontains(filtry.przeciwnik, autoescape=True)
                )
                zapytanie = zapytanie.where(StronyMeczuSql.rywal(MeczZawodnik.strona).in_(zespoly))
            wynik = []
            for *podstawowe, miejsce_wartosc, liczba_miejsc in self._sesja.execute(zapytanie):
                podstawowe.append(miejsce_wartosc if liczba_miejsc == 1 else None)
                wynik.append(AnalitykaMeczuZawodnika(*podstawowe))
            return tuple(wynik)
        except SQLAlchemyError as wyjatek:
            raise BladOdczytuDanych("Nie udało się odczytać analityki zawodnika.") from wyjatek

    def _zapytanie_meczow(
        self, id_zawodnik: int, filtry: FiltryMeczowZawodnika
    ) -> Select[tuple[Mecz, str, str, str | None, str | None]]:
        gospodarz = aliased(ZespolSezon)
        gosc = aliased(ZespolSezon)
        wpisy = select(MeczZawodnik.id_mecz).where(
            MeczZawodnik.id_mecz == Mecz.id, MeczZawodnik.id_zawodnik == id_zawodnik
        )
        if filtry.przeciwnik:
            zespoly = select(ZespolSezon.id_zespol).where(
                ZespolSezon.nazwa.icontains(filtry.przeciwnik, autoescape=True)
            )
            wpisy = wpisy.where(StronyMeczuSql.rywal(MeczZawodnik.strona).in_(zespoly))
        zapytanie = (
            select(Mecz, Sezon.nazwa, Rozgrywki.nazwa, gospodarz.nazwa, gosc.nazwa)
            .join(Sezon, Sezon.id == Mecz.id_sezon)
            .join(Rozgrywki, Rozgrywki.id == Mecz.id_rozgrywki)
            .outerjoin(
                gospodarz,
                and_(
                    gospodarz.id_zespol == Mecz.id_zespol_gosp,
                    gospodarz.id_sezon == Mecz.id_sezon,
                ),
            )
            .outerjoin(
                gosc,
                and_(
                    gosc.id_zespol == Mecz.id_zespol_gosc,
                    gosc.id_sezon == Mecz.id_sezon,
                ),
            )
            .where(wpisy.exists())
        )
        if filtry.id_sezon is not None:
            zapytanie = zapytanie.where(Mecz.id_sezon == filtry.id_sezon)
        if filtry.rozgrywki:
            zapytanie = zapytanie.where(Rozgrywki.nazwa == filtry.rozgrywki)
        return zapytanie
