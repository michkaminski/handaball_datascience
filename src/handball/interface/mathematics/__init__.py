from flask import Blueprint

from handball.interface.mathematics.views import (
    MatematykaArtykulView,
    MatematykaDzialView,
    MatematykaIndeksView,
)
from handball.request_dependencies import ZaleznosciZadaniaFactory


def utworz_blueprint_matematyki(fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> Blueprint:
    blueprint = Blueprint("matematyka", __name__, url_prefix="/matematyka")
    blueprint.add_url_rule(
        "/", view_func=MatematykaIndeksView.as_view("indeks", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/<dzial>/", view_func=MatematykaDzialView.as_view("dzial", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/<dzial>/<slug>/",
        view_func=MatematykaArtykulView.as_view("artykul", fabryka_zaleznosci),
    )
    return blueprint
