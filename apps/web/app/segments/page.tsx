"use client";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useState } from "react";
import { type Summary, useApi } from "@/lib/api";
import { count, money, pct } from "@/lib/format";
import { useTokens } from "@/lib/tokens";
import { type ColourMode, type GalaxyPoint, segmentColours } from "@/components/Galaxy";
import { ErrorState, Loading, PageHeader, Provenance } from "@/components/ui";

const Galaxy = dynamic(() => import("@/components/Galaxy"), { ssr: false, loading: () => <div className="skeleton" style={{ height: 520 }} /> });

type Segment = { segment: string; accounts: number; share: number; median_recency_days: number; median_purchase_days: number; median_net_spend: number; expected_value_90: number; mean_p_lapse: number; high_risk_share: number; play: string };
type Segments = { segments: Segment[]; clusters: { k: number; silhouette: Record<string, number>; profiles: { cluster: number; accounts: number; median_recency_days: number; median_purchase_days: number; median_net_spend: number }[] } };
type Lookalikes = { definition: string; test_auc: number; train_customers: number; test_customers: number; split: string; newcomers: number; top: { customer_id: string; score: number }[] };

export default function SegmentsPage() {
  const galaxy = useApi<GalaxyPoint[]>("/api/galaxy");
  const segments = useApi<Segments>("/api/segments");
  const lookalikes = useApi<Lookalikes>("/api/lookalikes");
  const summary = useApi<Summary>("/api/summary");
  const tokens = useTokens();
  const [mode, setMode] = useState<ColourMode>("risk");
  const colours = segmentColours(tokens);

  return (
    <>
      <PageHeader eyebrow="Segments · week 5" title="Every account as a star in the customer galaxy." lede="Position shows recency, purchase days and net spend. Size shows expected 90-day spend. Colour shows lapse risk or RFM segment. Select a point to open the account." />
      <section className="glass panel">
        <div className="panel-head">
          <h2>Customer galaxy</h2>
          <div className="segmented" role="group" aria-label="Colour points by">
            <button type="button" aria-pressed={mode === "risk"} onClick={() => setMode("risk")}>Colour by risk</button>
            <button type="button" aria-pressed={mode === "segment"} onClick={() => setMode("segment")}>Colour by segment</button>
          </div>
        </div>
        {galaxy.error && <ErrorState message={galaxy.error} onRetry={galaxy.reload} />}
        {galaxy.data && <Galaxy points={galaxy.data} tokens={tokens} mode={mode} />}
        <div className="legend">
          {mode === "risk" ? (
            <>
              <span><i style={{ background: "var(--magenta)" }} />High risk</span>
              <span><i style={{ background: "var(--amber)" }} />Watch</span>
              <span><i style={{ background: "var(--cyan)" }} />Healthy</span>
            </>
          ) : (
            Object.entries(colours).map(([name, c]) => <span key={name}><i style={{ background: c }} />{name}</span>)
          )}
          <span>{galaxy.data ? `${count(galaxy.data.length)} accounts` : ""} · drag to orbit</span>
        </div>
      </section>

      <section className="glass panel">
        <div className="panel-head"><h2>RFM segments and suggested plays</h2><span className="hint">scores are quintiles 1–5 of recency, purchase days and net spend</span></div>
        {segments.loading && <Loading rows={6} />}
        {segments.error && <ErrorState message={segments.error} onRetry={segments.reload} />}
        {segments.data && (
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <thead>
                <tr><th>Segment</th><th className="num">Accounts</th><th className="num">Median last order</th><th className="num">Median purchase days</th><th className="num">Median net spend</th><th className="num">Expected 90-day spend</th><th className="num">High risk</th><th>Suggested play</th></tr>
              </thead>
              <tbody>
                {segments.data.segments.map((s) => (
                  <tr key={s.segment}>
                    <td><span className="pill" style={{ color: colours[s.segment] }}>{s.segment}</span></td>
                    <td className="num">{count(s.accounts)} <span style={{ color: "var(--muted)" }}>({pct(s.share)})</span></td>
                    <td className="num">{s.median_recency_days} d</td>
                    <td className="num">{s.median_purchase_days}</td>
                    <td className="num">{money(s.median_net_spend)}</td>
                    <td className="num">{money(s.expected_value_90)}</td>
                    <td className="num">{pct(s.high_risk_share)}</td>
                    <td style={{ minWidth: 220 }}>{s.play}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="provenance">Plays are playbook suggestions for a person to judge, not automated actions.</p>
      </section>

      <div className="row">
        <section className="glass panel" style={{ flex: "1 1 420px" }}>
          <div className="panel-head"><h2>Finding new customers worth nurturing</h2><span className="hint">lookalike model</span></div>
          {lookalikes.error && <ErrorState message={lookalikes.error} onRetry={lookalikes.reload} />}
          {lookalikes.data && (
            <>
              <p>{lookalikes.data.definition}. Test AUC <strong className="mono">{lookalikes.data.test_auc.toFixed(3)}</strong> on {count(lookalikes.data.test_customers)} later customers ({lookalikes.data.split}).</p>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ maxHeight: 320 }}>
                <table>
                  <thead><tr><th>New account</th><th className="num">Lookalike score</th></tr></thead>
                  <tbody>
                    {lookalikes.data.top.map((r) => (
                      <tr key={r.customer_id}><td><Link href={`/accounts?id=${r.customer_id}`}>{r.customer_id}</Link></td><td className="num">{pct(r.score, 1)}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="provenance">{count(lookalikes.data.newcomers)} accounts placed their first order in the 90 days before scoring.</p>
            </>
          )}
        </section>
        <section className="glass panel" style={{ flex: "1 1 360px" }}>
          <div className="panel-head"><h2>Data-driven clusters</h2><span className="hint">k-means on log recency, frequency, spend</span></div>
          {segments.data && (
            <>
              <p>Chosen k = <strong>{segments.data.clusters.k}</strong> by silhouette score ({Object.entries(segments.data.clusters.silhouette).map(([k, v]) => `k${k}: ${v.toFixed(3)}`).join(" · ")}).</p>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
                <table>
                  <thead><tr><th>Cluster</th><th className="num">Accounts</th><th className="num">Median last order</th><th className="num">Median purchase days</th><th className="num">Median net spend</th></tr></thead>
                  <tbody>
                    {segments.data.clusters.profiles.map((c) => (
                      <tr key={c.cluster}><td>{c.cluster}</td><td className="num">{count(c.accounts)}</td><td className="num">{c.median_recency_days} d</td><td className="num">{c.median_purchase_days}</td><td className="num">{money(c.median_net_spend)}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      </div>
      <Provenance summary={summary.data} />
    </>
  );
}
