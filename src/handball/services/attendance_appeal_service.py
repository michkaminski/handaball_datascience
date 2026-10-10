from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from handball.contracts.attendance_appeal_store import ModeleMafReadStore
from handball.domain.attendance_appeal import (
    MODELE_MAF,
    POJECIA_MAF,
    ModelMaf,
    model_maf,
)
from handball.services.mathematics_service import BibliotekaMatematycznaService
from maf.artifacts import ModelArtifact
from maf.forecast import (
    AttendanceSimulator,
    ForecastScenario,
    HostOpponentAnalysis,
    compare_clubs,
)

JsonDict = dict[str, object]
POLA_KLUBU_W_PANELU = ("id", "name", "names_history", "home")


class BrakModeluMaf(LookupError):
    pass


@dataclass(frozen=True)
class OpcjaModeluMaf:
    klucz: str
    etykieta: str
    dostepny: bool
    wersja: str | None
    status: str | None


class AtrakcyjnoscFrekwencyjnaService:
    def __init__(
        self, magazyn: ModeleMafReadStore, biblioteka: BibliotekaMatematycznaService
    ) -> None:
        self._magazyn = magazyn
        self._biblioteka = biblioteka

    def modele(self) -> tuple[OpcjaModeluMaf, ...]:
        opcje = []
        for model in MODELE_MAF:
            artefakt = self._magazyn.latest(model.spec.key)
            informacje = _model(artefakt) if artefakt else {}
            opcje.append(
                OpcjaModeluMaf(
                    klucz=model.spec.key,
                    etykieta=model.spec.label,
                    dostepny=artefakt is not None,
                    wersja=str(informacje["version"]) if artefakt else None,
                    status=str(informacje["status"]) if artefakt else None,
                )
            )
        return tuple(opcje)

    def wybierz_model(self, klucz: str | None) -> ModelMaf:
        return model_maf(klucz)

    def artefakt(self, klucz: str) -> ModelArtifact:
        artefakt = self._magazyn.latest(klucz)
        if artefakt is None:
            raise BrakModeluMaf(klucz)
        return artefakt

    def odnosniki(self) -> JsonDict:
        identyfikatory = tuple(dict.fromkeys(pojecie for pojecie, _ in POJECIA_MAF.values()))
        linki = self._biblioteka.odnosniki(identyfikatory)
        return {
            "pojecia": linki,
            "metryki": {
                klucz: {
                    "pojecie": pojecie,
                    "url": self._biblioteka.rejestr.url(pojecie, kotwica),
                }
                for klucz, (pojecie, kotwica) in POJECIA_MAF.items()
            },
            "model": self._biblioteka.rejestr.url("atrakcyjnosc-frekwencyjna"),
        }

    def panel(self, klucz: str) -> JsonDict:
        artefakt = self.artefakt(klucz)
        podsumowanie = artefakt.summary
        kluby = [self._klub_w_panelu(klub) for klub in _lista(podsumowanie["clubs"])]
        return {
            "model": podsumowanie["model"],
            "quality": podsumowanie["quality"],
            "diagnostics": podsumowanie["diagnostics"],
            "coefficients": podsumowanie["coefficients"],
            "kpi": podsumowanie["kpi"],
            "clubs": kluby,
            "hosts": [
                {"id": host["club_id"], "capacity": host["capacity"]}
                for host in _lista(podsumowanie["hosts"])
            ],
            "competitions": podsumowanie["competitions"],
            "venues": podsumowanie["venues"][:400],  # type: ignore[index]
            "surprises": podsumowanie["surprises"],
            "records": podsumowanie["records"],
            "heatmap": podsumowanie["heatmap"],
            "ppc": podsumowanie["ppc"],
            "backtest": podsumowanie["backtest"],
            "links": self.odnosniki(),
        }

    def _klub_w_panelu(self, klub: JsonDict) -> JsonDict:
        wynik = {pole: klub.get(pole) for pole in POLA_KLUBU_W_PANELU}
        wyjazd = klub.get("away")
        if isinstance(wyjazd, dict):
            wynik["away"] = {
                pole: wartosc
                for pole, wartosc in wyjazd.items()
                if pole not in {"histogram", "central"}
            }
        return wynik

    def klub(self, klucz: str, identyfikator: int) -> JsonDict:
        artefakt = self.artefakt(klucz)
        podsumowanie = artefakt.summary
        klub = next(
            (item for item in _lista(podsumowanie["clubs"]) if item["id"] == identyfikator), None
        )
        if klub is None:
            raise KeyError(identyfikator)
        model = _model(artefakt)
        return {
            "club": klub,
            "model": {
                pole: model[pole]
                for pole in (
                    "key",
                    "label",
                    "measure",
                    "version",
                    "trained_at",
                    "status",
                    "matches_used",
                    "period",
                    "reference",
                    "sampler",
                    "groups",
                )
            },
            "links": self.odnosniki(),
        }

    def gospodarz(self, klucz: str, identyfikator: int) -> JsonDict:
        return HostOpponentAnalysis(self.artefakt(klucz)).analyze(identyfikator)

    def porownanie(self, klucz: str, pierwszy: int, drugi: int) -> JsonDict:
        return compare_clubs(self.artefakt(klucz), pierwszy, drugi)

    def prognoza(self, klucz: str, scenariusz: ForecastScenario) -> JsonDict:
        return AttendanceSimulator(self.artefakt(klucz)).simulate(scenariusz)

    def eksport_csv(self, klucz: str) -> str:
        artefakt = self.artefakt(klucz)
        bufor = io.StringIO()
        zapis = csv.writer(bufor, delimiter=";")
        zapis.writerow(
            [
                "id_klubu",
                "klub",
                "mecze_jako_rywal",
                "srednia_widzow",
                "mediana_widzow",
                "wypelnienie_srednie",
                "IAF_mediana",
                "IAF_q2.5",
                "IAF_q97.5",
                "P(IAF>100)",
                "efekt_pp_mediana",
                "dodatkowi_widzowie_mediana",
                "wiarygodny",
                "uwagi",
                "wersja_modelu",
            ]
        )
        wersja = artefakt.version
        for klub in _lista(artefakt.summary["clubs"]):
            wyjazd = klub.get("away")
            if not isinstance(wyjazd, dict):
                continue
            iaf = wyjazd["iaf"]
            pp = wyjazd.get("pp")
            dodatkowi = wyjazd["extra"]
            zapis.writerow(
                [
                    klub["id"],
                    klub["name"],
                    wyjazd["matches"],
                    _liczba(wyjazd["mean"]),
                    _liczba(wyjazd["median"]),
                    _liczba(wyjazd.get("fill_mean")),
                    _liczba(iaf["median"]),
                    _liczba(iaf["q025"]),
                    _liczba(iaf["q975"]),
                    _liczba(wyjazd["p_gt_100"]),
                    _liczba(pp["median"]) if isinstance(pp, dict) else "",
                    _liczba(dodatkowi["median"]),
                    "tak" if wyjazd["reliable"] else "nie",
                    "; ".join(wyjazd["notes"]),
                    wersja,
                ]
            )
        return bufor.getvalue()


def _model(artefakt: ModelArtifact) -> JsonDict:
    model = artefakt.summary["model"]
    assert isinstance(model, dict)
    return model


def _lista(wartosc: object) -> list[JsonDict]:
    assert isinstance(wartosc, list)
    return wartosc


def _liczba(wartosc: object) -> str:
    if wartosc is None:
        return ""
    return f"{float(wartosc):.4f}".replace(".", ",")  # type: ignore[arg-type]
