from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Zespol(Baza):
    __tablename__ = "zespoly"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nr_klubu: Mapped[int | None]
    nazwa: Mapped[str | None]
    plec: Mapped[str | None]
    kategoria: Mapped[str | None]
    wycofany: Mapped[bool | None]


class ZespolSezon(Baza):
    __tablename__ = "zespoly_sezony"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_zespol: Mapped[int] = mapped_column(ForeignKey("public.zespoly.id"))
    id_sezon: Mapped[int] = mapped_column(ForeignKey("public.sezony.id"))
    nazwa: Mapped[str | None]
    plec: Mapped[str | None]
    kategoria: Mapped[str | None]
    miasto: Mapped[str | None]
    wycofany: Mapped[bool | None]
