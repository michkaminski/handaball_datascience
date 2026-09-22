from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class ZespolRozgrywki(Baza):
    __tablename__ = "zespoly_rozgrywki"
    __table_args__ = {"schema": "public"}

    id_zespol: Mapped[int] = mapped_column(ForeignKey("public.zespoly.id"), primary_key=True)
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"), primary_key=True)
    grupa: Mapped[str | None]
    grupa_kolor: Mapped[str | None]
    id_sezon: Mapped[int] = mapped_column(ForeignKey("public.sezony.id"))


class Strzelec(Baza):
    __tablename__ = "strzelcy"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"))
    id_zawodnik: Mapped[int] = mapped_column(ForeignKey("public.zawodnicy.id"))
    id_zespol: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    mecze: Mapped[int | None] = mapped_column(SmallInteger)
    bramki: Mapped[int | None] = mapped_column(SmallInteger)
    srednia: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    dwie_minuty: Mapped[int | None] = mapped_column(SmallInteger)
    karne_liczba: Mapped[int | None] = mapped_column(SmallInteger)
    karne_bramki: Mapped[int | None] = mapped_column(SmallInteger)
    karne_skutecznosc: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    miejsce: Mapped[int | None]
    kolejnosc_zrodlowa: Mapped[int]


class Tabela(Baza):
    __tablename__ = "tabele"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"))
    tabela_id: Mapped[int]
    tabela_nazwa: Mapped[str | None]


class TabelaGrupa(Baza):
    __tablename__ = "tabele_grupy"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_tabela: Mapped[int] = mapped_column(ForeignKey("public.tabele.id"))
    grupa_id: Mapped[int]
    grupa_nazwa: Mapped[str | None]


class TabelaWiersz(Baza):
    __tablename__ = "tabele_wiersze"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_tabela_grupa: Mapped[int] = mapped_column(ForeignKey("public.tabele_grupy.id"))
    id_zespol: Mapped[int] = mapped_column(ForeignKey("public.zespoly.id"))
    mecze: Mapped[int | None] = mapped_column(SmallInteger)
    zwyciestwa: Mapped[int | None] = mapped_column(SmallInteger)
    remisy: Mapped[int | None] = mapped_column(SmallInteger)
    przegrane: Mapped[int | None] = mapped_column(SmallInteger)
    remis_wygrane: Mapped[int | None] = mapped_column(SmallInteger)
    remis_przegrane: Mapped[int | None] = mapped_column(SmallInteger)
    bramki_zdobyte: Mapped[int | None] = mapped_column(SmallInteger)
    bramki_stracone: Mapped[int | None] = mapped_column(SmallInteger)
    punkty_zdobyte: Mapped[int | None] = mapped_column(SmallInteger)
    punkty_bonusowe: Mapped[int | None] = mapped_column(SmallInteger)
    kryteria: Mapped[str | None]
    miejsce: Mapped[int | None]
    kolejnosc_zrodlowa: Mapped[int]
    id_pliku: Mapped[int | None] = mapped_column(BigInteger)
