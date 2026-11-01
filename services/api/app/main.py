"""RetentionLens API. Localhost decision-support service: no authentication, not for public exposure."""
from __future__ import annotations

from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import Database, now
from .settings import load_settings
from .store import NotBuilt, ServingStore

settings = load_settings()
store = ServingStore(settings.serving_dir)
database = Database(settings.state_db)

app = FastAPI(title="RetentionLens API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key"],
)

SORTABLE = {"value_at_risk_90", "p_lapse", "expected_value_90", "recency_days", "net_sales_total", "frequency"}


def _get(name: str):
    try:
        return store.get(name)
    except NotBuilt as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


def ollama_status() -> dict:
    try:
        response = httpx.get(f"{settings.ollama_url}/api/tags", timeout=1.5)
        models = [m["name"] for m in response.json().get("models", [])]
        return {"available": settings.ollama_model in models, "model": settings.ollama_model}
    except (httpx.HTTPError, ValueError):
        return {"available": False, "model": settings.ollama_model}


@app.get("/api/health")
def health():
    summary = store.get("summary") if store.ready() else None
    return {
        "ok": True,
        "serving_ready": summary is not None,
        "generated_at": summary and summary["generated_at"],
        "ollama": ollama_status(),
    }


@app.get("/api/summary")
def summary():
    return _get("summary")


@app.get("/api/accounts")
def accounts(
    search: str = "",
    band: Literal["all", "high", "watch", "healthy"] = "all",
    sort: str = "value_at_risk_90",
    order: Literal["asc", "desc"] = "desc",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    if sort not in SORTABLE:
        raise HTTPException(422, f"sort must be one of {sorted(SORTABLE)}")
    items = _get("accounts")
    term = search.strip().lower()
    if term:
        items = [a for a in items if term in a["customer_id"].lower() or term in (a["country"] or "").lower()]
    if band != "all":
        items = [a for a in items if a["risk_band"] == band]
    items = sorted(items, key=lambda a: (a.get(sort) is None, a.get(sort) or 0), reverse=(order == "desc"))
    return {"total": len(items), "items": items[offset : offset + limit]}


@app.get("/api/accounts/{customer_id}")
def account(customer_id: str):
    record = store.account(customer_id) if store.ready() else None
    if record is None:
        raise HTTPException(404, "Unknown account")
    return {
        "account": record,
        "timeline": _get("timeline").get(customer_id, []),
        "reviews": database.rows("SELECT * FROM reviews WHERE customer_id=? ORDER BY id DESC", (customer_id,)),
        "drafts": database.rows("SELECT id, status, source, subject, created_at FROM drafts WHERE customer_id=? ORDER BY id DESC", (customer_id,)),
    }


class Review(BaseModel):
    decision: Literal["contact", "keep_watching", "no_action"]
    note: str = Field(min_length=3, max_length=2000)
    reviewer: str = Field(min_length=1, max_length=100)


@app.post("/api/accounts/{customer_id}/reviews")
def add_review(customer_id: str, review: Review):
    if store.account(customer_id) is None:
        raise HTTPException(404, "Unknown account")
    with database.connect() as db:
        db.execute(
            "INSERT INTO reviews (customer_id, decision, note, reviewer, created_at) VALUES (?,?,?,?,?)",
            (customer_id, review.decision, review.note, review.reviewer, now()),
        )
        database.audit(db, review.reviewer, "review", customer_id, review.model_dump())
    return {"ok": True}


@app.get("/api/cohorts")
def cohorts():
    return _get("cohorts")


@app.get("/api/model-eval")
def model_eval():
    return _get("model_eval")


@app.get("/api/data")
def data():
    return {"profile": _get("data_profile"), "sources": _get("sources")}


@app.get("/api/audit")
def audit(limit: int = Query(100, ge=1, le=500)):
    return database.rows("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,))


for _name, _path in {"segments": "/api/segments", "galaxy": "/api/galaxy", "lookalikes": "/api/lookalikes",
                     "signals": "/api/signals", "product_lab": "/api/product-lab"}.items():
    app.add_api_route(_path, (lambda n: lambda: _get(n))(_name), methods=["GET"], name=_name)


# ---- Outreach studio (P6): grounded drafts, human approval, no send path ----
import csv as _csv
import io as _io
import json as _json

from fastapi import Header
from fastapi.responses import PlainTextResponse

from .genai.drafting import TONES, Facts, OllamaClient, check_draft, generate

CONSENT_RULES = {
    # UK PECR: corporate subscribers may receive B2B marketing under legitimate interests;
    # sole traders and some partnerships count as individuals and need consent or the soft opt-in.
    "company": {"legitimate_interest_b2b", "explicit_consent"},
    "sole_trader": {"explicit_consent", "soft_opt_in_existing_customer"},
}


class DraftRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=20)
    tone: Literal["warm", "brief", "seasonal"] = "warm"
    reviewer: str = Field(min_length=1, max_length=100)


class Decision(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer: str = Field(min_length=1, max_length=100)
    recipient_type: Literal["company", "sole_trader", "unknown"] = "unknown"
    consent_basis: Literal["legitimate_interest_b2b", "explicit_consent", "soft_opt_in_existing_customer", "none"] = "none"
    edited_body: str | None = Field(default=None, max_length=4000)
    acknowledge_review: bool = False
    note: str = Field(default="", max_length=1000)


def _play_for(segment: str | None) -> str:
    try:
        rows = store.get("segments")["segments"]
        return next((r["play"] for r in rows if r["segment"] == segment), "Check in and offer help with the next order.")
    except NotBuilt:
        return "Check in and offer help with the next order."


def _draft_row(draft_id: int) -> dict:
    rows = database.rows("SELECT * FROM drafts WHERE id=?", (draft_id,))
    if not rows:
        raise HTTPException(404, "Unknown draft")
    row = rows[0]
    row["checks"] = _json.loads(row["checks"])
    row["context"] = _json.loads(row["context"])
    return row


@app.post("/api/drafts")
def create_draft(request: DraftRequest):
    account_row = store.account(request.customer_id) if store.ready() else None
    if account_row is None:
        raise HTTPException(404, "Unknown account")
    facts = Facts.from_account(account_row, _play_for(account_row.get("segment")))
    client = OllamaClient(settings.ollama_url, settings.ollama_model) if ollama_status()["available"] else None
    result = generate(facts, request.tone, client)
    status = "pending_approval" if result["passed"] else "needs_revision"
    context = {"facts": facts.prompt_lines(), "tone": TONES[request.tone], "prompt": result["prompt"], "error": result["error"], "seconds": result["seconds"]}
    with database.connect() as db:
        cursor = db.execute(
            "INSERT INTO drafts (customer_id, status, source, model, subject, body, checks, context, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (request.customer_id, status, result["source"], settings.ollama_model if result["source"] == "model" else None,
             result["subject"], result["body"], _json.dumps(result["checks"]), _json.dumps(context), now()),
        )
        draft_id = cursor.lastrowid
        database.audit(db, request.reviewer, "draft_created", f"draft:{draft_id}",
                       {"customer_id": request.customer_id, "source": result["source"], "status": status, "passed": result["passed"]})
    return _draft_row(draft_id)


@app.get("/api/drafts")
def list_drafts(status: str | None = None, limit: int = Query(100, ge=1, le=500)):
    sql, params = "SELECT id, customer_id, status, source, subject, created_at, decided_by FROM drafts", ()
    if status:
        sql, params = sql + " WHERE status=?", (status,)
    return database.rows(sql + " ORDER BY id DESC LIMIT ?", (*params, limit))


@app.get("/api/drafts/export.csv", response_class=PlainTextResponse)
def export_drafts():
    rows = database.rows("SELECT id, customer_id, subject, body, recipient_type, consent_basis, decided_by, decided_at FROM drafts WHERE status='approved' ORDER BY id")
    buffer = _io.StringIO()
    writer = _csv.DictWriter(buffer, fieldnames=["id", "customer_id", "subject", "body", "recipient_type", "consent_basis", "decided_by", "decided_at"])
    writer.writeheader()
    writer.writerows(rows)
    return PlainTextResponse(buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=approved_drafts.csv"})


@app.get("/api/drafts/{draft_id}")
def get_draft(draft_id: int):
    return _draft_row(draft_id)


@app.post("/api/drafts/{draft_id}/decision")
def decide(draft_id: int, decision: Decision, idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=100)):
    previous = database.rows("SELECT response FROM idempotency WHERE key=?", (idempotency_key,))
    if previous:
        return _json.loads(previous[0]["response"])
    draft = _draft_row(draft_id)
    if draft["status"] in ("approved", "rejected"):
        raise HTTPException(409, f"Draft already {draft['status']}")
    body = decision.edited_body.strip() if decision.edited_body else draft["body"]
    if decision.decision == "approve":
        account_row = store.account(draft["customer_id"])
        facts = Facts.from_account(account_row, _play_for(account_row.get("segment")))
        checks = check_draft(draft["subject"], body, facts)
        if not checks.passed:
            raise HTTPException(422, "Draft fails checks: " + "; ".join(c["name"] for c in checks.checks if not c["passed"]))
        critic = next((c for c in draft["checks"] if c["name"].startswith("Second-pass")), None)
        if critic and not critic["passed"] and not decision.acknowledge_review and decision.edited_body is None:
            raise HTTPException(422, "The second-pass review raised issues: edit the draft or confirm you have read them")
        if decision.consent_basis not in CONSENT_RULES.get(decision.recipient_type, set()):
            raise HTTPException(422, "No valid consent basis for this recipient type (UK PECR): record the recipient type and basis first")
    status = "approved" if decision.decision == "approve" else "rejected"
    with database.connect() as db:
        db.execute(
            "UPDATE drafts SET status=?, body=?, recipient_type=?, consent_basis=?, decided_by=?, decided_at=? WHERE id=?",
            (status, body, decision.recipient_type, decision.consent_basis, decision.reviewer, now(), draft_id),
        )
        database.audit(db, decision.reviewer, f"draft_{status}", f"draft:{draft_id}",
                       {"edited": decision.edited_body is not None, "recipient_type": decision.recipient_type, "consent_basis": decision.consent_basis, "note": decision.note})
        response = {"id": draft_id, "status": status}
        db.execute("INSERT INTO idempotency (key, response, created_at) VALUES (?,?,?)", (idempotency_key, _json.dumps(response), now()))
    return response
