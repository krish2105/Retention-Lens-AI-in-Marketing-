"""Command line entry point: `uv run python -m retentionlens.cli data`."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .data.clean import clean_transactions
from .data.download import CITATION, LICENCE, MANIFEST_NAME, download_dataset
from .data.load import load_or_cache
from .data.profile import build_profile, render_markdown, upsert_register
from .eval.experiment import run_experiment
from .eval.report import render_report

REPO = Path(__file__).resolve().parents[2]


def run_data(repo: Path) -> dict:
    raw, interim, reports = repo / "data" / "raw", repo / "data" / "interim", repo / "reports"
    result = download_dataset(raw)
    df = load_or_cache(result.xlsx_path, interim / "transactions_raw.parquet")
    cleaned = clean_transactions(df)
    cleaned.lines.to_parquet(interim / "transactions_flagged.parquet", index=False)
    profile = build_profile(cleaned.lines, cleaned.issues)
    manifest = json.loads((raw / MANIFEST_NAME).read_text())
    reports.mkdir(exist_ok=True)
    (reports / "data_profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    (reports / "data_profile.md").write_text(render_markdown(profile, manifest))
    upsert_register(
        repo / "project" / "DATA_SOURCE_REGISTER.csv",
        {
            "name": "online_retail_ii",
            "url": manifest["url"],
            "version": "UCI id 502 (donated 2019-09-20)",
            "access_date": manifest["accessed_at"][:10],
            "license": LICENCE,
            "sha256": manifest["zip_sha256"],
            "allowed_use": "Coursework and public portfolio with attribution; raw file not redistributed in repo",
            "notes": CITATION,
        },
    )
    return profile


def run_models(repo: Path, include_test: bool) -> dict:
    flagged = repo / "data" / "interim" / "transactions_flagged.parquet"
    if not flagged.exists():
        raise SystemExit("No flagged data found. Run `python -m retentionlens.cli data` first.")
    manifest = json.loads((repo / "data" / "raw" / MANIFEST_NAME).read_text())
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ("-test" if include_test else "-dev")
    results = run_experiment(
        pd.read_parquet(flagged),
        repo / "artefacts" / "runs" / run_id,
        include_test=include_test,
        data_sha256=manifest["zip_sha256"],
    )
    stem = "model_results" if include_test else "model_results_dev"
    reports = repo / "reports"
    reports.mkdir(exist_ok=True)
    (reports / f"{stem}.md").write_text(render_report(results))
    summary = {k: v for k, v in results.items() if k not in ("cutoffs",)}
    summary["cutoffs"] = {
        c: {k: s[k] for k in ("role", "train_cutoffs", "n_train_rows", "n_customers", "lapse", "value", "reliability")}
        for c, s in results["cutoffs"].items()
    }
    (reports / f"{stem}.json").write_text(json.dumps(summary, indent=2) + "\n")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(prog="retentionlens")
    parser.add_argument("command", choices=["data", "models"])
    parser.add_argument("--include-test", action="store_true", help="also score the frozen test cutoff (run once)")
    args = parser.parse_args()
    if args.command == "data":
        profile = run_data(REPO)
        print(json.dumps({k: profile[k] for k in ("rows", "date_min", "date_max", "customers", "customer_model_rows")}))
    elif args.command == "models":
        results = run_models(REPO, args.include_test)
        print(json.dumps({"run_id": results["run_id"], "comparison": results["comparison"]}))


if __name__ == "__main__":
    main()
