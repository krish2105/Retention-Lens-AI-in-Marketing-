"use client";
import { useCallback, useEffect, useState } from "react";

export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
/** Public demo build: reads exported JSON instead of the API and is read-only. */
export const STATIC = process.env.NEXT_PUBLIC_STATIC === "1";
export const BASE = process.env.NEXT_PUBLIC_BASE_PATH || "";
export const asset = (path: string) => `${BASE}${path}`;
export const READ_ONLY_MESSAGE =
  "This public demo is read-only. Run RetentionLens on your own machine to record decisions and draft emails with the local AI model.";

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
  top_products?: string[];
  value_low_90?: number | null;
  value_high_90?: number | null;
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
  evaluation_run: string | null;
  frozen_test: { cutoff: string; customers: number; pr_auc: number; brier: number; value_gini: number } | null;
  intervals?: { available: boolean; level?: number; calibration_coverage?: number; reason?: string };
};

export type Me = {
  auth_mode: "off" | "local" | "supabase";
  user: { id: string; email: string; name: string };
  org: { id: string; name: string; plan: string; use_sample: boolean; active_dataset: string | null };
  role: "owner" | "reviewer" | "viewer";
  orgs: { id: string; name: string; role: string }[];
};

export type QueueItem = Pick<Account, "customer_id" | "country" | "risk_band" | "p_lapse" | "value_at_risk_90" | "expected_value_90" | "recency_days" | "segment" | "reasons"> & {
  status: "to_review" | "reviewed";
  decision: string | null;
  contacted: boolean;
};
export type Queue = { week: string; items: QueueItem[]; reviewed: number; total: number; cleared: boolean; holdout: number; holdout_share: number };

export type Cohort = { cohort: string; size: number; retention: number[] };

const cache = new Map<string, Promise<unknown>>();
function file<T>(name: string): Promise<T> {
  if (!cache.has(name)) {
    cache.set(name, fetch(asset(`/data/${name}.json`)).then((r) => {
      if (!r.ok) throw new Error(`Demo data ${name}.json is missing`);
      return r.json();
    }));
  }
  return cache.get(name) as Promise<T>;
}

const SORTABLE = new Set(["value_at_risk_90", "p_lapse", "expected_value_90", "recency_days", "net_sales_total", "frequency"]);

async function staticGet(path: string): Promise<unknown> {
  const url = new URL(path, "http://demo");
  const route = url.pathname;
  const simple: Record<string, string> = {
    "/api/summary": "summary", "/api/cohorts": "cohorts", "/api/model-eval": "model_eval", "/api/segments": "segments",
    "/api/galaxy": "galaxy", "/api/lookalikes": "lookalikes", "/api/signals": "signals", "/api/product-lab": "product_lab",
  };
  if (simple[route]) return file(simple[route]);
  if (route === "/api/health") {
    const summary = await file<Summary>("summary");
    return { ok: true, serving_ready: true, generated_at: summary.generated_at, ollama: { available: false, model: "qwen2.5:7b" }, static: true };
  }
  if (route === "/api/data") return { profile: await file("data_profile"), sources: await file("sources") };
  if (route === "/api/drafts" || route === "/api/audit" || route === "/api/datasets") return [];
  if (route === "/api/auth/me") return DEMO_ME;
  if (route === "/api/research") return { r5: await file("r5"), registry: await file("registry") };
  if (route === "/api/plans") return file("plans");
  if (route === "/api/billing") return { plan: "pilot", limits: null, usage: { active_accounts: (await file<Summary>("summary")).accounts, share: null }, billing_configured: false, note: "Public demo: billing runs only on a hosted server in Stripe test mode", status: "Pricing hypothesis: not yet validated with customers" };
  if (route === "/api/status") return file("status");
  if (route === "/api/org/members") return { members: [{ id: "demo", email: "demo@retentionlens.app", name: "Demo viewer", role: "viewer", created_at: null }], invites: [] };
  if (route === "/api/outcomes") return { arms: { contact: { accounts: 0, reordered: 0, rate: null, contacted: 0 }, holdout: { accounts: 0, reordered: 0, rate: null, contacted: 0 } }, uplift: { difference: null, ci95: null }, observe_days: 28, pending: 0, weeks: [], method: "No outreach is recorded in the public demo." };
  if (route === "/api/critic/calibration") return { labelled: 0, target: 46, kappa_target: 0.6 };
  if (route === "/api/queue") return staticQueue(await file<Account[]>("accounts"));
  if (route === "/api/accounts") {
    const q = url.searchParams;
    const term = (q.get("search") ?? "").trim().toLowerCase();
    const band = q.get("band") ?? "all";
    const sort = SORTABLE.has(q.get("sort") ?? "") ? (q.get("sort") as keyof Account) : "value_at_risk_90";
    const desc = (q.get("order") ?? "desc") === "desc";
    const limit = Number(q.get("limit") ?? 50), offset = Number(q.get("offset") ?? 0);
    let items = await file<Account[]>("accounts");
    if (term) items = items.filter((a) => a.customer_id.toLowerCase().includes(term) || (a.country ?? "").toLowerCase().includes(term));
    if (band !== "all") items = items.filter((a) => a.risk_band === band);
    items = [...items].sort((a, b) => ((Number(a[sort]) || 0) - (Number(b[sort]) || 0)) * (desc ? -1 : 1));
    return { total: items.length, items: items.slice(offset, offset + limit) };
  }
  const account = route.match(/^\/api\/accounts\/([^/]+)$/);
  if (account) {
    const found = (await file<Account[]>("accounts")).find((a) => a.customer_id === account[1]);
    if (!found) throw new Error("Unknown account");
    const timeline = await file<Record<string, unknown[]>>("timeline");
    return { account: found, timeline: timeline[account[1]] ?? [], reviews: [], drafts: [] };
  }
  throw new Error(READ_ONLY_MESSAGE);
}

const DEMO_ME: Me = {
  auth_mode: "off",
  user: { id: "demo", email: "demo@retentionlens.app", name: "Demo viewer" },
  org: { id: "demo", name: "Public demo", plan: "pilot", use_sample: true, active_dataset: null },
  role: "viewer",
  orgs: [{ id: "demo", name: "Public demo", role: "viewer" }],
};

/** Same rule as the API: top value-at-risk accounts, a seeded 20% holdout, this week's Monday. */
function staticQueue(accounts: Account[]): Queue {
  const today = new Date();
  const monday = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate() - ((today.getDay() + 6) % 7)));
  const week = monday.toISOString().slice(0, 10);
  const hash = (s: string) => [...s].reduce((h, c) => Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0, 2166136261) / 2 ** 32;
  const atRisk = accounts.filter((a) => a.risk_band !== "healthy").sort((a, b) => b.value_at_risk_90 - a.value_at_risk_90).slice(0, 32);
  const shown = atRisk.filter((a) => hash(`demo|${a.customer_id}|${week}`) >= 0.2).slice(0, 25);
  return {
    week,
    items: shown.map((a) => ({ ...a, segment: a.segment, status: "to_review", decision: null, contacted: false })),
    reviewed: 0,
    total: shown.length,
    cleared: false,
    holdout: atRisk.length - atRisk.filter((a) => hash(`demo|${a.customer_id}|${week}`) >= 0.2).length,
    holdout_share: 0.2,
  };
}

/** The API answers 401 when sign-in is on and the session is missing or expired. */
export class AuthRequired extends Error {}

const HEADERS = { "X-RL-Client": "web" };

export async function apiGet<T>(path: string): Promise<T> {
  if (STATIC) return staticGet(path) as Promise<T>;
  const response = await fetch(API + path, { cache: "no-store", credentials: "include", headers: { ...HEADERS } });
  if (response.status === 401) throw new AuthRequired("Sign in to continue");
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
  if (STATIC) throw new Error(READ_ONLY_MESSAGE);
  const headers: Record<string, string> = { "Content-Type": "application/json", ...HEADERS };
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
  const response = await fetch(API + path, { method: "POST", headers, body: JSON.stringify(body), credentials: "include" });
  const payload = await response.json().catch(() => ({}));
  if (response.status === 401 && !path.startsWith("/api/auth/sign")) throw new AuthRequired("Sign in to continue");
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail ?? response.status));
  return payload;
}

/** Raw file upload (CSV/XLSX bytes as the request body). */
export async function apiUpload<T>(path: string, file: File): Promise<T> {
  if (STATIC) throw new Error(READ_ONLY_MESSAGE);
  const response = await fetch(API + path, { method: "POST", body: file, credentials: "include", headers: { "Content-Type": file.type || "application/octet-stream", ...HEADERS } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : `Upload failed (${response.status})`);
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
      .catch((e: Error) => {
        if (e instanceof AuthRequired) {
          window.location.assign(`${BASE}/signin/?next=${encodeURIComponent(window.location.pathname)}`);
          return;
        }
        setError(e.message);
      })
      .finally(() => setLoading(false));
  }, [path]);
  useEffect(load, [load]);
  return { data, error, loading, reload: load };
}
