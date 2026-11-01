"""Accounts, roles and the two-tenant isolation gate (R3)."""
import time

import pytest
from fastapi.testclient import TestClient

from app.security import sign_hs256_jwt

PASSWORD = "correct horse battery"



@pytest.fixture
def local(make_app):
    return make_app(RL_AUTH_MODE="local").app


def signup(app, email, workspace):
    client = TestClient(app)
    r = client.post("/api/auth/signup", json={"email": email, "name": email.split("@")[0], "password": PASSWORD, "workspace": workspace})
    assert r.status_code == 200, r.text
    client.headers["Authorization"] = f"Bearer {r.json()['token']}"
    return client


def test_everything_needs_sign_in(local):
    anon = TestClient(local)
    for path in ("/api/summary", "/api/accounts", "/api/drafts", "/api/audit", "/api/datasets", "/api/queue", "/api/org/members"):
        assert anon.get(path).status_code == 401, path
    assert anon.get("/api/health").status_code == 200


def test_signup_signin_signout_and_password_rules(local):
    anon = TestClient(local)
    weak = anon.post("/api/auth/signup", json={"email": "a@x.com", "name": "A", "password": "short"})
    assert weak.status_code == 422
    alice = signup(local, "alice@a.com", "Alpha Ltd")
    me = alice.get("/api/auth/me").json()
    assert me["role"] == "owner" and me["org"]["name"] == "Alpha Ltd"
    assert anon.post("/api/auth/signup", json={"email": "alice@a.com", "name": "A", "password": PASSWORD}).status_code == 409
    assert anon.post("/api/auth/signin", json={"email": "alice@a.com", "password": "wrong password!!"}).status_code == 401
    good = anon.post("/api/auth/signin", json={"email": "ALICE@a.com", "password": PASSWORD})
    assert good.status_code == 200 and "rl_session" in good.cookies
    assert anon.get("/api/auth/me").status_code == 200  # cookie session
    anon.post("/api/auth/signout")
    assert anon.get("/api/auth/me").status_code == 401


def test_new_workspace_is_empty_until_sample_or_upload(local):
    alice = signup(local, "alice@a.com", "Alpha")
    assert alice.get("/api/accounts").status_code == 409
    alice.post("/api/org/sample", json={"enabled": True})
    assert alice.get("/api/accounts").json()["total"] == 3


def test_two_tenant_isolation(local):
    alice, bob = signup(local, "alice@a.com", "Alpha"), signup(local, "bob@b.com", "Beta")
    for c in (alice, bob):
        c.post("/api/org/sample", json={"enabled": True})
    assert alice.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "Alpha's private note"}).status_code == 200
    draft = alice.post("/api/drafts", json={"customer_id": "12345"}).json()
    upload = alice.post("/api/datasets?filename=a.csv", content=b"Order No,Qty,Date,Price,Account\n1,2,2024-01-01,3,A")
    assert upload.status_code == 200
    # Bob sees none of it, by list or by id.
    assert bob.get("/api/accounts/12345").json()["reviews"] == []
    assert bob.get("/api/drafts").json() == []
    assert bob.get(f"/api/drafts/{draft['id']}").status_code == 404
    assert bob.post(f"/api/drafts/{draft['id']}/decision", json={"decision": "reject"}, headers={"Idempotency-Key": "k-12345678"}).status_code == 404
    assert bob.get("/api/datasets").json() == []
    assert bob.get(f"/api/datasets/{upload.json()['id']}").status_code == 404
    assert all("Alpha" not in str(e) for e in bob.get("/api/audit").json())
    assert bob.post("/api/auth/switch", json={"org_id": alice.get("/api/auth/me").json()["org"]["id"]}).status_code == 403
    # Asking for Alice's org by header gets Bob nothing.
    other = alice.get("/api/auth/me").json()["org"]["id"]
    assert bob.get("/api/drafts", headers={"X-Org-Id": other}).status_code == 401


def test_roles_and_invites(local):
    alice = signup(local, "alice@a.com", "Alpha")
    alice.post("/api/org/sample", json={"enabled": True})
    invite = alice.post("/api/org/invites", json={"email": "vic@a.com", "role": "viewer"}).json()
    token = invite["invite_url"].split("invite=")[1]
    vic = TestClient(local)
    r = vic.post("/api/auth/signup", json={"email": "vic@a.com", "name": "Vic", "password": PASSWORD, "invite": token})
    assert r.status_code == 200
    vic.headers["Authorization"] = f"Bearer {r.json()['token']}"
    assert vic.get("/api/auth/me").json()["role"] == "viewer"
    assert vic.get("/api/accounts").status_code == 200
    assert vic.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "nope nope"}).status_code == 403
    assert vic.post("/api/org/invites", json={"email": "x@a.com"}).status_code == 403
    # The invite cannot be reused.
    again = TestClient(local).post("/api/auth/signup", json={"email": "vic2@a.com", "name": "V", "password": PASSWORD, "invite": token})
    assert again.status_code == 400
    members = alice.get("/api/org/members").json()["members"]
    vic_id = next(m["id"] for m in members if m["email"] == "vic@a.com")
    assert alice.post(f"/api/org/members/{vic_id}/role", json={"role": "reviewer"}).status_code == 200
    assert vic.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "now allowed"}).status_code == 200
    me = alice.get("/api/auth/me").json()["user"]["id"]
    assert alice.post(f"/api/org/members/{me}/role", json={"role": "viewer"}).status_code == 409


def test_reviewer_name_comes_from_session_not_client(local):
    alice = signup(local, "alice@a.com", "Alpha")
    alice.post("/api/org/sample", json={"enabled": True})
    alice.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "check", "reviewer": "Someone Else"})
    assert alice.get("/api/accounts/12345").json()["reviews"][0]["reviewer"] == "alice"


def test_export_and_delete_workspace(local):
    alice, bob = signup(local, "alice@a.com", "Alpha"), signup(local, "bob@b.com", "Beta")
    for c in (alice, bob):
        c.post("/api/org/sample", json={"enabled": True})
        c.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "keep me"})
    exported = alice.get("/api/org/export").json()
    assert len(exported["reviews"]) == 1 and exported["org"]["name"] == "Alpha"
    assert alice.post("/api/org/delete", json={"confirm": "wrong"}).status_code == 422
    deleted = alice.post("/api/org/delete", json={"confirm": "Alpha"})
    assert deleted.status_code == 200 and deleted.json()["deleted_rows"]["reviews"] == 1
    assert alice.get("/api/auth/me").status_code == 401  # sessions went with the workspace
    assert len(bob.get("/api/accounts/12345").json()["reviews"]) == 1  # the other tenant is untouched


def test_supabase_tokens(make_app):
    app = make_app(RL_AUTH_MODE="supabase", SUPABASE_JWT_SECRET="test-secret-not-real").app
    client = TestClient(app)
    claims = {"sub": "uuid-1", "email": "s@x.com", "aud": "authenticated", "exp": int(time.time()) + 600}
    good = sign_hs256_jwt(claims, "test-secret-not-real")
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {good}"})
    assert me.status_code == 200 and me.json()["role"] == "owner"
    forged = sign_hs256_jwt(claims, "another-secret")
    expired = sign_hs256_jwt({**claims, "exp": int(time.time()) - 600}, "test-secret-not-real")
    for token in (forged, expired, "not.a.jwt"):
        assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    assert client.post("/api/auth/signin", json={"email": "s@x.com", "password": PASSWORD}).status_code == 404


def test_signin_is_rate_limited(local):
    anon = TestClient(local)
    codes = [anon.post("/api/auth/signin", json={"email": "nobody@x.com", "password": "whatever-123"}).status_code for _ in range(12)]
    assert codes[:10] == [401] * 10 and codes[-1] == 429


def test_weak_passwords_refused_and_failed_signins_audited(local):
    import app.main as main

    anon = TestClient(local)
    for bad in ("password1234", "aaaaaaaaaaaab", "aliceinwonderland"):
        r = anon.post("/api/auth/signup", json={"email": "alice@a.com", "name": "A", "password": bad})
        assert r.status_code == 422, bad
    signup(local, "alice@a.com", "Alpha")
    anon.post("/api/auth/signin", json={"email": "alice@a.com", "password": "not the password"})
    events = main.database.rows("SELECT * FROM audit_events WHERE org_id='security'")
    assert len(events) == 1 and events[0]["action"] == "signin_failed" and "alice" not in events[0]["subject"]


def test_per_account_signin_throttle(local, monkeypatch):
    import app.main as main

    signup(local, "alice@a.com", "Alpha")
    codes = []
    for i in range(11):
        # A different address each time: only the per-account limit can stop this.
        monkeypatch.setattr(main.env.limiter, "allow", _only_account_limit(main.env.limiter))
        codes.append(TestClient(local).post("/api/auth/signin", json={"email": "alice@a.com", "password": f"wrong-{i}-password"}).status_code)
    assert codes[-1] == 429


def _only_account_limit(limiter):
    original = type(limiter).allow

    def allow(key, limit, window):
        return True if key.startswith("auth:") or key.startswith("global:") else original(limiter, key, limit, window)

    return allow
