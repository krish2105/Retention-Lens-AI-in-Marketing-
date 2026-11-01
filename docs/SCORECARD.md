# Project scorecard

## Re-score after the third build pass — 2026-11-01 (self-assessed, no agents)

Scored by the builder, so read it as less independent than the reviewer's 73 below. Each change cites new evidence.

| Lens | Reviewer (earlier today) | Now | New evidence | What still caps it |
|---|---|---|---|---|
| CEO | 67 | 67 | Waitlist admin view | No interviews, sign-ups or pilot |
| CMO | 74 | 75 | Reorder logging and week history complete the holdout loop | No campaign has run |
| COO | 75 | 80 | Postgres backend; Postgres load test (p95 85.6 ms) and `pg_dump` restore drill; scheduled backups; uptime check; upload-to-decision funnel | Not hosted; no on-call; no real ops history |
| CTO | 81 | 87 | API suite green on SQLite and Postgres in CI; Supabase RLS verified in CI; Supabase sign-in in the web; axe on all 23 pages | Not deployed; no external security review or pen test |
| AI engineer | 85 | 87 | Peak-season ranges fixed (74.2% → 80.0%, disclosed); per-upload backtest; human labelling UI with live kappa | Critic still has 0 human labels; local model missing; 1/16 live drafts pass |
| Professor | 82 | 84 | R5 results in the app; lab evidence packs; 63 s demo video; refreshed 18-slide deck and 17-page report | Lab reports, reflection and primary research not written |
| Course coverage | 84 | 86 | Exercises log template; evidence page maps every outcome to the new work | Labs and exercises (60% of marks) are the student's to write |
| Real MVP | 73 | 79 | Every screen works on uploaded data; Excel sheet choice; date-reading preview | No usability sessions; no hosted instance |
| Real SaaS | 38 | 46 | Postgres, RLS and Supabase Auth paths tested; waitlist admin | Nothing deployed, no keys, no customers, no support |
| **Mean** | **73** | **77** | | |

**Can code alone reach 95?** No. Every lens below 95 is now capped by evidence only the owner can create:
interviews and a "would pilot" count (CEO, CMO), usability sessions (MVP), a hosted deployment on the owner's
accounts (CTO, COO, SaaS), human labels for the critic plus the local model (AI engineer), the written labs,
exercises log and reflection (Professor, Course), and a pilot with a measured uplift and a paying or LOI
customer (CEO, CMO, SaaS). Each item has a kit or tool in the repository; `project/NEXT_ACTIONS.md` lists them in order.

---

## Re-score after the R1–R8 build — 2026-11-01 (independent reviewer)

Scored by a separate reviewer agent that read the repository cold, ran the ML and API test suites, checked CI
and recomputed report arithmetic. It did not run the browser suites, the load test or the restore drill.

| Lens | Before | After | Why it isn't higher |
|---|---|---|---|
| CEO | 62 | 67 | No interviews, waitlist sign-ups or pilot yet; pricing is a hypothesis |
| CMO | 70 | 74 | Holdout uplift design exists, but no campaign has run or been measured |
| COO | 60 | 75 | Upload, worker, load test and restore drill are real, but only local; backups not scheduled |
| CTO | 72 | 81 | SQLite on one disk; nothing hosted; Postgres RLS written but not applied |
| AI engineer | 78 | 85 | Critic uncalibrated (0/16 labels); 1/16 live drafts pass all checks; peak-season ranges too narrow |
| Professor of AI in Marketing | 80 | 82 | Graded writing and primary research not done |
| Course outline coverage | 82 | 84 | Labs and exercises log (60% of marks) not written |
| Real MVP | 62 | 73 | No usability sessions; no hosted instance |
| Real SaaS | 18 | 38 | Nothing deployed, no keys, no customers, no support process |
| **Unweighted mean** | **65** | **73** | |

Problems the reviewer found, and what was done: peak-season interval coverage (74.2%) was omitted from the
README and case study (now stated); two baseline numbers for the same model (explained: R5 fits net-of-returns
snapshots); a tie on the frozen test was phrased as a win in the LinkedIn kit (reworded); red-team count 22 vs 23
(corrected); stale BLOCKERS, roadmap status and model-card line (updated); the API could start open if a hosted
deploy forgot `RL_AUTH_MODE` (now refused when `RL_ENV=production`, tested). Still open: the restore drill ran on
a near-empty database, and one `/accounts` browser test is timing-flaky locally (passes on retry).

The biggest remaining gains are all owner actions: interviews, usability sessions, labelling drafts, a pilot,
hosting accounts, and the lab reports and exercises log.

---

## Baseline — 2026-11-01 (before the roadmap)

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
