from __future__ import annotations

import datetime

from sqlalchemy import CHAR, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from handball.infrastructure.database.models.base import Baza


class Mecz(Baza):
    __tablename__ = "mecze"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sezon: Mapped[int] = mapped_column(ForeignKey("public.sezony.id"))
    id_rozgrywki: Mapped[int] = mapped_column(ForeignKey("public.rozgrywki.id"))
    id_kolejka: Mapped[int] = mapped_column(ForeignKey("public.kolejki.id"))
    id_zespol_gosp: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    id_zespol_gosc: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    id_hala: Mapped[int | None] = mapped_column(ForeignKey("public.hale.id"))
    lp: Mapped[int | None]
    alias_gosp: Mapped[int | None]
    alias_gosc: Mapped[int | None]
    wynik_gosp_pol: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_gosp_full: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_gosc_pol: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_gosc_full: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_temp_gosp_pol: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_temp_gosp_full: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_temp_gosc_pol: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_temp_gosc_full: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_koncowy_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_koncowy_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_bramki_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    wynik_bramki_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_1_pol_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_1_pol_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_1_full_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_1_full_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_2_pol_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_2_pol_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_2_full_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_2_full_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_karne_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    dogrywka_karne_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    karne_bramki_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    karne_bramki_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    karne_ile_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    karne_ile_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    kary_gosp: Mapped[int | None] = mapped_column(SmallInteger)
    kary_gosc: Mapped[int | None] = mapped_column(SmallInteger)
    czy_remis: Mapped[bool | None]
    zwyciezca: Mapped[int | None] = mapped_column(SmallInteger)
    timeout1_gosp: Mapped[str | None]
    timeout2_gosp: Mapped[str | None]
    timeout3_gosp: Mapped[str | None]
    timeout1_gosc: Mapped[str | None]
    timeout2_gosc: Mapped[str | None]
    timeout3_gosc: Mapped[str | None]
    data_propozycji: Mapped[datetime.datetime | None]
    data_propozycji_dzien: Mapped[str | None]
    data_faktyczna: Mapped[datetime.datetime | None]
    data_faktyczna_dzien: Mapped[str | None]
    data_ostatniej_zmiany: Mapped[datetime.datetime | None]
    zamiana: Mapped[bool | None]
    wycofany: Mapped[bool | None]
    wycofany_typ: Mapped[str | None]
    id_zespol_wycofany: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    id_zespol_walkower: Mapped[int | None] = mapped_column(ForeignKey("public.zespoly.id"))
    protokol: Mapped[str | None]
    protokol_zatwierdzony: Mapped[bool | None]
    protokol_zalacznik_plik: Mapped[str | None]
    protokol_zalacznik_typ: Mapped[str | None]
    protokol_zalacznik_nazwa: Mapped[str | None]
    komentarz: Mapped[str | None]
    widzowie: Mapped[int | None]
    transmisja: Mapped[str | None]
    transmisja_godzina: Mapped[str | None]
    bilety_url: Mapped[str | None]
    po_para_id: Mapped[int | None]
    po_para_id_gosp: Mapped[int | None]
    po_para_id_gosc: Mapped[int | None]
    rozgrywki_code: Mapped[str | None]


class MeczZawodnik(Baza):
    __tablename__ = "mecze_zawodnicy"
    __table_args__ = {"schema": "public"}

    id_mecz: Mapped[int] = mapped_column(ForeignKey("public.mecze.id"), primary_key=True)
    strona: Mapped[str] = mapped_column(CHAR(4), primary_key=True)
    id_zawodnik: Mapped[int] = mapped_column(primary_key=True)
    nr_koszulki: Mapped[int | None]
    pozycja: Mapped[str | None]
    bramki: Mapped[int | None] = mapped_column(SmallInteger)
    dwie_minuty: Mapped[int | None] = mapped_column(SmallInteger)
    upomnienie: Mapped[bool | None]
    dyskwalifikacja: Mapped[bool | None]
    kd: Mapped[int | None] = mapped_column(SmallInteger)
    wyjscie: Mapped[bool | None]
    karne_liczba: Mapped[int | None] = mapped_column(SmallInteger)
    karne_bramki: Mapped[int | None] = mapped_column(SmallInteger)
    karne_liczba_seria: Mapped[int | None] = mapped_column(SmallInteger)
    karne_bramki_seria: Mapped[int | None] = mapped_column(SmallInteger)
    imie: Mapped[str | None]
    nazwisko: Mapped[str | None]
