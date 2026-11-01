# Immutable append-only session notes — RetentionLens

### 2026-10-22 — Starter generated
Scope: plans, synthetic domain sample, API/web source and prompts placed into ZIP. No customer data, trained results, UI screenshots or production readiness claimed. Next: Work M0 audit, install and run.

### 2026-11-01 — Audit: outline vs repo (no feature work)
Scope: read outline.docx and all repo files; ran pytest (6 passed), API smoke via curl, `next build` (OK). Wrote `project/GAP_ANALYSIS.md`. Findings: outcomes B and D unplanned; 60% of marks (exercises + labs) have no tracking; repo only supports C/A partially; no ML/data/GenAI code; docs contain template leftovers; not a git repo. Untested: browser UI. Hours: ~1. Next: owner answers scope questions, then typed invoice loader.

### 2026-11-01 — Research, UI directions, design spec (no app code)
Ran 5 research tracks (sources in `research_notes/RetentionLens product and UI research/`, report in `reports/`). Published 4 UI mockups on a private canvas; owner chose D Aurora, local Ollama, synthetic social data. Wrote `docs/superpowers/specs/2026-11-01-retentionlens-aurora-design.md` and replaced `assets/IMAGE_GENERATION_PROMPTS.md` with an Aurora series (AUR-01..10). Untested: everything in the spec; no ML/UI code written. Next: owner reviews spec, then implementation plan for P1 (data pipeline).

### 2026-11-01 — P1 data pipeline built and run on the real file
Plan `docs/superpowers/plans/2026-11-01-p1-data-pipeline.md` executed test-first on branch `p1-data-pipeline`: `ml/` package (download+sha256, real-header loader, issue flags, profile, CLI). 15 tests pass. Real run: 1,067,371 rows, 5,942 customers, 22.8% missing Customer ID, 34,335 duplicates (22,202 from the Dec 2010 sheet overlap). Wrote `docs/DATA_CARD.md`. Untested: nothing downstream uses these files yet (P2).

### 2026-11-01 — P2 models on rolling cutoffs
Plan `docs/superpowers/plans/2026-11-01-p2-models.md` executed test-first on branch `p2-models`: snapshots (leakage test), recency/logistic/naive/BG-NBD+GG/LightGBM models, metrics, experiment runner, `models` CLI. 33 tests pass. Dev run then one frozen-test run. Result: BG/NBD strongest; LightGBM does not beat logistic or BG/NBD. Seasonality under-prediction documented in `docs/MODEL_CARD.md`. Untested: conformal intervals, ZILN, UI use of these outputs.

### 2026-11-01 — Progress and remaining-work summary
Re-ran tests (ML 33 passed, demo API 6 passed). Wrote `PROGRESS.md` and `REMAINING.md` at the repo root. Remaining estimate ~80 h (P3–P8 ~51 h + course deliverables ~30 h). Owner's 11 final AUR images are generated but untracked (36 MB); compress before committing.

### 2026-11-01 — P3–P8 built without stopping (owner request)
Serving builder, FastAPI, Aurora UI (theme toggle, 3D terrain + galaxy), segments + lookalikes, signals (web CC0, network, synthetic social, scraper), outreach studio with local qwen2.5:7b + checks + consent gate + idempotent approval, product lab, evidence page, CI, README. Each phase merged to main and pushed. Findings: Christmas sales lead web interest by one month (r 0.90 lagged); critic flags 15/16 drafts (needs human calibration); elasticities confounded by price breaks.

### 2026-11-01 — Deploy, verify, accessibility
Static read-only export deployed to GitHub Pages and verified live (data files 200, no console errors). CI green after pinning setup-uv. axe-core WCAG 2.2 AA: fixed scrollable-region and theme-token contrast issues; 0 violations on 9 pages both themes; 375 px OK. Added critic calibration tool + labelling sheet, lab scaffolds, reading list; archived starter docs.

### 2026-11-01 — Errors, theme redesign, mobile pass, Vercel, deck and report
Fixed React "unmount a root while rendering" errors (removed drei Html labels) and a toggle hydration mismatch. Redesigned theme change (feathered View Transition reveal from the toggle + sliding indicator). Playwright audit: 11 pages x 6 widths (320–768) x 2 themes, fixed sidebar overflow, iOS input zoom, tap targets, small fonts, long links; live Pages site re-audited clean apart from exempt inline links (then padded). Deployed to Vercel (retentionlens-demo.vercel.app); Vercel SSO protection still on (disabling was blocked by the safety classifier; owner must run it). Built 14-slide PPTX (design/deck/build.js) and 11-page PDF report (design/report/) from result files, with 15 live screenshots.

### 2026-11-01 — Roadmap R1–R8 built (owner: "do all e2e")
Branch `roadmap`. R2: `retentionlens.ingest` (any-header mapping, row-level validation, scoring CLI), durable scoring worker, upload wizard, weekly queue with seeded 20% holdout and ITT uplift + 95% CI, reorder detection from the next upload. R3: workspaces/roles/invites (local email+password or Supabase JWT), org_id on every query, export and delete, rate limits, security headers, Supabase RLS migration (not applied), Dockerfile + render.yaml (not deployed). R5: seasonal multiplier adopted (dev bias 32.9%→16.8%, Brier+MAE 3/3), conformal 80% ranges (dev coverage 79.5/82.2/82.4%), ZILN challenger 0/3 (v1/v2 diverged, fixes disclosed), 22 OWASP LLM red-team tests. R4: load test (queue p95 1,045 ms found and fixed → 312 ms; SLO met), scoring 114,886 lines in 9.1 s, restore drill passed, 52 static Playwright tests + live flow, CodeQL/pip-audit/npm audit (postcss override). R1/R6/R7/R8: landing, pricing, waitlist, legal pages, status, 404, tour, locale + RTL check, case study, interview kit, personas (hypotheses), pilot kit, DPA template, coursework review, LinkedIn/CV kit. Tests: ML 61, API 60, browser 52 + 1 live. Untested: Docker image build (daemon not running locally; CI job added), hosted deployment, Stripe test checkout against real Stripe, Supabase migration. Owner-only and not done: interviews, usability, pilot, critic labels, lab reports.

### 2026-11-01 — Independent re-score and fixes
Reviewer agent re-scored (mean 65 → 73; table in `docs/SCORECARD.md`). Fixed what it found: peak-season coverage 74.2% now stated; baseline-number difference explained; tie no longer called a win; red-team count is 23 (the earlier entry said 22); stale BLOCKERS/roadmap/model card updated; API refuses `RL_AUTH_MODE=off` when `RL_ENV=production` (Dockerfile and render.yaml set it; test added; API tests 61). CI on 32adfe0 fully green including e2e and docker. Vercel redeployed and aliased; Pages deployed.

### 2026-11-01 — Second build pass ("build everything you can")
R5b pooled conformal calibration (dev 79.5/85.1/84.7%, peak 80.0%, disclosed as informed by the seen window); labelling UI + calibration panel; sign-in hardening; scheduled backups + seeded restore drill (passed); funnel metric; usability kit; uptime workflow; exercises log; lab evidence packs; captioned demo video (Playwright + Homebrew ffmpeg, since the bundled ffmpeg does not run on this macOS); Supabase RLS CI job (first two runs failed: storage schema timing, then an invalid container hostname from the repo folder name; both fixed). API tests 66, ML 61. Not done: deck/report refresh (next session). Ollama has no models installed right now.
