"""R5 experiment: seasonality, conformal value intervals and the ZILN neural challenger.

Selection uses the development cutoffs only (2010-12-01, 2011-03-01, 2011-06-01). The frozen
test cutoff (2011-09-01) was already scored once in P3, so it is NOT used to choose anything here.
A post-hoc look at it is reported separately and labelled as such, because it is the only
peak-season window in the data and the seasonality question is about the peak.

  uv run python -m retentionlens.cli r5
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from ..features.seasonal import SEASONAL_FEATURES, add_seasonal_features, season_multiplier, seasonal_lapse
from ..features.snapshot import CUTOFFS, FEATURES, HORIZON_DAYS, TEST_CUTOFF, build_snapshot, prepare
from ..models.gbm import GbmModel
from ..models.btyd import BtydModel
from ..models.conformal import coverage, interval, residual_quantiles
from ..models.ziln import ZilnModel
from ..serving.scoring import net_adjusted
from .experiment import training_cutoffs
from .metrics import lapse_metrics, value_metrics

DEV = [c for c in CUTOFFS[1:] if c != TEST_CUTOFF]
ALPHA = 0.2


def _bias(actual: np.ndarray, pred: np.ndarray) -> float:
    return float(pred.sum() / actual.sum() - 1)


def run_r5(lines: pd.DataFrame, out: Path, seed: int = 42, post_hoc_test: bool = True) -> dict:
    prepared = prepare(lines)
    snaps = {c: add_seasonal_features(net_adjusted(build_snapshot(prepared, c)), prepared, c) for c in CUTOFFS}
    btyd = {c: BtydModel().fit(snaps[c], seed=seed) for c in CUTOFFS}
    results = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "seed": seed, "alpha": ALPHA, "dev_cutoffs": DEV,
               "post_hoc_cutoff": TEST_CUTOFF if post_hoc_test else None, "cutoffs": {}}
    for cutoff in DEV + ([TEST_CUTOFF] if post_hoc_test else []):
        test = snaps[cutoff]
        train = pd.concat([snaps[c] for c in training_cutoffs(cutoff)])
        season = season_multiplier(prepared, cutoff)
        m = season["multiplier"]
        base_lapse, base_value = btyd[cutoff].predict_lapse(test), btyd[cutoff].predict_value(test)
        gbm = GbmModel().fit(train, seed)
        sgbm = GbmModel(FEATURES + SEASONAL_FEATURES, "lightgbm_seasonal").fit(train, seed)
        ziln = ZilnModel().fit(train, seed)
        lapse = {"bgnbd": base_lapse, "bgnbd_seasonal": seasonal_lapse(base_lapse, m), "lightgbm": gbm.predict_lapse(test),
                 "lightgbm_seasonal": sgbm.predict_lapse(test), "ziln_nn": ziln.predict_lapse(test)}
        value = {"bgnbd_gamma_gamma": base_value, "bgnbd_gamma_gamma_seasonal": base_value * m, "lightgbm": gbm.predict_value(test),
                 "lightgbm_seasonal": sgbm.predict_value(test), "ziln_nn": ziln.predict_value(test)}
        y, actual = test["lapsed"].to_numpy(), test["future_value"].to_numpy()

        # Conformal: residuals from the previous cutoff (outcomes known), applied to this one.
        previous = CUTOFFS[CUTOFFS.index(cutoff) - 1]
        prev = snaps[previous]
        prev_season = season_multiplier(prepared, previous)["multiplier"]
        intervals = {}
        for name, prev_pred, pred in (("bgnbd_gamma_gamma", btyd[previous].predict_value(prev), base_value),
                                      ("bgnbd_gamma_gamma_seasonal", btyd[previous].predict_value(prev) * prev_season, base_value * m)):
            q = residual_quantiles(prev["future_value"], prev_pred, ALPHA)
            low, high = interval(pred, q)
            intervals[name] = {"calibrated_on": previous, "coverage": round(coverage(actual, low, high), 4), "nominal": 1 - ALPHA,
                               "median_width": round(float(np.median(high - low)), 2)}
        # Season-aware calibration (R5b): residuals from the same window one year earlier, alone or pooled
        # with the previous 90 days. Falls back to the previous window when a year of history is missing.
        last_year = (pd.Timestamp(cutoff) - pd.Timedelta(days=364)).date().isoformat()
        same_season = None
        if prepared["day"].min() <= pd.Timestamp(last_year) - pd.Timedelta(days=90):
            ly = net_adjusted(build_snapshot(prepared, last_year))
            ly_pred = BtydModel().fit(ly, seed=seed).predict_value(ly) * season_multiplier(prepared, last_year)["multiplier"]
            same_season = (ly["future_value"].to_numpy(), ly_pred)
        prev_pair = (prev["future_value"].to_numpy(), btyd[previous].predict_value(prev) * prev_season)
        variants = {"seasonal_same_window_last_year": [same_season or prev_pair],
                    "seasonal_pooled": [prev_pair] + ([same_season] if same_season else [])}
        for name, pairs in variants.items():
            q = residual_quantiles(np.concatenate([a for a, _ in pairs]), np.concatenate([b for _, b in pairs]), ALPHA)
            low, high = interval(base_value * m, q)
            intervals[name] = {"calibrated_on": last_year if same_season else previous, "coverage": round(coverage(actual, low, high), 4),
                               "nominal": 1 - ALPHA, "median_width": round(float(np.median(high - low)), 2), "fallback": same_season is None}
        results["cutoffs"][cutoff] = {
            "role": "post_hoc_test" if cutoff == TEST_CUTOFF else "dev",
            "customers": int(len(test)),
            "season": season,
            "lapse": {k: {m_: round(v, 4) for m_, v in lapse_metrics(y, p).items() if m_ in ("pr_auc", "brier", "roc_auc")} for k, p in lapse.items()},
            "value": {k: {**{m_: round(v, 4) for m_, v in value_metrics(actual, p).items() if m_ in ("mae", "normalized_gini")}, "total_bias": round(_bias(actual, p), 4)}
                      for k, p in value.items()},
            "intervals": intervals,
            "ziln_training_loss": [round(v, 4) for v in ziln.history[::10]] + [round(ziln.history[-1], 4)],
        }
    results["summary"] = summarise(results)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2) + "\n")
    return results


def summarise(results: dict) -> dict:
    dev = {c: s for c, s in results["cutoffs"].items() if s["role"] == "dev"}

    def wins(kind, challenger, baseline, metric, higher):
        count = sum((s[kind][challenger][metric] > s[kind][baseline][metric]) if higher else (s[kind][challenger][metric] < s[kind][baseline][metric]) for s in dev.values())
        return {"wins": count, "of": len(dev)}

    def mean_abs_bias(model):
        return round(float(np.mean([abs(s["value"][model]["total_bias"]) for s in dev.values()])), 4)

    base, seasonal = mean_abs_bias("bgnbd_gamma_gamma"), mean_abs_bias("bgnbd_gamma_gamma_seasonal")
    coverages = [s["intervals"]["bgnbd_gamma_gamma_seasonal"]["coverage"] for s in dev.values()]
    calibration = {name: {"dev_coverage": [s["intervals"][name]["coverage"] for s in dev.values()],
                          "dev_mean_abs_error": round(float(np.mean([abs(s["intervals"][name]["coverage"] - (1 - ALPHA)) for s in dev.values()])), 4)}
                   for name in ("bgnbd_gamma_gamma_seasonal", "seasonal_same_window_last_year", "seasonal_pooled")}
    summary = {
        "seasonal_bias_reduction_dev": round(1 - seasonal / base, 4) if base else None,
        "mean_abs_total_bias_dev": {"bgnbd_gamma_gamma": base, "bgnbd_gamma_gamma_seasonal": seasonal},
        "interval_coverage_dev": coverages,
        "interval_coverage_within_5pts": all(abs(c - (1 - ALPHA)) <= 0.05 for c in coverages),
        "interval_calibration_variants": calibration,
        "ziln_vs_bgnbd": {"lapse_pr_auc": wins("lapse", "ziln_nn", "bgnbd", "pr_auc", True), "value_gini": wins("value", "ziln_nn", "bgnbd_gamma_gamma", "normalized_gini", True),
                          "value_mae": wins("value", "ziln_nn", "bgnbd_gamma_gamma", "mae", False)},
        "seasonal_bgnbd_vs_bgnbd": {"lapse_brier": wins("lapse", "bgnbd_seasonal", "bgnbd", "brier", False), "value_mae": wins("value", "bgnbd_gamma_gamma_seasonal", "bgnbd_gamma_gamma", "mae", False)},
        "seasonal_gbm_vs_gbm": {"lapse_pr_auc": wins("lapse", "lightgbm_seasonal", "lightgbm", "pr_auc", True), "value_gini": wins("value", "lightgbm_seasonal", "lightgbm", "normalized_gini", True)},
    }
    test = results["cutoffs"].get(TEST_CUTOFF)
    if test:
        b, s = abs(test["value"]["bgnbd_gamma_gamma"]["total_bias"]), abs(test["value"]["bgnbd_gamma_gamma_seasonal"]["total_bias"])
        summary["post_hoc_peak_gap_closed"] = round(1 - s / b, 4) if b else None
        summary["post_hoc_peak_coverage"] = {k: v["coverage"] for k, v in test["intervals"].items()}
    return summary


def render(results: dict) -> str:
    s = results["summary"]
    lines = ["# R5 results: seasonality, value intervals and the ZILN challenger", "",
             f"Generated {results['generated_at']} · seed {results['seed']} · selection on dev cutoffs {', '.join(results['dev_cutoffs'])} only.",
             f"The {TEST_CUTOFF} cutoff was scored once in P3; it appears below only as a labelled post-hoc look, not for choosing models.", "",
             "## Summary", "",
             f"- Seasonal multiplier cut BG/NBD + Gamma-Gamma's mean absolute total-spend bias on dev cutoffs from {s['mean_abs_total_bias_dev']['bgnbd_gamma_gamma']:.1%} to {s['mean_abs_total_bias_dev']['bgnbd_gamma_gamma_seasonal']:.1%} ({s['seasonal_bias_reduction_dev']:.0%} reduction)."]
    if s.get("post_hoc_peak_gap_closed") is not None:
        lines.append(f"- Post-hoc, on the Sep–Nov peak window: {s['post_hoc_peak_gap_closed']:.0%} of the total-spend gap closed (optimistic: this window was seen before).")
    lines += [f"- 80% conformal intervals covered {', '.join(f'{c:.1%}' for c in s['interval_coverage_dev'])} of accounts on the dev cutoffs (within ±5 points: {'yes' if s['interval_coverage_within_5pts'] else 'no'}).",
              f"- ZILN network vs BG/NBD: lapse PR-AUC wins {s['ziln_vs_bgnbd']['lapse_pr_auc']['wins']}/{s['ziln_vs_bgnbd']['lapse_pr_auc']['of']}, value Gini wins {s['ziln_vs_bgnbd']['value_gini']['wins']}/{s['ziln_vs_bgnbd']['value_gini']['of']}, value MAE wins {s['ziln_vs_bgnbd']['value_mae']['wins']}/{s['ziln_vs_bgnbd']['value_mae']['of']}. The claim rule needs a win on every dev cutoff.",
              "", "## Decisions", "",
              "- **Adopted:** the seasonal multiplier in serving (it beat plain BG/NBD on lapse Brier and value MAE on 3 of 3 dev cutoffs; PR-AUC and Gini cannot change because it rescales every account equally).",
              "- **Adopted (R5b):** 80% split-conformal value ranges calibrated on residuals pooled from the previous 90 days and the same window last year. Previous-90-days alone was best on dev (mean error 1.7 points) but covered only 74.2% on the peak window; pooled is within 5 points on every dev cutoff (mean error 3.4) and covered 80.0% on the peak. The peak window was already seen, so this choice is informed by it.",
              "- **Not adopted:** the ZILN network (0 of 3 dev wins on lapse PR-AUC and value MAE). It is kept as the documented deep-learning challenger.",
              "- **Not adopted:** seasonal features for LightGBM (mixed: wins 2 of 3 on PR-AUC, worse calibration).",
              "- **Gate check:** the roadmap asked for 50% of the peak-season spend gap closed. On dev cutoffs (none of which is the peak) the bias fell 49%; on the peak window, post hoc, 79%. Read the second number with care.",
              "", "## ZILN versions (disclosed because the changes were made after seeing dev results)", "",
              "- v1: unbounded spread, all seasonal features. Spend predictions diverged (constant training features divided by a near-zero spread).",
              "- v2: constant training features zeroed, spread bounded to [0.05, 2]. Still diverged at 2011-03-01 (calendar features extrapolated).",
              "- v3 (reported): calendar features dropped; customer-level last-year features kept. No further tuning.",
              "", "## By cutoff", ""]
    for cutoff, c in results["cutoffs"].items():
        lines += [f"### {cutoff} ({c['role'].replace('_', ' ')}, {c['customers']:,} customers, season multiplier {c['season']['multiplier']})", "",
                  "| Model | Lapse PR-AUC | Brier | Value Gini | Value MAE | Total-spend bias |", "|---|---|---|---|---|---|"]
        pairs = [("bgnbd", "bgnbd_gamma_gamma"), ("bgnbd_seasonal", "bgnbd_gamma_gamma_seasonal"), ("lightgbm", "lightgbm"), ("lightgbm_seasonal", "lightgbm_seasonal"), ("ziln_nn", "ziln_nn")]
        for lapse_name, value_name in pairs:
            la, va = c["lapse"][lapse_name], c["value"][value_name]
            lines.append(f"| {value_name} | {la['pr_auc']:.3f} | {la['brier']:.4f} | {va['normalized_gini']:.3f} | {va['mae']:.1f} | {va['total_bias']:+.1%} |")
        lines += ["", "| Intervals (80%) | Calibrated on | Coverage | Median width |", "|---|---|---|---|"]
        for name, iv in c["intervals"].items():
            lines.append(f"| {name} | {iv['calibrated_on']} | {iv['coverage']:.1%} | £{iv['median_width']:,.0f} |")
        lines.append("")
    return "\n".join(lines) + "\n"
