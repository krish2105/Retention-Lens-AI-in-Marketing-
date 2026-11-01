"use client";
import Link from "next/link";
import { API, type Queue, STATIC, useApi } from "@/lib/api";
import { date, money, pct } from "@/lib/format";
import { EmptyState, ErrorState, Loading, PageHeader, RiskPill } from "@/components/ui";

type Arm = { accounts: number; reordered: number; rate: number | null; contacted: number };
type Outcomes = { arms: { contact: Arm; holdout: Arm }; uplift: { difference: number | null; ci95: [number, number] | null }; observe_days: number; pending: number; method: string };

export default function QueuePage() {
  const queue = useApi<Queue>("/api/queue");
  const outcomes = useApi<Outcomes>("/api/outcomes");
  const q = queue.data;
  const o = outcomes.data;
  return (
    <>
      <PageHeader eyebrow={q ? `Week of ${date(q.week)}` : "This week"} title="This week's review queue." lede="The accounts with the most spend at risk, in order. Open each one, read the evidence and record a decision. A random share is held out each week so the effect of contacting accounts can be measured.">
        {!STATIC && <a className="btn" href={`${API}/api/reviews/export.csv`}>Export decisions (CSV)</a>}
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
