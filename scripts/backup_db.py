"""Online backup of the API's SQLite database (safe while the API runs), with a checksum.

  python3 scripts/backup_db.py [--db PATH] [--out DIR] [--keep 14]

Schedule nightly (cron or the host's scheduler). On Postgres/Supabase use their point-in-time
backups instead; the restore drill below is the part that must still be practised.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO / "services" / "api" / ".state" / "retentionlens.sqlite3"


def backup(db: Path, out: Path, keep: int = 14) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = out / f"retentionlens-{stamp}.sqlite3"
    with sqlite3.connect(db) as source, sqlite3.connect(target) as dest:
        source.backup(dest)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (target.with_suffix(".json")).write_text(json.dumps({"file": target.name, "sha256": digest, "source": str(db), "created_at": stamp}, indent=2) + "\n")
    for old in sorted(out.glob("retentionlens-*.sqlite3"))[:-keep]:
        old.unlink()
        old.with_suffix(".json").unlink(missing_ok=True)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=REPO / "services" / "api" / ".state" / "backups")
    parser.add_argument("--keep", type=int, default=14)
    args = parser.parse_args()
    print(backup(args.db, args.out, args.keep))
