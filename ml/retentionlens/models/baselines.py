"""Simple baselines every advanced model must beat."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler


class RecencyBucketModel:
    """Lapse rate per recency decile observed in the training snapshots."""

    name = "recency_rule"

    def fit(self, train: pd.DataFrame, seed: int = 0) -> "RecencyBucketModel":
        self.edges = np.unique(np.quantile(train["recency_days"], np.linspace(0, 1, 11)))
        self.prior = float(train["lapsed"].mean())
        self.rates = train["lapsed"].groupby(self._bin(train)).mean()
        return self

    def _bin(self, snap: pd.DataFrame) -> np.ndarray:
        return np.clip(np.searchsorted(self.edges, snap["recency_days"], side="right") - 1, 0, max(len(self.edges) - 2, 0))

    def predict_lapse(self, snap: pd.DataFrame) -> np.ndarray:
        return pd.Series(self._bin(snap)).map(self.rates).fillna(self.prior).to_numpy(dtype=float)


class LogisticRFM:
    """Logistic regression on log-scaled recency, frequency, spend and tenure."""

    name = "logistic_rfm"
    columns = ["recency_days", "frequency", "sales_total", "tenure_days"]

    def fit(self, train: pd.DataFrame, seed: int = 0) -> "LogisticRFM":
        self.pipeline = make_pipeline(
            FunctionTransformer(lambda x: np.log1p(np.clip(x, 0, None))),
            StandardScaler(),
            LogisticRegression(max_iter=1000, random_state=seed),
        )
        self.pipeline.fit(train[self.columns].to_numpy(dtype=float), train["lapsed"])
        return self

    def predict_lapse(self, snap: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict_proba(snap[self.columns].to_numpy(dtype=float))[:, 1]


class NaiveValueModel:
    """Next 90 days' spend = the last 90 days' spend."""

    name = "naive_last_90"

    def fit(self, train: pd.DataFrame, seed: int = 0) -> "NaiveValueModel":
        return self

    def predict_value(self, snap: pd.DataFrame, horizon_days: int = 90) -> np.ndarray:
        return np.clip(snap["sales_last_90"].to_numpy(dtype=float) * horizon_days / 90, 0, None)
