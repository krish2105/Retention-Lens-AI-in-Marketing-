"""Command line entry point: `uv run python -m retentionlens.cli data`."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data.clean import clean_transactions
from .data.download import CITATION, LICENCE, MANIFEST_NAME, download_dataset
from .data.load import load_or_cache
from .data.profile import build_profile, render_markdown, upsert_register

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


def main() -> None:
    parser = argparse.ArgumentParser(prog="retentionlens")
    parser.add_argument("command", choices=["data"])
    args = parser.parse_args()
    if args.command == "data":
        profile = run_data(REPO)
        print(json.dumps({k: profile[k] for k in ("rows", "date_min", "date_max", "customers", "customer_model_rows")}))


if __name__ == "__main__":
    main()
