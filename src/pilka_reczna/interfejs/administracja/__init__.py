from flask import Blueprint

from pilka_reczna.interfejs.administracja.widoki.start import WidokStartowy

blueprint_administracji = Blueprint("administracja", __name__, url_prefix="/administracja")
blueprint_administracji.add_url_rule("/", view_func=WidokStartowy.as_view("start"))
