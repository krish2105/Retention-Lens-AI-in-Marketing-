"""Score every account as of the day after the data ends, for the weekly review UI."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ..features.seasonal import season_multiplier, seasonal_lapse
from ..features.snapshot import build_snapshot
from ..models.btyd import BtydModel

HIGH, WATCH = 0.75, 0.5


def risk_band(p_lapse: float) -> str:
    if p_lapse >= HIGH:
        return "high"
    if p_lapse >= WATCH:
        return "watch"
    return "healthy"


def reasons_for(row: pd.Series) -> list[str]:
    """Plain-language evidence for a reviewer; every number comes from the snapshot row."""
    if row["frequency"] == 0:
        return ["Only one purchase day so far"]
    reasons = []
    gap = row["mean_gap_days"]
    if not math.isnan(gap) and row["recency_days"] > 2 * gap:
        reasons.append(f"No order for {int(row['recency_days'])} days; usual gap {gap:.0f} days")
    prior = row["sales_last_180"] - row["sales_last_90"]
    if prior > 0 and row["sales_last_90"] < 0.5 * prior:
        reasons.append(f"Spend in last 90 days down {100 * (1 - row['sales_last_90'] / prior):.0f}% on the 90 days before")
    if row["return_rate"] > 0.1:
        reasons.append(f"Returns are {100 * row['return_rate']:.0f}% of spend")
    if row["purchase_days_last_180"] == 0:
        reasons.append("No orders in the last 6 months")
    return reasons or ["Ordering on its usual cadence"]


def cohort_matrix(days: pd.DataFrame, max_months: int = 24) -> list[dict]:
    """Share of each first-purchase-month cohort that buys again N months later."""
    frame = days[["customer_id", "day"]].copy()
    frame["month"] = frame["day"].dt.to_period("M")
    first = frame.groupby("customer_id")["month"].min().rename("cohort")
    frame = frame.join(first, on="customer_id")
    frame["offset"] = (frame["month"] - frame["cohort"]).apply(lambda d: d.n)
    last_month = frame["month"].max()
    out = []
    for cohort, group in frame.groupby("cohort"):
        size = group["customer_id"].nunique()
        span = min(max_months, (last_month - cohort).n + 1)
        active = group.groupby("offset")["customer_id"].nunique()
        retention = [round(float(active.get(m, 0)) / size, 4) for m in range(span)]
        out.append({"cohort": str(cohort), "size": int(size), "retention": retention})
    return out


def net_adjusted(snap: pd.DataFrame) -> pd.DataFrame:
    """Spend net of returns, so a cancelled bulk order does not look like a valuable customer."""
    out = snap.copy()
    kept = 1 - out["return_rate"].clip(0, 1)
    out["net_sales_total"] = (out["sales_total"] - out["returns_total"]).clip(lower=0)
    out["repeat_mean_value"] = out["repeat_mean_value"] * kept
    return out


def score_accounts(prepared: pd.DataFrame, cutoff: str, seed: int = 42, seasonal: bool = True) -> pd.DataFrame:
    """BG/NBD + Gamma-Gamma, with the R5 seasonal multiplier (it beat the plain model on lapse
    Brier and value MAE on all three dev cutoffs; ranking metrics are unchanged by design)."""
    snap = net_adjusted(build_snapshot(prepared, cutoff))
    model = BtydModel().fit(snap, seed=seed)
    multiplier = season_multiplier(prepared, cutoff)["multiplier"] if seasonal else 1.0
    scored = snap.copy()
    scored["p_lapse"] = seasonal_lapse(model.predict_lapse(snap), multiplier)
    scored["p_alive"] = model.predict_alive(snap)
    scored["expected_purchases_90"] = model.predict_purchases(snap) * multiplier
    scored["expected_value_90"] = model.predict_value(snap) * multiplier
    run_rate = scored["net_sales_total"] / np.maximum(scored["tenure_days"], 90) * 90
    scored["value_at_risk_90"] = scored["p_lapse"] * run_rate
    scored["risk_band"] = scored["p_lapse"].map(risk_band)
    scored["reasons"] = [reasons_for(row) for _, row in scored.iterrows()]
    countries = prepared.groupby("customer_id", observed=True)["country"].first()
    scored["country"] = countries.reindex(scored.index).astype(str)
    return scored.sort_values("value_at_risk_90", ascending=False)
