"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { type Account, apiPost, type Summary, useApi } from "@/lib/api";
import { count, money, pct } from "@/lib/format";
import { useTokens } from "@/lib/tokens";
import { EmptyState, ErrorState, Icon, Loading, PageHeader, Provenance, RiskPill } from "@/components/ui";

type Detail = {
  account: Account;
  timeline: [string, number, number][];
  reviews: { id: number; decision: string; note: string; reviewer: string; created_at: string }[];
  drafts: { id: number; status: string; source: string; subject: string; created_at: string }[];
};

const PAGE = 25;
const SORTS = [
  ["value_at_risk_90", "Spend at risk"],
  ["p_lapse", "Lapse probability"],
  ["expected_value_90", "Expected 90-day spend"],
  ["net_sales_total", "Lifetime net spend"],
  ["recency_days", "Days since last order"],
] as const;

function AccountDrawer({ id, onClose }: { id: string; onClose: () => void }) {
  const detail = useApi<Detail>(`/api/accounts/${id}`);
  const tokens = useTokens();
  const [decision, setDecision] = useState("contact");
  const [note, setNote] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const save = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await apiPost(`/api/accounts/${id}/reviews`, { decision, note, reviewer });
      setNote("");
      setMessage({ ok: true, text: "Decision saved to the audit log." });
      detail.reload();
    } catch (e) {
      setMessage({ ok: false, text: `Not saved: ${(e as Error).message}` });
    } finally {
      setSaving(false);
    }
  };

  const a = detail.data?.account;
  const chart = (detail.data?.timeline ?? []).map(([month, sales, returns]) => ({ month, sales, returns: -returns }));
  return (
    <>
      <div className="backdrop" onClick={onClose} aria-hidden="true" />
      <aside className="drawer glass" role="dialog" aria-modal="true" aria-label={`Account ${id}`}>
        <button className="btn drawer-close" type="button" onClick={onClose} aria-label="Close account details">
          <Icon name="close" />
        </button>
        {detail.loading && <Loading rows={8} />}
        {detail.error && <ErrorState message={detail.error} onRetry={detail.reload} />}
        {a && (
          <>
            <div>
              <p className="eyebrow">{a.country}</p>
              <h2 style={{ fontSize: 24 }}>Account {a.customer_id}</h2>
              <div style={{ marginTop: 8 }}><RiskPill band={a.risk_band} p={a.p_lapse} /></div>
            </div>
            <div>
              <h3>Why it was flagged</h3>
              <ul className="reasons">{a.reasons.map((r) => <li key={r}>{r}</li>)}</ul>
            </div>
            <div className="kv">
              <div><span>P(no order in 90 days)</span><strong>{pct(a.p_lapse, 1)}</strong></div>
              <div><span>P(still active)</span><strong>{pct(a.p_alive, 1)}</strong></div>
              <div><span>Expected orders, 90 days</span><strong>{a.expected_purchases_90.toFixed(2)}</strong></div>
              <div><span>Expected spend, 90 days</span><strong>{money(a.expected_value_90)}</strong>{a.value_high_90 != null && <span>80% range {money(a.value_low_90)}–{money(a.value_high_90)}</span>}</div>
              <div><span>Spend at risk</span><strong>{money(a.value_at_risk_90)}</strong></div>
              <div><span>Lifetime net spend</span><strong>{money(a.net_sales_total)}</strong></div>
              <div><span>Last order</span><strong>{a.recency_days} days ago</strong></div>
              <div><span>Purchase days</span><strong>{a.frequency + 1}</strong></div>
              <div><span>Usual gap</span><strong>{a.mean_gap_days != null ? `${Math.round(a.mean_gap_days)} days` : "—"}</strong></div>
              <div><span>Returns</span><strong>{pct(a.return_rate)}</strong></div>
              {a.segment && <div><span>Segment</span><strong>{a.segment}</strong></div>}
            </div>
            <div>
              <h3>Monthly spend and returns</h3>
              <div style={{ height: 180, marginTop: 8 }}>
                <ResponsiveContainer>
                  <BarChart data={chart} margin={{ top: 4, right: 4, bottom: 0, left: -10 }}>
                    <CartesianGrid stroke={tokens.edge} vertical={false} />
                    <XAxis dataKey="month" tick={{ fill: tokens.muted, fontSize: 11 }} />
                    <YAxis tick={{ fill: tokens.muted, fontSize: 11 }} />
                    <Tooltip contentStyle={{ background: tokens.bg, border: `1px solid ${tokens.edge}`, color: tokens.ink }} formatter={(v) => money(Math.abs(Number(v)))} />
                    <Legend wrapperStyle={{ color: tokens.muted, fontSize: 11 }} />
                    <Bar dataKey="sales" name="Spend" fill={tokens.cyan} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="returns" name="Returns" fill={tokens.magenta} radius={[0, 0, 4, 4]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <form className="grid" style={{ gap: 10 }} onSubmit={(e) => { e.preventDefault(); save(); }}>
              <h3>Record your decision</h3>
              <label className="field">Decision
                <select value={decision} onChange={(e) => setDecision(e.target.value)}>
                  <option value="contact">Contact this account</option>
                  <option value="keep_watching">Keep watching</option>
                  <option value="no_action">No action</option>
                </select>
              </label>
              <label className="field">Why
                <textarea rows={3} value={note} onChange={(e) => setNote(e.target.value)} placeholder="Called last month; seasonal buyer, expect an order in March" />
              </label>
              <label className="field">Your name or initials
                <input value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="KM" />
              </label>
              <div className="row" style={{ gap: 10 }}>
                <button className="btn primary" type="submit" disabled={saving || note.trim().length < 3 || !reviewer.trim()}>{saving ? "Saving…" : "Save decision"}</button>
                <Link className="btn" href={`/outreach?account=${a.customer_id}`}>Draft outreach</Link>
              </div>
              {message && <p className={`toast ${message.ok ? "ok" : "error"}`} role="status">{message.text}</p>}
            </form>
            {detail.data!.reviews.length > 0 && (
              <div>
                <h3>Decision history</h3>
                <ul className="reasons">
                  {detail.data!.reviews.map((r) => <li key={r.id}><span className="mono">{r.created_at.slice(0, 16)}</span> · {r.reviewer} · {r.decision.replace("_", " ")}: {r.note}</li>)}
                </ul>
              </div>
            )}
          </>
        )}
      </aside>
    </>
  );
}

function AccountsInner() {
  const params = useSearchParams();
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [band, setBand] = useState(params.get("band") ?? "all");
  const [sort, setSort] = useState("value_at_risk_90");
  const [page, setPage] = useState(0);
  const selected = params.get("id");
  const query = useMemo(() => {
    const q = new URLSearchParams({ search, band, sort, order: sort === "recency_days" ? "desc" : "desc", limit: String(PAGE), offset: String(page * PAGE) });
    return `/api/accounts?${q}`;
  }, [search, band, sort, page]);
  const list = useApi<{ total: number; items: Account[] }>(query);
  const summary = useApi<Summary>("/api/summary");
  const open = (id: string | null) => {
    const q = new URLSearchParams(params.toString());
    if (id) q.set("id", id);
    else q.delete("id");
    router.replace(`/accounts?${q}`, { scroll: false });
  };
  const pages = list.data ? Math.max(1, Math.ceil(list.data.total / PAGE)) : 1;

  return (
    <>
      <PageHeader eyebrow="Accounts" title="Every account, ranked by what you could lose." lede="Lapse probability and expected spend come from the BG/NBD + Gamma-Gamma model, the best performer on the frozen test. Select a row to see the evidence and record a decision." />
      <section className="glass panel">
        <div className="toolbar">
          <label className="field grow">Search
            <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} placeholder="Account number or country" />
          </label>
          <label className="field">Risk
            <select value={band} onChange={(e) => { setBand(e.target.value); setPage(0); }}>
              <option value="all">All accounts</option>
              <option value="high">High risk</option>
              <option value="watch">Watch</option>
              <option value="healthy">Healthy</option>
            </select>
          </label>
          <label className="field">Sort by
            <select value={sort} onChange={(e) => { setSort(e.target.value); setPage(0); }}>
              {SORTS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
        </div>
        {list.error && <ErrorState message={list.error} onRetry={list.reload} />}
        {list.loading && !list.data && <Loading rows={10} />}
        {list.data && list.data.total === 0 && <EmptyState image="/img/aur-03-import.webp" title="No accounts match" body="Clear the search or choose another risk level." />}
        {list.data && list.data.total > 0 && (
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <caption className="sr-only">Accounts sorted by {SORTS.find((s) => s[0] === sort)?.[1]}</caption>
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Risk</th>
                  <th className="num">Spend at risk</th>
                  <th className="num">Expected 90-day spend</th>
                  <th className="num">Last order</th>
                  <th className="num">Purchase days</th>
                  <th className="num">Lifetime net</th>
                </tr>
              </thead>
              <tbody>
                {list.data.items.map((a) => (
                  <tr key={a.customer_id} className="clickable" aria-selected={selected === a.customer_id} onClick={() => open(a.customer_id)}>
                    <td>
                      <button className="row-btn" type="button" onClick={(e) => { e.stopPropagation(); open(a.customer_id); }}>{a.customer_id}</button>
                      <div style={{ fontSize: 12, color: "var(--muted)" }}>{a.country} · {a.reasons[0]}</div>
                    </td>
                    <td><RiskPill band={a.risk_band} p={a.p_lapse} /></td>
                    <td className="num">{money(a.value_at_risk_90)}</td>
                    <td className="num">{money(a.expected_value_90)}</td>
                    <td className="num">{a.recency_days} d</td>
                    <td className="num">{a.frequency + 1}</td>
                    <td className="num">{money(a.net_sales_total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {list.data && list.data.total > 0 && (
          <div className="pager">
            <span>{count(list.data.total)} accounts · page {page + 1} of {pages}</span>
            <span className="row" style={{ gap: 8 }}>
              <button className="btn" type="button" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
              <button className="btn" type="button" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>Next</button>
            </span>
          </div>
        )}
      </section>
      <Provenance summary={summary.data} />
      {selected && <AccountDrawer id={selected} onClose={() => open(null)} />}
    </>
  );
}

export default function AccountsPage() {
  return (
    <Suspense fallback={<Loading rows={8} />}>
      <AccountsInner />
    </Suspense>
  );
}
