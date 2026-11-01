"""Plans, entitlements and Stripe Checkout in TEST MODE only (R6).

Prices are a hypothesis to be tested in customer interviews (Van Westendorp), not validated.
Live Stripe keys are refused: this build must not take real money.
"""
from __future__ import annotations

import json
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from .db import now
from .env import Env
from .security import verify_stripe_signature
from .tenancy import Ctx

PLANS = {
    "pilot": {"name": "Pilot", "price_gbp_month": 0, "max_accounts": 2_000, "seats": 3, "note": "4-week pilot with a holdout test"},
    "starter": {"name": "Starter", "price_gbp_month": 49, "max_accounts": 2_000, "seats": 3, "note": "One sales team"},
    "growth": {"name": "Growth", "price_gbp_month": 149, "max_accounts": 15_000, "seats": 10, "note": "Several teams or regions"},
}
STATUS = "Pricing hypothesis: not yet validated with customers"


class CheckoutIn(BaseModel):
    plan: Literal["starter", "growth"]


def router(env: Env, ctx, require) -> APIRouter:
    api = APIRouter()
    settings = env.settings

    def configured() -> tuple[bool, str]:
        key = settings.stripe_secret_key
        if not key:
            return False, "Billing is not configured on this server (no STRIPE_SECRET_KEY)"
        if not key.startswith(("sk_test_", "rk_test_")):
            return False, "Only Stripe test-mode keys are accepted in this build"
        return True, "Stripe test mode"

    @api.get("/api/plans")
    def plans():
        return {"plans": PLANS, "status": STATUS, "currency": "GBP"}

    @api.get("/api/billing")
    def billing(context: Ctx = Depends(ctx)):
        org = env.org(context.org_id)
        accounts = 0
        try:
            accounts = len(env.store_for(context.org_id).get("accounts"))
        except Exception:
            pass
        ok, note = configured()
        plan = PLANS[org["plan"]]
        return {"plan": org["plan"], "limits": plan, "usage": {"active_accounts": accounts, "share": round(accounts / plan["max_accounts"], 3)},
                "billing_configured": ok, "note": note, "status": STATUS}

    @api.post("/api/billing/checkout")
    def checkout(body: CheckoutIn, context: Ctx = Depends(require("owner"))):
        ok, note = configured()
        price = settings.stripe_prices.get(body.plan)
        if not ok or not price:
            raise HTTPException(503, note if not ok else f"No Stripe price set for {body.plan} (STRIPE_PRICE_{body.plan.upper()})")
        form = {
            "mode": "subscription",
            "line_items[0][price]": price,
            "line_items[0][quantity]": "1",
            "success_url": f"{settings.public_web_url}/billing/?checkout=success",
            "cancel_url": f"{settings.public_web_url}/billing/?checkout=cancelled",
            "client_reference_id": context.org_id,
            "metadata[org_id]": context.org_id,
            "metadata[plan]": body.plan,
            "subscription_data[metadata][org_id]": context.org_id,
            "subscription_data[metadata][plan]": body.plan,
        }
        try:
            response = httpx.post("https://api.stripe.com/v1/checkout/sessions", data=form, auth=(settings.stripe_secret_key, ""), timeout=15)
        except httpx.HTTPError as error:
            raise HTTPException(502, "Stripe could not be reached") from error
        if response.status_code >= 400:
            raise HTTPException(502, f"Stripe refused the request: {response.json().get('error', {}).get('message', response.status_code)}")
        with env.db.connect() as db:
            env.db.audit(db, context.email, "checkout_started", f"plan:{body.plan}", {"mode": "test"}, context.org_id)
        return {"url": response.json()["url"]}

    @api.post("/api/billing/webhook")
    async def webhook(request: Request):
        payload = await request.body()
        if not verify_stripe_signature(payload, request.headers.get("stripe-signature", ""), settings.stripe_webhook_secret):
            raise HTTPException(400, "Bad signature")
        event = json.loads(payload)
        if event.get("livemode"):
            raise HTTPException(400, "Live-mode events are not accepted")
        obj = event.get("data", {}).get("object", {})
        org_id = (obj.get("metadata") or {}).get("org_id") or obj.get("client_reference_id")
        with env.db.connect() as db:
            if db.execute("SELECT 1 FROM billing_events WHERE id=?", (event["id"],)).fetchone():
                return {"ok": True, "duplicate": True}
            db.execute("INSERT INTO billing_events (id, org_id, type, created_at) VALUES (?,?,?,?)", (event["id"], org_id, event["type"], now()))
            if org_id and db.execute("SELECT 1 FROM orgs WHERE id=?", (org_id,)).fetchone():
                if event["type"] == "checkout.session.completed":
                    plan = (obj.get("metadata") or {}).get("plan")
                    if plan in PLANS:
                        db.execute("UPDATE orgs SET plan=?, stripe_customer=? WHERE id=?", (plan, obj.get("customer"), org_id))
                elif event["type"] == "customer.subscription.deleted":
                    db.execute("UPDATE orgs SET plan='pilot' WHERE id=?", (org_id,))
                env.db.audit(db, "stripe", event["type"], f"org:{org_id}", {"event": event["id"]}, org_id)
        return {"ok": True}

    return api
