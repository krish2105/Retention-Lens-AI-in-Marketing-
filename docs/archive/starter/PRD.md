# Product requirements and end-to-end workflow — RetentionLens

## Single job to be done
**User:** Small wholesaler owner or lifecycle marketer. **Problem:** 90-day repeat-purchase and customer value forecasting with human-led account reviews. **Job:** Check accounts with declining purchasing signals, assess expected future purchase range, approve appropriate outreach.
First user: Merchant account manager. Secondary: Marketing lead reviewing customer segments.

## End-to-end acceptance narrative
Given **real, legally permitted, validated input**, the user signs in, creates/selects an organisation, imports or connects data, inspects validation feedback, opens a domain work queue, reviews a calculated/model output with evidence, adjusts or rejects the decision, saves it, exports permitted records, and revisits its outcome later. **Only import/review/demo calculation slices are implemented in starter.**

## Tier P0 — assessed prototype requirements
- Customer/invoice import with cancellation semantics
- RFM summaries and provenance
- Versioned purchase probability and value forecast
- Calibration and cohort dashboard
- Weekly account review with explanation
- Human-approved campaign draft
- Observed follow-up and activity timeline
- Upload validation

## Tier P1 — after primary user validation
- Shopify or POS integrations
- Permissioned web metrics and customer support signals
- Randomized campaign experiments
- Billing and multi-brand

## Deliberate non-goals
- Claiming predicted risk is churn ground truth
- Causal claims without randomized trials
- Messaging customers without consent

## User journey
1. Onboard with example data and a **clearly visible synthetic-data banner**.
2. Import: file validation, preview, schema mapping, source and consent recording, idempotent run ID.
3. Review: see work queue, context, status, source and model/heuristic version.
4. Decide: approve, defer, reject or annotate, where authorised; save who/when/why.
5. Export: include data-version, assumptions and provenance; do not overwrite source.
6. Learn: outcomes and human corrections return to a separately governed evaluation dataset.

## Release acceptance checks
- Import duplicate does not silently double-count; bad rows are reported with row references.
- Changing theme persists between reloads and honours system preference when selected.
- All important actions respond to keyboard focus and show success/error states.
- API rejects bad payloads and separates synthetic rows from future real datasets.
- Domain calculations are tested at zero, boundary and missing-value conditions.
- A reviewer can identify every estimate's source, model/version and assumptions.
- A clean machine can install dependencies and run a smoke check from documented commands.
- Real data is never committed to version control; no secrets in screenshots/logs.

## KPIs that require measurement
**Academic:** 90-day purchase PR-AUC and Brier; monetary MAE and quantile coverage; segment stability; top-k prioritization utility (descriptive, not causal)..
**Workflow:** completion time, reviewer correction count, abandonment, import error rate and support requests; the exact target must be agreed with pilot users.
