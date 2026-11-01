# RetentionLens — product and system design (Aurora direction)

Date: 2026-11-01 · Status: DRAFT for owner review · Unit: AI in Marketing (MAIB AI 208)
Evidence base: `reports/RetentionLens product and UI research.md` (sourced), `project/GAP_ANALYSIS.md`, `course/outline.docx`.
Owner choices (2026-11-01): UI direction **D · Aurora**; GenAI on a **local open model (Ollama)**; social data **synthetic and labelled**.

## 1. Goal and scope

**Product:** a weekly account-review tool for small wholesalers. It predicts which accounts will not order in the next 90 days, what each is expected to be worth, groups accounts into segments, adds web and social context, and drafts outreach a person must approve.

**Course goal:** one coherent project whose artefacts evidence unit outcomes A, B, C, D and CLO1–CLO4, and feed the five labs, the week-6 presentation and the final project.

**Non-goals (stated in the README):** sending email; causal uplift claims (no campaign data exists); multi-tenant SaaS, auth and billing (documented as future work); real customer data; scraping anything except a sandbox site.

## 2. Outline traceability (what proves what)

| Outline item | Module | Evidence artefact |
|---|---|---|
| A · research + predictive analytics; wk 1–3 | Data pipeline, EDA, predictive core | Data card, quality report, EDA charts, model card |
| B · traditional + web + social; wk 9–10 | Signals | Wikimedia pageviews (CC0), GDELT, Google Trends CSV export, co-purchase network, synthetic social posts (labelled), toscrape.com scraper demo |
| C · CLV, churn, retention, new customers; wk 4–6 | Predictive core, Segments | BG/NBD + Gamma-Gamma CLV, 90-day lapse model, RFM clusters, lookalike "new customer" scoring |
| Positioning, brand, pricing; wk 7–8 | Product and pricing lab | Market-basket rules, associational price elasticity, segment positioning notes |
| D · Generative AI; wk 11; CLO4 ethics | Outreach studio | Grounded drafts, eval suite results, red-team log, ethics and consent notes |
| Labs wk 2/4/6/8/10 (30%) | `labs/week-XX/` | One notebook + 2-page report per lab, rubric headings: implementation, experimentation, problem-solving, reporting |
| Week-6 presentation (10%) | Slides from Model lab | Churn results on frozen test |
| Final project (30%, B·C·D) | Whole app + report | Demo recording, report, reproducible run |
| Reading | `docs/SOURCES.md` | Hwang (2019) chapters mapped to weeks; Winston (2014); Grigsby (2018) |

## 3. Business framing (CEO / CMO / COO)

- **ICP (hypothesis):** UK/UAE wholesaler, 50–2,000 trade accounts, orders via invoices/CSV, no data team. Buyer = owner; user = account manager.
- **Gap (sourced):** DTC tools need Shopify events and 500+ buyers (Klaviyo); distributor platforms are quote-only ERP projects. Nobody offers CSV-first, small-sample uncertainty, approval-gated drafts and public pricing.
- **Pricing (hypothesis, unvalidated):** $99–$399/month by active accounts. No interviews yet: labelled as such everywhere.
- **Ops:** weekly review loop = import → queue → decide → draft → approve → export → record outcome.

## 4. Architecture

```
data/raw (xlsx, gitignored, sha256 checked)
  → ml/ pipeline (Python 3.12, package `retentionlens`)
      ingest → clean → features@cutoff → models → eval → artefacts/runs/<run_id>/
  → services/api (FastAPI, reads run artefacts + SQLite for reviews/drafts/audit)
      → Ollama (localhost:11434) for drafts only, behind tool + checker layer
  → apps/web (Next.js, Aurora UI, R3F 3D)
```

Units and boundaries:
- `ml/retentionlens/data` — download with checksum, load real headers (`Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country`), clean (cancellations `C*`, negative qty, zero price, non-product codes such as POST/M/BANK CHARGES, missing Customer ID kept for market-level stats only), profile report.
- `ml/retentionlens/features` — RFM and behaviour features computed strictly from data before the cutoff.
- `ml/retentionlens/models` — `baselines.py` (recency rule, logistic RFM), `btyd.py` (PyMC-Marketing BG/NBD, Gamma-Gamma), `gbm.py` (LightGBM), `ziln.py` (optional two-head network, own loss implementation).
- `ml/retentionlens/eval` — rolling cutoffs, metrics, calibration, model card writer.
- `ml/retentionlens/segments`, `basket`, `pricing`, `signals` — one module per outline topic.
- `services/api` — read-only analytics endpoints + review/draft/approval/audit endpoints. Analytics numbers only come from run artefacts.
- `apps/web` — UI. Never computes metrics itself.

Python: 3.12 virtual env (PyMC-Marketing 1.3 needs ≥3.12; 3.14 wheels not assumed). Key libs: pandas, pyarrow, pymc-marketing, lightgbm, scikit-learn, mlxtend, networkx, (torch only if ZILN is built), httpx, fastapi.

## 5. Modelling and evaluation protocol

- **Label:** account lapses = no purchase in the 90 days after the cutoff. Value = net spend in those 90 days.
- **Cutoffs (data runs 2009-12-01 to 2011-12-09):** 2010-12-01, 2011-03-01, 2011-06-01 for development; **2011-09-01 frozen test**, touched once. Every cutoff keeps a full 90-day window.
- **Population:** accounts with a Customer ID and ≥1 purchase before the cutoff.
- **Baselines:** recency rule; 1 − P(alive) from BG/NBD; logistic regression on RFM. **Challenger:** LightGBM. **Optional:** ZILN two-head.
- **Metrics:** PR-AUC, Brier + reliability curve, lift/gain, top-k precision; CLV: MAE, normalised Gini, decile table; uncertainty via conformal intervals (MAPIE API to be checked first).
- **Rule:** a model is "better" only if it beats the GBM baseline on ≥3 of 4 cutoffs. Otherwise the report says so.
- **Leakage tests:** unit tests assert no feature reads a row dated after the cutoff.
- **Run record:** run_id, data sha256, cutoff, seed, library versions, params, metrics.json, predictions.parquet.

## 6. GenAI layer (outcome D) — local model

- **Runtime:** Ollama 0.34.4 on this Mac (24 GB RAM). Default model `qwen2.5:7b` (already installed), set by `OLLAMA_MODEL`. Can be swapped without code changes.
- **Pattern:** deterministic core → read-only tools (`get_account_summary`, `get_segment_profile`, `get_playbook`) → model writes a JSON draft against a schema (Ollama `format`) → **numeric checker** rejects any number not present in tool output → **critic pass** (same model, rubric: tone, pressure tactics, false urgency) → **human approval** → export to CSV/.eml file. **No send tool exists.**
- **Untrusted text:** synthetic posts and review text are never placed in the drafting prompt; only aggregated, numeric signals are. Injection test set checks this.
- **Consent:** dataset has no consent field. Export stays blocked until the reviewer records recipient type (company vs sole trader) and consent basis (UK PECR distinction).
- **Model offline:** UI shows an error state and offers a clearly labelled template, never a fabricated "AI" draft.
- **Evals (CI gate):** deterministic checks must pass 100% (schema valid, numbers grounded, no PII, placeholders filled); LLM-judge scores calibrated against ~30 human-labelled drafts; red-team suite (injection, PII leak, excessive agency). Thresholds set from the first baseline run, not invented.
- **Security mapping:** OWASP LLM Top 10 (2025) and Agentic Top 10 (2026) table in `docs/SECURITY_AND_SAAS.md`.

## 7. UI design — Aurora

**Look:** deep night ground with three blurred aurora fields (cyan, magenta, violet) behind frosted-glass panels; Space Grotesk for UI, IBM Plex Mono for figures and provenance; risk colours cyan (retained) / amber (fading) / magenta (lapsed). Light theme: pale ground #F3F4FB with soft pastel fields.

**Tokens (from approved mockup):** dark `--bg #070912`, `--ink #EEF0FF`, `--muted #A7ADC8`, `--cyan #67E8F9`, `--magenta #F472B6`, `--amber #FBBF24`; light `--bg #F3F4FB`, `--ink #11132A`, `--muted #4E5470`, `--cyan #0E7490`, `--magenta #BE185D`, `--amber #8A5D07`. Implemented as OKLCH CSS variables in Tailwind v4 `@theme`.

**Screens:** Overview (cohort retention terrain, KPIs, queue, draft), Accounts (table + drawer with evidence), Segments (3D customer galaxy: x recency, y frequency, z value, colour risk, size CLV), Signals, Outreach studio, Model lab (metrics per cutoff, calibration curve, model card), Course evidence, Imports, Settings.

**Theme:** Light / Dark / System via `next-themes` (no flash), circular View Transition reveal with instant fallback; 3D scenes and charts re-read tokens on change.

**3D rules:** React Three Fiber 9 + drei, lazy and client-only, `frameloop="demand"`, one `instancedMesh` for ≤6k points, dpr ≤1.5, `PerformanceMonitor`. Every 3D view has a data-table twin and a 2D fallback for no-WebGL and `prefers-reduced-motion`.

**Aurora risks handled:** text never sits directly on aurora fields (always on glass ≥0.72 opacity light / tinted dark); contrast tested at the worst-case blob position; `prefers-reduced-transparency` swaps glass for solid panels; blur fields are static images on low-power devices.

**Accessibility:** WCAG 2.2 AA — 4.5:1 text, 24px minimum targets, visible focus, keyboard-only flows, axe checks in CI.

**Versions (checked 2026-11-01):** keep Next.js 15.x, pin React 19.2.x (R3F 9 confirmed for 19.0–19.2), three 0.187, @react-three/fiber 9.8, drei 10.7, motion 14 (`motion/react`), Tailwind 4.3, recharts 3.10, next-themes 0.4.6.

## 8. Security and privacy (course MVP)

Localhost-only by default; strict CORS; request size limits; pydantic validation; prepared SQL; idempotency keys on approve/export; append-only audit log (who, what, model version, prompt hash, checker results); no secrets needed (local model); raw data and outputs gitignored; dataset IDs are already pseudonymous numbers. Auth, tenants and billing are documented future work.

## 9. Testing

pytest (cleaning edge cases, leakage, metrics, API), eval suite for drafts, Vitest for UI logic, Playwright smoke + axe for key flows, GitHub Actions running all of it. The UI shows "not yet run" rather than any number without an artefact.

## 10. Repository and presentation

- Professional README: problem, demo GIF, architecture diagram, outline mapping, real metrics table generated from run files, honest limits, how to run, data licence credit (CC BY 4.0, DOI 10.24432/C5CG6D), image disclosure (ChatGPT Images), no AI co-author credit.
- Git: initialise after owner OK; outline docx stays out of any public remote.
- Image prompts: `assets/IMAGE_GENERATION_PROMPTS.md` (Aurora style series).

## 11. Delivery phases (vertical slices, ~4 h/week)

| Phase | Slice | Done when |
|---|---|---|
| P1 | Data pipeline + profile report + data card | Real counts from local file; checksum recorded; tests pass |
| P2 | Baselines + BG/NBD/GG + GBM + eval on 4 cutoffs | metrics.json per cutoff; leakage tests pass |
| P3 | API + Aurora shell + theme + Overview/Accounts on real artefacts | UI shows real run values with provenance footer |
| P4 | Segments: RFM clusters, 3D galaxy, lookalike scoring | Galaxy renders run data; table twin; fallback |
| P5 | Signals (B) + synthetic social + scraper demo | Each source has licence row in register |
| P6 | Outreach studio (D) + evals + red team | Gate passes; no send path |
| P7 | Basket + pricing lab | Results labelled associational |
| P8 | README, evidence hub, labs index, demo recording | Clean-machine run works |

## 12. Open risks

Solo/group permission and Cloud Lab expectations (coordinator email drafted); 4 h/week vs 120 h nominal; qwen2.5:7b draft quality unmeasured; MAPIE v1 and motion v14 APIs to verify before use; Aurora glass contrast must be measured, not assumed.
