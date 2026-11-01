"""Calibrate the LLM critic against human judgement.

1. export: write reports/critic_labels.csv from the last live eval, with an empty human_label column.
2. A person fills human_label with "pass" or "revise" for every row (do not ask a model to do this).
3. score: compare the critic with the human labels (agreement, Cohen's kappa, precision/recall of "revise").

Usage (repo root): PYTHONPATH=services/api services/api/.venv/bin/python services/api/evals/calibrate_critic.py export|score
"""
from __future__ import annotations

import csv
import json
import sys

from app.settings import REPO

LABELS = REPO / "reports" / "critic_labels.csv"
FIELDS = ["customer_id", "segment", "tone", "subject", "body", "critic_verdict", "critic_issues", "human_label", "human_note"]


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    expected = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def export() -> None:
    rows = json.loads((REPO / "reports" / "genai_eval.json").read_text())["rows"]
    with LABELS.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            critic = next((c for c in r["checks"] if c["name"].startswith("Second-pass")), {"passed": None, "detail": ""})
            writer.writerow({"customer_id": r["customer_id"], "segment": r["segment"], "tone": r["tone"], "subject": r["subject"], "body": r["body"],
                             "critic_verdict": "pass" if critic["passed"] else "revise", "critic_issues": critic["detail"], "human_label": "", "human_note": ""})
    print(f"wrote {len(rows)} rows to {LABELS.relative_to(REPO)}; fill human_label with pass or revise")


def score() -> None:
    rows = list(csv.DictReader(LABELS.open(newline="")))
    labelled = [r for r in rows if r["human_label"].strip().lower() in ("pass", "revise")]
    if len(labelled) < len(rows):
        sys.exit(f"{len(rows) - len(labelled)} rows still need a human_label (pass or revise)")
    human = [r["human_label"].strip().lower() for r in labelled]
    critic = [r["critic_verdict"] for r in labelled]
    tp = sum(h == c == "revise" for h, c in zip(human, critic))
    precision = tp / max(critic.count("revise"), 1)
    recall = tp / max(human.count("revise"), 1)
    result = {"drafts": len(labelled), "agreement": round(sum(h == c for h, c in zip(human, critic)) / len(labelled), 3),
              "cohen_kappa": round(cohen_kappa(human, critic), 3), "critic_revise_precision": round(precision, 3), "critic_revise_recall": round(recall, 3),
              "human_revise_rate": round(human.count("revise") / len(human), 3), "critic_revise_rate": round(critic.count("revise") / len(critic), 3)}
    (REPO / "reports" / "critic_calibration.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    {"export": export, "score": score}[sys.argv[1]]()
