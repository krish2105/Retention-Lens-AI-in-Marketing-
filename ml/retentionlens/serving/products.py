"""Top products per account, so drafts can mention what the customer actually buys."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_account_products(prepared: pd.DataFrame, scored: pd.DataFrame, out: Path) -> pd.DataFrame:
    sales = prepared[prepared["is_sale"]]
    totals = sales.groupby(["customer_id", "description"], observed=True)["sale_value"].sum().reset_index()
    totals = totals.sort_values(["customer_id", "sale_value"], ascending=[True, False])
    top = totals.groupby("customer_id", observed=True)["description"].apply(lambda d: [" ".join(str(x).split()).title() for x in d.head(3)])
    return pd.DataFrame({"top_products": top.reindex(scored.index)})
