# Case study: RetentionLens

![Case study cover](../apps/web/public/img/aur-26-case-study.webp)

**Predicting which wholesale trade accounts will stop ordering, and building the means to prove whether outreach helps.**
Solo project for MAIB AI 208, AI in Marketing. Live demo: https://retentionlens-demo.vercel.app/case-study/

<!-- Every number below is traced: data_profile.json, artefacts/serving/summary.json, reports/r5_results.json,
     reports/load_test.json, artefacts/serving/lookalikes.json, pytest/playwright collection on 2026-11-01. -->

## Problem

A wholesaler's trade accounts rarely complain before they leave; they just stop reordering. The goal was a
weekly, short list of accounts worth contacting, with reasons a salesperson can repeat, and a built-in way to
measure whether contacting them changes anything.

## Data

UCI Online Retail II (CC BY 4.0): 1,067,371 invoice lines from a UK giftware wholesaler, 2009–2011. Every
problem row (cancellations, duplicates, missing customers, postage lines) is flagged, not silently dropped.

## Approach and results

| Decision | Evidence |
|---|---|
| Fix the evaluation before modelling: rolling time cutoffs, a frozen test scored once | `reports/model_results.md` |
| Serve the simpler model: LightGBM did not beat BG/NBD on any of 4 cutoffs (on the test, 0.819 vs 0.820: a tie) | Frozen test, 5,224 customers: lapse PR-AUC 0.820, Brier 0.186, value Gini 0.825 |
| Add seasonality: a multiplier from the same window last year | Dev cutoffs: mean absolute total-spend bias 32.9% → 16.8% (49% lower); won Brier and MAE on 3 of 3 |
| Show uncertainty: 80% split-conformal value ranges | Coverage 79.5%, 82.2%, 82.4% on the three dev cutoffs; 74.2% on the peak window (post hoc), below target |
| Test a deep-learning challenger honestly: ZILN network | 0 of 3 dev wins on lapse PR-AUC; not adopted; two dev-informed fixes disclosed |
| Find likely high-value newcomers | Lookalike model, time-based split: AUC 0.821 on 1,285 later customers |
| Measure outreach causally | Weekly queue holds out a random 20%; contact vs holdout reorder rates with a 95% CI |

## Product

Self-serve CSV/XLSX upload with column mapping and a row-level check report; a background scoring job;
the weekly queue; AI-drafted check-ins from a local open model with deterministic checks, a second-pass critic,
a UK PECR consent gate and no send path; workspaces with owner/reviewer/viewer roles, export and deletion.

## Engineering

- 61 ML tests, 60 API tests (two-tenant isolation, roles, jobs, billing signatures, 23 OWASP LLM red-team cases),
  52 static browser tests (every route, WCAG 2.2 AA in light and dark, 375 px, Arabic right-to-left) and a live
  upload-to-approval browser flow.
- Load test: 10,261 requests from 20 simulated reviewers in 30 s, 0 errors, p95 270.9 ms. The first run caught
  the weekly queue writing to SQLite on every read (p95 1,045 ms); fixed.
- Scoring 114,886 synthetic invoice lines took 9.1 s. Restore drill passed.

## What surprised me

1. Gradient boosting never beat the simple probabilistic model (0 of 4 cutoffs); on the frozen test they tied.
2. Seasonality, not model class, was the biggest source of error.
3. The neural network failed for data reasons (constant features, extrapolated calendar features), not
   architecture reasons.
4. A load test, not a code review, found the worst latency bug.

## Limitations

- One company's data from 2009–2011.
- Customer interviews, usability sessions and a pilot have **not** happened yet. Pricing is a hypothesis.
- The AI critic is not calibrated against human labels yet, and only 1 of 16 live drafts passed every check.
- Value ranges are too narrow before Christmas (74.2% coverage on the peak window against an 80% target).
- Hosting (Render/Supabase) and Stripe test mode are prepared but need the owner's accounts.

## Pilot results

None yet. This section stays empty until a real pilot reports contacted vs held-out reorder rates.
