from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np

from maf.records import MatchRecord

PRAWDZIWE_EFEKTY_RYWALI = (0.6, 0.3, 0.0, 0.0, -0.2, -0.4)


def syntetyczne_mecze(
    *,
    sezony: int = 4,
    kluby: int = 6,
    ziarno: int = 7,
    z_pojemnoscia: bool = True,
) -> list[MatchRecord]:
    generator = np.random.default_rng(ziarno)
    efekty_gospodarzy = np.linspace(0.5, -0.5, kluby)
    efekty_rywali = np.array(PRAWDZIWE_EFEKTY_RYWALI[:kluby])
    pojemnosci = [800 + 200 * indeks for indeks in range(kluby)]
    rekordy: list[MatchRecord] = []
    identyfikator = 1
    for sezon in range(sezony):
        start = datetime(2020 + sezon, 9, 5, 18, 0)
        kolejka = 0
        for gospodarz in range(kluby):
            for rywal in range(kluby):
                if gospodarz == rywal:
                    continue
                termin = start + timedelta(days=7 * kolejka + (gospodarz % 2))
                kolejka += 1
                eta = -0.4 + efekty_gospodarzy[gospodarz] + efekty_rywali[rywal]
                mu = 1.0 / (1.0 + np.exp(-eta))
                p = generator.beta(mu * 20.0, (1.0 - mu) * 20.0)
                widzowie = int(generator.binomial(pojemnosci[gospodarz], p))
                rekordy.append(
                    MatchRecord(
                        match_id=identyfikator,
                        kickoff=termin,
                        season_key=f"{2020 + sezon}/{2021 + sezon}",
                        season_order=2020 + sezon,
                        competition_key="Liga testowa",
                        competition_name="Liga testowa",
                        host_id=100 + gospodarz,
                        host_name=f"Klub {gospodarz}",
                        opponent_id=100 + rywal,
                        opponent_name=f"Klub {rywal}",
                        venue_id=500 + gospodarz,
                        venue_name=f"Hala {gospodarz}",
                        spectators=widzowie,
                        capacity=pojemnosci[gospodarz] if z_pojemnoscia else None,
                        phase="Runda zasadnicza",
                        host_goals=int(generator.integers(20, 35)),
                        opponent_goals=int(generator.integers(20, 35)),
                    )
                )
                identyfikator += 1
    return rekordy
