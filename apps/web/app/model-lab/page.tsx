"use client";
import { useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "@/lib/api";
import { fixed } from "@/lib/format";
import { useTokens } from "@/lib/tokens";
import { ErrorState, Loading, PageHeader } from "@/components/ui";

type Metrics = Record<string, number>;
type CutoffResult = {
  role: "dev" | "test";
  n_customers: number;
  n_train_rows: number;
  lapse: Record<string, Metrics>;
  value: Record<string, Metrics>;
  reliability: Record<string, { mean_pred: number | null; observed: number | null; n: number }[]>;
};
type Eval = { run_id: string; data_sha256: string; seed: number; cutoffs: Record<string, CutoffResult>; comparison: Record<string, Record<string, { wins: number; of: number }>>; versions: Record<string, string> };

const LAPSE = [["pr_auc", "PR-AUC", 3, true], ["roc_auc", "ROC-AUC", 3, true], ["brier", "Brier", 4, false], ["top_lift", "Top-10% lift", 2, true]] as const;
const VALUE = [["normalized_gini", "Normalised Gini", 3, true], ["mae", "MAE (£)", 1, false]] as const;
const NAMES: Record<string, string> = { recency_rule: "Recency rule", logistic_rfm: "Logistic RFM", bgnbd: "BG/NBD", lightgbm: "LightGBM", naive_last_90: "Last 90 days", bgnbd_gamma_gamma: "BG/NBD + Gamma-Gamma" };
const COLORS = ["cyan", "amber", "magenta", "violet"] as const;

function MetricTable({ data, kind, metric, digits, higher }: { data: Eval; kind: "lapse" | "value"; metric: string; digits: number; higher: boolean }) {
  const cutoffs = Object.keys(data.cutoffs);
  const models = Object.keys(data.cutoffs[cutoffs[0]][kind]);
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Model</th>
            {cutoffs.map((c) => <th key={c} className="num">{c}{data.cutoffs[c].role === "test" ? " · test" : ""}</th>)}
          </tr>
        </thead>
        <tbody>
          {models.map((m) => (
            <tr key={m}>
              <td>{NAMES[m] ?? m}</td>
              {cutoffs.map((c) => {
                const values = models.map((x) => data.cutoffs[c][kind][x][metric]);
                const best = higher ? Math.max(...values) : Math.min(...values);
                const v = data.cutoffs[c][kind][m][metric];
                return <td key={c} className="num" style={v === best ? { color: "var(--cyan)", fontWeight: 600 } : undefined}>{fixed(v, digits)}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ModelLab() {
  const result = useApi<Eval>("/api/model-eval");
  const tokens = useTokens();
  const [metric, setMetric] = useState(0);
  const data = result.data;
  const test = data ? Object.entries(data.cutoffs).find(([, r]) => r.role === "test") : undefined;
  const reliability = test
    ? test[1].reliability.bgnbd.map((b, i) => ({
        bin: b.mean_pred,
        ideal: b.mean_pred,
        ...Object.fromEntries(Object.entries(test[1].reliability).map(([m, bins]) => [m, bins[i].observed])),
      })).filter((r) => r.bin != null)
    : [];

  return (
    <>
      <PageHeader eyebrow="Model lab" title="Which model to trust, and how far." lede="Five cutoffs, a 90-day horizon, settings fixed before any result was seen, and one frozen test at 2011-09-01 scored once. The best value in each column is highlighted." />
      {result.error && <section className="glass panel"><ErrorState message={result.error} onRetry={result.reload} /></section>}
      {result.loading && <section className="glass panel"><Loading rows={8} /></section>}
      {data && (
        <>
          <section className="glass panel">
            <div className="panel-head">
              <h2>Lapse: will the account order in the next 90 days?</h2>
              <div className="segmented" role="group" aria-label="Lapse metric">
                {LAPSE.map(([, label], i) => <button key={label} type="button" aria-pressed={metric === i} onClick={() => setMetric(i)}>{label}</button>)}
              </div>
            </div>
            <MetricTable data={data} kind="lapse" metric={LAPSE[metric][0]} digits={LAPSE[metric][2]} higher={LAPSE[metric][3]} />
          </section>
          <div className="row">
            <section className="glass panel" style={{ flex: "1 1 460px" }}>
              <div className="panel-head"><h2>Calibration on the frozen test</h2><span className="hint">predicted vs observed lapse rate</span></div>
              <div style={{ height: 300 }}>
                <ResponsiveContainer>
                  <LineChart data={reliability} margin={{ top: 8, right: 12, bottom: 8, left: -8 }}>
                    <CartesianGrid stroke={tokens.edge} />
                    <XAxis dataKey="bin" type="number" domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} tick={{ fill: tokens.muted, fontSize: 11 }} />
                    <YAxis domain={[0, 1]} tick={{ fill: tokens.muted, fontSize: 11 }} />
                    <Tooltip contentStyle={{ background: tokens.bg, border: `1px solid ${tokens.edge}`, color: tokens.ink }} formatter={(v) => (v == null ? "—" : Number(v).toFixed(3))} labelFormatter={(v) => `predicted ≈ ${Number(v).toFixed(2)}`} />
                    <Legend wrapperStyle={{ color: tokens.muted, fontSize: 11 }} />
                    <Line dataKey="ideal" name="Perfect calibration" stroke={tokens.muted} strokeDasharray="4 4" dot={false} />
                    {Object.keys(test![1].reliability).map((m, i) => (
                      <Line key={m} dataKey={m} name={NAMES[m]} stroke={tokens[COLORS[i % COLORS.length]]} dot={{ r: 3 }} strokeWidth={2} connectNulls />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="provenance">Points below the dashed line: the model predicts more lapse than happened. The test window is the Christmas peak, and none of the models capture seasonality.</p>
            </section>
            <section className="glass panel" style={{ flex: "1 1 380px" }}>
              <h2>Value: expected 90-day spend</h2>
              {VALUE.map(([m, label, digits, higher]) => (
                <div key={m} className="grid" style={{ gap: 6 }}>
                  <h3>{label}</h3>
                  <MetricTable data={data} kind="value" metric={m} digits={digits} higher={higher} />
                </div>
              ))}
            </section>
          </div>
          <section className="glass panel">
            <h2>Does LightGBM beat each baseline? (a claim needs 3 of 4 cutoffs)</h2>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Comparison</th><th>Baseline</th><th className="num">LightGBM wins</th><th>Verdict</th></tr></thead>
                <tbody>
                  {Object.entries(data.comparison).flatMap(([comparison, baselines]) =>
                    Object.entries(baselines).map(([b, s]) => (
                      <tr key={comparison + b}>
                        <td>{comparison.replace("_", " ")}</td>
                        <td>{NAMES[b] ?? b}</td>
                        <td className="num">{s.wins} of {s.of}</td>
                        <td>{s.wins >= 3 ? "LightGBM better" : s.wins <= 1 ? "Baseline better" : "No clear winner"}</td>
                      </tr>
                    )),
                  )}
                </tbody>
              </table>
            </div>
            <p className="provenance">
              <span>run {data.run_id}</span><span>data sha256 {data.data_sha256.slice(0, 12)}…</span><span>seed {data.seed}</span>
              {Object.entries(data.versions).map(([k, v]) => <span key={k}>{k} {v}</span>)}
            </p>
          </section>
        </>
      )}
    </>
  );
}
