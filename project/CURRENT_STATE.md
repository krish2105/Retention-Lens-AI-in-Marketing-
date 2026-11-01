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
P2: write the plan for baselines + BG/NBD/Gamma-Gamma + LightGBM evaluated on 4 rolling cutoffs (spec section 5), after merging `p1-data-pipeline`.
