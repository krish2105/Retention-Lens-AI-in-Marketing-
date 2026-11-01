"""Postgres restore drill: pg_dump one schema, restore it into a fresh database, compare row counts.

  python3 scripts/restore_drill_postgres.py --url postgresql://postgres@127.0.0.1:54329/postgres --schema seeded

Needs pg_dump, pg_restore and psql on PATH. Writes reports/restore_drill_postgres.md.
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def psql(url: str, sql: str) -> str:
    return subprocess.run(["psql", url, "-tA", "-v", "ON_ERROR_STOP=1", "-c", sql], check=True, capture_output=True, text=True).stdout.strip()


def counts(url: str, schema: str) -> dict[str, int]:
    tables = psql(url, f"select tablename from pg_tables where schemaname='{schema}' order by 1").splitlines()
    return {t: int(psql(url, f'select count(*) from "{schema}"."{t}"')) for t in tables}


def main(url: str, schema: str, label: str) -> dict:
    live = counts(url, schema)
    target_db = f"drill_{int(time.time())}"
    base = url.rsplit("/", 1)[0]
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp:
        dump = Path(tmp) / "dump.pgc"
        subprocess.run(["pg_dump", url, "-n", schema, "-Fc", "-f", str(dump)], check=True)
        size = dump.stat().st_size
        psql(url, f"create database {target_db}")
        try:
            subprocess.run(["pg_restore", "-d", f"{base}/{target_db}", str(dump)], check=True)
            restored = counts(f"{base}/{target_db}", schema)
        finally:
            psql(url, f"drop database if exists {target_db}")
    seconds = round(time.perf_counter() - started, 2)
    mismatches = {t: (live.get(t), restored.get(t)) for t in set(live) | set(restored) if live.get(t) != restored.get(t)}
    passed = not mismatches and bool(live)
    lines = ["# Restore drill (Postgres)", "", f"Run {datetime.now(timezone.utc).isoformat(timespec='seconds')} by `scripts/restore_drill_postgres.py` against {label}.", "",
             f"- Result: **{'PASSED' if passed else 'FAILED'}**",
             f"- `pg_dump -Fc` of schema `{schema}`: {size:,} bytes; restored into a fresh database with `pg_restore`, then dropped",
             f"- Dump, restore and verification took {seconds} s",
             "- Row counts matched for every table" if not mismatches else f"- Mismatches: {mismatches}",
             "", "| Table | Rows |", "|---|---|", *[f"| {t} | {n:,} |" for t, n in restored.items()], ""]
    (REPO / "reports" / "restore_drill_postgres.md").write_text("\n".join(lines))
    return {"passed": passed, "seconds": seconds, "mismatches": mismatches}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--schema", default="retentionlens")
    parser.add_argument("--label", default="a local Postgres database")
    args = parser.parse_args()
    print(main(args.url, args.schema, args.label))
