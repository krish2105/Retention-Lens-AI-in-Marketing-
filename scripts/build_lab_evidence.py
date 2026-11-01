"""Write labs/week-XX/EVIDENCE.md: tables of real numbers from the run files, for the student to cite.

These are evidence tables, not lab reports. The interpretation and write-up are the student's own work.
  python3 scripts/build_lab_evidence.py   (after `cli models`, `cli serve`, `cli r5`)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SERVING = REPO / "artefacts" / "serving"
REPORTS = REPO / "reports"


def load(path: Path):
    return json.loads(path.read_text())


def table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def header(title: str, sources: list[str]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (f"# Evidence pack: {title}\n\nGenerated {stamp} by `scripts/build_lab_evidence.py` from: "
            + ", ".join(f"`{s}`" for s in sources)
            + ".\nNumbers only. The question, interpretation, limitations and write-up are yours to write.\n")


def week02() -> str:
    p = load(REPORTS / "data_profile.json")
    issues = p["issues"]
    return header("Lab 1 (week 2): markets and data", ["reports/data_profile.json"]) + "\n" + table(
        ["Measure", "Value"],
        [["Invoice lines", f"{p['rows']:,}"], ["Date range", f"{p['date_min']} to {p['date_max']}"], ["Invoices", f"{p['invoices']:,}"],
         ["Customers with an ID", f"{p['customers']:,}"], ["Countries", p["countries"]], ["Lines usable for customer models", f"{p['customer_model_rows']:,}"],
         *[[k.replace("is_", "").replace("_", " "), f"{v:,}"] for k, v in issues.items() if isinstance(v, int)]]) + "\n"


def model_rows(results: dict, kind: str, metrics: list[str]) -> list[list]:
    rows = []
    for cutoff, c in results["cutoffs"].items():
        for model, m in c[kind].items():
            rows.append([cutoff, c["role"], model, *[f"{m[k]:.4f}" if isinstance(m[k], float) else m[k] for k in metrics]])
    return rows


def week04() -> str:
    r = load(REPORTS / "model_results.json")
    r5 = load(REPORTS / "r5_results.json")
    text = header("Lab 2 (week 4): customer lifetime value", ["reports/model_results.json", "reports/r5_results.json"])
    text += "\n## 90-day value by cutoff (P2 protocol)\n\n" + table(["Cutoff", "Role", "Model", "Normalised Gini", "MAE (£)", "Total actual", "Total predicted"],
                                                                     model_rows(r, "value", ["normalized_gini", "mae", "total_actual", "total_pred"]))
    text += "\n\n## R5: seasonality and value ranges (dev cutoffs select; 2011-09-01 is post hoc)\n\n" + table(
        ["Cutoff", "Model", "Total-spend bias", "MAE (£)"],
        [[c, m, f"{v['total_bias']:+.1%}", f"{v['mae']:.1f}"] for c, s in r5["cutoffs"].items() for m, v in s["value"].items()])
    text += "\n\n" + table(["Cutoff", "Interval calibration", "Coverage (target 80%)", "Median width (£)"],
                           [[c, n, f"{v['coverage']:.1%}", f"{v['median_width']:,.0f}"] for c, s in r5["cutoffs"].items() for n, v in s["intervals"].items()])
    return text + "\n"


def week06() -> str:
    r = load(REPORTS / "model_results.json")
    text = header("Lab 3 (week 6): churn analysis", ["reports/model_results.json"])
    text += "\n## Lapse (no order in 90 days)\n\n" + table(["Cutoff", "Role", "Model", "PR-AUC", "ROC-AUC", "Brier", "Top-10% lift"],
                                                         model_rows(r, "lapse", ["pr_auc", "roc_auc", "brier", "top_lift"]))
    text += "\n\n## Does the challenger win? (claim rule: 3 of 4 cutoffs)\n\n" + table(
        ["Comparison", "Baseline", "LightGBM wins"],
        [[metric, base, f"{w['wins']} of {w['of']}"] for metric, d in r["comparison"].items() for base, w in d.items()])
    return text + "\n"


def week08() -> str:
    p = load(SERVING / "product_lab.json")
    text = header("Lab 4 (week 8): brand and pricing", ["artefacts/serving/product_lab.json"])
    text += "\n## Product loyalty (top 10)\n\n" + table(["Product", "Buyers", "Repeat rate"], [[x["product"], x["buyers"], f"{x['repeat_rate']:.1%}"] for x in p["loyalty"][:10]])
    text += "\n\n## Price elasticity estimates (read the caveats)\n\n" + table(["Product", "Elasticity", "95% CI", "Weeks", "R²"],
        [[x["product"], f"{x['elasticity']:.2f}", f"{x['ci_low']:.2f} to {x['ci_high']:.2f}", x["weeks"], f"{x['r2']:.2f}"] for x in p["elasticities"][:10]])
    text += "\n\nCaveats recorded with the run:\n" + "\n".join(f"- {c}" for c in p["caveats"])
    return text + "\n"


def size(value):
    return len(value) if isinstance(value, (list, dict)) else value


def week10() -> str:
    s = load(SERVING / "signals.json")
    c, n, soc = s["competitor"], s["network"], s["social"]
    text = header("Lab 5 (week 10): competitive intelligence and scraping", ["artefacts/serving/signals.json"])
    text += "\n" + table(["Measure", "Value"], [
        ["Practice site", c["site"]], ["Pages fetched", size(c["pages"])], ["Items collected", size(c["items"])],
        ["Co-purchase network nodes / edges", f"{size(n['nodes'])} / {size(n['edges'])}"], ["Communities, modularity", f"{size(n['communities'])}, {n['modularity']}"],
        ["Social posts (SYNTHETIC)", size(soc["posts"])], ["Injection posts planted / flagged", f"{size(soc['injection_posts'])} / {size(soc['injection_flagged'])}"]])
    if isinstance(c.get("price_by_rating"), list) and c["price_by_rating"] and isinstance(c["price_by_rating"][0], dict):
        text += "\n\n## Price by rating (practice site)\n\n" + table(list(c["price_by_rating"][0].keys()), [list(r.values()) for r in c["price_by_rating"]])
    return text + "\n"


if __name__ == "__main__":
    for folder, build in {"week-02-market-data": week02, "week-04-clv": week04, "week-06-churn": week06,
                          "week-08-brand-pricing": week08, "week-10-competitive-intel": week10}.items():
        (REPO / "labs" / folder / "EVIDENCE.md").write_text(build())
        print("wrote", f"labs/{folder}/EVIDENCE.md")
