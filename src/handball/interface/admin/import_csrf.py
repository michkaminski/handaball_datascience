from secrets import token_urlsafe

from flask import session


def token_importu() -> str:
    token = session.get("import_csrf")
    if not isinstance(token, str):
        token = token_urlsafe(32)
        session["import_csrf"] = token
    return token
