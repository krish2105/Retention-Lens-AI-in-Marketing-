"""Lapse (classification) and value (regression) metrics."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def lapse_metrics(y, p, top_frac: float = 0.1) -> dict:
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    k = max(1, int(round(len(y) * top_frac)))
    top = np.argsort(-p, kind="mergesort")[:k]
    base_rate = float(y.mean())
    top_precision = float(y[top].mean())
    return {
        "base_rate": base_rate,
        "pr_auc": float(average_precision_score(y, p)),
        "roc_auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "top_precision": top_precision,
        "top_lift": top_precision / base_rate if base_rate else float("nan"),
    }


def reliability_table(y, p, bins: int = 10) -> list[dict]:
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    edges = np.linspace(0, 1, bins + 1)
    index = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    table = []
    for b in range(bins):
        mask = index == b
        n = int(mask.sum())
        table.append(
            {
                "bin_low": float(edges[b]),
                "bin_high": float(edges[b + 1]),
                "n": n,
                "mean_pred": float(p[mask].mean()) if n else None,
                "observed": float(y[mask].mean()) if n else None,
            }
        )
    return table


def _gini(actual: np.ndarray, pred: np.ndarray) -> float:
    order = np.argsort(-pred, kind="mergesort")
    cumulative = np.cumsum(actual[order]) / actual.sum()
    n = len(actual)
    return float(cumulative.sum() / n - (n + 1) / (2 * n))


def normalized_gini(actual, pred) -> float:
    """How well `pred` ranks `actual` value, relative to the perfect ranking (1.0)."""
    actual, pred = np.asarray(actual, dtype=float), np.asarray(pred, dtype=float)
    perfect = _gini(actual, actual)
    return _gini(actual, pred) / perfect if perfect else float("nan")


def value_metrics(actual, pred) -> dict:
    actual, pred = np.asarray(actual, dtype=float), np.asarray(pred, dtype=float)
    return {
        "mae": float(np.mean(np.abs(actual - pred))),
        "normalized_gini": normalized_gini(actual, pred),
        "spearman": float(pd.Series(actual).corr(pd.Series(pred), method="spearman")),
        "total_actual": float(actual.sum()),
        "total_pred": float(pred.sum()),
    }


def decile_table(actual, pred) -> list[dict]:
    """Customers split into ten groups by predicted value (decile 1 = highest)."""
    frame = pd.DataFrame({"actual": np.asarray(actual, dtype=float), "pred": np.asarray(pred, dtype=float)})
    frame["decile"] = pd.qcut(frame["pred"].rank(method="first", ascending=False), 10, labels=range(1, 11))
    grouped = frame.groupby("decile", observed=True).agg(n=("actual", "size"), mean_actual=("actual", "mean"), mean_pred=("pred", "mean"))
    return [{"decile": int(d), **{k: float(v) for k, v in row.items()}} for d, row in grouped.iterrows()]
