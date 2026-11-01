"""Copy the serving JSON into the web app for the public, read-only static demo.

Run after `uv run python -m retentionlens.cli serve` (from ml/):
    python3 scripts/export_static_data.py
The files are derived from UCI Online Retail II (CC BY 4.0); attribution is shown on every page.
"""
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "artefacts" / "serving"
DST = REPO / "apps" / "web" / "public" / "data"
FILES = ["summary", "accounts", "timeline", "cohorts", "model_eval", "data_profile", "sources", "segments", "galaxy", "lookalikes", "signals", "product_lab"]

DST.mkdir(parents=True, exist_ok=True)
for name in FILES:
    shutil.copyfile(SRC / f"{name}.json", DST / f"{name}.json")
summary = json.loads((SRC / "summary.json").read_text())
(DST / "manifest.json").write_text(json.dumps({"exported_from": summary["generated_at"], "data_sha256": summary["data_sha256"], "files": FILES}, indent=2) + "\n")
print(f"exported {len(FILES)} files to {DST.relative_to(REPO)}")
