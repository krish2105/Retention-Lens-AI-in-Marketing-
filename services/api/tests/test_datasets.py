"""Upload wizard, scoring job, weekly queue with holdout, outcome tracking (R2)."""
import time
from datetime import date, timedelta

from fastapi.testclient import TestClient

CSV = b"Order No,Qty,Date,Price,Account\n1,2,2024-01-01,3,A\n"
MAPPING = {"invoice": "Order No", "quantity": "Qty", "invoice_date": "Date", "price": "Price", "customer_id": "Account"}


def wait_ready(client, dataset_id, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        ds = client.get(f"/api/datasets/{dataset_id}").json()
        if ds["status"] in ("ready", "failed"):
            return ds
        time.sleep(0.1)
    raise AssertionError("scoring did not finish")


def test_upload_map_validate_score_activate(client):
    up = client.post("/api/datasets?filename=invoices.csv", content=CSV)
    assert up.status_code == 200 and up.json()["status"] == "uploaded"
    assert up.json()["inspect"]["suggested_mapping"]["customer_id"] == "Account"
    again = client.post("/api/datasets?filename=copy.csv", content=CSV)
    assert again.json()["duplicate"] and again.json()["id"] == up.json()["id"]  # idempotent import
    dataset_id = up.json()["id"]
    assert client.post(f"/api/datasets/{dataset_id}/score").status_code == 409  # must validate first
    checked = client.post(f"/api/datasets/{dataset_id}/validate", json={"mapping": MAPPING}).json()
    assert checked["status"] == "validated"
    assert client.post(f"/api/datasets/{dataset_id}/score").json()["status"] in ("queued", "scoring", "ready")
    ds = wait_ready(client, dataset_id)
    assert ds["status"] == "ready" and ds["active"] and ds["summary"]["drift"]["psi"] is None
    accounts = client.get("/api/accounts").json()
    assert accounts["total"] == 2 and accounts["items"][0]["customer_id"] == "U1"
    assert client.get("/api/galaxy").status_code == 503  # reference-only view, said plainly
    assert "validation" in client.get("/api/data").json()


def test_rejects_wrong_type_empty_and_blocked_files(client):
    assert client.post("/api/datasets?filename=x.pdf", content=b"x").status_code == 415
    assert client.post("/api/datasets?filename=x.csv", content=b"").status_code == 422
    tiny = client.post("/api/datasets?filename=t.csv", content=b"Order No,Qty,Date,Price,Account\nTINY\n").json()
    assert client.post(f"/api/datasets/{tiny['id']}/validate", json={"mapping": MAPPING}).json()["status"] == "needs_fixes"
    assert client.post(f"/api/datasets/{tiny['id']}/score").status_code == 409


def test_plan_limit_blocks_scoring(client):
    big = client.post("/api/datasets?filename=b.csv", content=b"Order No,Qty,Date,Price,Account\nBIG\n").json()
    client.post(f"/api/datasets/{big['id']}/validate", json={"mapping": MAPPING})
    r = client.post(f"/api/datasets/{big['id']}/score")
    assert r.status_code == 402 and "Pilot plan" in r.json()["detail"]


def test_crashing_job_is_retried_then_marked_failed(client):
    bad = client.post("/api/datasets?filename=c.csv", content=b"Order No,Qty,Date,Price,Account\nCRASH\n").json()
    client.post(f"/api/datasets/{bad['id']}/validate", json={"mapping": MAPPING})
    client.post(f"/api/datasets/{bad['id']}/score")
    ds = wait_ready(client, bad["id"])
    assert ds["status"] == "failed" and ds["attempts"] == 2 and "exit 3" in ds["error"]


def test_delete_dataset_falls_back_to_sample(client):
    up = client.post("/api/datasets?filename=i.csv", content=CSV).json()
    client.post(f"/api/datasets/{up['id']}/validate", json={"mapping": MAPPING})
    client.post(f"/api/datasets/{up['id']}/score")
    wait_ready(client, up["id"])
    assert client.post(f"/api/datasets/{up['id']}/delete").status_code == 200
    assert client.get("/api/accounts").json()["total"] == 3  # back to the reference sample


def test_weekly_queue_holds_out_a_random_share(client):
    q = client.get("/api/queue?week=2026-11-02").json()
    assert q["week"] == "2026-11-02"
    shown = {i["customer_id"] for i in q["items"]}
    assert shown <= {"12345", "33333"} and q["holdout"] + len(shown) == 2
    again = client.get("/api/queue?week=2026-11-04").json()  # same week: same assignment
    assert {i["customer_id"] for i in again["items"]} == shown


def test_contact_review_marks_outcome_and_reorders_are_detected(client):
    week = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    q = client.get(f"/api/queue?week={week}").json()
    target = q["items"][0]["customer_id"] if q["items"] else None
    if target:
        client.post(f"/api/accounts/{target}/reviews", json={"decision": "contact", "note": "call them"})
        q = client.get(f"/api/queue?week={week}").json()
        assert q["items"][0]["status"] == "reviewed" and q["items"][0]["contacted"]
    assert client.post("/api/outcomes/reorder", json={"customer_id": "nobody", "week": week, "reordered_on": "2026-11-10"}).status_code == 404
    outcomes = client.get("/api/outcomes").json()
    assert outcomes["pending"] >= 1 and outcomes["arms"]["contact"]["accounts"] == 0  # nothing observed for 28 days yet


def test_rate_difference_ci():
    from app.loop import rate_difference

    r = rate_difference(30, 100, 20, 100)
    assert r["difference"] == 0.1 and r["ci95"][0] < 0.1 < r["ci95"][1]
    assert rate_difference(1, 0, 1, 1)["difference"] is None


def test_funnel_times_upload_to_first_decision(client):
    assert client.get("/api/funnel").json()["minutes_upload_to_first_decision"] is None
    up = client.post("/api/datasets?filename=f.csv", content=CSV).json()
    client.post(f"/api/datasets/{up['id']}/validate", json={"mapping": MAPPING})
    client.post(f"/api/datasets/{up['id']}/score")
    wait_ready(client, up["id"])
    client.post("/api/accounts/U1/reviews", json={"decision": "contact", "note": "first decision"})
    f = client.get("/api/funnel").json()
    assert f["minutes_upload_to_scored"] is not None and f["minutes_upload_to_first_decision"] < 1 and f["within_target"] is True
