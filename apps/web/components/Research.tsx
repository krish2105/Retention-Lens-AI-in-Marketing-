"use client";
import { useApi } from "@/lib/api";
import { fixed, pct } from "@/lib/format";
import { ErrorState } from "./ui";

type Lapse = { pr_auc: number; brier: number };
type Value = { normalized_gini: number; mae: number; total_bias: number };
type Interval = { calibrated_on: string; coverage: number; median_width: number };
type Cutoff = { role: string; customers: number; season: { multiplier: number }; lapse: Record<string, Lapse>; value: Record<string, Value>; intervals: Record<string, Interval> };
type R5 = { generated_at: string; dev_cutoffs: string[]; cutoffs: Record<string, Cutoff>; summary: Record<string, unknown> };
type Registry = { serving: { name: string; version: string }; models: { name: string; status: string }[] };

const ROWS: [string, string, string][] = [
  ["BG/NBD + Gamma-Gamma", "bgnbd", "bgnbd_gamma_gamma"],
  ["… with seasonal multiplier (served)", "bgnbd_seasonal", "bgnbd_gamma_gamma_seasonal"],
  ["LightGBM", "lightgbm", "lightgbm"],
  ["LightGBM + seasonal features", "lightgbm_seasonal", "lightgbm_seasonal"],
  ["ZILN neural network", "ziln_nn", "ziln_nn"],
];
const INTERVALS: [string, string][] = [
  ["Previous 90 days", "bgnbd_gamma_gamma_seasonal"],
  ["Same window last year", "seasonal_same_window_last_year"],
  ["Pooled (served, R5b)", "seasonal_pooled"],
];

/** R5 results: seasonality, value ranges and the deep-learning challenger, straight from reports/r5_results.json. */
export function Research() {
  const res = useApi<{ r5: R5 | null; registry: Registry | null }>("/api/research");
  if (res.error) return <section className="glass panel"><ErrorState message={res.error} onRetry={res.reload} /></section>;
  const r5 = res.data?.r5;
  if (!r5) return null;
  const cutoffs = Object.entries(r5.cutoffs);
  return (
    <>
      <section className="glass panel">
        <div className="panel-head">
          <h2>R5: seasonality and a neural challenger</h2>
          <span className="hint">dev cutoffs choose; {cutoffs.find(([, c]) => c.role !== "dev")?.[0]} is a labelled post-hoc look</span>
        </div>
        <div className="table-wrap" tabIndex={0} role="region" aria-label="R5 model comparison">
          <table>
            <thead>
              <tr><th>Model</th>{cutoffs.map(([c, v]) => <th key={c} className="num" colSpan={1}>{c}{v.role !== "dev" ? " · post hoc" : ""}</th>)}</tr>
            </thead>
            <tbody>
              {ROWS.map(([label, lapseKey, valueKey]) => (
                <tr key={label}>
                  <td>{label}</td>
                  {cutoffs.map(([c, v]) => (
                    <td key={c} className="num">
                      PR-AUC {fixed(v.lapse[lapseKey]?.pr_auc)}<br />
                      <small style={{ color: "var(--muted)" }}>bias {v.value[valueKey] ? `${v.value[valueKey].total_bias > 0 ? "+" : ""}${pct(v.value[valueKey].total_bias)}` : "—"} · MAE £{fixed(v.value[valueKey]?.mae, 0)}</small>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="provenance"><span>Total-spend bias = predicted ÷ actual − 1 across all accounts.</span><span>Season multipliers: {cutoffs.map(([c, v]) => `${c} ${v.season.multiplier}`).join(" · ")}</span></p>
      </section>
      <div className="row">
        <section className="glass panel" style={{ flex: "1 1 420px" }}>
          <div className="panel-head"><h2>80% value ranges: how often the truth landed inside</h2></div>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Interval coverage">
            <table>
              <thead><tr><th>Calibrated on</th>{cutoffs.map(([c]) => <th key={c} className="num">{c}</th>)}</tr></thead>
              <tbody>
                {INTERVALS.map(([label, key]) => (
                  <tr key={key}>
                    <td>{label}</td>
                    {cutoffs.map(([c, v]) => {
                      const cov = v.intervals[key]?.coverage;
                      const ok = cov != null && Math.abs(cov - 0.8) <= 0.05;
                      return <td key={c} className="num" style={{ color: ok ? "var(--cyan)" : "var(--magenta)" }}>{cov == null ? "—" : pct(cov, 1)}</td>;
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="provenance"><span>Target 80% ± 5 points (in colour when met). Pooling was chosen after seeing the peak window, so its peak number is optimistic.</span></p>
        </section>
        {res.data?.registry && (
          <section className="glass panel" style={{ flex: "1 1 380px" }}>
            <h2>Model registry</h2>
            <p>Serving: <strong>{res.data.registry.serving.version}</strong></p>
            <ul className="reasons">
              {res.data.registry.models.map((m) => <li key={m.name}><strong>{m.name}</strong>: {m.status}</li>)}
            </ul>
          </section>
        )}
      </div>
    </>
  );
}

type Backtest = {
  available: boolean; cutoff: string; reason?: string; customers?: number; base_rate?: number; pr_auc?: number; roc_auc?: number; brier?: number;
  top_lift?: number; baseline_rule_pr_auc?: number; value_gini?: number; value_mae?: number; total_actual?: number; total_pred?: number; method?: string;
  intervals?: { available: boolean; calibration_coverage?: number }; skipped_views?: Record<string, string>;
};

/** For uploaded data: one honest backtest on the customer's own last 90 days. */
export function UploadBacktest({ b }: { b: Backtest }) {
  return (
    <section className="glass panel">
      <div className="panel-head"><h2>How the model did on your last 90 days</h2><span className="hint">fitted before {b.cutoff}, checked on what happened next</span></div>
      {!b.available ? (
        <p className="notice">No backtest: {b.reason}</p>
      ) : (
        <>
          <div className="kv">
            <div><span>Accounts in the check</span><strong>{b.customers?.toLocaleString("en-GB")}</strong><span>{pct(b.base_rate ?? null)} did not reorder</span></div>
            <div><span>Lapse PR-AUC (model)</span><strong className="tone-healthy">{fixed(b.pr_auc)}</strong><span>simple rule: {fixed(b.baseline_rule_pr_auc)} · chance: {fixed(b.base_rate)}</span></div>
            <div><span>Brier score</span><strong>{fixed(b.brier, 4)}</strong><span>lower is better</span></div>
            <div><span>Top-10% lift</span><strong>{fixed(b.top_lift, 2)}×</strong><span>lapse rate in the riskiest tenth vs average</span></div>
            <div><span>Value ranking (Gini)</span><strong>{fixed(b.value_gini)}</strong><span>MAE £{fixed(b.value_mae, 0)}</span></div>
            <div><span>Total spend: predicted vs actual</span><strong>{b.total_actual ? `${b.total_pred! >= b.total_actual ? "+" : ""}${pct(b.total_pred! / b.total_actual - 1)}` : "—"}</strong><span>£{Math.round(b.total_pred ?? 0).toLocaleString("en-GB")} vs £{Math.round(b.total_actual ?? 0).toLocaleString("en-GB")}</span></div>
          </div>
          <p className="provenance"><span>{b.method}</span><span>One window is a sanity check, not a frozen test.</span></p>
        </>
      )}
      {b.skipped_views && Object.keys(b.skipped_views).length > 0 && (
        <p className="notice">Not built for this file: {Object.entries(b.skipped_views).map(([k, v]) => `${k} (${v})`).join("; ")}</p>
      )}
    </section>
  );
}
