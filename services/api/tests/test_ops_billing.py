"""Waitlist, billing in test mode, metrics, status and headers (R1, R4, R6)."""
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient

WAIT = {"email": "Owner@Shop.co.uk", "company": "Shop Ltd", "role": "Owner", "accounts_band": "200_1000", "consent": True}


def test_waitlist_requires_consent_and_hides_duplicates(make_app):
    client = TestClient(make_app(RL_ADMIN_TOKEN="admin-test-token").app)
    assert client.post("/api/waitlist", json={**WAIT, "consent": False}).status_code == 422
    assert client.post("/api/waitlist", json={**WAIT, "email": "not-an-email"}).status_code == 422
    assert client.post("/api/waitlist", json=WAIT).status_code == 200
    assert client.post("/api/waitlist", json=WAIT).status_code == 200  # duplicate looks the same
    assert client.get("/api/admin/waitlist").status_code == 401
    stats = client.get("/api/admin/waitlist", headers={"X-Admin-Token": "admin-test-token"}).json()
    assert stats["signups"] == 1 and stats["rows"][0]["email"] == "owner@shop.co.uk"


def test_billing_unconfigured_and_live_keys_refused(make_app):
    client = TestClient(make_app().app)
    assert client.get("/api/billing").json()["billing_configured"] is False
    assert client.post("/api/billing/checkout", json={"plan": "starter"}).status_code == 503
    live = TestClient(make_app(STRIPE_SECRET_KEY="sk_live_x", STRIPE_PRICE_STARTER="price_x").app)
    r = live.post("/api/billing/checkout", json={"plan": "starter"})
    assert r.status_code == 503 and "test-mode" in r.json()["detail"]
    assert client.get("/api/plans").json()["plans"]["growth"]["price_gbp_month"] == 149


def _signed(payload: dict, secret: str) -> tuple[bytes, str]:
    body = json.dumps(payload).encode()
    t = int(time.time())
    sig = hmac.new(secret.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return body, f"t={t},v1={sig}"


def test_stripe_webhook_signature_plan_change_and_replay(make_app):
    client = TestClient(make_app(STRIPE_WEBHOOK_SECRET="whsec_test").app)
    event = {"id": "evt_1", "type": "checkout.session.completed", "livemode": False,
             "data": {"object": {"metadata": {"org_id": "local", "plan": "growth"}, "customer": "cus_1"}}}
    body, header = _signed(event, "whsec_test")
    assert client.post("/api/billing/webhook", content=body, headers={"Stripe-Signature": "t=1,v1=bad"}).status_code == 400
    assert client.post("/api/billing/webhook", content=body, headers={"Stripe-Signature": header}).json() == {"ok": True}
    assert client.get("/api/billing").json()["plan"] == "growth"
    assert client.post("/api/billing/webhook", content=body, headers={"Stripe-Signature": header}).json()["duplicate"]
    live, live_header = _signed({**event, "id": "evt_2", "livemode": True}, "whsec_test")
    assert client.post("/api/billing/webhook", content=live, headers={"Stripe-Signature": live_header}).status_code == 400


def test_metrics_status_and_security_headers(client):
    r = client.get("/api/summary")
    assert r.headers["X-Content-Type-Options"] == "nosniff" and r.headers["X-Request-ID"]
    metrics = client.get("/api/metrics").json()
    assert metrics["routes"]["GET /api/summary"]["requests"] == 1 and metrics["slo"]["read_p95_ms"] == 500
    status = client.get("/api/status").json()
    assert status["status"] == "operational" and status["components"]["local_ai"]["ok"] is False


def test_csv_exports_neutralise_formulas(client):
    client.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "=HYPERLINK(1)", "reviewer": "R"})
    text = client.get("/api/reviews/export.csv").text
    assert "'=HYPERLINK(1)" in text
