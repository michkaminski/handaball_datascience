from __future__ import annotations

from flask import Response
from flask.views import MethodView


class WidokStartowy(MethodView):
    def get(self) -> Response:
        return Response("Handball DataScience: szkielet aplikacji dziala.", mimetype="text/plain")
