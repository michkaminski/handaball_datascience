from __future__ import annotations

import math
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from tests.helpers.maf_synthetic import syntetyczne_mecze

from maf.artifacts import ArtifactStore
from maf.design import GROUPS, ModelDataBuilder
from maf.diagnostics import basic_ess, ess_bulk, rank_normalized_rhat
from maf.features import FeatureBuilder, FeatureScaler, PhaseClassifier
from maf.forecast import AttendanceSimulator, ForecastScenario, HostOpponentAnalysis, compare_clubs
from maf.model import HierarchicalAttendanceModel
from maf.nuts import NutsSampler, SamplerSettings, adaptation_windows
from maf.quality import DataQualityChecker
from maf.records import CapacityOverride, Measure, ModelSpec
from maf.training import MafTrainer
from maf.validation import crps_from_samples, holdout_mask
from maf.zerosum import ZeroSumTransform


def test_transformacja_sumy_zerowej_jest_ortonormalna_i_zeruje_sumy_blokow() -> None:
    bloki = np.array([0, 1, 0, 2, 1, 1, 0, 2, 2, 2])
    transformacja = ZeroSumTransform(bloki)
    baza = np.stack([transformacja.forward(e) for e in np.eye(transformacja.n_free)], axis=1)
    assert transformacja.n_free == 10 - 3
    assert np.allclose(baza.T @ baza, np.eye(transformacja.n_free))
    for blok in range(3):
        assert np.allclose(baza[bloki == blok].sum(axis=0), 0.0)
    gradient = np.random.default_rng(1).normal(size=10)
    assert np.allclose(transformacja.backward(gradient), baza.T @ gradient)


def _dane(miara: Measure = Measure.FILL):
    rekordy = syntetyczne_mecze()
    przygotowane, _ = DataQualityChecker().prepare(rekordy)
    cechy, _ = FeatureBuilder().build(przygotowane)
    skaler = FeatureScaler.fit(list(cechy.values()))
    return ModelDataBuilder().build(przygotowane, cechy, miara, skaler)


@pytest.mark.parametrize("miara", [Measure.FILL, Measure.COUNT])
def test_gradient_analityczny_zgadza_sie_z_roznicami_skonczonymi(miara: Measure) -> None:
    model = HierarchicalAttendanceModel(_dane(miara))
    theta = model.initial_point(np.random.default_rng(3))
    _, gradient = model.logp_and_grad(theta)
    for indeks in range(model.dimension):
        krok = np.zeros_like(theta)
        krok[indeks] = 1e-5
        numeryczny = (
            model.logp_and_grad(theta + krok)[0] - model.logp_and_grad(theta - krok)[0]
        ) / 2e-5
        assert numeryczny == pytest.approx(gradient[indeks], rel=1e-4, abs=1e-3)


def test_rhat_i_ess_dla_niezaleznych_probek() -> None:
    probki = np.random.default_rng(5).normal(size=(4, 1000))
    assert rank_normalized_rhat(probki) < 1.01
    assert ess_bulk(probki) == pytest.approx(4000, rel=0.15)


def test_ess_procesu_ar1_odpowiada_teorii() -> None:
    generator = np.random.default_rng(11)
    phi = 0.8
    lancuchy = np.zeros((4, 4000))
    for lancuch in range(4):
        for t in range(1, 4000):
            lancuchy[lancuch, t] = phi * lancuchy[lancuch, t - 1] + generator.normal()
    teoretyczne = 16000 * (1 - phi) / (1 + phi)
    assert basic_ess(lancuchy) == pytest.approx(teoretyczne, rel=0.25)


def test_rhat_wykrywa_lancuchy_o_roznych_srednich() -> None:
    generator = np.random.default_rng(2)
    probki = generator.normal(size=(4, 500)) + np.array([[0.0], [0.0], [0.0], [3.0]])
    assert rank_normalized_rhat(probki) > 1.1


def test_okna_adaptacji_sa_rosnace_i_mieszcza_sie_w_rozgrzewce() -> None:
    okna = adaptation_windows(1000)
    assert okna == sorted(okna)
    assert okna[-1] == 950


def test_nuts_odtwarza_rozklad_normalny() -> None:
    kowariancja = np.array([[1.0, 0.8], [0.8, 1.0]])
    precyzja = np.linalg.inv(kowariancja)

    def gestosc(theta: np.ndarray) -> tuple[float, np.ndarray]:
        return float(-0.5 * theta @ precyzja @ theta), -precyzja @ theta

    sampler = NutsSampler(gestosc, 2, SamplerSettings(chains=1, warmup=400, draws=1500))
    wynik = sampler.sample_chain(np.array([2.0, -2.0]), seed=4)
    assert wynik.divergent.sum() == 0
    assert np.allclose(wynik.draws.mean(axis=0), 0.0, atol=0.15)
    assert np.allclose(np.cov(wynik.draws.T), kowariancja, atol=0.2)


def test_kontrola_jakosci_nie_traktuje_null_jako_zera_i_usuwa_duplikaty() -> None:
    rekordy = syntetyczne_mecze(sezony=1)
    brak = replace(rekordy[0], spectators=None)
    zero = replace(rekordy[1], spectators=0)
    nadmiar = replace(rekordy[2], spectators=(rekordy[2].capacity or 0) + 10)
    duplikat = replace(rekordy[3])
    przygotowane, raport = DataQualityChecker().prepare(
        [brak, zero, nadmiar, rekordy[3], duplikat, *rekordy[4:]]
    )
    assert raport.duplicates_removed == 1
    assert raport.attendance_unknown == 1
    assert raport.attendance_zero == 1
    assert raport.capacity_exceeded == 1
    po_id = {mecz.record.match_id: mecz for mecz in przygotowane}
    assert not po_id[brak.match_id].usable_count
    assert not po_id[zero.match_id].usable_count
    assert po_id[nadmiar.match_id].usable_count and not po_id[nadmiar.match_id].usable_fill


def test_korekta_pojemnosci_ma_pierwszenstwo_przed_nominalna() -> None:
    rekord = syntetyczne_mecze(sezony=1)[0]
    korekty = [
        CapacityOverride(rekord.venue_id, rekord.season_key, None, 5000),
        CapacityOverride(None, None, rekord.match_id, 4321),
    ]
    przygotowane, _ = DataQualityChecker(overrides=korekty).prepare([rekord])
    assert przygotowane[0].capacity == 4321
    assert przygotowane[0].capacity_source == "korekta"
    assert przygotowane[0].nominal_capacity == rekord.capacity


def test_brak_pojemnosci_wyklucza_tylko_model_wypelnienia() -> None:
    rekordy = syntetyczne_mecze(sezony=1, z_pojemnoscia=False)
    przygotowane, raport = DataQualityChecker().prepare(rekordy)
    assert raport.usable_fill == 0
    assert raport.usable_count == len(rekordy)


def test_turniej_na_obcej_hali_jest_terenem_neutralnym() -> None:
    rekordy = syntetyczne_mecze(sezony=1)
    final = replace(
        rekordy[0],
        match_id=9001,
        kickoff=datetime(2020, 12, 30, 18, 0),
        venue_id=999,
        host_id=100,
        opponent_id=101,
    )
    drugi = replace(
        rekordy[1],
        match_id=9002,
        kickoff=datetime(2020, 12, 31, 18, 0),
        venue_id=999,
        host_id=102,
        opponent_id=103,
    )
    przygotowane, raport = DataQualityChecker().prepare([*rekordy, final, drugi])
    neutralne = {mecz.record.match_id for mecz in przygotowane if mecz.neutral}
    assert {9001, 9002} <= neutralne
    assert raport.neutral_matches >= 2


def test_forma_uzywa_wylacznie_wczesniejszych_meczow() -> None:
    rekordy = syntetyczne_mecze(sezony=1)
    przygotowane, _ = DataQualityChecker().prepare(rekordy)
    cechy, _ = FeatureBuilder().build(przygotowane)
    pierwszy = min(rekordy, key=lambda rekord: rekord.kickoff or datetime.max)
    assert cechy[pierwszy.match_id].host_form is None
    assert cechy[pierwszy.match_id].host_position is None


@pytest.mark.parametrize(
    ("faza", "oczekiwana"),
    [
        ("Runda zasadnicza", "regular"),
        ("Group Phase", "regular"),
        ("Semi-finals", "playoff"),
        ("1/4 finału", "playoff"),
        ("Finał", "final"),
        ("Finals", "final"),
            ("Quarter-finals", "playoff"),
            ("Final Four", "final"),
            ("Play-offs", "playoff"),
        (None, "regular"),
    ],
)
def test_klasyfikacja_fazy(faza: str | None, oczekiwana: str) -> None:
    assert PhaseClassifier().classify(faza) == oczekiwana


def test_holdout_i_crps() -> None:
    sezony = np.array([2020, 2020, 2021, 2022, 2022])
    assert holdout_mask(sezony, 1).tolist() == [False, False, False, True, True]
    probki = np.random.default_rng(1).normal(size=(4000, 1))
    crps = crps_from_samples(probki, np.array([0.0]), np.random.default_rng(2))
    assert crps[0] == pytest.approx((math.sqrt(2) - 1) / math.sqrt(math.pi), rel=0.05)


@pytest.fixture(scope="module")
def artefakt_testowy(tmp_path_factory: pytest.TempPathFactory):
    katalog = tmp_path_factory.mktemp("maf")
    magazyn = ArtifactStore(Path(katalog))
    trener = MafTrainer(
        magazyn, SamplerSettings(chains=2, warmup=200, draws=200, thin_store=2), parallel=False
    )
    spec = ModelSpec("test-wypelnienie", "Test", Measure.FILL, "syntetyczne", holdout_seasons=1)
    trener.train(syntetyczne_mecze(), spec, {}, backtest=True)
    artefakt = magazyn.latest("test-wypelnienie")
    assert artefakt is not None
    return artefakt


def test_trening_zapisuje_odtwarzalny_artefakt(artefakt_testowy) -> None:
    podsumowanie = artefakt_testowy.summary
    model = podsumowanie["model"]
    assert model["measure"] == "fill"
    assert len(model["data_fingerprint"]) == 64
    assert model["sampler"]["seed"] == SamplerSettings().seed
    assert {grupa["name"] for grupa in model["groups"]} == set(GROUPS)
    assert podsumowanie["backtest"]["available"]
    assert artefakt_testowy.draws["iaf"].shape[0] == 2 * 200 // 2
    assert len(artefakt_testowy.matches) == model["matches_used"]


def test_iaf_jest_wyliczany_z_probek_posterior(artefakt_testowy) -> None:
    kluby = {klub["id"]: klub for klub in artefakt_testowy.summary["clubs"]}
    iaf = np.asarray(artefakt_testowy.draws["iaf"], dtype=np.float64)
    indeks = artefakt_testowy.summary["index"]["opponent"]
    for pozycja, klub in enumerate(indeks):
        wyjazd = kluby[klub]["away"]
        assert wyjazd["iaf"]["median"] == pytest.approx(float(np.median(iaf[:, pozycja])), rel=1e-4)
        assert wyjazd["p_gt_100"] == pytest.approx(float(np.mean(iaf[:, pozycja] > 100)), abs=1e-9)
        assert wyjazd["iaf"]["q025"] <= wyjazd["iaf"]["median"] <= wyjazd["iaf"]["q975"]
    najlepszy = kluby[100]["away"]["iaf"]["median"]
    najgorszy = kluby[105]["away"]["iaf"]["median"]
    assert najlepszy > 100 > najgorszy


def test_sredni_rywal_ma_iaf_okolo_100(artefakt_testowy) -> None:
    efekty = np.asarray(artefakt_testowy.draws["effect_opponent"], dtype=np.float64)
    assert np.allclose(efekty.sum(axis=1), 0.0, atol=1e-4)


def test_symulator_daje_spojne_przedzialy_i_prawdopodobienstwa(artefakt_testowy) -> None:
    scenariusz = ForecastScenario(
        100, 101, "Liga testowa", "2023/2024", 800, 5, 18.0, "regular", 500
    )
    wynik = AttendanceSimulator(artefakt_testowy).simulate(scenariusz)
    p50, p80, p95 = (wynik["intervals"][poziom] for poziom in ("50", "80", "95"))
    assert p95[0] <= p80[0] <= p50[0] <= p50[1] <= p80[1] <= p95[1] <= 800
    progi = wynik["fill_probabilities"]
    assert progi["75"] >= progi["90"] >= progi["95"] >= progi["100"]
    assert wynik["mean_parameter"]["q975"] - wynik["mean_parameter"]["q025"] < p95[1] - p95[0]
    assert sum(wynik["histogram"]["probabilities"]) == pytest.approx(1.0)


def test_symulator_odrzuca_ten_sam_klub(artefakt_testowy) -> None:
    with pytest.raises(ValueError):
        AttendanceSimulator(artefakt_testowy).simulate(
            ForecastScenario(100, 100, None, None, 800, 5, 18.0, "regular")
        )


def test_analiza_gospodarza_i_porownanie(artefakt_testowy) -> None:
    analiza = HostOpponentAnalysis(artefakt_testowy).analyze(103)
    assert analiza["top"][0]["index"]["median"] >= analiza["bottom"][0]["index"]["median"]
    porownanie = compare_clubs(artefakt_testowy, 100, 105)
    assert porownanie["p_first_greater"] > 0.9


def test_kontynuacja_klubu_laczy_poprzednika_z_nastepca() -> None:
    from maf.records import ClubLineage

    rekordy = syntetyczne_mecze(sezony=1)
    przygotowane, raport = DataQualityChecker(lineage=[ClubLineage(100, 199)]).prepare(rekordy)
    identyfikatory = {mecz.record.host_id for mecz in przygotowane} | {
        mecz.record.opponent_id for mecz in przygotowane
    }
    assert 100 not in identyfikatory and 199 in identyfikatory
    assert raport.lineage_remapped == sum(
        1 for rekord in rekordy if 100 in (rekord.host_id, rekord.opponent_id)
    )
