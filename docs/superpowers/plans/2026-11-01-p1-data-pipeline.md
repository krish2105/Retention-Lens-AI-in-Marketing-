# P1 Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Download UCI Online Retail II with a checksum manifest, load it with its real headers, flag data-quality issues without silently dropping rows, and publish a profile report and data card built from real counts.

**Architecture:** A small Python package `retentionlens` under `ml/` with one module per step (download, load, clean, profile) and a CLI that chains them. Raw and interim files stay in gitignored `data/`; only aggregate reports are committed.

**Tech Stack:** Python 3.12 (uv), pandas 2.x, pyarrow, openpyxl, pytest.

## Global Constraints

- Python `>=3.12,<3.13` (PyMC-Marketing 1.3 needs ≥3.12; later phases share this env).
- Dataset: UCI Online Retail II, CC BY 4.0, DOI 10.24432/C5CG6D, URL `https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip`.
- Never hard-code documented header names only: accept `Invoice`/`InvoiceNo`, `Price`/`UnitPrice`, `Customer ID`/`CustomerID`/`Customer_ID`.
- Never drop rows silently: every exclusion is a boolean flag with a counted total.
- Raw data, interim parquet and `.venv` are never committed.
- Commits carry the owner's identity only; no AI co-author lines.

---

### Task 1: Package scaffold

**Files:**
- Create: `ml/pyproject.toml`, `ml/retentionlens/__init__.py`, `ml/retentionlens/data/__init__.py`, `ml/tests/__init__.py`

**Interfaces:** Produces the importable package `retentionlens` and the `ml/.venv` environment used by every later task.

- [ ] **Step 1: Write `ml/pyproject.toml`**

```toml
[project]
name = "retentionlens"
version = "0.1.0"
description = "RetentionLens ML pipeline (MAIB AI 208)"
requires-python = ">=3.12,<3.13"
dependencies = ["pandas>=2.2,<3", "pyarrow>=16", "openpyxl>=3.1,<4"]

[dependency-groups]
dev = ["pytest>=8"]

[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["retentionlens*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create empty `__init__.py` files** (package docstring only in `retentionlens/__init__.py`: `"""RetentionLens ML pipeline."""`).

- [ ] **Step 3: Sync and smoke-test**

Run: `cd ml && uv sync --python 3.12 && uv run python -c "import retentionlens, pandas; print(pandas.__version__)"`
Expected: a pandas 2.x version string.

- [ ] **Step 4: Commit** `git add ml/pyproject.toml ml/uv.lock ml/retentionlens ml/tests && git commit -m "feat(ml): scaffold retentionlens package"`

### Task 2: Download with checksum manifest

**Files:**
- Create: `ml/retentionlens/data/download.py`
- Test: `ml/tests/test_download.py`

**Interfaces:**
- Produces: `download_dataset(dest_dir: Path, url: str = UCI_URL, expected_zip_sha256: str | None = None) -> DownloadResult`; `sha256_file(path: Path) -> str`; `ChecksumMismatch`; constants `UCI_URL`, `LICENCE`, `CITATION`. Writes `<dest_dir>/online_retail_ii.manifest.json`.

- [ ] **Step 1: Write the failing tests**

```python
import json
import zipfile

import pytest

from retentionlens.data.download import ChecksumMismatch, download_dataset, sha256_file


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return path


def test_downloads_extracts_and_writes_manifest(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"online_retail_II.xlsx": b"fake-xlsx"})
    dest = tmp_path / "raw"
    result = download_dataset(dest, url=src.as_uri())
    assert result.xlsx_path.read_bytes() == b"fake-xlsx"
    assert result.zip_sha256 == sha256_file(src)
    manifest = json.loads((dest / "online_retail_ii.manifest.json").read_text())
    assert manifest["licence"] == "CC BY 4.0"
    assert manifest["zip_sha256"] == result.zip_sha256
    assert manifest["xlsx_path"] == "online_retail_II.xlsx"


def test_checksum_mismatch_raises(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"online_retail_II.xlsx": b"x"})
    with pytest.raises(ChecksumMismatch):
        download_dataset(tmp_path / "raw", url=src.as_uri(), expected_zip_sha256="0" * 64)


def test_zip_without_xlsx_raises(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"readme.txt": b"no data"})
    with pytest.raises(FileNotFoundError):
        download_dataset(tmp_path / "raw", url=src.as_uri())


def test_member_path_cannot_escape_dest(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"../../evil.xlsx": b"x"})
    result = download_dataset(tmp_path / "raw", url=src.as_uri())
    assert result.xlsx_path.parent == tmp_path / "raw"
```

- [ ] **Step 2: Run to verify failure** — `cd ml && uv run pytest tests/test_download.py -v` → FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implement `ml/retentionlens/data/download.py`**

```python
"""Download UCI Online Retail II and record a checksum manifest."""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

UCI_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
LICENCE = "CC BY 4.0"
CITATION = (
    "Chen, D. (2019). Online Retail II [Dataset]. UCI Machine Learning Repository. "
    "https://doi.org/10.24432/C5CG6D"
)
ZIP_NAME = "online_retail_ii.zip"
MANIFEST_NAME = "online_retail_ii.manifest.json"


class ChecksumMismatch(RuntimeError):
    """The downloaded archive does not match the expected SHA-256."""


@dataclass(frozen=True)
class DownloadResult:
    zip_path: Path
    xlsx_path: Path
    zip_sha256: str
    xlsx_sha256: str
    zip_bytes: int
    url: str
    accessed_at: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_dataset(
    dest_dir: Path, url: str = UCI_URL, expected_zip_sha256: str | None = None
) -> DownloadResult:
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / ZIP_NAME
    if not zip_path.exists():
        partial = zip_path.with_suffix(".part")
        with urllib.request.urlopen(url, timeout=180) as response, partial.open("wb") as out:
            shutil.copyfileobj(response, out)
        partial.replace(zip_path)

    zip_sha256 = sha256_file(zip_path)
    if expected_zip_sha256 and zip_sha256 != expected_zip_sha256:
        raise ChecksumMismatch(f"zip sha256 {zip_sha256} != expected {expected_zip_sha256}")

    with zipfile.ZipFile(zip_path) as archive:
        member = next((n for n in archive.namelist() if n.lower().endswith(".xlsx")), None)
        if member is None:
            raise FileNotFoundError(f"no .xlsx file inside {zip_path.name}")
        xlsx_path = dest_dir / Path(member).name  # basename only: no path escape
        if not xlsx_path.exists():
            with archive.open(member) as src, xlsx_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)

    result = DownloadResult(
        zip_path=zip_path,
        xlsx_path=xlsx_path,
        zip_sha256=zip_sha256,
        xlsx_sha256=sha256_file(xlsx_path),
        zip_bytes=zip_path.stat().st_size,
        url=url,
        accessed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    manifest = {
        "url": result.url,
        "zip_path": zip_path.name,
        "xlsx_path": xlsx_path.name,
        "zip_sha256": result.zip_sha256,
        "xlsx_sha256": result.xlsx_sha256,
        "zip_bytes": result.zip_bytes,
        "accessed_at": result.accessed_at,
        "licence": LICENCE,
        "citation": CITATION,
    }
    (dest_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n")
    return result
```

- [ ] **Step 4: Run tests** — `uv run pytest tests/test_download.py -v` → 4 PASS.
- [ ] **Step 5: Commit** `git add ml/retentionlens/data/download.py ml/tests/test_download.py && git commit -m "feat(ml): download dataset with sha256 manifest"`

### Task 3: Loader with real headers and types

**Files:**
- Create: `ml/retentionlens/data/load.py`
- Test: `ml/tests/test_load.py`

**Interfaces:**
- Produces: `CANONICAL: list[str]` = `["invoice","stock_code","description","quantity","invoice_date","price","customer_id","country"]`; `SchemaError`; `standardise_columns(df) -> DataFrame`; `coerce_types(df) -> DataFrame` (customer_id is pandas `string` with `<NA>` for missing); `load_raw(xlsx_path: Path) -> DataFrame` (adds `source_sheet`); `load_or_cache(xlsx_path: Path, parquet_path: Path) -> DataFrame`.

- [ ] **Step 1: Write the failing tests**

```python
import pandas as pd
import pytest

from retentionlens.data.load import CANONICAL, SchemaError, coerce_types, load_raw, standardise_columns


def raw_frame(**renames):
    df = pd.DataFrame(
        {
            "Invoice": ["489434", "C489449"],
            "StockCode": ["85048", "22087"],
            "Description": [" LIGHT ", "PAPER"],
            "Quantity": [12, -12],
            "InvoiceDate": ["2009-12-01 07:45", "2009-12-01 10:33"],
            "Price": [6.95, 0.85],
            "Customer ID": [13085.0, None],
            "Country": ["United Kingdom", "Australia"],
        }
    )
    return df.rename(columns=renames)


def test_accepts_real_and_documented_headers():
    for renames in ({}, {"Invoice": "InvoiceNo", "Price": "UnitPrice", "Customer ID": "CustomerID"}, {"Customer ID": "Customer_ID"}):
        assert list(standardise_columns(raw_frame(**renames)).columns) == CANONICAL


def test_missing_column_raises():
    with pytest.raises(SchemaError):
        standardise_columns(raw_frame().drop(columns=["Price"]))


def test_coerce_types_keeps_missing_customer_as_na():
    out = coerce_types(standardise_columns(raw_frame()))
    assert out.loc[0, "customer_id"] == "13085"
    assert pd.isna(out.loc[1, "customer_id"])
    assert out.loc[0, "description"] == "LIGHT"
    assert str(out["invoice_date"].dtype).startswith("datetime64")
    assert out["quantity"].tolist() == [12, -12]


def test_load_raw_reads_every_sheet(tmp_path):
    path = tmp_path / "book.xlsx"
    with pd.ExcelWriter(path) as writer:
        raw_frame().to_excel(writer, sheet_name="Year 2009-2010", index=False)
        raw_frame().to_excel(writer, sheet_name="Year 2010-2011", index=False)
    out = load_raw(path)
    assert len(out) == 4
    assert set(out["source_sheet"]) == {"Year 2009-2010", "Year 2010-2011"}
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/test_load.py -v` → FAIL.

- [ ] **Step 3: Implement `ml/retentionlens/data/load.py`**

```python
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
```

- [ ] **Step 4: Run tests** → 4 PASS.
- [ ] **Step 5: Commit** `git commit -m "feat(ml): typed loader accepting real and documented headers"`

### Task 4: Cleaning flags (no silent drops)

**Files:**
- Create: `ml/retentionlens/data/clean.py`
- Test: `ml/tests/test_clean.py`

**Interfaces:**
- Consumes: `CANONICAL` from `load.py`.
- Produces: `FLAGS: list[str]`; `PRODUCT_CODE_PATTERN: str`; `CleanResult(lines: DataFrame, issues: dict[str, int])`; `clean_transactions(df) -> CleanResult` (adds flag columns + `line_value`); `customer_lines(lines) -> DataFrame` (rows usable for customer models; keeps cancellations so revenue nets).

- [ ] **Step 1: Write the failing tests**

```python
import pandas as pd

from retentionlens.data.clean import FLAGS, clean_transactions, customer_lines


def lines():
    return pd.DataFrame(
        {
            "invoice": ["1", "C2", "3", "4", "5", "5", "6"],
            "stock_code": ["85123A", "85123A", "POST", "22423", "22423", "22423", "79323P"],
            "description": ["A", "A", "POSTAGE", "B", "B", "B", "C"],
            "quantity": [6, -6, 1, 2, 3, 3, -1],
            "invoice_date": pd.to_datetime(["2010-01-01"] * 7),
            "price": [2.5, 2.5, 18.0, 0.0, 1.0, 1.0, 4.0],
            "customer_id": pd.array(["1", "1", "1", "2", None, None, "3"], dtype="string"),
            "country": pd.array(["UK"] * 7, dtype="string"),
            "source_sheet": ["s"] * 7,
        }
    )


def test_flags_are_counted_not_dropped():
    result = clean_transactions(lines())
    assert len(result.lines) == 7
    assert result.issues == {
        "rows": 7,
        "is_cancellation": 1,
        "is_negative_qty": 2,
        "is_nonpositive_price": 1,
        "is_non_product": 1,
        "is_missing_customer": 2,
        "is_duplicate": 1,
        "negative_qty_not_cancelled": 1,
    }
    assert set(FLAGS) <= set(result.lines.columns)


def test_line_value_signed():
    result = clean_transactions(lines())
    assert result.lines["line_value"].tolist()[:2] == [15.0, -15.0]


def test_customer_lines_keeps_cancellations_drops_unusable():
    usable = customer_lines(clean_transactions(lines()).lines)
    assert usable["invoice"].tolist() == ["1", "C2", "6"]
```

- [ ] **Step 2: Run to verify failure** → FAIL.

- [ ] **Step 3: Implement `ml/retentionlens/data/clean.py`**

```python
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
```

- [ ] **Step 4: Run tests** → 3 PASS.
- [ ] **Step 5: Commit** `git commit -m "feat(ml): flag cancellations, returns, non-products and duplicates"`

### Task 5: Profile, register and CLI; run on the real file

**Files:**
- Create: `ml/retentionlens/data/profile.py`, `ml/retentionlens/cli.py`
- Test: `ml/tests/test_profile.py`
- Outputs (committed): `reports/data_profile.md`, `reports/data_profile.json`, row in `project/DATA_SOURCE_REGISTER.csv`

**Interfaces:**
- Consumes: `clean_transactions`, `customer_lines`, `load_or_cache`, `download_dataset`, `LICENCE`, `CITATION`.
- Produces: `build_profile(lines: DataFrame, issues: dict) -> dict`; `render_markdown(profile: dict, manifest: dict) -> str`; `upsert_register(csv_path: Path, row: dict) -> None`; CLI `uv run python -m retentionlens.cli data`.

- [ ] **Step 1: Write the failing tests**

```python
import csv

import pandas as pd

from retentionlens.data.clean import clean_transactions
from retentionlens.data.profile import build_profile, render_markdown, upsert_register


def sample():
    return pd.DataFrame(
        {
            "invoice": ["1", "C2", "3"],
            "stock_code": ["85123A", "85123A", "POST"],
            "description": ["A", "A", "POSTAGE"],
            "quantity": [6, -6, 1],
            "invoice_date": pd.to_datetime(["2009-12-01", "2010-01-05", "2011-12-09"]),
            "price": [2.5, 2.5, 18.0],
            "customer_id": pd.array(["1", "1", None], dtype="string"),
            "country": pd.array(["UK", "UK", "France"], dtype="string"),
            "source_sheet": ["a", "a", "b"],
        }
    )


def test_profile_counts():
    result = clean_transactions(sample())
    p = build_profile(result.lines, result.issues)
    assert p["rows"] == 3
    assert p["date_min"] == "2009-12-01" and p["date_max"] == "2011-12-09"
    assert p["customers"] == 1 and p["countries"] == 2 and p["invoices"] == 3
    assert p["rows_by_sheet"] == {"a": 2, "b": 1}
    assert p["top_non_product_codes"] == {"POST": 1}
    assert p["customer_model_rows"] == 2
    assert p["customer_model_net_value"] == 0.0


def test_markdown_mentions_source_and_checksum():
    result = clean_transactions(sample())
    md = render_markdown(build_profile(result.lines, result.issues), {"zip_sha256": "abc", "url": "u", "licence": "CC BY 4.0", "citation": "c", "accessed_at": "t"})
    assert "abc" in md and "CC BY 4.0" in md and "| Rows | 3 |" in md


def test_register_upsert_is_idempotent(tmp_path):
    path = tmp_path / "reg.csv"
    path.write_text("name,url,version,access_date,license,sha256,allowed_use,notes\n")
    row = {"name": "online_retail_ii", "url": "u", "version": "v", "access_date": "d", "license": "CC BY 4.0", "sha256": "s", "allowed_use": "a", "notes": "n"}
    upsert_register(path, row)
    upsert_register(path, {**row, "sha256": "s2"})
    rows = list(csv.DictReader(path.open()))
    assert len(rows) == 1 and rows[0]["sha256"] == "s2"
```

- [ ] **Step 2: Run to verify failure** → FAIL.

- [ ] **Step 3: Implement `ml/retentionlens/data/profile.py`**

```python
"""Aggregate data-quality profile, report rendering and source register."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from .clean import customer_lines

REGISTER_FIELDS = ["name", "url", "version", "access_date", "license", "sha256", "allowed_use", "notes"]


def build_profile(lines: pd.DataFrame, issues: dict) -> dict:
    usable = customer_lines(lines)
    non_product = lines.loc[lines["is_non_product"], "stock_code"].value_counts().head(15)
    return {
        "rows": int(len(lines)),
        "date_min": lines["invoice_date"].min().date().isoformat(),
        "date_max": lines["invoice_date"].max().date().isoformat(),
        "invoices": int(lines["invoice"].nunique()),
        "customers": int(lines["customer_id"].nunique()),
        "countries": int(lines["country"].nunique()),
        "rows_by_sheet": {str(k): int(v) for k, v in lines["source_sheet"].value_counts().sort_index().items()},
        "issues": {k: int(v) for k, v in issues.items()},
        "top_non_product_codes": {str(k): int(v) for k, v in non_product.items()},
        "customer_model_rows": int(len(usable)),
        "customer_model_customers": int(usable["customer_id"].nunique()),
        "customer_model_net_value": round(float(usable["line_value"].sum()), 2),
    }


def render_markdown(profile: dict, manifest: dict) -> str:
    issues = profile["issues"]
    pct = lambda n: f"{100 * n / profile['rows']:.1f}%"  # noqa: E731
    lines = [
        "# Data profile — UCI Online Retail II",
        "",
        "Generated by `uv run python -m retentionlens.cli data`. Every number below is computed from the local file; none is typed by hand.",
        "",
        f"- Source: {manifest['url']}",
        f"- Licence: {manifest['licence']} · Citation: {manifest['citation']}",
        f"- Archive SHA-256: `{manifest['zip_sha256']}` · accessed {manifest['accessed_at']}",
        "",
        "## Shape",
        "",
        "| Measure | Value |",
        "|---|---|",
        f"| Rows | {profile['rows']} |",
        f"| Date range | {profile['date_min']} to {profile['date_max']} |",
        f"| Invoices | {profile['invoices']} |",
        f"| Customers (with ID) | {profile['customers']} |",
        f"| Countries | {profile['countries']} |",
        *[f"| Rows in sheet `{k}` | {v} |" for k, v in profile["rows_by_sheet"].items()],
        "",
        "## Data-quality flags (rows are flagged, never silently dropped)",
        "",
        "| Flag | Rows | Share |",
        "|---|---|---|",
        *[f"| `{k}` | {v} | {pct(v)} |" for k, v in issues.items() if k != "rows"],
        "",
        "## Most common non-product stock codes",
        "",
        "| Code | Rows |",
        "|---|---|",
        *[f"| `{k}` | {v} |" for k, v in profile["top_non_product_codes"].items()],
        "",
        "## Rows usable for customer-level models",
        "",
        "Known customer, product line, price above zero, not a duplicate. Cancellations are kept so spend nets correctly.",
        "",
        f"- Rows: {profile['customer_model_rows']} ({pct(profile['customer_model_rows'])})",
        f"- Customers: {profile['customer_model_customers']}",
        f"- Net line value: £{profile['customer_model_net_value']:,.2f}",
        "",
    ]
    return "\n".join(lines)


def upsert_register(csv_path: Path, row: dict) -> None:
    rows = []
    if csv_path.exists():
        rows = [r for r in csv.DictReader(csv_path.open(newline="")) if r.get("name") != row["name"]]
    rows.append({k: row.get(k, "") for k in REGISTER_FIELDS})
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
```

- [ ] **Step 4: Implement `ml/retentionlens/cli.py`**

```python
"""Command line entry point: `uv run python -m retentionlens.cli data`."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data.clean import clean_transactions
from .data.download import CITATION, LICENCE, MANIFEST_NAME, download_dataset
from .data.load import load_or_cache
from .data.profile import build_profile, render_markdown, upsert_register

REPO = Path(__file__).resolve().parents[2]


def run_data(repo: Path) -> dict:
    raw, interim, reports = repo / "data" / "raw", repo / "data" / "interim", repo / "reports"
    result = download_dataset(raw)
    df = load_or_cache(result.xlsx_path, interim / "transactions_raw.parquet")
    cleaned = clean_transactions(df)
    cleaned.lines.to_parquet(interim / "transactions_flagged.parquet", index=False)
    profile = build_profile(cleaned.lines, cleaned.issues)
    manifest = json.loads((raw / MANIFEST_NAME).read_text())
    reports.mkdir(exist_ok=True)
    (reports / "data_profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    (reports / "data_profile.md").write_text(render_markdown(profile, manifest))
    upsert_register(
        repo / "project" / "DATA_SOURCE_REGISTER.csv",
        {
            "name": "online_retail_ii",
            "url": manifest["url"],
            "version": "UCI id 502 (donated 2019-09-20)",
            "access_date": manifest["accessed_at"][:10],
            "license": LICENCE,
            "sha256": manifest["zip_sha256"],
            "allowed_use": "Coursework and public portfolio with attribution; raw file not redistributed in repo",
            "notes": CITATION,
        },
    )
    return profile


def main() -> None:
    parser = argparse.ArgumentParser(prog="retentionlens")
    parser.add_argument("command", choices=["data"])
    args = parser.parse_args()
    if args.command == "data":
        profile = run_data(REPO)
        print(json.dumps({k: profile[k] for k in ("rows", "date_min", "date_max", "customers", "customer_model_rows")}))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run unit tests** — `uv run pytest -v` → all PASS (14 tests).
- [ ] **Step 6: Run on the real data** — `uv run python -m retentionlens.cli data` (downloads ~44 MB once; Excel parse takes a few minutes). Expected: JSON line with `"rows": 1067371`, `"date_min": "2009-12-01"`, `"date_max": "2011-12-09"`. If counts differ from UCI's published 1,067,371, record the difference; do not adjust.
- [ ] **Step 7: Commit** `git add ml reports/data_profile.* project/DATA_SOURCE_REGISTER.csv && git commit -m "feat(ml): data profile report and source register from real file"`

### Task 6: Data card and docs

**Files:**
- Create: `docs/DATA_CARD.md`
- Modify: `README.md` (add "ML pipeline" run section), `project/CURRENT_STATE.md`, `project/SESSION_LOG.md`, `project/NEXT_ACTIONS.md`

- [ ] **Step 1:** Write `docs/DATA_CARD.md` with the dataset card checklist from `docs/DATA_AND_RESEARCH.md` (owner, release, access date, URL, citation, licence, checksum, granularity = invoice line, timestamp unit = minute, labels = none, missing fields, PII = pseudonymous numeric customer IDs, commercial use = allowed with attribution, preprocessing = flags from `clean.py`, splits = defined in P2, derived artefacts, deletion plan), copying every number from `reports/data_profile.json`.
- [ ] **Step 2:** Add to `README.md`: `cd ml && uv sync --python 3.12 && uv run pytest && uv run python -m retentionlens.cli data`.
- [ ] **Step 3:** Update project state files with commands run and observed outputs.
- [ ] **Step 4: Commit** `git commit -m "docs: data card and P1 run instructions"`
