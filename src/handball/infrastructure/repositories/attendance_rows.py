from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from handball.domain.attendance_aggregate import MiaryRozkladu


def agregat_z_wiersza(wiersz: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "rozegrane": int(wiersz["rozegrane"]),
        "znane": int(wiersz["znane"]),
        "suma": int(wiersz["suma"]),
        "maksimum": wiersz["maksimum"],
    }


def rozklad_z_wiersza(wiersz: Mapping[str, Any]) -> MiaryRozkladu:
    return MiaryRozkladu(
        mediana=wiersz["mediana"],
        dominanta=wiersz["dominanta"],
        minimum=wiersz["minimum"],
    )
