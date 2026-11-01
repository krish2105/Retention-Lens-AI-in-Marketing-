"use client";
import Link from "next/link";
import { useState } from "react";
import { apiPost, STATIC } from "@/lib/api";

const BANDS = [
  { value: "under_200", label: "Fewer than 200" },
  { value: "200_1000", label: "200 to 1,000" },
  { value: "1000_5000", label: "1,000 to 5,000" },
  { value: "over_5000", label: "More than 5,000" },
];

/** Pilot waitlist. Consent is a separate, unticked box; nothing else is collected. */
export function Waitlist({ source = "landing" }: { source?: string }) {
  const [form, setForm] = useState({ email: "", company: "", role: "", accounts_band: "", consent: false });
  const [state, setState] = useState<{ kind: "idle" | "sending" | "ok" | "error"; message?: string }>({ kind: "idle" });
  const set = (key: string, value: string | boolean) => setForm((f) => ({ ...f, [key]: value }));
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.consent) {
      setState({ kind: "error", message: "Tick the box so we may email you about the pilot." });
      return;
    }
    setState({ kind: "sending" });
    try {
      const result = await apiPost<{ message: string }>("/api/waitlist", { ...form, source });
      setState({ kind: "ok", message: result.message });
    } catch (error) {
      setState({ kind: "error", message: (error as Error).message });
    }
  };
  if (state.kind === "ok") {
    return <p className="toast ok" role="status">{state.message}</p>;
  }
  return (
    <form className="grid" style={{ gap: 12 }} onSubmit={submit} noValidate>
      {STATIC && (
        <p className="notice">This public demo is a static site and cannot store sign-ups. Join from the hosted version, or watch the GitHub repository for the pilot announcement.</p>
      )}
      <div className="form-grid">
        <label className="field">Work email
          <input type="email" required autoComplete="email" value={form.email} onChange={(e) => set("email", e.target.value)} disabled={STATIC} />
        </label>
        <label className="field">Company
          <input required autoComplete="organization" value={form.company} onChange={(e) => set("company", e.target.value)} disabled={STATIC} />
        </label>
        <label className="field">Your role
          <input required autoComplete="organization-title" placeholder="e.g. Owner, sales manager" value={form.role} onChange={(e) => set("role", e.target.value)} disabled={STATIC} />
        </label>
        <label className="field">Active trade accounts
          <select required value={form.accounts_band} onChange={(e) => set("accounts_band", e.target.value)} disabled={STATIC}>
            <option value="" disabled>Choose…</option>
            {BANDS.map((b) => <option key={b.value} value={b.value}>{b.label}</option>)}
          </select>
        </label>
        <label className="check-row full">
          <input type="checkbox" checked={form.consent} onChange={(e) => set("consent", e.target.checked)} disabled={STATIC} />
          <span>Email me about the RetentionLens pilot. I can unsubscribe at any time. See the <Link href="/legal/privacy">privacy notice</Link>.</span>
        </label>
      </div>
      {state.kind === "error" && <p className="toast error" role="alert">{state.message}</p>}
      <div><button className="btn primary" type="submit" disabled={STATIC || state.kind === "sending"}>{state.kind === "sending" ? "Joining…" : "Join the pilot waitlist"}</button></div>
    </form>
  );
}
