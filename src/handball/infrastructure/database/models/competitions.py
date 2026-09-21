from __future__ import annotations

import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Sezon(Baza):
    __tablename__ = "sezony"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nazwa: Mapped[str]
    rok_rozpoczecia: Mapped[int | None]
    ile_rozgrywek: Mapped[int | None]
    stan: Mapped[str | None]


class Rozgrywki(Baza):
    __tablename__ = "rozgrywki"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sezon: Mapped[int] = mapped_column(ForeignKey("public.sezony.id"))
    nazwa: Mapped[str]
    plec: Mapped[str | None]
    ile_zespolow: Mapped[int | None]


class Runda(Baza):
    __tablename__ = "rundy"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"))
    nazwa: Mapped[str | None]


class Kolejka(Baza):
    __tablename__ = "kolejki"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_runda: Mapped[int] = mapped_column(ForeignKey("public.rundy.id"))
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"))
    nazwa: Mapped[str | None]
    nr: Mapped[int | None]
    data_start: Mapped[datetime.datetime | None]
    data_koniec: Mapped[datetime.datetime | None]
