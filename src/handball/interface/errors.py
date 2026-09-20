from __future__ import annotations

from typing import NoReturn

from flask import abort

from handball.domain.errors import BladOdczytuDanych, NieZnalezionoMeczu, NieZnalezionoZawodnika


def obsluz_blad_domeny(wyjatek: Exception) -> NoReturn:
    if isinstance(wyjatek, (NieZnalezionoMeczu, NieZnalezionoZawodnika)):
        abort(404)
    if isinstance(wyjatek, BladOdczytuDanych):
        abort(503)
    raise wyjatek
