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
