"""Self-serve import: read a customer's CSV/XLSX, validate it row by row, then score it.

Nothing is filled in silently. Rows that cannot be parsed are rejected and listed;
optional columns that were not mapped are reported as "not provided".
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from ..data.clean import clean_transactions
from ..data.load import CANONICAL
from ..features.snapshot import prepare
from .mapping import check_mapping

NOT_PROVIDED = "Not provided"
# Common non-merchandise lines (postage, fees, manual adjustments). Uploaded SKUs follow no
# fixed pattern, so only these named codes are treated as non-product.
NON_PRODUCT_CODES = {"POST", "DOT", "M", "MANUAL", "BANK CHARGES", "AMAZONFEE", "C2", "D", "CRUK", "PADS", "ADJUST", "S", "B", "SHIPPING", "DELIVERY", "CARRIAGE", "DISCOUNT"}
MIN_CUSTOMERS, MIN_REPEAT_CUSTOMERS, MIN_SPAN_DAYS = 30, 10, 90
MAX_ERRORS_LISTED = 100

Progress = Callable[[str, int], None]


class IngestError(ValueError):
    """The file cannot be imported or scored; the message says why in plain words."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_table(path: Path) -> pd.DataFrame:
    """All cells as text; Excel sheets with the same headers as the first are stacked."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        sheets = pd.read_excel(path, sheet_name=None, dtype=str, keep_default_na=False)
        frames = list(sheets.values())
        if not frames:
            raise IngestError("The workbook has no sheets")
        first = list(frames[0].columns)
        frame = pd.concat([f for f in frames if list(f.columns) == first], ignore_index=True)
    elif suffix in (".csv", ".txt", ".tsv"):
        frame = None
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                frame = pd.read_csv(path, dtype=str, keep_default_na=False, sep=None, engine="python", encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        if frame is None:
            raise IngestError("Could not read the file's text encoding")
    else:
        raise IngestError("Upload a .csv or .xlsx file")
    frame.columns = [str(c).strip() for c in frame.columns]
    if frame.empty:
        raise IngestError("The file has headers but no rows")
    return frame


def inspect(path: Path) -> dict:
    from .mapping import suggest_mapping

    frame = read_table(path)
    headers = list(frame.columns)
    mapping = suggest_mapping(headers)
    return {
        "rows": int(len(frame)),
        "headers": headers,
        "suggested_mapping": mapping,
        "problems": check_mapping(mapping, headers),
        "sample": frame.head(5).to_dict(orient="records"),
    }


def parse_dates(values: pd.Series, order: str) -> tuple[pd.Series, str | None]:
    """Parse dates; with order="auto", pick the reading that parses more rows and say so when ambiguous."""
    def attempt(dayfirst: bool) -> pd.Series:
        return pd.to_datetime(values, errors="coerce", dayfirst=dayfirst, format="mixed")

    if order == "dayfirst":
        return attempt(True), None
    if order == "monthfirst":
        return attempt(False), None
    day, month = attempt(True), attempt(False)
    if day.notna().sum() > month.notna().sum():
        return day, None
    if month.notna().sum() > day.notna().sum():
        return month, None
    if (day.dropna() != month.dropna()).any():
        return day, "Dates could be read day-first or month-first; day-first (UK) was assumed. Change it if that is wrong."
    return day, None


def _numbers(values: pd.Series) -> pd.Series:
    cleaned = values.str.replace(r"(?i)aed|gbp|usd|eur|[£$€,\s]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def validate_frame(raw: pd.DataFrame, mapping: dict, date_order: str = "auto") -> tuple[dict, pd.DataFrame]:
    headers = list(raw.columns)
    problems = check_mapping(mapping, headers)
    if problems:
        raise IngestError("; ".join(problems))
    text = {c: (raw[mapping[c]].astype(str).str.strip() if mapping.get(c) else None) for c in CANONICAL}

    quantity = _numbers(text["quantity"])
    price = _numbers(text["price"])
    dates, date_note = parse_dates(text["invoice_date"], date_order)
    invoice = text["invoice"]
    customer = text["customer_id"].str.replace(r"\.0+$", "", regex=True).replace("", pd.NA)

    checks = {
        "invoice": (invoice == "", "Invoice number is empty"),
        "invoice_date": (dates.isna(), "Date could not be read"),
        "quantity": (quantity.isna(), "Quantity is not a number"),
        "price": (price.isna(), "Price is not a number"),
    }
    bad = pd.Series(False, index=raw.index)
    errors = []
    for column, (mask, problem) in checks.items():
        bad |= mask
        for index in mask[mask].index[: MAX_ERRORS_LISTED - len(errors)]:
            errors.append({"row": int(index) + 2, "column": mapping[column], "value": str(text[column].loc[index])[:60], "problem": problem})
    errors.sort(key=lambda e: e["row"])

    good = ~bad
    lines = pd.DataFrame(
        {
            "invoice": invoice[good],
            "stock_code": text["stock_code"][good] if text["stock_code"] is not None else NOT_PROVIDED,
            "description": (text["description"][good] if text["description"] is not None else NOT_PROVIDED),
            "quantity": quantity[good].astype("float64"),
            "invoice_date": dates[good],
            "price": price[good].astype("float64"),
            "customer_id": customer[good].astype("string"),
            "country": (text["country"][good].replace("", NOT_PROVIDED) if text["country"] is not None else NOT_PROVIDED),
        }
    )
    lines["description"] = lines["description"].astype("string")
    lines["country"] = lines["country"].astype("string")
    lines["source_sheet"] = "upload"
    cleaned = clean_transactions(lines.reset_index(drop=True))
    flagged = cleaned.lines
    flagged["is_non_product"] = flagged["stock_code"].str.upper().isin(NON_PRODUCT_CODES)
    issues = dict(cleaned.issues)
    issues["is_non_product"] = int(flagged["is_non_product"].sum())

    usable = prepare(flagged)
    sales = usable[usable["is_sale"]]
    purchase_days = sales.groupby("customer_id", observed=True)["day"].nunique()
    span = int((usable["day"].max() - usable["day"].min()).days) if len(usable) else 0
    blocking, warnings = [], []
    if len(purchase_days) < MIN_CUSTOMERS:
        blocking.append(f"Only {len(purchase_days)} customers with a sale; at least {MIN_CUSTOMERS} are needed to fit the model")
    if int((purchase_days >= 2).sum()) < MIN_REPEAT_CUSTOMERS:
        blocking.append(f"Only {int((purchase_days >= 2).sum())} customers ordered on two or more days; at least {MIN_REPEAT_CUSTOMERS} are needed")
    if span < MIN_SPAN_DAYS:
        blocking.append(f"The file covers {span} days; at least {MIN_SPAN_DAYS} days of history are needed")
    if date_note:
        warnings.append(date_note)
    for column in ("stock_code", "description", "country"):
        if not mapping.get(column):
            warnings.append(f"No {column.replace('_', ' ')} column: shown as '{NOT_PROVIDED}'")
    if issues["is_missing_customer"]:
        warnings.append(f"{issues['is_missing_customer']:,} lines have no customer ID and are left out of scoring")

    report = {
        "rows": int(len(raw)),
        "valid_rows": int(good.sum()),
        "rejected_rows": int(bad.sum()),
        "errors": errors,
        "issues": issues,
        "date_min": None if usable.empty else usable["day"].min().date().isoformat(),
        "date_max": None if usable.empty else usable["day"].max().date().isoformat(),
        "customers": int(len(purchase_days)),
        "repeat_customers": int((purchase_days >= 2).sum()),
        "usable_lines": int(len(usable)),
        "blocking": blocking,
        "warnings": warnings,
        "can_score": not blocking,
    }
    return report, flagged


def validate(path: Path, mapping: dict, date_order: str = "auto") -> dict:
    report, _ = validate_frame(read_table(path), mapping, date_order)
    return report


def _write(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n")


def score(path: Path, mapping: dict, out_dir: Path, date_order: str = "auto", progress: Progress = lambda stage, pct: None) -> dict:
    """Upload -> validate -> clean -> snapshot -> BG/NBD + Gamma-Gamma -> serving files in out_dir."""
    from ..serving.build import MODEL_NAME, account_records, timeline
    from ..serving.scoring import cohort_matrix, score_accounts
    from ..product.lab import build_product_lab
    from ..serving.products import build_account_products
    from ..serving.segments import build_segments
    from .intervals import add_value_intervals

    progress("reading", 5)
    raw = read_table(path)
    progress("validating", 15)
    report, flagged = validate_frame(raw, mapping, date_order)
    if not report["can_score"]:
        raise IngestError("; ".join(report["blocking"]))
    progress("preparing", 30)
    prepared = prepare(flagged)
    cutoff = (prepared["day"].max() + pd.Timedelta(days=1)).date().isoformat()
    progress("fitting", 45)
    scored = score_accounts(prepared, cutoff)
    progress("segmenting", 70)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Same builders as the reference dataset, so Segments, the 3D galaxy, lookalikes, Product lab and
    # draft product mentions all work on uploads. Each failure is reported, never silently filled.
    extras, skipped = [], {}
    for name, builder in (("segments", lambda: build_segments(prepared, scored, out_dir, cutoff)),
                          ("top_products", lambda: build_account_products(prepared, scored, out_dir)),
                          ("product_lab", lambda: build_product_lab(prepared, scored, out_dir))):
        try:
            frame = builder()
            if frame is not None:
                extras.append(frame)
        except Exception as error:  # a weak upload should still score
            skipped[name] = str(error)[:200]
    bounds, interval_meta = add_value_intervals(prepared, scored, cutoff)
    progress("checking", 82)
    backtest = upload_backtest(prepared, cutoff)
    extra = pd.concat([*extras, bounds], axis=1)

    progress("writing", 92)
    records = account_records(scored, extra)
    _write(out_dir / "accounts.json", records)
    _write(out_dir / "timeline.json", timeline(prepared))
    sale_days = prepared[prepared["is_sale"]][["customer_id", "day"]].drop_duplicates()
    _write(out_dir / "cohorts.json", cohort_matrix(sale_days))
    _write(out_dir / "upload_eval.json", {**backtest, "intervals": interval_meta, "skipped_views": skipped})
    bands = scored["risk_band"].value_counts().to_dict()
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scoring_cutoff": cutoff,
        "horizon_days": 90,
        "model": MODEL_NAME,
        "data_sha256": file_sha256(path),
        "data_source": f"Uploaded file ({report['rows']:,} rows, {report['date_min']} to {report['date_max']})",
        "licence": "Customer-owned data, used only inside this workspace",
        "accounts": int(len(scored)),
        "bands": {k: int(bands.get(k, 0)) for k in ("high", "watch", "healthy")},
        "value_at_risk_high": round(float(scored.loc[scored["risk_band"] == "high", "value_at_risk_90"].sum()), 2),
        "expected_value_total": round(float(np.nansum(scored["expected_value_90"])), 2),
        "evaluation_run": None,
        "frozen_test": None,
        "intervals": interval_meta,
        "backtest": {k: backtest.get(k) for k in ("available", "cutoff", "pr_auc", "brier", "customers")},
    }
    _write(out_dir / "summary.json", summary)
    _write(out_dir / "validation.json", report)
    progress("done", 100)
    return summary


def upload_backtest(prepared: pd.DataFrame, cutoff: str) -> dict:
    """How well would the served model have done on this customer's own last 90 days?

    Fits seasonal BG/NBD + Gamma-Gamma on history before cutoff-90 days and scores the 90 days that followed,
    against a recency rule fitted the same way. One backtest on one window: a sanity check, not a frozen test.
    """
    from ..eval.metrics import lapse_metrics, value_metrics
    from ..features.seasonal import season_multiplier, seasonal_lapse
    from ..features.snapshot import build_snapshot
    from ..models.btyd import BtydModel
    from ..serving.scoring import net_adjusted

    check = (pd.Timestamp(cutoff) - pd.Timedelta(days=90)).date().isoformat()
    try:
        snap = net_adjusted(build_snapshot(prepared, check))
        if snap["lapsed"].nunique() < 2 or len(snap) < 30:
            raise ValueError("too few customers, or everyone behaved the same, in the check window")
        model = BtydModel().fit(snap)
        m = season_multiplier(prepared, check)["multiplier"]
        p = seasonal_lapse(model.predict_lapse(snap), m)
        value = model.predict_value(snap) * m
        lapse = lapse_metrics(snap["lapsed"], p)
        gap = snap["mean_gap_days"].fillna(snap["recency_days"].median())
        rule = (snap["recency_days"] > 2 * gap).astype(float) * 0.5 + 0.25
        baseline = lapse_metrics(snap["lapsed"], rule)
        values = value_metrics(snap["future_value"], value)
    except (ValueError, KeyError, RuntimeError) as error:
        return {"available": False, "cutoff": check, "reason": str(error)[:200]}
    return {
        "available": True, "cutoff": check, "horizon_days": 90, "customers": int(len(snap)),
        "base_rate": round(lapse["base_rate"], 4), "pr_auc": round(lapse["pr_auc"], 4), "roc_auc": round(lapse["roc_auc"], 4),
        "brier": round(lapse["brier"], 4), "top_lift": round(lapse["top_lift"], 3),
        "baseline_rule_pr_auc": round(baseline["pr_auc"], 4),
        "value_gini": round(values["normalized_gini"], 4), "value_mae": round(values["mae"], 2),
        "total_actual": round(values["total_actual"], 2), "total_pred": round(values["total_pred"], 2),
        "method": "Seasonal BG/NBD + Gamma-Gamma fitted on history before the check date, scored on the following 90 days; "
                  "baseline: 'no order for over twice the usual gap'.",
    }
