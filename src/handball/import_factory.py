from __future__ import annotations

import os
from hashlib import sha256
from pathlib import Path

from flask import Flask

from handball.extensions import baza_danych
from handball.infrastructure.import_store import ImportFileStore
from handball.infrastructure.repositories.import_repository import ImportSQLAlchemyRepository
from handball.infrastructure.zprp_client import ZprpClient
from handball.interface.admin.views.import_views import ImportPanelView
from handball.services.import_service import ImportService


class ImportRegistrar:
    def zarejestruj(self, aplikacja: Flask) -> None:
        haslo = os.environ.get("HDS_IMPORT_PASSWORD", "")
        if haslo:
            aplikacja.secret_key = sha256(("hds-session:" + haslo).encode()).hexdigest()
        aplikacja.config["SESSION_COOKIE_HTTPONLY"] = True
        aplikacja.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        magazyn = ImportFileStore(Path(aplikacja.instance_path) / "imports")
        with aplikacja.app_context():
            repozytorium = ImportSQLAlchemyRepository(baza_danych.engine, magazyn)
        serwis = ImportService(magazyn, ZprpClient(), repozytorium)
        widok = ImportPanelView.as_view("administracja.import_danych", serwis, haslo)
        aplikacja.add_url_rule(
            "/administracja/import", view_func=widok, defaults={"identyfikator": None}
        )
        aplikacja.add_url_rule("/administracja/import/<uuid:identyfikator>", view_func=widok)
