import pandas as pd

from retentionlens.data.clean import FLAGS, clean_transactions, customer_lines


def lines():
    return pd.DataFrame(
        {
            "invoice": ["1", "C2", "3", "4", "5", "5", "6"],
            "stock_code": ["85123A", "85123A", "POST", "22423", "22423", "22423", "79323P"],
            "description": ["A", "A", "POSTAGE", "B", "B", "B", "C"],
            "quantity": [6, -6, 1, 2, 3, 3, -1],
            "invoice_date": pd.to_datetime(["2010-01-01"] * 7),
            "price": [2.5, 2.5, 18.0, 0.0, 1.0, 1.0, 4.0],
            "customer_id": pd.array(["1", "1", "1", "2", None, None, "3"], dtype="string"),
            "country": pd.array(["UK"] * 7, dtype="string"),
            "source_sheet": ["s"] * 7,
        }
    )


def test_flags_are_counted_not_dropped():
    result = clean_transactions(lines())
    assert len(result.lines) == 7
    assert result.issues == {
        "rows": 7,
        "is_cancellation": 1,
        "is_negative_qty": 2,
        "is_nonpositive_price": 1,
        "is_non_product": 1,
        "is_missing_customer": 2,
        "is_duplicate": 1,
        "negative_qty_not_cancelled": 1,
        "duplicate_within_sheet": 1,
        "duplicate_across_sheets": 0,
    }
    assert set(FLAGS) <= set(result.lines.columns)


def test_cross_sheet_overlap_is_counted_separately():
    df = lines()
    overlap = df.iloc[[0]].assign(source_sheet="t")
    result = clean_transactions(pd.concat([df, overlap], ignore_index=True))
    assert result.issues["is_duplicate"] == 2
    assert result.issues["duplicate_within_sheet"] == 1
    assert result.issues["duplicate_across_sheets"] == 1


def test_line_value_signed():
    result = clean_transactions(lines())
    assert result.lines["line_value"].tolist()[:2] == [15.0, -15.0]


def test_customer_lines_keeps_cancellations_drops_unusable():
    usable = customer_lines(clean_transactions(lines()).lines)
    assert usable["invoice"].tolist() == ["1", "C2", "6"]
