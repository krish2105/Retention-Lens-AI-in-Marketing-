# Priority backlog — RetentionLens

## Now (owner, 2026-11-01): the evidence code cannot produce
- [ ] 8–10 discovery interviews with `docs/research/INTERVIEW_KIT.md`; log in `research/interviews/`.
- [ ] Label 16+ drafts (Outreach studio or `reports/critic_labels.csv`); then `GET /api/critic/calibration`.
- [ ] 5 think-aloud usability sessions on upload → queue (gate: 4 of 5 under 10 minutes).
- [ ] Create Render, Supabase and Stripe (test mode) accounts; apply `supabase/` and `render.yaml`.
- [ ] Write the five lab reports and the presentation narrative (`docs/COURSEWORK_REVIEW.md`).
- [ ] Coordinator ruling on solo work, synthetic social data and the deep-learning wording.

## M0 — first Work session (historical; most items superseded by later phases)
- [x] 2026-11-01: audit outline vs repo, run tests/API/build (see GAP_ANALYSIS.md).
- [ ] Ask coordinator: solo allowed? Cloud Lab expectation? "deep learning" wording? B/D scope for final project.
- [ ] Create lab/exercise log + report template aligned to rubric (weeks 2,4,6,8,10).
- [ ] Add Hwang (2019), Winston (2014), Grigsby (2018) to docs/SOURCES.md; map chapters to weeks.
- [ ] Browser-verify the dashboard (theme, mobile, keyboard) and save screenshots.
- [ ] Clean template leftovers in prompts/00 and docs/ASSESSMENT.md; pick one venv location.
- [ ] Inspect original outline and current repo, reconcile marks/deadlines.
- [ ] Install requirements and run unit/API smoke checks; log real output.
- [ ] Verify frontend build/start and theme/review interaction; log screenshots only if executed.
- [ ] Choose and implement one missing validation check with a negative test.
- [ ] Update handoff documents.

## M1 — research input
- [x] 2026-11-01: research report + design spec written (awaiting owner review).
- [x] P1: data pipeline per spec section 4 (2026-11-01, 15 tests, real-file profile) (download+sha256, real headers, cleaning, profile report, data card).
- [x] Verify current data source schema/licence, capture hash and data card.
- [ ] Define holdout and baseline BEFORE modifying model pipeline.
- [ ] Add source import with strict validation and audit trail.

## M2 — academic result
- [x] P2: rolling-cutoff labels, baselines, BG/NBD + Gamma-Gamma, LightGBM, metrics per cutoff (2026-11-01; BG/NBD wins).
- [x] P2b/R5 (2026-11-01): seasonal multiplier adopted, split-conformal intervals (own implementation), ZILN challenger.
- [x] P3: API over run artefacts + Aurora UI shell.
- [ ] Implement baselines and justified own model or user-study protocol.
- [ ] Record true metrics / interviews, error analysis and limitations.
- [ ] Connect evaluated results to decision UI and export.

## M3 — pilot readiness
- [x] Implement auth, org isolation and permitted data onboarding (2026-11-01, R2/R3).
- [ ] Observe real user tasks, improve UX and test recovery.
- [ ] Produce buyer/pilot charter and measurable acceptance gates.

## M4 — SaaS readiness (after pilot)
- [x] Durable jobs, quotas, billing (test mode), restore test, runbook (2026-11-01). Open: external security review, unit economics.
