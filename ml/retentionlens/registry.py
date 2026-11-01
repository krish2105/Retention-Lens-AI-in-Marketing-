"""Model registry: which model version serves, which were challengers, and the evidence for each.

Written to reports/model_registry.json by `cli r5` and `cli serve`, so the decision trail is versioned in git.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else None


def write_registry(repo: Path) -> dict:
    reports = repo / "reports"
    serving = repo / "artefacts" / "serving" / "summary.json"
    summary = json.loads(serving.read_text()) if serving.exists() else {}
    r5 = json.loads((reports / "r5_results.json").read_text()) if (reports / "r5_results.json").exists() else {}
    registry = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "serving": {
            "name": summary.get("model"),
            "version": "bgnbd-gg-seasonal-v1",
            "scoring_cutoff": summary.get("scoring_cutoff"),
            "data_sha256": summary.get("data_sha256"),
            "season": summary.get("season"),
            "intervals": summary.get("intervals"),
            "evidence": ["reports/model_results.md", "reports/r5_results.md"],
        },
        "models": [
            {"name": "bgnbd_gamma_gamma", "status": "superseded by the seasonal version", "evidence": "reports/model_results.md", "evidence_sha": _sha(reports / "model_results.json")},
            {"name": "bgnbd_gamma_gamma_seasonal", "status": "serving", "evidence": "reports/r5_results.md", "evidence_sha": _sha(reports / "r5_results.json"),
             "dev_result": (r5.get("summary") or {}).get("seasonal_bgnbd_vs_bgnbd")},
            {"name": "lightgbm", "status": "challenger, rejected (lost to BG/NBD on the frozen test)", "evidence": "reports/model_results.md"},
            {"name": "lightgbm_seasonal", "status": "challenger, not adopted (mixed dev results)", "evidence": "reports/r5_results.md",
             "dev_result": (r5.get("summary") or {}).get("seasonal_gbm_vs_gbm")},
            {"name": "ziln_nn", "status": "deep-learning challenger, not adopted (0 of 3 dev wins on lapse PR-AUC)", "evidence": "reports/r5_results.md",
             "dev_result": (r5.get("summary") or {}).get("ziln_vs_bgnbd")},
        ],
    }
    (reports / "model_registry.json").write_text(json.dumps(registry, indent=2) + "\n")
    return registry
