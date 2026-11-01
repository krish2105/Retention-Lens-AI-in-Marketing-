import csv

import pandas as pd

from retentionlens.data.clean import clean_transactions
from retentionlens.data.profile import build_profile, render_markdown, upsert_register


def sample():
    return pd.DataFrame(
        {
            "invoice": ["1", "C2", "3"],
            "stock_code": ["85123A", "85123A", "POST"],
            "description": ["A", "A", "POSTAGE"],
            "quantity": [6, -6, 1],
            "invoice_date": pd.to_datetime(["2009-12-01", "2010-01-05", "2011-12-09"]),
            "price": [2.5, 2.5, 18.0],
            "customer_id": pd.array(["1", "1", None], dtype="string"),
            "country": pd.array(["UK", "UK", "France"], dtype="string"),
            "source_sheet": ["a", "a", "b"],
        }
    )


def test_profile_counts():
    result = clean_transactions(sample())
    p = build_profile(result.lines, result.issues)
    assert p["rows"] == 3
    assert p["date_min"] == "2009-12-01" and p["date_max"] == "2011-12-09"
    assert p["customers"] == 1 and p["countries"] == 2 and p["invoices"] == 3
    assert p["rows_by_sheet"] == {"a": 2, "b": 1}
    assert p["top_non_product_codes"] == {"POST": 1}
    assert p["customer_model_rows"] == 2
    assert p["customer_model_net_value"] == 0.0


def test_markdown_mentions_source_and_checksum():
    result = clean_transactions(sample())
    md = render_markdown(build_profile(result.lines, result.issues), {"zip_sha256": "abc", "url": "u", "licence": "CC BY 4.0", "citation": "c", "accessed_at": "t"})
    assert "abc" in md and "CC BY 4.0" in md and "| Rows | 3 |" in md


def test_register_upsert_is_idempotent(tmp_path):
    path = tmp_path / "reg.csv"
    path.write_text("name,url,version,access_date,license,sha256,allowed_use,notes\n")
    row = {"name": "online_retail_ii", "url": "u", "version": "v", "access_date": "d", "license": "CC BY 4.0", "sha256": "s", "allowed_use": "a", "notes": "n"}
    upsert_register(path, row)
    upsert_register(path, {**row, "sha256": "s2"})
    rows = list(csv.DictReader(path.open()))
    assert len(rows) == 1 and rows[0]["sha256"] == "s2"
