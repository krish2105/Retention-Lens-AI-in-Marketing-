"""Live evaluation of outreach drafting against the local Ollama model.

Usage (from repo root): PYTHONPATH=services/api services/api/.venv/bin/python services/api/evals/run_eval.py
Writes reports/genai_eval.json and reports/genai_eval.md. Thresholds are not invented: this run is the baseline.
"""
from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

from app.genai.drafting import Facts, OllamaClient, generate
from app.settings import REPO, load_settings
from app.store import ServingStore

PER_SEGMENT = 2
TONES = ["warm", "brief", "seasonal"]


def main() -> None:
    settings = load_settings()
    store = ServingStore(settings.serving_dir)
    plays = {r["segment"]: r["play"] for r in store.get("segments")["segments"]}
    by_segment = defaultdict(list)
    for account in store.get("accounts"):
        if len(by_segment[account.get("segment")]) < PER_SEGMENT and account.get("top_products"):
            by_segment[account.get("segment")].append(account)
    client = OllamaClient(settings.ollama_url, settings.ollama_model)
    rows = []
    for i, account in enumerate(a for group in by_segment.values() for a in group):
        facts = Facts.from_account(account, plays.get(account.get("segment"), ""))
        result = generate(facts, TONES[i % len(TONES)], client)
        rows.append({"customer_id": account["customer_id"], "segment": facts.segment, "tone": TONES[i % len(TONES)], "source": result["source"],
                     "passed": result["passed"], "seconds": result["seconds"], "checks": result["checks"], "subject": result["subject"], "body": result["body"]})
        print(account["customer_id"], facts.segment, result["source"], "PASS" if result["passed"] else "FAIL", result["seconds"], flush=True)
    check_pass = Counter()
    for row in rows:
        for c in row["checks"]:
            check_pass[c["name"]] += c["passed"]
    model_rows = [r for r in rows if r["source"] == "model"]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": settings.ollama_model,
        "drafts": len(rows),
        "model_drafts": len(model_rows),
        "all_checks_passed": sum(r["passed"] for r in rows),
        "per_check_pass": {k: f"{v}/{len(rows)}" for k, v in check_pass.items()},
        "median_seconds": statistics.median(r["seconds"] for r in rows) if rows else None,
        "rows": rows,
    }
    (REPO / "reports" / "genai_eval.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [
        "# Outreach drafting evaluation (live, local model)", "",
        f"Model `{summary['model']}` via Ollama · {summary['generated_at']} · {summary['drafts']} drafts across segments and tones.",
        "This is the first baseline run; it sets the reference, it is not compared with an invented target.", "",
        f"- Drafts passing every check: **{summary['all_checks_passed']} of {summary['drafts']}**",
        f"- Median time per draft (draft + second-pass review): {summary['median_seconds']} s", "",
        "| Check | Passed |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in summary["per_check_pass"].items()], "",
        "Deterministic red-team cases (invented numbers, discounts, pressure, contact data, injection text, consent rules, idempotency) are unit tests in `services/api/tests/test_outreach.py`.", "",
        "## Example drafts", "",
    ]
    for r in rows[:3]:
        lines += [f"**{r['segment']} · {r['tone']} · {'pass' if r['passed'] else 'fail'}**", "", f"> Subject: {r['subject']}", ">", *[f"> {line}" for line in r["body"].splitlines()], ""]
    (REPO / "reports" / "genai_eval.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
