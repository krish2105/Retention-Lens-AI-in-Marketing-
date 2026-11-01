import pandas as pd

from retentionlens.data.clean import clean_transactions
from retentionlens.features.snapshot import FEATURES, build_snapshot, prepare


def flagged(rows):
    df = pd.DataFrame(rows, columns=["invoice", "stock_code", "quantity", "invoice_date", "price", "customer_id"])
    df["description"] = "x"
    df["country"] = pd.array(["United Kingdom"] * len(df), dtype="string")
    df["customer_id"] = pd.array(df["customer_id"], dtype="string")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["source_sheet"] = "s"
    return clean_transactions(df).lines


ROWS = [
    ("1", "10001", 2, "2011-01-01 10:00", 10.0, "A"),   # A day 1: 20
    ("2", "10002", 1, "2011-02-10 09:00", 30.0, "A"),   # A day 2: 30
    ("C3", "10002", -1, "2011-02-15 09:00", 30.0, "A"), # A return: 30
    ("4", "10001", 5, "2011-02-20 12:00", 2.0, "B"),    # B one day: 10
    ("5", "10003", 1, "2011-03-10 12:00", 50.0, "A"),   # A buys in window
    ("6", "10003", 1, "2011-07-01 12:00", 99.0, "B"),   # B after window: ignored
]


def snap():
    return build_snapshot(prepare(flagged(ROWS)), "2011-03-01")


def test_features_from_history_only():
    s = snap()
    a, b = s.loc["A"], s.loc["B"]
    assert a["recency_days"] == 19 and a["tenure_days"] == 59
    assert a["frequency"] == 1 and a["btyd_recency"] == 40 and a["T"] == 59
    assert a["sales_total"] == 50.0 and a["returns_total"] == 30.0
    assert a["repeat_mean_value"] == 30.0
    assert b["frequency"] == 0 and pd.isna(b["repeat_mean_value"])
    assert set(FEATURES) <= set(s.columns)


def test_labels_from_window_only():
    s = snap()
    assert s.loc["A", "lapsed"] == 0 and s.loc["A", "future_value"] == 50.0
    assert s.loc["B", "lapsed"] == 1 and s.loc["B", "future_value"] == 0.0


def test_no_leakage_from_rows_after_cutoff():
    changed = [r if pd.Timestamp(r[3]) < pd.Timestamp("2011-03-01") else (r[0], r[1], r[2] * 10, r[3], r[4], r[5]) for r in ROWS]
    before = snap()[FEATURES]
    after = build_snapshot(prepare(flagged(changed)), "2011-03-01")[FEATURES]
    pd.testing.assert_frame_equal(before, after)


def test_customer_without_history_is_excluded():
    assert "C" not in build_snapshot(prepare(flagged(ROWS + [("7", "10001", 1, "2011-03-05 10:00", 5.0, "C")])), "2011-03-01").index


def test_negative_window_spend_floors_at_zero():
    rows = ROWS[:4] + [("C9", "10001", -3, "2011-03-05 10:00", 10.0, "B")]
    assert build_snapshot(prepare(flagged(rows)), "2011-03-01").loc["B", "future_value"] == 0.0
