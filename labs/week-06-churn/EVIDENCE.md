# Evidence pack: Lab 3 (week 6): churn analysis

Generated 2026-11-01 by `scripts/build_lab_evidence.py` from: `reports/model_results.json`.
Numbers only. The question, interpretation, limitations and write-up are yours to write.

## Lapse (no order in 90 days)

| Cutoff | Role | Model | PR-AUC | ROC-AUC | Brier | Top-10% lift |
|---|---|---|---|---|---|---|
| 2010-12-01 | dev | recency_rule | 0.8038 | 0.6944 | 0.2777 | 1.3450 |
| 2010-12-01 | dev | logistic_rfm | 0.8674 | 0.7911 | 0.2522 | 1.4050 |
| 2010-12-01 | dev | bgnbd | 0.8649 | 0.7884 | 0.1848 | 1.3768 |
| 2010-12-01 | dev | lightgbm | 0.8361 | 0.7585 | 0.2693 | 1.3380 |
| 2011-03-01 | dev | recency_rule | 0.7973 | 0.7261 | 0.1992 | 1.3262 |
| 2011-03-01 | dev | logistic_rfm | 0.8483 | 0.7850 | 0.1822 | 1.3945 |
| 2011-03-01 | dev | bgnbd | 0.8481 | 0.7896 | 0.1721 | 1.3809 |
| 2011-03-01 | dev | lightgbm | 0.8257 | 0.7597 | 0.1826 | 1.3672 |
| 2011-06-01 | dev | recency_rule | 0.8469 | 0.7704 | 0.1777 | 1.3820 |
| 2011-06-01 | dev | logistic_rfm | 0.8860 | 0.8113 | 0.1642 | 1.4397 |
| 2011-06-01 | dev | bgnbd | 0.8888 | 0.8239 | 0.1535 | 1.4124 |
| 2011-06-01 | dev | lightgbm | 0.8821 | 0.8107 | 0.1555 | 1.4215 |
| 2011-09-01 | test | recency_rule | 0.7619 | 0.7493 | 0.2131 | 1.4904 |
| 2011-09-01 | test | logistic_rfm | 0.8144 | 0.7877 | 0.1875 | 1.6177 |
| 2011-09-01 | test | bgnbd | 0.8200 | 0.7987 | 0.1864 | 1.5842 |
| 2011-09-01 | test | lightgbm | 0.8189 | 0.7927 | 0.1938 | 1.5909 |

## Does the challenger win? (claim rule: 3 of 4 cutoffs)

| Comparison | Baseline | LightGBM wins |
|---|---|---|
| lapse_pr_auc | recency_rule | 4 of 4 |
| lapse_pr_auc | logistic_rfm | 1 of 4 |
| lapse_pr_auc | bgnbd | 0 of 4 |
| lapse_brier | recency_rule | 4 of 4 |
| lapse_brier | logistic_rfm | 1 of 4 |
| lapse_brier | bgnbd | 0 of 4 |
| value_gini | naive_last_90 | 4 of 4 |
| value_gini | bgnbd_gamma_gamma | 1 of 4 |
| value_mae | naive_last_90 | 4 of 4 |
| value_mae | bgnbd_gamma_gamma | 2 of 4 |
