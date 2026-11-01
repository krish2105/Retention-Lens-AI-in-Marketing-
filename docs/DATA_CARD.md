# Data card — UCI Online Retail II

Every number here is copied from `reports/data_profile.json`, produced by `uv run python -m retentionlens.cli data` on 2026-11-01. Re-run that command to reproduce it.

| Field | Value |
|---|---|
| Owner / creator | Daqing Chen; donated to UCI on 2019-09-20 |
| Citation | Chen, D. (2019). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D |
| Download URL | https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip |
| Access date | 2026-11-01 |
| Licence | CC BY 4.0 (UCI page). Mirrors on Kaggle/OpenML label it CC0; the UCI licence is the one that applies |
| Archive SHA-256 | `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb` (45,622,418 bytes) |
| Workbook SHA-256 | `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980` (`online_retail_II.xlsx`) |
| Granularity | One row per invoice line (not per customer, not per order) |
| Rows | 1,067,371 across two sheets: `Year 2009-2010` 525,461 and `Year 2010-2011` 541,910 |
| Time span | 2009-12-01 to 2011-12-09; timestamps to the minute |
| Entities | 53,628 invoices · 5,942 customer IDs · 43 countries |
| Real column headers | `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country` (UCI's documentation uses `InvoiceNo`, `UnitPrice`, `CustomerID`; the loader accepts both) |
| Labels | None. Churn and value labels are derived per cutoff in P2 |
| Personal data | Customer IDs are pseudonymous five-digit numbers; no names, emails or addresses |
| Commercial use | Allowed with attribution and a note of changes (CC BY 4.0) |
| Repo policy | Raw and interim files are gitignored; only aggregate reports are committed |
| Deletion | `rm -rf data/raw data/interim/*.parquet` removes every local copy |

## Known issues found in the real file

| Issue | Rows | Share | Handling |
|---|---|---|---|
| Missing Customer ID | 243,007 | 22.8% | Kept for market-level analysis; excluded from customer models |
| Cancellations (invoice starts with `C`) | 19,494 | 1.8% | Kept; they net customer spend |
| Negative quantity | 22,950 | 2.2% | Kept; 3,457 of these are not cancellations (stock adjustments) |
| Price zero or below | 6,207 | 0.6% | Excluded from customer models |
| Non-product codes (POST, DOT, M, BANK CHARGES, gift vouchers, …) | 6,093 | 0.6% | Excluded from customer models |
| Exact duplicate rows | 34,335 | 3.2% | First copy kept |
| · of which repeated across the two sheets | 22,202 | 2.1% | The sheets overlap on 2010-12-01 to 2010-12-09, so the published row count double-counts that week |
| · of which repeated within one sheet | 12,133 | 1.1% | Treated as duplicates; could be genuine repeat scans (limitation) |

## Rows usable for customer-level models

Known customer, product line, positive price, not a duplicate: **794,163 rows (74.4%)**, **5,875 customers**, net line value **£16,358,614.54**.

## Limitations

- Product-code rule is `^\d{5}[A-Za-z]{0,2}$`. A few codes such as `DCGS0058`, `DCGSSBOY`, `DCGSSGIRL` (79 rows in total) may be real gift-set products and are currently excluded.
- No campaign, consent, contact or margin fields: uplift, consent status and profit cannot be derived.
- One UK online giftware wholesaler, 2009–2011: results may not transfer to other sectors or years.
