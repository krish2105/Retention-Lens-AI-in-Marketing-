"""Seasonality (R5): per-customer same-window-last-year features and a population multiplier.

Wholesale gift trade peaks before Christmas. BG/NBD assumes a steady purchase rate, so it
over-predicts after the peak and under-predicts going into it. Two fixes are tested:
1. features describing the same 90-day calendar window one year earlier (for supervised models);
2. a multiplier on BG/NBD's expected purchases: activity in that window last year relative
   to an average 90-day window in the year before the cutoff.
Both use only data from before the cutoff.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEASONAL_FEATURES = ["sales_same_window_last_year", "purchase_days_same_window_last_year", "days_to_christmas", "cutoff_month"]


def _window(prepared: pd.DataFrame, start: pd.Timestamp, days: int) -> pd.DataFrame:
    sales = prepared[prepared["is_sale"]]
    return sales[(sales["day"] >= start) & (sales["day"] < start + pd.Timedelta(days=days))]


def add_seasonal_features(snap: pd.DataFrame, prepared: pd.DataFrame, cutoff: str, horizon_days: int = 90) -> pd.DataFrame:
    start = pd.Timestamp(cutoff)
    last_year = _window(prepared, start - pd.Timedelta(days=365), horizon_days)
    grouped = last_year.groupby("customer_id", observed=True)
    out = snap.copy()
    out["sales_same_window_last_year"] = grouped["sale_value"].sum().reindex(out.index).fillna(0.0)
    out["purchase_days_same_window_last_year"] = grouped["day"].nunique().reindex(out.index).fillna(0).astype(float)
    christmas = pd.Timestamp(year=start.year, month=12, day=25)
    if christmas < start:
        christmas = pd.Timestamp(year=start.year + 1, month=12, day=25)
    out["days_to_christmas"] = float((christmas - start).days)
    out["cutoff_month"] = float(start.month)
    return out


def season_multiplier(prepared: pd.DataFrame, cutoff: str, horizon_days: int = 90) -> dict:
    """Purchase-days in the coming window last year / average 90-day window in the past year.

    Returns 1.0 (no adjustment) when the history does not reach back a full year.
    """
    start = pd.Timestamp(cutoff)
    year_start = start - pd.Timedelta(days=365)
    if prepared["day"].min() > year_start:
        return {"multiplier": 1.0, "available": False, "reason": "less than a year of history before the cutoff"}
    sales = prepared[prepared["is_sale"]][["customer_id", "day"]].drop_duplicates()
    year = sales[(sales["day"] >= year_start) & (sales["day"] < start)]
    window = year[year["day"] < year_start + pd.Timedelta(days=horizon_days)]
    expected = len(year) * horizon_days / 365
    multiplier = float(len(window) / expected) if expected else 1.0
    return {"multiplier": round(float(np.clip(multiplier, 0.5, 2.0)), 4), "available": True, "window_purchase_days": int(len(window)), "average_window": round(expected, 1)}


def seasonal_lapse(p_lapse: np.ndarray, multiplier: float) -> np.ndarray:
    """Scale the purchase rate: if P(no purchase) = exp(-rate * t), a rate x m gives P^m."""
    return np.clip(np.power(np.clip(p_lapse, 1e-9, 1.0), multiplier), 0.0, 1.0)
