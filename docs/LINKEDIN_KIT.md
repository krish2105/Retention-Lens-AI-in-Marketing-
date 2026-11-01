# LinkedIn and CV kit (real numbers only)

![LinkedIn image](../apps/web/public/img/aur-27-linkedin.webp)

Every number comes from the run files listed in `docs/CASE_STUDY.md`. Post only after the project owner
has read and edited it in their own voice.

## LinkedIn post draft (about 200 words)

> My gradient-boosting model lost. That turned out to be the most useful result of my AI in Marketing project.
>
> RetentionLens predicts which wholesale trade accounts will stop ordering in the next 90 days. On 1,067,371
> real invoice lines (UCI Online Retail II), I fixed the evaluation first: rolling time cutoffs and a frozen
> test scored once. A classic BG/NBD + Gamma-Gamma model beat LightGBM, reaching a lapse PR-AUC of 0.820 on
> 5,224 customers.
>
> The bigger error was seasonality. A simple same-window-last-year multiplier cut the total-spend bias by 49%
> on the development cutoffs. A zero-inflated lognormal neural network was tested too, and lost.
>
> The product side: self-serve CSV upload, a weekly review queue that holds out a random fifth of accounts so
> outreach can be measured properly, and AI-drafted emails from a local model that a person must approve.
> There is no send button.
>
> Next step is the part code can't do: talking to wholesalers and running a real pilot.
>
> Demo and code: https://retentionlens-demo.vercel.app · https://github.com/krish2105/Retention-Lens-AI-in-Marketing-
>
> #MarketingAnalytics #CustomerRetention #ResponsibleAI

Suggested image: the case-study cover above, or a screenshot of the weekly queue with the holdout count.

## CV bullets: AI/ML Analyst

1. Built RetentionLens, a churn and CLV system on 1,067,371 invoice lines (PyMC-Marketing, LightGBM, FastAPI, Next.js); BG/NBD beat LightGBM with 0.820 PR-AUC on a frozen test of 5,224 customers.
2. Added seasonality and 80% split-conformal value ranges to a BG/NBD + Gamma-Gamma model, cutting total-spend bias 49% and reaching 79.5–82.4% interval coverage across three time-based validation cutoffs.
3. Shipped a grounded GenAI outreach tool on a local open model with deterministic output checks, 22 OWASP LLM red-team tests in CI and human approval, with no automated send path.

## CV bullets: AI Business Analyst

1. Turned 1,067,371 wholesale invoice lines into a weekly at-risk account queue for sales teams, with plain-language reasons and spend-at-risk per account, validated on a frozen test (PR-AUC 0.820).
2. Designed a randomised holdout into the weekly workflow so retention outreach can be measured causally, reporting contact vs holdout reorder rates with a 95% confidence interval.
3. Wrote the pilot kit, DPA template, UK GDPR / PECR / UAE PDPL privacy notice and ASVS security checklist for a multi-tenant SaaS, with export and delete-my-data controls.

## 90-second demo script

| Time | Show | Say / on-screen text |
|---|---|---|
| 0–10 s | Landing page | "Trade accounts don't complain before they leave. They just stop ordering." |
| 10–25 s | Upload the synthetic sample, map columns, check | "Any invoice export. Every rejected row is listed, nothing is guessed." |
| 25–55 s | Scoring progress → weekly queue → open an account | "Lapse risk, expected spend with a range, and reasons you can say out loud. A fifth are held out at random." |
| 55–75 s | Model lab, then draft and approve an email | "Tested on a frozen set: simple models won. The AI drafts from facts only; you approve; there is no send button." |
| 75–90 s | Case study page | "Next: a real pilot. Demo and code at the link." |

## To measure next

Interview count and "would pilot" share; waitlist conversion; usability task success and time; critic kappa
against human labels; pilot uplift with a confidence interval.
