from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Sedzia(Baza):
    __tablename__ = "sedziowie"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nazwisko: Mapped[str | None]
    miasto: Mapped[str | None]


class MeczSedzia(Baza):
    __tablename__ = "mecze_sedziowie"
    __table_args__ = {"schema": "public"}

    id_mecz: Mapped[int] = mapped_column(ForeignKey("public.mecze.id"), primary_key=True)
    rola: Mapped[str] = mapped_column(primary_key=True)
    id_sedzia: Mapped[int] = mapped_column(ForeignKey("public.sedziowie.id"))
    nazwisko: Mapped[str | None]
    miasto: Mapped[str | None]
