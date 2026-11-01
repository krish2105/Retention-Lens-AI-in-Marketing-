# Handoff — resume here

Kept current at every push so any session (local or cloud) can continue. Last update: 2026-11-01.

## Status

| Phase | State |
|---|---|
| P1 data, P2 models | Done (see `PROGRESS.md`) |
| P3 API + Aurora UI shell | **Done**: `cli serve`, FastAPI (`services/api`), Next.js Overview / Accounts / Model lab / Data / Settings, 3D cohort terrain, light/dark/system theme |
| P4 segments + 3D galaxy + lookalikes | **Done**: RFM segments + playbook, k-means (k by silhouette), 3D galaxy (5.8k instanced points), lookalike model (test AUC 0.821) |
| P5 signals | **Done**: Wikipedia seasonality vs sales (Christmas r 0.34 same month, 0.90 with 1-month lead), co-purchase network (3 communities), 600 SYNTHETIC posts with lexicon sentiment + injection flags, polite toscrape.com scraper |
| P6 outreach studio | **Done**: local qwen2.5:7b drafts from structured facts only, numeric/pressure/offer/PII checker, critic pass, PECR consent gate, idempotent approval, CSV export, audit log, red-team tests; live eval script `services/api/evals/run_eval.py` |
| P7 product lab | **Done**: basket rules (lift), portfolio matrix, product loyalty, elasticity shown as a confounding lesson |
| P8 README, evidence page, CI | **Done**: professional README with real metrics, `/evidence` outcome map, GitHub Actions (ml, api, web) |
| Deploy | **Live** https://krish2105.github.io/Retention-Lens-AI-in-Marketing-/ via `.github/workflows/pages.yml` (static export; refresh data with `python3 scripts/export_static_data.py` after `cli serve`) |
| Vercel | Deployed: retentionlens-demo.vercel.app (`cd apps/web && vercel deploy --prod --build-env NEXT_PUBLIC_STATIC=1`, then `vercel alias set <url> retentionlens-demo.vercel.app`). Public access needs the owner to turn off Vercel Authentication |
| Submission pack | `submissions/` deck + PDF report + screenshots; rebuild with `design/deck/build.js` and `design/report/` |
| Remaining | See `REMAINING.md` (critic calibration, demo video, labs, presentation, report) |

## Rebuild everything from a clean clone

```bash
cd ml && uv sync --python 3.12
uv run python -m retentionlens.cli data                 # downloads UCI Online Retail II (~45 MB), checksums it
uv run python -m retentionlens.cli models --include-test  # P2 evaluation (re-scores the frozen test; results are deterministic)
uv run python -m retentionlens.cli serve                # writes artefacts/serving/*.json for the API
cd ../services/api && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8001              # API
cd ../../apps/web && npm install && echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local && npm run dev  # UI on :3000
```

Tests: `cd ml && uv run pytest -q` · `PYTHONPATH=services/api services/api/.venv/bin/pytest -q services/api/tests` · `cd apps/web && npx next build`.

## Conventions that matter

- Commits carry the owner's name only. **No AI co-author lines anywhere.**
- Never commit `data/raw`, `data/interim`, `artefacts/`, `.env*`, or the image collection folder/zip at the repo root.
- Every number in the UI must come from a serving JSON file; label synthetic data `SYNTHETIC`.
- New per-account columns from later phases go through `ml/retentionlens/serving/extras.py` (`EXTRA_BUILDERS`).
- In the Claude desktop preview, the API must start through `uv` (see `.claude/launch.json`); port 8001.
