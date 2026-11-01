"""Split-conformal intervals for 90-day customer value.

Residuals are taken on the log1p scale, so the interval widens with the predicted value.
Calibration uses an earlier cutoff whose outcomes are already known; coverage on a later
cutoff then holds if the residual distribution is stable over time (an assumption we test).
"""
from __future__ import annotations

import math

import numpy as np


def residual_quantiles(y_true, y_pred, alpha: float = 0.2) -> tuple[float, float]:
    residuals = np.log1p(np.clip(np.asarray(y_true, float), 0, None)) - np.log1p(np.clip(np.asarray(y_pred, float), 0, None))
    n = len(residuals)
    if n < 20:
        raise ValueError("need at least 20 calibration customers")
    # Finite-sample correction: use the ceil((n+1)(1-a/2))/n empirical quantile on each side.
    upper = min(1.0, math.ceil((n + 1) * (1 - alpha / 2)) / n)
    lower = max(0.0, math.floor((n + 1) * (alpha / 2)) / n)
    return float(np.quantile(residuals, lower)), float(np.quantile(residuals, upper))


def interval(y_pred, quantiles: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
    base = np.log1p(np.clip(np.asarray(y_pred, float), 0, None))
    low = np.clip(np.expm1(base + quantiles[0]), 0, None)
    high = np.clip(np.expm1(base + quantiles[1]), 0, None)
    return low, high


def coverage(y_true, low, high) -> float:
    y = np.asarray(y_true, float)
    return float(np.mean((y >= low) & (y <= high)))
