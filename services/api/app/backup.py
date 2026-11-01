"""Scheduled online backups of the SQLite database (R4). Same method as scripts/backup_db.py.

RL_BACKUP_HOURS sets the interval (default 24; 0 turns it off). Backups go to RL_BACKUP_DIR, keep the
newest 14, and each has a SHA-256 sidecar. The status endpoint reports the newest one.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

KEEP = 14


def backup_now(db: Path, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = out / f"retentionlens-{stamp}.sqlite3"
    with sqlite3.connect(db) as source, sqlite3.connect(target) as dest:
        source.backup(dest)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".json").write_text(json.dumps({"file": target.name, "sha256": digest, "created_at": stamp}) + "\n")
    for old in sorted(out.glob("retentionlens-*.sqlite3"))[:-KEEP]:
        old.unlink()
        old.with_suffix(".json").unlink(missing_ok=True)
    return target


def latest(out: Path) -> dict | None:
    files = sorted(out.glob("retentionlens-*.json")) if out.exists() else []
    return json.loads(files[-1].read_text()) if files else None


class BackupScheduler:
    def __init__(self, db: Path, out: Path, hours: float):
        self.db, self.out, self.hours = db, out, hours
        self.stop = threading.Event()
        self.last_error: str | None = None
        if hours > 0:
            threading.Thread(target=self._loop, name="backup-scheduler", daemon=True).start()

    def _loop(self) -> None:
        while not self.stop.wait(self.hours * 3600):
            try:
                backup_now(self.db, self.out)
                self.last_error = None
            except Exception as error:  # reported on /api/status, never crashes the API
                self.last_error = str(error)[:200]
