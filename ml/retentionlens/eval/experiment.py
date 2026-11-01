"""Rolling-cutoff experiment: fit every model, score every evaluation cutoff, keep a run record."""
from __future__ import annotations

import json
import platform
from importlib import metadata
from pathlib import Path

import pandas as pd

from ..features.snapshot import CUTOFFS, HORIZON_DAYS, TEST_CUTOFF, build_snapshot, prepare
from ..models.baselines import LogisticRFM, NaiveValueModel, RecencyBucketModel
from ..models.btyd import BtydModel
from ..models.gbm import GbmModel
from .metrics import decile_table, lapse_metrics, reliability_table, value_metrics

CHALLENGER = "lightgbm"
LAPSE_BASELINES = ["recency_rule", "logistic_rfm", "bgnbd"]
VALUE_BASELINES = ["naive_last_90", "bgnbd_gamma_gamma"]
PACKAGES = ["pandas", "numpy", "scikit-learn", "lightgbm", "pymc-marketing", "pymc"]


def training_cutoffs(eval_cutoff: str, horizon_days: int = HORIZON_DAYS) -> list[str]:
    earlier = [c for c in CUTOFFS if c < eval_cutoff]
    for c in earlier:
        if pd.Timestamp(c) + pd.Timedelta(days=horizon_days) > pd.Timestamp(eval_cutoff):
            raise ValueError(f"label window from {c} ({horizon_days} days) crosses evaluation cutoff {eval_cutoff}")
    return earlier


def evaluation_cutoffs(include_test: bool) -> list[str]:
    dev = [c for c in CUTOFFS[1:] if c != TEST_CUTOFF]
    return dev + ([TEST_CUTOFF] if include_test else [])


def _versions() -> dict:
    found = {"python": platform.python_version()}
    for package in PACKAGES:
        try:
            found[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            found[package] = "not installed"
    return found


def _wins(results: dict, kind: str, baselines: list[str], metric: str, higher_is_better: bool) -> dict:
    wins = {}
    for baseline in baselines:
        count = 0
        for scores in results["cutoffs"].values():
            challenger, other = scores[kind][CHALLENGER][metric], scores[kind][baseline][metric]
            count += (challenger > other) if higher_is_better else (challenger < other)
        wins[baseline] = {"wins": int(count), "of": len(results["cutoffs"])}
    return wins


def run_experiment(
    lines: pd.DataFrame,
    out_dir: Path,
    include_test: bool = False,
    seed: int = 42,
    horizon_days: int = HORIZON_DAYS,
    data_sha256: str = "unknown",
) -> dict:
    prepared = prepare(lines)
    snapshots = {c: build_snapshot(prepared, c, horizon_days) for c in CUTOFFS}
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {
        "run_id": out_dir.name,
        "data_sha256": data_sha256,
        "seed": seed,
        "horizon_days": horizon_days,
        "include_test": include_test,
        "versions": _versions(),
        "cutoffs": {},
    }

    for cutoff in evaluation_cutoffs(include_test):
        train = pd.concat([snapshots[c] for c in training_cutoffs(cutoff, horizon_days)])
        test = snapshots[cutoff]
        btyd = BtydModel().fit(test, seed=seed)
        gbm = GbmModel().fit(train, seed=seed)
        lapse = {
            "recency_rule": RecencyBucketModel().fit(train, seed).predict_lapse(test),
            "logistic_rfm": LogisticRFM().fit(train, seed).predict_lapse(test),
            "bgnbd": btyd.predict_lapse(test, horizon_days),
            "lightgbm": gbm.predict_lapse(test),
        }
        value = {
            "naive_last_90": NaiveValueModel().predict_value(test, horizon_days),
            "bgnbd_gamma_gamma": btyd.predict_value(test, horizon_days),
            "lightgbm": gbm.predict_value(test, horizon_days),
        }
        y, actual = test["lapsed"].to_numpy(), test["future_value"].to_numpy()
        results["cutoffs"][cutoff] = {
            "role": "test" if cutoff == TEST_CUTOFF else "dev",
            "train_cutoffs": training_cutoffs(cutoff, horizon_days),
            "n_train_rows": int(len(train)),
            "n_customers": int(len(test)),
            "lapse": {name: lapse_metrics(y, p) for name, p in lapse.items()},
            "reliability": {name: reliability_table(y, p) for name, p in lapse.items()},
            "value": {name: value_metrics(actual, v) for name, v in value.items()},
            "value_deciles": {name: decile_table(actual, v) for name, v in value.items()},
        }
        predictions = test[["lapsed", "future_value"]].copy()
        for name, p in lapse.items():
            predictions[f"p_lapse_{name}"] = p
        for name, v in value.items():
            predictions[f"value_{name}"] = v
        predictions.to_parquet(out_dir / f"predictions_{cutoff}.parquet")

    results["comparison"] = {
        "lapse_pr_auc": _wins(results, "lapse", LAPSE_BASELINES, "pr_auc", True),
        "lapse_brier": _wins(results, "lapse", LAPSE_BASELINES, "brier", False),
        "value_gini": _wins(results, "value", VALUE_BASELINES, "normalized_gini", True),
        "value_mae": _wins(results, "value", VALUE_BASELINES, "mae", False),
    }
    config = {k: results[k] for k in ("run_id", "data_sha256", "seed", "horizon_days", "include_test", "versions")}
    config["cutoffs"], config["test_cutoff"] = CUTOFFS, TEST_CUTOFF
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (out_dir / "metrics.json").write_text(json.dumps(results, indent=2) + "\n")
    return results
