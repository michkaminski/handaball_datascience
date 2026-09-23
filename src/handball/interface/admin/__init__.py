from flask import Blueprint

from handball.interface.admin.views.catalog_views import (
    DruzynaListView,
    RozgrywkiListView,
    SedziaListView,
    SezonListView,
)
from handball.interface.admin.views.classification_views import (
    SkladListView,
    SkladSzczegolyView,
    StrzelecListView,
    TabelaListView,
    TabelaSzczegolyView,
)
from handball.interface.admin.views.match_views import MeczListView, MeczSzczegolyView
from handball.interface.admin.views.opponent_defense_views import DefensywaRywalaZawodnikaView
from handball.interface.admin.views.player_detail_views import ZawodnikSzczegolyView
from handball.interface.admin.views.player_views import ZawodnikListView
from handball.interface.admin.views.referee_detail_views import SedziaSzczegolyView
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
        "/zawodnicy/<int:id_zawodnik>/defensywa-rywali",
        view_func=DefensywaRywalaZawodnikaView.as_view(
            "defensywa_rywala_zawodnika", fabryka_zaleznosci
        ),
    )
    blueprint.add_url_rule(
        "/hale",
        view_func=HalaListView.as_view("lista_hal", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/hale/<int:id_hala>",
        view_func=HalaSzczegolyView.as_view("szczegoly_hali", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/sedziowie",
        view_func=SedziaListView.as_view("lista_sedziow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/sedziowie/<int:id_sedzia>",
        view_func=SedziaSzczegolyView.as_view("szczegoly_sedziego", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/sklady", view_func=SkladListView.as_view("lista_skladow", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/sklady/<int:id_zespol_sezon>",
        view_func=SkladSzczegolyView.as_view("szczegoly_skladu", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/strzelcy",
        view_func=StrzelecListView.as_view("lista_strzelcow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/tabele", view_func=TabelaListView.as_view("lista_tabel", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/tabele/<int:id_tabela_grupa>",
        view_func=TabelaSzczegolyView.as_view("szczegoly_tabeli", fabryka_zaleznosci),
    )
    return blueprint
