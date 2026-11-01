# Model card — 90-day lapse and value (P2)

Numbers come from run `20261101T084302Z-test` (`reports/model_results.md`, `.json`). The dev-only run `20261101T084223Z-dev` was made first and gave identical dev numbers. Data: UCI Online Retail II, archive SHA-256 `572e3627…67bfb`. Seed 42.

## Task

For every customer with at least one purchase before a cutoff date, predict:
- **Lapse:** the probability of no purchase in the next 90 days (positive class).
- **Value:** net spend in the next 90 days, floored at £0.

## Protocol (fixed before any result was seen)

- Snapshots at 2010-09-01, 2010-12-01, 2011-03-01, 2011-06-01 and 2011-09-01.
- Evaluated on 2010-12-01, 2011-03-01 and 2011-06-01 (dev), and on **2011-09-01 (frozen test, scored once)**.
- Supervised models train on all earlier snapshots. The code rejects any training label window that crosses the evaluation date.
- BG/NBD and Gamma-Gamma are fitted on the history before each evaluation date.
- Hyperparameters were fixed in code and never tuned.
- Claim rule: one model beats another only if it wins on at least 3 of the 4 evaluation cutoffs.

## Models

| Name | What it is |
|---|---|
| `recency_rule` | Lapse rate per recency decile in the training data |
| `logistic_rfm` | Logistic regression on log recency, frequency, spend and tenure |
| `bgnbd` / `bgnbd_gamma_gamma` | PyMC-Marketing 1.3 BG/NBD (P(no purchase in 90 days)) × Gamma-Gamma spend, MAP fit |
| `lightgbm` | LightGBM 4.7 on 15 behaviour features; lapse classifier + log-spend regressor for buyers |
| `naive_last_90` | Next 90 days' spend = last 90 days' spend |

## Results on the frozen test cutoff (2011-09-01, 5,224 customers, lapse rate 0.572)

| Model | PR-AUC | ROC-AUC | Brier | Top-10% lift |
|---|---|---|---|---|
| `recency_rule` | 0.762 | 0.749 | 0.2131 | 1.49 |
| `logistic_rfm` | 0.814 | 0.788 | 0.1875 | 1.62 |
| `bgnbd` | **0.820** | **0.799** | **0.1864** | 1.58 |
| `lightgbm` | 0.819 | 0.793 | 0.1938 | 1.59 |

| Value model | Normalised Gini | MAE (£) | Predicted total (£) |
|---|---|---|---|
| `naive_last_90` | 0.717 | 382.5 | 1,837,055 |
| `bgnbd_gamma_gamma` | **0.825** | **362.4** | 1,802,398 |
| `lightgbm` | 0.807 | 369.2 | 1,314,807 |

Actual 90-day spend at test: £2,618,168.

## What the evidence supports (all four cutoffs)

- **BG/NBD is the strongest lapse model.** LightGBM beats it on 0 of 4 cutoffs for both PR-AUC and Brier.
- **LightGBM does not beat logistic regression** (PR-AUC 1 of 4, Brier 1 of 4). It reliably beats only the recency rule (4 of 4).
- **For value, BG/NBD + Gamma-Gamma ranks spend best** on 3 of 4 cutoffs; LightGBM wins 1 of 4 on Gini and 2 of 4 on MAE, so no winner claim. Both beat the naive baseline on 4 of 4.
- Conclusion for the research question: on ~4–5k customers and invoice data alone, a classic probabilistic model matches or beats gradient boosting. A neural two-head model (ZILN) is not justified by this evidence and stays optional.

## Known limitations

- **Seasonality is not modelled.** The test window (Sep–Nov) is the Christmas peak. Every model over-predicts lapse there (for example, BG/NBD predicts 0.85 for a bin where the observed rate is 0.77), and every model under-predicts total spend: BG/NBD + Gamma-Gamma by 31%, LightGBM by 50%. Supervised models trained only on 2010-09-01 performed worst at 2010-12-01 for the same reason.
- **Tenure is censored.** History starts on 2009-12-01, so tenure can't exceed the time since then. At later cutoffs, tenure values fall outside the training range.
- **Only one business, from 2009 to 2011.** No campaign data exists, so these are predictions, not effects of outreach.
- **Some data choices affect the population.** Cross-sheet duplicates are removed, and 79 gift-set lines are excluded (see `docs/DATA_CARD.md`).
- **No uncertainty intervals yet.** Conformal intervals (MAPIE) are planned once its v1 API is verified.

## Intended use

Ranking accounts for a human to review each week. It is not for automated contact, credit or pricing decisions.
