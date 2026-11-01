import numpy as np
import pytest

from retentionlens.eval.metrics import decile_table, lapse_metrics, normalized_gini, reliability_table, value_metrics


def test_perfect_and_reversed_gini():
    a = np.array([0, 1, 2, 3, 10.0])
    assert normalized_gini(a, a) == pytest.approx(1.0)
    assert normalized_gini(a, -a) < -0.5


def test_lapse_metrics_known_values():
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.7, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    m = lapse_metrics(y, p, top_frac=0.2)
    assert m["base_rate"] == 0.2 and m["pr_auc"] == pytest.approx(1.0) and m["roc_auc"] == pytest.approx(1.0)
    assert m["top_precision"] == 1.0 and m["top_lift"] == pytest.approx(5.0)
    assert m["brier"] == pytest.approx(np.mean((p - y) ** 2))


def test_reliability_counts_sum_to_n():
    rng = np.random.default_rng(0)
    p = rng.random(500)
    y = (rng.random(500) < p).astype(int)
    table = reliability_table(y, p)
    assert sum(r["n"] for r in table) == 500
    assert all(abs(r["observed"] - r["mean_pred"]) < 0.2 for r in table if r["n"] > 30)


def test_value_metrics_and_deciles():
    a = np.arange(100, dtype=float)
    m = value_metrics(a, a + 1)
    assert m["mae"] == pytest.approx(1.0) and m["spearman"] == pytest.approx(1.0)
    assert len(decile_table(a, a)) == 10
