# Immutable append-only session notes — RetentionLens

### 2026-10-22 — Starter generated
Scope: plans, synthetic domain sample, API/web source and prompts placed into ZIP. No customer data, trained results, UI screenshots or production readiness claimed. Next: Work M0 audit, install and run.

### 2026-11-01 — Audit: outline vs repo (no feature work)
Scope: read outline.docx and all repo files; ran pytest (6 passed), API smoke via curl, `next build` (OK). Wrote `project/GAP_ANALYSIS.md`. Findings: outcomes B and D unplanned; 60% of marks (exercises + labs) have no tracking; repo only supports C/A partially; no ML/data/GenAI code; docs contain template leftovers; not a git repo. Untested: browser UI. Hours: ~1. Next: owner answers scope questions, then typed invoice loader.

### 2026-11-01 — Research, UI directions, design spec (no app code)
Ran 5 research tracks (sources in `research_notes/RetentionLens product and UI research/`, report in `reports/`). Published 4 UI mockups on a private canvas; owner chose D Aurora, local Ollama, synthetic social data. Wrote `docs/superpowers/specs/2026-11-01-retentionlens-aurora-design.md` and replaced `assets/IMAGE_GENERATION_PROMPTS.md` with an Aurora series (AUR-01..10). Untested: everything in the spec; no ML/UI code written. Next: owner reviews spec, then implementation plan for P1 (data pipeline).

### 2026-11-01 — P1 data pipeline built and run on the real file
Plan `docs/superpowers/plans/2026-11-01-p1-data-pipeline.md` executed test-first on branch `p1-data-pipeline`: `ml/` package (download+sha256, real-header loader, issue flags, profile, CLI). 15 tests pass. Real run: 1,067,371 rows, 5,942 customers, 22.8% missing Customer ID, 34,335 duplicates (22,202 from the Dec 2010 sheet overlap). Wrote `docs/DATA_CARD.md`. Untested: nothing downstream uses these files yet (P2).
