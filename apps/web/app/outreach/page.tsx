"use client";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { type Account, API, apiPost, READ_ONLY_MESSAGE, STATIC, useApi } from "@/lib/api";
import { money } from "@/lib/format";
import { EmptyState, ErrorState, Loading, PageHeader, RiskPill } from "@/components/ui";

type Check = { name: string; passed: boolean; detail: string };
type Draft = {
  id: number; customer_id: string; status: string; source: "model" | "template"; model: string | null; subject: string; body: string;
  checks: Check[]; context: { facts: string[]; tone: string; error: string | null; seconds: number }; recipient_type: string | null; consent_basis: string | null; decided_by: string | null; created_at: string;
};
type DraftRow = { id: number; customer_id: string; status: string; source: string; subject: string; created_at: string };
type Health = { ollama: { available: boolean; model: string } };

const STATUS: Record<string, string> = { pending_approval: "Awaiting approval", needs_revision: "Needs revision", approved: "Approved", rejected: "Rejected" };
const TONE: Record<string, string> = { warm: "Warm", brief: "Brief", seasonal: "Seasonal" };

function newKey() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

function DraftView({ id, onChanged }: { id: number; onChanged: () => void }) {
  const draft = useApi<Draft>(`/api/drafts/${id}`);
  const [body, setBody] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [recipient, setRecipient] = useState("unknown");
  const [consent, setConsent] = useState("none");
  const [ack, setAck] = useState(false);
  const [key, setKey] = useState(newKey());
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (draft.data) { setBody(draft.data.body); setKey(newKey()); setMessage(null); } }, [draft.data]);
  const d = draft.data;
  if (draft.loading && !d) return <Loading rows={8} />;
  if (draft.error) return <ErrorState message={draft.error} onRetry={draft.reload} />;
  if (!d) return null;
  const decided = d.status === "approved" || d.status === "rejected";
  const critic = d.checks.find((c) => c.name.startsWith("Second-pass"));

  const decide = async (decision: "approve" | "reject") => {
    setBusy(true);
    setMessage(null);
    try {
      const edited = body.trim() !== d.body.trim() ? body : null;
      await apiPost(`/api/drafts/${d.id}/decision`, { decision, reviewer, recipient_type: recipient, consent_basis: consent, edited_body: edited, acknowledge_review: ack }, key);
      setMessage({ ok: true, text: decision === "approve" ? "Approved. It's ready to export; nothing has been sent." : "Rejected and logged." });
      draft.reload();
      onChanged();
    } catch (e) {
      setMessage({ ok: false, text: (e as Error).message });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid" style={{ gap: 16 }}>
      <div className="panel-head">
        <div>
          <p className="eyebrow">Draft {d.id} · account {d.customer_id}</p>
          <h2>{d.subject}</h2>
        </div>
        <span className={`pill ${d.status === "approved" ? "tone-healthy" : d.status === "needs_revision" || d.status === "rejected" ? "tone-high" : "tone-watch"}`}>{STATUS[d.status] ?? d.status}</span>
      </div>
      <p className="provenance">
        <span className={`badge ${d.source === "template" ? "synthetic" : ""}`}>{d.source === "model" ? `AI draft · ${d.model}` : "Template (local model offline)"}</span>
        <span>{d.context.tone}</span><span>{d.context.seconds}s</span>{d.context.error && <span className="tone-high">{d.context.error}</span>}
      </p>
      <label className="field">Email text {decided ? "" : "(you can edit it; checks run again on approval)"}
        <textarea rows={11} value={body} onChange={(e) => setBody(e.target.value)} readOnly={decided} />
      </label>
      <div>
        <h3>Automatic checks</h3>
        <ul className="reasons" style={{ listStyle: "none", paddingLeft: 0 }}>
          {d.checks.map((c) => (
            <li key={c.name}><span className={c.passed ? "tone-healthy" : "tone-high"}>{c.passed ? "✓" : "✕"}</span> {c.name} <span style={{ color: "var(--muted)" }}>· {c.detail}</span></li>
          ))}
        </ul>
      </div>
      <details className="twin">
        <summary>Facts the AI was given (it saw nothing else)</summary>
        <ul className="reasons" style={{ marginTop: 8 }}>{d.context.facts.map((f) => <li key={f}>{f}</li>)}</ul>
      </details>
      {decided ? (
        <p className="toast ok">Decided by {d.decided_by} · recipient {d.recipient_type} · basis {d.consent_basis?.replaceAll("_", " ")}</p>
      ) : (
        <form className="grid" style={{ gap: 10 }} onSubmit={(e) => e.preventDefault()}>
          <h3>Approval (required before export)</h3>
          <div className="row" style={{ gap: 10 }}>
            <label className="field" style={{ flex: "1 1 180px" }}>Recipient type
              <select value={recipient} onChange={(e) => setRecipient(e.target.value)}>
                <option value="unknown">Not recorded</option>
                <option value="company">Company (corporate subscriber)</option>
                <option value="sole_trader">Sole trader or partnership</option>
              </select>
            </label>
            <label className="field" style={{ flex: "1 1 220px" }}>Basis for contacting them
              <select value={consent} onChange={(e) => setConsent(e.target.value)}>
                <option value="none">Not recorded</option>
                <option value="legitimate_interest_b2b">Legitimate interest (B2B, companies only)</option>
                <option value="soft_opt_in_existing_customer">Soft opt-in (existing customer)</option>
                <option value="explicit_consent">Explicit consent</option>
              </select>
            </label>
            <label className="field" style={{ flex: "1 1 140px" }}>Your initials
              <input value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="KM" />
            </label>
          </div>
          {critic && !critic.passed && (
            <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input type="checkbox" checked={ack} onChange={(e) => setAck(e.target.checked)} /> I have read the second-pass review&apos;s issues
            </label>
          )}
          <div className="row" style={{ gap: 10 }}>
            <button className="btn primary" type="button" disabled={busy || !reviewer.trim()} onClick={() => decide("approve")}>Approve for export</button>
            <button className="btn" type="button" disabled={busy || !reviewer.trim()} onClick={() => decide("reject")}>Reject</button>
          </div>
          <p className="provenance">UK PECR: companies can be contacted under legitimate interests; sole traders need consent or the soft opt-in. Approval is blocked without a valid basis.</p>
        </form>
      )}
      {message && <p className={`toast ${message.ok ? "ok" : "error"}`} role="status">{message.text}</p>}
    </div>
  );
}

function OutreachInner() {
  const params = useSearchParams();
  const health = useApi<Health>("/api/health");
  const queue = useApi<{ items: Account[] }>("/api/accounts?band=high&limit=12");
  const drafts = useApi<DraftRow[]>("/api/drafts");
  const [account, setAccount] = useState(params.get("account") ?? "");
  const [tone, setTone] = useState("warm");
  const [reviewer, setReviewer] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const online = health.data?.ollama.available;

  const create = async () => {
    setBusy(true);
    setError(null);
    try {
      const d = await apiPost<Draft>("/api/drafts", { customer_id: account.trim(), tone, reviewer });
      setSelected(d.id);
      drafts.reload();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <PageHeader eyebrow="Outreach studio · outcome D" title="AI drafts the words. You approve every one." lede="A local language model writes a short check-in email using only facts from the scoring model. Automatic checks block invented numbers, offers, pressure and personal data. Nothing is ever sent from here: approved drafts are exported for you to send.">
      </PageHeader>
      {STATIC && (
        <section className="glass panel">
          <p className="toast">{READ_ONLY_MESSAGE} Example drafts and the live evaluation are in <a href="https://github.com/krish2105/Retention-Lens-AI-in-Marketing-/blob/main/reports/genai_eval.md">reports/genai_eval.md</a>.</p>
        </section>
      )}
      <div className="row">
        <section className="glass panel" style={{ flex: "1 1 340px" }}>
          <div className="panel-head">
            <h2>New draft</h2>
            <span className={`pill ${online ? "tone-healthy" : "tone-watch"}`}>{health.data ? (online ? `${health.data.ollama.model} running` : "Local model offline: template mode") : "Checking…"}</span>
          </div>
          <label className="field">Account number
            <input value={account} onChange={(e) => setAccount(e.target.value)} placeholder="16754" />
          </label>
          <label className="field">Tone
            <select value={tone} onChange={(e) => setTone(e.target.value)}>{Object.entries(TONE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
          </label>
          <label className="field">Your initials
            <input value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="KM" />
          </label>
          <button className="btn primary" type="button" disabled={busy || !account.trim() || !reviewer.trim()} onClick={create}>{busy ? "Drafting… (10–40 s on a local model)" : "Draft email"}</button>
          {error && <p className="toast error" role="alert">{error}</p>}
          <h3>High-risk accounts</h3>
          {queue.data?.items.map((a) => (
            <button key={a.customer_id} type="button" className="queue-item" style={{ background: "none", border: 0, borderTop: "1px solid var(--edge)", textAlign: "left", width: "100%" }} onClick={() => setAccount(a.customer_id)}>
              <span><strong>{a.customer_id}</strong><small>{a.segment} · {money(a.value_at_risk_90)} at risk</small></span>
              <RiskPill band={a.risk_band} p={a.p_lapse} />
            </button>
          ))}
        </section>
        <section className="glass panel" style={{ flex: "999 1 520px" }}>
          {selected ? <DraftView id={selected} onChanged={drafts.reload} /> : <EmptyState image="/img/aur-04-outreach.webp" title="Pick an account and draft an email" body="Or open an existing draft from the list below." />}
        </section>
      </div>
      <section className="glass panel">
        <div className="panel-head">
          <h2>All drafts</h2>
          {!STATIC && <a className="btn" href={`${API}/api/drafts/export.csv`}>Export approved (CSV)</a>}
        </div>
        {drafts.error && <ErrorState message={drafts.error} onRetry={drafts.reload} />}
        {drafts.data && drafts.data.length === 0 && <p style={{ color: "var(--muted)" }}>No drafts yet.</p>}
        {drafts.data && drafts.data.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Draft</th><th>Account</th><th>Subject</th><th>Source</th><th>Status</th><th>Created</th></tr></thead>
              <tbody>
                {drafts.data.map((d) => (
                  <tr key={d.id} className="clickable" aria-selected={selected === d.id} onClick={() => setSelected(d.id)}>
                    <td><button className="row-btn" type="button" onClick={(e) => { e.stopPropagation(); setSelected(d.id); }}>#{d.id}</button></td>
                    <td>{d.customer_id}</td><td>{d.subject}</td><td>{d.source}</td><td>{STATUS[d.status] ?? d.status}</td><td className="mono">{d.created_at.slice(0, 16)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}

export default function OutreachPage() {
  return <Suspense fallback={<Loading rows={8} />}><OutreachInner /></Suspense>;
}
