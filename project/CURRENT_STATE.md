# Current verified state — RetentionLens

Last edited: 2026-11-01 (audit + research + design spec; no application code changed).

## VERIFIED this session (observed output)
- `course/outline.docx` read in full; requirements summarised in `project/GAP_ANALYSIS.md` (new).
- `pytest -q services/api/tests` (Python 3.14.7, venv in scratchpad, deps from requirements.txt): **6 passed**, 1 starlette/httpx deprecation warning.
- uvicorn on :8765 with temp DB + curl: `/api/health`, `/api/demo/records` (3 rows), `/summary`, `/domain` return documented JSON; unknown record review -> 404. OpenAPI lists 6 paths.
- `npm install` + `npx next build` in `apps/web` (Node v26.10.0): compiled, types OK.
- Contrast computed from CSS tokens: accent/page 4.61:1, white-on-accent 4.93:1, dark accent/page 9.07:1 (AA body text passes; `--muted` unchecked).

## P1 data pipeline — VERIFIED 2026-11-01 (branch `p1-data-pipeline`)
- `cd ml && uv run pytest -q` → 15 passed (Python 3.12, pandas 2.3.3).
- `uv run python -m retentionlens.cli data` → 1,067,371 rows, 2009-12-01..2011-12-09, 5,942 customers, 794,163 rows usable for customer models (35 s run).
- Archive SHA-256 572e3627…67bfb recorded in `project/DATA_SOURCE_REGISTER.csv`; report `reports/data_profile.md`; card `docs/DATA_CARD.md`.
- Finding: the two workbook sheets overlap 2010-12-01..09; 22,202 rows repeat across sheets (flagged, first copy kept).

## P2 models — VERIFIED 2026-11-01 (branch `p2-models`)
- `cd ml && uv run pytest -q` → 33 passed.
- `uv run python -m retentionlens.cli models --include-test` → run `20261101T084302Z-test` (24 s); dev-only run `20261101T084223Z-dev` first, identical dev numbers.
- Frozen test 2011-09-01 (5,224 customers): BG/NBD PR-AUC 0.820 / Brier 0.1864 best; LightGBM 0.819 / 0.1938; logistic 0.814 / 0.1875. Value Gini: BG/NBD+GG 0.825 best.
- LightGBM beats BG/NBD on 0 of 4 cutoffs (lapse), logistic on 1 of 4; beats only the recency rule and naive value (4 of 4).
- Limitation found: seasonality not modelled; all models under-predict peak-season spend (actual £2.62M vs BG/NBD+GG £1.80M). See `docs/MODEL_CARD.md`.

## P3–P8 — VERIFIED 2026-11-01
- ML tests 48 passed; API tests 14 passed; `npx tsc --noEmit` clean; UI checked in the Claude browser (overview terrain, segments galaxy, signals, outreach end-to-end with real qwen2.5:7b draft).
- `cli serve` builds every screen's JSON from real data (5,852 accounts scored at 2011-12-10).
- Live GenAI eval (16 drafts): 15/16 numbers grounded, 16/16 on pressure/offers/PII/placeholders/length, critic passes 1/16.
- Not verified: CI on GitHub, axe/mobile audit, demo video.

## NOT verified / still absent
- Browser rendering, theme toggle, mobile layout, keyboard flow, screenshots: **not run**.
- No ML code, no dataset (DATA_SOURCE_REGISTER.csv header-only), no metrics, no lab/exercise artifacts, no GenAI component, no web/social source, no auth, not a git repo.
- Outline outcomes B (multi-source data) and D (Generative AI) have no plan or code; see `project/GAP_ANALYSIS.md`.

## Files changed this session
- NEW `project/GAP_ANALYSIS.md`; edited `project/CURRENT_STATE.md`, `SESSION_LOG.md`, `BLOCKERS.md`, `NEXT_ACTIONS.md`.
- Side effects (gitignored): `apps/web/node_modules/`, `apps/web/.next/`, `apps/web/package-lock.json`.

## Unresolved blockers
See `project/BLOCKERS.md` (added: B/D scope, Cloud Lab, "deep learning" rubric wording, no git).

## Design (2026-11-01, awaiting owner review)
- Spec: `docs/superpowers/specs/2026-11-01-retentionlens-aurora-design.md` (Aurora UI, local Ollama, synthetic social).
- Research report: `reports/RetentionLens product and UI research.md`.
- Image prompts: `assets/IMAGE_GENERATION_PROMPTS.md` (AUR-01..10, none generated).
- UI mockups (4 directions): private canvas https://claude.ai/artifact/MxLac3pzFvSX4fyx9M7Ty9

## Next runnable task
After merging `p2-models`: P3 = FastAPI endpoints over run artefacts + Aurora UI shell (theme, Overview, Accounts) showing real run values. Owner-generated images sit untracked in `RetentionLens_AUR_Complete_Image_Collection/` for the UI phase.
