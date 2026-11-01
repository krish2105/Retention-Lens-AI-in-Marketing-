"""Restore drill: restore the newest backup into a scratch file and prove it is usable.

Checks the checksum, runs PRAGMA integrity_check, compares row counts per table with the live
database, and times the restore. Writes reports/restore_drill.md as the evidence.

  python3 scripts/restore_drill.py [--db PATH] [--backups DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from backup_db import DEFAULT_DB, REPO, backup


def counts(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}


def drill(db: Path, backups: Path) -> dict:
    fresh = backup(db, backups)
    live = counts(db)
    meta = json.loads(fresh.with_suffix(".json").read_text())
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp:
        restored = Path(tmp) / "restored.sqlite3"
        shutil.copyfile(fresh, restored)
        checksum_ok = hashlib.sha256(restored.read_bytes()).hexdigest() == meta["sha256"]
        with sqlite3.connect(restored) as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        restored_counts = counts(restored)
    seconds = round(time.perf_counter() - started, 3)
    mismatches = {t: (live.get(t), restored_counts.get(t)) for t in set(live) | set(restored_counts) if live.get(t) != restored_counts.get(t)}
    return {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "backup": fresh.name, "bytes": fresh.stat().st_size, "checksum_ok": checksum_ok,
            "integrity": integrity, "restore_seconds": seconds, "tables": restored_counts, "mismatches": mismatches,
            "passed": checksum_ok and integrity == "ok" and not mismatches}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--backups", type=Path, default=REPO / "services" / "api" / ".state" / "backups")
    args = parser.parse_args()
    result = drill(args.db, args.backups)
    lines = ["# Restore drill", "", f"Run {result['at']} by `python3 scripts/restore_drill.py` against the local API database.", "",
             f"- Result: **{'PASSED' if result['passed'] else 'FAILED'}**",
             f"- Backup `{result['backup']}`, {result['bytes']:,} bytes, checksum {'matches' if result['checksum_ok'] else 'DOES NOT match'}",
             f"- `PRAGMA integrity_check`: {result['integrity']}",
             f"- Restore and verification took {result['restore_seconds']} s",
             f"- Row counts matched the live database for all {len(result['tables'])} tables" if not result["mismatches"] else f"- Mismatched tables: {result['mismatches']}",
             "", "| Table | Rows |", "|---|---|", *[f"| {t} | {n:,} |" for t, n in result["tables"].items()], "",
             "Recovery point: the last nightly backup (up to 24 h of decisions could be lost). Recovery time: the restore above plus restarting the API.", ""]
    (REPO / "reports" / "restore_drill.md").write_text("\n".join(lines))
    print(json.dumps({k: result[k] for k in ("passed", "backup", "integrity", "restore_seconds", "mismatches")}))
