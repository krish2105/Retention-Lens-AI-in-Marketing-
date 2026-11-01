"""Accounts, workspaces (orgs), roles and the "who is calling" context for every request.

Modes (RL_AUTH_MODE):
- off: one local workspace, no sign-in. For running on your own machine only.
- local: email + password, opaque session cookie (HttpOnly) or Bearer token.
- supabase: Supabase Auth access tokens (HS256), users provisioned on first call.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator

from .db import LOCAL_ORG, now
from .env import Env
from .security import (
    MIN_PASSWORD,
    InvalidToken,
    hash_password,
    new_token,
    password_problem,
    token_hash,
    verify_hs256_jwt,
    verify_password,
)

ROLE_RANK = {"viewer": 0, "reviewer": 1, "owner": 2}
SESSION_DAYS = 7
COOKIE = "rl_session"
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TENANT_TABLES = ["reviews", "drafts", "audit_events", "datasets", "outreach_outcomes", "critic_labels", "memberships", "invites", "sessions"]


@dataclass(frozen=True)
class Ctx:
    user_id: str
    email: str
    name: str
    org_id: str
    role: str

    def at_least(self, role: str) -> bool:
        return ROLE_RANK[self.role] >= ROLE_RANK[role]


LOCAL_CTX = Ctx("local", "local@localhost", "Local user", LOCAL_ORG, "owner")


def _expiry(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(timespec="seconds")


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def make_context(env: Env):
    settings = env.settings

    def membership(user_id: str, org_id: str | None) -> dict | None:
        sql = "SELECT m.org_id, m.role FROM memberships m WHERE m.user_id=?"
        params: tuple = (user_id,)
        if org_id:
            sql, params = sql + " AND m.org_id=?", (user_id, org_id)
        rows = env.db.rows(sql + " ORDER BY m.created_at LIMIT 1", params)
        return rows[0] if rows else None

    def from_session(token: str, requested_org: str | None) -> Ctx | None:
        rows = env.db.rows(
            "SELECT s.user_id, s.org_id, s.expires_at, u.email, u.name FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=?",
            (token_hash(token),),
        )
        if not rows or rows[0]["expires_at"] < now():
            return None
        row = rows[0]
        member = membership(row["user_id"], requested_org or row["org_id"])
        if member is None:
            return None
        return Ctx(row["user_id"], row["email"], row["name"], member["org_id"], member["role"])

    def from_supabase(token: str, requested_org: str | None) -> Ctx | None:
        try:
            claims = verify_hs256_jwt(token, settings.supabase_jwt_secret)
        except InvalidToken:
            return None
        email = (claims.get("email") or f"{claims['sub']}@users.supabase").lower()
        name = (claims.get("user_metadata") or {}).get("name") or email.split("@")[0]
        user = provision_user(email, name, external_id=claims["sub"])
        member = membership(user["id"], requested_org)
        if member is None:
            if requested_org:
                return None
            org_id = create_org(f"{name}'s workspace", user["id"])
            member = {"org_id": org_id, "role": "owner"}
        return Ctx(user["id"], email, name, member["org_id"], member["role"])

    def provision_user(email: str, name: str, external_id: str | None = None, password: str | None = None) -> dict:
        existing = env.db.rows("SELECT * FROM users WHERE email=?", (email,))
        if existing:
            return existing[0]
        user_id = "u_" + secrets.token_hex(8)
        with env.db.connect() as db:
            db.execute("INSERT INTO users (id, email, name, password_hash, external_id, created_at) VALUES (?,?,?,?,?,?)",
                       (user_id, email, name, hash_password(password) if password else None, external_id, now()))
        return env.db.rows("SELECT * FROM users WHERE id=?", (user_id,))[0]

    def create_org(name: str, owner_id: str) -> str:
        org_id = "o_" + secrets.token_hex(8)
        with env.db.connect() as db:
            db.execute("INSERT INTO orgs (id, name, plan, use_sample, created_at) VALUES (?,?,?,?,?)", (org_id, name, "pilot", 0, now()))
            db.execute("INSERT INTO memberships (org_id, user_id, role, created_at) VALUES (?,?,?,?)", (org_id, owner_id, "owner", now()))
            env.db.audit(db, owner_id, "org_created", f"org:{org_id}", {"name": name}, org_id)
        return org_id

    def ctx(request: Request) -> Ctx:
        if settings.auth_mode == "off":
            return LOCAL_CTX
        header = request.headers.get("authorization", "")
        token = header[7:] if header.lower().startswith("bearer ") else request.cookies.get(COOKIE)
        requested_org = request.headers.get("x-org-id")
        found = None
        if token:
            found = from_supabase(token, requested_org) if settings.auth_mode == "supabase" else from_session(token, requested_org)
        if found is None:
            raise HTTPException(401, "Sign in to continue")
        return found

    def require(role: str):
        def check(context: Ctx = Depends(ctx)) -> Ctx:
            if not context.at_least(role):
                raise HTTPException(403, f"This needs the {role} role")
            return context

        return check

    return ctx, require, provision_user, create_org


class SignUp(BaseModel):
    email: str = Field(max_length=254)
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=MIN_PASSWORD, max_length=200)
    workspace: str = Field(default="", max_length=100)
    invite: str | None = Field(default=None, max_length=200)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL.match(value):
            raise ValueError("Enter a valid email address")
        return value


class SignIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=200)


class InviteIn(BaseModel):
    email: str = Field(max_length=254)
    role: Literal["reviewer", "viewer", "owner"] = "reviewer"


class RoleIn(BaseModel):
    role: Literal["reviewer", "viewer", "owner"]


class SwitchIn(BaseModel):
    org_id: str = Field(max_length=40)


class DeleteOrgIn(BaseModel):
    confirm: str = Field(max_length=100)


class SampleIn(BaseModel):
    enabled: bool


def router(env: Env, ctx, require, provision_user, create_org) -> APIRouter:
    api = APIRouter()
    settings = env.settings

    def start_session(response: Response, user_id: str, org_id: str) -> dict:
        token, hashed = new_token()
        with env.db.connect() as db:
            db.execute("INSERT INTO sessions (token_hash, user_id, org_id, expires_at, created_at) VALUES (?,?,?,?,?)",
                       (hashed, user_id, org_id, _expiry(SESSION_DAYS), now()))
        response.set_cookie(COOKIE, token, max_age=SESSION_DAYS * 86400, httponly=True, secure=settings.cookie_secure,
                            samesite="none" if settings.cookie_secure else "lax", path="/")
        return {"token": token, "expires_in_days": SESSION_DAYS}

    def limited(request: Request, bucket: str, limit: int, window: int) -> None:
        if not env.limiter.allow(f"{bucket}:{_client_ip(request)}", limit, window):
            raise HTTPException(429, "Too many attempts; wait a minute and try again")

    def accept_invite(user_id: str, email: str, token: str) -> str:
        rows = env.db.rows("SELECT * FROM invites WHERE token_hash=? AND accepted_at IS NULL", (token_hash(token),))
        if not rows or rows[0]["expires_at"] < now() or rows[0]["email"] != email:
            raise HTTPException(400, "This invite is not valid for this email address, or it has expired")
        invite = rows[0]
        with env.db.connect() as db:
            db.execute("INSERT OR REPLACE INTO memberships (org_id, user_id, role, created_at) VALUES (?,?,?,?)", (invite["org_id"], user_id, invite["role"], now()))
            db.execute("UPDATE invites SET accepted_at=? WHERE token_hash=?", (now(), invite["token_hash"]))
            env.db.audit(db, email, "invite_accepted", f"user:{user_id}", {"role": invite["role"]}, invite["org_id"])
        return invite["org_id"]

    def local_only() -> None:
        if settings.auth_mode != "local":
            raise HTTPException(404, "Email sign-in is not enabled on this server")

    @api.post("/api/auth/signup")
    def signup(body: SignUp, request: Request, response: Response):
        local_only()
        limited(request, "auth", 10, 60)
        problem = password_problem(body.password, body.email)
        if problem:
            raise HTTPException(422, problem)
        if env.db.rows("SELECT id FROM users WHERE email=?", (body.email,)):
            raise HTTPException(409, "An account with this email already exists; sign in instead")
        user = provision_user(body.email, body.name.strip(), password=body.password)
        org_id = accept_invite(user["id"], body.email, body.invite) if body.invite else create_org(body.workspace.strip() or f"{body.name.strip()}'s workspace", user["id"])
        return start_session(response, user["id"], org_id)

    @api.post("/api/auth/signin")
    def signin(body: SignIn, request: Request, response: Response):
        local_only()
        limited(request, "auth", 10, 60)
        email = body.email.strip().lower()
        # Per-account throttle on top of the per-IP one, so spreading attempts over many IPs does not help.
        if not env.limiter.allow(f"signin-account:{email}", 10, 900):
            raise HTTPException(429, "Too many attempts for this account; wait 15 minutes")
        rows = env.db.rows("SELECT * FROM users WHERE email=?", (email,))
        if not verify_password(body.password, rows[0]["password_hash"] if rows else None):
            # Logged without the email itself: a short hash links repeated attempts on one account.
            with env.db.connect() as db:
                env.db.audit(db, "anonymous", "signin_failed", f"account:{hashlib.sha256(email.encode()).hexdigest()[:12]}",
                             {"ip": _client_ip(request), "known_account": bool(rows)}, "security")
            raise HTTPException(401, "Email or password is wrong")
        member = env.db.rows("SELECT org_id FROM memberships WHERE user_id=? ORDER BY created_at LIMIT 1", (rows[0]["id"],))
        if not member:
            raise HTTPException(403, "This account has no workspace")
        return start_session(response, rows[0]["id"], member[0]["org_id"])

    @api.post("/api/auth/signout")
    def signout(request: Request, response: Response):
        token = request.cookies.get(COOKIE) or request.headers.get("authorization", "")[7:]
        if token:
            with env.db.connect() as db:
                db.execute("DELETE FROM sessions WHERE token_hash=?", (token_hash(token),))
        response.delete_cookie(COOKIE, path="/")
        return {"ok": True}

    @api.get("/api/auth/me")
    def me(context: Ctx = Depends(ctx)):
        orgs = env.db.rows("SELECT o.id, o.name, m.role FROM memberships m JOIN orgs o ON o.id=m.org_id WHERE m.user_id=? ORDER BY o.name", (context.user_id,))
        org = env.org(context.org_id)
        return {"auth_mode": settings.auth_mode, "user": {"id": context.user_id, "email": context.email, "name": context.name},
                "org": {"id": org["id"], "name": org["name"], "plan": org["plan"], "use_sample": bool(org["use_sample"]), "active_dataset": org["active_dataset"]},
                "role": context.role, "orgs": orgs or [{"id": org["id"], "name": org["name"], "role": context.role}]}

    @api.post("/api/auth/switch")
    def switch(body: SwitchIn, request: Request, context: Ctx = Depends(ctx)):
        if not env.db.rows("SELECT 1 FROM memberships WHERE user_id=? AND org_id=?", (context.user_id, body.org_id)):
            raise HTTPException(403, "You are not a member of that workspace")
        token = request.cookies.get(COOKIE) or request.headers.get("authorization", "")[7:]
        with env.db.connect() as db:
            db.execute("UPDATE sessions SET org_id=? WHERE token_hash=?", (body.org_id, token_hash(token)))
        return {"ok": True, "org_id": body.org_id}

    @api.post("/api/auth/accept-invite")
    def accept(body: dict, context: Ctx = Depends(ctx)):
        return {"org_id": accept_invite(context.user_id, context.email, str(body.get("token", "")))}

    @api.get("/api/org/members")
    def members(context: Ctx = Depends(ctx)):
        people = env.db.rows("SELECT u.id, u.email, u.name, m.role, m.created_at FROM memberships m JOIN users u ON u.id=m.user_id WHERE m.org_id=? ORDER BY m.created_at", (context.org_id,))
        invites = env.db.rows("SELECT email, role, expires_at FROM invites WHERE org_id=? AND accepted_at IS NULL ORDER BY expires_at DESC", (context.org_id,)) if context.at_least("owner") else []
        if settings.auth_mode == "off":
            people = [{"id": "local", "email": LOCAL_CTX.email, "name": LOCAL_CTX.name, "role": "owner", "created_at": None}]
        return {"members": people, "invites": invites}

    @api.post("/api/org/invites")
    def invite(body: InviteIn, context: Ctx = Depends(require("owner"))):
        if settings.auth_mode == "off":
            raise HTTPException(400, "Invites need sign-in: set RL_AUTH_MODE=local or supabase")
        email = body.email.strip().lower()
        if not EMAIL.match(email):
            raise HTTPException(422, "Enter a valid email address")
        token, hashed = new_token()
        with env.db.connect() as db:
            db.execute("INSERT INTO invites (token_hash, org_id, email, role, created_by, expires_at) VALUES (?,?,?,?,?,?)",
                       (hashed, context.org_id, email, body.role, context.user_id, _expiry(7)))
            env.db.audit(db, context.email, "invite_created", f"invite:{email}", {"role": body.role}, context.org_id)
        # Nothing is emailed: the owner shares this link themselves. It is shown once.
        return {"invite_url": f"{settings.public_web_url}/signin/?invite={token}", "expires_in_days": 7}

    @api.post("/api/org/members/{user_id}/role")
    def set_role(user_id: str, body: RoleIn, context: Ctx = Depends(require("owner"))):
        owners = env.db.rows("SELECT user_id FROM memberships WHERE org_id=? AND role='owner'", (context.org_id,))
        if body.role != "owner" and [o["user_id"] for o in owners] == [user_id]:
            raise HTTPException(409, "A workspace needs at least one owner")
        with env.db.connect() as db:
            changed = db.execute("UPDATE memberships SET role=? WHERE org_id=? AND user_id=?", (body.role, context.org_id, user_id)).rowcount
            if not changed:
                raise HTTPException(404, "No such member")
            env.db.audit(db, context.email, "role_changed", f"user:{user_id}", {"role": body.role}, context.org_id)
        return {"ok": True}

    @api.post("/api/org/members/{user_id}/remove")
    def remove_member(user_id: str, context: Ctx = Depends(require("owner"))):
        owners = env.db.rows("SELECT user_id FROM memberships WHERE org_id=? AND role='owner'", (context.org_id,))
        if [o["user_id"] for o in owners] == [user_id]:
            raise HTTPException(409, "A workspace needs at least one owner")
        with env.db.connect() as db:
            db.execute("DELETE FROM memberships WHERE org_id=? AND user_id=?", (context.org_id, user_id))
            db.execute("DELETE FROM sessions WHERE org_id=? AND user_id=?", (context.org_id, user_id))
            env.db.audit(db, context.email, "member_removed", f"user:{user_id}", {}, context.org_id)
        return {"ok": True}

    @api.post("/api/org/sample")
    def sample(body: SampleIn, context: Ctx = Depends(require("owner"))):
        with env.db.connect() as db:
            db.execute("UPDATE orgs SET use_sample=? WHERE id=?", (int(body.enabled), context.org_id))
            env.db.audit(db, context.email, "sample_data", f"org:{context.org_id}", {"enabled": body.enabled}, context.org_id)
        return {"ok": True}

    @api.get("/api/org/export")
    def export(context: Ctx = Depends(require("owner"))):
        """Everything stored for this workspace, as JSON (data portability)."""
        out = {"org": env.org(context.org_id), "exported_at": now()}
        for table in ["reviews", "drafts", "audit_events", "datasets", "outreach_outcomes", "critic_labels", "memberships"]:
            out[table] = env.db.rows(f"SELECT * FROM {table} WHERE org_id=?", (context.org_id,))
        return out

    @api.post("/api/org/delete")
    def delete_org(body: DeleteOrgIn, context: Ctx = Depends(require("owner"))):
        """Erase this workspace: rows in every tenant table and all uploaded files. Cannot be undone."""
        org = env.org(context.org_id)
        if body.confirm.strip() != org["name"]:
            raise HTTPException(422, "Type the workspace name exactly to confirm")
        with env.db.connect() as db:
            counts = {t: db.execute(f"DELETE FROM {t} WHERE org_id=?", (context.org_id,)).rowcount for t in TENANT_TABLES}
            if context.org_id == LOCAL_ORG:
                db.execute("UPDATE orgs SET active_dataset=NULL, use_sample=1 WHERE id=?", (LOCAL_ORG,))
            else:
                db.execute("DELETE FROM orgs WHERE id=?", (context.org_id,))
            # A tombstone with no personal data, so the deletion itself is provable.
            db.execute("INSERT INTO audit_events (org_id, at, actor, action, subject, detail) VALUES (?,?,?,?,?,?)",
                       ("deleted", now(), "system", "org_deleted", f"org:{context.org_id}", json.dumps({"rows": counts}, sort_keys=True)))
        shutil.rmtree(env.org_dir(context.org_id), ignore_errors=True)
        return {"ok": True, "deleted_rows": counts}

    return api
