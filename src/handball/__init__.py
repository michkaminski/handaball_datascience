from __future__ import annotations

from flask import Flask

from handball.app_factory import AplikacjaFactory
from handball.settings import Ustawienia


def create_app() -> Flask:
    ustawienia = Ustawienia.z_srodowiska()
    fabryka = AplikacjaFactory(ustawienia)
    return fabryka.utworz()
