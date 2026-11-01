import importlib
import json

import pytest
from fastapi.testclient import TestClient

ACCOUNTS = [
    {"customer_id": "12345", "country": "United Kingdom", "risk_band": "high", "p_lapse": 0.9, "value_at_risk_90": 500.0,
     "expected_value_90": 20.0, "recency_days": 200, "net_sales_total": 4000.0, "frequency": 5, "reasons": ["No order for 200 days; usual gap 30 days"]},
    {"customer_id": "22222", "country": "France", "risk_band": "healthy", "p_lapse": 0.2, "value_at_risk_90": 50.0,
     "expected_value_90": 300.0, "recency_days": 5, "net_sales_total": 900.0, "frequency": 9, "reasons": ["Ordering on its usual cadence"]},
    {"customer_id": "33333", "country": "United Kingdom", "risk_band": "watch", "p_lapse": 0.6, "value_at_risk_90": 120.0,
     "expected_value_90": 80.0, "recency_days": 60, "net_sales_total": 1500.0, "frequency": 2, "reasons": []},
]


@pytest.fixture
def serving(tmp_path):
    d = tmp_path / "serving"
    d.mkdir()
    files = {
        "summary.json": {"generated_at": "2026-11-01T00:00:00+00:00", "accounts": 3},
        "accounts.json": ACCOUNTS,
        "timeline.json": {"12345": [["2011-01", 100.0, 0.0]]},
        "cohorts.json": [{"cohort": "2010-01", "size": 2, "retention": [1.0, 0.5]}],
        "model_eval.json": {"run_id": "r"},
        "data_profile.json": {"rows": 1},
        "sources.json": [{"name": "online_retail_ii"}],
    }
    for name, payload in files.items():
        (d / name).write_text(json.dumps(payload))
    return d


@pytest.fixture
def client(serving, tmp_path, monkeypatch):
    monkeypatch.setenv("RL_SERVING_DIR", str(serving))
    monkeypatch.setenv("RL_STATE_DB", str(tmp_path / "state.sqlite3"))
    monkeypatch.setenv("OLLAMA_URL", "http://127.0.0.1:9")
    import app.main as main

    importlib.reload(main)
    return TestClient(main.app)
