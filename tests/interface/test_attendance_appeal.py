from __future__ import annotations

from pathlib import Path

import pytest
from flask.testing import FlaskClient
from tests.conftest import ustawienia_testowe
from tests.helpers.maf_synthetic import syntetyczne_mecze

from handball.app_factory import AplikacjaFactory
from handball.interface.registration import WidokiRegistrar
from handball.request_dependencies import ZaleznosciZadaniaFactory
from maf.artifacts import ArtifactStore
from maf.nuts import SamplerSettings
from maf.records import Measure, ModelSpec
from maf.training import MafTrainer

URL = "/administracja/raporty/frekwencja/maf"


@pytest.fixture(scope="module")
def magazyn(tmp_path_factory: pytest.TempPathFactory) -> ArtifactStore:
    magazyn = ArtifactStore(Path(tmp_path_factory.mktemp("maf")))
    trener = MafTrainer(
        magazyn, SamplerSettings(chains=2, warmup=150, draws=150, thin_store=2), parallel=False
    )
    spec = ModelSpec("M-wypelnienie", "Mężczyźni — wypełnienie hali", Measure.FILL, "test")
    trener.train(syntetyczne_mecze(), spec, {100: "Klub Zero"}, backtest=False)
    return magazyn


def _klient(magazyn: ArtifactStore) -> FlaskClient:
    fabryka = ZaleznosciZadaniaFactory(magazyn_modeli_maf=magazyn)
    aplikacja = AplikacjaFactory(ustawienia_testowe(), WidokiRegistrar(fabryka)).utworz()
    return aplikacja.test_client()


def test_panel_zwraca_ranking_kpi_diagnostyke_i_odnosniki(magazyn: ArtifactStore) -> None:
    odpowiedz = _klient(magazyn).get(f"{URL}/dane?model=M-wypelnienie")
    assert odpowiedz.status_code == 200
    dane = odpowiedz.get_json()
    assert dane["model"]["key"] == "M-wypelnienie"
    assert dane["kpi"]["matches"] == dane["model"]["matches_used"]
    assert "histogram" not in dane["clubs"][0].get("away", {})
    assert dane["links"]["metryki"]["iaf"]["url"].startswith(
        "/matematyka/modele-sportowe/atrakcyjnosc-frekwencyjna/"
    )
    assert dane["diagnostics"]["status"] in {"ok", "ostrzezenie", "niewiarygodny"}


def test_brak_modelu_daje_404_z_instrukcja(tmp_path: Path) -> None:
    odpowiedz = _klient(ArtifactStore(tmp_path)).get(f"{URL}/dane?model=K-widzowie")
    assert odpowiedz.status_code == 404
    assert "maf_cli" in odpowiedz.get_json()["blad"]


def test_slad_obliczenia_klubu(magazyn: ArtifactStore) -> None:
    dane = _klient(magazyn).get(f"{URL}/klub/100?model=M-wypelnienie").get_json()
    wyjazd = dane["club"]["away"]
    assert dane["club"]["name"] == "Klub Zero"
    assert {"central", "histogram", "iaf", "p_gt_100", "effect"} <= set(wyjazd)
    assert dane["model"]["reference"]["matches_sampled"] > 0


def test_nieznany_klub_daje_404(magazyn: ArtifactStore) -> None:
    assert _klient(magazyn).get(f"{URL}/klub/1?model=M-wypelnienie").status_code == 404


def test_prognoza_i_walidacja_parametrow(magazyn: ArtifactStore) -> None:
    klient = _klient(magazyn)
    parametry = "model=M-wypelnienie&gospodarz=100&rywal=101&dzien=5&godzina=18:00&pojemnosc=800"
    wynik = klient.get(f"{URL}/prognoza?{parametry}&prog=300").get_json()
    assert set(wynik["intervals"]) == {"50", "80", "95"}
    assert 0.0 <= wynik["p_threshold"] <= 1.0
    zly_dzien = parametry.replace("dzien=5", "dzien=9")
    assert klient.get(f"{URL}/prognoza?{zly_dzien}").status_code == 400
    bez_pojemnosci = parametry.replace("&pojemnosc=800", "")
    assert klient.get(f"{URL}/prognoza?{bez_pojemnosci}").status_code == 400


def test_porownanie_gospodarz_i_eksport(magazyn: ArtifactStore) -> None:
    klient = _klient(magazyn)
    porownanie = klient.get(f"{URL}/porownanie?model=M-wypelnienie&a=100&b=105").get_json()
    assert 0.0 <= porownanie["p_first_greater"] <= 1.0
    assert klient.get(f"{URL}/gospodarz/103?model=M-wypelnienie").status_code == 200
    eksport = klient.get(f"{URL}/eksport.csv?model=M-wypelnienie")
    assert eksport.mimetype == "text/csv"
    assert "IAF_mediana" in eksport.get_data(as_text=True)
