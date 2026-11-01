"""Segments (week 5): RFM scores and named segments, k-means clusters, 3D galaxy points,
and lookalike scoring of new customers against those who became high-value."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PLAYBOOK = {
    "Champions": "Thank them, offer early access to new ranges, ask for referrals.",
    "Loyal": "Keep cadence; suggest complementary lines from basket rules.",
    "Can't lose": "Personal call from the account manager this week.",
    "At risk": "Check-in with a reason to reorder (new season, stock held).",
    "New": "Onboarding follow-up after the first delivery.",
    "Promising": "Second-order nudge with lines they have not tried.",
    "Hibernating": "Low-cost reminder only; do not spend sales time.",
    "Needs attention": "Review the evidence before deciding.",
}


def rfm_scores(scored: pd.DataFrame) -> pd.DataFrame:
    """1–5 quintile scores; recency is reversed so 5 means most recent."""
    def quintile(series: pd.Series, reverse: bool = False) -> pd.Series:
        ranks = series.rank(method="first", ascending=not reverse)
        return pd.qcut(ranks, 5, labels=[1, 2, 3, 4, 5]).astype(int)

    return pd.DataFrame(
        {
            "r_score": quintile(scored["recency_days"], reverse=True),
            "f_score": quintile(scored["frequency"]),
            "m_score": quintile(scored["net_sales_total"]),
        },
        index=scored.index,
    )


def name_segment(r: int, f: int, m: int) -> str:
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r <= 2 and f >= 4 and m >= 4:
        return "Can't lose"
    if f >= 4 and r >= 3:
        return "Loyal"
    if r <= 2 and f >= 3:
        return "At risk"
    if r >= 4 and f <= 1:
        return "New"
    if r >= 3 and f <= 2:
        return "Promising"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs attention"


def _log_features(scored: pd.DataFrame) -> np.ndarray:
    return np.column_stack([
        np.log1p(scored["recency_days"]),
        np.log1p(scored["frequency"]),
        np.log1p(scored["net_sales_total"].clip(lower=0)),
    ])


def clusters(scored: pd.DataFrame, seed: int = 42) -> tuple[pd.Series, dict]:
    x = StandardScaler().fit_transform(_log_features(scored))
    rng = np.random.default_rng(seed)
    sample = rng.choice(len(x), size=min(3000, len(x)), replace=False)
    scores = {}
    models = {}
    for k in range(3, 7):
        model = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(x)
        scores[k] = float(silhouette_score(x[sample], model.labels_[sample]))
        models[k] = model
    best = max(scores, key=scores.get)
    return pd.Series(models[best].labels_, index=scored.index, name="cluster"), {"k": best, "silhouette": scores}


def galaxy_points(scored: pd.DataFrame, segments: pd.Series) -> list[dict]:
    feats = _log_features(scored)
    lo, hi = feats.min(axis=0), feats.max(axis=0)
    unit = 2 * (feats - lo) / np.where(hi > lo, hi - lo, 1) - 1
    unit[:, 0] *= -1  # recent customers on the right
    size = np.sqrt(scored["expected_value_90"].clip(lower=0).to_numpy())
    size = 0.4 + 1.6 * size / max(size.max(), 1e-9)
    return [
        {"id": str(cid), "x": round(float(u[0]), 4), "y": round(float(u[1]), 4), "z": round(float(u[2]), 4),
         "band": band, "segment": seg, "size": round(float(s), 3)}
        for cid, u, band, seg, s in zip(scored.index, unit, scored["risk_band"], segments, size)
    ]


def first_order_features(prepared: pd.DataFrame) -> pd.DataFrame:
    sales = prepared[prepared["is_sale"]]
    first_day = sales.groupby("customer_id", observed=True)["day"].min().rename("first_day")
    first = sales.join(first_day, on="customer_id")
    first = first[first["day"] == first["first_day"]]
    g = first.groupby("customer_id", observed=True)
    return pd.DataFrame({
        "first_day": first_day,
        "first_value": g["sale_value"].sum(),
        "first_lines": g.size(),
        "first_products": g["stock_code"].nunique(),
        "first_is_uk": g["country"].first() == "United Kingdom",
    })


LOOKALIKE_FEATURES = ["first_value", "first_lines", "first_products", "first_is_uk"]


def _lookalike_x(frame: pd.DataFrame) -> np.ndarray:
    x = frame[LOOKALIKE_FEATURES].astype(float).to_numpy()
    x[:, :3] = np.log1p(x[:, :3])
    return x


def lookalike_model(prepared: pd.DataFrame, cutoff: str, seed: int = 42) -> tuple[pd.Series, dict]:
    """Which brand-new customers look like the ones who became top-20% spenders in their first year?"""
    cut = pd.Timestamp(cutoff)
    feats = first_order_features(prepared)
    sales = prepared[prepared["is_sale"]].join(feats["first_day"], on="customer_id")
    in_year = sales[sales["day"] < sales["first_day"] + pd.Timedelta(days=365)]
    year_value = in_year.groupby("customer_id", observed=True)["sale_value"].sum()
    history = feats[feats["first_day"] <= cut - pd.Timedelta(days=365)].copy()
    history["year_value"] = year_value.reindex(history.index).fillna(0)
    history["top"] = (history["year_value"] >= history["year_value"].quantile(0.8)).astype(int)
    split = history["first_day"].quantile(0.7)
    train, test = history[history["first_day"] <= split], history[history["first_day"] > split]
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=seed))
    model.fit(_lookalike_x(train), train["top"])
    auc = float(roc_auc_score(test["top"], model.predict_proba(_lookalike_x(test))[:, 1]))
    model.fit(_lookalike_x(history), history["top"])
    newcomers = feats[(feats["first_day"] > cut - pd.Timedelta(days=90)) & (feats["first_day"] < cut)]
    scores = pd.Series(model.predict_proba(_lookalike_x(newcomers))[:, 1], index=newcomers.index, name="lookalike_score")
    meta = {
        "definition": "P(first-year spend in the top 20%) from first-order features, for customers whose first order was in the last 90 days",
        "features": LOOKALIKE_FEATURES,
        "train_customers": int(len(train)),
        "test_customers": int(len(test)),
        "test_auc": round(auc, 4),
        "split": "time-based: earliest 70% of first-order dates train, latest 30% test",
        "newcomers": int(len(newcomers)),
    }
    return scores, meta


def build_segments(prepared: pd.DataFrame, scored: pd.DataFrame, out: Path, cutoff: str = "2011-12-10") -> pd.DataFrame:
    rfm = rfm_scores(scored)
    segment = pd.Series([name_segment(r, f, m) for r, f, m in rfm.itertuples(index=False)], index=scored.index, name="segment")
    cluster, cluster_meta = clusters(scored)
    lookalike, lookalike_meta = lookalike_model(prepared, cutoff)

    frame = scored.join(rfm).assign(segment=segment, cluster=cluster)
    table = []
    for name, group in frame.groupby("segment"):
        table.append({
            "segment": name, "accounts": int(len(group)), "share": round(len(group) / len(frame), 4),
            "median_recency_days": float(group["recency_days"].median()),
            "median_purchase_days": float(group["frequency"].median() + 1),
            "median_net_spend": round(float(group["net_sales_total"].median()), 2),
            "expected_value_90": round(float(group["expected_value_90"].sum()), 2),
            "mean_p_lapse": round(float(group["p_lapse"].mean()), 4),
            "high_risk_share": round(float((group["risk_band"] == "high").mean()), 4),
            "play": PLAYBOOK[name],
        })
    profiles = [
        {"cluster": int(c), "accounts": int(len(g)), "median_recency_days": float(g["recency_days"].median()),
         "median_purchase_days": float(g["frequency"].median() + 1), "median_net_spend": round(float(g["net_sales_total"].median()), 2)}
        for c, g in frame.groupby("cluster")
    ]
    top_newcomers = lookalike.sort_values(ascending=False).head(25)
    (out / "segments.json").write_text(json.dumps({"segments": sorted(table, key=lambda r: -r["expected_value_90"]),
                                                   "clusters": {**cluster_meta, "profiles": profiles}}, separators=(",", ":")))
    (out / "galaxy.json").write_text(json.dumps(galaxy_points(scored, segment), separators=(",", ":")))
    (out / "lookalikes.json").write_text(json.dumps({**lookalike_meta, "top": [{"customer_id": str(k), "score": round(float(v), 4)} for k, v in top_newcomers.items()]}, separators=(",", ":")))
    return pd.concat([rfm, segment, cluster, lookalike.reindex(scored.index)], axis=1)
