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
