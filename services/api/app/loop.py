"""The weekly review loop (R2) and outcome tracking (R6 evidence).

Each week the queue takes the highest value-at-risk accounts. A random share of them
(RL_HOLDOUT_SHARE, default 20%) is held out and not shown, so reorder rates of contacted
and held-out accounts can be compared: a randomised test, not a before/after story.
Reorders are detected from the next upload, or logged by hand.
"""
from __future__ import annotations

import hashlib
import math
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .db import now
from .env import Env
from .tenancy import Ctx

OBSERVE_DAYS = 28


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def in_holdout(org_id: str, customer_id: str, week: str, share: float) -> bool:
    digest = hashlib.sha256(f"{org_id}|{customer_id}|{week}".encode()).hexdigest()
    return int(digest[:8], 16) / 2**32 < share


def mark_contacted(env: Env, db, org_id: str, customer_id: str) -> None:
    db.execute(
        "UPDATE outreach_outcomes SET contacted_at=? WHERE org_id=? AND customer_id=? AND arm='contact' AND contacted_at IS NULL "
        "AND week=(SELECT MAX(week) FROM outreach_outcomes WHERE org_id=? AND customer_id=?)",
        (now(), org_id, customer_id, org_id, customer_id),
    )


def detect_reorders(env: Env, org_id: str, accounts: list[dict], cutoff: str) -> int:
    """Mark outcomes whose account bought on or after the start of the week it was queued."""
    end = date.fromisoformat(cutoff)
    last_purchase = {a["customer_id"]: end - timedelta(days=int(a["recency_days"])) for a in accounts}
    updated = 0
    with env.db.connect() as db:
        for row in db.execute("SELECT id, customer_id, week, reordered_at FROM outreach_outcomes WHERE org_id=?", (org_id,)).fetchall():
            bought = last_purchase.get(row["customer_id"])
            if row["reordered_at"] is None and bought is not None and bought >= date.fromisoformat(row["week"]):
                db.execute("UPDATE outreach_outcomes SET reordered_at=? WHERE id=?", (bought.isoformat(), row["id"]))
                updated += 1
        db.execute("UPDATE outreach_outcomes SET checked_through=? WHERE org_id=? AND (checked_through IS NULL OR checked_through<?)", (end.isoformat(), org_id, end.isoformat()))
    return updated


def rate_difference(a_hits: int, a_n: int, b_hits: int, b_n: int) -> dict:
    if not a_n or not b_n:
        return {"difference": None, "ci95": None}
    pa, pb = a_hits / a_n, b_hits / b_n
    se = math.sqrt(pa * (1 - pa) / a_n + pb * (1 - pb) / b_n)
    diff = pa - pb
    return {"difference": round(diff, 4), "ci95": [round(diff - 1.96 * se, 4), round(diff + 1.96 * se, 4)]}


class ReorderIn(BaseModel):
    customer_id: str = Field(min_length=1, max_length=40)
    week: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    reordered_on: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


def router(env: Env, ctx, require) -> APIRouter:
    api = APIRouter()
    settings = env.settings

    @api.get("/api/queue")
    def weekly_queue(week: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"), context: Ctx = Depends(ctx)):
        start = week_start(date.fromisoformat(week) if week else date.today())
        key = start.isoformat()
        accounts = env.store_for(context.org_id).get("accounts")
        at_risk = sorted((a for a in accounts if a["risk_band"] in ("high", "watch")), key=lambda a: -(a["value_at_risk_90"] or 0))
        take = math.ceil(settings.queue_size / max(1 - settings.holdout_share, 0.05))
        chosen = at_risk[:take]
        arms = {a["customer_id"]: ("holdout" if in_holdout(context.org_id, a["customer_id"], key, settings.holdout_share) else "contact") for a in chosen}
        stored = {r["customer_id"]: r for r in env.db.rows("SELECT * FROM outreach_outcomes WHERE org_id=? AND week=?", (context.org_id, key))}
        missing = [(context.org_id, cid, key, arm, now()) for cid, arm in arms.items() if cid not in stored]
        # Write only the first time an account enters this week's queue: repeat reads stay read-only,
        # so concurrent reviewers do not queue behind SQLite's write lock (found by the load test).
        if missing and context.at_least("reviewer"):
            with env.db.connect() as db:
                db.executemany("INSERT OR IGNORE INTO outreach_outcomes (org_id, customer_id, week, arm, created_at) VALUES (?,?,?,?,?)", missing)
                stored.update({r["customer_id"]: dict(r) for r in db.execute("SELECT * FROM outreach_outcomes WHERE org_id=? AND week=?", (context.org_id, key))})
        reviews = env.db.rows(
            "SELECT customer_id, decision, reviewer, created_at FROM reviews WHERE org_id=? AND created_at>=? ORDER BY id", (context.org_id, key)
        )
        latest = {r["customer_id"]: r for r in reviews}
        items = []
        for a in chosen:
            if arms[a["customer_id"]] != "contact":
                continue
            review = latest.get(a["customer_id"])
            items.append({**{k: a.get(k) for k in ("customer_id", "country", "risk_band", "p_lapse", "value_at_risk_90", "expected_value_90", "recency_days", "segment", "reasons")},
                          "status": "reviewed" if review else "to_review", "decision": review and review["decision"],
                          "contacted": bool(stored.get(a["customer_id"], {}).get("contacted_at"))})
            if len(items) >= settings.queue_size:
                break
        reviewed = sum(i["status"] == "reviewed" for i in items)
        return {"week": key, "items": items, "reviewed": reviewed, "total": len(items), "cleared": bool(items) and reviewed == len(items),
                "holdout": sum(arm == "holdout" for arm in arms.values()), "holdout_share": settings.holdout_share}

    @api.post("/api/outcomes/reorder")
    def log_reorder(body: ReorderIn, context: Ctx = Depends(require("reviewer"))):
        with env.db.connect() as db:
            changed = db.execute("UPDATE outreach_outcomes SET reordered_at=? WHERE org_id=? AND customer_id=? AND week=?",
                                 (body.reordered_on, context.org_id, body.customer_id, body.week)).rowcount
            if not changed:
                raise HTTPException(404, "That account was not in the queue that week")
            env.db.audit(db, context.email, "reorder_logged", body.customer_id, body.model_dump(), context.org_id)
        return {"ok": True}

    @api.get("/api/funnel")
    def funnel(context: Ctx = Depends(ctx)):
        """Time from first upload to scored data to first decision, from the audit log (the R2 usability gate)."""
        events = env.db.rows(
            "SELECT action, MIN(at) AS first FROM audit_events WHERE org_id=? AND action IN ('dataset_uploaded', 'dataset_ready', 'review') GROUP BY action",
            (context.org_id,),
        )
        first = {e["action"]: e["first"] for e in events}

        def minutes(a: str, b: str):
            if a not in first or b not in first or first[b] < first[a]:
                return None
            from datetime import datetime

            return round((datetime.fromisoformat(first[b]) - datetime.fromisoformat(first[a])).total_seconds() / 60, 1)

        to_decision = minutes("dataset_uploaded", "review")
        return {"first_upload": first.get("dataset_uploaded"), "first_scored": first.get("dataset_ready"), "first_decision": first.get("review"),
                "minutes_upload_to_scored": minutes("dataset_uploaded", "dataset_ready"), "minutes_upload_to_first_decision": to_decision,
                "target_minutes": 10, "within_target": None if to_decision is None else to_decision <= 10}

    @api.get("/api/outcomes")
    def outcomes(context: Ctx = Depends(ctx)):
        rows = env.db.rows("SELECT * FROM outreach_outcomes WHERE org_id=? ORDER BY week DESC, customer_id", (context.org_id,))
        mature = [r for r in rows if r["checked_through"] and date.fromisoformat(r["checked_through"]) >= date.fromisoformat(r["week"]) + timedelta(days=OBSERVE_DAYS)]
        arms = {}
        for arm in ("contact", "holdout"):
            group = [r for r in mature if r["arm"] == arm]
            hits = sum(r["reordered_at"] is not None for r in group)
            arms[arm] = {"accounts": len(group), "reordered": hits, "rate": round(hits / len(group), 4) if group else None,
                         "contacted": sum(r["contacted_at"] is not None for r in group)}
        weeks = sorted({r["week"] for r in rows}, reverse=True)
        return {
            "arms": arms,
            "uplift": rate_difference(arms["contact"]["reordered"], arms["contact"]["accounts"], arms["holdout"]["reordered"], arms["holdout"]["accounts"]),
            "observe_days": OBSERVE_DAYS,
            "pending": len(rows) - len(mature),
            "weeks": weeks,
            "method": "Intention to treat: every queued account counts in the contact arm whether or not it was contacted. 95% CI uses a normal approximation.",
        }

    return api
