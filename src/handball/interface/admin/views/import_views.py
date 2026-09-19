from __future__ import annotations

from hashlib import sha256
from hmac import compare_digest
from secrets import token_urlsafe
from uuid import UUID

from flask import Response, make_response, redirect, render_template, request, session, url_for
from flask.views import MethodView

from handball.domain.imports import LIGI_IMPORTU, BladImportu
from handball.services.import_service import ImportService


class ImportPanelView(MethodView):
    def __init__(self, serwis: ImportService, haslo: str) -> None:
        self._serwis = serwis
        self._haslo = haslo

    def _dostep(self) -> Response | None:
        if not self._haslo:
            return make_response(
                render_template(
                    "admin/import/panel.html",
                    sekcja_aktywna="import",
                    ligi=LIGI_IMPORTU,
                    przebieg=None,
                    historia=[],
                    konfiguracja=False,
                ),
                503,
            )
        dane = request.authorization
        podane = dane.password if dane and dane.type == "basic" else None
        if (
            not dane
            or dane.username != "admin"
            or not podane
            or not compare_digest(
                sha256(podane.encode()).digest(), sha256(self._haslo.encode()).digest()
            )
        ):
            return Response(
                "Wymagane logowanie administratora.",
                401,
                {"WWW-Authenticate": 'Basic realm="Handball DataScience import", charset="UTF-8"'},
            )
        return None

    def get(self, identyfikator: UUID | None) -> Response:
        odmowa = self._dostep()
        if odmowa is not None:
            return odmowa
        token = session.get("import_csrf")
        if not isinstance(token, str):
            token = token_urlsafe(32)
            session["import_csrf"] = token
        try:
            przebieg = self._serwis.magazyn.pobierz(identyfikator.hex) if identyfikator else None
            odpowiedz = make_response(
                render_template(
                    "admin/import/panel.html",
                    sekcja_aktywna="import",
                    ligi=LIGI_IMPORTU,
                    przebieg=przebieg,
                    historia=self._serwis.magazyn.historia(),
                    konfiguracja=True,
                    csrf=token,
                )
            )
            odpowiedz.headers["Cache-Control"] = "no-store"
            return odpowiedz
        except BladImportu as blad:
            return make_response(str(blad), 404)

    def post(self, identyfikator: UUID | None) -> Response:
        odmowa = self._dostep()
        if odmowa is not None:
            return odmowa
        token = session.get("import_csrf")
        if not isinstance(token, str) or not compare_digest(token, request.form.get("csrf", "")):
            return make_response("Formularz wygasł. Odśwież stronę i spróbuj ponownie.", 400)
        akcja = request.form.get("akcja")
        try:
            if identyfikator is None and akcja == "rozpocznij":
                if request.form.get("sezon") != "195":
                    raise BladImportu("Obsługiwany sezon to 2026/2027.")
                przebieg = self._serwis.rozpocznij(
                    [int(v) for v in request.form.getlist("ligi")],
                    request.form.get("tryb", "pelny"),
                )
            elif identyfikator and akcja == "krok":
                przebieg = self._serwis.krok(identyfikator.hex)
            elif (
                identyfikator and akcja == "zastosuj" and request.form.get("potwierdzenie") == "tak"
            ):
                przebieg = self._serwis.zastosuj(identyfikator.hex)
            elif identyfikator and akcja == "porownaj":
                przebieg = self._serwis.odswiez_podglad(identyfikator.hex)
            else:
                raise BladImportu("Nieprawidłowa operacja importu.")
            if request.headers.get("Accept") == "application/json":
                odpowiedz = make_response(
                    {
                        "status": przebieg.status,
                        "wykonane": len(przebieg.wykonane),
                        "oczekujace": len(przebieg.kolejka),
                        "blad": przebieg.blad,
                    }
                )
                odpowiedz.headers["Cache-Control"] = "no-store"
                return odpowiedz
            return make_response(
                redirect(
                    url_for("administracja.import_danych", identyfikator=UUID(przebieg.id)), 303
                )
            )
        except (BladImportu, ValueError) as blad:
            return make_response(
                str(blad) if isinstance(blad, BladImportu) else "Nieprawidłowy wybór ligi.", 400
            )
