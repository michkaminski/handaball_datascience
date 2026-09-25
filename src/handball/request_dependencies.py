from __future__ import annotations

from collections.abc import Callable
from typing import cast

from sqlalchemy.orm import Session

from handball.contracts.classification_repository import KlasyfikacjaReadRepository
from handball.contracts.competition_repository import RozgrywkiReadRepository
from handball.contracts.core_catalog_repository import KatalogPodstawowyReadRepository
from handball.contracts.match_prediction_repository import MeczeLigoweReadRepository
from handball.contracts.match_repository import MeczReadRepository
from handball.contracts.match_stage_repository import EtapMeczowReadRepository
from handball.contracts.news_repository import AktualnosciReadRepository
from handball.contracts.opponent_defense_repository import DefensywaRywalaReadRepository
from handball.contracts.player_detail_repository import SzczegolyZawodnikaReadRepository
from handball.contracts.player_repository import ZawodnikReadRepository
from handball.contracts.referee_detail_repository import SzczegolySedziegoReadRepository
from handball.contracts.season_repository import SezonReadRepository
from handball.contracts.team_detail_repository import SzczegolyDruzynyReadRepository
from handball.contracts.venue_catalog_repository import HalaKatalogReadRepository
from handball.contracts.venue_detail_repository import SzczegolyHaliReadRepository
from handball.contracts.venue_repository import HalaReadRepository
from handball.domain.match_predictions import (
    KwalifikacjaMeczuPolicy,
    OcenaPrognozyPolicy,
    ProgiTrafnosci,
    WzorceNazwLig,
    ZakresBacktestu,
)
from handball.domain.match_rules import MeczPolicy
from handball.domain.team_details import KolejnoscPozycjiPolicy, WystepDruzynyPolicy
from handball.extensions import baza_danych
from handball.infrastructure.repositories.classification_repository import (
    KlasyfikacjaSQLAlchemyRepository,
)
from handball.infrastructure.repositories.competition_repository import (
    RozgrywkiSQLAlchemyRepository,
)
from handball.infrastructure.repositories.core_catalog_repository import (
    KatalogPodstawowySQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_prediction_repository import (
    MeczeLigoweSQLAlchemyRepository,
)
from handball.infrastructure.repositories.match_repository import MeczSQLAlchemyRepository
from handball.infrastructure.repositories.match_stage_repository import (
    EtapMeczowSQLAlchemyRepository,
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
from handball.interface.presenters.news_presenter import AktualnosciPresenter
from handball.interface.presenters.opponent_defense_presenter import DefensywaRywalaPresenter
from handball.interface.presenters.player_detail_presenter import SzczegolyZawodnikaPresenter
from handball.interface.presenters.player_presenter import ZawodnikPresenter
from handball.interface.presenters.referee_detail_presenter import SzczegolySedziegoPresenter
from handball.interface.presenters.team_detail_presenter import SzczegolyDruzynyPresenter
from handball.interface.presenters.venue_detail_presenter import SzczegolyHaliPresenter
from handball.services.catalog_service import KatalogService
from handball.services.classification_service import KlasyfikacjaService
from handball.services.goal_statistics import StatystykiBramekCalculator
from handball.services.match_dictionary_service import SlownikiMeczowService
from handball.services.match_prediction_service import (
    BacktestPrognozService,
    KatalogModeliPrognoz,
    PodsumowaniePrognozCalculator,
    PodzialSezonowPolicy,
    RaportPrognozService,
    SzczegolyPrognozyService,
)
from handball.services.match_service import MeczService
from handball.services.news_service import AktualnosciService
from handball.services.opponent_defense_service import DefensywaRywalaService
from handball.services.player_detail_service import (
    SzczegolyZawodnikaAnalyticsService,
    SzczegolyZawodnikaService,
)
from handball.services.player_dictionary_service import SlownikiZawodnikowService
from handball.services.player_service import ZawodnikService
from handball.services.referee_detail_service import SzczegolySedziegoService
from handball.services.team_detail_service import (
    AnalitykaDruzynyService,
    BilansDruzynyCalculator,
    FrekwencjaDruzynyCalculator,
    SzczegolyDruzynyService,
    ZestawienieDruzynyService,
)
from handball.services.venue_detail_service import SzczegolyHaliService
from handball.services.venue_service import HalaService


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
        fabryka_szczegolow_sedziego: Callable[[], SzczegolySedziegoReadRepository] | None = None,
        fabryka_klasyfikacji: Callable[[], KlasyfikacjaReadRepository] | None = None,
        fabryka_defensywy_rywala: Callable[[], DefensywaRywalaReadRepository] | None = None,
        fabryka_aktualnosci: Callable[[], AktualnosciReadRepository] | None = None,
        fabryka_szczegolow_druzyny: Callable[[], SzczegolyDruzynyReadRepository] | None = None,
        fabryka_meczow_ligowych: Callable[[], MeczeLigoweReadRepository] | None = None,
        katalog_modeli_prognoz: KatalogModeliPrognoz | None = None,
    ) -> None:
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
        )

    def utworz_presenter_meczow(self) -> MeczPresenter:
        formatowanie = MeczFormat()
        reguly = MeczPolicy()
        return MeczPresenter(reguly, formatowanie, SkladMeczuPresenter(formatowanie, reguly))

    def utworz_serwis_zawodnikow(self) -> ZawodnikService:
        return ZawodnikService(self._fabryka_repozytorium_zawodnikow())

    def utworz_presenter_zawodnikow(self) -> ZawodnikPresenter:
        return ZawodnikPresenter()

    def utworz_slowniki_zawodnikow(self) -> SlownikiZawodnikowService:
        return SlownikiZawodnikowService(
            self._fabryka_repozytorium_sezonow(), self._fabryka_repozytorium_rozgrywek()
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
        return SzczegolyDruzynyService(self._fabryka_szczegolow_druzyny())

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

    def utworz_serwis_defensywy_rywala(self) -> DefensywaRywalaService:
        return DefensywaRywalaService(self._fabryka_defensywy_rywala())

    def utworz_presenter_defensywy_rywala(self) -> DefensywaRywalaPresenter:
        return DefensywaRywalaPresenter(MeczFormat())

    def utworz_serwis_hal(self) -> HalaService:
        return HalaService(self._fabryka_katalogu_hal())

    def utworz_serwis_katalogu(self) -> KatalogService:
        return KatalogService(self._fabryka_katalogu_podstawowego())

    def utworz_serwis_szczegolow_hali(self) -> SzczegolyHaliService:
        return SzczegolyHaliService(self._fabryka_szczegolow_hali())

    def utworz_presenter_szczegolow_hali(self) -> SzczegolyHaliPresenter:
        return SzczegolyHaliPresenter(MeczFormat())

    def utworz_serwis_szczegolow_sedziego(self) -> SzczegolySedziegoService:
        return SzczegolySedziegoService(self._fabryka_szczegolow_sedziego())

    def utworz_presenter_szczegolow_sedziego(self) -> SzczegolySedziegoPresenter:
        return SzczegolySedziegoPresenter(MeczFormat())

    def utworz_serwis_klasyfikacji(self) -> KlasyfikacjaService:
        return KlasyfikacjaService(self._fabryka_klasyfikacji())

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
