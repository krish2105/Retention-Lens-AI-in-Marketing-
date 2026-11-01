"""Local SQLite state: reviews, outreach drafts and an append-only audit log."""
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
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def audit(self, db, actor: str, action: str, subject: str, detail: dict) -> None:
        db.execute(
            "INSERT INTO audit_events (at, actor, action, subject, detail) VALUES (?,?,?,?,?)",
            (now(), actor, action, subject, json.dumps(detail, sort_keys=True)),
        )

    def rows(self, sql: str, params: tuple = ()) -> list[dict]:
        with self.connect() as db:
            return [dict(r) for r in db.execute(sql, params).fetchall()]
