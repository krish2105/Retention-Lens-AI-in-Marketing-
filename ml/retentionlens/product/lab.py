"""Product lab (weeks 7–8): basket rules, price elasticity, portfolio matrix and product loyalty.

Everything here is associational: the data has no experiments, so none of it is a causal effect.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


def basket_rules(lines: pd.DataFrame, top_products: int = 200, min_support: float = 0.01, min_lift: float = 2.0, limit: int = 40) -> list[dict]:
    sales = lines[lines["is_sale"]][["invoice", "stock_code", "description"]].drop_duplicates(["invoice", "stock_code"])
    keep = set(sales["stock_code"].value_counts().head(top_products).index)
    sales = sales[sales["stock_code"].isin(keep)]
    names = sales.drop_duplicates("stock_code").set_index("stock_code")["description"].fillna("").map(lambda s: " ".join(str(s).split()).title()).to_dict()
    n = sales["invoice"].nunique()
    single = sales["stock_code"].value_counts()
    pairs: Counter = Counter()
    for items in sales.groupby("invoice")["stock_code"].apply(sorted):
        pairs.update(combinations(items, 2))
    rules = []
    for (a, b), both in pairs.items():
        support = both / n
        if support < min_support:
            continue
        for x, y in ((a, b), (b, a)):
            confidence = both / single[x]
            lift = confidence / (single[y] / n)
            if lift >= min_lift:
                rules.append({"if": names[x], "then": names[y], "support": round(support, 4), "confidence": round(confidence, 3), "lift": round(lift, 2), "invoices": int(both)})
    return sorted(rules, key=lambda r: (-r["lift"], -r["support"]))[:limit]


def elasticity(weekly: pd.DataFrame) -> dict | None:
    """log(quantity) = a + b·log(price) + quarter dummies. Returns b with a 95% interval."""
    weekly = weekly[(weekly["quantity"] > 0) & (weekly["price"] > 0)]
    if len(weekly) < 20 or weekly["price"].nunique() < 4:
        return None
    quarter = pd.get_dummies(weekly.index.quarter, prefix="q", drop_first=True).astype(float).to_numpy()
    x = np.column_stack([np.ones(len(weekly)), np.log(weekly["price"].to_numpy()), quarter])
    y = np.log(weekly["quantity"].to_numpy())
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    dof = max(len(y) - x.shape[1], 1)
    cov = (resid @ resid / dof) * np.linalg.pinv(x.T @ x)
    se = float(np.sqrt(cov[1, 1]))
    r2 = 1 - float(resid @ resid) / float(((y - y.mean()) ** 2).sum())
    return {"elasticity": round(float(beta[1]), 3), "ci_low": round(float(beta[1] - 1.96 * se), 3), "ci_high": round(float(beta[1] + 1.96 * se), 3), "weeks": int(len(y)), "r2": round(r2, 3)}


def price_elasticities(lines: pd.DataFrame, top_products: int = 30) -> list[dict]:
    sales = lines[lines["is_sale"]]
    out = []
    for code in sales["stock_code"].value_counts().head(top_products).index:
        item = sales[sales["stock_code"] == code]
        weekly = item.set_index("day").resample("W").apply(
            lambda w: pd.Series({"quantity": w["quantity"].sum(), "price": (w["price"] * w["quantity"]).sum() / max(w["quantity"].sum(), 1)})
        )
        result = elasticity(weekly)
        if result:
            out.append({"product": " ".join(str(item["description"].iloc[0]).split()).title(), **result})
    return sorted(out, key=lambda r: r["elasticity"])


def portfolio(lines: pd.DataFrame, top_products: int = 40) -> list[dict]:
    """Volume vs growth (Jan–Nov 2011 vs Jan–Nov 2010), a BCG-style view of the range."""
    sales = lines[lines["is_sale"]].assign(month=lambda d: d["day"].dt.month, year=lambda d: d["day"].dt.year)
    window = sales[sales["month"] <= 11]
    by_year = window.groupby(["stock_code", "year"])["sale_value"].sum().unstack(fill_value=0)
    if 2010 not in by_year or 2011 not in by_year:
        return []
    top = by_year[2011].sort_values(ascending=False).head(top_products).index
    names = sales.drop_duplicates("stock_code").set_index("stock_code")["description"]
    median_sales = float(by_year.loc[top, 2011].median())
    rows = []
    for code in top:
        before, after = float(by_year.loc[code, 2010]), float(by_year.loc[code, 2011])
        growth = (after - before) / before if before > 0 else None
        rows.append({"product": " ".join(str(names[code]).split()).title(), "sales_2011": round(after, 2), "sales_2010": round(before, 2),
                     "growth": None if growth is None else round(growth, 3),
                     "quadrant": None if growth is None else ("Star" if after >= median_sales and growth > 0 else "Cash cow" if after >= median_sales else "Question mark" if growth > 0 else "Dog")})
    return rows


def product_loyalty(lines: pd.DataFrame, top_products: int = 40, min_buyers: int = 50) -> list[dict]:
    """Share of a product's buyers who bought it again on a later day: a simple brand-loyalty signal."""
    sales = lines[lines["is_sale"]]
    top = sales["stock_code"].value_counts().head(top_products).index
    days = sales[sales["stock_code"].isin(top)].groupby(["stock_code", "customer_id"], observed=True)["day"].nunique().reset_index()
    names = sales.drop_duplicates("stock_code").set_index("stock_code")["description"]
    out = []
    for code, group in days.groupby("stock_code"):
        if len(group) >= min_buyers:
            out.append({"product": " ".join(str(names[code]).split()).title(), "buyers": int(len(group)), "repeat_rate": round(float((group["day"] > 1).mean()), 3)})
    return sorted(out, key=lambda r: -r["repeat_rate"])


def build_product_lab(prepared: pd.DataFrame, scored: pd.DataFrame, out: Path):
    payload = {
        "rules": basket_rules(prepared),
        "elasticities": price_elasticities(prepared),
        "portfolio": portfolio(prepared),
        "loyalty": product_loyalty(prepared),
        "caveats": [
            "Association, not causation: no prices or promotions were randomised.",
            "Wholesale price breaks mean larger orders get lower unit prices, which biases elasticities towards negative values.",
            "Rules use invoices from customers with an ID only.",
        ],
    }
    (out / "product_lab.json").write_text(json.dumps(payload, separators=(",", ":")))
    return None
