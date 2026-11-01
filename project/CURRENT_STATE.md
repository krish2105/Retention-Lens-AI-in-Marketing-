# Current state — 2026-11-01 (after roadmap R1–R8 build)

## Verified by execution this session
- ML tests: 61 passed (`cd ml && uv run pytest`). API tests: 60 passed (`PYTHONPATH=services/api pytest services/api/tests`).
- Browser: 52 static Playwright tests pass (one `/accounts` render test is timing-flaky on the slow local static server and passes on retry); live upload→score→review→draft→approve flow passed against the local API.
- Real upload of the synthetic sample through the UI: 118 accounts scored in ~12 s; 114,886-line synthetic file scored in 9.1 s.
- R5 experiment: `reports/r5_results.md`; serving rebuilt with the seasonal model; static demo data re-exported.
- Load test `reports/load_test.md` (SLO met); restore drill `reports/restore_drill.md` (passed); `npm audit` 0 high; `pip-audit` clean.

## Not verified / not done
- Docker image build (Docker daemon not running here; CI `docker` job builds and health-checks it).
- Hosted API (Render/Azure), Supabase migration, Stripe test checkout: need the owner's accounts.
- Vercel Analytics: code gated by `NEXT_PUBLIC_VERCEL_ANALYTICS=1`; must be enabled in the Vercel project.
- Owner-only: interviews (R1), usability sessions (R2), critic labels (R5), pilot (R6), lab reports and narrative (R7).

## Changed areas
ml/retentionlens/{ingest,features/seasonal.py,models/{conformal,ziln}.py,eval/r5.py,registry.py}; services/api/app/{tenancy,datasets,loop,billing,ops,security,env,calibration}.py; apps/web (site pages, upload, queue, team, privacy, billing, status, case study, e2e); docs/{research,pilot,security,OPERATIONS,COURSEWORK_REVIEW,CASE_STUDY,LINKEDIN_KIT}.md; supabase/; Dockerfile; render.yaml.

## Next runnable task
Owner: run interviews with `docs/research/INTERVIEW_KIT.md`; label drafts in the Outreach studio; create Render + Supabase + Stripe test accounts, then follow `supabase/README.md` and `render.yaml`.
