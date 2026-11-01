"""Stand-in for `python -m retentionlens.ingest` in API tests: same arguments, same JSON-lines output."""
import json
import sys
from pathlib import Path

command, path = sys.argv[1], Path(sys.argv[2])
args = dict(zip(sys.argv[3::2], sys.argv[4::2]))
text = path.read_text()
if "CRASH" in text and command == "score":
    sys.exit(3)
headers = text.splitlines()[0].split(",")
if command == "inspect":
    mapping = {"invoice": "Order No", "stock_code": None, "description": None, "quantity": "Qty", "invoice_date": "Date",
               "price": "Price", "customer_id": "Account", "country": None}
    print(json.dumps({"result": {"rows": 3, "headers": headers, "suggested_mapping": mapping, "problems": [], "sample": []}}))
elif command == "validate":
    customers = 5000 if "BIG" in text else 40
    tiny = "TINY" in text
    print(json.dumps({"result": {"rows": 3, "valid_rows": 3, "rejected_rows": 0, "errors": [], "issues": {}, "customers": customers,
                                 "blocking": ["Only 2 customers"] if tiny else [], "warnings": [], "can_score": not tiny}}))
else:
    out = Path(args["--out"])
    out.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"stage": "fitting", "pct": 50}), flush=True)
    accounts = [
        {"customer_id": "U1", "country": "Not provided", "risk_band": "high", "p_lapse": 0.9, "value_at_risk_90": 900.0, "expected_value_90": 10.0,
         "recency_days": 3, "net_sales_total": 5000.0, "frequency": 4, "reasons": ["x"], "segment": "At risk"},
        {"customer_id": "U2", "country": "Not provided", "risk_band": "healthy", "p_lapse": 0.1, "value_at_risk_90": 10.0, "expected_value_90": 100.0,
         "recency_days": 200, "net_sales_total": 100.0, "frequency": 1, "reasons": ["y"], "segment": "New"},
    ]
    (out / "accounts.json").write_text(json.dumps(accounts))
    (out / "timeline.json").write_text("{}")
    (out / "cohorts.json").write_text("[]")
    (out / "validation.json").write_text(json.dumps({"rows": 3}))
    summary = {"generated_at": "2026-11-01T00:00:00+00:00", "scoring_cutoff": "2026-11-02", "accounts": 2, "frozen_test": None}
    (out / "summary.json").write_text(json.dumps(summary))
    print(json.dumps({"result": summary}))
