from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Pozycja(Baza):
    __tablename__ = "pozycje"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nazwa: Mapped[str]


class SkladSezonowy(Baza):
    __tablename__ = "sklady"
    __table_args__ = {"schema": "public"}

    id_zespol_sezon: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("public.zespoly_sezony.id"), primary_key=True
    )
    id_zawodnik: Mapped[int] = mapped_column(ForeignKey("public.zawodnicy.id"), primary_key=True)
    nr_koszulki: Mapped[int | None]
    id_pozycja: Mapped[int | None] = mapped_column(SmallInteger, ForeignKey("public.pozycje.id"))
    pozycja_nazwa: Mapped[str | None]
    wzrost: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    waga: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    foto_url: Mapped[str | None]
    imie: Mapped[str | None]
    nazwisko: Mapped[str | None]
    data_urodzenia: Mapped[date | None]
