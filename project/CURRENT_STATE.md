# Current state — 2026-11-01 (after roadmap R1–R8 build and the submission refresh)

## Submission refresh (scheduled run, branch `submission-refresh`, fast-forwarded to main)
- Screenshots: 25 in `submissions/screenshots/` (01–15 recaptured under the same names, overview now at /overview; new 16–25: landing, upload mapping and check report on the SYNTHETIC sample, queue, queue uplift panel, status, case study, phone landing and queue). Captured with Playwright + installed Chrome at 1440×900 and 390×844, @2x. The synthetic upload was deleted afterwards (`/api/datasets` returns `[]`). Capturing 08 created one template-mode draft in the local database.
- Deck: `submissions/RetentionLens_Presentation.pptx`, 18 slides with notes (new: upload, holdout queue, R5/R5b + ZILN, SaaS foundations, "what is still missing"); rendered through LibreOffice and checked visually.
- Report: `submissions/RetentionLens_Project_Report.pdf`, 17 A4 pages (new sections 3b loop, 5b R5/R5b, 10b SaaS foundations, 12 what is still missing). `print.js` now uses the Chrome channel by default.
- Test counts in `design/test_counts.json` (collection only, not runs): ML 61, API 66 (23 red team), static e2e 52, live 1.
- Owner placeholders: deck slides 16–17 and report sections 11–12 mark lab reports and reflection as `[OWNER: ...]`.

## Verified by execution this session
- ML tests: 61 passed (`cd ml && uv run pytest`). API tests: 60 passed (`PYTHONPATH=services/api pytest services/api/tests`).
- Browser: 52 static Playwright tests pass (one `/accounts` render test is timing-flaky on the slow local static server and passes on retry); live upload→score→review→draft→approve flow passed against the local API.
- Real upload of the synthetic sample through the UI: 118 accounts scored in ~12 s; 114,886-line synthetic file scored in 9.1 s.
- Restore drill caveat: it ran on a small local database with empty user and dataset tables; repeat on a hosted instance with real rows.
- R5 experiment: `reports/r5_results.md`; serving rebuilt with the seasonal model; static demo data re-exported.
- Docker image builds and passes its health check in CI; the whole CI run on 32adfe0 (ml, api, web, e2e, docker, security) passed, as did CodeQL.
- Load test `reports/load_test.md` (SLO met); restore drill `reports/restore_drill.md` (passed); `npm audit` 0 high; `pip-audit` clean.

## Added in the second build pass (same day)
- R5b season-aware value ranges (peak coverage 74.2% → 80.0%, choice informed by the seen peak window); serving and demo data rebuilt.
- Outreach studio: human labelling and a live critic-calibration panel (kappa, false alarms). API tests 66.
- Sign-in hardening: failed sign-ins audited (hashed), per-account throttle, common/weak passwords refused.
- Backups scheduled in the API (`RL_BACKUP_HOURS`); restore drill re-run on a seeded synthetic database.
- `/api/funnel` (upload → scored → first decision minutes), usability kit with SUS, uptime workflow.
- Exercises log template; `labs/*/EVIDENCE.md` generated from run files; 63-second captioned demo video.
- Supabase migration applied to a local stack in CI and the RLS leak test passes (commit 5b81f51, all 7 CI jobs green).
- Ollama currently has no models installed (`qwen2.5:7b` missing): drafts use the labelled template until it is pulled again.

## Third build pass (2026-11-01 evening, worktree branch ui-complete)
- Uploads run the full serving builders (segments, galaxy, lookalikes with a stated fallback, top products, product lab) plus a 90-day backtest; Data, Segments, Product lab and Model lab verified in the browser on an uploaded file.
- Model lab shows R5/R5b results and the model registry; course evidence page updated.
- Queue week picker and manual reorder logging; waitlist admin page; Excel sheet choice; date-reading preview; Supabase sign-in (web, gated by env).
- Arabic for navigation, tour, queue and upload (AI-drafted, pending native review); theme toggle no longer slides in on load.
- axe + 375 px checks on all 23 pages, both themes: 98 browser tests (one or two timing flakes pass on retry); fixed a prohibited aria-label on the loading placeholder.
- Postgres backend (`RL_DATABASE_URL`): API suite 66/66 on Postgres 17 locally; CI job added. Postgres load test and pg_dump/pg_restore drill passed.
- Scheduled run (10:57 PM) refreshed 25 screenshots, the 18-slide deck and 17-page report (commit 57d49f9).

## Not verified / not done
- Hosted API (Render/Azure), Supabase migration, Stripe test checkout: need the owner's accounts.
- Vercel Analytics: code gated by `NEXT_PUBLIC_VERCEL_ANALYTICS=1`; must be enabled in the Vercel project.
- Owner-only: interviews (R1), usability sessions (R2), critic labels (R5), pilot (R6), lab reports and narrative (R7).

## Changed areas
ml/retentionlens/{ingest,features/seasonal.py,models/{conformal,ziln}.py,eval/r5.py,registry.py}; services/api/app/{tenancy,datasets,loop,billing,ops,security,env,calibration}.py; apps/web (site pages, upload, queue, team, privacy, billing, status, case study, e2e); docs/{research,pilot,security,OPERATIONS,COURSEWORK_REVIEW,CASE_STUDY,LINKEDIN_KIT}.md; supabase/; Dockerfile; render.yaml.

## Next runnable task
Owner: run interviews with `docs/research/INTERVIEW_KIT.md`; label drafts in the Outreach studio; create Render + Supabase + Stripe test accounts, then follow `supabase/README.md` and `render.yaml`.
