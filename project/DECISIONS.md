# Decision register

| Date | Decision | Reason / evidence | Revisit when |
|---|---|---|---|
| 2026-10-22 | Keep RetentionLens distinct from four other subjects | Independent coursework and reproducible submission | Only if university instructs otherwise |
| 2026-10-22 | Use a synthetic demo scaffold; no real dataset shipped | Dataset rights, size, reproducible provenance | After source licence audit |
| 2026-10-22 | Use Next.js/FastAPI for vertical slice | Maintainable solo workflow | After actual implementation bottleneck |
| 2026-10-22 | 4 hours/week initial allocation | 20 hours shared across five projects | When course timetable is known |
| 2026-11-01 | UI direction D "Aurora" (glass over aurora fields, 3D cohort terrain + customer galaxy) | Owner picked from 4 live mockups (canvas https://claude.ai/artifact/MxLac3pzFvSX4fyx9M7Ty9) | If glass contrast fails WCAG AA in testing |
| 2026-11-01 | GenAI runs on local Ollama, default `qwen2.5:7b` (installed), configurable | Owner choice: no API key/cost; Ollama 0.34.4 on 24 GB Mac | If draft quality fails eval gate |
| 2026-11-01 | Social-media data for outcome B is synthetic and labelled SYNTHETIC; web signals are real (Wikimedia CC0, GDELT, Trends CSV) | Yelp/Reddit/Amazon terms block public-repo use (see research report) | If a licensed social source is found |
| 2026-11-01 | No Claude co-author/credit in commits, PRs or README | Owner instruction | Never |
| 2026-11-01 | Keep Next.js 15, pin React 19.2.x; Python 3.12 for ML | R3F 9 confirmed for React 19.0–19.2; PyMC-Marketing 1.3 needs ≥3.12 | When R3F confirms 19.3 |
| 2026-11-01 | Ship BG/NBD + Gamma-Gamma as the default scoring model; keep LightGBM as comparison; ZILN not pursued for now | Frozen-test + 3 dev cutoffs: LightGBM beats BG/NBD on 0 of 4 (lapse); see `docs/MODEL_CARD.md` | If seasonality features change the ranking |
| 2026-11-01 | Plain CSS tokens instead of Tailwind/shadcn for the Aurora UI | Faster to build and theme glass/aurora precisely; no component library needed | If the UI grows many form components |
| 2026-11-01 | Serving values use spend net of returns | A cancelled £168k bulk order (customer 16446) inflated gross-spend CLV | Never |
| 2026-11-01 | No free text ever reaches the LLM prompt; tone is an enum | Prompt-injection defence (OWASP LLM01) | If a reviewed free-text field is needed |

## 2026-11-01 — Roadmap build decisions
- Tenancy enforced in the app (org_id on every query, SQLite) now; Postgres RLS prepared for Supabase. Reason: no Supabase account yet; isolation tests run in CI either way.
- ML scoring runs in a subprocess (`python -m retentionlens.ingest`) from a durable SQLite-backed queue. Reason: keeps the API light; a model crash cannot take the API down; jobs resume after restart.
- Seasonal BG/NBD adopted for serving on dev evidence only (3/3 on Brier and MAE). ZILN not adopted (0/3). Frozen test not reused for selection.
- Weekly queue holds out 20% at random (seeded hash of org, account, week) and reports intention-to-treat uplift.
- Billing accepts Stripe test keys only; live keys are refused in code.
- No email-sending capability anywhere (OWASP LLM06); approved drafts export only.
