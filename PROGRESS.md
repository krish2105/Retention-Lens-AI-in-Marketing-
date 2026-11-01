# Progress — RetentionLens (MAIB AI 208 · AI in Marketing)

Last updated: 2026-11-01. Everything listed here was checked by running it. What is still missing is in [REMAINING.md](REMAINING.md).

## At a glance

| Phase | Status | Evidence |
|---|---|---|
| Course audit and gap analysis | Done | `project/GAP_ANALYSIS.md` |
| Research (data, methods, GenAI safety, competitors, UI) | Done | `reports/RetentionLens product and UI research.md`, `research_notes/` |
| Product and system design (Aurora direction) | Done, approved | `docs/superpowers/specs/2026-11-01-retentionlens-aurora-design.md` |
| ChatGPT image prompts (AUR-01 to AUR-10) | Done | `assets/IMAGE_GENERATION_PROMPTS.md` |
| Images generated from those prompts | Done locally, not yet in the repo | 11 final PNGs in `RetentionLens_AUR_Complete_Image_Collection/` (untracked, 36 MB) |
| **P1** Data pipeline | Done, merged | `ml/retentionlens/data/`, `reports/data_profile.md`, `docs/DATA_CARD.md` |
| **P2** Models on rolling cutoffs + frozen test | Done, merged | `ml/retentionlens/{features,models,eval}/`, `reports/model_results.md`, `docs/MODEL_CARD.md` |
| P3 to P8 | Not started | see [REMAINING.md](REMAINING.md) |

## Tests (run 2026-11-01)

- `cd ml && uv run pytest -q` → **33 passed** (Python 3.12, pandas 2.3.3, LightGBM 4.7.0, PyMC-Marketing 1.3.0)
- `PYTHONPATH=services/api pytest -q services/api/tests` → **6 passed** (the original demo API, synthetic data)
- `cd apps/web && npx next build` → compiles (the original starter dashboard, not yet the Aurora UI)

## P1 — data pipeline (merged in `98ff1d1`)

- Downloads UCI Online Retail II (CC BY 4.0, DOI 10.24432/C5CG6D) and records its SHA-256 (`572e3627…67bfb`) in `project/DATA_SOURCE_REGISTER.csv`.
- The loader accepts the file's real headers and the names UCI documents.
- Problem rows are flagged and counted; none is silently dropped.
- Real-file facts:
  - 1,067,371 rows from 2009-12-01 to 2011-12-09, with 53,628 invoices, 5,942 customers and 43 countries.
  - 22.8% of rows have no customer ID.
  - 794,163 rows (74.4%) are usable for customer models.
- Finding: the two workbook sheets overlap on 2010-12-01 to 2010-12-09, so 22,202 rows appear twice. The duplicate flag catches them.

## P2 — models (merged in `0209209`)

- A customer snapshot is built at each of 5 cutoffs. Features use only data before the cutoff, and labels come from the 90 days after it. A test checks there is no leakage.
- Models compared: recency rule, logistic RFM, BG/NBD + Gamma-Gamma, LightGBM, and a naive "last 90 days" baseline.
- The protocol was fixed before any results were seen: 3 dev cutoffs, then one frozen test at 2011-09-01, scored once, with no tuning.
- Frozen test (5,224 customers):
  - **BG/NBD** is best on PR-AUC (0.820), Brier (0.1864) and value Gini (0.825).
  - LightGBM reaches 0.819 / 0.1938.
- Across all 4 cutoffs, LightGBM beats BG/NBD on 0 and logistic regression on 1, so the default scoring model is BG/NBD.
- Known limit: seasonality isn't modelled. Peak-season spend is under-predicted (£2.62M actual against £1.80M predicted).

## Course outcome coverage so far

| Outcome | Status | Evidence |
|---|---|---|
| A · Marketing research + predictive analytics | **Partly evidenced** | Data profile, data card, lapse models and metrics |
| B · Traditional + web + social data | **Not started** | Planned for P5 |
| C · CLV, churn, retention, new customers | **Partly evidenced** | Churn (lapse) and CLV models done; segmentation and finding new customers not done |
| D · Generative AI for marketing decisions | **Not started** | Planned for P6 |
| CLO4 · Ethics | **Not started** | Planned for P6 (consent, approval gate, red team) |

| Lab week | Topic | Usable material so far |
|---|---|---|
| 2 | Market data and plots | Data profile tables only, no charts yet |
| 4 | Customer lifetime value | BG/NBD + Gamma-Gamma results (P2) |
| 6 | Churn | Lapse model comparison (P2) |
| 8 | Brand and pricing | None |
| 10 | Competitive intelligence and web scraping | None |

## Design assets ready

- 4 UI directions mocked up (private canvas). **D · Aurora** was chosen.
- Choices made: GenAI on a local Ollama model (`qwen2.5:7b`, installed), and social data synthetic and labelled as such.
- The 11 final Aurora images are generated (hero, light hero, galaxy, import, outreach, model lab, signals, offline, app mark, README banner, social card).
