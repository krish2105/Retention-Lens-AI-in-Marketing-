# Domain pipeline and build specification

**Canonical pipeline:** Invoice import -> customer identity cleaning -> temporal feature extraction -> baselines + neural training -> forecast and calibration -> account queue -> outreach approval -> observed later orders.

## Stage 0: Source validation
- Register source owner, URL, collection/release date, licence, allowed use, checksum, credentials requirements.
- Create a field-by-field mapping to a declared schema. Reject unknown/unexpected states without inventing values.
- Keep raw original separate from standardised feature layers; redact nonessential identifiers.

## Stage 1: Deterministic first slice
- Use the audited data fields to implement a baseline, rule, or computation.
- Save the input, configuration, result and a semantic version tag.
- Compare deterministic output against handcrafted unit tests and edge cases.

## Stage 2: Research experiments
**Research:** Does a two-part probabilistic neural predictor outperform RFM and gradient boosting on calibrated 90-day repeat-purchase and customer-value forecasts under temporal change?
**Models:** RFM heuristic; BG/NBD where assumptions appropriate; gradient boosting; trained two-head neural model for purchase/no-purchase and conditional purchase value.
**Evaluation:** 90-day purchase PR-AUC and Brier; monetary MAE and quantile coverage; segment stability; top-k prioritization utility (descriptive, not causal).
**Leakage/validity:** Rolling origin splits; ensure full 90-day future windows; no future invoices; signed returns/cancellations handled transparently; contact uplift not inferable.
- Preserve train, validation and frozen test definitions BEFORE tuning.
- Record run seed, git commit, data checksum, feature list, hyperparameters, timing and model size.
- Compare meaningful baselines; evaluate subgroup / temporal / shift cases where appropriate.
- Make figures directly from measured result artifacts; never manually type a score as proof.

## Stage 3: Application serving
- Route only approved model artifacts to serving.
- Validate request units and source version. Return uncertainty, abstention and a fallback response when not confident.
- Never infer monetary, causal or social outcomes unsupported by the dataset.

## Stage 4: Decision and follow-up
- A person reviews/overrides relevant outputs, with a reason and timestamps.
- Track real outcomes separately; do not train on them without permission and a versioned data process.
- Monitor drift, wrong decisions, data quality and user feedback.

## Data access plan
UCI Online Retail II import using invoice-date cuts and refunds; do not bundle customer details or conflate line rows with distinct customers.
**Never imply that an external dataset is embedded in this ZIP.** Only small fictional records are included for smoke tests.
