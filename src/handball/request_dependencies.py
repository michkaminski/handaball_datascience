from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

from sqlalchemy.orm import Session

from handball.contracts.attendance_analytics_repository import FrekwencjaReadRepository
from handball.contracts.attendance_appeal_store import ModeleMafReadStore
from handball.contracts.classification_repository import KlasyfikacjaReadRepository
from handball.contracts.competition_repository import RozgrywkiReadRepository
from handball.contracts.core_catalog_repository import KatalogPodstawowyReadRepository
from handball.contracts.database_stats_repository import StatystykiBazyReadRepository
from handball.contracts.goal_distribution_repository import RozkladBramekReadRepository
from handball.contracts.import_schedule_repository import PobieranieMeczowReadRepository
from handball.contracts.match_prediction_repository import MeczeLigoweReadRepository
from handball.contracts.match_preview_repository import ZapowiedzMeczuReadRepository
from handball.contracts.match_protocol_repository import ProtokolMeczuReadRepository
from handball.contracts.match_repository import MeczReadRepository
from handball.contracts.match_stage_repository import EtapMeczowReadRepository
from handball.contracts.match_statistics_repository import FormaMeczuReadRepository
from handball.contracts.match_tip_repository import TypowaniaReadRepository
from handball.contracts.news_repository import AktualnosciReadRepository
from handball.contracts.opponent_defense_repository import DefensywaRywalaReadRepository
from handball.contracts.pdf_renderer import DokumentPdfRenderer
from handball.contracts.player_detail_repository import SzczegolyZawodnikaReadRepository
from handball.contracts.player_repository import ZawodnikReadRepository
from handball.contracts.referee_detail_repository import SzczegolySedziegoReadRepository
from handball.contracts.schedule_repository import TerminarzReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.contracts.team_detail_repository import SzczegolyDruzynyReadRepository
from handball.contracts.team_report_repository import KadraRaportuReadRepository
from handball.contracts.venue_catalog_repository import HalaKatalogReadRepository
from handball.contracts.venue_detail_repository import SzczegolyHaliReadRepository
from handball.contracts.venue_repository import HalaReadRepository
from handball.domain.attendance_analytics import FrekwencjaCalculator
from handball.domain.attendance_calendar import KalendarzFrekwencjiCalculator
from handball.domain.attendance_cities import MiastaFrekwencjiCalculator
from handball.domain.attendance_data_science import FrekwencjaDataScienceCalculator
from handball.domain.attendance_forecast import PrognozaFrekwencjiCalculator, RegresjaOLS
from handball.domain.attendance_opponents import PrzeciwnicyFrekwencjiCalculator
from handball.domain.competition_levels import KolejnoscRozgrywekPolicy
from handball.domain.match_predictions import (
    KwalifikacjaMeczuPolicy,
    OcenaPrognozyPolicy,
    ProgiTrafnosci,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.domain.match_preview import (
    KadraZapowiedziCalculator,
    StatystykiZapowiedziCalculator,
)
from handball.domain.match_protocol import KolejnoscZawodnikowProtokoluPolicy
from handball.domain.match_report import (
    AnalizaModeluCalculator,
    AtakDruzynyCalculator,
    TloSezonuCalculator,
)
from handball.domain.match_rules import MeczPolicy
from handball.domain.match_statistics import StatystykiMeczuCalculator
from handball.domain.team_details import KolejnoscPozycjiPolicy, WystepDruzynyPolicy
from handball.domain.team_report import KolejnoscZawodnikowRaportuPolicy, MiejscaPolicy
from handball.extensions import baza_danych
from handball.infrastructure.maf_store import katalog_modeli
from handball.infrastructure.pdf_renderer import WeasyPrintPdfRenderer
from handball.infrastructure.repositories.attendance_analytics_repository import (
    FrekwencjaSQLAlchemyRepository,
)
from handball.infrastructure.repositories.classification_repository import (
    KlasyfikacjaSQLAlchemyRepository,
)
from handball.infrastructure.repositories.competition_repository import (
    RozgrywkiSQLAlchemyRepository,
)
from handball.infrastructure.repositories.core_catalog_repository import (
    KatalogPodstawowySQLAlchemyRepository,
)
from handball.infrastructure.repositories.database_stats_repository import (
    StatystykiBazySQLAlchemyRepository,
)
from handball.infrastructure.repositories.goal_distribution_repository import (
    RozkladBramekSQLAlchemyRepository,
)
from handball.infrastructure.repositories.import_schedule_repository import (
    PobieranieMeczowSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_prediction_repository import (
    MeczeLigoweSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_preview_repository import (
    ZapowiedzMeczuSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_protocol_repository import (
    ProtokolMeczuSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository
from handball.infrastructure.repositories.match_stage_repository import (
    EtapMeczowSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_statistics_repository import (
    FormaMeczuSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_tip_repository import (
    TypowaniaSQLAlchemyRepository,
)
from handball.infrastructure.repositories.news_repository import AktualnosciSQLAlchemyRepository
from handball.infrastructure.repositories.opponent_defense_repository import (
    DefensywaRywalaSQLAlchemyRepository,
)
from handball.infrastructure.repositories.player_detail_repository import (
    SzczegolyZawodnikaSQLAlchemyRepository,
)
from handball.infrastructure.repositories.player_repository import ZawodnikSQLAlchemyRepository
from handball.infrastructure.repositories.referee_detail_repository import (
    SzczegolySedziegoSQLAlchemyRepository,
)
from handball.infrastructure.repositories.schedule_repository import (
    TerminarzSQLAlchemyRepository,
)
from handball.infrastructure.repositories.season_repository import SezonSQLAlchemyRepository
from handball.infrastructure.repositories.team_detail_repository import (
    SzczegolyDruzynySQLAlchemyRepository,
)
from handball.infrastructure.repositories.venue_catalog_repository import (
    HalaKatalogSQLAlchemyRepository,
)
from handball.infrastructure.repositories.venue_detail_repository import (
    SzczegolyHaliSQLAlchemyRepository,
)
from handball.infrastructure.repositories.venue_repository import HalaSQLAlchemyRepository
from handball.interface.match_report_charts import (
    HistogramResztBuilder,
    WykresRatinguBuilder,
    WykresSezonuBuilder,
)
from handball.interface.presenters.attendance_analytics_presenter import (
    FrekwencjaWykresPresenter,
)
from handball.interface.presenters.classification_presenter import SkladPresenter
from handball.interface.presenters.goal_statistics_presenter import StatystykiBramekPresenter
from handball.interface.presenters.match_prediction_presenter import (
    PrognozaFormat,
    PrognozaMeczuPresenter,
)
from handball.interface.presenters.match_presenter import (
    MeczFormat,
    MeczPresenter,
    SkladMeczuPresenter,
)
from handball.interface.presenters.match_protocol_live_presenter import (
    NazwaPlikuProtokoluPolicy,
    NumeryProtokoluLivePolicy,
    ProtokolLivePresenter,
)
from handball.interface.presenters.match_protocol_presenter import (
    ProtokolMeczuPresenter,
    UkladProtokoluPolicy,
)
from handball.interface.presenters.match_report_presenter import RaportMeczuPresenter
from handball.interface.presenters.match_statistics_presenter import StatystykiMeczuPresenter
from handball.interface.presenters.match_tip_presenter import TypowaniaPresenter
from handball.interface.presenters.news_presenter import AktualnosciPresenter
from handball.interface.presenters.opponent_defense_presenter import DefensywaRywalaPresenter
from handball.interface.presenters.player_detail_presenter import SzczegolyZawodnikaPresenter
from handball.interface.presenters.player_presenter import ZawodnikPresenter
from handball.interface.presenters.referee_detail_presenter import SzczegolySedziegoPresenter
from handball.interface.presenters.schedule_presenter import (
    KalendarzFormat,
    TerminarzPresenter,
    ZapowiedzMeczuPresenter,
)
from handball.interface.presenters.team_detail_presenter import SzczegolyDruzynyPresenter
from handball.interface.presenters.team_report_presenter import (
    RaportDruzynyPresenter,
    UkladRaportuPolicy,
    UkladZestawieniaPolicy,
)
from handball.interface.presenters.venue_detail_presenter import SzczegolyHaliPresenter
from handball.services.attendance_analytics_service import FrekwencjaService
from handball.services.attendance_appeal_service import (
    AtrakcyjnoscFrekwencyjnaService,
)
from handball.services.catalog_service import KatalogService
from handball.services.classification_service import KlasyfikacjaService
from handball.services.database_stats_service import StatystykiBazyService
from handball.services.goal_distribution_service import RozkladBramekService
from handball.services.goal_statistics import StatystykiBramekCalculator
from handball.services.import_schedule_service import PobieranieMeczowService
from handball.services.match_dictionary_service import SlownikiMeczowService
from handball.services.match_prediction_service import (
    BacktestPrognozService,
    KatalogModeliPrognoz,
    PodsumowaniePrognozCalculator,
    PodzialSezonowPolicy,
    PrognozaZapowiedziService,
    PrognozyModeluService,
    RaportPrognozService,
    SzczegolyPrognozyService,
)
from handball.services.match_preview_service import (
    KadraMeczuBuilder,
    ZapowiedzMeczuService,
    Zegar,
    ZegarWarszawa,
)
from handball.services.match_protocol_service import ProtokolMeczuService
from handball.services.match_report_service import RaportMeczuService
from handball.services.match_service import MeczService
from handball.services.match_statistics_service import StatystykiMeczuService
from handball.services.match_tip_service import RaportTypowanService, TypowaniaKolejkiService
from handball.services.mathematics_service import BibliotekaMatematycznaService
from handball.services.news_service import AktualnosciService
from handball.services.opponent_defense_service import DefensywaRywalaService
from handball.services.player_detail_service import (
    SzczegolyZawodnikaAnalyticsService,
    SzczegolyZawodnikaService,
)
from handball.services.player_dictionary_service import SlownikiZawodnikowService
from handball.services.player_service import ZawodnikService
from handball.services.referee_detail_service import SzczegolySedziegoService
from handball.services.schedule_service import TerminarzService
from handball.services.team_detail_service import (
    AnalitykaDruzynyService,
    BilansDruzynyCalculator,
    FrekwencjaDruzynyCalculator,
    SzczegolyDruzynyService,
    ZestawienieDruzynyService,
)
from handball.services.team_report_service import RaportDruzynyService
from handball.services.venue_detail_service import SzczegolyHaliService
from handball.services.venue_service import HalaService
from maf.artifacts import ArtifactStore
from mathlib.registry import MathRegistry, default_registry


class ZaleznosciZadaniaFactory:
    def __init__(
        self,
        fabryka_repozytorium_meczow: Callable[[], MeczReadRepository] | None = None,
        fabryka_repozytorium_sezonow: Callable[[], SezonReadRepository] | None = None,
        fabryka_repozytorium_rozgrywek: Callable[[], RozgrywkiReadRepository] | None = None,
        fabryka_repozytorium_hal: Callable[[], HalaReadRepository] | None = None,
        fabryka_repozytorium_etapow: Callable[[], EtapMeczowReadRepository] | None = None,
        fabryka_repozytorium_zawodnikow: Callable[[], ZawodnikReadRepository] | None = None,
        fabryka_szczegolow_zawodnika: Callable[[], SzczegolyZawodnikaReadRepository] | None = None,
        fabryka_katalogu_hal: Callable[[], HalaKatalogReadRepository] | None = None,
        fabryka_szczegolow_hali: Callable[[], SzczegolyHaliReadRepository] | None = None,
        fabryka_katalogu_podstawowego: Callable[[], KatalogPodstawowyReadRepository] | None = None,
        fabryka_statystyk_bazy: Callable[[], StatystykiBazyReadRepository] | None = None,
        fabryka_rozkladu_bramek: Callable[[], RozkladBramekReadRepository] | None = None,
        fabryka_szczegolow_sedziego: Callable[[], SzczegolySedziegoReadRepository] | None = None,
        fabryka_klasyfikacji: Callable[[], KlasyfikacjaReadRepository] | None = None,
        fabryka_defensywy_rywala: Callable[[], DefensywaRywalaReadRepository] | None = None,
        fabryka_aktualnosci: Callable[[], AktualnosciReadRepository] | None = None,
        fabryka_szczegolow_druzyny: Callable[[], SzczegolyDruzynyReadRepository] | None = None,
        fabryka_meczow_ligowych: Callable[[], MeczeLigoweReadRepository] | None = None,
        katalog_modeli_prognoz: KatalogModeliPrognoz | None = None,
        fabryka_terminarza: Callable[[], TerminarzReadRepository] | None = None,
        fabryka_zapowiedzi_meczu: Callable[[], ZapowiedzMeczuReadRepository] | None = None,
        zegar: Zegar | None = None,
        fabryka_typowan: Callable[[], TypowaniaReadRepository] | None = None,
        renderer_pdf: DokumentPdfRenderer | None = None,
        fabryka_protokolow: Callable[[], ProtokolMeczuReadRepository] | None = None,
        fabryka_kadr_raportu: Callable[[], KadraRaportuReadRepository] | None = None,
        fabryka_frekwencji: Callable[[], FrekwencjaReadRepository] | None = None,
        magazyn_modeli_maf: ModeleMafReadStore | None = None,
        rejestr_matematyki: MathRegistry | None = None,
        fabryka_formy_meczu: Callable[[], FormaMeczuReadRepository] | None = None,
        fabryka_pobierania_meczow: Callable[[], PobieranieMeczowReadRepository] | None = None,
    ) -> None:
        self._fabryka_pobierania_meczow = fabryka_pobierania_meczow or (
            lambda: PobieranieMeczowSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_formy_meczu = fabryka_formy_meczu or (
            lambda: FormaMeczuSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._magazyn_modeli_maf = magazyn_modeli_maf or ArtifactStore(katalog_modeli())
        self._rejestr_matematyki = rejestr_matematyki or default_registry()
        self._fabryka_frekwencji = fabryka_frekwencji or (
            lambda: FrekwencjaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_kadr_raportu = fabryka_kadr_raportu or (
            lambda: ZapowiedzMeczuSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_protokolow = fabryka_protokolow or (
            lambda: ProtokolMeczuSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._renderer_pdf = renderer_pdf or WeasyPrintPdfRenderer(
            Path(__file__).parent / "interface" / "static"
        )
        self._fabryka_typowan = fabryka_typowan or (
            lambda: TypowaniaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_terminarza = fabryka_terminarza or (
            lambda: TerminarzSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_zapowiedzi_meczu = fabryka_zapowiedzi_meczu or (
            lambda: ZapowiedzMeczuSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._zegar = zegar or ZegarWarszawa()
        self._fabryka_meczow_ligowych = fabryka_meczow_ligowych or (
            lambda: MeczeLigoweSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._katalog_modeli_prognoz = katalog_modeli_prognoz or KatalogModeliPrognoz()
        self._fabryka_szczegolow_druzyny = fabryka_szczegolow_druzyny or (
            lambda: SzczegolyDruzynySQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_aktualnosci = fabryka_aktualnosci or (
            lambda: AktualnosciSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_defensywy_rywala = fabryka_defensywy_rywala or (
            lambda: DefensywaRywalaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_klasyfikacji = fabryka_klasyfikacji or (
            lambda: KlasyfikacjaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_szczegolow_sedziego = fabryka_szczegolow_sedziego or (
            lambda: SzczegolySedziegoSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_katalogu_podstawowego = fabryka_katalogu_podstawowego or (
            lambda: KatalogPodstawowySQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_statystyk_bazy = fabryka_statystyk_bazy or (
            lambda: StatystykiBazySQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_rozkladu_bramek = fabryka_rozkladu_bramek or (
            lambda: RozkladBramekSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_szczegolow_hali = fabryka_szczegolow_hali or (
            lambda: SzczegolyHaliSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_katalogu_hal = fabryka_katalogu_hal or (
            lambda: HalaKatalogSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_szczegolow_zawodnika = fabryka_szczegolow_zawodnika or (
            lambda: SzczegolyZawodnikaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_zawodnikow = fabryka_repozytorium_zawodnikow or (
            lambda: ZawodnikSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_meczow = fabryka_repozytorium_meczow or (
            lambda: MeczSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_sezonow = fabryka_repozytorium_sezonow or (
            lambda: SezonSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_rozgrywek = fabryka_repozytorium_rozgrywek or (
            lambda: RozgrywkiSQLAlchemyRepository(cast(Session, baza_danych.session))
        )
        self._fabryka_repozytorium_hal = fabryka_repozytorium_hal or (
            lambda: HalaSQLAlchemyRepository(cast(Session, baza_danych.session))
        )

        self._fabryka_repozytorium_etapow = fabryka_repozytorium_etapow or (
            lambda: EtapMeczowSQLAlchemyRepository(cast(Session, baza_danych.session))
        )

    def utworz_serwis_aktualnosci(self) -> AktualnosciService:
        return AktualnosciService(self._fabryka_aktualnosci())

    def utworz_presenter_aktualnosci(self) -> AktualnosciPresenter:
        return AktualnosciPresenter()

    def utworz_serwis_meczow(self) -> MeczService:
        return MeczService(self._fabryka_repozytorium_meczow())

    def utworz_serwis_slownikow(self) -> SlownikiMeczowService:
        return SlownikiMeczowService(
            self._fabryka_repozytorium_sezonow(),
            self._fabryka_repozytorium_rozgrywek(),
            self._fabryka_repozytorium_hal(),
            self._fabryka_repozytorium_etapow(),
            KolejnoscRozgrywekPolicy(),
        )

    def utworz_presenter_meczow(self) -> MeczPresenter:
        formatowanie = MeczFormat()
        reguly = MeczPolicy()
        return MeczPresenter(reguly, formatowanie, SkladMeczuPresenter(formatowanie, reguly))

    def utworz_serwis_statystyk_meczu(self) -> StatystykiMeczuService:
        reguly = MeczPolicy()
        return StatystykiMeczuService(
            self._fabryka_repozytorium_meczow(),
            self._fabryka_formy_meczu(),
            StatystykiMeczuCalculator(reguly),
            reguly,
        )

    def utworz_presenter_statystyk_meczu(self) -> StatystykiMeczuPresenter:
        return StatystykiMeczuPresenter(MeczFormat())

    def utworz_serwis_raportu_meczu(self) -> RaportMeczuService:
        return RaportMeczuService(
            self.utworz_serwis_statystyk_meczu(),
            self._fabryka_zapowiedzi_meczu(),
            PrognozyModeluService(self.utworz_backtest_prognoz(), self._katalog_modeli_prognoz),
            AnalizaModeluCalculator(),
            AtakDruzynyCalculator(),
            TloSezonuCalculator(),
            StatystykiZapowiedziCalculator(),
        )

    def utworz_presenter_raportu_meczu(self) -> RaportMeczuPresenter:
        return RaportMeczuPresenter(
            self.utworz_presenter_statystyk_meczu(),
            HistogramResztBuilder(),
            WykresRatinguBuilder(),
            WykresSezonuBuilder(),
        )

    def utworz_serwis_zawodnikow(self) -> ZawodnikService:
        return ZawodnikService(self._fabryka_repozytorium_zawodnikow())

    def utworz_presenter_zawodnikow(self) -> ZawodnikPresenter:
        return ZawodnikPresenter()

    def utworz_slowniki_zawodnikow(self) -> SlownikiZawodnikowService:
        return SlownikiZawodnikowService(
            self._fabryka_repozytorium_sezonow(),
            self._fabryka_repozytorium_rozgrywek(),
            KolejnoscRozgrywekPolicy(),
        )

    def utworz_serwis_szczegolow_zawodnika(self) -> SzczegolyZawodnikaService:
        return SzczegolyZawodnikaService(self._fabryka_szczegolow_zawodnika())

    def utworz_analityke_szczegolow_zawodnika(self) -> SzczegolyZawodnikaAnalyticsService:
        return SzczegolyZawodnikaAnalyticsService(
            self._fabryka_szczegolow_zawodnika(), StatystykiBramekCalculator()
        )

    def utworz_presenter_szczegolow_zawodnika(self) -> SzczegolyZawodnikaPresenter:
        formatowanie = MeczFormat()
        return SzczegolyZawodnikaPresenter(
            formatowanie, self.utworz_presenter_meczow(), StatystykiBramekPresenter(formatowanie)
        )

    def utworz_serwis_szczegolow_druzyny(self) -> SzczegolyDruzynyService:
        return SzczegolyDruzynyService(
            self._fabryka_szczegolow_druzyny(), KolejnoscRozgrywekPolicy()
        )

    def utworz_zestawienie_druzyny(self) -> ZestawienieDruzynyService:
        return ZestawienieDruzynyService(
            self._fabryka_szczegolow_druzyny(),
            WystepDruzynyPolicy(MeczPolicy()),
            KolejnoscPozycjiPolicy(),
        )

    def utworz_analityke_druzyny(self) -> AnalitykaDruzynyService:
        return AnalitykaDruzynyService(
            self._fabryka_szczegolow_druzyny(),
            WystepDruzynyPolicy(MeczPolicy()),
            BilansDruzynyCalculator(FrekwencjaDruzynyCalculator()),
            StatystykiBramekCalculator(),
        )

    def utworz_presenter_szczegolow_druzyny(self) -> SzczegolyDruzynyPresenter:
        formatowanie = MeczFormat()
        return SzczegolyDruzynyPresenter(
            formatowanie,
            self.utworz_presenter_meczow(),
            StatystykiBramekPresenter(formatowanie),
            WystepDruzynyPolicy(MeczPolicy()),
        )

    def utworz_serwis_raportu_druzyny(self) -> RaportDruzynyService:
        return RaportDruzynyService(
            self._fabryka_szczegolow_druzyny(),
            self._fabryka_kadr_raportu(),
            self.utworz_zestawienie_druzyny(),
            BilansDruzynyCalculator(FrekwencjaDruzynyCalculator()),
            WystepDruzynyPolicy(MeczPolicy()),
            KolejnoscZawodnikowRaportuPolicy(KolejnoscPozycjiPolicy()),
            self._zegar,
        )

    def utworz_presenter_raportu_druzyny(self) -> RaportDruzynyPresenter:
        return RaportDruzynyPresenter(
            self.utworz_presenter_szczegolow_druzyny(),
            KolejnoscZawodnikowRaportuPolicy(KolejnoscPozycjiPolicy()),
            MiejscaPolicy(),
            UkladRaportuPolicy(),
            UkladZestawieniaPolicy(),
        )

    def utworz_serwis_defensywy_rywala(self) -> DefensywaRywalaService:
        return DefensywaRywalaService(self._fabryka_defensywy_rywala())

    def utworz_presenter_defensywy_rywala(self) -> DefensywaRywalaPresenter:
        return DefensywaRywalaPresenter(MeczFormat())

    def utworz_serwis_hal(self) -> HalaService:
        return HalaService(self._fabryka_katalogu_hal())

    def utworz_serwis_katalogu(self) -> KatalogService:
        return KatalogService(self._fabryka_katalogu_podstawowego())

    def utworz_serwis_statystyk_bazy(self) -> StatystykiBazyService:
        return StatystykiBazyService(self._fabryka_statystyk_bazy())

    def utworz_serwis_rozkladu_bramek(self) -> RozkladBramekService:
        return RozkladBramekService(self._fabryka_rozkladu_bramek())

    def utworz_biblioteke_matematyczna(self) -> BibliotekaMatematycznaService:
        return BibliotekaMatematycznaService(self._rejestr_matematyki)

    def utworz_serwis_atrakcyjnosci(self) -> AtrakcyjnoscFrekwencyjnaService:
        return AtrakcyjnoscFrekwencyjnaService(
            self._magazyn_modeli_maf, self.utworz_biblioteke_matematyczna()
        )

    def utworz_serwis_frekwencji(self) -> FrekwencjaService:
        return FrekwencjaService(
            self._fabryka_frekwencji(),
            FrekwencjaCalculator(),
            PrzeciwnicyFrekwencjiCalculator(),
            KalendarzFrekwencjiCalculator(),
            FrekwencjaDataScienceCalculator(PrognozaFrekwencjiCalculator(RegresjaOLS())),
            MiastaFrekwencjiCalculator(),
        )

    def utworz_presenter_frekwencji(self) -> FrekwencjaWykresPresenter:
        return FrekwencjaWykresPresenter()

    def utworz_serwis_szczegolow_hali(self) -> SzczegolyHaliService:
        return SzczegolyHaliService(self._fabryka_szczegolow_hali())

    def utworz_presenter_szczegolow_hali(self) -> SzczegolyHaliPresenter:
        return SzczegolyHaliPresenter(MeczFormat())

    def utworz_serwis_szczegolow_sedziego(self) -> SzczegolySedziegoService:
        return SzczegolySedziegoService(self._fabryka_szczegolow_sedziego())

    def utworz_presenter_szczegolow_sedziego(self) -> SzczegolySedziegoPresenter:
        return SzczegolySedziegoPresenter(MeczFormat())

    def utworz_serwis_klasyfikacji(self) -> KlasyfikacjaService:
        return KlasyfikacjaService(self._fabryka_klasyfikacji(), KolejnoscRozgrywekPolicy())

    def utworz_presenter_skladu(self) -> SkladPresenter:
        return SkladPresenter()

    def utworz_katalog_modeli_prognoz(self) -> KatalogModeliPrognoz:
        return self._katalog_modeli_prognoz

    def utworz_backtest_prognoz(self) -> BacktestPrognozService:
        wzorce = WzorceNazwLig()
        return BacktestPrognozService(
            self._fabryka_meczow_ligowych(),
            self._katalog_modeli_prognoz,
            KwalifikacjaMeczuPolicy(wzorce),
            OcenaPrognozyPolicy(ProgiTrafnosci()),
            PodzialSezonowPolicy(ZakresBacktestu()),
            wzorce,
        )

    def utworz_raport_prognoz_meczow(self) -> RaportPrognozService:
        return RaportPrognozService(
            self.utworz_backtest_prognoz(),
            self._katalog_modeli_prognoz,
            PodsumowaniePrognozCalculator(ProgiTrafnosci()),
        )

    def utworz_szczegoly_prognozy_meczu(self) -> SzczegolyPrognozyService:
        return SzczegolyPrognozyService(
            self.utworz_backtest_prognoz(), self._katalog_modeli_prognoz
        )

    def utworz_presenter_prognoz_meczow(self) -> PrognozaMeczuPresenter:
        return PrognozaMeczuPresenter(MeczFormat(), PrognozaFormat())

    def utworz_serwis_pobierania_meczow(self) -> PobieranieMeczowService:
        return PobieranieMeczowService(
            self.utworz_serwis_terminarza(), self._fabryka_pobierania_meczow()
        )

    def utworz_serwis_terminarza(self) -> TerminarzService:
        return TerminarzService(
            self._fabryka_terminarza(),
            self._fabryka_repozytorium_sezonow(),
            KolejnoscRozgrywekPolicy(),
        )

    def utworz_presenter_terminarza(self) -> TerminarzPresenter:
        return TerminarzPresenter(MeczFormat(), MeczPolicy(), KalendarzFormat())

    def utworz_prognoze_zapowiedzi(self) -> PrognozaZapowiedziService:
        return PrognozaZapowiedziService(
            self.utworz_backtest_prognoz(),
            self._katalog_modeli_prognoz,
            KwalifikacjaMeczuPolicy(WzorceNazwLig()),
        )

    def utworz_serwis_zapowiedzi_meczu(self) -> ZapowiedzMeczuService:
        return ZapowiedzMeczuService(
            self._fabryka_zapowiedzi_meczu(),
            StatystykiZapowiedziCalculator(),
            KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy()),
            self.utworz_prognoze_zapowiedzi(),
            self._zegar,
        )

    def utworz_presenter_zapowiedzi_meczu(self) -> ZapowiedzMeczuPresenter:
        return ZapowiedzMeczuPresenter(
            KalendarzFormat(), PrognozaFormat(), self.utworz_presenter_prognoz_meczow()
        )

    def utworz_serwis_protokolu_meczu(self) -> ProtokolMeczuService:
        return ProtokolMeczuService(
            self._fabryka_zapowiedzi_meczu(),
            self._fabryka_protokolow(),
            KadraMeczuBuilder(
                self._fabryka_zapowiedzi_meczu(),
                KadraZapowiedziCalculator(KolejnoscPozycjiPolicy(), KolejnoscRozgrywekPolicy()),
            ),
            self._zegar,
        )

    def utworz_presenter_protokolu_meczu(self) -> ProtokolMeczuPresenter:
        return ProtokolMeczuPresenter(UkladProtokoluPolicy(), KolejnoscZawodnikowProtokoluPolicy())

    def utworz_presenter_protokolu_live(self) -> ProtokolLivePresenter:
        return ProtokolLivePresenter(
            KolejnoscZawodnikowProtokoluPolicy(),
            NumeryProtokoluLivePolicy(),
            NazwaPlikuProtokoluPolicy(),
        )

    def utworz_renderer_pdf(self) -> DokumentPdfRenderer:
        return self._renderer_pdf

    def utworz_typowania_kolejki(self) -> TypowaniaKolejkiService:
        return TypowaniaKolejkiService(
            self._fabryka_terminarza(),
            self.utworz_prognoze_zapowiedzi(),
            self._katalog_modeli_prognoz,
        )

    def utworz_raport_typowan(self) -> RaportTypowanService:
        return RaportTypowanService(
            self._fabryka_typowan(),
            self.utworz_prognoze_zapowiedzi(),
            self._katalog_modeli_prognoz,
            WzorceNazwLig(),
            self._zegar,
            KolejnoscRozgrywekPolicy(),
        )

    def utworz_presenter_typowan(self) -> TypowaniaPresenter:
        return TypowaniaPresenter(
            self.utworz_presenter_prognoz_meczow(), MeczFormat(), MeczPolicy(), KalendarzFormat()
        )
