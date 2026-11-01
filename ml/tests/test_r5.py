import numpy as np
import pandas as pd

from retentionlens.features.seasonal import add_seasonal_features, season_multiplier, seasonal_lapse
from retentionlens.models.ziln import ZilnModel


def prepared_frame(days, customers=40, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(customers):
        for d in pd.date_range("2022-01-03", periods=days, freq="7D"):
            if rng.random() < (0.6 if d.month in (10, 11) else 0.3):
                rows.append({"customer_id": f"C{c}", "day": d, "is_sale": True, "sale_value": float(rng.gamma(2, 50))})
    return pd.DataFrame(rows)


def test_multiplier_needs_a_year_and_tracks_the_season():
    short = prepared_frame(30)
    assert season_multiplier(short, "2022-06-01") == {"multiplier": 1.0, "available": False, "reason": "less than a year of history before the cutoff"}
    long = prepared_frame(110)
    peak, quiet = season_multiplier(long, "2023-10-01"), season_multiplier(long, "2023-04-01")
    assert peak["available"] and peak["multiplier"] > 1 > quiet["multiplier"]


def test_seasonal_lapse_moves_the_right_way():
    p = np.array([0.2, 0.5, 0.9])
    assert (seasonal_lapse(p, 2.0) < p).all() and (seasonal_lapse(p, 0.5) > p).all()
    assert np.allclose(seasonal_lapse(p, 1.0), p)


def test_same_window_features_use_only_last_year():
    long = prepared_frame(110)
    snap = pd.DataFrame(index=pd.Index([f"C{i}" for i in range(40)], name="customer_id"))
    out = add_seasonal_features(snap, long, "2023-10-01")
    last_year = long[(long["day"] >= "2022-10-01") & (long["day"] < "2022-12-30")]
    assert np.isclose(out["sales_same_window_last_year"].sum(), last_year["sale_value"].sum())
    assert out["days_to_christmas"].iloc[0] == 85


def test_ziln_learns_and_predicts_finite_values():
    rng = np.random.default_rng(0)
    n = 1500
    x = rng.normal(size=n)
    spend = np.where(rng.random(n) < 1 / (1 + np.exp(-2 * x)), np.exp(4 + 0.5 * x + rng.normal(0, 0.3, n)), 0.0)
    frame = pd.DataFrame({"a": x, "b": rng.normal(size=n), "future_value": spend})
    model = ZilnModel(columns=["a", "b"]).fit(frame, seed=1)
    assert model.history[-1] < model.history[0]
    value, lapse = model.predict_value(frame), model.predict_lapse(frame)
    assert np.isfinite(value).all() and ((lapse >= 0) & (lapse <= 1)).all()
    buyers = spend > 0
    assert lapse[buyers].mean() < lapse[~buyers].mean()
    assert np.corrcoef(value, spend)[0, 1] > 0.5
