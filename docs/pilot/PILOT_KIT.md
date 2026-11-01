# Pilot kit (R6)

Everything needed to run a four-week pilot with one real wholesaler. The pilot itself is the owner's job;
nothing here may be filled with invented results.

## One-page offer (send after a discovery interview that ended in "yes" or "maybe")

> **RetentionLens pilot: four weeks, free, on your own data.**
> Upload a year or more of invoice lines. Each Monday you get a short list of trade accounts most likely to stop
> ordering, the spend at risk, and the reasons. Your team decides who to contact; RetentionLens can draft a
> check-in for you to edit and approve. A random fifth of the list is held back each week so that, at the end,
> we can see whether contacted accounts reordered more than similar ones we left alone.
> You keep your data: export or delete it at any time. We need a signed pilot agreement and data processing
> agreement first.

## Before day 1

- [ ] Signed pilot agreement (scope, 4 weeks, free, either side can stop) and the DPA (`docs/pilot/DPA_TEMPLATE.md`).
- [ ] Hosted API running with `RL_AUTH_MODE=local` or `supabase`, HTTPS, backups scheduled, restore drill run.
- [ ] Workspace created; the customer's owner invited; reviewers invited.
- [ ] Customer confirms they hold a lawful basis to contact their trade customers (UK PECR / UAE PDPL).
- [ ] Agree the outcome measure in writing: reorder within 28 days of being queued, contact arm vs holdout arm.

## Weekly rhythm

| Day | Who | What |
|---|---|---|
| Monday | Customer | Upload the latest invoice export (reorders are detected from it automatically) |
| Monday | Customer | Work through the weekly queue; record a decision for every account |
| During week | Customer | Draft, edit and approve check-ins; send from their own email system |
| Friday | Owner | 15-minute call; log feedback in `research/pilot/feedback-log.csv` |

## Measuring the result (end of week 4 + 28 days)

- The `/queue` page and `GET /api/outcomes` report reorder rates for the contact and holdout arms, the
  difference and a 95% confidence interval (intention to treat).
- With ~25 queued accounts a week for 4 weeks (~80 contact, ~20 holdout), only a large effect will be
  detectable. Say so in the write-up: a CI that crosses zero means "no proven effect", not "it works".
- A case study is written **only** if the customer agrees in writing and the result is real.

## Exit

Export the workspace (`/privacy` → Download my data), hand it to the customer, then delete the workspace
unless they choose a paid plan.
