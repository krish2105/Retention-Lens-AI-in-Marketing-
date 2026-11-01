"""SQLite state: tenants, users, datasets, reviews, drafts, outcomes and an append-only audit log.

Every tenant table carries org_id and every query in the API filters on it. The Postgres
version with row-level security is in supabase/migrations/.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id TEXT NOT NULL,
  decision TEXT NOT NULL,
  note TEXT NOT NULL,
  reviewer TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id TEXT NOT NULL,
  status TEXT NOT NULL,
  source TEXT NOT NULL,
  model TEXT,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  checks TEXT NOT NULL,
  context TEXT NOT NULL,
  recipient_type TEXT,
  consent_basis TEXT,
  decided_by TEXT,
  decided_at TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  subject TEXT NOT NULL,
  detail TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency (
  key TEXT PRIMARY KEY,
  response TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orgs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'pilot',
  use_sample INTEGER NOT NULL DEFAULT 0,
  active_dataset TEXT,
  stripe_customer TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  password_hash TEXT,
  external_id TEXT UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memberships (
  org_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('owner', 'reviewer', 'viewer')),
  created_at TEXT NOT NULL,
  PRIMARY KEY (org_id, user_id)
);
CREATE TABLE IF NOT EXISTS invites (
  token_hash TEXT PRIMARY KEY,
  org_id TEXT NOT NULL,
  email TEXT NOT NULL,
  role TEXT NOT NULL,
  created_by TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  accepted_at TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  org_id TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS datasets (
  id TEXT PRIMARY KEY,
  org_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  bytes INTEGER NOT NULL,
  status TEXT NOT NULL,
  stage TEXT,
  pct INTEGER NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0,
  mapping TEXT,
  date_order TEXT NOT NULL DEFAULT 'auto',
  inspect TEXT,
  validation TEXT,
  summary TEXT,
  error TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (org_id, sha256)
);
CREATE TABLE IF NOT EXISTS outreach_outcomes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  org_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  week TEXT NOT NULL,
  arm TEXT NOT NULL CHECK (arm IN ('contact', 'holdout')),
  contacted_at TEXT,
  reordered_at TEXT,
  checked_through TEXT,
  created_at TEXT NOT NULL,
  UNIQUE (org_id, customer_id, week)
);
CREATE TABLE IF NOT EXISTS waitlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  company TEXT NOT NULL,
  role TEXT NOT NULL,
  accounts_band TEXT NOT NULL,
  consent_at TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS critic_labels (
  org_id TEXT NOT NULL,
  draft_id INTEGER NOT NULL,
  label TEXT NOT NULL CHECK (label IN ('pass', 'revise')),
  note TEXT NOT NULL,
  labeller TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (org_id, draft_id)
);
CREATE TABLE IF NOT EXISTS billing_events (
  id TEXT PRIMARY KEY,
  org_id TEXT,
  type TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""

# Tables from before tenancy (P6) gain an org_id; existing rows belong to the local workspace.
TENANT_COLUMNS = {"reviews", "drafts", "audit_events"}
LOCAL_ORG = "local"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)
            for table in TENANT_COLUMNS:
                columns = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
                if "org_id" not in columns:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN org_id TEXT NOT NULL DEFAULT '{LOCAL_ORG}'")
            db.execute("CREATE INDEX IF NOT EXISTS reviews_org ON reviews (org_id, customer_id)")
            db.execute("CREATE INDEX IF NOT EXISTS drafts_org ON drafts (org_id, status)")
            db.execute("CREATE INDEX IF NOT EXISTS audit_org ON audit_events (org_id, id)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def audit(self, db, actor: str, action: str, subject: str, detail: dict, org_id: str = LOCAL_ORG) -> None:
        db.execute(
            "INSERT INTO audit_events (org_id, at, actor, action, subject, detail) VALUES (?,?,?,?,?,?)",
            (org_id, now(), actor, action, subject, json.dumps(detail, sort_keys=True)),
        )

    def rows(self, sql: str, params: tuple = ()) -> list[dict]:
        with self.connect() as db:
            return [dict(r) for r in db.execute(sql, params).fetchall()]
