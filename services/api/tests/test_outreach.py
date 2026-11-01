import app.main as main
from app.genai.drafting import Facts, check_draft, generate

ACCOUNT = {"customer_id": "12345", "segment": "At risk", "risk_band": "high", "recency_days": 200, "mean_gap_days": 30.0,
           "frequency": 5, "top_products": ["Jumbo Bag Red Retrospot", "Pack Of 72 Cake Cases"]}
FACTS = Facts.from_account(ACCOUNT, "Check-in with a reason to reorder.")
GOOD = ("Hi [First name],\n\nIt has been a while since your last order and I wanted to check in. You often stock the Jumbo Bag Red Retrospot "
        "and our new season range has arrived. I would be glad to suggest a reorder based on what sold well for you, or talk about anything "
        "that did not work.\n\nBest wishes,\n[Your name]")


class FakeClient:
    def __init__(self, draft, critic=None):
        self.draft, self.critic, self.prompts = draft, critic or {"verdict": "pass", "issues": []}, []

    def chat(self, system, user, schema, seed=42):
        self.prompts.append(user)
        return self.draft if "subject" in schema["properties"] else self.critic


def test_good_draft_passes_all_checks():
    assert check_draft("Checking in", GOOD, FACTS).passed


def test_invented_number_discount_pressure_and_pii_are_blocked():
    bad = GOOD + " Order 500 units today for 20% off - last chance! Call 07700 900123 or email a@b.com"
    failed = {c["name"] for c in check_draft("Hi", bad, FACTS).checks if not c["passed"]}
    assert {"Numbers match the model's facts", "No pressure or false urgency", "No discounts or offers", "No personal contact data"} <= failed


def test_numbers_from_facts_are_allowed():
    text = GOOD.replace("It has been a while", "It has been 200 days")
    assert check_draft("Hi", text, FACTS).passed


def test_prompt_contains_only_structured_facts_no_injection_text():
    client = FakeClient({"subject": "Checking in", "body": GOOD})
    result = generate(FACTS, "warm", client)
    assert result["source"] == "model" and result["passed"]
    assert "Ignore all previous instructions" not in client.prompts[0]
    assert all(line in client.prompts[0] for line in FACTS.prompt_lines())


def test_critic_revise_marks_draft_failed():
    client = FakeClient({"subject": "Hi", "body": GOOD}, {"verdict": "revise", "issues": ["too pushy"]})
    assert not generate(FACTS, "warm", client)["passed"]


def test_offline_model_falls_back_to_labelled_template():
    result = generate(FACTS, "brief", None)
    assert result["source"] == "template" and result["passed"]


def test_draft_approval_flow_with_consent_and_idempotency(client, serving, monkeypatch):
    import json
    accounts = json.loads((serving / "accounts.json").read_text())
    accounts[0].update({"segment": "At risk", "mean_gap_days": 30.0, "top_products": ["Jumbo Bag Red Retrospot"]})
    (serving / "accounts.json").write_text(json.dumps(accounts))
    monkeypatch.setattr(main, "ollama_status", lambda: {"available": False, "model": "x"})
    draft = client.post("/api/drafts", json={"customer_id": "12345", "tone": "warm", "reviewer": "KM"}).json()
    assert draft["source"] == "template" and draft["status"] == "pending_approval"
    url = f"/api/drafts/{draft['id']}/decision"
    no_consent = client.post(url, json={"decision": "approve", "reviewer": "KM"}, headers={"Idempotency-Key": "key-0001"})
    assert no_consent.status_code == 422 and "PECR" in no_consent.json()["detail"]
    sole = {"decision": "approve", "reviewer": "KM", "recipient_type": "sole_trader", "consent_basis": "legitimate_interest_b2b"}
    assert client.post(url, json=sole, headers={"Idempotency-Key": "key-0002"}).status_code == 422
    ok = {"decision": "approve", "reviewer": "KM", "recipient_type": "company", "consent_basis": "legitimate_interest_b2b"}
    first = client.post(url, json=ok, headers={"Idempotency-Key": "key-0003"})
    again = client.post(url, json=ok, headers={"Idempotency-Key": "key-0003"})
    assert first.json() == again.json() == {"id": draft["id"], "status": "approved"}
    assert client.post(url, json=ok, headers={"Idempotency-Key": "key-0004"}).status_code == 409
    assert "Jumbo Bag" in client.get("/api/drafts/export.csv").text
    actions = [e["action"] for e in client.get("/api/audit").json()]
    assert actions.count("draft_approved") == 1 and "draft_created" in actions


def test_missing_idempotency_key_rejected(client):
    assert client.post("/api/drafts/1/decision", json={"decision": "reject", "reviewer": "KM"}).status_code == 422


def test_human_labels_drive_critic_calibration(client, monkeypatch):
    monkeypatch.setattr(main, "ollama_status", lambda: {"available": False, "model": "x"})
    ids = [client.post("/api/drafts", json={"customer_id": "12345"}).json()["id"] for _ in range(3)]
    assert client.get("/api/critic/calibration").json()["labelled"] == 0
    for draft_id, label in zip(ids, ["pass", "pass", "revise"]):
        assert client.post(f"/api/drafts/{draft_id}/label", json={"label": label}).status_code == 200
    assert client.post("/api/drafts/999/label", json={"label": "pass"}).status_code == 404
    cal = client.get("/api/critic/calibration").json()
    # Template drafts carry no critic verdict, so nothing can be compared yet; labels are still stored.
    assert cal["labelled"] == 0 and sum(cal["confusion"].values()) == 0
    rows = {r["id"]: r["human_label"] for r in client.get("/api/drafts").json()}
    assert [rows[i] for i in ids] == ["pass", "pass", "revise"]
