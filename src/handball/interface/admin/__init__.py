from flask import Blueprint

from handball.interface.admin.views.attendance_analytics_views import FrekwencjaView
from handball.interface.admin.views.attendance_appeal_views import (
    AtrakcyjnoscEksportView,
    AtrakcyjnoscGospodarzView,
    AtrakcyjnoscKlubView,
    AtrakcyjnoscPanelView,
    AtrakcyjnoscPorownanieView,
    AtrakcyjnoscPrognozaView,
)
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
from handball.interface.admin.views.database_stats_views import StatystykiBazyView
from handball.interface.admin.views.distribution_views import (
    MeczeRozkladuBramekView,
    RozkladBramekView,
    RozkladyListView,
)
from handball.interface.admin.views.match_views import MeczListView, MeczSzczegolyView
from handball.interface.admin.views.opponent_defense_views import DefensywaRywalaZawodnikaView
from handball.interface.admin.views.player_detail_views import ZawodnikSzczegolyView
from handball.interface.admin.views.player_views import ZawodnikListView
from handball.interface.admin.views.referee_detail_views import SedziaSzczegolyView
from handball.interface.admin.views.report_views import (
    PrognozaMeczuSzczegolyView,
    PrognozyMeczowListView,
    RaportyListView,
    TypowaniaMeczowView,
)
from handball.interface.admin.views.schedule_views import (
    ProtokolMeczuPdfView,
    TerminarzView,
    TypowaniaKolejkiView,
    ZapowiedzMeczuPdfView,
    ZapowiedzMeczuView,
)
from handball.interface.admin.views.start import StartView
from handball.interface.admin.views.team_detail_views import DruzynaSzczegolyView
from handball.interface.admin.views.team_report_views import (
    RaportDruzynyPdfView,
    RaportyDruzynListView,
    ZestawieniaDruzynyPdfView,
)
from handball.interface.admin.views.venue_detail_views import HalaSzczegolyView
from handball.interface.admin.views.venue_views import HalaListView
from handball.request_dependencies import ZaleznosciZadaniaFactory


def utworz_blueprint_administracji(fabryka_zaleznosci: ZaleznosciZadaniaFactory) -> Blueprint:
    blueprint = Blueprint("administracja", __name__, url_prefix="/administracja")
    blueprint.add_url_rule("/", view_func=StartView.as_view("start", fabryka_zaleznosci))
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
        "/druzyny/<int:id_zespol>",
        view_func=DruzynaSzczegolyView.as_view("szczegoly_druzyny", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/druzyny/<int:id_zespol>/raport",
        view_func=RaportDruzynyPdfView.as_view("raport_druzyny_pdf", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/druzyny/<int:id_zespol>/zestawienia",
        view_func=ZestawieniaDruzynyPdfView.as_view("zestawienia_druzyny_pdf", fabryka_zaleznosci),
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
        "/terminarz", view_func=TerminarzView.as_view("terminarz", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/terminarz/typowania",
        view_func=TypowaniaKolejkiView.as_view("typowania_kolejki", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/terminarz/<int:id_mecz>",
        view_func=ZapowiedzMeczuView.as_view("zapowiedz_meczu", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/terminarz/<int:id_mecz>/pdf",
        view_func=ZapowiedzMeczuPdfView.as_view("zapowiedz_meczu_pdf", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/terminarz/<int:id_mecz>/protokol",
        view_func=ProtokolMeczuPdfView.as_view("protokol_meczu_pdf", fabryka_zaleznosci),
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
    blueprint.add_url_rule(
        "/raporty", view_func=RaportyListView.as_view("lista_raportow", fabryka_zaleznosci)
    )
    blueprint.add_url_rule(
        "/raporty/prognozy-meczow",
        view_func=PrognozyMeczowListView.as_view("raport_prognoz_meczow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/raporty/prognozy-meczow/<int:id_mecz>",
        view_func=PrognozaMeczuSzczegolyView.as_view(
            "szczegoly_prognozy_meczu", fabryka_zaleznosci
        ),
    )
    blueprint.add_url_rule(
        "/raporty/druzyny",
        view_func=RaportyDruzynListView.as_view("raporty_druzyn", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/raporty/rozklady",
        view_func=RozkladyListView.as_view("lista_rozkladow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/raporty/rozklady/bramki",
        view_func=RozkladBramekView.as_view("rozklad_bramek", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/raporty/rozklady/bramki/mecze",
        view_func=MeczeRozkladuBramekView.as_view("mecze_rozkladu_bramek", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/raporty/frekwencja",
        view_func=FrekwencjaView.as_view("raport_frekwencji", fabryka_zaleznosci),
    )
    for sciezka, widok, nazwa in (
        ("/raporty/frekwencja/maf/dane", AtrakcyjnoscPanelView, "maf_dane"),
        ("/raporty/frekwencja/maf/klub/<int:id_klubu>", AtrakcyjnoscKlubView, "maf_klub"),
        (
            "/raporty/frekwencja/maf/gospodarz/<int:id_klubu>",
            AtrakcyjnoscGospodarzView,
            "maf_gospodarz",
        ),
        ("/raporty/frekwencja/maf/porownanie", AtrakcyjnoscPorownanieView, "maf_porownanie"),
        ("/raporty/frekwencja/maf/prognoza", AtrakcyjnoscPrognozaView, "maf_prognoza"),
        ("/raporty/frekwencja/maf/eksport.csv", AtrakcyjnoscEksportView, "maf_eksport"),
    ):
        blueprint.add_url_rule(sciezka, view_func=widok.as_view(nazwa, fabryka_zaleznosci))
    blueprint.add_url_rule(
        "/raporty/typowania-meczow",
        view_func=TypowaniaMeczowView.as_view("raport_typowan_meczow", fabryka_zaleznosci),
    )
    blueprint.add_url_rule(
        "/statystyki-tabel",
        view_func=StatystykiBazyView.as_view("statystyki_tabel", fabryka_zaleznosci),
    )
    return blueprint
