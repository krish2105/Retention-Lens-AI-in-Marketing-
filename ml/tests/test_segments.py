import numpy as np
import pandas as pd

from retentionlens.serving.segments import galaxy_points, name_segment, rfm_scores


def test_segment_names():
    assert name_segment(5, 5, 5) == "Champions"
    assert name_segment(1, 5, 5) == "Can't lose"
    assert name_segment(2, 3, 2) == "At risk"
    assert name_segment(5, 1, 1) == "New"
    assert name_segment(1, 1, 1) == "Hibernating"


def scored(n=50):
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "recency_days": rng.integers(1, 400, n), "frequency": rng.integers(0, 30, n),
        "net_sales_total": rng.gamma(2, 500, n), "expected_value_90": rng.gamma(2, 50, n),
        "risk_band": ["high"] * n,
    }, index=[f"c{i}" for i in range(n)])


def test_rfm_quintiles_and_recency_reversed():
    s = scored()
    r = rfm_scores(s)
    assert set(r["r_score"]) == {1, 2, 3, 4, 5}
    assert r.loc[s["recency_days"].idxmin(), "r_score"] == 5


def test_galaxy_points_are_unit_scaled():
    pts = galaxy_points(scored(), pd.Series(["Champions"] * 50))
    for axis in "xyz":
        vals = [p[axis] for p in pts]
        assert min(vals) >= -1 and max(vals) <= 1
