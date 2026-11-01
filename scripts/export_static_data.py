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
# Plans and a status snapshot for the demo's pricing, billing and status pages.
import sys  # noqa: E402

sys.path.insert(0, str(REPO / "services" / "api"))
from app.billing import PLANS, STATUS  # noqa: E402
from app.ops import SLO  # noqa: E402

(DST / "plans.json").write_text(json.dumps({"plans": PLANS, "status": STATUS, "currency": "GBP"}, indent=2) + "\n")
summary = json.loads((SRC / "summary.json").read_text())
(DST / "status.json").write_text(json.dumps({
    "status": "static demo", "static": True, "slo": SLO, "uptime_seconds": None, "worst_read_p95_ms": None, "auth_mode": "off", "version": "0.4.0",
    "components": {"static_snapshot": {"ok": True, "detail": f"Exported {summary['generated_at'][:10]}"},
                   "api": {"ok": False, "detail": "The public demo has no live API; run it locally or on the hosted server"}},
}, indent=2) + "\n")
(DST / "manifest.json").write_text(json.dumps({"exported_from": summary["generated_at"], "data_sha256": summary["data_sha256"], "files": FILES}, indent=2) + "\n")
print(f"exported {len(FILES)} files to {DST.relative_to(REPO)}")
