# Roadmap to 95+ on every lens

Status: **plan only, not started.** Wait for the owner's go-ahead (Krishna). Baseline scores are from `docs/SCORECARD.md` (2026-11-01).

| Lens | Now | Target | Main gap |
|---|---|---|---|
| CEO | 62 | 95 | No customer evidence, pilot or paid validation |
| CMO | 70 | 95 | No go-to-market assets or measured campaign result |
| COO | 60 | 95 | No self-serve data import, scheduling, monitoring or backups |
| CTO | 72 | 95 | No auth, tenancy, hosted API, end-to-end tests or observability |
| AI engineer | 78 | 95 | No seasonality, intervals or critic calibration; weak drafts |
| Professor | 80 | 95 | Graded writing not done; no primary research; no deep-learning element |
| Course coverage | 82 | 95 | Deliverables and exercises log pending |
| Real MVP | 62 | 95 | No real user data flow or user testing |
| Real SaaS | 18 | 95 | No accounts, tenants, billing, hosting, SLOs or support |

## Honesty rule

Some points can only come from the real world, and code cannot fake them:
- interviews, a pilot with a real wholesaler, a paying customer;
- usability sessions and coordinator rulings.

The plan marks these **[OWNER]**. Without them, CEO, CMO, MVP and SaaS cap at about 75–85, however good the software is. Nothing is fabricated.

---

## Phase R1: Product truth and customer evidence (CEO, CMO, Professor)

**[OWNER] Discovery interviews.** Interview 8–10 wholesale owners or account managers using the guide in `docs/archive/starter/GO_TO_MARKET.md`. Record consent, notes and the pains you hear.

**Synthesis (Claude):**
- Personas, a jobs-to-be-done map and an opportunity tree.
- Pricing hypothesis tests: Van Westendorp questions in the interviews.
- Update the ideal customer profile and positioning.

**Landing page:**
- Value proposition, pricing hypothesis and waitlist form, with consent and no dark patterns.
- Analytics that respect privacy (Plausible or Vercel Analytics).

**Gate:** at least 8 interviews logged, with 3 or more saying "would pilot". Waitlist conversion is measured, not assumed.

**Effort:** 12 h, of which 8 h are the owner's interviews.

## Phase R2: Self-serve MVP (COO, MVP)

**CSV/XLSX upload:**
- Column mapping UI that accepts any header names, reusing `retentionlens.data.load.HEADER_MAP`.
- Validation report built on the P1 flags: row-level errors, duplicates, cancellations.
- Preview before import, with an idempotent import ID.

**Per-dataset scoring job:** upload → clean → snapshot → BG/NBD + Gamma-Gamma → serving rows. Runs as a background job with progress and retries.

**Weekly review loop:**
- A review status per account.
- A "this week" queue.
- Outcome tracking: did the account reorder after contact? This becomes the data for a future uplift test.

**Exports:** approved drafts and the review list as CSV.

**[OWNER] Usability:** 5 usability sessions (think-aloud) on the upload-and-review flow. Record task success and time, then fix the top issues.

**Gate:** a stranger uploads their own invoices and reaches a scored queue in under 10 minutes without help, in 4 of 5 sessions.

**Effort:** 20 h, plus 5 h of the owner's sessions.

## Phase R3: SaaS foundation (CTO, SaaS)

**Stack (researched):**
- Supabase for Postgres, Auth and row-level security. The free tier gives 2 projects, 500 MB of database and 50k monthly active users, and pauses after 7 days idle ([automationatlas](https://automationatlas.io/answers/supabase-free-tier-limits-2026/), [jetadmin](https://www.jetadmin.io/blog/supabase-pricing-2026-guide-to-plans-limits-and-real-world-costs/)).
- API on Render. The free tier sleeps after about 15 minutes with a 30–60 s cold start, and its free Postgres expires, so use Supabase for the database. The $7/month plan avoids the sleep ([costbench](https://costbench.com/software/developer-tools/render/free-plan), [livemy](https://livemy.app/blog/render-pricing)).
- Alternative: Azure Container Apps, using student credit (see the `azure-deploy` skill).

**Tenancy and auth:**
- Organisations, members and roles (owner, reviewer, viewer).
- Every table carries `org_id`, with Postgres row-level security plus checks in the app.
- Cross-tenant isolation tests: a user in org B can never read org A.

**Storage and jobs:**
- Uploads in Supabase Storage, scoped to each org.
- Durable job queue: Postgres-backed jobs or `arq`/RQ.
- Data retention and per-org deletion (a GDPR, UK GDPR and UAE PDPL "delete my data" flow).

**Security:**
- Secrets managed outside the repo.
- Rate limits, CORS allow-list, OWASP ASVS L1 checklist, dependency scanning (pip-audit, npm audit, CodeQL in CI).

**Gate:** two-tenant isolation tests pass in CI; a security checklist is signed off; the hosted API is reachable with sign-in.

**Effort:** 30 h.

## Phase R4: Reliability and operations (COO, CTO)

**Observability:**
- Structured logs, Sentry or OpenTelemetry for errors, and a health dashboard.
- SLOs: API p95 under 500 ms for reads; scoring job under 5 min for 100k lines.

**Data safety:**
- Nightly database backup with a **tested restore drill**.
- Runbook and incident template.
- Load test with k6 or locust, with results recorded.

**End-to-end tests:**
- Playwright suites in CI: the upload flow, review flow and approval flow, plus the mobile and axe audits already scripted.

**Gate:** a restore drill is documented; the load-test report meets the SLOs; end-to-end tests are green in CI.

**Effort:** 15 h.

## Phase R5: Model and AI excellence (AI engineer, Professor)

**Seasonality:** month-of-year and days-to-Christmas features plus same-season training. Re-run the frozen-test protocol with a new frozen cutoff so the old test isn't reused.

**Uncertainty:**
- Conformal intervals for 90-day value (MAPIE v1, checking the API first).
- Interval coverage reported for each cutoff.

**Deep-learning element:** a ZILN two-head network as a *documented challenger*, using the same win-on-3-of-4-cutoffs rule. This meets the rubric's "deep learning" wording honestly, even if it loses.

**GenAI:**
- **[OWNER]** Human labels for `reports/critic_labels.csv` (16 drafts, then 30 more).
- Critic calibration measured with Cohen's kappa.
- Prompt and model iteration against the labelled set: qwen2.5:7b vs a newer local model vs optional Claude Haiku/Sonnet via API key.
- Red-team suite expanded to OWASP LLM Top 10 cases, with CI gating on deterministic checks.

**Monitoring:** drift checks on score distribution, and a model registry with versioned artefacts.

**Gate:** seasonality closes at least 50% of the peak-season spend gap; interval coverage is within ±5% of nominal; kappa ≥ 0.6; draft pass rate ≥ 80% on the labelled set.

**Effort:** 25 h, plus 3 h of the owner's labelling.

## Phase R6: Commercial readiness (CEO, CMO, SaaS)

**Billing:** Stripe in **test mode** first, with plans from the validated pricing, usage metering per active account and an entitlements check.

**Go-to-market:**
- Pilot offer one-pager, onboarding checklist and terms of service.
- Privacy notice (UK GDPR / PECR / UAE PDPL wording), data processing agreement template and a status page.

**[OWNER] Pilot:**
- One real wholesaler on their own data for 4 weeks, with written consent and a data agreement.
- Weekly feedback is logged, and outcomes are measured: accounts reactivated vs a holdout group, so the effect is *causal*.

**Marketing evidence:**
- A small randomised outreach test inside the pilot: contacted vs not contacted.
- A case study only if the result is real.

**Gate:** a signed pilot; a measured reactivation-uplift result with a confidence interval; at least one paid or letter-of-intent customer for SaaS 95.

**Effort:** 15 h, plus the owner's sales time.

## Phase R7: Academic excellence and course completeness (Professor, Course)

**Labs:** five lab reports written by the owner from the `labs/` scaffolds. Claude reviews against the rubric but does not ghost-write.

**Presentation and report:**
- Week-6 presentation slides (generated from results, owner's narrative), with a rehearsed demo and a recorded video.
- Final project report v2 with interviews (R1), usability (R2), the pilot (R6), the deep-learning challenger and seasonality (R5), a literature review and limitations.

**Coursework admin:** an exercises log for every session; coordinator rulings recorded (solo submission, Cloud Lab, "deep learning").

**Viva preparation:** the 8 viva questions in `docs/VIVA_AND_SUBMISSION.md` answered with evidence links.

**Gate:** every rubric row in outline section 3 has evidence; every outcome A–D has a primary-research or experiment artefact.

**Effort:** 25 h (owner-led).

## Phase R8: Polish and proof (all lenses)

**Product and design:** an onboarding tour, a recorded 3-minute demo, internationalisation of number and date formats (en-GB / en-AE), an Arabic right-to-left smoke test for the UAE, and a refreshed screenshot set.

**Documentation:** README v3, a case study, CV bullets and a LinkedIn post (`proof-of-work` skill, real numbers only).

**Final check:** a scorecard re-run by an independent reviewer subagent, with each score tied to evidence.

**Effort:** 10 h.

---

## Order, dependencies and time

| Order | Phase | Depends on | Hours (Claude + owner) |
|---|---|---|---|
| 1 | R1 customer evidence | none | 12 |
| 2 | R2 self-serve MVP | R1 insights | 25 |
| 3 | R3 SaaS foundation | R2 data model | 30 |
| 4 | R5 model and AI | none (parallel to R3) | 28 |
| 5 | R4 reliability | R3 | 15 |
| 6 | R6 commercial and pilot | R2, R3, R4 | 15+ |
| 7 | R7 academic | R1, R2, R5, R6 results | 25 |
| 8 | R8 polish | all | 10 |

**Total: about 160 hours.** At 4 h/week this takes about 40 weeks, much longer than the term. To finish in about 12 weeks the project needs about 13 h/week, or the targets need re-scoping. A realistic in-term target is 95 on Professor, Course and AI engineer, and 85–90 on the others, unless a real pilot and a paying customer arrive.

## Rules carried forward

- No fabricated data, interviews, results or customers.
- No Claude credit in commits or the README.
- Push at every milestone.
- Every number in the UI or report comes from a run file.
- Real customer data only with written consent and after R3 (auth plus tenancy).
