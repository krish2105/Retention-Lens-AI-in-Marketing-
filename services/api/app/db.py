"""SQLite state: tenants, users, datasets, reviews, drafts, outcomes and an append-only audit log.

Every tenant table carries org_id and every query in the API filters on it. The Postgres
version with row-level security is in supabase/migrations/.
"""
from __future__ import annotations

import json
import re
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
INDEXES = [
    "CREATE INDEX IF NOT EXISTS reviews_org ON reviews (org_id, customer_id)",
    "CREATE INDEX IF NOT EXISTS drafts_org ON drafts (org_id, status)",
    "CREATE INDEX IF NOT EXISTS audit_org ON audit_events (org_id, id)",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# Postgres needs explicit conflict targets for SQLite's INSERT OR REPLACE.
UPSERT_KEYS = {"memberships": ("org_id", "user_id"), "critic_labels": ("org_id", "draft_id")}
SERIAL_TABLES = {"reviews", "drafts", "audit_events", "outreach_outcomes", "waitlist"}
_INSERT = re.compile(r"^\s*INSERT OR (IGNORE|REPLACE) INTO (\w+) \(([^)]*)\)", re.I)


def to_postgres(sql: str) -> str:
    """Translate the small SQLite dialect the API uses into Postgres."""
    match = _INSERT.match(sql)
    out = sql.replace("?", "%s")
    if match:
        kind, table, columns = match.group(1).upper(), match.group(2), [c.strip() for c in match.group(3).split(",")]
        out = re.sub(r"INSERT OR (IGNORE|REPLACE) INTO", "INSERT INTO", out, count=1, flags=re.I)
        if kind == "IGNORE":
            out += " ON CONFLICT DO NOTHING"
        else:
            key = UPSERT_KEYS[table]
            updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in columns if c not in key)
            out += f" ON CONFLICT ({', '.join(key)}) DO UPDATE SET {updates}"
    return out


class _PgCursor:
    def __init__(self, cursor, lastrowid=None):
        self._cursor, self.lastrowid = cursor, lastrowid

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor.fetchall())


class _PgConnection:
    """Gives a psycopg connection the sqlite3 surface the API code uses (execute, executemany, lastrowid)."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql: str, params: tuple = ()):
        query = to_postgres(sql)
        insert = re.match(r"^\s*INSERT INTO (\w+)", query, re.I)
        want_id = bool(insert and insert.group(1) in SERIAL_TABLES and "ON CONFLICT" not in query)
        if want_id:
            query += " RETURNING id"
        cursor = self._conn.execute(query, params)
        return _PgCursor(cursor, cursor.fetchone()["id"] if want_id else None)

    def executemany(self, sql: str, seq):
        cursor = self._conn.cursor()
        cursor.executemany(to_postgres(sql), list(seq))
        return _PgCursor(cursor)


class Database:
    """SQLite by default; Postgres when RL_DATABASE_URL is set (tables live in their own schema)."""

    def __init__(self, path: Path, url: str = "", schema: str = "retentionlens"):
        self.path, self.url, self.schema = path, url, schema
        self.dialect = "postgres" if url else "sqlite"
        self._pool = None
        if self.dialect == "postgres":
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", schema):
                raise ValueError("RL_DB_SCHEMA must be a simple lower-case identifier")
            import psycopg
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool

            with psycopg.connect(url, autocommit=True) as admin:
                admin.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            self._pool = ConnectionPool(url, min_size=1, max_size=10, open=True,
                                        kwargs={"row_factory": dict_row, "options": f"-c search_path={schema}"})
            with self.connect() as db:
                db._conn.execute(SCHEMA.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY"))
                for table in TENANT_COLUMNS:
                    db._conn.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS org_id TEXT NOT NULL DEFAULT '{LOCAL_ORG}'")
                for statement in INDEXES:
                    db._conn.execute(statement)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)
            for table in TENANT_COLUMNS:
                columns = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
                if "org_id" not in columns:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN org_id TEXT NOT NULL DEFAULT '{LOCAL_ORG}'")
            for statement in INDEXES:
                db.execute(statement)

    @contextmanager
    def connect(self):
        if self._pool is not None:
            with self._pool.connection() as conn:
                yield _PgConnection(conn)  # the pool commits on success and rolls back on error
            return
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
