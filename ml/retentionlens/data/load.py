"""Load Online Retail II into canonical, typed columns."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

CANONICAL = ["invoice", "stock_code", "description", "quantity", "invoice_date", "price", "customer_id", "country"]

# Real file headers and the names UCI documents both map to one canonical name.
HEADER_MAP = {
    "Invoice": "invoice",
    "InvoiceNo": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "UnitPrice": "price",
    "Customer ID": "customer_id",
    "CustomerID": "customer_id",
    "Customer_ID": "customer_id",
    "Country": "country",
}
TEXT_COLUMNS = {"Invoice": str, "InvoiceNo": str, "StockCode": str}


class SchemaError(ValueError):
    """Source columns do not match the expected Online Retail II schema."""


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(columns={c: HEADER_MAP.get(str(c).strip(), str(c).strip()) for c in df.columns})
    missing = [c for c in CANONICAL if c not in renamed.columns]
    if missing:
        raise SchemaError(f"missing columns {missing}; got {list(df.columns)}")
    return renamed[CANONICAL]


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["invoice"] = out["invoice"].astype(str).str.strip()
    out["stock_code"] = out["stock_code"].astype(str).str.strip()
    out["description"] = out["description"].astype("string").str.strip()
    out["quantity"] = pd.to_numeric(out["quantity"], errors="raise").astype("int64")
    out["price"] = pd.to_numeric(out["price"], errors="raise").astype("float64")
    out["invoice_date"] = pd.to_datetime(out["invoice_date"], errors="raise")
    customer = pd.to_numeric(out["customer_id"], errors="coerce").astype("Int64")
    out["customer_id"] = customer.astype("string")
    out["country"] = out["country"].astype("string").str.strip()
    return out


def load_raw(xlsx_path: Path) -> pd.DataFrame:
    sheets = pd.read_excel(xlsx_path, sheet_name=None, dtype=TEXT_COLUMNS)
    frames = []
    for name, frame in sheets.items():
        part = coerce_types(standardise_columns(frame))
        part["source_sheet"] = name
        frames.append(part)
    return pd.concat(frames, ignore_index=True)


def load_or_cache(xlsx_path: Path, parquet_path: Path) -> pd.DataFrame:
    if parquet_path.exists() and parquet_path.stat().st_mtime >= xlsx_path.stat().st_mtime:
        return pd.read_parquet(parquet_path)
    df = load_raw(xlsx_path)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    return df
