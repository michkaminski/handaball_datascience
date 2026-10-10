from __future__ import annotations

from dataclasses import dataclass

from maf.records import Measure, ModelSpec


@dataclass(frozen=True)
class ModelMaf:
    spec: ModelSpec
    plec: str


MODELE_MAF: tuple[ModelMaf, ...] = (
    ModelMaf(
        ModelSpec(
            "M-wypelnienie",
            "Mężczyźni — wypełnienie hali",
            Measure.FILL,
            "Rozgrywki ZPRP mężczyzn; mecze ze znaną frekwencją i pojemnością hali",
        ),
        "M",
    ),
    ModelMaf(
        ModelSpec(
            "M-widzowie",
            "Mężczyźni — liczba widzów",
            Measure.COUNT,
            "Rozgrywki ZPRP mężczyzn; wszystkie mecze ze znaną frekwencją",
        ),
        "M",
    ),
    ModelMaf(
        ModelSpec(
            "K-wypelnienie",
            "Kobiety — wypełnienie hali",
            Measure.FILL,
            "Rozgrywki ZPRP kobiet; mecze ze znaną frekwencją i pojemnością hali",
        ),
        "K",
    ),
    ModelMaf(
        ModelSpec(
            "K-widzowie",
            "Kobiety — liczba widzów",
            Measure.COUNT,
            "Rozgrywki ZPRP kobiet; wszystkie mecze ze znaną frekwencją",
        ),
        "K",
    ),
)
DOMYSLNY_MODEL_MAF = MODELE_MAF[0].spec.key


def model_maf(klucz: str | None) -> ModelMaf:
    for model in MODELE_MAF:
        if model.spec.key == klucz:
            return model
    return MODELE_MAF[0]


POJECIA_MAF: dict[str, tuple[str, str | None]] = {
    "suma": ("srednia-arytmetyczna", "definicja"),
    "srednia": ("srednia-arytmetyczna", "wzor"),
    "mediana": ("mediana", "definicja"),
    "odchylenie": ("odchylenie-standardowe", "wzor"),
    "wypelnienie": ("rozklad-beta", "definicja"),
    "mecze": ("partial-pooling", "wzor"),
    "rekord": ("percentyle", "definicja"),
    "efekt_rywala": ("interpretacja-wspolczynnikow", None),
    "iaf": ("atrakcyjnosc-frekwencyjna", "wzor"),
    "iaf_posterior": ("rozklad-posterior", "definicja"),
    "przedzial": ("przedzial-wiarygodnosci", "wzor"),
    "p_iaf": ("probabilistyczne-porownanie-parametrow", "wzor"),
    "efekt_pp": ("interpretacja-wspolczynnikow", "wzor"),
    "hierarchia": ("modele-hierarchiczne", "definicja"),
    "pooling": ("partial-pooling", "wzor"),
    "efekty_losowe": ("efekty-stale-i-losowe", "definicja"),
    "identyfikowalnosc": ("identyfikowalnosc-parametrow", "definicja"),
    "logit": ("funkcja-logit", "wzor"),
    "beta_dwumianowy": ("rozklad-beta-dwumianowy", "wzor"),
    "ujemny_dwumianowy": ("rozklad-ujemny-dwumianowy", "wzor"),
    "bayes": ("twierdzenie-bayesa", "wzor"),
    "prior": ("priory", "definicja"),
    "hiperprior": ("hiperpriory", "definicja"),
    "mcmc": ("mcmc", "definicja"),
    "monte_carlo": ("monte-carlo", "definicja"),
    "predykcja": ("rozklad-predykcyjny", "wzor"),
    "przedzial_predykcyjny": ("przedzialy-predykcyjne", "definicja"),
    "niepewnosc": ("niepewnosc-predykcyjna", "wzor"),
    "wartosc_oczekiwana_prognozy": ("wartosc-oczekiwana-prognozy", "wzor"),
    "z_score": ("z-score", None),
    "reszty": ("diagnostyka-reszt", "definicja"),
    "rhat": ("r-hat", "wzor"),
    "ess": ("effective-sample-size", "wzor"),
    "ppc": ("posterior-predictive-checks", "definicja"),
    "mae": ("mae", "wzor"),
    "rmse": ("rmse", "wzor"),
    "pokrycie": ("pokrycie-przedzialow-predykcyjnych", "wzor"),
    "kalibracja": ("kalibracja-prawdopodobienstw", "definicja"),
    "backtest": ("backtesting", "definicja"),
    "forma": ("srednia-ruchoma", "wzor"),
    "standaryzacja": ("standaryzacja", "wzor"),
    "wspolczynniki": ("interpretacja-wspolczynnikow", "definicja"),
    "trend": ("regresja-hierarchiczna", "definicja"),
}
