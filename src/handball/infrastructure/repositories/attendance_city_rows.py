from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from handball.domain.attendance_aggregate import AgregatFrekwencji
from handball.domain.attendance_cities import MiastoFrekwencji, WkladMiasta
from handball.domain.attendance_city_breakdowns import HalaMiasta, RozgrywkiMiasta, SezonMiasta
from handball.infrastructure.repositories.attendance_rows import (
    agregat_z_wiersza,
    rozklad_z_wiersza,
)


def miasto_z_wiersza(wiersz: Mapping[str, Any]) -> MiastoFrekwencji:
    return MiastoFrekwencji(
        **agregat_z_wiersza(wiersz),
        miasto=str(wiersz["miasto"]),
        liczba_klubow=int(wiersz["liczba_klubow"]),
        liczba_rozgrywek=int(wiersz["liczba_rozgrywek"]),
        rozklad=rozklad_z_wiersza(wiersz),
    )


def wklad_z_wiersza(wiersz: Mapping[str, Any]) -> WkladMiasta:
    return WkladMiasta(
        miasto=str(wiersz["miasto"]),
        id_zespol=int(wiersz["id_zespol"]),
        klub=str(wiersz["klub"]),
        rozgrywki=str(wiersz["rozgrywki"]),
        agregat=AgregatFrekwencji(**agregat_z_wiersza(wiersz)),
    )


def sezon_z_wiersza(wiersz: Mapping[str, Any]) -> SezonMiasta:
    rok = wiersz["rok_poczatku"]
    return SezonMiasta(
        klucz=str(wiersz["klucz"]),
        sezon=str(wiersz["sezon"]),
        rok_poczatku=None if rok is None else int(rok),
        agregat=AgregatFrekwencji(**agregat_z_wiersza(wiersz)),
        rozklad=rozklad_z_wiersza(wiersz),
    )


def rozgrywki_z_wiersza(wiersz: Mapping[str, Any]) -> RozgrywkiMiasta:
    return RozgrywkiMiasta(
        klucz=str(wiersz["klucz"]),
        rozgrywki=str(wiersz["rozgrywki"]),
        liczba_klubow=int(wiersz["liczba_klubow"]),
        agregat=AgregatFrekwencji(**agregat_z_wiersza(wiersz)),
        rozklad=rozklad_z_wiersza(wiersz),
    )


def hala_z_wiersza(wiersz: Mapping[str, Any]) -> HalaMiasta:
    return HalaMiasta(
        klucz=str(wiersz["klucz"]),
        id_hala=int(wiersz["id_hala"]),
        hala=str(wiersz["hala"]),
        miasto_hali=wiersz["miasto_hali"],
        agregat=AgregatFrekwencji(**agregat_z_wiersza(wiersz)),
        rozklad=rozklad_z_wiersza(wiersz),
    )
