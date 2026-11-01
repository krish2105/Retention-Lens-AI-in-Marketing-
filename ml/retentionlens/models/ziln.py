"""Zero-inflated lognormal (ZILN) neural network: the deep-learning challenger (R5).

One small network with three outputs per customer: the logit of "spends anything in the
next 90 days", and the mean and spread of log-spend if they do (Wang, Liu & Miao, 2019,
"A Deep Probabilistic Model for Customer Lifetime Value Prediction"). Written in NumPy with
hand-derived gradients so it needs no deep-learning framework and is fully reproducible.

Hyperparameters are fixed in advance and not tuned on any evaluation cutoff.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..features.snapshot import FEATURES
from ..features.seasonal import SEASONAL_FEATURES

LOG_FEATURES = {"recency_days", "tenure_days", "frequency", "sales_total", "sales_mean", "purchase_days_last_90", "purchase_days_last_180",
                "sales_last_90", "sales_last_180", "returns_total", "distinct_products", "lines_per_day", "mean_gap_days",
                "sales_same_window_last_year", "purchase_days_same_window_last_year", "days_to_christmas"}
HIDDEN, EPOCHS, BATCH, LR, L2 = 32, 40, 256, 3e-3, 1e-4
# v2 (changed after v1 diverged on the dev cutoffs, so these two choices are dev-informed): constant
# training features are zeroed (see fit), and the spread of log-spend is bounded, because the lognormal mean exp(mu + sigma^2 / 2) explodes when sigma grows.
SIGMA_MIN, SIGMA_MAX = 0.05, 2.0


def _sigma(s):
    return SIGMA_MIN + (SIGMA_MAX - SIGMA_MIN) * _sigmoid(s)


def _sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -40, 40)))


class ZilnModel:
    name = "ziln_nn"

    def __init__(self, columns: list[str] | None = None):
        # v3 (dev-informed, final): calendar features that are the same for every customer at a cutoff
        # (month, days to Christmas) are left out. With 1-3 training cutoffs the network can only
        # extrapolate them, which blew up spend predictions. Customer-level last-year features stay.
        self.columns = columns or FEATURES + [f for f in SEASONAL_FEATURES if f not in ("cutoff_month", "days_to_christmas")]

    def _matrix(self, snap: pd.DataFrame) -> np.ndarray:
        frame = snap[self.columns].astype(float).fillna(0.0)
        for column in self.columns:
            if column in LOG_FEATURES:
                frame[column] = np.log1p(frame[column].clip(lower=0))
        return frame.to_numpy()

    def fit(self, train: pd.DataFrame, seed: int = 0) -> "ZilnModel":
        rng = np.random.default_rng(seed)
        x = self._matrix(train)
        # A feature that is constant in training (e.g. the month, when training spans one cutoff)
        # carries no information; give it zero weight instead of dividing by a near-zero spread.
        std = x.std(0)
        self.mean, self.scale, self.keep = x.mean(0), np.where(std > 1e-9, std, 1.0), (std > 1e-9).astype(float)
        x = (x - self.mean) / self.scale * self.keep
        y = train["future_value"].to_numpy(dtype=float)
        positive = (y > 0).astype(float)
        log_y = np.log(np.where(y > 0, y, 1.0))
        d = x.shape[1]
        params = {
            "W1": rng.normal(0, np.sqrt(2 / d), (d, HIDDEN)), "b1": np.zeros(HIDDEN),
            "W2": rng.normal(0, np.sqrt(1 / HIDDEN), (HIDDEN, 3)), "b2": np.array([0.0, float(log_y[positive > 0].mean()) if positive.any() else 0.0, 0.0]),
        }
        moments = {k: (np.zeros_like(v), np.zeros_like(v)) for k, v in params.items()}
        step = 0
        self.history = []
        for _ in range(EPOCHS):
            order = rng.permutation(len(x))
            total = 0.0
            for start in range(0, len(x), BATCH):
                idx = order[start : start + BATCH]
                loss, grads = self._loss_and_grads(params, x[idx], positive[idx], log_y[idx])
                total += loss * len(idx)
                step += 1
                for key, grad in grads.items():
                    grad = grad + L2 * params[key] if key.startswith("W") else grad
                    m, v = moments[key]
                    m = 0.9 * m + 0.1 * grad
                    v = 0.999 * v + 0.001 * grad**2
                    moments[key] = (m, v)
                    params[key] -= LR * (m / (1 - 0.9**step)) / (np.sqrt(v / (1 - 0.999**step)) + 1e-8)
            self.history.append(total / len(x))
        self.params = params
        return self

    @staticmethod
    def _forward(params, x):
        h_pre = x @ params["W1"] + params["b1"]
        h = np.maximum(h_pre, 0)
        out = h @ params["W2"] + params["b2"]
        return h_pre, h, out

    def _loss_and_grads(self, params, x, positive, log_y):
        h_pre, h, out = self._forward(params, x)
        logit, mu, s = out[:, 0], out[:, 1], out[:, 2]
        sigma = _sigma(s)
        p = _sigmoid(logit)
        z = (log_y - mu) / sigma
        n = len(x)
        bce = -(positive * np.log(p + 1e-12) + (1 - positive) * np.log(1 - p + 1e-12))
        nll = positive * (np.log(sigma) + 0.5 * z**2 + log_y)
        loss = float(np.mean(bce + nll))
        d_out = np.zeros_like(out)
        d_out[:, 0] = (p - positive) / n
        d_out[:, 1] = positive * (-z / sigma) / n
        d_out[:, 2] = positive * (1 / sigma - z**2 / sigma) * (SIGMA_MAX - SIGMA_MIN) * _sigmoid(s) * (1 - _sigmoid(s)) / n
        grads = {"W2": h.T @ d_out, "b2": d_out.sum(0)}
        d_h = (d_out @ params["W2"].T) * (h_pre > 0)
        grads["W1"], grads["b1"] = x.T @ d_h, d_h.sum(0)
        return loss, grads

    def _heads(self, snap: pd.DataFrame):
        x = (self._matrix(snap) - self.mean) / self.scale * self.keep
        _, _, out = self._forward(self.params, x)
        return _sigmoid(out[:, 0]), out[:, 1], _sigma(out[:, 2])

    def predict_lapse(self, snap: pd.DataFrame) -> np.ndarray:
        p, _, _ = self._heads(snap)
        return 1 - p

    def predict_value(self, snap: pd.DataFrame, horizon_days: int = 90) -> np.ndarray:
        p, mu, sigma = self._heads(snap)
        return p * np.exp(np.clip(mu + sigma**2 / 2, -20, 20))
