"use client";
import { useMemo, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useApi } from "@/lib/api";
import { count, fixed, money, pct } from "@/lib/format";
import { useTokens } from "@/lib/tokens";
import { ErrorState, Loading, PageHeader } from "@/components/ui";

type Theme = { theme: string; available: boolean; error?: string; sales_index: number[]; web_index: number[]; correlation: number; correlation_web_one_month_later: number; sales_peak_month: number; web_peak_month: number; sales_total: number; source: { article: string; first: string; last: string } };
type Node = { id: string; label: string; invoices: number; community: number; degree: number; x: number; y: number };
type Signals = {
  web: { themes: Theme[]; licence: string; note: string };
  network: { nodes: Node[]; edges: { a: string; b: string; weight: number; lift: number }[]; communities: { id: number; size: number; examples: string[] }[]; modularity: number; method: string };
  social: { posts: number; sentiment_counts: Record<string, number>; lexicon_agreement_on_synthetic: number; injection_posts: number; injection_flagged: number; most_negative_products: { product: string; posts: number; negative_share: number }[]; samples: { post_id: string; product: string; text: string; sentiment: string; flagged_injection: boolean }[]; note: string };
  competitor: { available?: boolean; error?: string; site: string; items: number; price_by_rating: Record<string, { items: number; mean_price: number }>; sample: { title: string; price_gbp: number; rating: number }[]; practice: string[] };
};
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function NetworkMap({ data }: { data: Signals["network"] }) {
  const tokens = useTokens();
  const [hover, setHover] = useState<Node | null>(null);
  const palette = [tokens.cyan, tokens.magenta, tokens.amber, tokens.violet, tokens.muted];
  const pos = useMemo(() => Object.fromEntries(data.nodes.map((n) => [n.id, n])), [data.nodes]);
  const maxW = Math.max(...data.edges.map((e) => e.weight));
  const sx = (x: number) => 50 + x * 44, sy = (y: number) => 50 + y * 44;
  return (
    <div style={{ position: "relative" }}>
      <svg viewBox="0 0 100 100" style={{ width: "100%", height: 460 }} role="img" aria-label={`Co-purchase network of ${data.nodes.length} products in ${data.communities.length} communities`}>
        {data.edges.map((e) => pos[e.a] && pos[e.b] && (
          <line key={e.a + e.b} x1={sx(pos[e.a].x)} y1={sy(pos[e.a].y)} x2={sx(pos[e.b].x)} y2={sy(pos[e.b].y)} stroke={tokens.edge} strokeWidth={0.08 + (0.35 * e.weight) / maxW} />
        ))}
        {data.nodes.map((n) => (
          <circle key={n.id} cx={sx(n.x)} cy={sy(n.y)} r={0.6 + Math.sqrt(n.degree) * 0.28} fill={palette[n.community % palette.length]} stroke={hover?.id === n.id ? tokens.ink : "none"} strokeWidth={0.3}
            onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)}>
            <title>{`${n.label} · ${n.invoices} invoices · ${n.degree} links`}</title>
          </circle>
        ))}
      </svg>
      {hover && <div className="scene-tip glass"><strong>{hover.label}</strong><br />{count(hover.invoices)} invoices · linked to {hover.degree} products · community {hover.community + 1}</div>}
    </div>
  );
}

export default function SignalsPage() {
  const result = useApi<Signals>("/api/signals");
  const tokens = useTokens();
  const s = result.data;
  return (
    <>
      <PageHeader eyebrow="Signals · outcome B · weeks 9–10" title="Traditional, web and social data in one view." lede="Invoices (traditional), Wikipedia interest (web), a co-purchase network, synthetic social posts and a polite scraping demo, each with its source and limits stated." />
      {result.error && <section className="glass panel"><ErrorState message={result.error} onRetry={result.reload} /></section>}
      {result.loading && <section className="glass panel"><Loading rows={8} /></section>}
      {s && (
        <>
          <section className="glass panel">
            <div className="panel-head"><h2>Web interest vs wholesale sales, by season</h2><span className="badge">real · {s.web.licence}</span></div>
            <p className="lede" style={{ marginTop: 0 }}>{s.web.note} Index 1.0 = an average month.</p>
            <div className="stats">
              {s.web.themes.filter((t) => t.available).map((t) => (
                <div key={t.theme} className="glass stat" style={{ gap: 4 }}>
                  <span className="label">{t.theme} · Wikipedia “{t.source.article.replace(/_/g, " ")}”</span>
                  <div style={{ height: 150 }}>
                    <ResponsiveContainer>
                      <LineChart data={MONTHS.map((m, i) => ({ m, sales: t.sales_index[i], web: t.web_index[i] }))} margin={{ top: 6, right: 6, bottom: 0, left: -24 }}>
                        <CartesianGrid stroke={tokens.edge} vertical={false} />
                        <XAxis dataKey="m" tick={{ fill: tokens.muted, fontSize: 9 }} interval={1} />
                        <YAxis tick={{ fill: tokens.muted, fontSize: 9 }} />
                        <Tooltip contentStyle={{ background: tokens.bg, border: `1px solid ${tokens.edge}`, color: tokens.ink }} formatter={(v) => Number(v).toFixed(2)} />
                        <Line dataKey="sales" name="Sales" stroke={tokens.cyan} dot={false} strokeWidth={2} />
                        <Line dataKey="web" name="Web interest" stroke={tokens.magenta} dot={false} strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <span className="sub">Same month r = <b className="mono">{fixed(t.correlation, 2)}</b> · sales vs interest one month later r = <b className="mono">{fixed(t.correlation_web_one_month_later, 2)}</b></span>
                  <span className="sub">Sales peak {MONTHS[t.sales_peak_month - 1]} · interest peak {MONTHS[t.web_peak_month - 1]} · {money(t.sales_total)} sales</span>
                </div>
              ))}
            </div>
            <p className="provenance">Twelve monthly points per theme: treat correlations as exploratory. A higher “one month later” value means wholesale buying leads consumer interest.</p>
          </section>

          <div className="row">
            <section className="glass panel" style={{ flex: "999 1 520px" }}>
              <div className="panel-head"><h2>Co-purchase network</h2><span className="hint">modularity {fixed(s.network.modularity, 3)} · {s.network.nodes.length} products</span></div>
              <NetworkMap data={s.network} />
              <p className="provenance">{s.network.method}. It shows which products sell together, not social influence between customers.</p>
            </section>
            <section className="glass panel" style={{ flex: "1 1 320px" }}>
              <h2>Communities</h2>
              {s.network.communities.map((c) => (
                <div key={c.id} style={{ borderTop: "1px solid var(--edge)", paddingTop: 10 }}>
                  <strong>Community {c.id + 1}</strong> <span className="mono" style={{ color: "var(--muted)" }}>{c.size} products</span>
                  <p style={{ color: "var(--muted)", fontSize: 13 }}>{c.examples.join(" · ")}</p>
                </div>
              ))}
            </section>
          </div>

          <div className="row">
            <section className="glass panel" style={{ flex: "1 1 460px" }}>
              <div className="panel-head"><h2>Social posts about our products</h2><span className="badge synthetic">synthetic</span></div>
              <p style={{ color: "var(--muted)" }}>{s.social.note}</p>
              <div className="kv">
                <div><span>Posts</span><strong>{count(s.social.posts)}</strong></div>
                <div><span>Lexicon agreement</span><strong>{pct(s.social.lexicon_agreement_on_synthetic, 1)}</strong></div>
                <div><span>Negative posts</span><strong>{count(s.social.sentiment_counts.negative)}</strong></div>
                <div><span>Injection attempts flagged</span><strong>{s.social.injection_flagged} of {s.social.injection_posts}</strong></div>
              </div>
              <h3>Most negative products</h3>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ maxHeight: 260 }}>
                <table>
                  <thead><tr><th>Product</th><th className="num">Posts</th><th className="num">Negative</th></tr></thead>
                  <tbody>{s.social.most_negative_products.map((p) => <tr key={p.product}><td>{p.product}</td><td className="num">{p.posts}</td><td className="num">{pct(p.negative_share)}</td></tr>)}</tbody>
                </table>
              </div>
            </section>
            <section className="glass panel" style={{ flex: "1 1 380px" }}>
              <div className="panel-head"><h2>Sample posts</h2><span className="badge synthetic">synthetic</span></div>
              {s.social.samples.map((p) => (
                <div key={p.post_id} style={{ borderTop: "1px solid var(--edge)", paddingTop: 8 }}>
                  <p>{p.text}</p>
                  <p className="provenance"><span>{p.post_id}</span><span>sentiment {p.sentiment}</span>{p.flagged_injection && <span className="tone-high">flagged: prompt injection, never sent to the AI</span>}</p>
                </div>
              ))}
            </section>
          </div>

          <section className="glass panel">
            <div className="panel-head"><h2>Competitive intelligence: scraping demo</h2><span className="badge">sandbox · {s.competitor.site}</span></div>
            {s.competitor.available === false ? <ErrorState message={s.competitor.error ?? "unavailable"} /> : (
              <div className="row">
                <div style={{ flex: "1 1 320px" }}>
                  <h3>Average price by star rating ({s.competitor.items} listings)</h3>
                  <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table"><table>
                    <thead><tr><th>Rating</th><th className="num">Listings</th><th className="num">Mean price</th></tr></thead>
                    <tbody>{Object.entries(s.competitor.price_by_rating).map(([r, v]) => <tr key={r}><td>{"★".repeat(Number(r))}</td><td className="num">{v.items}</td><td className="num">£{v.mean_price.toFixed(2)}</td></tr>)}</tbody>
                  </table></div>
                </div>
                <div style={{ flex: "1 1 320px" }}>
                  <h3>How it scrapes responsibly</h3>
                  <ul className="reasons">{s.competitor.practice.map((p) => <li key={p}>{p}</li>)}</ul>
                  <p className="provenance" style={{ marginTop: 10 }}>Real competitor sites need their terms checked first; personal data needs a lawful basis (UK ICO: legitimate interests).</p>
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </>
  );
}
