import json
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from retentionlens.ingest.mapping import check_mapping, suggest_mapping
from retentionlens.ingest.pipeline import IngestError, inspect, parse_dates, score, validate
from retentionlens.models.conformal import coverage, interval, residual_quantiles

MAPPING = {"invoice": "Order No", "stock_code": "SKU", "description": "Item", "quantity": "Qty", "invoice_date": "Order Date",
           "price": "Unit Price", "customer_id": "Account", "country": "Country"}


def synthetic_csv(path, customers=60, seed=1):
    rng = random.Random(seed)
    rows, invoice = [], 0
    for c in range(customers):
        day = date(2024, 1, 1) + timedelta(days=rng.randint(0, 60))
        while day < date(2024, 12, 31):
            invoice += 1
            rows.append({"Order No": f"SO{invoice}", "SKU": "A-1", "Item": "Thing", "Qty": rng.choice([6, 12]), "Order Date": day.isoformat(),
                         "Unit Price": "£2.50", "Account": f"ACC{c}", "Country": "United Kingdom"})
            day += timedelta(days=rng.randint(10, 80))
    rows.append({"Order No": "", "SKU": "A-1", "Item": "Thing", "Qty": "x", "Order Date": "2024-02-30", "Unit Price": "n/a", "Account": "ACC1", "Country": "UK"})
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_suggest_mapping_handles_uci_and_alias_headers():
    uci = suggest_mapping(["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"])
    assert uci["customer_id"] == "Customer ID" and uci["invoice"] == "Invoice"
    other = suggest_mapping(list(MAPPING.values()))
    assert other == MAPPING


def test_check_mapping_reports_missing_unknown_and_duplicate_headers():
    problems = check_mapping({"invoice": "A", "invoice_date": "A", "quantity": "Q"}, ["A", "Q"])
    assert "Choose a column for price" in problems
    assert "Choose a column for customer id" in problems
    assert any("used more than once" in p for p in problems)
    assert check_mapping({**MAPPING, "price": "Missing"}, list(MAPPING.values())) == ["Column 'Missing' is not in the file"]


def test_validate_rejects_unparseable_rows_and_lists_them(tmp_path):
    report = validate(synthetic_csv(tmp_path / "f.csv"), MAPPING)
    assert report["rejected_rows"] == 1
    assert {e["problem"] for e in report["errors"]} >= {"Invoice number is empty", "Date could not be read", "Quantity is not a number", "Price is not a number"}
    assert report["can_score"] and report["customers"] == 60


def test_validate_blocks_tiny_files(tmp_path):
    path = synthetic_csv(tmp_path / "f.csv", customers=5)
    report = validate(path, MAPPING)
    assert not report["can_score"]
    assert any("at least 30" in b for b in report["blocking"])


def test_missing_optional_columns_are_reported_not_invented(tmp_path):
    path = synthetic_csv(tmp_path / "f.csv")
    report = validate(path, {**MAPPING, "country": None, "description": None})
    assert any("No country column" in w for w in report["warnings"])
    assert any("No description column" in w for w in report["warnings"])


def test_ambiguous_dates_are_flagged():
    values = pd.Series(["01/02/2024", "03/04/2024"])
    parsed, note = parse_dates(values, "auto")
    assert parsed.iloc[0] == pd.Timestamp("2024-02-01") and "day-first" in note
    assert parse_dates(values, "monthfirst")[0].iloc[0] == pd.Timestamp("2024-01-02")


def test_inspect_and_bad_extension(tmp_path):
    result = inspect(synthetic_csv(tmp_path / "f.csv"))
    assert result["suggested_mapping"] == MAPPING and not result["problems"]
    bad = tmp_path / "f.json"
    bad.write_text("{}")
    with pytest.raises(IngestError):
        inspect(bad)


def test_score_writes_serving_files(tmp_path):
    out = tmp_path / "serving"
    stages = []
    summary = score(synthetic_csv(tmp_path / "f.csv"), MAPPING, out, progress=lambda s, p: stages.append(s))
    assert stages[0] == "reading" and stages[-1] == "done"
    assert summary["accounts"] == 60 and summary["frozen_test"] is None
    accounts = json.loads((out / "accounts.json").read_text())
    assert {"p_lapse", "segment", "value_low_90", "value_high_90"} <= set(accounts[0])
    for name in ("timeline", "cohorts", "segments", "summary", "validation"):
        assert (out / f"{name}.json").exists()


def test_conformal_interval_covers_nominal_share():
    rng = np.random.default_rng(0)
    pred = rng.gamma(2, 50, 4000)
    truth = pred * rng.lognormal(0, 0.5, 4000)
    q = residual_quantiles(truth[:2000], pred[:2000], alpha=0.2)
    low, high = interval(pred[2000:], q)
    assert abs(coverage(truth[2000:], low, high) - 0.8) < 0.03
    with pytest.raises(ValueError):
        residual_quantiles([1.0] * 5, [1.0] * 5)
