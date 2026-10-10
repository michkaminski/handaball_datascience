from __future__ import annotations

from collections.abc import Callable

from flask import Response, abort, jsonify, request
from flask.views import MethodView

from handball.domain.attendance_appeal import model_maf
from handball.request_dependencies import ZaleznosciZadaniaFactory
from handball.services.attendance_appeal_service import (
    AtrakcyjnoscFrekwencyjnaService,
    BrakModeluMaf,
)
from maf.forecast import ForecastScenario, parse_hour

JsonDict = dict[str, object]


class _AtrakcyjnoscApiView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def _odpowiedz(
        self, akcja: Callable[[AtrakcyjnoscFrekwencyjnaService, str], JsonDict]
    ) -> Response:
        serwis = self._fabryka.utworz_serwis_atrakcyjnosci()
        klucz = model_maf(request.args.get("model")).spec.key
        try:
            wynik = akcja(serwis, klucz)
        except BrakModeluMaf:
            return _blad(
                404,
                f"Model {klucz} nie został jeszcze wytrenowany. Uruchom: "
                f"uv run python -m handball.maf_cli {klucz}",
            )
        except KeyError as wyjatek:
            return _blad(404, f"Brak obiektu w modelu: {wyjatek}")
        except ValueError as wyjatek:
            return _blad(400, str(wyjatek))
        return jsonify(wynik)


def _blad(kod: int, komunikat: str) -> Response:
    odpowiedz = jsonify({"blad": komunikat})
    odpowiedz.status_code = kod
    return odpowiedz


def _liczba(nazwa: str) -> int:
    wartosc = request.args.get(nazwa, "")
    if not wartosc.lstrip("-").isdigit():
        abort(400, description=f"parametr {nazwa} musi być liczbą całkowitą")
    return int(wartosc)


def _liczba_opcjonalna(nazwa: str) -> int | None:
    wartosc = request.args.get(nazwa, "").strip()
    return _liczba(nazwa) if wartosc else None


class AtrakcyjnoscPanelView(_AtrakcyjnoscApiView):
    def get(self) -> Response:
        return self._odpowiedz(lambda serwis, klucz: serwis.panel(klucz))


class AtrakcyjnoscKlubView(_AtrakcyjnoscApiView):
    def get(self, id_klubu: int) -> Response:
        return self._odpowiedz(lambda serwis, klucz: serwis.klub(klucz, id_klubu))


class AtrakcyjnoscGospodarzView(_AtrakcyjnoscApiView):
    def get(self, id_klubu: int) -> Response:
        return self._odpowiedz(lambda serwis, klucz: serwis.gospodarz(klucz, id_klubu))


class AtrakcyjnoscPorownanieView(_AtrakcyjnoscApiView):
    def get(self) -> Response:
        pierwszy, drugi = _liczba("a"), _liczba("b")
        return self._odpowiedz(lambda serwis, klucz: serwis.porownanie(klucz, pierwszy, drugi))


class AtrakcyjnoscPrognozaView(_AtrakcyjnoscApiView):
    def get(self) -> Response:
        try:
            godzina = parse_hour(request.args.get("godzina") or None)
        except ValueError:
            return _blad(400, "godzina w formacie GG:MM")
        dzien = _liczba("dzien")
        if not 0 <= dzien <= 6:
            return _blad(400, "dzień tygodnia 0–6")
        scenariusz = ForecastScenario(
            host_id=_liczba("gospodarz"),
            opponent_id=_liczba("rywal"),
            competition_key=request.args.get("rozgrywki") or None,
            season_key=request.args.get("sezon") or None,
            capacity=_liczba_opcjonalna("pojemnosc"),
            weekday=dzien,
            hour=godzina,
            phase=request.args.get("faza", "regular"),
            threshold=_liczba_opcjonalna("prog"),
        )
        return self._odpowiedz(lambda serwis, klucz: serwis.prognoza(klucz, scenariusz))


class AtrakcyjnoscEksportView(MethodView):
    def __init__(self, fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> None:
        self._fabryka = fabryka_zaleznosci

    def get(self) -> Response:
        serwis = self._fabryka.utworz_serwis_atrakcyjnosci()
        klucz = model_maf(request.args.get("model")).spec.key
        try:
            tresc = serwis.eksport_csv(klucz)
        except BrakModeluMaf:
            abort(404)
        return Response(
            "﻿" + tresc,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=maf_{klucz}.csv"},
        )
