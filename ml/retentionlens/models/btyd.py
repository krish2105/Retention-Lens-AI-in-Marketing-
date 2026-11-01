"""BG/NBD purchase model plus Gamma-Gamma spend model (PyMC-Marketing, MAP fits)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from pymc_marketing import clv


def _posterior_mean(values) -> np.ndarray:
    dims = [d for d in ("chain", "draw") if d in values.dims]
    return np.asarray(values.mean(dims) if dims else values, dtype=float)


def _purchase_frame(snap: pd.DataFrame) -> pd.DataFrame:
    # PyMC-Marketing keys rows by customer_id; positional ids keep output order = snapshot order.
    return pd.DataFrame(
        {
            "customer_id": np.arange(len(snap)),
            "frequency": snap["frequency"].to_numpy(dtype=float),
            "recency": snap["btyd_recency"].to_numpy(dtype=float),
            "T": snap["T"].to_numpy(dtype=float),
        }
    )


class BtydModel:
    """Fit on the evaluation snapshot's own history: it needs no labels."""

    name = "bgnbd_gamma_gamma"

    def fit(self, snap: pd.DataFrame, seed: int = 0) -> "BtydModel":
        self.purchases = clv.BetaGeoModel()
        self.purchases.fit(data=_purchase_frame(snap), method="map", progressbar=False, random_seed=seed)
        repeat = snap[(snap["frequency"] > 0) & (snap["repeat_mean_value"] > 0)]
        self.population_spend = float(repeat["repeat_mean_value"].mean())
        self.spend = clv.GammaGammaModel()
        self.spend.fit(data=self._spend_frame(repeat), method="map", progressbar=False, random_seed=seed)
        return self

    @staticmethod
    def _spend_frame(repeat: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "customer_id": np.arange(len(repeat)),
                "frequency": repeat["frequency"].to_numpy(dtype=float),
                "monetary_value": repeat["repeat_mean_value"].to_numpy(dtype=float),
            }
        )

    def predict_lapse(self, snap: pd.DataFrame, horizon_days: int = 90) -> np.ndarray:
        p = self.purchases.expected_probability_no_purchase(t=horizon_days, data=_purchase_frame(snap))
        return np.clip(_posterior_mean(p), 0.0, 1.0)

    def predict_alive(self, snap: pd.DataFrame) -> np.ndarray:
        return np.clip(_posterior_mean(self.purchases.expected_probability_alive(data=_purchase_frame(snap))), 0.0, 1.0)

    def predict_purchases(self, snap: pd.DataFrame, horizon_days: int = 90) -> np.ndarray:
        return _posterior_mean(self.purchases.expected_purchases(data=_purchase_frame(snap), future_t=horizon_days))

    def predict_value(self, snap: pd.DataFrame, horizon_days: int = 90) -> np.ndarray:
        expected = _posterior_mean(self.purchases.expected_purchases(data=_purchase_frame(snap), future_t=horizon_days))
        spend = np.full(len(snap), self.population_spend)
        eligible = ((snap["frequency"] > 0) & (snap["repeat_mean_value"] > 0)).to_numpy()
        if eligible.any():
            spend[eligible] = _posterior_mean(self.spend.expected_customer_spend(data=self._spend_frame(snap[eligible])))
        return np.clip(expected * spend, 0.0, None)
