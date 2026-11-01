def test_health_reports_serving_and_model(client):
    body = client.get("/api/health").json()
    assert body["serving_ready"] is True and body["ollama"]["available"] is False


def test_accounts_filter_sort_page(client):
    body = client.get("/api/accounts", params={"band": "all", "sort": "p_lapse", "order": "desc", "limit": 2}).json()
    assert body["total"] == 3 and [a["customer_id"] for a in body["items"]] == ["12345", "33333"]
    uk = client.get("/api/accounts", params={"search": "united"}).json()
    assert uk["total"] == 2
    assert client.get("/api/accounts", params={"band": "watch"}).json()["items"][0]["customer_id"] == "33333"


def test_bad_sort_rejected(client):
    assert client.get("/api/accounts", params={"sort": "drop table"}).status_code == 422


def test_account_detail_and_review_audit(client):
    assert client.get("/api/accounts/99999").status_code == 404
    r = client.post("/api/accounts/12345/reviews", json={"decision": "contact", "note": "Call this week", "reviewer": "KM"})
    assert r.status_code == 200
    detail = client.get("/api/accounts/12345").json()
    assert detail["timeline"] == [["2011-01", 100.0, 0.0]]
    assert detail["reviews"][0]["decision"] == "contact"
    assert client.get("/api/audit").json()[0]["action"] == "review"


def test_review_validation(client):
    bad = client.post("/api/accounts/12345/reviews", json={"decision": "delete", "note": "x", "reviewer": ""})
    assert bad.status_code == 422


def test_not_built_artefact_returns_503(client):
    r = client.get("/api/galaxy")
    assert r.status_code == 503 and "cli serve" in r.json()["detail"]
