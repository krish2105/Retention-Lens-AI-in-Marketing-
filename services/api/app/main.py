"""RetentionLens API.

RL_AUTH_MODE=off (default) is a single local workspace with no sign-in: run it on your own
machine only. RL_AUTH_MODE=local or supabase adds accounts, workspaces and roles; every query
is scoped to the caller's workspace (org_id).
"""
from __future__ import annotations

import csv
import io
import json
import re
from typing import Literal

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, field_validator

from . import billing, datasets, loop, ops, tenancy
from .db import now
from .env import Env
from .genai.drafting import TONES, Facts, OllamaClient, check_draft, generate
from .settings import load_settings
from .store import NotBuilt, ServingStore
from .tenancy import Ctx

VERSION = "0.4.0"
settings = load_settings()
env = Env(settings)
database = env.db
store = env.reference  # kept for evals that import it

app = FastAPI(title="RetentionLens API", version=VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key", "Authorization", "X-Org-Id", "X-Request-ID", "X-RL-Client"],
)
metrics = ops.Metrics()
ops.install(app, env, metrics)

ctx, require, provision_user, create_org = tenancy.make_context(env)


def on_dataset_ready(org_id: str, dataset_id: str) -> None:
    """A new scored upload becomes the active dataset and closes the loop on earlier outreach."""
    with database.connect() as db:
        db.execute("UPDATE orgs SET active_dataset=? WHERE id=?", (dataset_id, org_id))
        database.audit(db, "system", "dataset_ready", f"dataset:{dataset_id}", {}, org_id)
    scored = env.dataset_store(org_id, dataset_id)
    loop.detect_reorders(env, org_id, scored.get("accounts"), scored.get("summary")["scoring_cutoff"])


runner = datasets.SubprocessRunner(settings.ml_command)
worker = datasets.Worker(env, runner, on_dataset_ready)

app.include_router(tenancy.router(env, ctx, require, provision_user, create_org))
app.include_router(datasets.router(env, ctx, require, runner, worker))
app.include_router(loop.router(env, ctx, require))
app.include_router(billing.router(env, ctx, require))
app.include_router(ops.router(env, metrics, lambda: worker.thread.is_alive()))

SORTABLE = {"value_at_risk_90", "p_lapse", "expected_value_90", "recency_days", "net_sales_total", "frequency"}


def data_for(context: Ctx) -> ServingStore:
    return env.store_for(context.org_id)


def _get(source: ServingStore, name: str):
    try:
        return source.get(name)
    except NotBuilt as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


def actor(context: Ctx, claimed: str | None) -> str:
    """With sign-in, the signed-in user is the actor; the name a client sends is ignored."""
    return claimed if settings.auth_mode == "off" and claimed else context.name


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
        "version": VERSION,
        "auth_mode": settings.auth_mode,
        "serving_ready": summary is not None,
        "generated_at": summary and summary["generated_at"],
        "ollama": ollama_status(),
    }


@app.get("/api/summary")
def summary(context: Ctx = Depends(ctx)):
    return _get(data_for(context), "summary")


@app.get("/api/accounts")
def accounts(
    search: str = "",
    band: Literal["all", "high", "watch", "healthy"] = "all",
    sort: str = "value_at_risk_90",
    order: Literal["asc", "desc"] = "desc",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    context: Ctx = Depends(ctx),
):
    if sort not in SORTABLE:
        raise HTTPException(422, f"sort must be one of {sorted(SORTABLE)}")
    items = _get(data_for(context), "accounts")
    term = search.strip().lower()
    if term:
        items = [a for a in items if term in a["customer_id"].lower() or term in (a["country"] or "").lower()]
    if band != "all":
        items = [a for a in items if a["risk_band"] == band]
    items = sorted(items, key=lambda a: (a.get(sort) is None, a.get(sort) or 0), reverse=(order == "desc"))
    return {"total": len(items), "items": items[offset : offset + limit]}


@app.get("/api/accounts/{customer_id}")
def account(customer_id: str, context: Ctx = Depends(ctx)):
    source = data_for(context)
    record = source.account(customer_id) if source.ready() else None
    if record is None:
        raise HTTPException(404, "Unknown account")
    return {
        "account": record,
        "timeline": _get(source, "timeline").get(customer_id, []),
        "reviews": database.rows("SELECT * FROM reviews WHERE org_id=? AND customer_id=? ORDER BY id DESC", (context.org_id, customer_id)),
        "drafts": database.rows("SELECT id, status, source, subject, created_at FROM drafts WHERE org_id=? AND customer_id=? ORDER BY id DESC", (context.org_id, customer_id)),
    }


class Review(BaseModel):
    decision: Literal["contact", "keep_watching", "no_action"]
    note: str = Field(min_length=3, max_length=2000)
    reviewer: str | None = Field(default=None, max_length=100)


@app.post("/api/accounts/{customer_id}/reviews")
def add_review(customer_id: str, review: Review, context: Ctx = Depends(require("reviewer"))):
    if data_for(context).account(customer_id) is None:
        raise HTTPException(404, "Unknown account")
    who = actor(context, review.reviewer)
    with database.connect() as db:
        db.execute(
            "INSERT INTO reviews (org_id, customer_id, decision, note, reviewer, created_at) VALUES (?,?,?,?,?,?)",
            (context.org_id, customer_id, review.decision, review.note, who, now()),
        )
        database.audit(db, who, "review", customer_id, {**review.model_dump(), "reviewer": who}, context.org_id)
        if review.decision == "contact":
            loop.mark_contacted(env, db, context.org_id, customer_id)
    return {"ok": True}


@app.get("/api/cohorts")
def cohorts(context: Ctx = Depends(ctx)):
    return _get(data_for(context), "cohorts")


@app.get("/api/model-eval")
def model_eval(context: Ctx = Depends(ctx)):
    return _get(data_for(context), "model_eval")


@app.get("/api/data")
def data(context: Ctx = Depends(ctx)):
    source = data_for(context)
    if source is store:
        return {"profile": _get(source, "data_profile"), "sources": _get(source, "sources")}
    return {"validation": _get(source, "validation"), "summary": _get(source, "summary")}


@app.get("/api/audit")
def audit(limit: int = Query(100, ge=1, le=500), context: Ctx = Depends(ctx)):
    return database.rows("SELECT * FROM audit_events WHERE org_id=? ORDER BY id DESC LIMIT ?", (context.org_id, limit))


def _reference_view(name: str):
    def view(context: Ctx = Depends(ctx)):
        return _get(data_for(context), name)

    return view


for _name, _path in {"segments": "/api/segments", "galaxy": "/api/galaxy", "lookalikes": "/api/lookalikes",
                     "signals": "/api/signals", "product_lab": "/api/product-lab"}.items():
    app.add_api_route(_path, _reference_view(_name), methods=["GET"], name=_name)


# ---- Waitlist (R1): consent required, no pre-ticked boxes, duplicate sign-ups not revealed ----
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class WaitlistIn(BaseModel):
    email: str = Field(max_length=254)
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=80)
    accounts_band: Literal["under_200", "200_1000", "1000_5000", "over_5000"]
    consent: bool
    source: str = Field(default="landing", max_length=40)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL.match(value):
            raise ValueError("Enter a valid work email")
        return value


@app.post("/api/waitlist")
def join_waitlist(body: WaitlistIn, request: Request):
    if not body.consent:
        raise HTTPException(422, "Tick the box to agree to be contacted about the pilot")
    client = request.client.host if request.client else "unknown"
    if not env.limiter.allow(f"waitlist:{client}", 5, 60):
        raise HTTPException(429, "Too many sign-ups from this address; try again in a minute")
    with database.connect() as db:
        db.execute(
            "INSERT OR IGNORE INTO waitlist (email, company, role, accounts_band, consent_at, source, created_at) VALUES (?,?,?,?,?,?,?)",
            (body.email, body.company.strip(), body.role.strip(), body.accounts_band, now(), body.source, now()),
        )
    return {"ok": True, "message": "Thanks. We will email you about the pilot, and only about the pilot."}


def _admin(token: str | None) -> None:
    if not settings.admin_token or token != settings.admin_token:
        raise HTTPException(401, "Admin token required")


@app.get("/api/admin/waitlist")
def waitlist_admin(x_admin_token: str | None = Header(default=None)):
    _admin(x_admin_token)
    rows = database.rows("SELECT * FROM waitlist ORDER BY id")
    by_band = {}
    for row in rows:
        by_band[row["accounts_band"]] = by_band.get(row["accounts_band"], 0) + 1
    return {"signups": len(rows), "by_accounts_band": by_band, "rows": rows}


# ---- Outreach studio (P6): grounded drafts, human approval, no send path ----
CONSENT_RULES = {
    # UK PECR: corporate subscribers may receive B2B marketing under legitimate interests;
    # sole traders and some partnerships count as individuals and need consent or the soft opt-in.
    "company": {"legitimate_interest_b2b", "explicit_consent"},
    "sole_trader": {"explicit_consent", "soft_opt_in_existing_customer"},
}


class DraftRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=40)
    tone: Literal["warm", "brief", "seasonal"] = "warm"
    reviewer: str | None = Field(default=None, max_length=100)


class Decision(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer: str | None = Field(default=None, max_length=100)
    recipient_type: Literal["company", "sole_trader", "unknown"] = "unknown"
    consent_basis: Literal["legitimate_interest_b2b", "explicit_consent", "soft_opt_in_existing_customer", "none"] = "none"
    edited_body: str | None = Field(default=None, max_length=4000)
    acknowledge_review: bool = False
    note: str = Field(default="", max_length=1000)


class LabelIn(BaseModel):
    label: Literal["pass", "revise"]
    note: str = Field(default="", max_length=1000)


def _play_for(source: ServingStore, segment: str | None) -> str:
    try:
        rows = source.get("segments")["segments"]
        return next((r["play"] for r in rows if r["segment"] == segment), "Check in and offer help with the next order.")
    except NotBuilt:
        return "Check in and offer help with the next order."


def _draft_row(context: Ctx, draft_id: int) -> dict:
    rows = database.rows("SELECT * FROM drafts WHERE id=? AND org_id=?", (draft_id, context.org_id))
    if not rows:
        raise HTTPException(404, "Unknown draft")
    row = rows[0]
    row["checks"] = json.loads(row["checks"])
    row["context"] = json.loads(row["context"])
    return row


@app.post("/api/drafts")
def create_draft(request: DraftRequest, context: Ctx = Depends(require("reviewer"))):
    # Each draft is two model calls; cap them per workspace (OWASP LLM10, unbounded consumption).
    if not env.limiter.allow(f"drafts:{context.org_id}", 30, 60):
        raise HTTPException(429, "Draft limit reached: 30 per minute per workspace")
    source = data_for(context)
    account_row = source.account(request.customer_id) if source.ready() else None
    if account_row is None:
        raise HTTPException(404, "Unknown account")
    facts = Facts.from_account(account_row, _play_for(source, account_row.get("segment")))
    client = OllamaClient(settings.ollama_url, settings.ollama_model) if ollama_status()["available"] else None
    result = generate(facts, request.tone, client)
    status = "pending_approval" if result["passed"] else "needs_revision"
    draft_context = {"facts": facts.prompt_lines(), "tone": TONES[request.tone], "prompt": result["prompt"], "error": result["error"], "seconds": result["seconds"]}
    who = actor(context, request.reviewer)
    with database.connect() as db:
        cursor = db.execute(
            "INSERT INTO drafts (org_id, customer_id, status, source, model, subject, body, checks, context, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (context.org_id, request.customer_id, status, result["source"], settings.ollama_model if result["source"] == "model" else None,
             result["subject"], result["body"], json.dumps(result["checks"]), json.dumps(draft_context), now()),
        )
        draft_id = cursor.lastrowid
        database.audit(db, who, "draft_created", f"draft:{draft_id}",
                       {"customer_id": request.customer_id, "source": result["source"], "status": status, "passed": result["passed"]}, context.org_id)
    return _draft_row(context, draft_id)


@app.get("/api/drafts")
def list_drafts(status: str | None = None, limit: int = Query(100, ge=1, le=500), context: Ctx = Depends(ctx)):
    sql = ("SELECT d.id, d.customer_id, d.status, d.source, d.subject, d.created_at, d.decided_by, l.label AS human_label FROM drafts d "
           "LEFT JOIN critic_labels l ON l.org_id=d.org_id AND l.draft_id=d.id WHERE d.org_id=?")
    params = (context.org_id,)
    if status:
        sql, params = sql + " AND d.status=?", (*params, status)
    return database.rows(sql + " ORDER BY d.id DESC LIMIT ?", (*params, limit))


@app.get("/api/drafts/export.csv", response_class=PlainTextResponse)
def export_drafts(context: Ctx = Depends(ctx)):
    rows = database.rows("SELECT id, customer_id, subject, body, recipient_type, consent_basis, decided_by, decided_at FROM drafts WHERE org_id=? AND status='approved' ORDER BY id", (context.org_id,))
    return _csv(rows, ["id", "customer_id", "subject", "body", "recipient_type", "consent_basis", "decided_by", "decided_at"], "approved_drafts.csv")


@app.get("/api/reviews/export.csv", response_class=PlainTextResponse)
def export_reviews(context: Ctx = Depends(ctx)):
    rows = database.rows("SELECT customer_id, decision, note, reviewer, created_at FROM reviews WHERE org_id=? ORDER BY id", (context.org_id,))
    return _csv(rows, ["customer_id", "decision", "note", "reviewer", "created_at"], "review_decisions.csv")


def _csv(rows: list[dict], fields: list[str], filename: str) -> PlainTextResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        # Neutralise spreadsheet formulas (CSV injection) in free-text cells.
        writer.writerow({k: ("'" + v if isinstance(v, str) and v[:1] in "=+-@" else v) for k, v in row.items()})
    return PlainTextResponse(buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.get("/api/drafts/{draft_id}")
def get_draft(draft_id: int, context: Ctx = Depends(ctx)):
    row = _draft_row(context, draft_id)
    label = database.rows("SELECT label, note, labeller FROM critic_labels WHERE org_id=? AND draft_id=?", (context.org_id, draft_id))
    return {**row, "human_label": label[0] if label else None}


@app.post("/api/drafts/{draft_id}/decision")
def decide(draft_id: int, decision: Decision, idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=100),
           context: Ctx = Depends(require("reviewer"))):
    scoped_key = f"{context.org_id}:{idempotency_key}"
    previous = database.rows("SELECT response FROM idempotency WHERE key=?", (scoped_key,))
    if previous:
        return json.loads(previous[0]["response"])
    draft = _draft_row(context, draft_id)
    if draft["status"] in ("approved", "rejected"):
        raise HTTPException(409, f"Draft already {draft['status']}")
    body = decision.edited_body.strip() if decision.edited_body else draft["body"]
    source = data_for(context)
    if decision.decision == "approve":
        account_row = source.account(draft["customer_id"])
        facts = Facts.from_account(account_row, _play_for(source, account_row.get("segment")))
        checks = check_draft(draft["subject"], body, facts)
        if not checks.passed:
            raise HTTPException(422, "Draft fails checks: " + "; ".join(c["name"] for c in checks.checks if not c["passed"]))
        critic = next((c for c in draft["checks"] if c["name"].startswith("Second-pass")), None)
        if critic and not critic["passed"] and not decision.acknowledge_review and decision.edited_body is None:
            raise HTTPException(422, "The second-pass review raised issues: edit the draft or confirm you have read them")
        if decision.consent_basis not in CONSENT_RULES.get(decision.recipient_type, set()):
            raise HTTPException(422, "No valid consent basis for this recipient type (UK PECR): record the recipient type and basis first")
    status = "approved" if decision.decision == "approve" else "rejected"
    who = actor(context, decision.reviewer)
    with database.connect() as db:
        db.execute(
            "UPDATE drafts SET status=?, body=?, recipient_type=?, consent_basis=?, decided_by=?, decided_at=? WHERE id=? AND org_id=?",
            (status, body, decision.recipient_type, decision.consent_basis, who, now(), draft_id, context.org_id),
        )
        database.audit(db, who, f"draft_{status}", f"draft:{draft_id}",
                       {"edited": decision.edited_body is not None, "recipient_type": decision.recipient_type, "consent_basis": decision.consent_basis, "note": decision.note},
                       context.org_id)
        if status == "approved":
            loop.mark_contacted(env, db, context.org_id, draft["customer_id"])
        response = {"id": draft_id, "status": status}
        db.execute("INSERT INTO idempotency (key, response, created_at) VALUES (?,?,?)", (scoped_key, json.dumps(response), now()))
    return response


# ---- Critic calibration (R5): people label drafts; agreement with the LLM critic is measured ----
from .calibration import cohen_kappa  # noqa: E402


@app.post("/api/drafts/{draft_id}/label")
def label_draft(draft_id: int, body: LabelIn, context: Ctx = Depends(require("reviewer"))):
    _draft_row(context, draft_id)
    with database.connect() as db:
        db.execute("INSERT OR REPLACE INTO critic_labels (org_id, draft_id, label, note, labeller, created_at) VALUES (?,?,?,?,?,?)",
                   (context.org_id, draft_id, body.label, body.note, context.name if settings.auth_mode != "off" else "local reviewer", now()))
    return {"ok": True}


@app.get("/api/critic/calibration")
def critic_calibration(context: Ctx = Depends(ctx)):
    rows = database.rows("SELECT d.id, d.checks, l.label FROM critic_labels l JOIN drafts d ON d.id=l.draft_id AND d.org_id=l.org_id WHERE l.org_id=?", (context.org_id,))
    pairs = []
    for row in rows:
        critic = next((c for c in json.loads(row["checks"]) if c["name"].startswith("Second-pass")), None)
        if critic is not None:
            pairs.append((row["label"], "pass" if critic["passed"] else "revise"))
    labelled = len(pairs)
    result = {"labelled": labelled, "target": 46, "kappa_target": 0.6,
              "confusion": {f"human_{h}_critic_{c}": sum(p == (h, c) for p in pairs) for h in ("pass", "revise") for c in ("pass", "revise")}}
    if labelled >= 2:
        human, critic = [p[0] for p in pairs], [p[1] for p in pairs]
        result.update({"agreement": round(sum(h == c for h, c in pairs) / labelled, 3), "cohen_kappa": round(cohen_kappa(human, critic), 3)})
    return result
