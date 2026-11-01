# Verified source starting points and academic design

## First data source
**URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
**Known purpose:** UCI Online Retail II: 1,067,371 historical transactional invoice lines (2009-2011), CC BY 4.0. Not a million users; no causal campaign treatment assignments.
**Licence/rights caveat:** UCI CC BY 4.0; retain attribution and modification notes. Customer email/web/social data needs permission and reliable identifiers.
**First Work task:** verify the most recent publisher docs, version, schema, files, licence, and any limits before downloading; record URLs/access date/checksums in `project/DATA_SOURCE_REGISTER.csv`.

## Academic research question
> Does a two-part probabilistic neural predictor outperform RFM and gradient boosting on calibrated 90-day repeat-purchase and customer-value forecasts under temporal change?

## Proposed experiments
- Baseline vs trained alternative: RFM heuristic; BG/NBD where assumptions appropriate; gradient boosting; trained two-head neural model for purchase/no-purchase and conditional purchase value.
- Metrics: 90-day purchase PR-AUC and Brier; monetary MAE and quantile coverage; segment stability; top-k prioritization utility (descriptive, not causal).
- Known evaluation threats: Rolling origin splits; ensure full 90-day future windows; no future invoices; signed returns/cancellations handled transparently; contact uplift not inferable.
- Prior work must be cited; specific originality must be demonstrated through a novel, evaluated change or a new permissioned user study.
- Report confidence intervals or variation across runs where technically meaningful.
- Every chart must name its population, horizon/units, data version and sample size.

## Honest claims vocabulary
- **Observed**: measured from downloaded or customer data with provenance.
- **Modelled**: held-out evaluation result, reproducible from saved run.
- **Simulated**: calculated from declared hypothetical assumptions; not observed profit/impact.
- **Proposed**: user interface, business hypotheses and future features.

## Licence and privacy checks
External data is never automatically suitable for customer-facing reuse. Document publisher license and any upstream third-party rights; minimise PII and retain an auditable lawful basis / permission record. Synthetic demo records are only for development and cannot support empirical conclusions.

## Literature and data starting URLs
- https://archive.ics.uci.edu/dataset/502/online+retail+ii
- https://research.google/pubs/a-deep-probabilistic-model-for-customer-lifetime-value-prediction/
- https://www.w3.org/WAI/WCAG22/quickref/

## Dataset card fill-in checklist
`owner; published release date; access date; download URL; citation; license; file checksum; row/entity granularity; timestamp unit; available labels; missing fields; privacy/PII; permissible commercial use; preprocessing; train/test split; derived artifacts; deletion plan`.
