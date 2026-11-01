"""One row per customer per cutoff: features from before it, labels from the 90 days after."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..data.clean import customer_lines

CUTOFFS = ["2010-09-01", "2010-12-01", "2011-03-01", "2011-06-01", "2011-09-01"]
TEST_CUTOFF = "2011-09-01"
HORIZON_DAYS = 90
FEATURES = [
    "recency_days",
    "tenure_days",
    "frequency",
    "sales_total",
    "sales_mean",
    "purchase_days_last_90",
    "purchase_days_last_180",
    "sales_last_90",
    "sales_last_180",
    "returns_total",
    "return_rate",
    "distinct_products",
    "lines_per_day",
    "mean_gap_days",
    "is_uk",
]


def prepare(lines: pd.DataFrame) -> pd.DataFrame:
    """Customer-usable lines with the per-line columns snapshots need."""
    usable = customer_lines(lines)
    is_sale = ~usable["is_cancellation"] & (usable["quantity"] > 0)
    return pd.DataFrame(
        {
            "customer_id": usable["customer_id"],
            "invoice": usable["invoice"],
            "description": usable["description"],
            "day": usable["invoice_date"].dt.normalize(),
            "stock_code": usable["stock_code"],
            "country": usable["country"],
            "is_sale": is_sale,
            "sale_value": usable["line_value"].where(is_sale, 0.0),
            "return_value": (-usable["line_value"]).where(~is_sale, 0.0),
            "line_value": usable["line_value"],
        }
    )


def build_snapshot(prepared: pd.DataFrame, cutoff: str, horizon_days: int = HORIZON_DAYS) -> pd.DataFrame:
    start = pd.Timestamp(cutoff)
    end = start + pd.Timedelta(days=horizon_days)
    history = prepared[prepared["day"] < start]
    window = prepared[(prepared["day"] >= start) & (prepared["day"] < end)]

    sales = history[history["is_sale"]]
    days = sales.groupby(["customer_id", "day"], observed=True)["sale_value"].sum().reset_index()
    days = days[days["sale_value"] > 0]
    by_customer = days.groupby("customer_id", observed=True)
    first, last = by_customer["day"].min(), by_customer["day"].max()

    snap = pd.DataFrame({"purchase_days": by_customer["day"].count()})
    snap["recency_days"] = (start - last).dt.days
    snap["tenure_days"] = (start - first).dt.days
    snap["frequency"] = snap["purchase_days"] - 1
    snap["btyd_recency"] = (last - first).dt.days
    snap["T"] = snap["tenure_days"]
    snap["sales_total"] = by_customer["sale_value"].sum()
    snap["sales_mean"] = by_customer["sale_value"].mean()

    repeat = days[days["day"] > days["customer_id"].map(first)]
    snap["repeat_mean_value"] = repeat.groupby("customer_id", observed=True)["sale_value"].mean()

    for span in (90, 180):
        recent = days[days["day"] >= start - pd.Timedelta(days=span)].groupby("customer_id", observed=True)
        snap[f"purchase_days_last_{span}"] = recent["day"].count()
        snap[f"sales_last_{span}"] = recent["sale_value"].sum()

    snap["returns_total"] = history.groupby("customer_id", observed=True)["return_value"].sum()
    snap["distinct_products"] = sales.groupby("customer_id", observed=True)["stock_code"].nunique()
    snap["lines_per_day"] = sales.groupby("customer_id", observed=True).size() / snap["purchase_days"]
    counts = ["purchase_days_last_90", "purchase_days_last_180", "sales_last_90", "sales_last_180", "returns_total", "distinct_products"]
    snap[counts] = snap[counts].fillna(0)
    snap["return_rate"] = snap["returns_total"] / snap["sales_total"]
    snap["mean_gap_days"] = np.where(snap["frequency"] > 0, snap["btyd_recency"] / snap["frequency"].clip(lower=1), np.nan)
    snap["is_uk"] = history.groupby("customer_id", observed=True)["country"].first().reindex(snap.index) == "United Kingdom"

    future_days = window[window["is_sale"]].groupby("customer_id", observed=True)["day"].nunique()
    snap["future_purchase_days"] = future_days.reindex(snap.index).fillna(0).astype(int)
    snap["lapsed"] = (snap["future_purchase_days"] == 0).astype(int)
    net = window.groupby("customer_id", observed=True)["line_value"].sum().reindex(snap.index).fillna(0.0)
    snap["future_value"] = net.clip(lower=0.0)
    snap["cutoff"] = start
    snap.index.name = "customer_id"
    return snap.sort_index()
