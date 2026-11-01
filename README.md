# RetentionLens — AI in Marketing (MAIB AI 208)

**Pack type:** research + product + engineering STARTER KIT. **Not:** a completed trained model, proven customer product, or deployed SaaS. The included API, dashboard, sample data, calculation and tests form a demo vertical slice.

**Term starts:** 10 November 2026. **Owner:** solo builder. **Available time:** 20 hours/week **TOTAL across five independent products**, not per product. Each pack is a self-contained project; do not merge core source, models or assessment evidence.

## Start here (under 10 minutes)
1. Read `START_HERE.md`, then `AGENTS.md` and `docs/ASSESSMENT.md`. The original outline is included in `course/outline.docx`.
2. Run `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then `pip install -r services/api/requirements.txt`.
3. In one terminal run `cd services/api && uvicorn app.main:app --reload --port 8000`.
4. In another terminal run `cd apps/web && npm install && npm run dev` and open `http://localhost:3000`.
5. API `http://localhost:8000/docs`, automated tests from root: `PYTHONPATH=services/api pytest -q services/api/tests`.
6. Open this folder in ChatGPT Work and paste the entire `prompts/00_MASTER_WORK_PROMPT.md`. Work must begin with repo audit and course/rubric confirmation, not generate an imagined final product.

**Demo scope:** sample records are fictional; the API stores reviews and CSV imports in local SQLite, a deterministic domain demonstration is available, and the frontend provides a functional theme toggle and review actions. **The training pipeline, real data connectors, advanced views, security and commercial production features are documented requirements to implement, not already built.**

## ML pipeline (P1: data)
Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.
```bash
cd ml && uv sync --python 3.12 && uv run pytest && uv run python -m retentionlens.cli data
```
Downloads UCI Online Retail II (CC BY 4.0) into gitignored `data/raw/`, checks its SHA-256, flags data-quality issues without dropping rows, and writes `reports/data_profile.md`. Dataset facts and known issues: `docs/DATA_CARD.md`.

## ML pipeline (P2: models)
```bash
cd ml && uv run python -m retentionlens.cli models            # dev cutoffs only
cd ml && uv run python -m retentionlens.cli models --include-test  # adds the frozen 2011-09-01 test
```
Compares a recency rule, logistic RFM, BG/NBD + Gamma-Gamma and LightGBM on rolling 90-day cutoffs. Results: `reports/model_results.md`; findings and limits: `docs/MODEL_CARD.md`.

## Domain
**Problem:** 90-day repeat-purchase and customer value forecasting with human-led account reviews
**Target user:** Small wholesaler owner or lifecycle marketer
**Core job:** Check accounts with declining purchasing signals, assess expected future purchase range, approve appropriate outreach.
**Research question:** Does a two-part probabilistic neural predictor outperform RFM and gradient boosting on calibrated 90-day repeat-purchase and customer-value forecasts under temporal change?

## File guide
- `AGENTS.md` — authoritative agent instructions; read every fresh session.
- `prompts/00_MASTER_WORK_PROMPT.md` — full Work handoff. More focused prompts in `prompts/`.
- `docs/ASSESSMENT.md` — unit outcomes, evidence matrix, marks and risks.
- `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` — E2E system and research flow.
- `docs/PRD.md` — features, acceptance criteria and phased product scope.
- `docs/DATA_AND_RESEARCH.md` — sources, licensing, experiment designs and leakage rules.
- `docs/UX_DESIGN_SYSTEM.md` — premium UI specifications and theme tokens.
- `assets/IMAGE_GENERATION_PROMPTS.md` — copy-ready ChatGPT image creation prompts and naming convention.
- `docs/ROADMAP.md` — solo schedule with a shared 20-hour weekly constraint.
- `docs/SECURITY_AND_SAAS.md`, `docs/GO_TO_MARKET.md`, `docs/TEST_PLAN.md` — release readiness.
- `project/CURRENT_STATE.md`, `project/SESSION_LOG.md`, `project/DECISIONS.md`, `project/NEXT_ACTIONS.md` — context recovery.
- `services/api` / `apps/web` — demo starter code; `data/sample` — synthetic example CSV.
- `course/outline.docx` — original uploaded outline, for independent verification.

## Ground rules
Never claim models have been trained, external data downloaded, customer feedback gathered, savings achieved or tests passed unless the artifacts and actual execution results demonstrate this. Never commit secrets, customer records or acquired public dataset files to the repo. Preserve original data licenses and source versions. Request human review for consequential actions.
