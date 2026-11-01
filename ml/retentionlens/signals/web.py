"""Web signal (outcome B): Wikipedia pageview seasonality vs sales seasonality by product theme.

Wikimedia pageviews start in mid-2015, so they cannot overlap the 2009–2011 invoices. We compare
month-of-year *shape* (when interest peaks), not same-month values.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

USER_AGENT = "RetentionLens-coursework/0.3 (MAIB AI 208; github.com/krish2105)"
API = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{article}/monthly/2016010100/2025123100"
THEMES = {
    "Christmas": {"pattern": r"CHRISTMAS|XMAS", "article": "Christmas_decoration"},
    "Candles and lights": {"pattern": r"CANDLE|T-LIGHT|TEALIGHT|LANTERN", "article": "Candle"},
    "Bags": {"pattern": r"\bBAG\b|BAGS", "article": "Tote_bag"},
    "Mugs and cups": {"pattern": r"\bMUG\b|MUGS|\bCUP\b|CUPS", "article": "Mug"},
}


def month_index(values: pd.Series) -> list[float]:
    """Average value per calendar month divided by the overall monthly average (1.0 = typical month)."""
    by_month = values.groupby(values.index.month).mean().reindex(range(1, 13))
    return [round(float(v), 4) for v in (by_month / by_month.mean()).fillna(0)]


def fetch_pageviews(article: str, cache_dir: Path) -> tuple[pd.Series, dict]:
    cache = cache_dir / f"wikimedia_{article}.json"
    if not cache.exists():
        request = urllib.request.Request(API.format(article=article), headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        payload["_accessed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(payload))
    payload = json.loads(cache.read_text())
    items = payload["items"]
    series = pd.Series({pd.Timestamp(i["timestamp"][:8]): i["views"] for i in items}).sort_index()
    return series, {"article": article, "months": len(series), "first": str(series.index.min().date()), "last": str(series.index.max().date()), "accessed_at": payload.get("_accessed_at")}


def theme_sales(lines: pd.DataFrame, pattern: str) -> pd.Series:
    """Monthly sale value of product lines whose description matches the theme (full calendar months only)."""
    match = lines["description"].fillna("").str.upper().str.contains(pattern, regex=True)
    sales = lines[match & lines["is_sale"]]
    monthly = sales.groupby(sales["day"].dt.to_period("M"))["sale_value"].sum()
    monthly = monthly[(monthly.index >= pd.Period("2009-12")) & (monthly.index <= pd.Period("2011-11"))]
    return pd.Series(monthly.to_numpy(), index=monthly.index.to_timestamp())


def web_signals(lines: pd.DataFrame, cache_dir: Path) -> dict:
    out = []
    for theme, spec in THEMES.items():
        sales = theme_sales(lines, spec["pattern"])
        try:
            views, meta = fetch_pageviews(spec["article"], cache_dir)
        except OSError as error:
            out.append({"theme": theme, "available": False, "error": str(error)})
            continue
        s_idx, w_idx = month_index(sales), month_index(views)
        out.append({
            "theme": theme,
            "available": True,
            "sales_index": s_idx,
            "web_index": w_idx,
            "correlation": round(float(np.corrcoef(s_idx, w_idx)[0, 1]), 3),
            # Wholesale buying should lead consumer interest: compare sales with web interest one month later.
            "correlation_web_one_month_later": round(float(np.corrcoef(s_idx, np.roll(w_idx, -1))[0, 1]), 3),
            "sales_peak_month": int(np.argmax(s_idx) + 1),
            "web_peak_month": int(np.argmax(w_idx) + 1),
            "sales_total": round(float(sales.sum()), 2),
            "source": meta,
        })
    return {"themes": out, "licence": "Wikimedia pageviews data: CC0", "note": "Pageviews cover 2016–2025; invoices cover 2009–2011. Only seasonal shape is compared."}
