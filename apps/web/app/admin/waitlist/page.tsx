"use client";
import { useEffect, useState } from "react";
import { API, STATIC } from "@/lib/api";
import { count, date } from "@/lib/format";
import { PageHeader } from "@/components/ui";

type Row = { id: number; email: string; company: string; role: string; accounts_band: string; consent_at: string; source: string; created_at: string };
type Data = { signups: number; by_accounts_band: Record<string, number>; rows: Row[] };
const BAND: Record<string, string> = { under_200: "Under 200", "200_1000": "200–1,000", "1000_5000": "1,000–5,000", over_5000: "Over 5,000" };

/** Operator view of the pilot waitlist. The admin token is kept only for this browser tab. */
export default function WaitlistAdmin() {
  const [token, setToken] = useState("");
  const [data, setData] = useState<Data | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    try {
      setToken(window.sessionStorage.getItem("rl-admin") ?? "");
    } catch {}
  }, []);
  const load = async (event?: React.FormEvent) => {
    event?.preventDefault();
    setError(null);
    try {
      const response = await fetch(`${API}/api/admin/waitlist`, { headers: { "X-Admin-Token": token, "X-RL-Client": "web" } });
      if (!response.ok) throw new Error(response.status === 401 ? "Wrong or missing admin token (RL_ADMIN_TOKEN on the server)" : `Error ${response.status}`);
      setData(await response.json());
      try {
        window.sessionStorage.setItem("rl-admin", token);
      } catch {}
    } catch (e) {
      setError((e as Error).message);
    }
  };
  const csv = () => {
    if (!data) return;
    const header = "email,company,role,accounts_band,consent_at,source,created_at";
    const lines = data.rows.map((r) => [r.email, r.company, r.role, r.accounts_band, r.consent_at, r.source, r.created_at].map((v) => `"${String(v).replaceAll('"', '""').replace(/^([=+\-@])/, "'$1")}"`).join(","));
    const url = URL.createObjectURL(new Blob([[header, ...lines].join("\n")], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "waitlist.csv";
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <>
      <PageHeader eyebrow="Operator" title="Pilot waitlist." lede="Sign-ups from the landing page, with their consent time. Use them only to contact people about the pilot." />
      {STATIC ? (
        <section className="glass panel"><p className="notice">The public demo stores no sign-ups.</p></section>
      ) : (
        <section className="glass panel">
          <form className="toolbar" onSubmit={load}>
            <label className="field grow">Admin token<input type="password" autoComplete="off" value={token} onChange={(e) => setToken(e.target.value)} /></label>
            <button className="btn primary" type="submit">Load</button>
          </form>
          {error && <p className="toast error" role="alert">{error}</p>}
          {data && (
            <>
              <div className="kv">
                <div><span>Sign-ups</span><strong>{count(data.signups)}</strong></div>
                {Object.entries(data.by_accounts_band).map(([k, v]) => <div key={k}><span>{BAND[k] ?? k} accounts</span><strong>{count(v)}</strong></div>)}
              </div>
              <div><button className="btn" type="button" onClick={csv}>Download CSV</button></div>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Waitlist">
                <table>
                  <thead><tr><th>Email</th><th>Company</th><th>Role</th><th>Accounts</th><th>Consented</th><th>Source</th></tr></thead>
                  <tbody>{data.rows.map((r) => <tr key={r.id}><td>{r.email}</td><td>{r.company}</td><td>{r.role}</td><td>{BAND[r.accounts_band] ?? r.accounts_band}</td><td>{date(r.consent_at)}</td><td>{r.source}</td></tr>)}</tbody>
                </table>
              </div>
            </>
          )}
        </section>
      )}
    </>
  );
}
