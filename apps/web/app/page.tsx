"use client";
import dynamic from "next/dynamic";
import Link from "next/link";
import { type Account, asset, type Cohort, type Summary, useApi } from "@/lib/api";
import { count, fixed, money, moneyShort } from "@/lib/format";
import { useTokens } from "@/lib/tokens";
import { ErrorState, Loading, PageHeader, Provenance, RiskPill } from "@/components/ui";

const CohortTerrain = dynamic(() => import("@/components/CohortTerrain"), {
  ssr: false,
  loading: () => <div className="skeleton" style={{ height: 420 }} />,
});

export default function Overview() {
  const summary = useApi<Summary>("/api/summary");
  const queue = useApi<{ total: number; items: Account[] }>("/api/accounts?limit=8&sort=value_at_risk_90&band=high");
  const cohorts = useApi<Cohort[]>("/api/cohorts");
  const tokens = useTokens();
  const s = summary.data;

  if (summary.error) return <section className="glass panel"><ErrorState message={summary.error} onRetry={summary.reload} /></section>;

  return (
    <>
      <section className="glass hero">
        <div className="copy">
          <p className="eyebrow">Weekly account review · scored {s?.scoring_cutoff ?? "…"}</p>
          <h1>See retention as a landscape.</h1>
          <p className="lede">
            Ninety-day lapse risk and expected spend for every wholesale account, the evidence behind each call, and outreach you approve before anything leaves.
          </p>
          <div className="row" style={{ marginTop: 18, gap: 10 }}>
            <Link className="btn primary" href="/accounts?band=high">Review high-risk accounts</Link>
            <Link className="btn" href="/model-lab">How accurate is this?</Link>
          </div>
        </div>
        <img className="only-dark" src={asset("/img/aur-01-hero.webp")} alt="" />
        <img className="only-light" src={asset("/img/aur-01-hero-light.webp")} alt="" />
      </section>

      <section className="stats" aria-label="Key figures">
        <div className="glass stat">
          <span className="label">High-risk accounts</span>
          <span className="value tone-high">{s ? count(s.bands.high) : "…"}</span>
          <span className="sub">of {s ? count(s.accounts) : "…"} · P(no order in 90 days) ≥ 75%</span>
        </div>
        <div className="glass stat">
          <span className="label">Spend at risk, high-risk accounts</span>
          <span className="value">{s ? moneyShort(s.value_at_risk_high) : "…"}</span>
          <span className="sub">usual 90-day spend × lapse probability</span>
        </div>
        <div className="glass stat">
          <span className="label">Expected spend, next 90 days</span>
          <span className="value">{s ? moneyShort(s.expected_value_total) : "…"}</span>
          <span className="sub">BG/NBD × Gamma-Gamma, net of returns</span>
        </div>
        <div className="glass stat">
          <span className="label">Model PR-AUC on frozen test</span>
          <span className="value tone-healthy">{s ? fixed(s.frozen_test.pr_auc) : "…"}</span>
          <span className="sub">Brier {s ? fixed(s.frozen_test.brier, 4) : "…"} · {s ? count(s.frozen_test.customers) : "…"} customers, {s?.frozen_test.cutoff}</span>
        </div>
      </section>

      <div className="row">
        <section className="glass panel" style={{ flex: "999 1 560px" }}>
          <div className="panel-head">
            <h2>Cohort retention terrain</h2>
            <span className="hint">x months since first order · z first-order month · height share who bought again</span>
          </div>
          {cohorts.error && <ErrorState message={cohorts.error} onRetry={cohorts.reload} />}
          {cohorts.data && <CohortTerrain cohorts={cohorts.data} tokens={tokens} />}
          <div className="legend">
            <span><i style={{ background: "var(--cyan)" }} />High repeat rate</span>
            <span><i style={{ background: "var(--amber)" }} />Fading</span>
            <span><i style={{ background: "var(--magenta)" }} />Low</span>
            <span>Drag to orbit · scroll to zoom</span>
          </div>
          {cohorts.data && (
            <details className="twin">
              <summary>View the same data as a table</summary>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ maxHeight: 320, marginTop: 10 }}>
                <table>
                  <thead>
                    <tr>
                      <th>Cohort</th>
                      <th className="num">Customers</th>
                      {[1, 2, 3, 6, 12].map((m) => <th key={m} className="num">Month {m}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {cohorts.data.map((c) => (
                      <tr key={c.cohort}>
                        <td className="mono">{c.cohort}</td>
                        <td className="num">{c.size}</td>
                        {[1, 2, 3, 6, 12].map((m) => <td key={m} className="num">{c.retention[m] != null ? `${(c.retention[m] * 100).toFixed(1)}%` : "—"}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          )}
        </section>

        <section className="glass panel" style={{ flex: "1 1 340px" }}>
          <div className="panel-head">
            <h2>Call first</h2>
            <span className="hint">high risk, most spend at stake</span>
          </div>
          {queue.loading && <Loading rows={6} />}
          {queue.error && <ErrorState message={queue.error} onRetry={queue.reload} />}
          {queue.data?.items.map((a) => (
            <Link key={a.customer_id} href={`/accounts?id=${a.customer_id}`} className="queue-item">
              <span>
                <strong>Account {a.customer_id}</strong>
                <small>{a.reasons[0]}</small>
              </span>
              <span style={{ textAlign: "right" }}>
                <RiskPill band={a.risk_band} p={a.p_lapse} />
                <small className="mono">{money(a.value_at_risk_90)} at risk</small>
              </span>
            </Link>
          ))}
          <Link className="btn" href="/accounts?band=high">Open the full queue</Link>
        </section>
      </div>
      <Provenance summary={s} />
    </>
  );
}
