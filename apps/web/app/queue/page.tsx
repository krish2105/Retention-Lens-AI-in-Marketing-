"use client";
import Link from "next/link";
import { useState } from "react";
import { API, apiPost, type Queue, STATIC, useApi } from "@/lib/api";
import { date, money, pct } from "@/lib/format";
import { EmptyState, ErrorState, Loading, PageHeader, RiskPill } from "@/components/ui";

type Arm = { accounts: number; reordered: number; rate: number | null; contacted: number };
type Outcomes = { arms: { contact: Arm; holdout: Arm }; uplift: { difference: number | null; ci95: [number, number] | null }; observe_days: number; pending: number; method: string };

function monday(offsetWeeks: number) {
  const d = new Date();
  d.setUTCHours(0, 0, 0, 0);
  d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 7 * offsetWeeks);
  return d.toISOString().slice(0, 10);
}

export default function QueuePage() {
  const [offset, setOffset] = useState(0);
  const queue = useApi<Queue>(`/api/queue?week=${monday(offset)}`);
  const outcomes = useApi<Outcomes>("/api/outcomes");
  const [logged, setLogged] = useState<Record<string, string>>({});
  const logReorder = async (customerId: string) => {
    if (!queue.data) return;
    try {
      await apiPost("/api/outcomes/reorder", { customer_id: customerId, week: queue.data.week, reordered_on: new Date().toISOString().slice(0, 10) });
      setLogged((l) => ({ ...l, [customerId]: "Reorder logged" }));
      outcomes.reload();
    } catch (e) {
      setLogged((l) => ({ ...l, [customerId]: (e as Error).message }));
    }
  };
  const q = queue.data;
  const o = outcomes.data;
  return (
    <>
      <PageHeader eyebrow={q ? `Week of ${date(q.week)}` : "This week"} title="This week's review queue." lede="The accounts with the most spend at risk, in order. Open each one, read the evidence and record a decision. A random share is held out each week so the effect of contacting accounts can be measured.">
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          {!STATIC && <div className="segmented glass" role="group" aria-label="Week">
            <button type="button" onClick={() => setOffset(offset - 1)} aria-label="Previous week">← Previous</button>
            <button type="button" aria-pressed={offset === 0} onClick={() => setOffset(0)}>This week</button>
            <button type="button" onClick={() => setOffset(offset + 1)} disabled={offset >= 0} aria-label="Next week">Next →</button>
          </div>}
          {!STATIC && <a className="btn" href={`${API}/api/reviews/export.csv`}>Export decisions (CSV)</a>}
        </div>
      </PageHeader>
      <section className="glass panel">
        {queue.loading && <Loading rows={6} />}
        {queue.error && <ErrorState message={queue.error} onRetry={queue.reload} />}
        {q && (
          <>
            <div className="panel-head">
              <h2>{q.reviewed} of {q.total} reviewed</h2>
              <span className="hint">{q.holdout} accounts held out at random ({pct(q.holdout_share)})</span>
            </div>
            <div className="progress" role="progressbar" aria-valuenow={q.reviewed} aria-valuemin={0} aria-valuemax={q.total} aria-label="Queue progress"><span style={{ width: `${q.total ? (100 * q.reviewed) / q.total : 0}%` }} /></div>
            {q.cleared && <EmptyState image="/img/aur-19-all-done.webp" title="Queue cleared for this week" body="Every account in this week's queue has a decision. New accounts join next Monday, or after your next upload." />}
            {q.total === 0 && <EmptyState image="/img/aur-19-all-done.webp" title="Nobody at risk this week" body="No account is in the high-risk or watch band right now." />}
            <div>
              {q.items.map((item) => (
                <Link key={item.customer_id} className="queue-item" href={`/accounts?id=${encodeURIComponent(item.customer_id)}`}>
                  <span style={{ minWidth: 0 }}>
                    <strong>Account {item.customer_id}</strong> {item.segment && <span className="badge">{item.segment}</span>}
                    <small>{item.reasons?.[0]} · {item.country}</small>
                  </span>
                  <span style={{ textAlign: "end", flex: "none" }}>
                    {item.status === "reviewed" ? <span className="pill tone-healthy">{item.decision?.replace("_", " ")}</span> : <RiskPill band={item.risk_band} p={item.p_lapse} />}
                    <small>{money(item.value_at_risk_90)} at risk</small>
                  </span>
                </Link>
              ))}
              {!STATIC && q.items.some((i) => i.status === "reviewed") && (
                <details className="twin" style={{ marginTop: 12 }}>
                  <summary>Log a reorder you heard about (phone, email, rep visit)</summary>
                  <p style={{ color: "var(--muted)", margin: "8px 0" }}>Reorders are also picked up automatically from your next upload. Logging one here records today&apos;s date for this week&apos;s queue.</p>
                  <div className="grid" style={{ gap: 6 }}>
                    {q.items.filter((i) => i.status === "reviewed").map((i) => (
                      <div key={i.customer_id} className="row" style={{ gap: 8, alignItems: "center" }}>
                        <span style={{ minWidth: 140 }}>Account {i.customer_id}</span>
                        <button className="btn" type="button" onClick={() => logReorder(i.customer_id)} disabled={Boolean(logged[i.customer_id])}>They reordered</button>
                        {logged[i.customer_id] && <span role="status" style={{ color: "var(--muted)" }}>{logged[i.customer_id]}</span>}
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          </>
        )}
      </section>
      <section className="glass panel">
        <div className="panel-head"><h2>Is outreach working?</h2><span className="hint">contacted vs held out, after {o?.observe_days ?? 28} days</span></div>
        {outcomes.error && <ErrorState message={outcomes.error} onRetry={outcomes.reload} />}
        {o && (
          <>
            <div className="kv">
              <div><span>Queued accounts that reordered</span><strong>{o.arms.contact.rate == null ? "—" : pct(o.arms.contact.rate, 1)}</strong><span>{o.arms.contact.reordered} of {o.arms.contact.accounts}</span></div>
              <div><span>Held-out accounts that reordered</span><strong>{o.arms.holdout.rate == null ? "—" : pct(o.arms.holdout.rate, 1)}</strong><span>{o.arms.holdout.reordered} of {o.arms.holdout.accounts}</span></div>
              <div><span>Difference (uplift)</span><strong>{o.uplift.difference == null ? "—" : `${o.uplift.difference > 0 ? "+" : ""}${pct(o.uplift.difference, 1)}`}</strong>{o.uplift.ci95 && <span>95% CI {pct(o.uplift.ci95[0], 1)} to {pct(o.uplift.ci95[1], 1)}</span>}</div>
              <div><span>Still being observed</span><strong>{o.pending}</strong><span>accounts queued less than {o.observe_days} days ago</span></div>
            </div>
            <p className="provenance"><span>{o.method}</span><span>Reorders are detected from your next upload, or logged by hand.</span></p>
            {o.arms.contact.accounts === 0 && <p style={{ color: "var(--muted)" }}>No result yet. It needs a few weeks of queues and at least one new upload after them. A confidence interval that crosses zero means no proven effect.</p>}
          </>
        )}
      </section>
    </>
  );
}
