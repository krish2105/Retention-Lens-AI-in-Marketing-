"use client";
import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";
import { useApi } from "@/lib/api";
import { count, money, pct } from "@/lib/format";
import { useTokens } from "@/lib/tokens";
import { ErrorState, Loading, PageHeader } from "@/components/ui";

type Lab = {
  rules: { if: string; then: string; support: number; confidence: number; lift: number; invoices: number }[];
  elasticities: { product: string; elasticity: number; ci_low: number; ci_high: number; weeks: number; r2: number }[];
  portfolio: { product: string; sales_recent: number; sales_prior: number; growth: number | null; quadrant: string | null }[];
  portfolio_window?: { recent: string; prior: string; available: boolean; reason?: string };
  loyalty: { product: string; buyers: number; repeat_rate: number }[];
  caveats: string[];
};

export default function ProductLab() {
  const result = useApi<Lab>("/api/product-lab");
  const tokens = useTokens();
  const lab = result.data;
  const quadrantColour: Record<string, string> = { Star: tokens.cyan, "Cash cow": tokens.violet, "Question mark": tokens.amber, Dog: tokens.magenta };
  return (
    <>
      <PageHeader eyebrow="Product lab · weeks 7–8" title="What sells together, what grows, what people come back for." lede="Basket rules for cross-selling, a portfolio view for positioning, repeat-purchase loyalty by product, and a price analysis that shows why observational data can mislead." />
      {result.error && <section className="glass panel"><ErrorState message={result.error} onRetry={result.reload} /></section>}
      {result.loading && <section className="glass panel"><Loading rows={8} /></section>}
      {lab && (
        <>
          <section className="glass panel">
            <div className="panel-head"><h2>Basket rules: bought together</h2><span className="hint">top {lab.rules.length} by lift · support ≥ 1% of invoices</span></div>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ maxHeight: 380 }}>
              <table>
                <thead><tr><th>If they buy</th><th>They also buy</th><th className="num">Confidence</th><th className="num">Lift</th><th className="num">Invoices</th></tr></thead>
                <tbody>{lab.rules.map((r) => <tr key={r.if + r.then}><td>{r.if}</td><td>{r.then}</td><td className="num">{pct(r.confidence)}</td><td className="num">{r.lift.toFixed(1)}×</td><td className="num">{count(r.invoices)}</td></tr>)}</tbody>
              </table>
            </div>
            {lab.rules.length === 0 ? (
              <p className="notice">No product pairs pass the thresholds (each pair in at least 1% of invoices, lift of 2 or more). Small catalogues or few multi-line invoices often give none.</p>
            ) : (
              <p className="provenance">Lift {lab.rules[0].lift.toFixed(0)}× means the top pair appears together {lab.rules[0].lift.toFixed(0)} times more often than chance. Use it for “customers also stock” suggestions in outreach.</p>
            )}
          </section>

          <div className="row">
            <section className="glass panel" style={{ flex: "1 1 480px" }}>
              <div className="panel-head"><h2>Portfolio: volume vs growth</h2><span className="hint">{lab.portfolio_window ? `${lab.portfolio_window.recent} vs ${lab.portfolio_window.prior}` : "last 12 months vs the 12 before"}, top 40 products</span></div>
              <div style={{ height: 320 }}>
                <ResponsiveContainer>
                  <ScatterChart margin={{ top: 10, right: 16, bottom: 10, left: 0 }}>
                    <CartesianGrid stroke={tokens.edge} />
                    <XAxis type="number" dataKey="sales_recent" name="Last 12 months" tickFormatter={(v) => `£${Math.round(v / 1000)}k`} tick={{ fill: tokens.muted, fontSize: 11 }} />
                    <YAxis type="number" dataKey="growth" name="Growth" tickFormatter={(v) => `${Math.round(v * 100)}%`} tick={{ fill: tokens.muted, fontSize: 11 }} />
                    <ZAxis range={[60, 60]} />
                    <Tooltip contentStyle={{ background: tokens.bg, border: `1px solid ${tokens.edge}`, color: tokens.ink }} formatter={(v, n) => (n === "Growth" ? pct(Number(v)) : money(Number(v)))} labelFormatter={() => ""} />
                    {["Star", "Cash cow", "Question mark", "Dog"].map((q) => (
                      <Scatter key={q} name={q} data={lab.portfolio.filter((p) => p.quadrant === q)} fill={quadrantColour[q]} />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
              <div className="legend">{Object.entries(quadrantColour).map(([q, c]) => <span key={q}><i style={{ background: c }} />{q}</span>)}</div>
            </section>
            <section className="glass panel" style={{ flex: "1 1 360px" }}>
              <div className="panel-head"><h2>Product loyalty</h2><span className="hint">share of buyers who reorder</span></div>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ maxHeight: 360 }}>
                <table>
                  <thead><tr><th>Product</th><th className="num">Buyers</th><th className="num">Reorder</th></tr></thead>
                  <tbody>{lab.loyalty.slice(0, 15).map((r) => <tr key={r.product}><td>{r.product}</td><td className="num">{count(r.buyers)}</td><td className="num">{pct(r.repeat_rate)}</td></tr>)}</tbody>
                </table>
              </div>
            </section>
          </div>

          <section className="glass panel">
            <div className="panel-head"><h2>Price elasticity: a lesson in confounding</h2><span className="badge">associational · do not use for pricing</span></div>
            <p>Weekly log-log regressions with quarter controls give elasticities far below anything plausible for giftware. The reason: wholesale <strong>price breaks</strong> mean big orders get lower unit prices, so low prices and high quantities go together. That is the price list, not customer price sensitivity. A randomised price test would be needed for a causal answer.</p>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ maxHeight: 300 }}>
              <table>
                <thead><tr><th>Product</th><th className="num">Elasticity</th><th className="num">95% interval</th><th className="num">Weeks</th><th className="num">R²</th></tr></thead>
                <tbody>{lab.elasticities.map((e) => <tr key={e.product}><td>{e.product}</td><td className="num">{e.elasticity.toFixed(2)}</td><td className="num">{e.ci_low.toFixed(1)} to {e.ci_high.toFixed(1)}</td><td className="num">{e.weeks}</td><td className="num">{e.r2.toFixed(2)}</td></tr>)}</tbody>
              </table>
            </div>
            <ul className="reasons" style={{ color: "var(--muted)" }}>{lab.caveats.map((c) => <li key={c}>{c}</li>)}</ul>
          </section>
        </>
      )}
    </>
  );
}
