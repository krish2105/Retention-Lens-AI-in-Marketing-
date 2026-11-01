"""Flag data-quality issues in Online Retail II without dropping rows."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .load import CANONICAL

# Product codes are five digits with an optional letter suffix (85123A, 79323P).
# Everything else (POST, M, BANK CHARGES, gift vouchers, ...) is a non-product line.
PRODUCT_CODE_PATTERN = r"\d{5}[A-Za-z]{0,2}"
FLAGS = [
    "is_cancellation",
    "is_negative_qty",
    "is_nonpositive_price",
    "is_non_product",
    "is_missing_customer",
    "is_duplicate",
]


@dataclass(frozen=True)
class CleanResult:
    lines: pd.DataFrame
    issues: dict[str, int]


def clean_transactions(df: pd.DataFrame) -> CleanResult:
    out = df.copy()
    out["is_cancellation"] = out["invoice"].str.upper().str.startswith("C")
    out["is_negative_qty"] = out["quantity"] < 0
    out["is_nonpositive_price"] = out["price"] <= 0
    out["is_non_product"] = ~out["stock_code"].str.fullmatch(PRODUCT_CODE_PATTERN)
    out["is_missing_customer"] = out["customer_id"].isna()
    out["is_duplicate"] = out.duplicated(subset=CANONICAL, keep="first")
    out["line_value"] = out["quantity"] * out["price"]

    issues = {"rows": len(out)}
    issues.update({flag: int(out[flag].sum()) for flag in FLAGS})
    issues["negative_qty_not_cancelled"] = int((out["is_negative_qty"] & ~out["is_cancellation"]).sum())
    return CleanResult(lines=out, issues=issues)


def customer_lines(lines: pd.DataFrame) -> pd.DataFrame:
    """Rows usable for customer-level models. Cancellations stay so spend nets correctly."""
    usable = ~(
        lines["is_missing_customer"]
        | lines["is_non_product"]
        | lines["is_duplicate"]
        | lines["is_nonpositive_price"]
    )
    return lines.loc[usable].copy()
