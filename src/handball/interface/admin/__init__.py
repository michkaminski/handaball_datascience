from flask import Blueprint

from handball.interface.admin.views.match_views import MeczListView
from handball.interface.admin.views.start import StartView
from handball.request_dependencies import ZaleznosciZadaniaFactory


def utworz_blueprint_administracji(fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> Blueprint:
    blueprint = Blueprint("administracja", __name__, url_prefix="/administracja")
    blueprint.add_url_rule("/", view_func=StartView.as_view("start"))
    blueprint.add_url_rule(
        "/mecze",
        view_func=MeczListView.as_view("lista_meczow", fabryka_zaleznosci),
    )
    return blueprint
