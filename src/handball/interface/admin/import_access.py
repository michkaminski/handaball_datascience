import os
from hashlib import sha256
from hmac import compare_digest

from flask import Response, request


def haslo_importu() -> str:
    return os.environ.get("HDS_IMPORT_PASSWORD", "")


def logowanie_importu_poprawne(haslo: str) -> bool:
    dane = request.authorization
    podane = dane.password if dane and dane.type == "basic" else None
    if not dane or dane.username != "admin" or not podane:
        return False
    return compare_digest(sha256(podane.encode()).digest(), sha256(haslo.encode()).digest())


def odmowa_logowania_importu() -> Response:
    return Response(
        "Wymagane logowanie administratora.",
        401,
        {"WWW-Authenticate": 'Basic realm="Handball DataScience import", charset="UTF-8"'},
    )
