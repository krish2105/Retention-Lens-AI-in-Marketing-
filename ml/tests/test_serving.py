import pandas as pd

from retentionlens.serving.scoring import cohort_matrix, reasons_for, risk_band


def test_risk_band_thresholds():
    assert risk_band(0.9) == "high" and risk_band(0.75) == "high"
    assert risk_band(0.6) == "watch" and risk_band(0.2) == "healthy"


def test_reasons_describe_the_evidence():
    row = pd.Series({"frequency": 4, "recency_days": 200, "mean_gap_days": 40.0, "sales_last_90": 0.0,
                     "sales_last_180": 500.0, "return_rate": 0.2, "purchase_days_last_180": 1})
    text = " | ".join(reasons_for(row))
    assert "200 days" in text and "usual gap 40 days" in text
    assert "down 100%" in text and "Returns are 20%" in text


def test_single_purchase_reason():
    row = pd.Series({"frequency": 0, "recency_days": 30, "mean_gap_days": float("nan"), "sales_last_90": 50.0,
                     "sales_last_180": 50.0, "return_rate": 0.0, "purchase_days_last_180": 1})
    assert reasons_for(row) == ["Only one purchase day so far"]


def test_net_adjustment_zeroes_fully_returned_spend():
    from retentionlens.serving.scoring import net_adjusted

    snap = pd.DataFrame({"sales_total": [1000.0, 200.0], "returns_total": [1000.0, 50.0],
                         "return_rate": [1.0, 0.25], "repeat_mean_value": [500.0, 100.0]})
    out = net_adjusted(snap)
    assert out["net_sales_total"].tolist() == [0.0, 150.0]
    assert out["repeat_mean_value"].tolist() == [0.0, 75.0]


def test_cohort_matrix_shares():
    days = pd.DataFrame({
        "customer_id": ["a", "a", "b", "c"],
        "day": pd.to_datetime(["2010-01-05", "2010-02-10", "2010-01-20", "2010-02-01"]),
    })
    matrix = cohort_matrix(days, max_months=2)
    jan = next(c for c in matrix if c["cohort"] == "2010-01")
    assert jan["size"] == 2 and jan["retention"][0] == 1.0 and jan["retention"][1] == 0.5
    feb = next(c for c in matrix if c["cohort"] == "2010-02")
    assert feb["size"] == 1 and feb["retention"] == [1.0]
