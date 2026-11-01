"use client";
import { useCallback, useEffect, useState } from "react";

export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Band = "high" | "watch" | "healthy";

export type Account = {
  customer_id: string;
  country: string;
  risk_band: Band;
  p_lapse: number;
  p_alive: number;
  expected_purchases_90: number;
  expected_value_90: number;
  value_at_risk_90: number;
  recency_days: number;
  tenure_days: number;
  frequency: number;
  sales_total: number;
  sales_last_90: number;
  sales_last_180: number;
  net_sales_total: number;
  returns_total: number;
  return_rate: number;
  distinct_products: number;
  mean_gap_days: number | null;
  reasons: string[];
  segment?: string;
  cluster?: number;
  lookalike_score?: number | null;
};

export type Summary = {
  generated_at: string;
  scoring_cutoff: string;
  horizon_days: number;
  model: string;
  data_sha256: string;
  data_source: string;
  licence: string;
  accounts: number;
  bands: Record<Band, number>;
  value_at_risk_high: number;
  expected_value_total: number;
  evaluation_run: string;
  frozen_test: { cutoff: string; customers: number; pr_auc: number; brier: number; value_gini: number };
};

export type Cohort = { cohort: string; size: number; retention: number[] };

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(API + path, { cache: "no-store" });
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      detail = (await response.json()).detail ?? detail;
    } catch {}
    throw new Error(String(detail));
  }
  return response.json();
}

export async function apiPost<T>(path: string, body: unknown, idempotencyKey?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
  const response = await fetch(API + path, { method: "POST", headers, body: JSON.stringify(body) });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail ?? response.status));
  return payload;
}

export function useApi<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(path));
  const load = useCallback(() => {
    if (!path) return;
    setLoading(true);
    setError(null);
    apiGet<T>(path)
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [path]);
  useEffect(load, [load]);
  return { data, error, loading, reload: load };
}
