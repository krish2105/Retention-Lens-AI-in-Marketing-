# R5 results: seasonality, value intervals and the ZILN challenger

Generated 2026-11-01T15:27:16+00:00 · seed 42 · selection on dev cutoffs 2010-12-01, 2011-03-01, 2011-06-01 only.
The 2011-09-01 cutoff was scored once in P3; it appears below only as a labelled post-hoc look, not for choosing models.

## Summary

- Seasonal multiplier cut BG/NBD + Gamma-Gamma's mean absolute total-spend bias on dev cutoffs from 32.9% to 16.8% (49% reduction).
- Post-hoc, on the Sep–Nov peak window: 79% of the total-spend gap closed (optimistic: this window was seen before).
- 80% conformal intervals covered 79.5%, 82.2%, 82.4% of accounts on the dev cutoffs (within ±5 points: yes).
- ZILN network vs BG/NBD: lapse PR-AUC wins 0/3, value Gini wins 1/3, value MAE wins 0/3. The claim rule needs a win on every dev cutoff.

## Decisions

- **Adopted:** the seasonal multiplier in serving (it beat plain BG/NBD on lapse Brier and value MAE on 3 of 3 dev cutoffs; PR-AUC and Gini cannot change because it rescales every account equally).
- **Adopted (R5b):** 80% split-conformal value ranges calibrated on residuals pooled from the previous 90 days and the same window last year. Previous-90-days alone was best on dev (mean error 1.7 points) but covered only 74.2% on the peak window; pooled is within 5 points on every dev cutoff (mean error 3.4) and covered 80.0% on the peak. The peak window was already seen, so this choice is informed by it.
- **Not adopted:** the ZILN network (0 of 3 dev wins on lapse PR-AUC and value MAE). It is kept as the documented deep-learning challenger.
- **Not adopted:** seasonal features for LightGBM (mixed: wins 2 of 3 on PR-AUC, worse calibration).
- **Gate check:** the roadmap asked for 50% of the peak-season spend gap closed. On dev cutoffs (none of which is the peak) the bias fell 49%; on the peak window, post hoc, 79%. Read the second number with care.

## ZILN versions (disclosed because the changes were made after seeing dev results)

- v1: unbounded spread, all seasonal features. Spend predictions diverged (constant training features divided by a near-zero spread).
- v2: constant training features zeroed, spread bounded to [0.05, 2]. Still diverged at 2011-03-01 (calendar features extrapolated).
- v3 (reported): calendar features dropped; customer-level last-year features kept. No further tuning.

## By cutoff

### 2010-12-01 (dev, 4,239 customers, season multiplier 0.8059)

| Model | Lapse PR-AUC | Brier | Value Gini | Value MAE | Total-spend bias |
|---|---|---|---|---|---|
| bgnbd_gamma_gamma | 0.865 | 0.1848 | 0.800 | 366.0 | +61.8% |
| bgnbd_gamma_gamma_seasonal | 0.865 | 0.1736 | 0.800 | 323.4 | +30.4% |
| lightgbm | 0.836 | 0.2693 | 0.807 | 480.9 | +106.4% |
| lightgbm_seasonal | 0.836 | 0.2693 | 0.807 | 480.9 | +106.4% |
| ziln_nn | 0.862 | 0.2480 | 0.817 | 558.0 | +153.7% |

| Intervals (80%) | Calibrated on | Coverage | Median width |
|---|---|---|---|
| bgnbd_gamma_gamma | 2010-09-01 | 72.8% | £1,064 |
| bgnbd_gamma_gamma_seasonal | 2010-09-01 | 79.5% | £858 |
| seasonal_same_window_last_year | 2010-09-01 | 79.5% | £858 |
| seasonal_pooled | 2010-09-01 | 79.5% | £858 |

### 2011-03-01 (dev, 4,512 customers, season multiplier 0.9315)

| Model | Lapse PR-AUC | Brier | Value Gini | Value MAE | Total-spend bias |
|---|---|---|---|---|---|
| bgnbd_gamma_gamma | 0.848 | 0.1721 | 0.810 | 289.8 | +28.5% |
| bgnbd_gamma_gamma_seasonal | 0.848 | 0.1701 | 0.810 | 279.8 | +19.7% |
| lightgbm | 0.826 | 0.1826 | 0.775 | 268.3 | -4.8% |
| lightgbm_seasonal | 0.835 | 0.2389 | 0.801 | 390.9 | +76.0% |
| ziln_nn | 0.812 | 0.1873 | 0.768 | 329.1 | +37.3% |

| Intervals (80%) | Calibrated on | Coverage | Median width |
|---|---|---|---|
| bgnbd_gamma_gamma | 2010-12-01 | 81.4% | £229 |
| bgnbd_gamma_gamma_seasonal | 2010-12-01 | 82.2% | £264 |
| seasonal_same_window_last_year | 2010-03-02 | 89.0% | £407 |
| seasonal_pooled | 2010-03-02 | 85.1% | £312 |

### 2011-06-01 (dev, 4,908 customers, season multiplier 0.9239)

| Model | Lapse PR-AUC | Brier | Value Gini | Value MAE | Total-spend bias |
|---|---|---|---|---|---|
| bgnbd_gamma_gamma | 0.889 | 0.1535 | 0.852 | 270.5 | +8.5% |
| bgnbd_gamma_gamma_seasonal | 0.889 | 0.1526 | 0.852 | 265.4 | +0.2% |
| lightgbm | 0.882 | 0.1555 | 0.845 | 260.5 | -27.9% |
| lightgbm_seasonal | 0.882 | 0.1762 | 0.850 | 294.8 | +4.2% |
| ziln_nn | 0.884 | 0.1554 | 0.845 | 295.4 | +22.1% |

| Intervals (80%) | Calibrated on | Coverage | Median width |
|---|---|---|---|
| bgnbd_gamma_gamma | 2011-03-01 | 82.4% | £252 |
| bgnbd_gamma_gamma_seasonal | 2011-03-01 | 82.4% | £250 |
| seasonal_same_window_last_year | 2010-06-02 | 86.9% | £292 |
| seasonal_pooled | 2010-06-02 | 84.7% | £266 |

### 2011-09-01 (post hoc test, 5,224 customers, season multiplier 1.3976)

| Model | Lapse PR-AUC | Brier | Value Gini | Value MAE | Total-spend bias |
|---|---|---|---|---|---|
| bgnbd_gamma_gamma | 0.820 | 0.1864 | 0.825 | 359.7 | -33.5% |
| bgnbd_gamma_gamma_seasonal | 0.820 | 0.1785 | 0.825 | 360.0 | -7.1% |
| lightgbm | 0.819 | 0.1938 | 0.807 | 369.2 | -49.8% |
| lightgbm_seasonal | 0.818 | 0.1830 | 0.804 | 378.6 | -20.7% |
| ziln_nn | 0.821 | 0.1862 | 0.799 | 372.8 | -28.7% |

| Intervals (80%) | Calibrated on | Coverage | Median width |
|---|---|---|---|
| bgnbd_gamma_gamma | 2011-06-01 | 70.8% | £214 |
| bgnbd_gamma_gamma_seasonal | 2011-06-01 | 74.2% | £323 |
| seasonal_same_window_last_year | 2010-09-02 | 84.6% | £621 |
| seasonal_pooled | 2010-09-02 | 80.0% | £456 |

