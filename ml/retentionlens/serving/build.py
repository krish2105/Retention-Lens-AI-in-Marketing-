"""Write the JSON files the API serves. Every number shown in the UI comes from here."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ..features.snapshot import TEST_CUTOFF, prepare
from .scoring import cohort_matrix, score_accounts

LIVE_CUTOFF = "2011-12-10"  # the day after the last invoice in the dataset
MODEL_NAME = "BG/NBD + Gamma-Gamma with seasonal multiplier (PyMC-Marketing 1.3, MAP fit)"
ACCOUNT_FIELDS = [
    "country", "risk_band", "p_lapse", "p_alive", "expected_purchases_90", "expected_value_90",
    "value_at_risk_90", "recency_days", "tenure_days", "frequency", "sales_total", "sales_last_90",
    "sales_last_180", "net_sales_total", "returns_total", "return_rate", "distinct_products", "mean_gap_days", "reasons",
]


def _clean(value):
    if isinstance(value, float):
        return None if value != value else round(value, 4)
    if hasattr(value, "item"):
        return _clean(value.item())
    return value


def _write(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n")


def account_records(scored: pd.DataFrame, extra: pd.DataFrame | None = None) -> list[dict]:
    frame = scored[ACCOUNT_FIELDS]
    if extra is not None:
        frame = frame.join(extra)
    return [{"customer_id": str(cid), **{k: _clean(v) for k, v in row.items()}} for cid, row in frame.iterrows()]


def timeline(prepared: pd.DataFrame) -> dict:
    monthly = prepared.assign(month=prepared["day"].dt.to_period("M").astype(str))
    grouped = monthly.groupby(["customer_id", "month"], observed=True)[["sale_value", "return_value"]].sum().reset_index()
    out: dict[str, list] = {}
    for row in grouped.itertuples(index=False):
        out.setdefault(str(row.customer_id), []).append([row.month, round(row.sale_value, 2), round(row.return_value, 2)])
    return out


def build_serving(repo: Path, extra_builders=()) -> dict:
    out = repo / "artefacts" / "serving"
    out.mkdir(parents=True, exist_ok=True)
    prepared = prepare(pd.read_parquet(repo / "data" / "interim" / "transactions_flagged.parquet"))
    scored = score_accounts(prepared, LIVE_CUTOFF)

    from ..features.seasonal import season_multiplier
    from ..ingest.intervals import add_value_intervals

    bounds, interval_meta = add_value_intervals(prepared, scored, LIVE_CUTOFF)
    extras = [bounds] + [builder(prepared, scored, out) for builder in extra_builders]
    extra = pd.concat([e for e in extras if e is not None], axis=1) if any(e is not None for e in extras) else None
    _write(out / "accounts.json", account_records(scored, extra))
    _write(out / "timeline.json", timeline(prepared))
    sale_days = prepared[prepared["is_sale"]][["customer_id", "day"]].drop_duplicates()
    _write(out / "cohorts.json", cohort_matrix(sale_days))

    manifest = json.loads((repo / "data" / "raw" / "online_retail_ii.manifest.json").read_text())
    evaluation = json.loads((repo / "reports" / "model_results.json").read_text())
    test = evaluation["cutoffs"][TEST_CUTOFF]
    bands = scored["risk_band"].value_counts().to_dict()
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scoring_cutoff": LIVE_CUTOFF,
        "horizon_days": 90,
        "model": MODEL_NAME,
        "data_sha256": manifest["zip_sha256"],
        "data_source": manifest["citation"],
        "licence": manifest["licence"],
        "accounts": int(len(scored)),
        "bands": {k: int(bands.get(k, 0)) for k in ("high", "watch", "healthy")},
        "value_at_risk_high": round(float(scored.loc[scored["risk_band"] == "high", "value_at_risk_90"].sum()), 2),
        "expected_value_total": round(float(scored["expected_value_90"].sum()), 2),
        "evaluation_run": evaluation["run_id"],
        "season": season_multiplier(prepared, LIVE_CUTOFF),
        "intervals": interval_meta,
        "frozen_test": {
            "cutoff": TEST_CUTOFF,
            "customers": test["n_customers"],
            "pr_auc": test["lapse"]["bgnbd"]["pr_auc"],
            "brier": test["lapse"]["bgnbd"]["brier"],
            "value_gini": test["value"]["bgnbd_gamma_gamma"]["normalized_gini"],
        },
    }
    _write(out / "summary.json", summary)
    _write(out / "model_eval.json", evaluation)
    _write(out / "data_profile.json", json.loads((repo / "reports" / "data_profile.json").read_text()))
    with (repo / "project" / "DATA_SOURCE_REGISTER.csv").open(newline="") as handle:
        _write(out / "sources.json", list(csv.DictReader(handle)))
    return summary
