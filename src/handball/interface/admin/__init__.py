from flask import Blueprint

from handball.interface.admin.views.catalog_views import (
    DruzynaListView,
    RozgrywkiListView,
    SezonListView,
)
from handball.interface.admin.views.match_views import MeczListView, MeczSzczegolyView
from handball.interface.admin.views.player_detail_views import ZawodnikSzczegolyView
from handball.interface.admin.views.player_views import ZawodnikListView
from handball.interface.admin.views.start import StartView
from handball.interface.admin.views.venue_detail_views import HalaSzczegolyView
from handball.interface.admin.views.venue_views import HalaListView
from handball.request_dependencies import ZaleznosciZadaniaFactory


def utworz_blueprint_administracji(fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> Blueprint:
    blueprint = Blueprint("administracja", __name__, url_prefix="/administracja")
    blueprint.add_url_rule("/", view_func=StartView.as_view("start"))
    blueprint.add_url_rule(
        "/sezony", view_func=SezonListView.as_view("lista_sezonow", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/rozgrywki",
        view_func=RozgrywkiListView.as_view("lista_rozgrywek", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/druzyny", view_func=DruzynaListView.as_view("lista_druzyn", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/mecze",
        view_func=MeczListView.as_view("lista_meczow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/mecze/<int:id_mecz>",
        view_func=MeczSzczegolyView.as_view("szczegoly_meczu", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/zawodnicy",
        view_func=ZawodnikListView.as_view("lista_zawodnikow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/zawodnicy/<int:id_zawodnik>",
        view_func=ZawodnikSzczegolyView.as_view("szczegoly_zawodnika", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/hale",
        view_func=HalaListView.as_view("lista_hal", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/hale/<int:id_hala>",
        view_func=HalaSzczegolyView.as_view("szczegoly_hali", fabryka_zaleznosci),
    )
    return blueprint
