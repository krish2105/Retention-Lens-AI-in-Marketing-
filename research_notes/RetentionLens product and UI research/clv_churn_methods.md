# CLV, churn, segmentation and pricing/brand analytics methods for RetentionLens (UCI Online Retail II)

Research date: 2026-11-01. Researcher: subagent (web search + fetch, 19 tool calls).

Evidence labels used throughout (per AGENTS.md):
- **VERIFIED (fetched)**: the page was fetched or returned by search in this session and the claim was read there.
- **CANONICAL REF (not fetched)**: a well-known primary reference whose URL is given for the report writer, but whose content was NOT fetched this session. Treat it as "check before quoting".
- **INFERENCE / ASSUMPTION / TODO**: the researcher's reasoning, not a sourced fact.

---

## 1. Probabilistic CLV (BTYD): BG/NBD, Pareto/NBD, MBG/NBD, Gamma-Gamma, plus 2026 library status

### Takeaway
BG/NBD + Gamma-Gamma is still the defensible baseline for non-contractual CLV. In November 2026 the maintained Python implementation is **PyMC-Marketing 1.3.0** (Oct 22, 2026). `lifetimes` has been archived and read-only since June 28, 2024, and names PyMC-Marketing as its successor. On Online Retail II, the main known failure modes are the Nov-Dec seasonality, one-time buyers being "alive" by construction, and the Gamma-Gamma independence assumption.

### Cited Findings
**Original models (VERIFIED for BG/NBD bibliographic facts)**
- Fader, Hardie & Lee (2005), "'Counting Your Customers' the Easy Way: An Alternative to the Pareto/NBD Model", *Marketing Science* 24(2):275-284, DOI 10.1287/mksc.1040.0098. BG/NBD tells "a slightly different behavioral story" about dropout than Pareto/NBD and is far easier to estimate (it can be done in Excel). Across purchasing settings the two models gave very similar results — [EconPapers](https://econpapers.repec.org/RePEc:inm:ormksc:v:24:y:2005:i:2:p:275-284); [core.ac.uk](https://core.ac.uk/display/6438828)
- Free working-paper PDF (2004 revision) — [brucehardie.com](https://www.brucehardie.com/papers/bgnbd_2004-04-20.pdf); Excel implementation note — [brucehardie.com note 004](https://brucehardie.com/notes/004/bgnbd_spreadsheet_note.pdf)
- Pareto/NBD comes from Schmittlein et al. (1987). Its estimation was historically hard, which motivated BG/NBD — [EconPapers](https://econpapers.repec.org/RePEc:inm:ormksc:v:24:y:2005:i:2:p:275-284)
- Recent arXiv work on a simpler, numerically stable BG/NBD churn formulation: arXiv 2502.12912 — [arXiv](https://arxiv.org/pdf/2502.12912) (VERIFIED via search result title only; contents not read)

**Model assumptions and quirks (VERIFIED from PyMC-Marketing CLV quickstart)**
- Input is one row per customer with `customer_id`, `frequency` (= repeat purchases = total purchases − 1), `recency` (time from first to last purchase, 0 for one-time buyers), `T` (time from first purchase to the end of the calibration period), and `monetary_value` (**mean** of the repeat purchases, not the sum; 0 for one-time buyers). Monetary value can be revenue or profit if it is calculated consistently — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- BG/NBD quirk: customers with no repeat purchase get P(alive) = 1 (the docs call this a "quirk"). ParetoNBDModel is the suggested alternative — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- Gamma-Gamma needs customers with `frequency > 0` and assumes spend is independent of frequency. The quickstart checks this with a Pearson correlation, using < 0.3 as the rule of thumb; CDNOW gives 0.053 — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- The quickstart validates on CDNOW with a 52-week calibration period and a 26-week holdout. MAP and MCMC estimates come out close — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)

**Library status, November 2026 (VERIFIED)**
- **`lifetimes`** was archived on Jun 28, 2024 and is read-only. The README says maintainers "won't be adding new features, improvements, or even answering issues" and that "A project has emerged as a successor to lifetimes" (PyMC-Marketing). **DEPRECATED, do not use for new work** — [GitHub CamDavidsonPilon/lifetimes](https://github.com/CamDavidsonPilon/lifetimes)
- **PyMC-Marketing**: version 1.3.0, released Oct 22, 2026, Python >= 3.12 (classifiers list 3.12-3.14), Apache-2.0. It covers contractual and non-contractual settings and discrete and continuous time — [PyPI pymc-marketing](https://pypi.org/project/pymc-marketing/)
- `pymc_marketing.clv.models` submodules: `basic`, `beta_geo` (BG/NBD), `beta_geo_beta_binom` (BG/BB, discrete time), `gamma_gamma`, `modified_beta_geo` (MBG/NBD), `pareto_nbd`, `shifted_beta_geo` (sBG, contractual) — [PyMC-Marketing API: clv.models](https://www.pymc-marketing.io/en/stable/api/generated/pymc_marketing.clv.models.html)
- Exact API names seen in the quickstart: `from pymc_marketing import clv`; `clv.utils.rfm_summary(raw_trans, customer_id_col=..., datetime_col=..., monetary_value_col=..., datetime_format=..., time_unit="W")`; `clv.utils.rfm_train_test_split(..., train_period_end=...)` (adds `test_frequency`, `test_monetary_value`, `test_T`); `clv.BetaGeoModel(data=...)` with `.build_model()`, `.fit(method="map")` (MCMC by default), `.fit_summary()`, `.expected_purchases(future_t=...)`, `.expected_purchases_new_customer(t=...)`, `.expected_probability_alive(data=...)`, `.thin_fit_result(keep_every=...)`; `clv.GammaGammaModel` with `.expected_customer_spend(data=...)`, `.expected_new_customer_spend()`, `.expected_customer_lifetime_value(transaction_model=bgm, data=..., future_t=12, discount_rate=0.01, time_unit="W")`; plotting helpers `clv.plot_frequency_recency_matrix`, `clv.plot_probability_alive_matrix`, `clv.plot_expected_purchases_over_time`, `clv.plot_customer_exposure` — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- The quickstart imports `arviz_plots` and `arviz_base`, which points to the newer ArviZ 1.x split-package stack. Pin versions accordingly — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- Core PyMC 6.0.0 makes numba the default backend. Core PyMC 5.28.5 was published May 1, 2026 — [newreleases.io PyMC 6.0.0](https://newreleases.io/project/github/pymc-devs/pymc/release/v6.0.0); [Zenodo PyMC v5.28.5](https://zenodo.org/records/19952458)

**Online Retail II specifics (VERIFIED)**
- 1,067,371 rows covering 01/12/2009 to 09/12/2011 from a UK non-store online retailer of all-occasion giftware, with many wholesale customers. Variables: Invoice, StockCode, Description, Quantity, InvoiceDate, Price (GBP), Customer ID, Country. Invoices starting with "C" are cancellations. The data has missing values. License CC BY 4.0, DOI 10.24432/C5CG6D, creator Daqing Chen — [UCI dataset 502](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

**Community (non-peer-reviewed) BTYD fits on Online Retail II (VERIFIED as claims in READMEs, not independently reproduced)**
- One repo fits BG/NBD and Gamma-Gamma on the UK subset. It reports about 71% repeat customers and dropout parameters of roughly a ≈ 0.11, b ≈ 2.82. Its out-of-time check under-predicts the Nov-Dec holiday window, which the author attributes to seasonality the model cannot capture — [GitHub Psytwin-24/customer-lifetime-value](https://github.com/Psytwin-24/customer-lifetime-value)
- Another repo implements BG/NBD and Gamma-Gamma from scratch. It claims "-2% error on next-26-week purchases vs +68% naive" (holdout around Jun-Dec 2011) and notes that one-time buyers are "alive" by construction — [GitHub Rxyxs/customer-lifetime-value](https://github.com/Rxyxs/customer-lifetime-value)

### Inferences
- Recommended baseline: `clv.BetaGeoModel` (MAP first, then MCMC for credible intervals) + `clv.GammaGammaModel`, fitted on a weekly `rfm_summary`. Add `ParetoNBDModel` and `ModifiedBetaGeoModel` as robustness checks: MBG/NBD lets one-time buyers drop out, which removes the P(alive)=1 quirk that matters for a wholesaler with many single-invoice customers.
- When BTYD fails on this data: (a) seasonality, since stationary purchase rates break across Nov-Dec peaks, so pick a holdout that contains a full season or report a seasonal residual; (b) wholesalers with very large orders violate the Gamma-Gamma homogeneity and heavy-tail assumptions, so cap or log values and report the frequency-spend correlation; (c) returns/cancellations must be netted or excluded consistently before computing `monetary_value`; (d) rows with missing Customer ID cannot enter any customer-level model. Report the share dropped and do NOT impute IDs.
- Mark Gamma-Gamma CLV as the expected value of a stochastic model (SYNTHETIC/MODEL OUTPUT), not an observed value.

### Gaps
- `btyd` (the lifetimes fork): PyPI page did not load this session, so its 2026 version and maintenance status are **not verified**. Treat it as an unverified alternative and prefer PyMC-Marketing.
- The exact class name for MBG/NBD (likely `ModifiedBetaGeoModel`) and for Pareto/NBD (`ParetoNBDModel`, which is named in the quickstart) should be confirmed against the 1.3.0 module pages. Only submodule names were verified.
- MBG/NBD original paper (Batislam, Denizel & Filiztekin, 2007) and Gamma-Gamma original (Fader, Hardie & Lee, 2005, "RFM and CLV: Using iso-value curves", *JMR*): CANONICAL REFS, not fetched. Bruce Hardie's note "The Gamma-Gamma Model of Monetary Value" is at https://www.brucehardie.com/notes/025/gamma_gamma.pdf (not fetched).
- No peer-reviewed paper was found that reports BTYD accuracy on Online Retail II specifically.

---

## 2. ML/DL CLV: ZILN, two-head networks, gradient boosting, sequence models; published Online Retail results

### Takeaway
Wang, Liu & Miao (2019) model LTV as a zero point mass plus a lognormal, using the ZILN loss, and recommend the **normalized Gini** for discrimination and **decile charts** for calibration. The reference repo `google/lifetime_value` was **archived on Apr 18, 2026**, so re-implement the loss (about 20 lines) instead of depending on that package. No peer-reviewed benchmark numbers on Online Retail I or II were found for any ML CLV model.

### Cited Findings
- Wang, Liu & Miao, "A Deep Probabilistic Model for Customer Lifetime Value Prediction", arXiv:1912.07753 (Dec 16, 2019). LTV is modeled as a zero point mass mixed with a lognormal (ZILN loss). This captures churn probability and heavy tails in one model and quantifies uncertainty. It works for linear models and DNNs. The paper recommends normalized Gini for discrimination and decile charts for calibration. The abstract contains no numeric results — [arXiv 1912.07753](https://arxiv.org/abs/1912.07753)
- Reference implementation `google/lifetime_value`: a Keras ZILN loss, Apache-2.0, with notebooks on the Kaggle Acquire Valued Shoppers Challenge (>300k shoppers, ~350M rows; top-20 companies; regression and classification) and KDD Cup 98 (~200k lapsed donors). The README reports no benchmark numbers. **Archived Apr 18, 2026 (read-only)** — [GitHub google/lifetime_value](https://github.com/google/lifetime_value)
- Gadgil, Gill & Abdelmoniem (2023), "A Meta-learning based Stacked Regression Approach for Customer Lifetime Value Prediction", arXiv:2308.08502. It stacks bagging and boosting regressors and evaluates on "an openly available Online Retail dataset" (the abstract does not say whether that is version I or II). The abstract reports **no numeric metrics** — [arXiv 2308.08502](https://arxiv.org/abs/2308.08502)
- That paper cites Jasek et al., "Modeling and application of customer lifetime value in online retail" — [arXiv 2308.08502 PDF](https://arxiv.org/pdf/2308.08502) (citation seen in search snippet; Jasek paper not fetched)
- Chamberlain et al., "Customer Lifetime Value Prediction Using Embeddings", arXiv:1703.02596 (ASOS), is an example of embedding-based CLV at scale — [arXiv 1703.02596](https://arxiv.org/pdf/1703.02596) (title verified via search only)

### Inferences
- Honest ML stack for a student project:
  1. **Baseline 0:** a naive "last-period spend = next-period spend" or historical mean, which every model must beat.
  2. **Baseline 1:** BTYD (section 1).
  3. **Baseline 2:** LightGBM/XGBoost/CatBoost on RFM + behavioural features at a cutoff date, with two targets: P(purchase in the next H days) as a classifier and 12-month (or H-day) spend as a regressor, using Tweedie or log1p targets.
  4. **Advanced model (pick one):** a two-head MLP or a GBM-plus-ZILN head. The ZILN head outputs p(purchase), mu and sigma, and the expected value is p·exp(mu + sigma²/2). That gives one model for churn probability and conditional spend, with intervals from the lognormal.
- Transformer and sequence models over invoice sequences are defensible only as a stretch goal. Online Retail II has about 2 years of history and a few thousand identified customers (ASSUMPTION; verify the count from data), so deep sequence models will likely not beat GBMs. Report that honestly if it happens.
- Any CLV result on Online Retail II should be labelled "our run, our split". There is no accepted public leaderboard to compare against.

### Gaps
- No peer-reviewed numeric benchmark (Gini, MAE, RMSE, decile MAPE) for Online Retail I or II CLV was found. **Benchmark numbers: NOT FOUND.**
- ZILN paper datasets and numbers (beyond the abstract) were not read, so its full-text results are not quoted here.
- Transformer-for-CLV papers were not searched within the budget. TODO if the student pursues the stretch goal.
- LightGBM, XGBoost and CatBoost 2026 versions were not verified this session.

---

## 3. Churn in non-contractual settings: definition, leakage and evaluation protocol

### Takeaway
In a non-contractual setting churn is not observed, so it has to be **defined**. Use "no purchase in the H days after a cutoff date", features computed strictly before the cutoff, rolling-origin temporal validation, and report discrimination (PR-AUC, ROC-AUC, top-k precision, lift and gain), calibration (Brier score, reliability curve) and value-weighted metrics (normalized Gini, decile tables). Compare against BTYD 1 − P(alive) as a baseline score.

### Cited Findings
- One community project on Online Retail II uses a 12-week observation window, a 1-week gap, labels churn = 1 when there are 0 transactions in the prediction window, compares LR, XGBoost, LightGBM and CatBoost, chooses thresholds by maximizing F1, and evaluates on a time-based holdout (scores not visible in the snippet; not peer-reviewed) — [daffadaniel.github.io churn modelling](https://daffadaniel.github.io/05-ChurnModelling/)
- The PyMC-Marketing train/test pattern (`rfm_train_test_split` with `train_period_end`) gives the calibration/holdout split used by BTYD, and P(alive) comes from `expected_probability_alive` — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- ZILN authors recommend normalized Gini (discrimination) and decile charts (calibration) for value predictions — [arXiv 1912.07753](https://arxiv.org/abs/1912.07753); [GitHub google/lifetime_value](https://github.com/google/lifetime_value)
- CANONICAL REFS (not fetched): scikit-learn probability calibration (`CalibratedClassifierCV` with `method="sigmoid"` (Platt) or `"isotonic"`; `sklearn.calibration.calibration_curve`; `sklearn.metrics.brier_score_loss`, `average_precision_score`) — https://scikit-learn.org/stable/modules/calibration.html ; `TimeSeriesSplit` — https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html

### Inferences
- **Recommended protocol (TODO to implement):**
  1. Clean the data: drop rows with missing Customer ID (report the count), and handle "C" invoices by netting or excluding them. Exclude non-product StockCodes (postage, manual adjustments, bank charges; ASSUMPTION that these exist, verify with `value_counts`).
  2. Pick cutoff dates t0 ∈ {2010-09-01, 2010-12-01, 2011-03-01, 2011-06-01} (rolling origin). For each, compute features on [start, t0) and labels on [t0, t0 + H), with H = 90 days as the primary horizon and 180 days as a sensitivity check. Keep the final origin (e.g. 2011-09-09 + 90d = 2011-12-09, the data end) as the untouched test set.
  3. The population at each t0 is customers with ≥ 1 purchase before t0. Customers whose first purchase is after t0 are excluded, which prevents look-ahead leakage.
  4. **Leakage traps:** features that use any post-cutoff invoice; cancellations dated after t0 that reverse pre-t0 invoices; global scalers or target encoders fitted on all periods; random K-fold over customer-rows mixed across origins; tuning hyperparameters on the test origin; using `Country` aggregates computed on the full dataset.
  5. **Metrics:** PR-AUC (the churn base rate will be high, so also report the base rate); ROC-AUC; precision@top-k% and lift at deciles (cumulative gains chart); Brier score plus reliability curve before and after isotonic/Platt calibration, fitted on a separate temporal calibration fold; for value, normalized Gini, decile table of predicted vs actual, and MAE on log1p spend.
  6. **Baselines:** recency-only rule (e.g. recency > 90 days ⇒ churn), 1 − P(alive) from BG/NBD, and logistic regression on RFM. The GBM must beat all three on the same origins. Report mean ± sd across origins.
- Seasonality warning: an origin at 2011-09 leads into the Q4 peak and will have a much lower churn rate than an origin at 2011-01, so always report metrics per origin.

### Gaps
- No peer-reviewed churn benchmark on Online Retail II was found. **NOT FOUND.**
- The scikit-learn version and API changes as of Nov 2026 (e.g. `FrozenEstimator` replacing `cv="prefit"` in calibration) were not verified this session.

---

## 4. Segmentation and targeting (RFM, clustering, value-based segments, lookalike/prospect scoring)

### Takeaway
Use transparent RFM quintile scores plus named segments as the business-facing layer, k-means or GMM on log/standardized RFM plus behavioural features as the analytic layer, and CLV deciles (section 1) as value-based segments. "Identify new customers" can only mean scoring early-tenure customers or lookalike profiles of existing customers. There is no prospect universe in Online Retail II.

### Cited Findings
- PyMC-Marketing provides `clv.utils.rfm_summary` to build per-customer frequency/recency/T/monetary tables from raw transactions — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- PyMC-Marketing can predict expected purchases and spend for a **new** customer (`expected_purchases_new_customer`, `expected_new_customer_spend`), which gives a population-level prior for "a new customer is worth X" — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- Hwang (2019) has chapters on "Data-Driven Customer Segmentation", "Customer Lifetime Value", "Predicting the Likelihood of Marketing Engagement" and "Retaining Customers" — [Packt listing via search](https://packtpub.com/en-MT/product/hands-on-data-science-for-marketing-9781789346343/chapter/preface-pref/section/what-this-book-covers-preflvl1sec03); [Lehmanns](https://lehmanns.de/shop/mathematik-informatik/47348454-9781789346343-hands-on-data-science-for-marketing)
- CANONICAL REFS (not fetched): scikit-learn `KMeans`, `GaussianMixture`, `HDBSCAN` (in `sklearn.cluster` since 1.3), silhouette score — https://scikit-learn.org/stable/modules/clustering.html

### Inferences
- Pipeline: log1p-transform the skewed M and F, standardize, and add behavioural features (basket breadth = distinct StockCodes, avg unit price, return rate, inter-purchase-time CV, share of Q4 spend, country = UK vs non-UK). Choose k for k-means using silhouette plus business interpretability, and check stability with bootstrap ARI. GMM gives soft membership probabilities that can be shown in the UI. HDBSCAN suits wholesaler outliers, which it labels as noise.
- Value-based targeting: build a 2×2 of P(alive) × predicted CLV, giving "protect", "win back", "nurture" and "deprioritize". Write this up as a decision rule, not as a causal effect.
- Lookalike modelling with transactions only: train a classifier on first-30/60-day behaviour to predict "becomes top-decile CLV" and apply it to newly acquired customers. That is the honest "identify new valuable customers" story. Firmographic or demographic prospect data are **absent**, so do not fabricate them.

### Gaps
- No benchmark segmentation results for Online Retail II from peer-reviewed sources were found.

---

## 5. Market-basket, product embeddings and price elasticity (weeks 7-8)

### Takeaway
Use mlxtend (0.25.0, Jun 2026) FP-growth and association rules for basket analysis, item2vec/word2vec on invoice baskets for product similarity and positioning maps, and log-log or DML elasticity estimates explicitly labelled **associational**. Online Retail II prices are posted list prices with no exogenous variation, so causal pricing claims are not supportable.

### Cited Findings
- mlxtend 0.25.0 released Jun 6, 2026; Python >= 3.11; "Production/Stable"; one maintainer (rasbt); releases roughly every 6-11 months — [PyPI mlxtend](https://pypi.org/project/mlxtend/)
- EconML 0.17.0 released Jul 31, 2026; Python >= 3.9 (classifiers 3.9-3.14); estimators include `LinearDML(model_y=..., model_t=...)` and `CausalForestDML`, with a yearly release cadence (0.15.1 Jul 2024, 0.16.0 Jul 2025, 0.17.0 Jul 2026) — [PyPI econml](https://pypi.org/project/econml/)
- Hwang (2019) includes "Product Analytics" and "Recommending the Right Products" chapters — [Packt TOC via search](https://subscription.packtpub.com/book/data/9781789346343/8/ch08lvl1sec26/product-analytics)
- CANONICAL REFS (not fetched): mlxtend `frequent_patterns.apriori`, `fpgrowth`, `association_rules` — https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/ ; Barkan & Koenigstein (2016) "Item2Vec" arXiv:1603.04259 — https://arxiv.org/abs/1603.04259 ; Chernozhukov et al. (2018) "Double/Debiased Machine Learning" arXiv:1608.00060 — https://arxiv.org/abs/1608.00060

### Inferences
- Basket analysis: build an invoice × StockCode boolean matrix (exclude postage and cancellations), use `fpgrowth(min_support≈0.01-0.02)` then `association_rules(metric="lift")`, and report support, confidence, lift and conviction. Split UK and non-UK, or Q4 and non-Q4, to show stability.
- Elasticity: aggregate to StockCode × week. Regress log(quantity) on log(price) with product and week fixed effects. Wholesale quantity breaks are likely, since price varies with order size (ASSUMPTION: verify in data), and this creates reverse causality. DML (`LinearDML`, with confounders such as seasonality, customer mix and country) can reduce bias from observed confounders but **not** from unobserved ones. Label all elasticities "associational elasticity under stated assumptions".
- "AI-driven pricing" deliverable: a what-if simulator using the estimated elasticity with wide intervals, behind a human approval gate (AGENTS.md external-effects rule). It must not issue automated price recommendations.

### Gaps
- No published elasticity or association-rule benchmarks on Online Retail II were found.
- gensim's 2026 version and status (for word2vec/item2vec) were not verified.

---

## 6. Explainability and uncertainty in a business UI

### Takeaway
Use SHAP TreeExplainer for global and local explanations of the GBM, MAPIE v1 conformal intervals for CLV regressors (MAPIE 1.6.0, Oct 2026, has a **breaking v1 API**), and Bayesian credible intervals from PyMC-Marketing for BTYD. Show intervals and calibration in the UI, not just point scores.

### Cited Findings
- MAPIE 1.6.0 released Oct 19, 2026. PyPI metadata says Python >= 3.10 while the README says >= 3.9 (conflict). It requires NumPy >= 1.23 and scikit-learn >= 1.4. The README states: "MAPIE v1 is live! This new version introduces major changes to the API" — [PyPI MAPIE](https://pypi.org/project/MAPIE/); [MAPIE docs](https://mapie.readthedocs.io/en/stable/)
- PyMC-Marketing BTYD supports full MCMC posteriors (default) and MAP, so per-customer CLV and P(alive) come with posterior uncertainty — [PyMC-Marketing CLV quickstart](https://www.pymc-marketing.io/en/stable/notebooks/clv/clv_quickstart.html)
- ZILN produces a full predictive distribution, which gives uncertainty for point predictions — [arXiv 1912.07753](https://arxiv.org/abs/1912.07753)
- CANONICAL REFS (not fetched): Lundberg & Lee (2017) SHAP, arXiv:1705.07874 — https://arxiv.org/abs/1705.07874 ; SHAP docs — https://shap.readthedocs.io/

### Inferences
- UI pattern: each customer card shows CLV as a median plus an 80% interval (conformal or posterior), P(alive) as a percentage alongside a model-calibration badge (Brier score on the latest origin), and the top 3 SHAP drivers in plain language ("recency 140 days ↑ churn risk"). Add a provenance footer: dataset DOI, cutoff date, model version, seed.
- Conformal caveat: split-conformal coverage assumes exchangeability, and temporal drift (Q4) breaks it. Calibrate on the most recent pre-test origin and report empirical coverage on the test origin.

### Gaps
- MAPIE v1 class names: the API and release-notes pages returned 404 this session. From prior knowledge (UNVERIFIED) they are `SplitConformalRegressor`, `CrossConformalRegressor`, `JackknifeAfterBootstrapRegressor`, `ConformalizedQuantileRegressor`, `SplitConformalClassifier` and `CrossConformalClassifier`, using a `confidence_level` argument and `fit` / `conformalize` / `predict_interval`, replacing `MapieRegressor` / `MapieClassifier`. **Verify against the installed 1.6.0 before coding.**
- SHAP's 2026 version and maintenance status were not verified.

---

## 7. Uplift and causal claims: what can honestly be said

### Takeaway
Online Retail II has no campaign, treatment or randomization fields, so **campaign uplift cannot be estimated**. RetentionLens can rank *who is at risk* and *who is valuable*. It cannot say *who would respond to a retention offer*. Present uplift as a designed A/B test the business would need to run.

### Cited Findings
- The dataset's variables are only invoice, product, quantity, date, price, customer and country. No marketing-exposure fields exist — [UCI dataset 502](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- EconML provides heterogeneous-treatment-effect estimators (`LinearDML`, `CausalForestDML`) that require a treatment variable and confounder adjustment — [PyPI econml](https://pypi.org/project/econml/)
- Hwang (2019) includes "A/B Testing for Better Marketing Strategy" as a chapter, which maps to the honest "design the experiment" deliverable — [Lehmanns listing](https://lehmanns.de/shop/mathematik-informatik/47348454-9781789346343-hands-on-data-science-for-marketing)

### Inferences
- Suggested wording for the report: "Churn-risk and CLV scores are predictive, not causal. Targeting high-risk customers does not guarantee that an intervention changes their behaviour. Estimating uplift requires a randomized holdout (e.g. a 50/50 split within the top-risk decile) and a pre-registered outcome window."
- A synthetic uplift demo is allowed only if it is clearly labelled SYNTHETIC DEMO with simulated treatment. It must never be presented as a finding from Online Retail II.

### Gaps
- Uplift-specific libraries (`causalml`, `scikit-uplift`) and their 2026 status were not researched within the budget.

---

## 8. Network analysis on transactions (bridge to week 9)

### Takeaway
Build a customer-product bipartite graph from invoices. Project it to product-product co-purchase (weighted by Jaccard or lift) or customer-customer similarity, and run NetworkX community detection (Louvain or greedy modularity) to find product clusters and customer communities. This is a valid "network analysis" substitute when no social graph exists.

### Cited Findings
- Online Retail II has customer and product identifiers per invoice line, which is sufficient to construct a bipartite graph — [UCI dataset 502](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- CANONICAL REFS (not fetched): NetworkX bipartite projections (`networkx.algorithms.bipartite.weighted_projected_graph`) — https://networkx.org/documentation/stable/reference/algorithms/bipartite.html ; community detection (`louvain_communities`, `greedy_modularity_communities`) — https://networkx.org/documentation/stable/reference/algorithms/community.html

### Inferences
- Keep the graph tractable: filter to the top N products by invoice count (e.g. 500), set an edge threshold of co-occurrence ≥ k, fix the Louvain seed, and report modularity. Compare communities with FP-growth rule clusters and item2vec clusters (triangulation across three methods).
- Honest framing: these are co-purchase networks, not social influence networks. No word-of-mouth or social claims can be made.

### Gaps
- NetworkX's 2026 version was not verified. No published network analyses on Online Retail II were found within the budget.

---

## 9. Recommended model stack, textbook mapping and library status summary

### Takeaway
Stack: data audit → RFM + segments → BTYD (PyMC-Marketing BG/NBD + Gamma-Gamma) → GBM churn and CLV with rolling-origin validation and calibration → one advanced model (ZILN two-head) with conformal or lognormal intervals → basket, item2vec and network analyses for weeks 7-9 → elasticity labelled associational. Every reported metric comes from the student's own runs. No external benchmark exists to cite for this dataset.

### Cited Findings
- Library status table (as of 2026-11-01):

| Library | Version / date | Status | Source |
|---|---|---|---|
| lifetimes | archived Jun 28, 2024 | **DEPRECATED** (read-only; successor PyMC-Marketing) | [GitHub](https://github.com/CamDavidsonPilon/lifetimes) |
| pymc-marketing | 1.3.0, Oct 22, 2026; Py >= 3.12 | Active | [PyPI](https://pypi.org/project/pymc-marketing/) |
| google/lifetime_value (ZILN) | archived Apr 18, 2026 | **ARCHIVED**: re-implement the loss | [GitHub](https://github.com/google/lifetime_value) |
| MAPIE | 1.6.0, Oct 19, 2026 | Active; v1 breaking API | [PyPI](https://pypi.org/project/MAPIE/) |
| mlxtend | 0.25.0, Jun 6, 2026; Py >= 3.11 | Active, single maintainer | [PyPI](https://pypi.org/project/mlxtend/) |
| econml | 0.17.0, Jul 31, 2026 | Active (yearly releases) | [PyPI](https://pypi.org/project/econml/) |
| btyd | unknown | **UNVERIFIED** (PyPI page failed to load) | — |

- Hwang (2019), *Hands-On Data Science for Marketing*, Packt, March 2019, 464 pp., Python and R. Chapters: Data Science and Marketing; Key Performance Indicators and Visualizations; Drivers behind Marketing Engagement; From Engagement to Conversion; Product Analytics; Recommending the Right Products; Exploratory Analysis for Customer Behavior; Predicting the Likelihood of Marketing Engagement; Customer Lifetime Value; Data-Driven Customer Segmentation; Retaining Customers; A/B Testing for Better Marketing Strategy; What's Next? Chapter numbering differs between Packt's preface and its TOC — [Packt TOC/preface](https://packtpub.com/en-MT/product/hands-on-data-science-for-marketing-9781789346343/chapter/preface-pref/section/what-this-book-covers-preflvl1sec03); [Lehmanns](https://lehmanns.de/shop/mathematik-informatik/47348454-9781789346343-hands-on-data-science-for-marketing)

### Inferences
- Mapping of course topics to Hwang chapters and RetentionLens modules:
  - Predictive analytics for consumer choice → "Predicting the Likelihood of Marketing Engagement" → churn classifier (section 3)
  - CLV → "Customer Lifetime Value" → BTYD + ZILN (sections 1-2)
  - Segmentation/targeting → "Data-Driven Customer Segmentation" → section 4
  - Churn → "Retaining Customers" → section 3
  - Product positioning / brand assessment → "Product Analytics", "Recommending the Right Products" → section 5 (basket, item2vec maps)
  - AI-driven pricing → (not a Hwang chapter) → section 5 elasticity with an approval gate
  - Social/network analysis → (not a Hwang chapter) → section 8
  - Experimentation honesty → "A/B Testing for Better Marketing Strategy" → section 7
- Minimum acceptance criteria for "honest advanced model": the ZILN/two-head model must beat the GBM baseline on normalized Gini **and** decile calibration on ≥ 3 of 4 rolling origins. Otherwise report it as "did not outperform". Seeds, cutoff dates, data checksum and package versions go into an evidence JSON.
- Brand assessment from transactions only: the only defensible proxies are repeat-purchase share by product line, cross-category penetration, and price premium vs category median. Survey-based brand equity is **absent** from the data.

### Gaps
- No published benchmark numbers on Online Retail I or II for CLV, churn, segmentation or elasticity were found in peer-reviewed sources. **All benchmark comparisons: NOT FOUND.** Community GitHub claims (section 1) are unreviewed.
- Versions of LightGBM, XGBoost, CatBoost, SHAP, scikit-learn, gensim and NetworkX as of Nov 2026 were not verified within the tool budget.
- `btyd` status is unverified.
