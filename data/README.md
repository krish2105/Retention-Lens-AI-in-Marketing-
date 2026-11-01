# Data contract and rights

Only `sample/demo_cases.csv` is bundled. It is fictional data suitable for UI and API smoke tests, **not** ML evaluation.

Real source start: https://archive.ics.uci.edu/dataset/502/online+retail+ii

- Never commit real customer files or sensitive survey data to the repository. Place local secrets and downloaded datasets under ignored `data/raw/`.
- Complete `project/DATA_SOURCE_REGISTER.csv` before any modelling.
- Preserve immutable raw, separate `data/interim/` and `data/processed/`; record transformations and entity granularity.
- Expected first specialist adapter: UCI Online Retail II import using invoice-date cuts and refunds; do not bundle customer details or conflate line rows with distinct customers.
- Check published licences and any upstream third-party content obligations before commercial use.
