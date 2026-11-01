# Project scorecard — 2026-11-01

An honest assessment of RetentionLens as it stands on `main`: CI green, demo live at https://krish2105.github.io/Retention-Lens-AI-in-Marketing-/. Scores are judgement calls, each with its reasons. Evidence lives in the files named.

| Lens | Score /100 | Why it isn't higher |
|---|---|---|
| CEO | 62 | No customer interviews, pilot or pricing evidence; one 2009–2011 dataset from one company |
| CMO | 70 | Strong insight tools, but no go-to-market assets and no measured campaign outcomes |
| COO | 60 | Customers can't upload their own invoices; single user, no scheduling, monitoring or backups |
| CTO | 72 | No auth or multi-tenancy, API not hosted, no end-to-end browser tests or observability |
| AI engineer | 78 | No uncertainty intervals or seasonality; LLM critic uncalibrated; 7B drafts rarely pass review |
| Professor of AI in Marketing | 80 | Graded labs, slides and report not written yet; social data synthetic; no deep-learning model |
| Course outline coverage | 82 | All outcomes A–D and weeks 1–11 have evidence; assessed deliverables and an exercises log are pending |
| Real MVP | 62 | Works end to end on the reference dataset, but there's no self-serve data import and no user testing |
| Real SaaS | 18 | No accounts, tenants, billing, hosted API, hosted LLM, SLAs or support |
| **Unweighted mean** | **65** | |

## Strengths behind the scores

- **Rigour:**
  - The protocol was fixed before any results were seen, with 4 rolling cutoffs and a frozen test scored once.
  - A leakage test is in place.
  - The negative result is reported honestly: BG/NBD beats LightGBM (`docs/MODEL_CARD.md`).
- **Real data, end to end:** 1,067,371 checksummed lines flow through to 5,852 scored accounts and every screen. No number is typed by hand.
- **Course fit:**
  - **A:** predictive models.
  - **B:** real web data (CC0), the co-purchase network and synthetic social data, all labelled.
  - **C:** CLV, lapse, segments and lookalikes (AUC 0.821).
  - **D:** grounded GenAI with checks, a consent gate and a red team.
  - Weekly topics are mapped on `/evidence`.
- **Responsible AI:**
  - No free text reaches the model.
  - The numeric checker and critic run on every draft.
  - UK PECR consent rules, idempotent approval, an audit log, and no send path.
- **Engineering:** 48 ML tests and 15 API tests, green CI, a static deploy, and an accessibility scan with 0 violations.
- **Design:** distinctive Aurora UI, a theme toggle, 3D terrain and galaxy with table fallbacks, and a working 375 px layout.

## Fastest ways to raise each score

| Lens | Next move | Expected gain |
|---|---|---|
| CEO / CMO | Interview 6–10 wholesalers or account managers; test the pricing hypothesis; publish a landing page | +10 to +15 |
| COO / MVP | CSV upload with schema mapping and validation feedback, reusing P1 flags, so a real business can load its own invoices | +10 to +15 |
| CTO / SaaS | Auth plus per-tenant data (Postgres row-level security), hosted API (Render or Azure Container Apps), monitoring and backups | +15 to +25 for SaaS |
| AI engineer | Label the 16 drafts and calibrate the critic; add seasonality features; add conformal intervals | +5 to +8 |
| Professor / course | Write the five lab reports and the week-6 slides from the scaffolds; get the coordinator's ruling on solo work and "deep learning" | +5 to +10 on assessed marks |
