from __future__ import annotations

from flask import Flask

from pilka_reczna.fabryka import FabrykaAplikacji
from pilka_reczna.ustawienia import Ustawienia


def create_app() -> Flask:
    ustawienia = Ustawienia.z_srodowiska()
    fabryka = FabrykaAplikacji(ustawienia)
    return fabryka.utworz()
