# Coursework review against the assessment (R7)

Reviewed 2026-11-01 against `docs/ASSESSMENT.md` (extracted from the unit outline). **This is a review, not
graded work.** The lab reports, presentation narrative, report text and viva answers must be written by the
student. Each row says what evidence exists in the repository and what is still the student's to do.

## Assessment components

| Component (weight) | Evidence in the repo | Status | What the student still writes or does |
|---|---|---|---|
| Exercises (30%) | Weekly topics mapped on `/evidence`; code per week | Not started as a deliverable | An exercises log: one entry per session (date, exercise, what you did, link to evidence). Template below |
| Labs (30%), weeks 2/4/6/8/10 | `labs/week-*/README.md` scaffolds (134–143 words each); every lab's data, code and results exist | Scaffolds only | Five lab reports in your own words: question, method, result, limitation, link to the run file |
| Presentation (10%), week 6 | `submissions/RetentionLens_Presentation.pptx` (14 slides, built from results) | Slides exist | Your narrative and speaker notes; a rehearsed live demo; a recorded 3-minute video |
| Final project (30%) | `submissions/RetentionLens_Project_Report.pdf` v1; product, tests, R5 results, ops evidence | v1 exists; v2 needs primary research | Report v2 sections that need you: interviews (R1), usability (R2), pilot (R6), reflection, contribution diary |

## Learning outcomes: is there primary evidence?

| Outcome | Experiment or artefact | Primary research? | Gap |
|---|---|---|---|
| A Research, prediction, trends | Rolling-cutoff evaluation, frozen test, R5 seasonality | Secondary data only | Interviews would add the "marketing research" half |
| B Traditional + web + social sources | UCI invoices, Wikimedia pageviews (CC0), co-purchase network, synthetic labelled social | Social data is synthetic, labelled | Coordinator ruling on synthetic social data |
| C CLV, churn, retention, acquisition | BG/NBD + Gamma-Gamma, conformal ranges, lookalikes (AUC 0.821), holdout queue | Holdout design ready; no pilot result | A pilot outcome, even small and inconclusive, honestly reported |
| D GenAI decisions | Grounded drafting, checker, critic, PECR gate, OWASP red team | Critic calibration needs human labels | Label 16+ drafts in `reports/critic_labels.csv` or in the Outreach studio (kappa target 0.6) |

## Rubric risks found in review

1. **"Group" wording.** Presentation and final project are group-assessed in the outline; this is a solo
   project. Get the coordinator's ruling in writing (the email draft exists) and file it in `project/DECISIONS.md`.
2. **"Deep learning".** The ZILN network now exists and is evaluated honestly (it loses: `reports/r5_results.md`).
   Ask whether a documented, losing deep-learning challenger satisfies the wording.
3. **Frozen test reuse.** R5 used dev cutoffs for every choice; the 2011-09-01 post-hoc numbers are labelled.
   Keep that distinction in the report, since examiners will look for it.
4. **Synthetic data.** Every synthetic file is labelled SYNTHETIC (`data/samples/`, social posts). Keep the label
   on every figure that uses it.
5. **Claims vs evidence.** The landing page says "pilot stage, no paying customers yet". Keep the report the same.

## Viva questions: where your evidence is (answers are yours to write)

| # | Question | Evidence to cite |
|---|---|---|
| 1 | Which outcome does the central experiment prove? | `reports/model_results.md`, `reports/r5_results.md` (C, A) |
| 2 | Why is the simple baseline sufficient or not? | Logistic RFM ≈ BG/NBD on PR-AUC; LightGBM lost; `docs/MODEL_CARD.md` |
| 3 | What could cause leakage? | `training_cutoffs` guard and leakage test in `ml/tests/test_experiment.py` |
| 4 | Real observation vs simulation? | Data card, SYNTHETIC labels, `research/interviews/log.csv` (empty until you interview) |
| 5 | How would a customer notice wrong output? | Reasons per account, value ranges, holdout uplift report, audit log |
| 6 | Competitors and your focus? | `docs/archive/starter/GO_TO_MARKET.md`, personas (hypotheses) |
| 7 | Cost of one more tenant; cross-tenant access? | `services/api/tests/test_tenancy.py`, `supabase/migrations/0001_tenancy.sql`, `render.yaml` |
| 8 | What surprised you and changed the product? | Simple models beat LightGBM; queue latency found by load test; ZILN divergence; seasonality |

## Exercises log template (copy to `project/EXERCISES_LOG.md`)

| Week | Date | Exercise | What I did | Evidence link | Time |
|---|---|---|---|---|---|
| 1 | | | | | |
