# Evidence pack: Lab 2 (week 4): customer lifetime value

Generated 2026-11-01 by `scripts/build_lab_evidence.py` from: `reports/model_results.json`, `reports/r5_results.json`.
Numbers only. The question, interpretation, limitations and write-up are yours to write.

## 90-day value by cutoff (P2 protocol)

| Cutoff | Role | Model | Normalised Gini | MAE (£) | Total actual | Total predicted |
|---|---|---|---|---|---|---|
| 2010-12-01 | dev | naive_last_90 | 0.7685 | 498.2927 | 1326622.9200 | 2952863.5900 |
| 2010-12-01 | dev | bgnbd_gamma_gamma | 0.8018 | 375.6527 | 1326622.9200 | 2208849.0568 |
| 2010-12-01 | dev | lightgbm | 0.8071 | 480.9014 | 1326622.9200 | 2738719.2400 |
| 2011-03-01 | dev | naive_last_90 | 0.6823 | 289.5707 | 1427532.5800 | 1570176.0600 |
| 2011-03-01 | dev | bgnbd_gamma_gamma | 0.8111 | 300.5876 | 1427532.5800 | 1910561.5038 |
| 2011-03-01 | dev | lightgbm | 0.7751 | 268.2769 | 1427532.5800 | 1359407.5959 |
| 2011-06-01 | dev | naive_last_90 | 0.7578 | 271.0420 | 1624712.9100 | 1656138.9900 |
| 2011-06-01 | dev | bgnbd_gamma_gamma | 0.8509 | 278.0517 | 1624712.9100 | 1832922.1017 |
| 2011-06-01 | dev | lightgbm | 0.8445 | 260.4596 | 1624712.9100 | 1170908.2191 |
| 2011-09-01 | test | naive_last_90 | 0.7170 | 382.5112 | 2618168.0900 | 1837054.7400 |
| 2011-09-01 | test | bgnbd_gamma_gamma | 0.8246 | 362.4455 | 2618168.0900 | 1802398.2203 |
| 2011-09-01 | test | lightgbm | 0.8072 | 369.1648 | 2618168.0900 | 1314806.7642 |

## R5: seasonality and value ranges (dev cutoffs select; 2011-09-01 is post hoc)

| Cutoff | Model | Total-spend bias | MAE (£) |
|---|---|---|---|
| 2010-12-01 | bgnbd_gamma_gamma | +61.8% | 366.0 |
| 2010-12-01 | bgnbd_gamma_gamma_seasonal | +30.4% | 323.4 |
| 2010-12-01 | lightgbm | +106.4% | 480.9 |
| 2010-12-01 | lightgbm_seasonal | +106.4% | 480.9 |
| 2010-12-01 | ziln_nn | +153.7% | 558.0 |
| 2011-03-01 | bgnbd_gamma_gamma | +28.5% | 289.8 |
| 2011-03-01 | bgnbd_gamma_gamma_seasonal | +19.7% | 279.8 |
| 2011-03-01 | lightgbm | -4.8% | 268.3 |
| 2011-03-01 | lightgbm_seasonal | +76.0% | 390.9 |
| 2011-03-01 | ziln_nn | +37.3% | 329.1 |
| 2011-06-01 | bgnbd_gamma_gamma | +8.5% | 270.5 |
| 2011-06-01 | bgnbd_gamma_gamma_seasonal | +0.2% | 265.4 |
| 2011-06-01 | lightgbm | -27.9% | 260.5 |
| 2011-06-01 | lightgbm_seasonal | +4.2% | 294.8 |
| 2011-06-01 | ziln_nn | +22.1% | 295.4 |
| 2011-09-01 | bgnbd_gamma_gamma | -33.5% | 359.7 |
| 2011-09-01 | bgnbd_gamma_gamma_seasonal | -7.1% | 360.0 |
| 2011-09-01 | lightgbm | -49.8% | 369.2 |
| 2011-09-01 | lightgbm_seasonal | -20.7% | 378.6 |
| 2011-09-01 | ziln_nn | -28.7% | 372.8 |

| Cutoff | Interval calibration | Coverage (target 80%) | Median width (£) |
|---|---|---|---|
| 2010-12-01 | bgnbd_gamma_gamma | 72.8% | 1,064 |
| 2010-12-01 | bgnbd_gamma_gamma_seasonal | 79.5% | 858 |
| 2010-12-01 | seasonal_same_window_last_year | 79.5% | 858 |
| 2010-12-01 | seasonal_pooled | 79.5% | 858 |
| 2011-03-01 | bgnbd_gamma_gamma | 81.4% | 229 |
| 2011-03-01 | bgnbd_gamma_gamma_seasonal | 82.2% | 264 |
| 2011-03-01 | seasonal_same_window_last_year | 89.0% | 407 |
| 2011-03-01 | seasonal_pooled | 85.1% | 312 |
| 2011-06-01 | bgnbd_gamma_gamma | 82.4% | 252 |
| 2011-06-01 | bgnbd_gamma_gamma_seasonal | 82.4% | 250 |
| 2011-06-01 | seasonal_same_window_last_year | 86.9% | 292 |
| 2011-06-01 | seasonal_pooled | 84.7% | 266 |
| 2011-09-01 | bgnbd_gamma_gamma | 70.8% | 214 |
| 2011-09-01 | bgnbd_gamma_gamma_seasonal | 74.2% | 323 |
| 2011-09-01 | seasonal_same_window_last_year | 84.6% | 621 |
| 2011-09-01 | seasonal_pooled | 80.0% | 456 |
